"""Entrenamiento: modelos iniciales, búsqueda de hiperparámetros, umbral global y umbrales
por grupo de edad, y persistencia de los modelos.

Uso:  python -m src.train
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, precision_recall_curve, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, cross_val_score

from .data_processing import FEATURES, preparar_datos
from .model import (ModeloRiesgo, asignar_grupo_edad, crear_gradient_boosting, crear_random_forest,
                    crear_regresion_logistica)
from .utils import cargar_config, guardar_json, obtener_logger, ruta


def umbral_para_recall(y, p, recall_objetivo: float) -> float:
    """Mayor umbral cuyo recall (en y, p) alcanza el objetivo."""
    prec, rec, thr = precision_recall_curve(y, p)
    ok = np.where(rec[:-1] >= recall_objetivo)[0]
    return float(thr[ok[-1]])


def metricas_basicas(y, p) -> dict:
    return {"auc_roc": float(roc_auc_score(y, p)), "auc_pr": float(average_precision_score(y, p)),
            "brier": float(brier_score_loss(y, p))}


def predicciones_oof(params: dict, X, y, g, semilla_oof: int, semilla: int, n_splits: int = 5) -> np.ndarray:
    """Predicciones fuera de muestra con CV agrupada por paciente (solo entrenamiento)."""
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=semilla_oof)
    oof = np.zeros(len(X))
    for a, b in cv.split(X, y, g):
        m = crear_gradient_boosting(semilla, **params).fit(X.iloc[a], y.iloc[a])
        oof[b] = m.predict_proba(X.iloc[b])[:, 1]
    return oof


def entrenar(cfg: dict | None = None) -> dict:
    cfg = cfg or cargar_config()
    log = obtener_logger(archivo=cfg["rutas"]["logs"])
    t0 = time.time()
    semilla = cfg["proyecto"]["semilla"]
    df, train, test, freq = preparar_datos(cfg)

    # Datos procesados para notebooks, evaluación y app
    ruta(cfg["rutas"]["datos_procesados"]).parent.mkdir(parents=True, exist_ok=True)
    procesado = pd.concat([train.assign(conjunto="entrenamiento"), test.assign(conjunto="prueba")])
    cols = ["PatientId", "AppointmentID", "Neighbourhood", "no_show", "conjunto"] + FEATURES
    procesado[cols].to_csv(ruta(cfg["rutas"]["datos_procesados"]), index=False)
    guardar_json(freq, cfg["rutas"]["frecuencia_barrios"])

    Xtr, ytr, gtr = train[FEATURES], train["no_show"], train["PatientId"]
    Xte, yte = test[FEATURES], test["no_show"]
    res = {"particion": {"n_train": len(train), "n_test": len(test),
                         "pacientes_train": int(gtr.nunique()), "pacientes_test": int(test["PatientId"].nunique()),
                         "prevalencia_train": float(ytr.mean()), "prevalencia_test": float(yte.mean())}}

    # 1) Modelos iniciales y líneas base
    iniciales = {"Regresión logística": crear_regresion_logistica(),
                 "Random Forest": crear_random_forest(semilla),
                 "Gradient Boosting (inicial)": crear_gradient_boosting(semilla)}
    res["modelos_iniciales"] = {}
    for nombre, m in iniciales.items():
        m.fit(Xtr, ytr)
        res["modelos_iniciales"][nombre] = {**metricas_basicas(yte, m.predict_proba(Xte)[:, 1]),
                                            "auc_roc_train": float(roc_auc_score(ytr, m.predict_proba(Xtr)[:, 1]))}
        log.info("modelo inicial %s: AUC prueba %.4f", nombre, res["modelos_iniciales"][nombre]["auc_roc"])
    base = crear_regresion_logistica().fit(Xtr[["lead_time_days"]], ytr)
    res["modelos_iniciales"]["Referencia: solo antelación"] = metricas_basicas(
        yte, base.predict_proba(Xte[["lead_time_days"]])[:, 1])

    # 2) Búsqueda de hiperparámetros (CV agrupada por paciente, solo entrenamiento)
    cv3 = StratifiedGroupKFold(n_splits=cfg["particion"]["pliegues_cv_busqueda"], shuffle=True, random_state=semilla)
    gs_rf = GridSearchCV(crear_random_forest(semilla, n_estimators=150), cfg["modelo"]["rejilla_rf"],
                         scoring="roc_auc", cv=cv3, n_jobs=1).fit(Xtr, ytr, groups=gtr)
    gs_gb = GridSearchCV(crear_gradient_boosting(semilla), cfg["modelo"]["rejilla_gb"],
                         scoring="roc_auc", cv=cv3, n_jobs=1).fit(Xtr, ytr, groups=gtr)
    log.info("rejilla RF %s (CV %.4f); rejilla GB %s (CV %.4f)", gs_rf.best_params_, gs_rf.best_score_,
             gs_gb.best_params_, gs_gb.best_score_)
    params = {k: (float(v) if isinstance(v, float) else int(v)) for k, v in gs_gb.best_params_.items()}
    final = crear_gradient_boosting(semilla, **params).fit(Xtr, ytr)
    rf_aj = crear_random_forest(semilla, **gs_rf.best_params_).fit(Xtr, ytr)
    res["busqueda"] = {"gb_mejores_parametros": params, "gb_cv3_auc": float(gs_gb.best_score_),
                       "rf_mejores_parametros": gs_rf.best_params_, "rf_cv3_auc": float(gs_rf.best_score_),
                       "gb_auc_prueba": float(roc_auc_score(yte, final.predict_proba(Xte)[:, 1])),
                       "rf_auc_prueba": float(roc_auc_score(yte, rf_aj.predict_proba(Xte)[:, 1])),
                       "resultados_rejilla_gb": [
                           {**{k: (float(v) if isinstance(v, float) else int(v)) for k, v in p.items()},
                            "cv_auc": float(s)} for p, s in zip(gs_gb.cv_results_["params"],
                                                               gs_gb.cv_results_["mean_test_score"])]}
    cv5 = StratifiedGroupKFold(n_splits=cfg["particion"]["pliegues_cv_final"], shuffle=True, random_state=semilla)
    s5 = cross_val_score(final, Xtr, ytr, groups=gtr, cv=cv5, scoring="roc_auc", n_jobs=1)
    res["cv5_modelo_final"] = {"media": float(s5.mean()), "de": float(s5.std()), "pliegues": s5.tolist()}

    # 3) Umbral global y umbrales por grupo de edad (con OOF de entrenamiento)
    oof = predicciones_oof(params, Xtr, ytr, gtr, cfg["particion"]["semilla_oof"], semilla)
    objetivo = cfg["modelo"]["recall_objetivo"]
    thr_global = umbral_para_recall(ytr, oof, objetivo)
    eq = cfg["equidad"]
    grupos_tr = asignar_grupo_edad(Xtr["Age"], eq["grupos_edad"], eq["etiquetas_grupos"])
    thr_grupo = {lab: umbral_para_recall(ytr[grupos_tr == lab], oof[grupos_tr == lab], objetivo)
                 for lab in eq["etiquetas_grupos"]}
    log.info("umbral global %.4f; umbrales por grupo %s", thr_global, {k: round(v, 4) for k, v in thr_grupo.items()})

    meta = {"version": cfg["proyecto"]["version"], "parametros": params, "recall_objetivo": objetivo,
            "auc_prueba": res["busqueda"]["gb_auc_prueba"], "cv5_auc": res["cv5_modelo_final"]["media"],
            "entrenado_con": "Medical Appointment No Shows (Hoppen, 2016), CC BY-NC-SA 4.0",
            "n_entrenamiento": len(train)}
    ModeloRiesgo(final, FEATURES, thr_global, thr_grupo, eq["grupos_edad"], eq["etiquetas_grupos"], meta) \
        .guardar(cfg["rutas"]["mejor_modelo"])
    v1 = iniciales["Gradient Boosting (inicial)"]
    oof_v1 = predicciones_oof({}, Xtr, ytr, gtr, cfg["particion"]["semilla_oof"], semilla)
    ModeloRiesgo(v1, FEATURES, umbral_para_recall(ytr, oof_v1, objetivo), {}, eq["grupos_edad"],
                 eq["etiquetas_grupos"], {"version": "0.1.0", "parametros": "valores por defecto",
                                          "auc_prueba": res["modelos_iniciales"]["Gradient Boosting (inicial)"]["auc_roc"]}) \
        .guardar(cfg["rutas"]["modelo_v1"])
    res["umbrales"] = {"global": thr_global, "por_grupo": thr_grupo}
    np.save(ruta(cfg["rutas"]["metricas"]) / "oof_entrenamiento.npy", oof)
    guardar_json(res, f"{cfg['rutas']['metricas']}/entrenamiento.json")
    log.info("entrenamiento completo en %.0f s", time.time() - t0)
    return res


if __name__ == "__main__":
    entrenar()

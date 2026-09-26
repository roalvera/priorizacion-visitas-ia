"""Evaluación del modelo final en prueba: discriminación, calibración, umbral, importancia,
SHAP, equidad por grupo de edad (antes y después de la mitigación), confusión del SMS y
simulación de asignación.

Uso:  python -m src.evaluate
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.calibration import calibration_curve
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)

from .data_processing import FEATURES
from .model import ModeloRiesgo, asignar_grupo_edad
from .simulation import construir_escenario, simular
from .utils import cargar_config, guardar_json, obtener_logger, ruta


def cargar_particiones(cfg: dict):
    df = pd.read_csv(ruta(cfg["rutas"]["datos_procesados"]))
    return df[df["conjunto"] == "entrenamiento"].copy(), df[df["conjunto"] == "prueba"].copy()


def metricas_umbral(y, pred) -> dict:
    return {"precision": float(precision_score(y, pred, zero_division=0)), "recall": float(recall_score(y, pred)),
            "f1": float(f1_score(y, pred)), "exactitud": float(accuracy_score(y, pred)),
            "porcentaje_senalado": float(np.mean(pred))}


def equidad_por_grupo(test: pd.DataFrame, p, modelo: ModeloRiesgo, n_boot: int, semilla: int) -> pd.DataFrame:
    """AUC con IC bootstrap por paciente, y recall/precisión/% señalado con umbral global y mitigado."""
    y = test["no_show"].values
    grupos = asignar_grupo_edad(test["Age"], modelo.grupos_edad, modelo.etiquetas_grupos)
    pred_g = (p >= modelo.umbral_global).astype(int)
    pred_m = (p >= modelo.umbrales_por_fila(test, mitigado=True)).astype(int)
    rng = np.random.RandomState(semilla)
    filas = []
    for lab in modelo.etiquetas_grupos + ["Mujeres", "Hombres"]:
        if lab == "Mujeres":
            m = test["gender_f"].values == 1
        elif lab == "Hombres":
            m = test["gender_f"].values == 0
        else:
            m = grupos == lab
        sub = test[m]
        pac = sub["PatientId"].unique()
        idx_por_pac = sub.groupby("PatientId").indices
        pos = np.flatnonzero(m)
        boots = []
        for _ in range(n_boot):
            elegidos = rng.choice(pac, len(pac), replace=True)
            ii = pos[np.concatenate([idx_por_pac[q] for q in elegidos])]
            if y[ii].min() != y[ii].max():
                boots.append(roc_auc_score(y[ii], p[ii]))
        fila = {"grupo": lab, "n": int(m.sum()), "tasa_base": float(y[m].mean()),
                "auc": float(roc_auc_score(y[m], p[m])),
                "auc_ic95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                "recall_global": float(recall_score(y[m], pred_g[m])),
                "precision_global": float(precision_score(y[m], pred_g[m], zero_division=0)),
                "senalado_global": float(pred_g[m].mean())}
        if lab in modelo.etiquetas_grupos:
            fila.update({"umbral_mitigado": float(modelo.umbrales_grupo[lab]),
                         "recall_mitigado": float(recall_score(y[m], pred_m[m])),
                         "precision_mitigado": float(precision_score(y[m], pred_m[m], zero_division=0)),
                         "senalado_mitigado": float(pred_m[m].mean())})
        filas.append(fila)
    return pd.DataFrame(filas)


def confusion_sms(df: pd.DataFrame) -> dict:
    """Asociación cruda y ajustada por tramo de antelación entre SMS y no-show."""
    d = df.copy()
    d["tramo"] = pd.cut(d["lead_time_days"], [-1, 0, 3, 7, 30, 10_000], labels=["0", "1-3", "4-7", "8-30", "31+"])
    crudo = d.groupby("SMS_received")["no_show"].mean()
    fit = smf.logit("no_show ~ SMS_received + C(tramo)", data=d).fit(
        disp=0, cov_type="cluster", cov_kwds={"groups": d["PatientId"]})
    ci = fit.conf_int().loc["SMS_received"]
    return {"tasa_sin_sms": float(crudo[0]), "tasa_con_sms": float(crudo[1]),
            "or_ajustado": float(np.exp(fit.params["SMS_received"])),
            "or_ic95": [float(np.exp(ci[0])), float(np.exp(ci[1]))]}


def valores_shap(modelo: ModeloRiesgo, X: pd.DataFrame, n: int = 3000, semilla: int = 42):
    """Valores SHAP (TreeExplainer) sobre una muestra del conjunto de prueba."""
    import shap
    muestra = X.sample(min(n, len(X)), random_state=semilla)
    explicador = shap.TreeExplainer(modelo.estimador)
    return explicador, muestra, explicador.shap_values(muestra)


def evaluar(cfg: dict | None = None) -> dict:
    cfg = cfg or cargar_config()
    log = obtener_logger(archivo=cfg["rutas"]["logs"])
    modelo = ModeloRiesgo.cargar(cfg["rutas"]["mejor_modelo"])
    train, test = cargar_particiones(cfg)
    Xte, yte = test[FEATURES], test["no_show"].values
    p = modelo.predecir_probabilidad(Xte)
    res = {"auc_roc": float(roc_auc_score(yte, p)), "auc_pr": float(average_precision_score(yte, p)),
           "brier": float(brier_score_loss(yte, p)),
           "brier_sin_informacion": float(brier_score_loss(yte, np.full(len(yte), train["no_show"].mean())))}
    pred05 = (p >= 0.5).astype(int)
    pred_g = modelo.clasificar(Xte, mitigado=False)
    pred_m = modelo.clasificar(test, mitigado=True)
    res["umbral_05"] = metricas_umbral(yte, pred05)
    res["umbral_global"] = {"umbral": modelo.umbral_global, **metricas_umbral(yte, pred_g),
                            "matriz_confusion": confusion_matrix(yte, pred_g).tolist()}
    res["umbral_mitigado"] = metricas_umbral(yte, pred_m)
    fr, mp = calibration_curve(yte, p, n_bins=10, strategy="quantile")
    res["calibracion"] = {"prob_media": mp.tolist(), "tasa_observada": fr.tolist(),
                          "brecha_media_abs": float(np.mean(np.abs(fr - mp)))}
    pi = permutation_importance(modelo.estimador, Xte, yte, scoring="roc_auc", n_repeats=5,
                                random_state=cfg["proyecto"]["semilla"], n_jobs=1)
    res["importancia_permutacion"] = dict(sorted(
        {f: {"media": float(m), "de": float(s)} for f, m, s in zip(FEATURES, pi.importances_mean, pi.importances_std)}
        .items(), key=lambda kv: -kv[1]["media"]))
    _, muestra, sv = valores_shap(modelo, Xte, semilla=cfg["proyecto"]["semilla"])
    res["shap_media_abs"] = dict(sorted({f: float(v) for f, v in zip(FEATURES, np.abs(sv).mean(axis=0))}.items(),
                                        key=lambda kv: -kv[1]))
    eq = equidad_por_grupo(test, p, modelo, cfg["equidad"]["remuestreos_bootstrap"], cfg["proyecto"]["semilla"])
    res["equidad"] = eq.to_dict(orient="records")
    res["confusion_sms"] = confusion_sms(pd.concat([train, test]))
    # Simulación
    sim = cfg["simulacion"]
    _, solicitudes, dist = construir_escenario(cfg)
    k = int(round(sim["fraccion_intervenida"] * sim["n_solicitudes"]))
    res["simulacion"] = {"principal": simular(p, yte, dist, sim["reduccion_relativa"], k, sim["replicas"], sim["semilla"]),
                         "sensibilidad_efecto": {str(r): simular(p, yte, dist, r, k, sim["replicas_sensibilidad"], sim["semilla"])
                                                 for r in [0.15, 0.35, 0.50]},
                         "millas_totales": float(dist.sum())}
    top = np.argsort(-p)[: int(0.2 * len(p))]
    res["simulacion"]["captura_top20"] = float(yte[top].sum() / yte.sum())
    guardar_json(res, f"{cfg['rutas']['metricas']}/evaluacion.json")
    log.info("evaluación: AUC %.4f | recall global %.3f | recall mitigado %.3f", res["auc_roc"],
             res["umbral_global"]["recall"], res["umbral_mitigado"]["recall"])
    return res


if __name__ == "__main__":
    evaluar()

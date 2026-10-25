"""Experimento de control: qué pasaría sin las medidas contra la fuga de información.

Compara, con el mismo modelo final (Gradient Boosting, mismos hiperparámetros), tres variantes:
  A. Pipeline del proyecto: historial solo con citas ya atendidas al agendar y partición por paciente.
  B. Historial con fuga: tasa de inasistencia del paciente calculada con TODAS sus citas, incluida la
     propia y las futuras, manteniendo la partición por paciente.
  C. Historial con fuga y partición aleatoria por cita (un mismo paciente en entrenamiento y prueba).
El AUC de B y C no es real: mide cuánto se inflaría el desempeño si se cometieran esos errores.

Uso:  python scripts/experimento_fuga.py   (guarda results/metrics/experimento_fuga.json)
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_processing import (FEATURES, agregar_historial, cargar_crudos, limpiar,  # noqa: E402
                                 particionar_por_paciente)
from src.model import crear_gradient_boosting  # noqa: E402
from src.utils import cargar_config, guardar_json, leer_json  # noqa: E402


def historial_con_fuga(d):
    """Versión ingenua (incorrecta): usa todas las citas del paciente, incluido el desenlace actual."""
    d = d.copy()
    g = d.groupby("PatientId")["no_show"]
    d["prior_appts"] = g.transform("size") - 1
    d["prior_noshow_rate"] = g.transform("mean")
    return d


def auc_prueba(train, test, params, semilla):
    m = crear_gradient_boosting(semilla, **params).fit(train[FEATURES], train["no_show"])
    return float(roc_auc_score(test["no_show"], m.predict_proba(test[FEATURES])[:, 1]))


if __name__ == "__main__":
    cfg = cargar_config()
    semilla = cfg["proyecto"]["semilla"]
    params = leer_json(Path(cfg["rutas"]["metricas"]) / "entrenamiento.json")["busqueda"]["gb_mejores_parametros"]
    base = limpiar(cargar_crudos(cfg["rutas"]["datos_crudos"]))
    n = cfg["particion"]["pliegues_particion"]
    tr, te, _ = particionar_por_paciente(agregar_historial(base), n, semilla)
    res = {"A_proyecto": auc_prueba(tr, te, params, semilla)}
    fuga = historial_con_fuga(base)
    tr, te, _ = particionar_por_paciente(fuga, n, semilla)
    res["B_historial_con_fuga"] = auc_prueba(tr, te, params, semilla)
    tr, te = train_test_split(fuga, test_size=0.25, stratify=fuga["no_show"], random_state=semilla)
    freq = tr["Neighbourhood"].value_counts(normalize=True)
    tr, te = tr.copy(), te.copy()
    for part in (tr, te):
        part["neighbourhood_freq"] = part["Neighbourhood"].map(freq).fillna(0.0)
    res["C_fuga_y_particion_aleatoria"] = auc_prueba(tr, te, params, semilla)
    res["pacientes_compartidos_en_C"] = int(len(set(tr["PatientId"]) & set(te["PatientId"])))
    guardar_json(res, Path(cfg["rutas"]["metricas"]) / "experimento_fuga.json")
    print({k: round(v, 4) if isinstance(v, float) else v for k, v in res.items()})

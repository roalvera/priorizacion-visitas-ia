"""Pruebas de la evaluación de equidad ampliada y del análisis de sensibilidad de la simulación."""
import numpy as np
import pandas as pd
import pytest

from src.evaluate import proxy_vulnerabilidad_barrio
from src.utils import leer_json, ruta

EVAL = ruta("results/metrics/evaluacion.json")


def test_proxy_barrio_usa_solo_entrenamiento():
    train = pd.DataFrame({"Neighbourhood": ["A"] * 4 + ["B"] * 4 + ["C"] * 4,
                          "Scholarship": [1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0]})
    test = pd.DataFrame({"Neighbourhood": ["A", "B", "C", "Z"]})
    etiquetas = proxy_vulnerabilidad_barrio(train, test)
    assert list(etiquetas[:3]) == ["alta", "media", "baja"]
    assert etiquetas[3] in {"alta", "media", "baja"}       # barrio nuevo: proporción global


@pytest.mark.skipif(not EVAL.exists(), reason="ejecute primero python -m src.evaluate")
def test_equidad_incluye_sexo_y_proxies_con_intervalos():
    ev = leer_json(EVAL)
    dims = {f["dimension"] for f in ev["equidad"]}
    assert dims == {"edad", "sexo", "programa social", "barrio"}
    for f in ev["equidad"]:
        for clave in ["auc_ic95", "recall_global_ic95", "recall_mitigado_ic95"]:
            lo, hi = f[clave]
            assert lo <= hi
        assert f["auc_ic95"][0] <= f["auc"] <= f["auc_ic95"][1]
    n_test = sum(f["n"] for f in ev["equidad"] if f["dimension"] == "edad")
    for dim in ["sexo", "programa social", "barrio"]:
        assert sum(f["n"] for f in ev["equidad"] if f["dimension"] == dim) == n_test


@pytest.mark.skipif(not EVAL.exists(), reason="ejecute primero python -m src.evaluate")
def test_sensibilidad_10_25_40_y_orden_de_politicas():
    sim = leer_json(EVAL)["simulacion"]
    sens = sim["sensibilidad_efecto"]
    assert set(sens) == {"0.1", "0.25", "0.4"}
    assert sens["0.25"] == sim["principal"]
    for esc in sens.values():
        medias = [esc[k]["media"] for k in ["azar", "distancia", "riesgo", "riesgo_x_distancia", "oraculo"]]
        assert np.all(np.diff(medias) > 0)

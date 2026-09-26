"""Pruebas del modelo entrenado y de la lógica de umbrales."""
import numpy as np
import pandas as pd
import pytest

from src.data_processing import FEATURES
from src.model import ModeloRiesgo, asignar_grupo_edad
from src.simulation import priorizar_lote
from src.utils import ruta

MODELO = ruta("models/best_model.pkl")
pytestmark = pytest.mark.skipif(not MODELO.exists(), reason="ejecute primero python -m src.train")


@pytest.fixture(scope="module")
def modelo():
    return ModeloRiesgo.cargar(MODELO)


@pytest.fixture(scope="module")
def muestra():
    df = pd.read_csv(ruta("data/processed/citas_procesadas.csv"))
    return df[df["conjunto"] == "prueba"].head(500)


def test_probabilidades_validas(modelo, muestra):
    p = modelo.predecir_probabilidad(muestra[FEATURES])
    assert p.shape == (500,)
    assert np.all((p >= 0) & (p <= 1))


def test_prediccion_determinista(modelo, muestra):
    X = muestra[FEATURES]
    assert np.array_equal(modelo.predecir_probabilidad(X), modelo.predecir_probabilidad(X))


def test_falta_variable_lanza_error(modelo, muestra):
    with pytest.raises(ValueError):
        modelo.predecir_probabilidad(muestra[FEATURES].drop(columns=["Age"]))


def test_umbral_mitigado_es_mas_bajo_en_adultos_mayores(modelo):
    assert modelo.umbrales_grupo["65 o más"] < modelo.umbral_global


def test_grupos_de_edad():
    g = asignar_grupo_edad([0, 18, 19, 64, 65, 90], [[0, 18], [19, 35], [36, 55], [56, 64], [65, 200]],
                           ["a", "b", "c", "d", "e"])
    assert list(g) == ["a", "a", "b", "d", "e", "e"]


def test_priorizar_lote_respeta_capacidad():
    marca = priorizar_lote(np.array([0.1, 0.9, 0.5, 0.2]), np.array([10, 1, 5, 50.0]), 0.5)
    assert marca.sum() == 2
    assert marca[3] and marca[2]     # 0.2*50=10 y 0.5*5=2.5 superan a 0.9*1 y 0.1*10

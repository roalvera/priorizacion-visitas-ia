"""Pruebas de la interfaz Streamlit con AppTest (sin navegador)."""
import pytest
from streamlit.testing.v1 import AppTest

from src.utils import ruta

pytestmark = pytest.mark.skipif(not ruta("models/best_model.pkl").exists(), reason="falta el modelo entrenado")
APP = str(ruta("app/app.py"))


def test_app_carga_sin_errores():
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception
    assert len(at.tabs) == 4


def test_ejemplo_y_prediccion():
    at = AppTest.from_file(APP, default_timeout=120).run()
    at.button[1].click().run()                          # "Prueba con ejemplo: riesgo alto"
    assert at.number_input(key="in_edad").value == 23
    at.button(key="FormSubmitter:formulario-Calcular riesgo").click().run()
    assert not at.exception
    assert any("Riesgo" in m.value for m in at.markdown)


def test_error_si_inasistencias_superan_citas():
    at = AppTest.from_file(APP, default_timeout=120).run()
    at.number_input(key="in_previas").set_value(1)
    at.number_input(key="in_faltas").set_value(3)
    at.button(key="FormSubmitter:formulario-Calcular riesgo").click().run()
    assert any("no pueden ser más" in e.value for e in at.error)

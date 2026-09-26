"""Pruebas de las funciones de procesamiento de datos."""
import numpy as np
import pandas as pd
import pytest

from src.data_processing import (FEATURES, agregar_historial, limpiar, registro_a_features, validar_lote,
                                 validar_registro)


def _fila(pid, agendada, cita, no_show, **extra):
    return {"PatientId": pid, "ScheduledDay": f"2016-05-{agendada}T08:00:00Z",
            "AppointmentDay": f"2016-05-{cita}T00:00:00Z", "No-show": no_show, **extra}


def _crudo(filas):
    base = {"AppointmentID": 1, "Gender": "F", "Age": 30, "Neighbourhood": "CENTRO", "Scholarship": 0,
            "Hipertension": 0, "Diabetes": 0, "Alcoholism": 0, "Handcap": 0, "SMS_received": 0}
    return pd.DataFrame([{**base, **f} for f in filas])


def _registro_valido():
    return {"gender_f": 1, "Age": 40, "Scholarship": 0, "Hipertension": 1, "Diabetes": 0, "Alcoholism": 0,
            "Handcap": 0, "SMS_received": 1, "lead_time_days": 10, "appt_dow": 2, "prior_appts": 3,
            "prior_noshow_rate": 0.33, "neighbourhood_freq": 0.01}


def test_limpiar_elimina_edad_negativa_y_recorta_antelacion():
    df = _crudo([
        _fila(1, "10", "12", "No"),
        _fila(2, "10", "09", "Yes"),
        _fila(3, "10", "10", "No", Age=-1)])
    out = limpiar(df)
    assert len(out) == 2
    assert out["lead_time_days"].tolist() == [2, 0]
    assert out["no_show"].tolist() == [0, 1]


def test_historial_sin_fuga_temporal():
    # Cita B se agenda ANTES de que ocurra la cita A: el desenlace de A no puede entrar al historial de B.
    df = _crudo([
        _fila(7, "01", "10", "Yes"),
        _fila(7, "05", "20", "No"),
        _fila(7, "15", "25", "No")])
    out = agregar_historial(limpiar(df))
    assert out["prior_appts"].tolist() == [0, 0, 1]
    assert out["prior_noshow_rate"].tolist() == [0.0, 0.0, 1.0]


def test_validar_registro_detecta_errores():
    r = _registro_valido()
    assert validar_registro(r) == []
    r["Age"] = 150
    r["SMS_received"] = 3
    errores = validar_registro(r)
    assert any("Edad" in e for e in errores)
    assert any("SMS" in e for e in errores)


def test_registro_a_features_calcula_condiciones_cronicas():
    X = registro_a_features(_registro_valido())
    assert list(X.columns) == FEATURES
    assert X["chronic_count"].iloc[0] == 1


def test_validar_lote_reporta_columnas_faltantes_y_filas_invalidas():
    _, errores = validar_lote(pd.DataFrame({"Age": [30]}))
    assert errores and "Faltan columnas" in errores[0]
    lote = pd.DataFrame([_registro_valido(), {**_registro_valido(), "prior_noshow_rate": 2.0}])
    validas, errores = validar_lote(lote)
    assert len(validas) == 1 and len(errores) == 1

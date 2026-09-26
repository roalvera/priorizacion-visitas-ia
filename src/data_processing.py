"""Carga, limpieza, ingeniería de variables sin fuga temporal, partición por paciente
y validación de entradas de la interfaz."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from .utils import obtener_logger, ruta

LOG = obtener_logger()

FEATURES = ["gender_f", "Age", "Scholarship", "Hipertension", "Diabetes", "Alcoholism", "Handcap",
            "SMS_received", "lead_time_days", "appt_dow", "chronic_count", "prior_appts",
            "prior_noshow_rate", "neighbourhood_freq"]

ETIQUETAS = {
    "gender_f": "Sexo femenino", "Age": "Edad", "Scholarship": "Programa social (Bolsa Família)",
    "Hipertension": "Hipertensión", "Diabetes": "Diabetes", "Alcoholism": "Alcoholismo",
    "Handcap": "Discapacidad", "SMS_received": "Recordatorio SMS", "lead_time_days": "Antelación (días)",
    "appt_dow": "Día de la semana", "chronic_count": "Condiciones crónicas", "prior_appts": "Citas previas",
    "prior_noshow_rate": "Tasa previa de inasistencia", "neighbourhood_freq": "Frecuencia del barrio",
}

COLUMNAS_CRUDAS = ["PatientId", "AppointmentID", "Gender", "ScheduledDay", "AppointmentDay", "Age",
                   "Neighbourhood", "Scholarship", "Hipertension", "Diabetes", "Alcoholism", "Handcap",
                   "SMS_received", "No-show"]

# Rangos válidos para la interfaz y para la validación de lotes
RANGOS = {"Age": (0, 115), "lead_time_days": (0, 365), "appt_dow": (0, 6), "prior_appts": (0, 100),
          "prior_noshow_rate": (0.0, 1.0), "neighbourhood_freq": (0.0, 1.0)}
BINARIAS = ["gender_f", "Scholarship", "Hipertension", "Diabetes", "Alcoholism", "Handcap", "SMS_received"]


def cargar_crudos(path: str = "data/raw/noshow_appointments.csv") -> pd.DataFrame:
    """Lee el dataset público y verifica que tenga las columnas esperadas."""
    try:
        df = pd.read_csv(ruta(path))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"No se encontró {path}. Revise data/README.md para descargarlo.") from exc
    df.columns = [c.strip() for c in df.columns]
    faltan = set(COLUMNAS_CRUDAS) - set(df.columns)
    if faltan:
        raise ValueError(f"El archivo no tiene las columnas esperadas: {sorted(faltan)}")
    LOG.info("datos crudos cargados: %d filas", len(df))
    return df


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina edades negativas, normaliza fechas y crea variables básicas."""
    d = df.copy()
    d["ScheduledDay"] = pd.to_datetime(d["ScheduledDay"], utc=True).dt.tz_localize(None)
    d["AppointmentDay"] = pd.to_datetime(d["AppointmentDay"], utc=True).dt.tz_localize(None)
    n_neg = int((d["Age"] < 0).sum())
    d = d[d["Age"] >= 0].copy().reset_index(drop=True)
    d["Handcap"] = (d["Handcap"] > 0).astype(int)
    d["no_show"] = (d["No-show"] == "Yes").astype(int)
    d["sched_date"] = d["ScheduledDay"].dt.normalize()
    d["appt_date"] = d["AppointmentDay"].dt.normalize()
    lead = (d["appt_date"] - d["sched_date"]).dt.days
    d["lead_time_days"] = lead.clip(lower=0)
    d["appt_dow"] = d["AppointmentDay"].dt.dayofweek
    d["chronic_count"] = d[["Hipertension", "Diabetes", "Alcoholism"]].sum(axis=1) + d["Handcap"]
    d["gender_f"] = (d["Gender"] == "F").astype(int)
    LOG.info("limpieza: %d edades negativas eliminadas, %d antelaciones negativas llevadas a 0",
             n_neg, int((lead < 0).sum()))
    return d


def agregar_historial(d: pd.DataFrame) -> pd.DataFrame:
    """Historial del paciente SIN fuga temporal: solo cuentan citas cuya fecha de atención es
    anterior a la fecha de agendamiento de la cita evaluada (desenlace ya conocido)."""
    d = d.copy()
    sched = d["sched_date"].values.astype("datetime64[D]").astype(np.int64)
    appt = d["appt_date"].values.astype("datetime64[D]").astype(np.int64)
    ns = d["no_show"].values
    n_prior = np.zeros(len(d), dtype=int)
    n_prior_ns = np.zeros(len(d), dtype=int)
    for _, idx in d.groupby("PatientId").indices.items():
        if len(idx) == 1:
            continue
        order = np.argsort(appt[idx], kind="stable")
        a_sorted = appt[idx][order]
        cum = np.concatenate([[0], np.cumsum(ns[idx][order])])
        pos = np.searchsorted(a_sorted, sched[idx], side="left")
        self_prior = appt[idx] < sched[idx]   # la propia cita figura como anterior (casos anómalos)
        n_prior[idx] = pos - self_prior
        n_prior_ns[idx] = cum[pos] - ns[idx] * self_prior
    d["prior_appts"] = n_prior
    d["prior_noshow_rate"] = np.where(n_prior > 0, n_prior_ns / np.maximum(n_prior, 1), 0.0)
    return d


def particionar_por_paciente(d: pd.DataFrame, n_splits: int = 4, semilla: int = 42):
    """Partición estratificada y agrupada por paciente (ningún paciente en ambos lados).
    Calcula la frecuencia de barrio SOLO con entrenamiento."""
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=semilla)
    tr_idx, te_idx = next(splitter.split(d, d["no_show"], groups=d["PatientId"]))
    train, test = d.iloc[tr_idx].copy(), d.iloc[te_idx].copy()
    if set(train["PatientId"]) & set(test["PatientId"]):
        raise RuntimeError("Hay pacientes en ambos conjuntos: la partición no es válida")
    freq = train["Neighbourhood"].value_counts(normalize=True)
    for part in (train, test):
        part["neighbourhood_freq"] = part["Neighbourhood"].map(freq).fillna(0.0)
    LOG.info("partición por paciente: %d entrenamiento, %d prueba", len(train), len(test))
    return train, test, freq.to_dict()


def preparar_datos(cfg: dict):
    """Pipeline completo: carga, limpieza, historial y partición."""
    df = agregar_historial(limpiar(cargar_crudos(cfg["rutas"]["datos_crudos"])))
    train, test, freq = particionar_por_paciente(df, cfg["particion"]["pliegues_particion"],
                                                 cfg["proyecto"]["semilla"])
    return df, train, test, freq


def validar_registro(registro: dict) -> list[str]:
    """Valida una cita ingresada en la interfaz. Devuelve la lista de errores (vacía si es válida)."""
    errores = []
    for col in FEATURES:
        if col == "chronic_count":
            continue
        if col not in registro or registro[col] is None or (isinstance(registro[col], float) and np.isnan(registro[col])):
            errores.append(f"Falta el valor de «{ETIQUETAS[col]}».")
            continue
        try:
            v = float(registro[col])
        except (TypeError, ValueError):
            errores.append(f"«{ETIQUETAS[col]}» debe ser numérico.")
            continue
        if col in BINARIAS and v not in (0, 1):
            errores.append(f"«{ETIQUETAS[col]}» debe ser 0 o 1.")
        if col in RANGOS and not (RANGOS[col][0] <= v <= RANGOS[col][1]):
            errores.append(f"«{ETIQUETAS[col]}» debe estar entre {RANGOS[col][0]} y {RANGOS[col][1]}.")
    return errores


def registro_a_features(registro: dict) -> pd.DataFrame:
    """Convierte una cita validada en la fila de variables que espera el modelo."""
    r = {k: float(registro[k]) for k in FEATURES if k != "chronic_count"}
    r["chronic_count"] = r["Hipertension"] + r["Diabetes"] + r["Alcoholism"] + r["Handcap"]
    return pd.DataFrame([r])[FEATURES]


def validar_lote(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Valida un CSV cargado en la interfaz; devuelve las filas válidas y los errores encontrados."""
    requeridas = [c for c in FEATURES if c != "chronic_count"]
    faltan = [c for c in requeridas if c not in df.columns]
    if faltan:
        return pd.DataFrame(), [f"Faltan columnas en el CSV: {', '.join(faltan)}"]
    errores, validas = [], []
    for i, fila in df.iterrows():
        e = validar_registro(fila.to_dict())
        if e:
            errores.append(f"Fila {i + 2}: " + " ".join(e))
        else:
            validas.append(i)
    return df.loc[validas].reset_index(drop=True), errores

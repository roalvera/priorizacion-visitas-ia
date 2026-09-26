"""Simulación de Monte Carlo del motor de asignación geográfica y de la capa de priorización.

Cada solicitud se asigna a la sede de NP más cercana (heurística de vecino más cercano); la
priorización decide qué 20% de solicitudes recibe una confirmación proactiva. Las ubicaciones
son reales y públicas (centroides ZCTA del Census Bureau y códigos postales del NPI Registry);
la asociación paciente-ubicación es sintética y así se declara en toda la documentación.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .utils import haversine_millas, ruta

POLITICAS = {"azar": "Al azar", "distancia": "Solo distancia", "riesgo": "Por riesgo",
             "riesgo_x_distancia": "Riesgo × distancia", "oraculo": "Óptimo (cota)"}


def construir_escenario(cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """Devuelve sedes, solicitudes y la distancia de cada solicitud a su sede más cercana."""
    zc = pd.read_csv(ruta(cfg["rutas"]["centroides_zip"]), dtype={"zip": str})
    sim = cfg["simulacion"]
    sedes = zc.set_index("zip").loc[sim["sedes_np"]].reset_index()
    solicitudes = zc.sample(sim["n_solicitudes"], random_state=sim["semilla_solicitudes"], replace=False) \
        .reset_index(drop=True)
    dist = np.column_stack([haversine_millas(solicitudes["lat"].values, solicitudes["lon"].values, la, lo)
                            for la, lo in zip(sedes["lat"], sedes["lon"])])
    solicitudes["sede_asignada"] = sedes["zip"].values[dist.argmin(axis=1)]
    solicitudes["millas"] = dist.min(axis=1)
    return sedes, solicitudes, solicitudes["millas"].values


def seleccionar(politica: str, p, y, dist, k: int, rng) -> np.ndarray:
    if politica == "azar":
        return rng.choice(len(p), k, replace=False)
    if politica == "distancia":
        return np.argsort(-dist)[:k]
    if politica == "riesgo":
        return np.argsort(-p)[:k]
    if politica == "riesgo_x_distancia":
        return np.argsort(-(p * dist))[:k]
    if politica == "oraculo":
        return np.argsort(-(y * dist))[:k]
    raise ValueError(f"Política desconocida: {politica}")


def simular(p_all, y_all, dist, reduccion: float, k: int, replicas: int, semilla: int) -> dict:
    """Reducción porcentual de millas desperdiciadas por política (media e IC 95% entre réplicas).
    En cada réplica se asigna a cada solicitud la cita de un paciente real del conjunto de prueba."""
    rng = np.random.RandomState(semilla)
    n = len(dist)
    out = {pol: [] for pol in POLITICAS}
    for _ in range(replicas):
        idx = rng.randint(0, len(p_all), n)
        p, y = p_all[idx], y_all[idx]
        base = float((dist * y).sum())
        if base == 0:
            continue
        for pol in POLITICAS:     # "azar" consume el generador primero, como en el informe
            f = seleccionar(pol, p, y, dist, k, rng)
            out[pol].append(100 * reduccion * float((dist * y)[f].sum()) / base)
    return {pol: {"media": float(np.mean(v)), "ic95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]}
            for pol, v in out.items()}


def priorizar_lote(prob: np.ndarray, millas: np.ndarray | None, fraccion: float) -> np.ndarray:
    """Marca la fracción de visitas a confirmar primero: por riesgo × distancia si hay millas;
    si no, solo por riesgo. Devuelve un vector booleano."""
    k = max(1, int(round(fraccion * len(prob))))
    puntaje = prob * millas if millas is not None else prob
    marca = np.zeros(len(prob), dtype=bool)
    marca[np.argsort(-puntaje)[:k]] = True
    return marca

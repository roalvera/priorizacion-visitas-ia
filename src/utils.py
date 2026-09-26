"""Funciones auxiliares: configuración, rutas, logging y persistencia de resultados."""
from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any

import numpy as np
import yaml

RAIZ = Path(__file__).resolve().parents[1]


def ruta(relativa: str | Path) -> Path:
    """Convierte una ruta relativa a la raíz del repositorio en una ruta absoluta."""
    p = Path(relativa)
    return p if p.is_absolute() else RAIZ / p


def cargar_config(archivo: str | Path = "config.yaml") -> dict:
    """Lee config.yaml. Lanza un error informativo si no existe o está mal formado."""
    path = ruta(archivo)
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"config.yaml tiene un error de formato: {exc}") from exc


def obtener_logger(nombre: str = "priorizacion", archivo: str | Path | None = None) -> logging.Logger:
    """Logger con salida a consola y, opcionalmente, a archivo."""
    logger = logging.getLogger(nombre)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    consola = logging.StreamHandler()
    consola.setFormatter(fmt)
    logger.addHandler(consola)
    if archivo:
        destino = ruta(archivo)
        destino.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(destino, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


def fijar_semilla(semilla: int) -> None:
    random.seed(semilla)
    np.random.seed(semilla)


def _a_json(obj: Any):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return str(obj)


def guardar_json(datos: dict, archivo: str | Path) -> Path:
    destino = ruta(archivo)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=2, default=_a_json)
    return destino


def leer_json(archivo: str | Path) -> dict:
    with open(ruta(archivo), encoding="utf-8") as fh:
        return json.load(fh)


def haversine_millas(lat1, lon1, lat2, lon2):
    """Distancia de gran círculo en millas entre coordenadas (vectorizada)."""
    r = 3958.8
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))

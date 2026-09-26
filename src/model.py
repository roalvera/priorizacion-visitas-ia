"""Definición del modelo de riesgo de no-show y de los modelos de comparación."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .utils import ruta


def crear_gradient_boosting(semilla: int = 42, **params) -> HistGradientBoostingClassifier:
    """Gradient Boosting basado en histogramas (modelo final). Sin early stopping interno,
    para que el número de iteraciones sea un hiperparámetro explícito."""
    return HistGradientBoostingClassifier(early_stopping=False, random_state=semilla, **params)


def crear_random_forest(semilla: int = 42, **params) -> RandomForestClassifier:
    """Random Forest de comparación (por defecto: 300 árboles, profundidad 8, hoja mínima 20)."""
    base = {"n_estimators": 300, "max_depth": 8, "min_samples_leaf": 20}
    base.update(params)
    return RandomForestClassifier(random_state=semilla, n_jobs=-1, **base)


def crear_regresion_logistica():
    """Línea base interpretable (con estandarización)."""
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))


def asignar_grupo_edad(edades, grupos: list, etiquetas: list) -> np.ndarray:
    """Etiqueta de grupo de edad para cada paciente."""
    edades = np.asarray(edades, dtype=float)
    out = np.empty(len(edades), dtype=object)
    for (lo, hi), lab in zip(grupos, etiquetas):
        out[(edades >= lo) & (edades <= hi)] = lab
    return out


@dataclass
class ModeloRiesgo:
    """Modelo entrenado + umbrales de decisión + metadatos, serializable en un solo .pkl.

    * umbral_global: elegido con predicciones fuera de muestra para un recall objetivo.
    * umbrales_grupo: un umbral por grupo de edad (mitigación de la brecha de cobertura
      en adultos mayores), elegido con el mismo procedimiento dentro de cada grupo.
    """
    estimador: object
    features: list
    umbral_global: float
    umbrales_grupo: dict = field(default_factory=dict)
    grupos_edad: list = field(default_factory=list)
    etiquetas_grupos: list = field(default_factory=list)
    metadatos: dict = field(default_factory=dict)

    def _matriz(self, X: pd.DataFrame) -> pd.DataFrame:
        faltan = [c for c in self.features if c not in X.columns]
        if faltan:
            raise ValueError(f"Faltan variables para predecir: {faltan}")
        return X[self.features]

    def predecir_probabilidad(self, X: pd.DataFrame) -> np.ndarray:
        """Probabilidad de inasistencia (clase 1) para cada fila de X."""
        return self.estimador.predict_proba(self._matriz(X))[:, 1]

    def umbrales_por_fila(self, X: pd.DataFrame, mitigado: bool = True) -> np.ndarray:
        """Umbral que corresponde a cada fila: por grupo de edad si mitigado=True, si no el global."""
        if not mitigado or not self.umbrales_grupo:
            return np.full(len(X), self.umbral_global)
        grupos = asignar_grupo_edad(X["Age"], self.grupos_edad, self.etiquetas_grupos)
        return np.array([self.umbrales_grupo.get(g, self.umbral_global) for g in grupos])

    def clasificar(self, X: pd.DataFrame, mitigado: bool = True) -> np.ndarray:
        """1 = riesgo alto (se recomienda contacto proactivo de confirmación)."""
        return (self.predecir_probabilidad(X) >= self.umbrales_por_fila(X, mitigado)).astype(int)

    def guardar(self, path: str | Path) -> Path:
        """Serializa el modelo completo con joblib y devuelve la ruta."""
        destino = ruta(path)
        destino.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, destino)
        return destino

    @staticmethod
    def cargar(path: str | Path) -> "ModeloRiesgo":
        """Carga un ModeloRiesgo guardado, con errores informativos si falta o no es válido."""
        origen = ruta(path)
        if not origen.exists():
            raise FileNotFoundError(f"No existe el modelo {origen}. Ejecute primero: python -m src.train")
        modelo = joblib.load(origen)
        if not isinstance(modelo, ModeloRiesgo):
            raise TypeError("El archivo no contiene un ModeloRiesgo válido")
        return modelo

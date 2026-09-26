"""Diagnóstico de sobreajuste y subajuste (actividad de la Semana 3) aplicado al modelo del proyecto.

* ``RegistroMetricas``: tracking por iteración (árbol a árbol) de pérdida logarítmica, exactitud y AUC
  en entrenamiento y validación, usando ``staged_predict_proba`` de Gradient Boosting.
* ``cuantificar`` y ``diagnosticar``: traducen a números los patrones de las curvas (brecha, subida de la
  pérdida de validación desde su mínimo, nivel frente a un modelo sin información) con umbrales explícitos.
* ``curva_aprendizaje`` y ``curva_validacion``: envoltorios de scikit-learn con validación cruzada
  agrupada por paciente.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, learning_curve, validation_curve

EPS = 1e-7


def metricas_conjunto(y, prob, prefijo: str, umbral: float = 0.5) -> dict:
    """Pérdida logarítmica, exactitud y AUC de un conjunto."""
    prob = np.clip(np.asarray(prob, dtype=float), EPS, 1 - EPS)
    return {f"{prefijo}_loss": float(log_loss(y, prob, labels=[0, 1])),
            f"{prefijo}_acc": float(accuracy_score(y, (prob >= umbral).astype(int))),
            f"{prefijo}_auc": float(roc_auc_score(y, prob))}


class RegistroMetricas:
    """Registro de métricas por iteración, con utilidades de consulta y exportación."""

    def __init__(self, nombre: str):
        self.nombre = nombre
        self.historial: list[dict] = []

    def registrar(self, iteracion: int, **metricas) -> None:
        """Agrega las métricas de una iteración."""
        self.historial.append({"iteracion": int(iteracion), **{k: float(v) for k, v in metricas.items()}})

    def tabla(self) -> pd.DataFrame:
        """Historial como DataFrame."""
        return pd.DataFrame(self.historial)

    def mejor(self, metrica: str = "val_loss") -> dict:
        """Fila con el menor valor de la métrica (por defecto, pérdida de validación)."""
        df = self.tabla()
        return df.loc[df[metrica].idxmin()].to_dict()


def seguir_boosting(modelo, X_tr, y_tr, X_val, y_val, nombre: str, cada: int = 5) -> RegistroMetricas:
    """Tracking árbol a árbol de un Gradient Boosting ya entrenado (staged_predict_proba)."""
    reg = RegistroMetricas(nombre)
    etapas = zip(modelo.staged_predict_proba(X_tr), modelo.staged_predict_proba(X_val))
    for i, (p_tr, p_val) in enumerate(etapas, start=1):
        if i % cada and i != 1:
            continue
        reg.registrar(i, **metricas_conjunto(y_tr, p_tr[:, 1], "train"), **metricas_conjunto(y_val, p_val[:, 1], "val"))
    return reg


@dataclass
class Umbrales:
    """Umbrales del diagnóstico (ajustables)."""
    brecha_pequena: float = 0.02      # brecha de pérdida val - train considerada pequeña
    brecha_grande: float = 0.05
    subida_val: float = 0.02          # subida relativa de val_loss sobre su mínimo (2%)
    ratio_subajuste: float = 0.90     # train_loss / pérdida sin información por encima de esto = pérdida alta


def perdida_sin_informacion(prevalencia: float) -> float:
    """Pérdida logarítmica de un modelo que predice siempre la prevalencia."""
    return float(-(prevalencia * np.log(prevalencia) + (1 - prevalencia) * np.log(1 - prevalencia)))


def cuantificar(reg: RegistroMetricas, prevalencia: float) -> dict:
    """Métricas cuantitativas de una curva de entrenamiento."""
    df = reg.tabla()
    tr, va = df["train_loss"].to_numpy(), df["val_loss"].to_numpy()
    i = int(np.argmin(va))
    cola = max(3, len(df) // 4)
    return {"modelo": reg.nombre, "iteraciones": int(df["iteracion"].iloc[-1]),
            "mejor_iteracion": int(df["iteracion"].iloc[i]), "train_loss_final": float(tr[-1]),
            "val_loss_final": float(va[-1]), "val_loss_min": float(va[i]), "brecha_final": float(va[-1] - tr[-1]),
            "pendiente_brecha_final": float(np.polyfit(np.arange(cola), (va - tr)[-cola:], 1)[0]),
            "subida_val_pct": float(100 * (va[-1] - va[i]) / va[i]),
            "ratio_sin_informacion": float(tr[-1] / perdida_sin_informacion(prevalencia)),
            "train_auc_final": float(df["train_auc"].iloc[-1]), "val_auc_final": float(df["val_auc"].iloc[-1])}


def diagnosticar(q: dict, u: Umbrales = Umbrales()) -> tuple[str, str]:
    """Etiqueta (Overfitting, Underfitting, Óptimo o intermedio) y su justificación."""
    sube = q["subida_val_pct"] > 100 * u.subida_val
    grande = q["brecha_final"] > u.brecha_grande
    alta = q["ratio_sin_informacion"] > u.ratio_subajuste
    pequena = q["brecha_final"] <= u.brecha_pequena
    if sube and (grande or q["pendiente_brecha_final"] > 0):
        return "Overfitting", (f"val_loss sube {q['subida_val_pct']:.1f}% desde su mínimo (iteración "
                               f"{q['mejor_iteracion']}) y la brecha final es {q['brecha_final']:.3f}")
    if alta and pequena:
        return "Underfitting", (f"train_loss = {q['ratio_sin_informacion']:.0%} de la pérdida sin información "
                                f"y brecha pequeña ({q['brecha_final']:.3f})")
    if pequena and not sube:
        return "Óptimo", f"brecha {q['brecha_final']:.3f} y val_loss a {q['subida_val_pct']:.1f}% de su mínimo"
    return "Overfitting leve", f"brecha moderada ({q['brecha_final']:.3f})"


def umbrales_dict(u: Umbrales = Umbrales()) -> dict:
    """Umbrales del diagnóstico como diccionario (para reportes)."""
    return asdict(u)


def _cv(n_splits: int, semilla: int) -> StratifiedGroupKFold:
    return StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=semilla)


def curva_aprendizaje(estimador, X, y, grupos, tamanos=np.linspace(0.1, 1.0, 6), scoring: str = "roc_auc",
                      n_splits: int = 3, semilla: int = 42) -> pd.DataFrame:
    """Curva de aprendizaje por tamaño del conjunto de entrenamiento (CV agrupada por paciente)."""
    n, tr, va = learning_curve(estimador, X, y, groups=grupos, train_sizes=tamanos, cv=_cv(n_splits, semilla),
                               scoring=scoring, shuffle=True, random_state=semilla, n_jobs=1)
    signo = -1.0 if scoring.startswith("neg_") else 1.0
    return pd.DataFrame({"n": n, "train": signo * tr.mean(1), "train_de": tr.std(1),
                         "val": signo * va.mean(1), "val_de": va.std(1)})


def curva_validacion(estimador, X, y, grupos, parametro: str, valores, scoring: str = "roc_auc",
                     n_splits: int = 3, semilla: int = 42) -> pd.DataFrame:
    """Curva de validación de un hiperparámetro (CV agrupada por paciente)."""
    tr, va = validation_curve(estimador, X, y, groups=grupos, param_name=parametro, param_range=valores,
                              cv=_cv(n_splits, semilla), scoring=scoring, n_jobs=1)
    signo = -1.0 if scoring.startswith("neg_") else 1.0
    return pd.DataFrame({"valor": list(valores), "train": signo * tr.mean(1), "train_de": tr.std(1),
                         "val": signo * va.mean(1), "val_de": va.std(1)})

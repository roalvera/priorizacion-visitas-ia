"""Análisis de sensibilidad de hiperparámetros (Workshop S5).

1. Búsqueda aleatoria en un espacio amplio (escalas logarítmicas donde corresponde).
2. Sensibilidad de un factor a la vez alrededor de la configuración final.
3. Modelo sustituto (Random Forest) sobre configuración -> AUC de validación cruzada, que permite:
   * ranking de importancia de hiperparámetros (importancia por permutación en el sustituto),
   * gráficos de dependencia parcial (1D y 2D),
   * interacciones mediante el estadístico H de Friedman.
Toda la evaluación usa CV estratificada y agrupada por paciente sobre el conjunto de entrenamiento.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import partial_dependence, permutation_importance
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score

from .model import crear_gradient_boosting

HP = ["learning_rate", "max_depth", "max_iter", "min_samples_leaf", "l2_regularization", "max_leaf_nodes"]
LOG_HP = {"learning_rate", "min_samples_leaf", "l2_regularization"}
ENTEROS = {"max_depth", "max_iter", "min_samples_leaf", "max_leaf_nodes"}


def muestrear_configuraciones(espacio: dict, n: int, semilla: int) -> list[dict]:
    rng = np.random.RandomState(semilla)
    confs = []
    for _ in range(n):
        c = {}
        for hp in HP:
            lo, hi = espacio[hp]
            v = float(np.exp(rng.uniform(np.log(lo), np.log(hi)))) if hp in LOG_HP else float(rng.uniform(lo, hi))
            c[hp] = int(round(v)) if hp in ENTEROS else v
        confs.append(c)
    return confs


def configuraciones_un_factor(base: dict, niveles: dict) -> list[dict]:
    """Varía un hiperparámetro a la vez manteniendo el resto en la configuración base."""
    confs = []
    for hp, valores in niveles.items():
        for v in valores:
            c = dict(base)
            c[hp] = v
            c["_factor"] = hp
            confs.append(c)
    return confs


def evaluar_configuraciones(confs: list[dict], X, y, g, semilla: int, n_splits: int = 3, logger=None) -> pd.DataFrame:
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=semilla)
    filas = []
    for i, c in enumerate(confs):
        params = {k: v for k, v in c.items() if not k.startswith("_")}
        t0 = time.time()
        s = cross_val_score(crear_gradient_boosting(semilla, **params), X, y, groups=g, cv=cv,
                            scoring="roc_auc", n_jobs=1)
        filas.append({**c, "cv_auc": float(s.mean()), "cv_auc_de": float(s.std()), "segundos": time.time() - t0})
        if logger and (i + 1) % 10 == 0:
            logger.info("configuraciones evaluadas: %d/%d", i + 1, len(confs))
    return pd.DataFrame(filas)


def _transformar(df: pd.DataFrame) -> pd.DataFrame:
    X = df[HP].astype(float).copy()
    X["l2_regularization"] = X["l2_regularization"].clip(lower=1e-4)   # 0 (valor por defecto) -> límite inferior
    for hp in LOG_HP:
        X[hp] = np.log10(X[hp])
    return X


def ajustar_sustituto(resultados: pd.DataFrame, semilla: int = 42):
    X, y = _transformar(resultados), resultados["cv_auc"].values
    sust = RandomForestRegressor(n_estimators=500, min_samples_leaf=2, random_state=semilla).fit(X, y)
    return sust, X


def ranking_importancia(sust, X, y, semilla: int = 42) -> pd.DataFrame:
    pi = permutation_importance(sust, X, y, n_repeats=30, random_state=semilla)
    return pd.DataFrame({"hiperparametro": HP, "importancia": pi.importances_mean,
                         "de": pi.importances_std}).sort_values("importancia", ascending=False)


def dependencia_parcial(sust, X, hp: str, n: int = 25) -> pd.DataFrame:
    pd_ = partial_dependence(sust, X, [HP.index(hp)], grid_resolution=n, kind="average")
    grid = pd_["grid_values"][0]
    valores = 10 ** grid if hp in LOG_HP else grid
    return pd.DataFrame({"valor": valores, "auc_parcial": pd_["average"][0]})


def estadistico_h(sust, X, a: str, b: str, n: int = 12) -> float:
    """Estadístico H de Friedman para la interacción entre dos hiperparámetros (0 = sin interacción)."""
    ia, ib = HP.index(a), HP.index(b)
    pab = partial_dependence(sust, X, [(ia, ib)], grid_resolution=n, kind="average")
    f_ab = pab["average"][0]
    # Con la misma resolución, la rejilla 1D coincide con cada eje de la rejilla 2D
    f_a = partial_dependence(sust, X, [ia], grid_resolution=n, kind="average")["average"][0]
    f_b = partial_dependence(sust, X, [ib], grid_resolution=n, kind="average")["average"][0]
    f_ab = f_ab - f_ab.mean()
    f_a, f_b = f_a - f_a.mean(), f_b - f_b.mean()
    inter = f_ab - f_a[:, None] - f_b[None, :]
    return float(np.sqrt((inter ** 2).sum() / max((f_ab ** 2).sum(), 1e-12)))


NIVELES_UN_FACTOR = {
    "learning_rate": [0.01, 0.03, 0.05, 0.2, 0.3],
    "max_depth": [2, 3, 4, 7, 10],
    "max_iter": [50, 150, 200, 300, 400],
    "min_samples_leaf": [5, 20, 50, 200, 400],
    "l2_regularization": [0.001, 0.1, 1.0, 10.0],
    "max_leaf_nodes": [7, 15, 63],
}


def ejecutar(cfg: dict | None = None) -> pd.DataFrame:
    """Corre la búsqueda aleatoria y la sensibilidad de un factor; guarda los resultados en CSV.
    Uso:  python -m src.optimization"""
    from .evaluate import cargar_particiones
    from .data_processing import FEATURES
    from .utils import cargar_config, leer_json, obtener_logger, ruta

    cfg = cfg or cargar_config()
    log = obtener_logger(archivo=cfg["rutas"]["logs"])
    semilla = cfg["proyecto"]["semilla"]
    train, _ = cargar_particiones(cfg)
    X, y, g = train[FEATURES], train["no_show"], train["PatientId"]
    base = dict(leer_json(f"{cfg['rutas']['metricas']}/entrenamiento.json")["busqueda"]["gb_mejores_parametros"])
    base.update({"l2_regularization": 0.0, "max_leaf_nodes": 31})
    confs = [dict(base, _factor="base")] + configuraciones_un_factor(base, NIVELES_UN_FACTOR)
    aleatorias = muestrear_configuraciones(cfg["optimizacion"]["espacio"],
                                           cfg["optimizacion"]["n_configuraciones_aleatorias"], semilla)
    confs += [dict(c, _factor="aleatoria") for c in aleatorias]
    log.info("sensibilidad de hiperparámetros: %d configuraciones", len(confs))
    res = evaluar_configuraciones(confs, X, y, g, semilla, cfg["particion"]["pliegues_cv_busqueda"], log)
    res.rename(columns={"_factor": "tipo"}).to_csv(ruta(cfg["rutas"]["metricas"]) / "sensibilidad_hiperparametros.csv",
                                                  index=False)
    return res


if __name__ == "__main__":
    ejecutar()

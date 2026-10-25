"""Caso de falla documentado: citas cercanas de adultos de 50 a 58 años sin historial ni SMS.

Es el perfil típico de los falsos negativos (mediana: 54 años, 3 días de antelación, sin citas previas).
Uso:  python scripts/caso_de_falla.py   (guarda results/metrics/caso_falla.json)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_processing import FEATURES  # noqa: E402
from src.evaluate import cargar_particiones  # noqa: E402
from src.model import ModeloRiesgo  # noqa: E402
from src.utils import cargar_config, guardar_json  # noqa: E402

if __name__ == "__main__":
    cfg = cargar_config()
    modelo = ModeloRiesgo.cargar(cfg["rutas"]["mejor_modelo"])
    _, test = cargar_particiones(cfg)
    p = modelo.predecir_probabilidad(test[FEATURES])
    pred = p >= modelo.umbral_global
    fn = test[(~pred) & (test["no_show"] == 1)]
    s = test[test["Age"].between(50, 58) & test["lead_time_days"].between(1, 5) & (test["prior_appts"] == 0)
             & (test["SMS_received"] == 0)]
    ps = modelo.predecir_probabilidad(s[FEATURES])
    faltaron = s["no_show"].values == 1
    res = {"falsos_negativos": int(len(fn)),
           "fn_mediana": {c: float(fn[c].median()) for c in ["Age", "lead_time_days", "prior_appts"]},
           "fn_con_antelacion_hasta_7_dias": float((fn["lead_time_days"] <= 7).mean()),
           "fn_sin_historial": float((fn["prior_appts"] == 0).mean()),
           "perfil": "50 a 58 años, 1 a 5 días de antelación, sin historial, sin SMS",
           "citas_perfil": int(len(s)), "tasa_real_perfil": float(s["no_show"].mean()),
           "probabilidad_media_perfil": float(ps.mean()), "inasistencias_perfil": int(faltaron.sum()),
           "detectadas_umbral_global": int(((ps >= modelo.umbral_global) & faltaron).sum()),
           "detectadas_umbrales_por_edad": int(((ps >= modelo.umbrales_por_fila(s, mitigado=True)) & faltaron).sum())}
    guardar_json(res, Path(cfg["rutas"]["metricas"]) / "caso_falla.json")
    print(res)

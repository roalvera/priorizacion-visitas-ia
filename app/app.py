"""Interfaz Streamlit del Sistema Inteligente de Priorización de Visitas Domiciliarias.

Ejecutar desde la raíz del repositorio:  streamlit run app/app.py
"""
from __future__ import annotations

import io
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.data_processing import ETIQUETAS, FEATURES, registro_a_features, validar_lote, validar_registro  # noqa: E402
from src.model import ModeloRiesgo, asignar_grupo_edad  # noqa: E402
from src.simulation import priorizar_lote  # noqa: E402
from src.utils import cargar_config, obtener_logger  # noqa: E402

LOG = obtener_logger("app")
ASSETS = Path(__file__).resolve().parent / "assets"
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

st.set_page_config(page_title="Priorización de visitas domiciliarias", page_icon="🩺", layout="wide")
try:
    st.markdown(f"<style>{(ASSETS / 'estilo.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
except OSError:
    pass


# --------------------------------------------------------------------------- recursos
@st.cache_resource(show_spinner="Cargando el modelo...")
def cargar_recursos():
    cfg = cargar_config(RAIZ / "config.yaml")
    modelo = ModeloRiesgo.cargar(RAIZ / cfg["rutas"]["mejor_modelo"])
    with open(RAIZ / cfg["rutas"]["frecuencia_barrios"], encoding="utf-8") as fh:
        barrios = json.load(fh)
    with open(RAIZ / cfg["rutas"]["metricas"] / "evaluacion.json", encoding="utf-8") as fh:
        evaluacion = json.load(fh)
    with open(ASSETS / "ejemplos.json", encoding="utf-8") as fh:
        ejemplos = json.load(fh)
    import shap
    explicador = shap.TreeExplainer(modelo.estimador)
    return cfg, modelo, barrios, evaluacion, ejemplos, explicador


try:
    CFG, MODELO, BARRIOS, EVAL, EJEMPLOS, EXPLICADOR = cargar_recursos()
except Exception as exc:  # error de despliegue: se muestra un mensaje comprensible
    LOG.exception("no se pudieron cargar los recursos")
    st.error("No se pudo cargar el modelo o sus archivos de apoyo. Verifique que existan "
             "`models/best_model.pkl` y `results/metrics/evaluacion.json` (ejecute `python -m src.train` "
             "y `python -m src.evaluate`).")
    st.caption(f"Detalle técnico: {type(exc).__name__}")
    st.stop()

LISTA_BARRIOS = sorted(BARRIOS)
PREVALENCIA = 0.202

if "historial" not in st.session_state:
    st.session_state.historial = []


def aplicar_ejemplo(nombre: str) -> None:
    for k, v in EJEMPLOS[nombre]["valores"].items():
        st.session_state[f"in_{k}"] = v


def categoria(prob: float, umbral: float) -> tuple[str, str]:
    if prob >= umbral:
        return "Riesgo alto", "#C0392B"
    if prob >= umbral * 0.6:
        return "Riesgo moderado", "#E67E22"
    return "Riesgo bajo", "#1E8449"


def grafico_indicador(prob: float, umbral: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=100 * prob, number={"suffix": "%", "valueformat": ".1f"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#1F3A5F"},
               "steps": [{"range": [0, 100 * umbral * 0.6], "color": "#D5F5E3"},
                         {"range": [100 * umbral * 0.6, 100 * umbral], "color": "#FDEBD0"},
                         {"range": [100 * umbral, 100], "color": "#FADBD8"}],
               "threshold": {"line": {"color": "#C0392B", "width": 3}, "value": 100 * umbral}},
        title={"text": "Probabilidad estimada de inasistencia"}))
    fig.update_layout(height=270, margin=dict(l=20, r=20, t=60, b=10))
    return fig


def grafico_shap(fila: pd.DataFrame) -> go.Figure:
    valores = EXPLICADOR.shap_values(fila)[0]
    orden = np.argsort(np.abs(valores))[::-1][:8][::-1]
    nombres = [f"{ETIQUETAS[FEATURES[i]]} = {fila.iloc[0, i]:.3g}" for i in orden]
    colores = ["#C0392B" if valores[i] > 0 else "#1E8449" for i in orden]
    fig = go.Figure(go.Bar(x=valores[orden], y=nombres, orientation="h", marker_color=colores))
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=40, b=10),
                      title="¿Qué empuja esta predicción? (valores SHAP, escala log-odds)",
                      xaxis_title="← reduce el riesgo | aumenta el riesgo →")
    return fig


# --------------------------------------------------------------------------- encabezado
st.title("🩺 Priorización de visitas domiciliarias de salud")
st.markdown("Estima el **riesgo de inasistencia (no-show)** de una cita y ayuda a decidir **a quién confirmar "
            "primero**. Es una herramienta de apoyo: la decisión final siempre es del equipo de coordinación.")
st.warning("Prototipo académico entrenado con datos públicos de citas ambulatorias de Vitória, Brasil (2016). "
           "No usar para negar, retrasar ni cancelar atención de salud.", icon="⚠️")

with st.sidebar:
    st.header("⚙️ Configuración")
    mitigado = st.toggle("Umbral ajustado por grupo de edad (recomendado)", value=True,
                         help="Usa un umbral por grupo de edad para que cada grupo tenga una cobertura similar. "
                              "Corrige la brecha que el modelo muestra en adultos de 65 años o más.")
    fraccion = st.slider("Capacidad de confirmación (% del lote)", 5, 50, 20, 5,
                         help="Porcentaje de visitas del lote que el equipo puede confirmar por teléfono.") / 100
    st.divider()
    st.caption(f"Modelo: Gradient Boosting v{MODELO.metadatos.get('version', '1.0.0')} · "
               f"AUC en prueba {EVAL['auc_roc']:.3f}")
    st.caption("Tema claro u oscuro: menú ⋮ → Settings.")

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Predicción individual", "📋 Priorizar un lote (CSV)",
                                  "🕘 Historial de la sesión", "ℹ️ Acerca del modelo"])

# --------------------------------------------------------------------------- pestaña 1
with tab1:
    st.subheader("Datos de la cita")
    st.caption("¿Primera vez? Cargue un ejemplo con uno de estos botones y luego presione **Calcular riesgo**.")
    cols = st.columns(len(EJEMPLOS))
    for c, (nombre, ej) in zip(cols, EJEMPLOS.items()):
        c.button(f"Prueba con ejemplo: {nombre}", on_click=aplicar_ejemplo, args=(nombre,),
                 help=ej["descripcion"], width="stretch")

    with st.form("formulario"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Paciente**")
            sexo = st.selectbox("Sexo", ["Femenino", "Masculino"], key="in_sexo")
            edad = st.number_input("Edad (años)", min_value=0, max_value=115, step=1, key="in_edad",
                                   help="Entre 0 y 115 años.")
            barrio = st.selectbox("Barrio de residencia", ["(Otro / desconocido)"] + LISTA_BARRIOS, key="in_barrio")
            social = st.checkbox("Participa en programa social", key="in_social")
        with c2:
            st.markdown("**Condiciones registradas**")
            hta = st.checkbox("Hipertensión", key="in_hta")
            dm = st.checkbox("Diabetes", key="in_dm")
            alc = st.checkbox("Alcoholismo", key="in_alc")
            disc = st.checkbox("Discapacidad", key="in_disc")
        with c3:
            st.markdown("**Cita e historial**")
            antelacion = st.number_input("Días de antelación", min_value=0, max_value=365, step=1, key="in_antelacion",
                                         help="Días entre el agendamiento y la fecha de la cita.")
            dia = st.selectbox("Día de la cita", DIAS[:6], key="in_dia")
            sms = st.checkbox("Recibió recordatorio SMS", key="in_sms")
            previas = st.number_input("Citas previas ya realizadas", min_value=0, max_value=100, step=1, key="in_previas")
            faltas = st.number_input("De ellas, inasistencias", min_value=0, max_value=100, step=1, key="in_faltas")
        enviado = st.form_submit_button("Calcular riesgo", type="primary", width="stretch")

    if enviado:
        if faltas > previas:
            st.error("Las inasistencias previas no pueden ser más que las citas previas. Corrija los valores.")
        else:
            registro = {"gender_f": int(sexo == "Femenino"), "Age": edad, "Scholarship": int(social),
                        "Hipertension": int(hta), "Diabetes": int(dm), "Alcoholism": int(alc), "Handcap": int(disc),
                        "SMS_received": int(sms), "lead_time_days": antelacion, "appt_dow": DIAS.index(dia),
                        "prior_appts": previas, "prior_noshow_rate": (faltas / previas) if previas else 0.0,
                        "neighbourhood_freq": float(BARRIOS.get(barrio, 0.0))}
            errores = validar_registro(registro)
            if errores:
                for e in errores:
                    st.error(e)
            else:
                try:
                    with st.spinner("Calculando el riesgo..."):
                        X = registro_a_features(registro)
                        prob = float(MODELO.predecir_probabilidad(X)[0])
                        umbral = float(MODELO.umbrales_por_fila(X, mitigado)[0])
                        grupo = asignar_grupo_edad([edad], MODELO.grupos_edad, MODELO.etiquetas_grupos)[0]
                    cat, color = categoria(prob, umbral)
                    r1, r2 = st.columns([1, 1])
                    with r1:
                        st.plotly_chart(grafico_indicador(prob, umbral), width="stretch")
                    with r2:
                        st.markdown(f"<div class='tarjeta' style='border-left:6px solid {color}'>"
                                    f"<h3 style='color:{color};margin:0'>{cat}</h3>"
                                    f"<p>Probabilidad estimada: <b>{prob:.1%}</b> · confianza del modelo: "
                                    f"{max(prob, 1 - prob):.1%} en la clase predicha</p>"
                                    f"<p>Umbral aplicado: <b>{umbral:.1%}</b> "
                                    f"({'grupo de edad ' + grupo if mitigado else 'global'})</p>"
                                    f"<p>Tasa promedio de inasistencia en los datos: {PREVALENCIA:.1%}</p></div>",
                                    unsafe_allow_html=True)
                        if cat == "Riesgo alto":
                            st.info("Sugerencia: confirmar la visita por teléfono antes de programar el desplazamiento "
                                    "y ofrecer reprogramación si el paciente no está disponible.")
                        else:
                            st.info("Sugerencia: seguir el flujo habitual de confirmación.")
                    st.plotly_chart(grafico_shap(X), width="stretch")
                    st.caption("Barras rojas: variables que aumentan el riesgo estimado; verdes: lo reducen. "
                               "Es una explicación del modelo, no una relación causal.")
                    st.session_state.historial.append({"hora": datetime.now().strftime("%H:%M:%S"), "edad": edad,
                                                       "antelacion": antelacion, "sms": int(sms),
                                                       "probabilidad": round(prob, 4), "categoria": cat,
                                                       "umbral": round(umbral, 4)})
                    LOG.info("predicción individual: prob=%.3f categoría=%s", prob, cat)
                except Exception:
                    LOG.exception("error en predicción individual")
                    st.error("Ocurrió un problema al calcular el riesgo. Revise los datos e intente de nuevo.")

# --------------------------------------------------------------------------- pestaña 2
with tab2:
    st.subheader("Priorizar un lote de visitas")
    st.markdown("Suba un CSV con una fila por visita. Si incluye la columna opcional `millas` (distancia a la sede "
                "del NP), la priorización combina **riesgo × distancia**, que en la simulación del proyecto fue la "
                "política más eficiente; si no, prioriza solo por riesgo.")
    plantilla = pd.read_csv(ASSETS / "lote_ejemplo.csv")
    c1, c2 = st.columns(2)
    c1.download_button("Descargar plantilla CSV", plantilla.head(3).to_csv(index=False).encode("utf-8"),
                       "plantilla_visitas.csv", "text/csv", width="stretch")
    usar_ejemplo = c2.button("Prueba con ejemplo: lote de 50 visitas", width="stretch")
    archivo = st.file_uploader("Archivo CSV", type=["csv"], help="Columnas: " + ", ".join(
        [c for c in FEATURES if c != "chronic_count"]) + " y, opcionalmente, millas e id_visita.")
    lote = None
    if usar_ejemplo:
        st.session_state.lote = plantilla
    if archivo is not None:
        try:
            st.session_state.lote = pd.read_csv(archivo)
        except Exception:
            st.error("No se pudo leer el archivo. Verifique que sea un CSV separado por comas.")
    lote = st.session_state.get("lote")
    if lote is not None:
        validas, errores = validar_lote(lote)
        if errores:
            with st.expander(f"⚠️ {len(errores)} fila(s) con errores fueron excluidas", expanded=len(validas) == 0):
                for e in errores[:50]:
                    st.write(e)
        if len(validas):
            with st.spinner("Calculando riesgos del lote..."):
                X = validas.copy()
                X["chronic_count"] = X[["Hipertension", "Diabetes", "Alcoholism", "Handcap"]].sum(axis=1)
                prob = MODELO.predecir_probabilidad(X)
                umbral = MODELO.umbrales_por_fila(X, mitigado)
                millas = validas["millas"].astype(float).values if "millas" in validas else None
                marca = priorizar_lote(prob, millas, fraccion)
            salida = validas.copy()
            salida["probabilidad_no_show"] = prob.round(4)
            salida["riesgo_alto"] = (prob >= umbral).astype(int)
            salida["confirmar_primero"] = marca.astype(int)
            salida = salida.sort_values(["confirmar_primero", "probabilidad_no_show"], ascending=False)
            primeras = [c for c in ["id_visita", "probabilidad_no_show", "riesgo_alto", "confirmar_primero", "millas"]
                        if c in salida.columns]
            salida = salida[primeras + [c for c in salida.columns if c not in primeras]]
            m1, m2, m3 = st.columns(3)
            m1.metric("Visitas válidas", len(salida))
            m2.metric("Riesgo alto", int(salida["riesgo_alto"].sum()))
            m3.metric("A confirmar primero", int(salida["confirmar_primero"].sum()))
            fig = go.Figure(go.Histogram(x=salida["probabilidad_no_show"], nbinsx=20, marker_color="#1F3A5F"))
            fig.update_layout(height=280, title="Distribución del riesgo en el lote",
                              xaxis_title="Probabilidad de inasistencia", yaxis_title="Visitas",
                              margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, width="stretch")
            st.dataframe(salida, width="stretch", hide_index=True)
            st.download_button("Descargar resultados (CSV)", salida.to_csv(index=False).encode("utf-8"),
                               "priorizacion_visitas.csv", "text/csv", type="primary")

# --------------------------------------------------------------------------- pestaña 3
with tab3:
    st.subheader("Historial de predicciones de esta sesión")
    if not st.session_state.historial:
        st.info("Aún no hay predicciones. Use la pestaña **Predicción individual**.")
    else:
        hist = pd.DataFrame(st.session_state.historial)
        st.dataframe(hist, width="stretch", hide_index=True)
        fig = go.Figure(go.Bar(x=[f"#{i + 1} ({h})" for i, h in enumerate(hist["hora"])],
                               y=hist["probabilidad"], marker_color="#1F3A5F"))
        fig.add_scatter(x=[f"#{i + 1} ({h})" for i, h in enumerate(hist["hora"])], y=hist["umbral"],
                        mode="lines+markers", name="Umbral", line=dict(color="#C0392B", dash="dash"))
        fig.update_layout(height=300, title="Comparación de predicciones", yaxis_tickformat=".0%",
                          margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, width="stretch")
        c1, c2 = st.columns(2)
        c1.download_button("Descargar historial (CSV)", hist.to_csv(index=False).encode("utf-8"),
                           "historial_predicciones.csv", "text/csv", width="stretch")
        if c2.button("Borrar historial", width="stretch"):
            st.session_state.historial = []
            st.rerun()

# --------------------------------------------------------------------------- pestaña 4
with tab4:
    st.subheader("Acerca del modelo")
    st.markdown(
        "**Qué hace.** Estima la probabilidad de que un paciente no se presente a una cita, a partir de 13 variables "
        "demográficas, clínicas, de la cita y de su historial. El riesgo se usa para **ordenar el trabajo de "
        "confirmación**, no para decidir quién recibe atención.\n\n"
        "**Modelo.** Gradient Boosting basado en histogramas (scikit-learn), elegido por validación cruzada agrupada "
        "por paciente frente a regresión logística y Random Forest. Probabilidades bien calibradas.\n\n"
        "**Datos.** *Medical Appointment No Shows* (Hoppen, 2016, Kaggle, licencia CC BY-NC-SA 4.0): 110,526 citas "
        "de 62,298 pacientes. No se usa ningún dato real de programas IHA/HRA ni información protegida de salud.")
    m = st.columns(4)
    m[0].metric("AUC-ROC (prueba)", f"{EVAL['auc_roc']:.3f}")
    m[1].metric("AUC-PR (prueba)", f"{EVAL['auc_pr']:.3f}", help="Referencia sin información: 0.202")
    m[2].metric("Brier (prueba)", f"{EVAL['brier']:.3f}", help=f"Sin información: {EVAL['brier_sin_informacion']:.3f}")
    m[3].metric("Recall con umbral", f"{EVAL['umbral_global']['recall']:.1%}")
    st.markdown("**Equidad por grupo de edad (conjunto de prueba)**")
    eq = pd.DataFrame(EVAL["equidad"][:5])
    st.dataframe(pd.DataFrame({
        "Grupo": eq["grupo"], "Citas": eq["n"], "AUC": eq["auc"].round(3),
        "Recall (umbral global)": eq["recall_global"].map("{:.1%}".format),
        "Recall (umbral por grupo)": eq["recall_mitigado"].map("{:.1%}".format)}),
        hide_index=True, width="stretch")
    st.markdown("**Limitaciones y advertencias**")
    st.markdown(
        "- Entrenado con citas ambulatorias de Brasil (2016), **no** con visitas domiciliarias de Estados Unidos: "
        "las cifras no son extrapolables sin reentrenar con datos del programa real.\n"
        "- El modelo discrimina peor en adultos de 65 años o más; por eso el umbral por grupo viene activado.\n"
        "- AUC de 0.74: se equivoca con frecuencia. Úselo para ordenar llamadas, nunca para negar o retrasar atención.\n"
        "- Las explicaciones SHAP describen al modelo, no causas: por ejemplo, el SMS aparece asociado a más "
        "inasistencias solo porque se envía a citas con más antelación.\n"
        "- Licencia de datos no comercial: un uso real exige reentrenar con datos propios y autorizados.")
    st.caption("Autores: Romel Alberto Vera Macías y Jhon Henry Quimi Loza · Maestría en Inteligencia Artificial, UEES.")

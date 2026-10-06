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
for _ruta in (RAIZ, RAIZ / "app"):
    if str(_ruta) not in sys.path:
        sys.path.insert(0, str(_ruta))

from src.data_processing import ETIQUETAS, FEATURES, registro_a_features, validar_lote, validar_registro  # noqa: E402
from src.model import ModeloRiesgo, asignar_grupo_edad  # noqa: E402
from src.simulation import priorizar_lote  # noqa: E402
from src.utils import cargar_config, obtener_logger  # noqa: E402

from textos import TEXTOS  # noqa: E402

LOG = obtener_logger("app")
ASSETS = Path(__file__).resolve().parent / "assets"

st.set_page_config(page_title="Priorización de visitas / Visit prioritization", page_icon="🩺", layout="wide")
try:
    st.markdown(f"<style>{(ASSETS / 'estilo.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
except OSError:
    pass


IDIOMA = "en" if st.sidebar.radio("Idioma / Language", ["Español", "English"], horizontal=True,
                                  key="idioma") == "English" else "es"
T = TEXTOS[IDIOMA]
VARIABLES = T.get("variables", ETIQUETAS)


# --------------------------------------------------------------------------- recursos
@st.cache_resource(show_spinner="Cargando el modelo...")
def cargar_recursos():
    """Carga configuración, modelo, barrios, métricas, ejemplos y explicador SHAP (en caché)."""
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
    st.error(T["error_carga"])
    st.caption(T["detalle"].format(e=type(exc).__name__))
    st.stop()

LISTA_BARRIOS = sorted(BARRIOS)
PREVALENCIA = 0.202

if "historial" not in st.session_state:
    st.session_state.historial = []
if "revisiones" not in st.session_state:
    st.session_state.revisiones = []


def aplicar_ejemplo(nombre: str) -> None:
    """Carga en el formulario los valores de un ejemplo precargado."""
    for k, v in EJEMPLOS[nombre]["valores"].items():
        st.session_state[f"in_{k}"] = v


def categoria(prob: float, umbral: float) -> tuple[str, str, str]:
    """Categoría de riesgo (código, texto en el idioma activo y color)."""
    if prob >= umbral:
        return "alto", T["cat"]["alto"], "#C0392B"
    if prob >= umbral * 0.6:
        return "moderado", T["cat"]["moderado"], "#E67E22"
    return "bajo", T["cat"]["bajo"], "#1E8449"


def grafico_indicador(prob: float, umbral: float) -> go.Figure:
    """Indicador tipo velocímetro con la probabilidad y el umbral."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=100 * prob, number={"suffix": "%", "valueformat": ".1f"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#1F3A5F"},
               "steps": [{"range": [0, 100 * umbral * 0.6], "color": "#D5F5E3"},
                         {"range": [100 * umbral * 0.6, 100 * umbral], "color": "#FDEBD0"},
                         {"range": [100 * umbral, 100], "color": "#FADBD8"}],
               "threshold": {"line": {"color": "#C0392B", "width": 3}, "value": 100 * umbral}},
        title={"text": T["gauge"]}))
    fig.update_layout(height=270, margin=dict(l=20, r=20, t=60, b=10))
    return fig


def grafico_shap(fila: pd.DataFrame) -> go.Figure:
    """Contribuciones SHAP de las 8 variables más influyentes en una predicción."""
    valores = EXPLICADOR.shap_values(fila)[0]
    orden = np.argsort(np.abs(valores))[::-1][:8][::-1]
    nombres = [f"{VARIABLES[FEATURES[i]]} = {fila.iloc[0, i]:.3g}" for i in orden]
    colores = ["#C0392B" if valores[i] > 0 else "#1E8449" for i in orden]
    fig = go.Figure(go.Bar(x=valores[orden], y=nombres, orientation="h", marker_color=colores))
    fig.update_layout(height=330, margin=dict(l=10, r=10, t=40, b=10), title=T["shap_titulo"],
                      xaxis_title=T["shap_eje"])
    return fig


# --------------------------------------------------------------------------- encabezado
st.title(T["titulo"])
st.markdown(T["intro"])
st.warning(T["aviso"], icon="⚠️")
with st.expander(T["como_usar"]):
    st.markdown(T["instrucciones"])

with st.sidebar:
    st.header(T["config"])
    mitigado = st.toggle(T["mitigado"], value=True, help=T["mitigado_ayuda"])
    fraccion = st.slider(T["capacidad"], 5, 50, 20, 5, help=T["capacidad_ayuda"]) / 100
    st.divider()
    st.caption(T["modelo_pie"].format(v=MODELO.metadatos.get("version", "1.0.0"), auc=EVAL["auc_roc"]))
    st.caption(T["tema"])

tab1, tab2, tab3, tab4 = st.tabs(T["tabs"])

# --------------------------------------------------------------------------- pestaña 1
with tab1:
    st.subheader(T["datos_cita"])
    st.caption(T["primera_vez"])
    cols = st.columns(len(EJEMPLOS))
    for c, (nombre, ej) in zip(cols, EJEMPLOS.items()):
        c.button(T["prueba_ejemplo"].format(n=ej["etiqueta"][IDIOMA]), on_click=aplicar_ejemplo, args=(nombre,),
                 help=ej["descripcion"][IDIOMA], width="stretch")

    with st.form("formulario"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**{T['paciente']}**")
            sexo = st.selectbox(T["sexo"], ["F", "M"], format_func=lambda v: T["sexos"][v], key="in_sexo")
            edad = st.number_input(T["edad"], min_value=0, max_value=115, step=1, key="in_edad", help=T["edad_ayuda"])
            barrio = st.selectbox(T["barrio"], ["__otro__"] + LISTA_BARRIOS, key="in_barrio",
                                  format_func=lambda v: T["barrio_otro"] if v == "__otro__" else v)
            social = st.checkbox(T["social"], key="in_social")
        with c2:
            st.markdown(f"**{T['condiciones']}**")
            hta = st.checkbox(T["hta"], key="in_hta")
            dm = st.checkbox(T["dm"], key="in_dm")
            alc = st.checkbox(T["alc"], key="in_alc")
            disc = st.checkbox(T["disc"], key="in_disc")
        with c3:
            st.markdown(f"**{T['cita_hist']}**")
            antelacion = st.number_input(T["antelacion"], min_value=0, max_value=365, step=1, key="in_antelacion",
                                         help=T["antelacion_ayuda"])
            dia = st.selectbox(T["dia"], list(range(6)), format_func=lambda i: T["dias"][i], key="in_dia")
            sms = st.checkbox(T["sms"], key="in_sms")
            previas = st.number_input(T["previas"], min_value=0, max_value=100, step=1, key="in_previas")
            faltas = st.number_input(T["faltas"], min_value=0, max_value=100, step=1, key="in_faltas")
        enviado = st.form_submit_button(T["calcular"], type="primary", width="stretch")

    if enviado:
        if faltas > previas:
            st.error(T["error_faltas"])
        else:
            registro = {"gender_f": int(sexo == "F"), "Age": edad, "Scholarship": int(social),
                        "Hipertension": int(hta), "Diabetes": int(dm), "Alcoholism": int(alc), "Handcap": int(disc),
                        "SMS_received": int(sms), "lead_time_days": antelacion, "appt_dow": int(dia),
                        "prior_appts": previas, "prior_noshow_rate": (faltas / previas) if previas else 0.0,
                        "neighbourhood_freq": float(BARRIOS.get(barrio, 0.0))}
            errores = validar_registro(registro)
            if errores:
                for e in errores:
                    st.error(e)
            else:
                try:
                    with st.spinner(T["calculando"]):
                        X = registro_a_features(registro)
                        prob = float(MODELO.predecir_probabilidad(X)[0])
                        umbral = float(MODELO.umbrales_por_fila(X, mitigado)[0])
                        grupo = asignar_grupo_edad([edad], MODELO.grupos_edad, MODELO.etiquetas_grupos)[0]
                    codigo, cat, _ = categoria(prob, umbral)
                    st.session_state.historial.append({"hora": datetime.now().strftime("%H:%M:%S"), "edad": edad,
                                                       "antelacion": antelacion, "sms": int(sms),
                                                       "probabilidad": round(prob, 4), "categoria": cat,
                                                       "umbral": round(umbral, 4)})
                    # El resultado se guarda en la sesión para que siga visible al enviar una solicitud de revisión
                    st.session_state.ultimo = {"registro": registro, "prob": prob, "umbral": umbral, "grupo": grupo,
                                               "mitigado": mitigado, "n": len(st.session_state.historial)}
                    LOG.info("predicción individual: prob=%.3f categoría=%s", prob, codigo)
                except Exception:
                    LOG.exception("error en predicción individual")
                    st.error(T["error_general"])

    ultimo = st.session_state.get("ultimo")
    if ultimo:
        try:
            X = registro_a_features(ultimo["registro"])
            prob, umbral, grupo = ultimo["prob"], ultimo["umbral"], ultimo["grupo"]
            codigo, cat, color = categoria(prob, umbral)
            r1, r2 = st.columns([1, 1])
            with r1:
                st.plotly_chart(grafico_indicador(prob, umbral), width="stretch")
            with r2:
                tipo = f"{T['grupo_edad']} {T['grupos'].get(grupo, grupo)}" if ultimo["mitigado"] else T["global"]
                st.markdown(f"<div class='tarjeta' style='border-left:6px solid {color}'>"
                            f"<h3 style='color:{color};margin:0'>{cat}</h3>"
                            f"<p>{T['prob']}: <b>{prob:.1%}</b> · {T['prob_asistir']}: "
                            f"{1 - prob:.1%}</p>"
                            f"<p>{T['umbral_aplicado']}: <b>{umbral:.1%}</b> ({tipo})</p>"
                            f"<p>{T['tasa_ref']}: {PREVALENCIA:.1%}</p></div>",
                            unsafe_allow_html=True)
                st.info(T["sug_alto"] if codigo == "alto" else T["sug_normal"])
            st.plotly_chart(grafico_shap(X), width="stretch")
            st.caption(T["shap_nota"])

            # Canal de revisión humana (apelación): el usuario puede objetar la predicción
            with st.expander(T["rev_titulo"]):
                st.caption(T["rev_ayuda"])
                with st.form("form_revision", clear_on_submit=True):
                    motivo = st.selectbox(T["rev_motivo"], list(range(len(T["rev_motivos"]))),
                                          format_func=lambda i: T["rev_motivos"][i], key="rev_motivo")
                    comentario = st.text_area(T["rev_comentario"], max_chars=300, key="rev_comentario",
                                              help=T["rev_comentario_ayuda"])
                    enviar_rev = st.form_submit_button(T["rev_enviar"])
                if enviar_rev:
                    if motivo == len(T["rev_motivos"]) - 1 and not comentario.strip():
                        st.error(T["rev_error"])
                    else:
                        st.session_state.revisiones.append({
                            "solicitud": len(st.session_state.revisiones) + 1,
                            "hora": datetime.now().strftime("%H:%M:%S"),
                            "prediccion": f"#{ultimo['n']}", "probabilidad": round(prob, 4),
                            "categoria": cat, "umbral": round(umbral, 4),
                            "motivo": T["rev_motivos"][motivo], "comentario": comentario.strip(),
                            "estado": T["rev_estado"]})
                        # Se registra el evento sin el texto del comentario (minimización de datos)
                        LOG.info("solicitud de revisión registrada: motivo=%d prob=%.3f", motivo, prob)
                        st.success(T["rev_ok"].format(n=len(st.session_state.revisiones)))
        except Exception:
            LOG.exception("error al mostrar el resultado")
            st.error(T["error_general"])

# --------------------------------------------------------------------------- pestaña 2
with tab2:
    st.subheader(T["lote_titulo"])
    st.markdown(T["lote_intro"])
    plantilla = pd.read_csv(ASSETS / "lote_ejemplo.csv")
    c1, c2 = st.columns(2)
    c1.download_button(T["plantilla"], plantilla.head(3).to_csv(index=False).encode("utf-8"),
                       "plantilla_visitas.csv", "text/csv", width="stretch")
    usar_ejemplo = c2.button(T["lote_ejemplo"], width="stretch")
    archivo = st.file_uploader(T["archivo"], type=["csv"], help=T["archivo_ayuda"].format(
        c=", ".join(c for c in FEATURES if c != "chronic_count")))
    if usar_ejemplo:
        st.session_state.lote = plantilla
    if archivo is not None:
        try:
            st.session_state.lote = pd.read_csv(archivo)
        except Exception:
            LOG.warning("CSV ilegible cargado en la interfaz")
            st.error(T["error_csv"])
    lote = st.session_state.get("lote")
    if lote is not None:
        validas, errores = validar_lote(lote)
        if errores:
            with st.expander(T["filas_error"].format(n=len(errores)), expanded=len(validas) == 0):
                for e in errores[:50]:
                    st.write(e)
        if len(validas):
            with st.spinner(T["calc_lote"]):
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
            m1.metric(T["validas"], len(salida))
            m2.metric(T["riesgo_alto"], int(salida["riesgo_alto"].sum()))
            m3.metric(T["confirmar"], int(salida["confirmar_primero"].sum()))
            fig = go.Figure(go.Histogram(x=salida["probabilidad_no_show"], nbinsx=20, marker_color="#1F3A5F"))
            fig.update_layout(height=280, title=T["hist_lote"], xaxis_title=T["eje_prob"], yaxis_title=T["visitas"],
                              margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, width="stretch")
            st.dataframe(salida, width="stretch", hide_index=True)
            st.download_button(T["descargar_res"], salida.to_csv(index=False).encode("utf-8"),
                               "priorizacion_visitas.csv", "text/csv", type="primary")

# --------------------------------------------------------------------------- pestaña 3
with tab3:
    st.subheader(T["hist_titulo"])
    if not st.session_state.historial:
        st.info(T["hist_vacio"])
    else:
        hist = pd.DataFrame(st.session_state.historial)
        st.dataframe(hist, width="stretch", hide_index=True)
        etiquetas = [f"#{i + 1} ({h})" for i, h in enumerate(hist["hora"])]
        fig = go.Figure(go.Bar(x=etiquetas, y=hist["probabilidad"], marker_color="#1F3A5F", name=T["prob"]))
        fig.add_scatter(x=etiquetas, y=hist["umbral"], mode="lines+markers", name=T["umbral"],
                        line=dict(color="#C0392B", dash="dash"))
        fig.update_layout(height=300, title=T["comparacion"], yaxis_tickformat=".0%",
                          margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, width="stretch")
        c1, c2 = st.columns(2)
        c1.download_button(T["descargar_hist"], hist.to_csv(index=False).encode("utf-8"),
                           "historial_predicciones.csv", "text/csv", width="stretch")
        if c2.button(T["borrar_hist"], width="stretch"):
            st.session_state.historial = []
            st.session_state.revisiones = []
            st.session_state.pop("ultimo", None)
            st.rerun()
    st.subheader(T["rev_hist_titulo"])
    if not st.session_state.revisiones:
        st.info(T["rev_hist_vacio"])
    else:
        rev = pd.DataFrame(st.session_state.revisiones)
        st.dataframe(rev, width="stretch", hide_index=True)
        st.download_button(T["rev_descargar"], rev.to_csv(index=False).encode("utf-8"),
                           "solicitudes_revision.csv", "text/csv", type="primary")
        st.caption(T["rev_hist_nota"])

# --------------------------------------------------------------------------- pestaña 4
with tab4:
    st.subheader(T["acerca_titulo"])
    st.markdown(T["acerca"])
    m = st.columns(4)
    m[0].metric(T["m_auc"], f"{EVAL['auc_roc']:.3f}")
    m[1].metric(T["m_pr"], f"{EVAL['auc_pr']:.3f}", help=T["ref_sin_info"].format(v="0.202"))
    ref_brier = T["ref_sin_info"].format(v=f"{EVAL['brier_sin_informacion']:.3f}")
    m[2].metric(T["m_brier"], f"{EVAL['brier']:.3f}", help=ref_brier)
    m[3].metric(T["m_recall"], f"{EVAL['umbral_global']['recall']:.1%}")
    st.markdown(T["equidad"])
    eq = pd.DataFrame(EVAL["equidad"][:5])
    st.dataframe(pd.DataFrame({
        T["col_grupo"]: eq["grupo"].map(lambda g: T["grupos"].get(g, g)), T["col_citas"]: eq["n"],
        "AUC": eq["auc"].round(3),
        T["col_rg"]: eq["recall_global"].map("{:.1%}".format),
        T["col_rm"]: eq["recall_mitigado"].map("{:.1%}".format)}),
        hide_index=True, width="stretch")
    st.markdown(T["limitaciones"])
    st.markdown(T["lim_texto"])
    st.caption(T["autores"])

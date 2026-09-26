"""Textos de la interfaz en español e inglés."""

TEXTOS = {
    "es": {
        "titulo": "🩺 Priorización de visitas domiciliarias de salud",
        "intro": ("Estima el **riesgo de inasistencia (no-show)** de una cita y ayuda a decidir **a quién confirmar "
                  "primero**. Es una herramienta de apoyo: la decisión final siempre es del equipo de coordinación."),
        "aviso": ("Prototipo académico entrenado con datos públicos de citas ambulatorias de Vitória, Brasil (2016). "
                  "No usar para negar, retrasar ni cancelar atención de salud."),
        "como_usar": "📘 ¿Cómo usar esta herramienta?",
        "instrucciones": (
            "1. **Predicción individual:** presione un botón *Prueba con ejemplo* o complete el formulario y "
            "presione **Calcular riesgo**.\n"
            "2. **Lote:** en la pestaña *Priorizar un lote* descargue la plantilla o use el lote de ejemplo, suba su "
            "CSV y descargue el resultado ordenado.\n"
            "3. **Historial:** compare las predicciones de la sesión y expórtelas a CSV.\n"
            "4. **Acerca del modelo:** métricas, equidad y limitaciones.\n\n"
            "En la barra lateral puede cambiar el idioma, el tipo de umbral y la capacidad de confirmación. "
            "Pase el cursor sobre los íconos ⓘ para ver ayudas."),
        "config": "⚙️ Configuración", "idioma": "Idioma / Language",
        "mitigado": "Umbral ajustado por grupo de edad (recomendado)",
        "mitigado_ayuda": ("Usa un umbral por grupo de edad para que cada grupo tenga una cobertura similar. "
                           "Corrige la brecha que el modelo muestra en adultos de 65 años o más."),
        "capacidad": "Capacidad de confirmación (% del lote)",
        "capacidad_ayuda": "Porcentaje de visitas del lote que el equipo puede confirmar por teléfono.",
        "modelo_pie": "Modelo: Gradient Boosting v{v} · AUC en prueba {auc:.3f}",
        "tema": "Tema claro u oscuro: menú ⋮ → Settings.",
        "tabs": ["🔍 Predicción individual", "📋 Priorizar un lote (CSV)", "🕘 Historial de la sesión",
                 "ℹ️ Acerca del modelo"],
        "datos_cita": "Datos de la cita",
        "primera_vez": "¿Primera vez? Cargue un ejemplo con uno de estos botones y luego presione **Calcular riesgo**.",
        "prueba_ejemplo": "Prueba con ejemplo: {n}",
        "paciente": "Paciente", "condiciones": "Condiciones registradas", "cita_hist": "Cita e historial",
        "sexo": "Sexo", "sexos": {"F": "Femenino", "M": "Masculino"}, "edad": "Edad (años)",
        "edad_ayuda": "Entre 0 y 115 años.", "barrio": "Barrio de residencia", "barrio_otro": "(Otro / desconocido)",
        "social": "Participa en programa social", "hta": "Hipertensión", "dm": "Diabetes", "alc": "Alcoholismo",
        "disc": "Discapacidad", "antelacion": "Días de antelación",
        "antelacion_ayuda": "Días entre el agendamiento y la fecha de la cita.", "dia": "Día de la cita",
        "dias": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"],
        "sms": "Recibió recordatorio SMS", "previas": "Citas previas ya realizadas",
        "faltas": "De ellas, inasistencias",
        "calcular": "Calcular riesgo",
        "error_faltas": "Las inasistencias previas no pueden ser más que las citas previas. Corrija los valores.",
        "calculando": "Calculando el riesgo...",
        "cat": {"alto": "Riesgo alto", "moderado": "Riesgo moderado", "bajo": "Riesgo bajo"},
        "prob": "Probabilidad de inasistencia", "prob_asistir": "probabilidad de asistencia",
        "grupos": {},
        "umbral_aplicado": "Umbral aplicado", "grupo_edad": "grupo de edad", "global": "global",
        "tasa_ref": "Tasa promedio de inasistencia en los datos",
        "sug_alto": ("Sugerencia: confirmar la visita por teléfono antes de programar el desplazamiento y ofrecer "
                     "reprogramación si el paciente no está disponible."),
        "sug_normal": "Sugerencia: seguir el flujo habitual de confirmación.",
        "gauge": "Probabilidad estimada de inasistencia",
        "shap_titulo": "¿Qué empuja esta predicción? (valores SHAP, escala log-odds)",
        "shap_eje": "← reduce el riesgo | aumenta el riesgo →",
        "shap_nota": ("Barras rojas: variables que aumentan el riesgo estimado; verdes: lo reducen. Es una explicación "
                      "del modelo, no una relación causal."),
        "error_general": "Ocurrió un problema al calcular el riesgo. Revise los datos e intente de nuevo.",
        "lote_titulo": "Priorizar un lote de visitas",
        "lote_intro": ("Suba un CSV con una fila por visita. Si incluye la columna opcional `millas` (distancia a la "
                       "sede del NP), la priorización combina **riesgo × distancia**, que en la simulación del "
                       "proyecto fue la política más eficiente; si no, prioriza solo por riesgo."),
        "plantilla": "Descargar plantilla CSV", "lote_ejemplo": "Prueba con ejemplo: lote de 50 visitas",
        "archivo": "Archivo CSV", "archivo_ayuda": "Columnas: {c} y, opcionalmente, millas e id_visita.",
        "error_csv": "No se pudo leer el archivo. Verifique que sea un CSV separado por comas.",
        "filas_error": "⚠️ {n} fila(s) con errores fueron excluidas", "calc_lote": "Calculando riesgos del lote...",
        "validas": "Visitas válidas", "riesgo_alto": "Riesgo alto", "confirmar": "A confirmar primero",
        "hist_lote": "Distribución del riesgo en el lote", "eje_prob": "Probabilidad de inasistencia",
        "visitas": "Visitas", "descargar_res": "Descargar resultados (CSV)",
        "hist_titulo": "Historial de predicciones de esta sesión",
        "hist_vacio": "Aún no hay predicciones. Use la pestaña **Predicción individual**.",
        "comparacion": "Comparación de predicciones", "umbral": "Umbral",
        "descargar_hist": "Descargar historial (CSV)", "borrar_hist": "Borrar historial",
        "acerca_titulo": "Acerca del modelo",
        "acerca": (
            "**Qué hace.** Estima la probabilidad de que un paciente no se presente a una cita, a partir de 13 "
            "variables demográficas, clínicas, de la cita y de su historial. El riesgo se usa para **ordenar el "
            "trabajo de confirmación**, no para decidir quién recibe atención.\n\n"
            "**Modelo.** Gradient Boosting basado en histogramas (scikit-learn), elegido por validación cruzada "
            "agrupada por paciente frente a regresión logística y Random Forest. Probabilidades bien calibradas.\n\n"
            "**Datos.** *Medical Appointment No Shows* (Hoppen, 2016, Kaggle, licencia CC BY-NC-SA 4.0): 110,526 "
            "citas de 62,298 pacientes. No se usa ningún dato real de programas IHA/HRA ni información protegida de "
            "salud."),
        "m_auc": "AUC-ROC (prueba)", "m_pr": "AUC-PR (prueba)", "m_brier": "Brier (prueba)",
        "m_recall": "Recall con umbral", "ref_sin_info": "Referencia sin información: {v}",
        "equidad": "**Equidad por grupo de edad (conjunto de prueba)**",
        "col_grupo": "Grupo", "col_citas": "Citas", "col_rg": "Recall (umbral global)",
        "col_rm": "Recall (umbral por grupo)",
        "limitaciones": "**Limitaciones y advertencias**",
        "lim_texto": (
            "- Entrenado con citas ambulatorias de Brasil (2016), **no** con visitas domiciliarias de Estados Unidos: "
            "las cifras no son extrapolables sin reentrenar con datos del programa real.\n"
            "- El modelo discrimina peor en adultos de 65 años o más; por eso el umbral por grupo viene activado.\n"
            "- AUC de 0.74: se equivoca con frecuencia. Úselo para ordenar llamadas, nunca para negar o retrasar "
            "atención.\n"
            "- Las explicaciones SHAP describen al modelo, no causas: por ejemplo, el SMS aparece asociado a más "
            "inasistencias solo porque se envía a citas con más antelación.\n"
            "- Licencia de datos no comercial: un uso real exige reentrenar con datos propios y autorizados."),
        "autores": ("Autores: Romel Alberto Vera Macías y Jhon Henry Quimi Loza · Maestría en Inteligencia "
                    "Artificial, UEES."),
        "error_carga": ("No se pudo cargar el modelo o sus archivos de apoyo. Verifique que existan "
                        "`models/best_model.pkl` y `results/metrics/evaluacion.json` (ejecute `python -m src.train` "
                        "y `python -m src.evaluate`)."),
        "detalle": "Detalle técnico: {e}",
    },
    "en": {
        "titulo": "🩺 Home health visit prioritization",
        "intro": ("Estimates the **no-show risk** of an appointment and helps decide **whom to confirm first**. It is "
                  "a decision-support tool: the final decision always belongs to the scheduling team."),
        "aviso": ("Academic prototype trained on public outpatient appointment data from Vitória, Brazil (2016). "
                  "Do not use it to deny, delay or cancel health care."),
        "como_usar": "📘 How to use this tool",
        "instrucciones": (
            "1. **Single prediction:** click a *Try an example* button or fill in the form and click "
            "**Calculate risk**.\n"
            "2. **Batch:** in the *Prioritize a batch* tab, download the template or use the example batch, upload "
            "your CSV and download the sorted result.\n"
            "3. **History:** compare this session's predictions and export them to CSV.\n"
            "4. **About the model:** metrics, fairness and limitations.\n\n"
            "Use the sidebar to change the language, the threshold type and the confirmation capacity. "
            "Hover over the ⓘ icons for help."),
        "config": "⚙️ Settings", "idioma": "Idioma / Language",
        "mitigado": "Age-group adjusted threshold (recommended)",
        "mitigado_ayuda": ("Uses one threshold per age group so every group gets similar coverage. It corrects the "
                           "gap the model shows for adults aged 65 or older."),
        "capacidad": "Confirmation capacity (% of batch)",
        "capacidad_ayuda": "Share of the batch the team can confirm by phone.",
        "modelo_pie": "Model: Gradient Boosting v{v} · test AUC {auc:.3f}",
        "tema": "Light or dark theme: menu ⋮ → Settings.",
        "tabs": ["🔍 Single prediction", "📋 Prioritize a batch (CSV)", "🕘 Session history", "ℹ️ About the model"],
        "datos_cita": "Appointment data",
        "primera_vez": "First time? Load an example with one of these buttons and then click **Calculate risk**.",
        "prueba_ejemplo": "Try an example: {n}",
        "paciente": "Patient", "condiciones": "Recorded conditions", "cita_hist": "Appointment and history",
        "sexo": "Sex", "sexos": {"F": "Female", "M": "Male"}, "edad": "Age (years)", "edad_ayuda": "Between 0 and 115.",
        "barrio": "Neighborhood", "barrio_otro": "(Other / unknown)", "social": "Enrolled in a social program",
        "hta": "Hypertension", "dm": "Diabetes", "alc": "Alcoholism", "disc": "Disability",
        "antelacion": "Lead time (days)", "antelacion_ayuda": "Days between scheduling and the appointment date.",
        "dia": "Appointment day", "dias": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "sms": "Received SMS reminder", "previas": "Previous completed appointments", "faltas": "Of those, no-shows",
        "calcular": "Calculate risk",
        "error_faltas": "Previous no-shows cannot exceed previous appointments. Please correct the values.",
        "calculando": "Calculating risk...",
        "cat": {"alto": "High risk", "moderado": "Moderate risk", "bajo": "Low risk"},
        "prob": "No-show probability", "prob_asistir": "attendance probability",
        "grupos": {"0 a 18": "0 to 18", "19 a 35": "19 to 35", "36 a 55": "36 to 55", "56 a 64": "56 to 64",
                   "65 o más": "65 or older"},
        "umbral_aplicado": "Threshold applied", "grupo_edad": "age group", "global": "global",
        "tasa_ref": "Average no-show rate in the data",
        "sug_alto": ("Suggestion: confirm the visit by phone before scheduling the trip and offer rescheduling if the "
                     "patient is not available."),
        "sug_normal": "Suggestion: follow the usual confirmation workflow.",
        "gauge": "Estimated no-show probability",
        "shap_titulo": "What drives this prediction? (SHAP values, log-odds scale)",
        "shap_eje": "← lowers the risk | raises the risk →",
        "shap_nota": ("Red bars: variables that raise the estimated risk; green: they lower it. This explains the "
                      "model, not a causal relationship."),
        "error_general": "Something went wrong while calculating the risk. Check the data and try again.",
        "lote_titulo": "Prioritize a batch of visits",
        "lote_intro": ("Upload a CSV with one row per visit. If it includes the optional `millas` column (distance to "
                       "the NP base), prioritization combines **risk × distance**, the most efficient policy in the "
                       "project's simulation; otherwise it uses risk only."),
        "plantilla": "Download CSV template", "lote_ejemplo": "Try an example: batch of 50 visits",
        "archivo": "CSV file", "archivo_ayuda": "Columns: {c} and, optionally, millas and id_visita.",
        "error_csv": "The file could not be read. Make sure it is a comma-separated CSV.",
        "filas_error": "⚠️ {n} row(s) with errors were excluded", "calc_lote": "Calculating batch risks...",
        "validas": "Valid visits", "riesgo_alto": "High risk", "confirmar": "Confirm first",
        "hist_lote": "Risk distribution in the batch", "eje_prob": "No-show probability", "visitas": "Visits",
        "descargar_res": "Download results (CSV)",
        "hist_titulo": "Predictions in this session",
        "hist_vacio": "No predictions yet. Use the **Single prediction** tab.",
        "comparacion": "Prediction comparison", "umbral": "Threshold",
        "descargar_hist": "Download history (CSV)", "borrar_hist": "Clear history",
        "acerca_titulo": "About the model",
        "acerca": (
            "**What it does.** Estimates the probability that a patient will miss an appointment, from 13 demographic, "
            "clinical, appointment and history variables. The risk is used to **order confirmation work**, not to "
            "decide who receives care.\n\n"
            "**Model.** Histogram-based Gradient Boosting (scikit-learn), selected with patient-grouped "
            "cross-validation over logistic regression and Random Forest. Well-calibrated probabilities.\n\n"
            "**Data.** *Medical Appointment No Shows* (Hoppen, 2016, Kaggle, CC BY-NC-SA 4.0 license): 110,526 "
            "appointments from 62,298 patients. No real IHA/HRA program data or protected health information is used."),
        "m_auc": "ROC AUC (test)", "m_pr": "PR AUC (test)", "m_brier": "Brier (test)",
        "m_recall": "Recall at threshold", "ref_sin_info": "No-information reference: {v}",
        "equidad": "**Fairness by age group (test set)**",
        "col_grupo": "Group", "col_citas": "Appointments", "col_rg": "Recall (global threshold)",
        "col_rm": "Recall (group threshold)",
        "limitaciones": "**Limitations and warnings**",
        "lim_texto": (
            "- Trained on outpatient appointments from Brazil (2016), **not** on US home visits: the figures do not "
            "transfer without retraining on real program data.\n"
            "- The model discriminates worse for adults aged 65 or older; that is why the group threshold is on.\n"
            "- AUC of 0.74: it is often wrong. Use it to order calls, never to deny or delay care.\n"
            "- SHAP explanations describe the model, not causes: e.g., SMS looks associated with more no-shows only "
            "because it is sent to appointments booked further ahead.\n"
            "- Non-commercial data license: real use requires retraining on authorized data."),
        "autores": ("Authors: Romel Alberto Vera Macías and Jhon Henry Quimi Loza · Master's in Artificial "
                    "Intelligence, UEES."),
        "error_carga": ("The model or its support files could not be loaded. Check that `models/best_model.pkl` and "
                        "`results/metrics/evaluacion.json` exist (run `python -m src.train` and "
                        "`python -m src.evaluate`)."),
        "detalle": "Technical detail: {e}",
        "variables": {
            "gender_f": "Female", "Age": "Age", "Scholarship": "Social program", "Hipertension": "Hypertension",
            "Diabetes": "Diabetes", "Alcoholism": "Alcoholism", "Handcap": "Disability", "SMS_received": "SMS reminder",
            "lead_time_days": "Lead time (days)", "appt_dow": "Weekday", "chronic_count": "Chronic conditions",
            "prior_appts": "Previous appointments", "prior_noshow_rate": "Previous no-show rate",
            "neighbourhood_freq": "Neighborhood frequency"},
    },
}

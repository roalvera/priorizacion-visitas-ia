# Planificación del proyecto

## 1. Definición del problema

Los programas de valoración de salud en el hogar (In-Home Assessments, IHA, y Health Risk Assessments, HRA) que administran aseguradoras de Estados Unidos para afiliados de Medicare, Medicaid y Marketplace enfrentan dos problemas operativos:

1. **Inasistencias (no-show).** Una parte relevante de las visitas agendadas no se concreta porque el paciente no está disponible. La literatura reporta una tasa promedio cercana a 23% (Dantas et al., 2018).
2. **Asignación puramente geográfica.** El personal itinerante (Nurse Practitioners, NP) se asigna por cercanía, sin considerar el riesgo de que la visita termine en inasistencia. Una visita de alto riesgo recibe el mismo tratamiento que una de bajo riesgo.

**Pregunta de negocio:** ¿se puede usar un modelo de riesgo de inasistencia para decidir qué visitas confirmar primero y así reducir el desplazamiento desperdiciado del personal?

## 2. Objetivos

**General.** Desarrollar, evaluar y desplegar un sistema de IA que combine un modelo predictivo de riesgo de no-show con un motor de asignación geográfica, para priorizar las confirmaciones proactivas y reducir el desperdicio de recursos.

**Específicos.**

| # | Objetivo | Evidencia en el repositorio |
|---|---|---|
| 1 | Construir y evaluar un modelo de riesgo con datos públicos | `notebooks/03_modelado.ipynb`, `src/train.py` |
| 2 | Diseñar un entorno de simulación con geografía pública real | `src/simulation.py`, `data/raw/ohio_zcta_centroides_2023.csv` |
| 3 | Incorporar el riesgo como criterio de priorización frente al azar y a la distancia | `notebooks/05_evaluacion.ipynb` (5 políticas) |
| 4 | Evaluar con métricas adecuadas al desbalance y analizar sobreajuste, subajuste y sesgos | notebooks 03 y 05 |
| 5 | Optimizar hiperparámetros, umbral y calibración | `notebooks/04_optimizacion.ipynb`, `docs/optimizacion.md` |
| 6 | Mitigar la brecha de equidad detectada | umbrales por grupo de edad en `src/model.py` |
| 7 | Desplegar una interfaz utilizable | `app/app.py` |
| 8 | Analizar implicaciones éticas | `docs/consideraciones_eticas.md` |

**Preguntas de investigación.**
1. ¿Es posible predecir el riesgo de no-show con desempeño aceptable usando solo datos públicos?
2. ¿Qué variables son más predictivas y coincide con la literatura?
3. ¿Cuánto reduce el desplazamiento desperdiciado priorizar por riesgo, frente al azar y frente a usar solo la distancia, y qué implicaciones éticas tiene?

## 3. Relevancia

Cada visita fallida consume tiempo de viaje de personal clínico escaso. Cualquier reducción del desplazamiento no efectivo se traduce en más visitas completadas con la misma dotación y en mejor cobertura de afiliados que, en el caso de Medicare, son adultos mayores con necesidades de salud relevantes. El problema surge de la experiencia profesional de uno de los integrantes en programación de visitas IHA/HRA.

## 4. Alcance

**Incluye**
- Modelo de riesgo entrenado con 110,526 citas públicas (Hoppen, 2016).
- Simulación de asignación con ubicaciones públicas reales de Ohio (NPI Registry y Census Bureau).
- Interfaz Streamlit para predicción individual y priorización de lotes.
- Mitigación de la brecha de cobertura por edad.

**No incluye**
- Datos reales de pacientes ni de ningún empleador (ninguna PHI).
- Integración con sistemas de programación en producción.
- Ruteo multi-parada en tiempo real ni reoptimización ante cancelaciones.

## 5. Cronograma: planificado frente a real

| Semana | Planificado | Real |
|---|---|---|
| 1 | Tema, marco teórico, literatura, objetivos | Cumplido. El tema se basó en una herramienta de asignación heurística previa. |
| 2 | Limpieza de datos, EDA, arquitectura | Cumplido. Se detectó y corrigió una fuga temporal en las variables de historial: ahora solo usan citas ya atendidas al momento de agendar. |
| 3 | Entrenamiento de modelos | Cumplido. Se cambió la partición aleatoria por una partición **por paciente**. |
| 4 | Motor de asignación y simulación | Cumplido con ajustes. Se reemplazó un archivo de ZIP de terceros por fuentes oficiales (NPI Registry, consulta del 18/09/2026, y Gazetteer 2023). |
| 5 | Evaluación, optimización, sesgos | Cumplido. Se agregaron la política "solo distancia" y la re-ejecución de verificación (25/09/2026). |
| 6 | Ética, video, entrega | Ampliado: análisis de sensibilidad de hiperparámetros, SHAP, mitigación de equidad, interfaz Streamlit, pruebas unitarias y documentación del repositorio. |

## 6. Recursos

| Tipo | Recurso |
|---|---|
| Datos | Medical Appointment No Shows (Kaggle, CC BY-NC-SA 4.0); NPI Registry de CMS; Gazetteer ZCTA 2023 del Census Bureau |
| Hardware | Una computadora personal (el pipeline completo corre en CPU en unos 30 minutos, incluyendo la búsqueda de hiperparámetros) |
| Software | Python 3.12, scikit-learn 1.8, pandas 3.0, SHAP 0.52, statsmodels 0.15, Streamlit 1.64, Plotly 7.1, pytest 9.1 |
| Despliegue | Streamlit Community Cloud (gratuito) |

## 7. Riesgos y mitigación

| Riesgo | Impacto | Mitigación |
|---|---|---|
| El dataset público (Brasil, ambulatorio) no representa visitas domiciliarias de EE. UU. | Alto | Declararlo como limitación central; recomendar reentrenar con datos reales antes de cualquier uso |
| Fuga de información que infle las métricas | Alto | Historial sin fuga temporal, partición por paciente, umbral elegido fuera de la prueba; pruebas unitarias que lo verifican |
| Sesgo contra adultos mayores | Alto | Evaluación por subgrupos con IC bootstrap y umbrales por grupo de edad |
| Supuesto de efectividad de la intervención (25%) no medido | Medio | Tomarlo de un metaanálisis (Robotham et al., 2016) y presentar análisis de sensibilidad |
| Cambios en la API pública del NPI Registry | Bajo | Sedes fijadas en `config.yaml` para reproducibilidad exacta |
| Licencia no comercial del dataset | Medio | Uso exclusivamente académico; documentado en `data/README.md` |

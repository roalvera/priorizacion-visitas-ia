# Lista de verificación de la entrega final

Cada requisito de la guía *Proyecto Final: Sistema de IA Integral* y dónde se cumple en este repositorio. **Pendiente (equipo)** marca lo que solo el equipo puede completar: publicar, grabar y enlazar.

## 1. Repositorio de GitHub (60%)

### Estructura de carpetas requerida

| Requisito | Ubicación | Estado |
|---|---|---|
| README.md, requirements.txt, .gitignore, LICENSE | raíz | ✅ |
| docs/: planificacion, analisis_datos, arquitectura, optimizacion, consideraciones_eticas, manual_usuario | `docs/` | ✅ |
| data/raw, data/processed, data/README.md | `data/` | ✅ |
| notebooks 01_exploracion a 05_evaluacion | `notebooks/` (ejecutados, sin errores) | ✅ |
| src/: `__init__`, data_processing, model, train, evaluate, utils | `src/` (más diagnosis, optimization, simulation) | ✅ |
| models/: best_model.pkl, model_v1.pkl, README.md | `models/` | ✅ |
| app/: app.py, requirements.txt, assets/ | `app/` | ✅ |
| tests/: test_data_processing, test_model, test_app | `tests/` (18 pruebas) | ✅ |
| results/: figures, metrics, reports | `results/` | ✅ |
| Repositorio **público** | GitHub | Pendiente (equipo) |

### Contenido obligatorio del README

| # | Requisito | Sección del README | Estado |
|---|---|---|---|
| 1 | Título, badges, descripción de 2 a 3 oraciones | Encabezado | ✅ |
| 2 | Tabla de contenidos | Tabla de contenidos | ✅ |
| 3 | Problema, importancia, usuarios objetivo | 1 | ✅ |
| 4 | Dataset: descripción, fuente, licencia, tamaño, variables, enlace | 2 | ✅ |
| 5 | Metodología: modelo y justificación, preprocesamiento, optimización, métricas | 3 | ✅ |
| 6 | Resultados: accuracy, F1 y otras; comparación con baseline; tabla y gráfico | 4 | ✅ |
| 7 | Requisitos, instalación paso a paso, comandos, ejemplos de uso | 5 | ✅ |
| 8 | Interfaz: descripción, capturas, instrucciones | 6 | ✅ |
| 8 | Enlace a la aplicación desplegada | 6 | Pendiente (equipo) |
| 9 | Estructura del proyecto | 7 | ✅ |
| 10 | Ética: resumen, limitaciones, advertencias | 8 | ✅ |
| 11 | Autores y roles | 9 | ✅ |
| 12 | Licencia | 10 | ✅ |
| 13 | Agradecimientos y referencias | 11 | ✅ |
| 14 | Enlaces al video pitch y al video de preguntas | 12 | Pendiente (equipo) |

## 2. Interfaz de usuario (20%)

| Requisito | Implementación | Estado |
|---|---|---|
| Formulario de entrada | Pestaña *Predicción individual*; carga de CSV en *Priorizar un lote* | ✅ |
| Validación de inputs | `validar_registro` y `validar_lote`; rangos, tipos, columnas e inasistencias ≤ citas | ✅ |
| Botón para predecir | **Calcular riesgo** | ✅ |
| Indicador de carga | `st.spinner` en predicción y lote; carga inicial del modelo | ✅ |
| Manejo de errores | Mensajes claros, sin detalles técnicos; registro en el log | ✅ |
| Predicción clara | Tarjeta con categoría, sugerencia de acción | ✅ |
| Confianza o probabilidades | Probabilidad de inasistencia y de asistencia, umbral aplicado | ✅ |
| Visualizaciones | Indicador, gráfico SHAP, histograma del lote, comparación de historial (Plotly) | ✅ |
| Sección "Acerca de" con métricas y limitaciones | Pestaña *Acerca del modelo* | ✅ |
| Datos de ejemplo y botón "Prueba con ejemplo" | 3 pacientes y 1 lote de 50 visitas | ✅ |
| Valorado: responsive | Probado en celular (`app/assets/capturas/07_movil.png`) | ✅ |
| Valorado: tema claro u oscuro | Menú ⋮ → Settings | ✅ |
| Valorado: español e inglés | Selector *Idioma / Language* | ✅ |
| Valorado: exportación | CSV del lote y del historial | ✅ |
| Valorado: historial y comparación | Pestaña *Historial de la sesión* | ✅ |
| Valorado: visualizaciones interactivas | Plotly | ✅ |
| Valorado por el workshop de ética: canal de apelación | Botón *Solicitar revisión* en cada predicción, con descarga de solicitudes | ✅ |
| Sugerencia de la docente (workshop): equidad por sexo y proxies socioeconómicos | Tabla con AUC y recall [IC 95%] por sexo, Bolsa Família y vulnerabilidad del barrio en *Acerca del modelo* | ✅ |
| Instrucciones dentro de la app | Desplegable "¿Cómo usar esta herramienta?" y ayudas ⓘ | ✅ |
| Aplicación publicada | Streamlit Community Cloud | Pendiente (equipo) |

## 3. Documentación en docs/ (10%)

| Documento | Contenido exigido | Estado |
|---|---|---|
| planificacion.md | Problema y objetivos, relevancia, alcance, cronograma planificado frente a real, recursos, riesgos | ✅ |
| analisis_datos.md | Dataset, estadísticas, 8 gráficos (piden 5 a 6), patrones, correlaciones, outliers, decisiones de preprocesamiento, faltantes y desbalance | ✅ |
| arquitectura.md | Modelo y justificación, hiperparámetros, diagrama de flujo, pipeline, tecnologías con versiones | ✅ |
| optimizacion.md | Diagnóstico de la Semana 3; proceso del Workshop S5; rangos; sensibilidad; dependencia parcial; ranking; interacciones; configuración final; antes y después | ✅ |
| consideraciones_eticas.md | Los 8 apartados: sesgos, equidad (métricas por edad, sexo y proxies socioeconómicos, mitigación implementada y justificación del uso de la edad), privacidad (HIPAA, GDPR, CCPA), explicabilidad (SHAP), impacto, responsabilidad y monitoreo, uso dual, limitaciones | ✅ |
| manual_usuario.md | Guía paso a paso, capturas anotadas, cada funcionalidad, solución de problemas, preguntas frecuentes, contacto | ✅ |

## 4. Código fuente (10%)

| Requisito | Evidencia | Estado |
|---|---|---|
| PEP 8 | `pycodestyle src app tests scripts` sin errores (`setup.cfg`) | ✅ |
| Docstrings | Todas las funciones y clases públicas | ✅ |
| Modularidad y separación de responsabilidades | Procesamiento, modelo, entrenamiento, evaluación, diagnóstico, optimización, simulación; la app reutiliza `src/` | ✅ |
| Try-except, mensajes informativos, validación, logging | `utils.obtener_logger`, validaciones en `data_processing`, errores controlados en la app | ✅ |
| Configuración sin valores fijos y rutas relativas | `config.yaml`; `utils.ruta()` | ✅ |
| Commits descriptivos, ramas y tags | `main`, `develop`, 5 ramas de funcionalidades, tags `v1.0.0` y `v1.1.0` | ✅ |
| Commits frecuentes de ambos integrantes | Historial en GitHub | Pendiente (equipo) |
| requirements.txt con versiones | raíz y `app/` | ✅ |
| 3 a 5 pruebas como mínimo, documentación de cómo ejecutarlas | 18 pruebas; `pytest -v` en el README | ✅ |

## 5. Actividades del curso integradas

| Actividad | Dónde |
|---|---|
| Semana 3: diagnóstico de overfitting/underfitting (tracking, curvas A, B, C y D, diagnóstico cuantitativo, estrategias) | `notebooks/03_modelado.ipynb`, `src/diagnosis.py`, `docs/optimizacion.md` sección 1, figuras 21 a 24 |
| Workshop S5: optimización y sensibilidad de hiperparámetros | `notebooks/04_optimizacion.ipynb`, `src/optimization.py`, `docs/optimizacion.md` secciones 2 a 10, figuras 11 a 15 |

## 6. Videos (requisito)

| Requisito | Apoyo en el repositorio | Estado |
|---|---|---|
| Guion del pitch con los 7 bloques y tiempos | `results/reports/guion_pitch_5min.md` | ✅ |
| Preparación de respuestas | `results/reports/preparacion_preguntas.md` | ✅ |
| Informe escrito completo (APA) | `results/reports/informe_proyecto_integrador.docx` | ✅ |
| Workshop de impacto social y responsabilidad | `results/reports/workshop_impacto_social.pdf` | ✅ |
| Observaciones de la docente al workshop (95/100) | Corregidas en el workshop, el informe y el repositorio: beneficio de la simulación presentado como simulado y con origen de la distancia; sensibilidad 10%, 25% y 40%; grupos de edad consistentes (56 a 64 y 65 o más); AUC y recall con IC por sexo y proxies socioeconómicos; transferencia de dominio como riesgo prioritario con mitigación; justificación del uso de la edad frente a la norma de no discriminación; alcance de la cifra de 23%; efectividades medidas frente a esperadas | ✅ |
| Código QR del repositorio y de la app | `python scripts/generar_qr.py <url_repo> <url_app>` | Pendiente (equipo) |
| Diapositivas (8 a 10), grabación de al menos 720p con la app publicada | | Pendiente (equipo) |
| Video de respuestas, en orden y numeradas | | Pendiente (equipo) |

## 7. Causales de penalización revisadas

| Riesgo | Cómo se evita |
|---|---|
| Repositorio privado | Crear el repositorio como **público** |
| Interfaz no funcional | 4 pruebas de la app con AppTest; verificada en navegador y en celular |
| Documentación ética superficial | 8 apartados con métricas, mitigación implementada y plan de monitoreo |
| Código sin atribución | Referencias en el README; librerías de código abierto citadas |
| Datos fabricados | Datos públicos con fuente y licencia; la simulación está declarada como simulación en `data/README.md`, en la app y en la documentación |

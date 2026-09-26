# Sistema Inteligente de Priorización de Riesgo y Asignación de Visitas Domiciliarias de Salud

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.8-F7931E?logo=scikitlearn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.64-FF4B4B?logo=streamlit&logoColor=white)
![Pruebas](https://img.shields.io/badge/pruebas-14%20aprobadas-brightgreen)
![Licencia código](https://img.shields.io/badge/c%C3%B3digo-MIT-green)
![Licencia datos](https://img.shields.io/badge/datos-CC%20BY--NC--SA%204.0-lightgrey)

Sistema de IA que estima el riesgo de inasistencia (no-show) de una visita de valoración de salud y lo combina con la distancia para decidir **a quién confirmar primero**. Integra un modelo de Gradient Boosting con validación rigurosa, explicaciones SHAP, una mitigación de equidad por grupo de edad y una interfaz Streamlit lista para usar.

## Tabla de contenidos
1. [Descripción del problema](#1-descripción-del-problema)
2. [Dataset](#2-dataset)
3. [Metodología](#3-metodología)
4. [Resultados](#4-resultados)
5. [Instalación y uso](#5-instalación-y-uso)
6. [Interfaz de usuario](#6-interfaz-de-usuario)
7. [Estructura del proyecto](#7-estructura-del-proyecto)
8. [Consideraciones éticas](#8-consideraciones-éticas)
9. [Autores y contribuciones](#9-autores-y-contribuciones)
10. [Licencia](#10-licencia)
11. [Agradecimientos y referencias](#11-agradecimientos-y-referencias)
12. [Videos](#12-videos)

## 1. Descripción del problema

**¿Qué resuelve?** En los programas de valoración de salud en el hogar (IHA/HRA) de aseguradoras de EE. UU. para Medicare, Medicaid y Marketplace, una parte de las visitas no se concreta porque el paciente no está, y el personal itinerante (Nurse Practitioners) se asigna solo por cercanía. El sistema anticipa qué visitas tienen más riesgo de inasistencia y ordena las llamadas de confirmación antes de comprometer el desplazamiento.

**¿Por qué importa?** Cada visita fallida es tiempo de viaje perdido de personal clínico escaso. Menos desplazamiento inútil significa más visitas efectivas con la misma dotación y mejor cobertura de afiliados, muchos de ellos adultos mayores.

**Usuarios objetivo:** coordinadores y analistas de programación de visitas domiciliarias, y equipos de operaciones de salud que planifican rutas de personal itinerante.

## 2. Dataset

| | |
|---|---|
| Datos principales | *Medical Appointment No Shows* (Hoppen, 2016): 110,527 citas de 62,299 pacientes de la red pública de Vitória, Brasil (2016) |
| Enlace | https://www.kaggle.com/datasets/joniarroba/noshowappointments |
| Licencia | CC BY-NC-SA 4.0 (uso académico, no comercial) |
| Variables | 14 originales (sexo, edad, barrio, condiciones clínicas, SMS, fechas, no-show); 14 variables de modelo tras la ingeniería |
| Objetivo | `no_show` (20.2% de positivos) |
| Datos geográficos | Centroides ZCTA 2023 del U.S. Census Bureau (dominio público) y 15 códigos postales de NP del NPI Registry de CMS |

No se usa ningún dato real de pacientes ni de ningún empleador. El componente de asignación es una **simulación declarada** con ubicaciones públicas reales. Detalles y diccionario de variables: [`data/README.md`](data/README.md).

## 3. Metodología

- **Modelo:** `HistGradientBoostingClassifier`, elegido por validación cruzada frente a regresión logística y Random Forest. Justificación completa en [`docs/arquitectura.md`](docs/arquitectura.md).
- **Preprocesamiento:** limpieza de errores de captura; historial del paciente **sin fuga temporal** (solo citas ya atendidas al agendar); partición 75/25 **por paciente**; frecuencia de barrio calculada solo con entrenamiento. Ver [`docs/analisis_datos.md`](docs/analisis_datos.md).
- **Optimización:** rejilla con CV agrupada, análisis de sensibilidad de 68 configuraciones, ranking de importancia de hiperparámetros, dependencia parcial, interacciones (estadístico H), umbral elegido con predicciones fuera de muestra y verificación de calibración. Ver [`docs/optimizacion.md`](docs/optimizacion.md).
- **Métricas:** AUC-ROC, AUC-PR, Brier, precisión, recall y F1 con umbral explícito; AUC por subgrupo con IC bootstrap por paciente; reducción de millas desperdiciadas en una simulación de Monte Carlo (2,000 réplicas).
- **Explicabilidad y equidad:** SHAP (global y por predicción) y umbrales por grupo de edad para igualar la cobertura.

## 4. Resultados

**Modelo (conjunto de prueba: 27,631 citas de 15,662 pacientes no vistos)**

| Modelo | AUC-ROC | AUC-PR | Brier |
|---|---|---|---|
| Sin información (prevalencia) | 0.500 | 0.202 | 0.161 |
| Referencia: solo antelación | 0.702 | 0.311 | 0.156 |
| Regresión logística | 0.665 | 0.305 | 0.154 |
| Random Forest | 0.734 | 0.366 | 0.144 |
| **Gradient Boosting final** | **0.741** | **0.377** | **0.142** |

- Validación cruzada agrupada de 5 pliegues: AUC 0.735 ± 0.003.
- Con el umbral de 0.242: recall 0.710, precisión 0.334, F1 0.454 (con 0.5 el recall era 0.017).
- Variable más influyente: la antelación de la cita, seguida de la edad (permutación y SHAP coinciden).
- **Equidad:** con un umbral único, el sistema detectaba solo el 30.6% de las inasistencias de los adultos de 65 años o más; con umbrales por grupo, el recall de todos los grupos queda entre 70% y 74%.

![Curvas ROC](results/figures/09_roc.png)

**Sistema completo (simulación: priorizar el 20% de 300 visitas en Ohio; supuesto de 25% menos no-show por confirmación)**

| Política | Reducción de millas desperdiciadas (IC 95%) |
|---|---|
| Al azar | 5.0% (2.5 a 7.7) |
| Solo distancia (sin modelo) | 8.9% (5.3 a 12.1) |
| Por riesgo | 9.6% (6.6 a 13.0) |
| **Riesgo × distancia** | **12.6% (9.5 a 15.7)** |
| Cota óptima (conoce el desenlace) | 24.8% (23.6 a 25.0) |

El aporte del modelo es de unos 3.7 puntos sobre la mejor política sin modelo. **Dónde funciona peor:** dentro de un mismo tramo de antelación el AUC baja a 0.59 a 0.68 (el modelo se apoya mucho en la antelación) y en adultos mayores es 0.707. Análisis completo en [`notebooks/05_evaluacion.ipynb`](notebooks/05_evaluacion.ipynb).

## 5. Instalación y uso

**Requisitos:** Python 3.12, unos 2 GB de RAM y 500 MB de disco. Funciona en Windows, macOS y Linux, solo con CPU.

```bash
git clone https://github.com/<usuario>/priorizacion-visitas-ia.git
cd priorizacion-visitas-ia
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Ejecutar**

| Comando | Qué hace | Tiempo aprox. (CPU) |
|---|---|---|
| `streamlit run app/app.py` | Abre la interfaz (el modelo ya viene entrenado) | segundos |
| `python -m src.train` | Reentrena y guarda `models/*.pkl` | 3 min |
| `python -m src.evaluate` | Evalúa en prueba y guarda `results/metrics/evaluacion.json` | 1 min |
| `python -m src.optimization` | Análisis de sensibilidad de hiperparámetros | 10 a 20 min |
| `bash scripts/ejecutar_notebooks.sh` | Ejecuta los 5 notebooks en orden | 25 min |
| `pytest -v` | Corre las 14 pruebas unitarias | 10 s |

Los parámetros (rutas, semillas, rejillas, umbral objetivo, simulación) están en [`config.yaml`](config.yaml).

**Ejemplo de uso en Python**

```python
import pandas as pd
from src.model import ModeloRiesgo
from src.data_processing import registro_a_features

modelo = ModeloRiesgo.cargar("models/best_model.pkl")
cita = {"gender_f": 0, "Age": 23, "Scholarship": 1, "Hipertension": 0, "Diabetes": 0, "Alcoholism": 0,
        "Handcap": 0, "SMS_received": 1, "lead_time_days": 40, "appt_dow": 4, "prior_appts": 2,
        "prior_noshow_rate": 1.0, "neighbourhood_freq": 0.032}
X = registro_a_features(cita)
print(modelo.predecir_probabilidad(X))   # [0.527]
print(modelo.clasificar(X))              # [1] -> confirmar primero
```

## 6. Interfaz de usuario

Aplicación Streamlit con cuatro pestañas:
- **Predicción individual:** formulario validado, tres ejemplos precargados, indicador de probabilidad, categoría de riesgo, umbral aplicado y explicación SHAP del caso.
- **Priorizar un lote (CSV):** carga de archivo con validación por fila, plantilla descargable, lote de ejemplo, priorización por riesgo × distancia y descarga de resultados.
- **Historial de la sesión:** comparación de predicciones y exportación a CSV.
- **Acerca del modelo:** métricas, equidad por grupo de edad y limitaciones.

También incluye manejo de errores con mensajes claros, indicadores de carga, diseño adaptable a celular y tema claro u oscuro.

**Aplicación desplegada:** `https://<su-app>.streamlit.app` *(se completa al publicar en Streamlit Community Cloud)*

| Predicción individual | Priorización de un lote |
|---|---|
| ![Predicción](app/assets/capturas/02_prediccion.png) | ![Lote](app/assets/capturas/04_lote.png) |

Guía paso a paso, solución de problemas y preguntas frecuentes: [`docs/manual_usuario.md`](docs/manual_usuario.md).

## 7. Estructura del proyecto

```
priorizacion-visitas-ia/
├── README.md, requirements.txt, config.yaml, LICENSE, .gitignore
├── docs/          Planificación, EDA, arquitectura, optimización, ética y manual de usuario
├── data/          raw/ (datos públicos), processed/ (datos limpios), README.md (fuentes y diccionario)
├── notebooks/     01 exploración, 02 preprocesamiento, 03 modelado, 04 optimización, 05 evaluación
├── src/           data_processing, model, train, evaluate, optimization, simulation, utils
├── models/        best_model.pkl, model_v1.pkl, README.md
├── app/           app.py (Streamlit), requirements.txt, assets/ (ejemplos, estilos y capturas)
├── tests/         Pruebas de procesamiento, modelo e interfaz (pytest)
├── results/       figures/ (20 gráficos), metrics/ (JSON y CSV), reports/ (guion del pitch y preparación)
└── scripts/       Generación y ejecución de notebooks, código QR
```

## 8. Consideraciones éticas

- **Sesgos:** datos de otro país y otro tipo de cita; menos datos de adultos mayores; el barrio y el programa social funcionan como indicadores socioeconómicos.
- **Equidad:** brecha de cobertura en adultos de 65 años o más, **mitigada** con umbrales por grupo de edad (activados por defecto).
- **Privacidad:** datos públicos y anónimos, sin PHI; la app no almacena nada. Un uso real exigiría HIPAA (y GDPR o CCPA según jurisdicción).
- **Transparencia:** SHAP por predicción y advertencias sobre lo que *no* explica (el SMS no causa inasistencias).
- **Advertencia de uso:** el riesgo sirve para **ordenar llamadas de confirmación**. No debe usarse para negar, retrasar ni cancelar atención, ni con fines comerciales.

Análisis completo con los 8 apartados: [`docs/consideraciones_eticas.md`](docs/consideraciones_eticas.md).

## 9. Autores y contribuciones

| Integrante | Rol |
|---|---|
| **Romel Alberto Vera Macías** | Definición del problema y objetivos, arquitectura, modelo predictivo, simulación combinada de asignación y priorización |
| **Jhon Henry Quimi Loza** | Datos y metodología, motor de asignación geográfica, evaluación de sobreajuste y sesgos, optimización, reflexión ética |
| Ambos | Revisión de literatura, documentación, interfaz, pruebas y videos |

Maestría en Inteligencia Artificial, Universidad Espíritu Santo (UEES). Docente: Gladys María Villegas Rugel.

## 10. Licencia

Código bajo licencia [MIT](LICENSE). Los datos de citas y sus derivados se rigen por CC BY-NC-SA 4.0.

## 11. Agradecimientos y referencias

Gracias a Joni Hoppen por publicar el dataset, a CMS y al U.S. Census Bureau por sus datos abiertos, y a la comunidad de scikit-learn, SHAP y Streamlit.

- Beauchamp, T. L., y Childress, J. F. (2019). *Principles of biomedical ethics* (8.ª ed.). Oxford University Press.
- Dantas, L. F., Fleck, J. L., Cyrino Oliveira, F. L., y Hamacher, S. (2018). No-shows in appointment scheduling: A systematic literature review. *Health Policy, 122*(4), 412–421. https://doi.org/10.1016/j.healthpol.2018.02.002
- Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics, 29*(5), 1189–1232. https://doi.org/10.1214/aos/1013203451
- Hoppen, J. (2016). *Medical appointment no shows* [Conjunto de datos]. Kaggle. https://www.kaggle.com/datasets/joniarroba/noshowappointments
- James, G., Witten, D., Hastie, T., y Tibshirani, R. (2021). *An introduction to statistical learning* (2.ª ed.). Springer. https://doi.org/10.1007/978-1-0716-1418-1
- Lundberg, S. M., y Lee, S.-I. (2017). A unified approach to interpreting model predictions. En *Advances in Neural Information Processing Systems* (Vol. 30, pp. 4765–4774).
- Obermeyer, Z., Powers, B., Vogeli, C., y Mullainathan, S. (2019). Dissecting racial bias in an algorithm used to manage the health of populations. *Science, 366*(6464), 447–453. https://doi.org/10.1126/science.aax2342
- Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.
- Robotham, D., Satkunanathan, S., Reynolds, J., Stahl, D., y Wykes, T. (2016). Using digital notifications to improve attendance in clinic: Systematic review and meta-analysis. *BMJ Open, 6*(10), e012116. https://doi.org/10.1136/bmjopen-2016-012116

## 12. Videos

- **Video pitch (5 minutos):** `<enlace de YouTube no listado o Google Drive>`
- **Video de respuestas a las preguntas:** `<enlace>`

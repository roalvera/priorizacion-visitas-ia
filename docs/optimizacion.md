# Diagnóstico del ajuste (Semana 3) y optimización de hiperparámetros (Workshop S5)

Notebook: [`notebooks/04_optimizacion.ipynb`](../notebooks/04_optimizacion.ipynb). Código: [`src/optimization.py`](../src/optimization.py). Resultados crudos: [`results/metrics/sensibilidad_hiperparametros.csv`](../results/metrics/sensibilidad_hiperparametros.csv).

**Regla de oro:** toda la optimización usa **validación cruzada estratificada y agrupada por paciente sobre el conjunto de entrenamiento**. El conjunto de prueba solo se usa en la comparación final.

## 1. Diagnóstico de sobreajuste y subajuste (Semana 3)

Antes de optimizar, se diagnostica el ajuste del modelo con la metodología de la actividad de la Semana 3, aplicada al problema del proyecto. Notebook: [`notebooks/03_modelado.ipynb`](../notebooks/03_modelado.ipynb). Código: [`src/diagnosis.py`](../src/diagnosis.py). Resultados: [`results/metrics/diagnostico_ajuste.json`](../results/metrics/diagnostico_ajuste.json).

### 1.1 Tracking de métricas

`RegistroMetricas` guarda, árbol a árbol, la pérdida logarítmica, la exactitud y el AUC en entrenamiento y validación, usando `staged_predict_proba` de Gradient Boosting. La validación es el 20% del conjunto de entrenamiento separado **por paciente**; el conjunto de prueba no se usa en esta etapa. Para las curvas por tamaño de dataset y por hiperparámetro se usan `learning_curve` y `validation_curve` de scikit-learn con validación cruzada agrupada por paciente.

Se comparan tres regímenes:

| Régimen | Configuración |
|---|---|
| Complejo sin regularización | `max_depth=None`, `max_leaf_nodes=255`, `min_samples_leaf=1`, 300 árboles, tasa 0.1 |
| Muy simple | tocones (`max_depth=1`), tasa 0.01, 100 árboles |
| Configuración final | `max_depth=5`, `min_samples_leaf=100`, 100 árboles, tasa 0.1 |

### 1.2 Curvas de entrenamiento y validación (A: pérdida; B: exactitud y AUC)

![Curvas por iteración](../results/figures/21_curvas_entrenamiento_validacion.png)

### 1.3 Diagnóstico cuantitativo

Reglas con umbrales explícitos (`Umbrales` en `src/diagnosis.py`): **sobreajuste** si la pérdida de validación sube más de 2% desde su mínimo con brecha grande (más de 0.05) o creciente; **subajuste** si la pérdida de entrenamiento supera el 90% de la de un modelo sin información con brecha pequeña (0.02 o menos); **óptimo** si la brecha es pequeña y la validación no sube.

| Régimen | Mejor iteración | Pérdida train / val | Brecha | Subida de val_loss | Pérdida train vs. sin información | AUC train / val | Diagnóstico |
|---|---|---|---|---|---|---|---|
| Complejo sin regularización | 25 | 0.212 / 0.480 | +0.268 | 8.4% | 42% | 0.991 / 0.710 | **Overfitting** |
| Muy simple | 100 | 0.465 / 0.463 | −0.002 | 0.0% | 92% | 0.687 / 0.690 | **Underfitting** |
| Configuración final | 95 | 0.429 / 0.438 | +0.010 | 0.0% | 85% | 0.760 / 0.738 | **Óptimo** |

- **Sobreajuste:** la pérdida de validación es mínima en el árbol 25 y luego sube mientras la de entrenamiento sigue bajando; el AUC de entrenamiento llega a 0.99 y el de validación cae a 0.71. Aparecen los tres síntomas de la guía.
- **Subajuste:** ambas curvas convergen a una pérdida alta, la brecha es nula y la exactitud queda fija en la de la clase mayoritaria (el modelo nunca predice inasistencia con umbral 0.5).
- **Óptimo:** brecha pequeña y estable, y la validación todavía mejora levemente al final. Esto justifica el análisis de sensibilidad de las secciones siguientes.

### 1.4 Curvas de aprendizaje por tamaño de dataset (C)

![Curvas por tamaño](../results/figures/22_curvas_aprendizaje_tamano.png)

| Régimen | AUC val con 10% de los datos | AUC val con 100% | Brecha final |
|---|---|---|---|
| Complejo sin regularización | 0.679 | 0.709 | 0.285 |
| Muy simple | 0.688 | 0.681 | 0.001 |
| Configuración final | 0.720 | 0.736 | 0.029 |

El modelo complejo mejora con más datos, pero mantiene una brecha enorme (alta varianza). El modelo simple no mejora con más datos (alto sesgo: hace falta más capacidad, no más datos). La configuración final aprovecha los datos con una brecha pequeña.

### 1.5 Curvas de validación por hiperparámetro (D)

![Curvas de validación](../results/figures/23_curvas_validacion_hiperparametros.png)

- `max_depth`: con profundidad 1 subajusta (AUC val 0.725); el óptimo es 5 (0.736); de ahí en adelante el AUC de entrenamiento sigue subiendo (hasta 0.781) sin mejorar la validación, señal de sobreajuste creciente.
- `learning_rate`: el óptimo es 0.1 (0.736); con 0.7 el AUC de validación cae a 0.719 mientras el de entrenamiento sube a 0.807.

### 1.6 Estrategias de mejora aplicadas

| Modelo | Pérdida val | Brecha | AUC val | Diagnóstico |
|---|---|---|---|---|
| Base con sobreajuste | 0.480 | 0.268 | 0.710 | Overfitting |
| E1 early stopping en la mejor iteración (25 árboles) | 0.443 | 0.049 | 0.730 | Overfitting leve |
| E2 regularización (L2 = 10, hoja mínima 200) | 0.461 | 0.127 | 0.720 | Overfitting |
| E3 menor complejidad (profundidad 5, hoja 100, 100 árboles) | **0.438** | **0.010** | **0.738** | **Óptimo** |
| Base con subajuste | 0.463 | −0.002 | 0.690 | Underfitting |
| U1 más capacidad y mayor tasa (configuración final) | **0.438** | **0.010** | **0.738** | **Óptimo** |

![Estrategias](../results/figures/24_estrategias_diagnostico.png)

El early stopping corrige la mayor parte del sobreajuste; la regularización por sí sola lo reduce pero no lo elimina con 300 árboles; limitar la complejidad del árbol es lo más efectivo. Por el lado del subajuste, aumentar la capacidad y la tasa lleva al mismo punto. Ambas correcciones convergen en la configuración final, que es la que se optimiza a continuación.

## 2. Proceso

| Etapa | Qué se hizo | Configuraciones |
|---|---|---|
| 1. Selección del modelo | Rejilla para Gradient Boosting y Random Forest (CV de 3 pliegues) | 16 + 6 |
| 2. Sensibilidad de un factor a la vez | Variar cada hiperparámetro alrededor de la configuración elegida | 28 (incluida la base) |
| 3. Búsqueda aleatoria amplia | Muestreo en todo el espacio (escala logarítmica para tasa, hoja y L2) | 40 |
| 4. Modelo sustituto | Random Forest que aprende configuración → AUC (R² = 0.81) para el ranking, la dependencia parcial y las interacciones | 68 puntos |
| 5. Umbral de decisión | Predicciones fuera de muestra (CV de 5 pliegues) con recall objetivo de 70% | |
| 6. Calibración | Verificación con curva de confiabilidad y puntaje de Brier | |

## 3. Hiperparámetros explorados y rangos

| Hiperparámetro | Rango (búsqueda aleatoria) | Niveles de un factor | Valor final |
|---|---|---|---|
| `learning_rate` | 0.01 a 0.3 (log) | 0.01, 0.03, 0.05, **0.10**, 0.2, 0.3 | 0.10 |
| `max_depth` | 2 a 10 | 2, 3, 4, **5**, 7, 10 | 5 |
| `max_iter` | 50 a 400 | 50, **100**, 150, 200, 300, 400 | 100 |
| `min_samples_leaf` | 5 a 400 (log) | 5, 20, 50, **100**, 200, 400 | 100 |
| `l2_regularization` | 0.0001 a 10 (log) | **0**, 0.001, 0.1, 1, 10 | 0 |
| `max_leaf_nodes` | 7 a 63 | 7, 15, **31**, 63 | 31 |

## 4. Resultados del análisis de sensibilidad

Las 68 configuraciones obtienen un AUC de validación cruzada entre 0.714 y 0.736 (mediana 0.735). El desempeño forma una **meseta amplia**: la mayoría de las configuraciones razonables quedan a menos de 0.002 del máximo.

![Sensibilidad de un factor a la vez](../results/figures/11_sensibilidad_un_factor.png)

| Hiperparámetro | Rango de AUC al variarlo solo | Lectura |
|---|---|---|
| `learning_rate` | 0.0049 | El más sensible: muy bajo (0.01) no alcanza a aprender en 100 árboles; muy alto (0.3) sobreajusta |
| `max_depth` | 0.0044 | Profundidad 2 subajusta; de 4 en adelante es casi plano |
| `max_iter` | 0.0031 | Más de 200 árboles empeora ligeramente (sobreajuste por iteraciones) |
| `min_samples_leaf`, `max_leaf_nodes`, `l2_regularization` | 0.0007 cada uno | Prácticamente indiferentes en sus rangos |

## 5. Dependencia parcial

![Dependencia parcial](../results/figures/13_dependencia_parcial.png)

Observe las escalas: solo `learning_rate` y `max_depth` mueven el AUC parcial en más de 0.001. La tasa de aprendizaje tiene una zona óptima entre 0.03 y 0.12 y cae bruscamente sobre 0.2; la profundidad mejora hasta 4 o 5 y luego se estabiliza; el número de árboles tiene su mejor zona entre 90 y 130.

## 6. Ranking de importancia de hiperparámetros

![Ranking](../results/figures/12_ranking_hiperparametros.png)

| Posición | Hiperparámetro | Importancia (permutación en el sustituto) |
|---|---|---|
| 1 | `learning_rate` | 0.951 |
| 2 | `max_depth` | 0.114 |
| 3 | `max_iter` | 0.088 |
| 4 | `max_leaf_nodes` | 0.082 |
| 5 | `min_samples_leaf` | 0.032 |
| 6 | `l2_regularization` | 0.016 |

La tasa de aprendizaje concentra la mayor parte del efecto. El ranking coincide con el de la sensibilidad de un factor a la vez en las tres primeras posiciones.

## 7. Análisis de interacciones

Estadístico H de Friedman sobre el sustituto (0 = efectos aditivos):

| Par | H |
|---|---|
| `learning_rate` × `max_iter` | 0.135 |
| `learning_rate` × `max_depth` | 0.123 |
| `max_depth` × `max_leaf_nodes` | 0.070 |
| `max_depth` × `max_iter` | 0.067 |

![Interacción](../results/figures/14_interaccion.png)

La interacción más fuerte es la esperada en boosting: **tasa de aprendizaje × número de árboles**. Con una tasa baja hacen falta muchos más árboles, y con una tasa alta, muchos árboles sobreajustan. Por eso ambos deben ajustarse juntos y no por separado.

## 8. Configuración final y justificación

**Final:** `learning_rate=0.1`, `max_depth=5`, `max_iter=100`, `min_samples_leaf=100` (CV AUC 0.7359).

La mejor configuración de toda la búsqueda solo cambia `l2_regularization` a 1.0 y logra 0.7362: una diferencia de **0.0003**, diez veces menor que la desviación estándar entre pliegues (0.003). No se cambia la configuración porque:
1. La mejora no es distinguible del ruido de la validación cruzada.
2. La configuración final está en el centro de la meseta, lejos de las zonas de caída (tasa > 0.2, profundidad 2, más de 300 árboles), lo que la hace robusta.
3. Mantenerla conserva la trazabilidad con el informe escrito.

**Hallazgo principal:** el desempeño está limitado por la información de las variables, no por los hiperparámetros.

## 9. Umbral de decisión y calibración

![Umbral](../results/figures/15_umbral.png)

Con el umbral por defecto de 0.5 el modelo detecta solo el 1.7% de las inasistencias, porque pocas citas superan el 50% de probabilidad (la prevalencia es 20%). El umbral de **0.242**, elegido con predicciones fuera de muestra para un recall de 70%, detecta el 71.0% en prueba. Las probabilidades están bien calibradas (Brier 0.142 frente a 0.161 sin información; brecha media por decil 0.006), por lo que no se aplicó recalibración.

## 10. Comparación antes y después (conjunto de prueba)

| Modelo | AUC-ROC | AUC-PR | Brier | Umbral | Recall | Precisión |
|---|---|---|---|---|---|---|
| v1: valores por defecto, umbral 0.5 | 0.740 | 0.376 | 0.143 | 0.500 | 0.022 | 0.573 |
| **Final: rejilla + umbral fuera de muestra** | **0.741** | **0.377** | **0.142** | **0.242** | **0.710** | **0.334** |

La optimización de hiperparámetros aporta poco al AUC (+0.002), coherente con la meseta observada. La mejora operativa grande viene del **umbral**: el recall pasa de 2% a 71%. A esto se suma la mitigación de equidad (umbrales por grupo de edad), descrita en [`consideraciones_eticas.md`](consideraciones_eticas.md).

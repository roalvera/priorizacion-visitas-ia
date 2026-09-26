# Consideraciones éticas

El análisis se organiza con los cuatro principios de la ética biomédica (autonomía, no maleficencia, beneficencia y justicia; Beauchamp y Childress, 2019), porque el sistema opera en un contexto de acceso a servicios de salud.

## 1. Análisis de sesgos

**¿El dataset tiene sesgos?** Sí, y conviene nombrarlos:

| Sesgo | Descripción | Posible efecto |
|---|---|---|
| De población | Citas ambulatorias de la red pública de Vitória (Brasil), 2016. No son visitas domiciliarias de Medicare/Medicaid en EE. UU. | Las cifras no son extrapolables al caso de uso real sin reentrenar |
| Demográfico | 65% de las citas son de mujeres; los adultos de 65 años o más son solo 13% de la prueba (3,594 citas) | Menos datos del grupo más relevante para Medicare y peor desempeño en él |
| Socioeconómico | El programa social (Bolsa Família) y el barrio actúan como indicadores indirectos de nivel socioeconómico | El modelo puede asignar más riesgo a personas de barrios pobres |
| De registro | Las condiciones clínicas se registran solo como presencia o ausencia; la discapacidad se simplificó a binaria | Información clínica incompleta |
| De intervención | El SMS no se asignó al azar, sino a citas con más antelación | Asociación engañosa: sin controlar, el SMS parece aumentar el no-show |

**Grupos que podrían ser perjudicados:** adultos mayores (el modelo los detecta peor) y residentes de barrios con más inasistencia histórica (reciben más contactos, lo que puede sentirse como vigilancia).

## 2. Equidad (fairness)

**Métricas evaluadas en el conjunto de prueba**, con intervalos de confianza por bootstrap por paciente (300 remuestreos):

| Grupo | Citas | AUC [IC 95%] | Recall con umbral único | Recall con umbral por grupo | % señalado (único → por grupo) |
|---|---|---|---|---|---|
| 0 a 18 | 7,356 | 0.745 [0.732, 0.757] | 82.3% | 70.3% | 53.0% → 41.7% |
| 19 a 35 | 6,029 | 0.736 [0.724, 0.750] | 90.9% | 72.9% | 62.4% → 46.4% |
| 36 a 55 | 7,428 | 0.730 [0.713, 0.747] | 68.5% | 70.4% | 42.9% → 44.5% |
| 56 a 64 | 3,224 | 0.714 [0.681, 0.739] | 31.7% | 72.3% | 14.9% → 46.7% |
| **65 o más** | 3,594 | **0.707 [0.684, 0.729]** | **30.6%** | **74.0%** | 15.2% → 49.9% |
| Mujeres | 18,371 | 0.737 [0.728, 0.745] | 70.9% | | |
| Hombres | 9,260 | 0.750 [0.737, 0.763] | 71.1% | | |

**Hallazgo.** El AUC baja con la edad, pero el problema más serio es de cobertura: con un umbral único el sistema detecta solo el 30.6% de las inasistencias de los adultos de 65 años o más, frente a 90.9% en el grupo de 19 a 35. Ocurre porque su tasa base de no-show es menor (15.4%) y sus probabilidades quedan más a menudo bajo el umbral. Es el mismo principio que documentaron Obermeyer et al. (2019): un modelo puede no usar una variable sensible y aun así tratar de forma desigual a un grupo.

**Mitigación implementada (post-procesamiento).** Umbrales por grupo de edad elegidos con predicciones fuera de muestra del entrenamiento, con el mismo objetivo de recall (70%) en cada grupo. En prueba, el recall de todos los grupos queda entre 70.3% y 74.0% (criterio de *igualdad de oportunidades*). El costo es explícito: el porcentaje total de citas señaladas pasa de 43.0% a 45.1% y la precisión global baja de 0.334 a 0.320. La mitigación viene **activada por defecto** en la interfaz, que permite desactivarla para comparar.

**Lo que la mitigación no resuelve:** el AUC menor en adultos mayores (0.707) persiste. Corregirlo requiere variables que el dataset no tiene (movilidad, apoyo de cuidadores, transporte).

## 3. Privacidad

- **Datos personales:** el dataset es público y anónimo (identificadores numéricos). No se usa ningún dato real de pacientes ni de la operación de ningún empleador, ni información protegida de salud (PHI) en el sentido de HIPAA.
- **Datos de proveedores:** del NPI Registry solo se conservan los 15 **códigos postales** usados como sedes. Los registros individuales de los profesionales no se publican en el repositorio.
- **Interfaz:** no guarda datos. El historial vive solo en la memoria de la sesión del navegador y se borra al cerrarla. No se piden nombres ni identificadores.
- **Regulación:** un despliegue real en EE. UU. requeriría cumplir la Regla de Privacidad y la Regla de Seguridad de HIPAA (acuerdos de asociado comercial, cifrado y control de acceso). Si hubiera usuarios o pacientes en California aplicaría también la CCPA/CPRA, y en la Unión Europea el GDPR, que clasifica los datos de salud como categoría especial (artículo 9) y exige base legal, minimización y evaluación de impacto (DPIA).

## 4. Transparencia y explicabilidad

- **Interpretabilidad global:** importancia por permutación y SHAP coinciden en que la antelación de la cita domina, seguida de la edad (`results/figures/18_shap_resumen.png`).
- **Explicación individual:** la interfaz muestra, para cada predicción, las variables que más suben o bajan el riesgo (valores SHAP), junto con el umbral aplicado.
- **Comunicación honesta:** la interfaz advierte que SHAP explica **al modelo, no causas**. El caso del SMS lo ilustra: el modelo lo asocia a más riesgo aunque, controlando por antelación, se asocia a menos inasistencia (razón de momios ajustada 0.77, IC 95% 0.75 a 0.80).
- **Documentación:** la sección "Acerca del modelo" de la app resume métricas, equidad y limitaciones en lenguaje no técnico.

## 5. Impacto social

| | Descripción |
|---|---|
| **Impacto positivo** | Más visitas efectivas con el mismo personal. En la simulación, priorizar por riesgo × distancia redujo el desplazamiento desperdiciado en 12.6%, frente a 8.9% de usar solo la distancia y 5.0% al azar (supuesto: la confirmación reduce el no-show en 25%). |
| **Impacto negativo posible** | Que el riesgo se use para **dejar de visitar** a quienes faltan más, que suelen ser personas con más barreras de acceso. Sería lo contrario del propósito del sistema. |
| **Quiénes se benefician** | Afiliados que reciben una visita efectiva, equipos de programación y NP (menos viajes inútiles). |
| **Quiénes podrían perjudicarse** | Adultos mayores (sin la mitigación) y personas de barrios con alta inasistencia, si el sistema se usara para restringir acceso. |

## 6. Responsabilidad

- **Si el modelo falla**, la responsabilidad es de la organización que lo despliega y del equipo que lo valida, no del algoritmo. El sistema es de apoyo: el coordinador conserva la decisión final sobre cada visita.
- **Mecanismos de accountability:** versión del modelo y métricas visibles en la app; modelos versionados (`model_v1.pkl`, `best_model.pkl`); configuración y semillas en `config.yaml`; registro de eventos en `results/reports/ejecucion.log`; pruebas automáticas.
- **Plan de monitoreo propuesto para un uso real:**
  1. Mensualmente: AUC, Brier y recall por grupo de edad con los desenlaces reales.
  2. Alerta si el recall de algún grupo cae bajo 60% o si el Brier sube más de 10% sobre el valor de validación.
  3. Revisión trimestral de deriva de datos (antelación, edad, canal de recordatorio).
  4. Reentrenamiento anual o ante cambios de proceso (por ejemplo, un nuevo sistema de recordatorios).
  5. Medir el efecto real de la confirmación con una prueba aleatorizada, en lugar de suponer el 25%.

## 7. Uso dual y mal uso

| Posible mal uso | Salvaguarda |
|---|---|
| Negar, retrasar o cancelar visitas a pacientes de alto riesgo | Advertencia permanente en la app; la documentación restringe el uso a ordenar confirmaciones |
| Sobreagendar citas contando con que ciertos pacientes faltarán, degradando su atención | Fuera del alcance declarado; se recomienda no usarlo para sobreagendamiento sin evaluación ética |
| Perfilar barrios o grupos socioeconómicos | La app no permite consultar ni exportar riesgos agregados por barrio |
| Usar las probabilidades en decisiones de cobertura o precios de seguros | Prohibido por las limitaciones documentadas; además, la licencia del dataset es no comercial |

## 8. Limitaciones reconocidas

**No usar el modelo:**
- Para decidir quién recibe o no atención de salud.
- En poblaciones distintas a la de entrenamiento sin reentrenarlo y revalidarlo (en particular, en visitas domiciliarias reales de EE. UU.).
- Con fines comerciales, por la licencia CC BY-NC-SA 4.0 del dataset.
- Como estimación causal del efecto de los recordatorios.

**Casos límite donde no es confiable:**
- Adultos de 65 años o más (AUC 0.707, menor que el global).
- Pacientes sin historial de citas (la mayoría de los casos), donde la predicción se apoya casi solo en la antelación y la edad.
- Citas con antelaciones fuera del rango observado (más de 179 días).
- Barrios que no aparecen en los datos (frecuencia 0).

**Advertencia general para usuarios:** un AUC de 0.74 significa que el modelo se equivoca con frecuencia. Úselo para ordenar llamadas de confirmación, nunca como única base de una decisión.

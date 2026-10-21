# Consideraciones éticas

El análisis se organiza con los cuatro principios de la ética biomédica (autonomía, no maleficencia, beneficencia y justicia; Beauchamp y Childress, 2019), porque el sistema opera en un contexto de acceso a servicios de salud.

## 1. Análisis de sesgos

**¿El dataset tiene sesgos?** Sí, y conviene nombrarlos:

| Sesgo | Descripción | Posible efecto |
|---|---|---|
| De población | Citas ambulatorias de la red pública de Vitória (Brasil), 2016. No son visitas domiciliarias de Medicare/Medicaid en EE. UU. | Las cifras no son extrapolables al caso de uso real sin reentrenar |
| Demográfico | 65% de las citas son de mujeres; los adultos de 65 años o más son solo 13% de la prueba (3,594 citas) | Menos datos del grupo más relevante para Medicare y peor desempeño en él |
| Socioeconómico | El programa social (Bolsa Família) y el barrio actúan como indicadores indirectos de nivel socioeconómico | El modelo asigna más riesgo y más confirmaciones a beneficiarios y a barrios vulnerables (medido en la sección 2) |
| De registro | Las condiciones clínicas se registran solo como presencia o ausencia; la discapacidad se simplificó a binaria | Información clínica incompleta |
| De intervención | El SMS no se asignó al azar, sino a citas con más antelación | Asociación engañosa: sin controlar, el SMS parece aumentar el no-show |

**Grupos que podrían ser perjudicados:** adultos de 56 a 64 y de 65 años o más (con un umbral único el modelo detecta peor sus inasistencias) y beneficiarios de programas sociales o residentes de barrios vulnerables (reciben más contactos, lo que puede sentirse como vigilancia, y serían los más afectados si el riesgo se usara para restringir el acceso).

## 2. Equidad (fairness)

**Métricas evaluadas en el conjunto de prueba** por edad, sexo y dos indicadores indirectos de nivel socioeconómico, con intervalos de confianza de 95% por bootstrap por paciente (300 remuestreos; el mismo remuestreo para todos los grupos). La vulnerabilidad del barrio es el tercil de la proporción de pacientes con Bolsa Família en el barrio, calculada solo con el entrenamiento. Los umbrales por grupo se fijan por edad; en las filas de sexo y de proxies se muestra su efecto.

| Grupo | Citas | AUC [IC 95%] | Recall con umbral único [IC 95%] | Recall con umbrales por edad [IC 95%] |
|---|---|---|---|---|
| 0 a 18 | 7,356 | 0.745 [0.732, 0.760] | 82.3% [80.3, 84.4] | 70.3% [68.1, 72.8] |
| 19 a 35 | 6,029 | 0.736 [0.723, 0.751] | 90.9% [89.4, 92.3] | 72.9% [70.5, 75.5] |
| 36 a 55 | 7,428 | 0.730 [0.710, 0.745] | 68.5% [65.9, 71.3] | 70.4% [67.9, 72.9] |
| 56 a 64 | 3,224 | 0.714 [0.681, 0.743] | 31.7% [27.3, 37.5] | 72.3% [67.9, 76.5] |
| **65 o más** | 3,594 | **0.707 [0.684, 0.729]** | **30.6% [25.9, 34.7]** | **74.0% [70.2, 77.8]** |
| Mujeres | 18,371 | 0.737 [0.728, 0.747] | 70.9% [69.4, 72.5] | 72.2% [70.8, 73.9] |
| Hombres | 9,260 | 0.750 [0.737, 0.765] | 71.1% [68.6, 73.4] | 70.2% [67.8, 72.4] |
| Con Bolsa Família | 2,763 | 0.757 [0.733, 0.781] | 86.8% [84.0, 89.5] | 83.2% [79.9, 86.2] |
| Sin Bolsa Família | 24,868 | 0.738 [0.730, 0.747] | 68.9% [67.3, 70.5] | 70.0% [68.6, 71.5] |
| Barrios de vulnerabilidad alta | 8,877 | 0.755 [0.743, 0.766] | 75.2% [73.2, 77.0] | 73.3% [71.1, 75.6] |
| Barrios de vulnerabilidad media | 9,428 | 0.739 [0.727, 0.752] | 73.0% [70.9, 75.3] | 72.4% [69.9, 74.5] |
| Barrios de vulnerabilidad baja | 9,326 | 0.725 [0.712, 0.740] | 64.2% [61.7, 66.8] | 68.8% [66.5, 71.3] |

El porcentaje de citas señaladas por grupo de edad pasa, con los umbrales por edad, de 53.0% a 41.7% (0 a 18), de 62.4% a 46.4% (19 a 35), de 42.9% a 44.5% (36 a 55), de 14.9% a 46.7% (56 a 64) y de 15.2% a 49.9% (65 o más).

**Hallazgo.** El AUC baja con la edad, pero el problema más serio es de cobertura: con un umbral único el sistema detecta solo el 30.6% de las inasistencias de los adultos de 65 años o más, frente a 90.9% en el grupo de 19 a 35. Ocurre porque su tasa base de no-show es menor (15.4%) y sus probabilidades quedan más a menudo bajo el umbral. Es el mismo principio que documentaron Obermeyer et al. (2019): un modelo puede no usar una variable sensible y aun así tratar de forma desigual a un grupo.

**Mitigación implementada (post-procesamiento).** Umbrales por grupo de edad elegidos con predicciones fuera de muestra del entrenamiento, con el mismo objetivo de recall (70%) en cada grupo. En prueba, el recall de todos los grupos queda entre 70.3% y 74.0% (criterio de *igualdad de oportunidades*). El costo es explícito: el porcentaje total de citas señaladas pasa de 43.0% a 45.1% y la precisión global baja de 0.334 a 0.320. La mitigación viene **activada por defecto** en la interfaz, que permite desactivarla para comparar.

**Métrica de equidad resumida:** diferencia de igualdad de oportunidades (máximo menos mínimo del recall entre grupos de edad): **0.603** con umbral único (90.9% frente a 30.6%) y **0.037** con umbrales por grupo (74.0% frente a 70.3%). La diferencia de AUC entre el grupo de 65 años o más y el resto es de 0.034.

**Sexo y proxies socioeconómicos.** Por sexo no hay brecha relevante: el recall es casi idéntico con umbral único (70.9% y 71.1%) y los intervalos del AUC se traslapan. En los proxies socioeconómicos la brecha existe, pero en sentido contrario al que se temía: el modelo detecta **más** inasistencias de los beneficiarios de Bolsa Família (86.8% frente a 68.9%) y de los barrios de vulnerabilidad alta (75.2% frente a 64.2% en los de vulnerabilidad baja), porque su tasa base de no-show es mayor. Como la intervención es una confirmación de apoyo, esto dirige más ayuda a quienes tienen más barreras; el riesgo real es de uso indebido (si el puntaje se usara para restringir visitas, ellos serían los más afectados) y de percepción de vigilancia. Los umbrales por edad reducen además esas brechas (de 17.9 a 13.2 puntos por programa social y de 11.0 a 4.5 puntos entre terciles de barrio), sin haber sido diseñados para ello.

**¿Es legítimo usar la edad para fijar umbrales?** Usar la edad para tratar distinto a las personas exige una justificación explícita, porque la Sección 1557 y la Ley contra la Discriminación por Edad protegen precisamente esa característica. La justificación del proyecto es la siguiente:

1. **Propósito correctivo.** Con un umbral único, la propia regla de decisión produce un efecto dispar por edad (30.6% de cobertura en 65 o más frente a 90.9% en 19 a 35). Los umbrales por edad buscan igualar la probabilidad de que una inasistencia real reciba apoyo (igualdad de oportunidades; Hardt et al., 2016), no favorecer ni excluir a un grupo.
2. **Solo agrega un beneficio.** El umbral decide quién recibe primero una llamada de confirmación; nadie pierde su visita ni ve retrasada su atención por su edad. Los grupos jóvenes reciben menos confirmaciones que con el umbral único (por ejemplo, de 62.4% a 46.4% en 19 a 35), pero mantienen un recall de 70% o más.
3. **Encaje normativo.** La regla de la Sección 1557 (45 CFR § 92.210) no prohíbe que una herramienta use la edad: exige identificar ese uso y hacer esfuerzos razonables para mitigar el riesgo de discriminación, que es lo que hace esta corrección. La reglamentación de HHS de la Ley contra la Discriminación por Edad (45 CFR parte 91) admite distinciones por edad necesarias para el funcionamiento normal de un programa (§ 91.13), presume necesarios los beneficios especiales para adultos mayores (§ 91.17) y permite acciones afirmativas para superar una participación limitada por edad (§ 91.16).
4. **Salvaguardas.** La decisión está documentada, la mitigación puede desactivarse para comparar, los umbrales se recalculan con datos del programa real y se revisan trimestralmente, y antes de un despliegue debe validarla asesoría legal. Esta es una justificación razonada, no un dictamen jurídico.

**Lo que la mitigación no resuelve:** el AUC menor en adultos mayores (0.707) persiste. Corregirlo requiere variables que el dataset no tiene (movilidad, apoyo de cuidadores, transporte).

## 3. Privacidad

- **Datos personales:** el dataset es público y anónimo (identificadores numéricos). No se usa ningún dato real de pacientes ni de la operación de ningún empleador, ni información protegida de salud (PHI) en el sentido de HIPAA.
- **Datos de proveedores:** del NPI Registry solo se conservan los 15 **códigos postales** usados como sedes. Los registros individuales de los profesionales no se publican en el repositorio.
- **Interfaz:** no guarda datos. El historial y las solicitudes de revisión viven solo en la memoria de la sesión del navegador y se borran al cerrarla. No se piden nombres ni identificadores, y el campo de comentario de las solicitudes de revisión advierte que no se escriban datos que identifiquen al paciente; el registro de eventos guarda solo el motivo, nunca el comentario.
- **Regulación:** un despliegue real en EE. UU. requeriría cumplir la Regla de Privacidad y la Regla de Seguridad de HIPAA (acuerdos de asociado comercial, cifrado y control de acceso). Si hubiera usuarios o pacientes en California aplicaría también la CCPA/CPRA, y en la Unión Europea el GDPR, que clasifica los datos de salud como categoría especial (artículo 9) y exige base legal, minimización y evaluación de impacto (DPIA).
- **No discriminación (EE. UU.):** la regla de 2024 de la Sección 1557 de la ACA (45 CFR § 92.210) obliga a las entidades de salud a identificar las herramientas de apoyo a la decisión que usan variables de edad, sexo, raza u otras características protegidas, y a mitigar su riesgo de discriminación (U.S. Department of Health and Human Services, 2024). Este modelo usa edad y sexo, por lo que un despliegue real exigiría inventariarlo y auditarlo; la mitigación por grupo de edad y el monitoreo propuesto responden a esa obligación. La Ley contra la Discriminación por Edad de 1975 refuerza el mismo principio en programas con fondos federales.
- **AI Act de la UE:** el Reglamento (UE) 2024/1689 clasifica como de alto riesgo los sistemas que evalúan el acceso de las personas a servicios de salud. Este sistema no aplica a la UE y está diseñado para **informar el orden** de las confirmaciones, no para decidir el acceso; si se usara para conceder o negar visitas, pasaría a ser de alto riesgo.
- Un despliegue real requeriría asesoría legal.

## 4. Transparencia y explicabilidad

- **Interpretabilidad global:** importancia por permutación y SHAP coinciden en que la antelación de la cita domina, seguida de la edad (`results/figures/18_shap_resumen.png`).
- **Explicación individual:** la interfaz muestra, para cada predicción, las variables que más suben o bajan el riesgo (valores SHAP), junto con el umbral aplicado.
- **Comunicación honesta:** la interfaz advierte que SHAP explica **al modelo, no causas**. El caso del SMS lo ilustra: el modelo lo asocia a más riesgo aunque, controlando por antelación, se asocia a menos inasistencia (razón de momios ajustada 0.77, IC 95% 0.75 a 0.80).
- **Documentación:** la sección "Acerca del modelo" de la app resume métricas, equidad y limitaciones en lenguaje no técnico.

## 5. Impacto social

| | Descripción |
|---|---|
| **Impacto positivo** | Más visitas efectivas con el mismo personal. **Beneficio simulado, no observado:** el conjunto de datos no trae distancias, así que se construyó un escenario con 300 solicitudes en centroides reales de códigos postales de Ohio (Census Bureau) y 15 sedes reales de NP (NPI Registry), asignando a cada solicitud el riesgo y el desenlace de una cita real de prueba. Priorizar por riesgo × distancia redujo el desplazamiento desperdiciado en 12.6% (IC 95%: 9.5 a 15.7) con el supuesto de 25% de efecto de la confirmación; con 10% y 40% de efecto, la reducción es 5.0% y 20.0%, y el orden de las políticas no cambia. |
| **Impacto negativo posible** | Que el riesgo se use para **dejar de visitar** a quienes faltan más, que suelen ser personas con más barreras de acceso. Sería lo contrario del propósito del sistema. |
| **Quiénes se benefician** | Afiliados que reciben una visita efectiva, equipos de programación y NP (menos viajes inútiles). |
| **Quiénes podrían perjudicarse** | Adultos mayores (sin la mitigación) y personas de barrios con alta inasistencia, si el sistema se usara para restringir acceso. |

**Stakeholders.** El análisis completo de impacto social (workshop de la asignatura, en `results/reports/workshop_impacto_social.pdf`) identifica cinco grupos:

| Stakeholder | Beneficio principal | Riesgo principal | Poder o voz |
|---|---|---|---|
| Afiliados (pacientes) | Visita confirmada a tiempo | Trato distinto según su riesgo; errores del modelo | Bajo |
| Adultos mayores y afiliados de bajos ingresos | Cobertura similar a la del resto con la mitigación | Menor cobertura sin mitigación; el barrio actúa como indicador socioeconómico | Bajo |
| Coordinadores de programación | Lista priorizada y explicada | Sesgo de automatización; más llamadas | Medio |
| Nurse Practitioners | Menos viajes sin paciente | Uso de métricas para evaluarlos | Medio |
| Organización | Más visitas con la misma dotación | Riesgo legal y reputacional | Alto |

Los dos grupos con menos voz son los más expuestos; por eso la protección de sus intereses quedó en el diseño (umbrales por grupo, uso limitado a confirmar y canal de revisión) y no depende de que ellos la reclamen.

## 6. Responsabilidad

- **Si el modelo falla**, la responsabilidad es de la organización que lo despliega y del equipo que lo valida, no del algoritmo. El sistema es de apoyo: el coordinador conserva la decisión final sobre cada visita.
- **Mecanismos de accountability:** versión del modelo y métricas visibles en la app; modelos versionados (`model_v1.pkl`, `best_model.pkl`); configuración y semillas en `config.yaml`; registro de eventos en `results/reports/ejecucion.log`; pruebas automáticas.
- **Canal de revisión (apelación), implementado:** cada predicción de la interfaz incluye la opción **Solicitar revisión**. El usuario elige un motivo (por ejemplo, el paciente ya confirmó o tiene una barrera de acceso) y puede agregar un comentario; la solicitud queda como *pendiente de revisión humana* y se descarga en CSV desde la pestaña *Historial*. En un despliegue real, esas solicitudes llegarían a la cola del líder de programación y se auditarían cada trimestre junto con las métricas de equidad. **Alcance actual:** el canal está implementado para los usuarios del sistema (coordinadores). El afiliado no ve su puntaje; si objeta una llamada o una reprogramación, lo dice durante la confirmación y el coordinador registra la solicitud en su nombre. Queda propuesta una vía formal propia del afiliado, integrada al proceso de quejas que los planes de Medicare Advantage y Medicaid ya deben tener (42 C.F.R. § 422.564; 42 C.F.R. pt. 438, subpt. F).
- **Plan de monitoreo propuesto para un uso real:**
  1. Mensualmente: AUC, Brier y recall por grupo de edad, sexo, programa social y barrio, con los desenlaces reales.
  2. Alerta si el recall de algún grupo cae bajo 60% o si el Brier sube más de 10% sobre el valor de validación.
  3. Revisión trimestral de deriva de datos (antelación, edad, canal de recordatorio).
  4. Reentrenamiento anual o ante cambios de proceso (por ejemplo, un nuevo sistema de recordatorios).
  5. Medir el efecto real de la confirmación con una prueba aleatorizada, en lugar de suponer el 25%.

**Transferencia de dominio (riesgo prioritario con mitigación propia).** El modelo se entrenó con citas ambulatorias de Brasil (2016), no con visitas domiciliarias de EE. UU. Antes de cualquier uso real:
  1. Extraer, con autorización y bajo HIPAA, al menos 12 meses de visitas IHA/HRA del programa y reentrenar con el mismo pipeline (`python -m src.train`).
  2. Validar con partición por paciente y temporal (últimos meses como prueba), y recalibrar las probabilidades y los umbrales por grupo con esos datos.
  3. Ejecutar un piloto en sombra de 8 a 12 semanas: el sistema predice, pero las predicciones no se usan; se comparan con los desenlaces reales.
  4. Criterios de aprobación: AUC de 0.70 o más con IC 95% que no baje de 0.65, Brier menor que el de la referencia sin información y recall de 60% o más en cada grupo de edad, sexo y proxy socioeconómico. Si alguno falla, no se despliega.

## 7. Uso dual y mal uso

| Posible mal uso | Salvaguarda |
|---|---|
| Negar, retrasar o cancelar visitas a pacientes de alto riesgo | Advertencia permanente en la app; la documentación restringe el uso a ordenar confirmaciones |
| Sobreagendar citas contando con que ciertos pacientes faltarán, degradando su atención | Fuera del alcance declarado; se recomienda no usarlo para sobreagendamiento sin evaluación ética |
| Perfilar barrios o grupos socioeconómicos | La app no permite consultar ni exportar riesgos agregados por barrio |
| Aceptar sin cuestionar una predicción errónea | Canal **Solicitar revisión** en cada predicción y decisión final del coordinador |
| Usar las probabilidades en decisiones de cobertura o precios de seguros | Prohibido por las limitaciones documentadas; además, la licencia del dataset es no comercial |

## 8. Limitaciones reconocidas

**No usar el modelo:**
- Para decidir quién recibe o no atención de salud.
- En poblaciones distintas a la de entrenamiento sin reentrenarlo y revalidarlo (en particular, en visitas domiciliarias reales de EE. UU.; ver los criterios de aprobación de la sección 6).
- Con fines comerciales, por la licencia CC BY-NC-SA 4.0 del dataset.
- Como estimación causal del efecto de los recordatorios.

**Casos límite donde no es confiable:**
- Adultos de 65 años o más (AUC 0.707, menor que el global).
- Pacientes sin historial de citas (la mayoría de los casos), donde la predicción se apoya casi solo en la antelación y la edad.
- Citas con antelaciones fuera del rango observado (más de 179 días).
- Barrios que no aparecen en los datos (frecuencia 0).

**Advertencia general para usuarios:** un AUC de 0.74 significa que el modelo se equivoca con frecuencia. Úselo para ordenar llamadas de confirmación, nunca como única base de una decisión.

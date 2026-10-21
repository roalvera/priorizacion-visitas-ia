# Preparación para el video de preguntas

Respuestas cortas y fundamentadas a las preguntas más probables. Cada una indica dónde apoyarse en el repositorio.

**1. ¿Por qué Gradient Boosting y no una red neuronal?** Datos tabulares de tamaño moderado, donde los ensambles de árboles igualan o superan a las redes profundas; además dan probabilidades calibradas y explicaciones SHAP exactas. Evidencia: `notebooks/03_modelado.ipynb`.

**2. El AUC de 0.741 es moderado; ¿sirve?** Sirve para ordenar, no para decidir. Supera a la referencia de solo antelación en 0.039 y es estable en la validación cruzada (0.735 ± 0.003). Estudios con más variables llegan a 0.9, lo que indica que el límite es la información disponible, no el método (la meseta de `docs/optimizacion.md` lo confirma).

**3. ¿Cómo evitaron la fuga de información?** Con tres medidas: historial solo con citas ya atendidas al agendar, partición por paciente y umbral elegido con predicciones fuera de muestra del entrenamiento. Hay una prueba unitaria que lo verifica: `tests/test_data_processing.py::test_historial_sin_fuga_temporal`.

**4. ¿Por qué no usaron SMOTE o pesos de clase para el desbalance?** Porque distorsionan las probabilidades, y el sistema las usa para priorizar. El desbalance se maneja con AUC-PR, Brier y la elección explícita del umbral.

**5. ¿Qué aprendieron del análisis de sensibilidad?** Que la tasa de aprendizaje domina y que interactúa con el número de árboles (H = 0.135); que el resto es casi indiferente; y que la mejor configuración encontrada no es distinguible de la elegida (0.0003 de diferencia frente a 0.003 de ruido). Figuras 11 a 14.

**5b. ¿Cómo diagnosticaron sobreajuste y subajuste (Semana 3)?** Con tracking árbol a árbol (`staged_predict_proba`) sobre una validación separada por paciente, curvas por tamaño de dataset y curvas de validación de `max_depth` y `learning_rate`, más reglas cuantitativas (brecha, subida de la pérdida de validación desde su mínimo y pérdida frente a un modelo sin información). El modelo complejo sin regularización sobreajusta, el de tocones con tasa 0.01 subajusta y la configuración final queda como óptima. Evidencia: `notebooks/03_modelado.ipynb` (figuras 21 a 24) y `src/diagnosis.py`.

**6. ¿Por qué un umbral de 0.242 y no 0.5?** Con 20% de prevalencia pocas citas superan 0.5 y el recall era 1.7%. Una falsa alarma cuesta una llamada; una inasistencia no detectada cuesta un viaje completo. Por eso se prioriza el recall (70%).

**7. ¿La mitigación por edad no es discriminación?** Es un ajuste correctivo para acercar la *cobertura* entre grupos (igualdad de oportunidades): con un umbral único, la propia regla producía un efecto dispar (30.6% en 65 o más frente a 90.9% en 19 a 35). Solo decide quién recibe primero una llamada de apoyo; nadie pierde su visita. Encaja con la Sección 1557 (45 CFR § 92.210), que pide mitigar el riesgo de discriminación de herramientas que usan la edad, y con la reglamentación de HHS de la Ley contra la Discriminación por Edad (45 CFR parte 91: §§ 91.13, 91.16 y 91.17). El costo está documentado: precisión de 0.334 a 0.320, 2 puntos más de citas señaladas y menos confirmaciones para los jóvenes, que mantienen un recall de 70% o más. Requiere validación legal antes de un despliegue.

**7b. ¿Y por sexo o por nivel socioeconómico?** Se midió con IC 95%: por sexo el recall es 70.9% y 71.1%. Los beneficiarios de Bolsa Família (86.8% frente a 68.9%) y los barrios de vulnerabilidad alta (75.2% frente a 64.2%) reciben más cobertura, no menos, porque faltan más. El riesgo es de uso indebido, no de exclusión. Evidencia: `docs/consideraciones_eticas.md` y `notebooks/05_evaluacion.ipynb`.

**8. ¿Los resultados de la simulación son reales?** No: el beneficio es simulado. El conjunto de datos no trae distancias; las ubicaciones son reales y públicas (centroides de códigos postales de Ohio y códigos postales de NP del NPI Registry) y los riesgos y desenlaces provienen de citas reales, pero la asociación paciente-ubicación es sintética. El 25% de efecto de la confirmación es un supuesto de un metaanálisis; con 10% y 40% la reducción de riesgo × distancia es 5.0% y 20.0%, y el orden de las políticas no cambia.

**8b. ¿El 23% de inasistencia aplica a IHA/HRA?** No necesariamente: es el promedio de consultas ambulatorias de una revisión sistemática (Dantas et al., 2018). No encontramos una cifra publicada específica de IHA/HRA, así que solo es un orden de magnitud; la tasa real se mide en el piloto.

**8c. ¿Y la transferencia de Brasil a EE. UU.?** Es un riesgo prioritario con mitigación propia: reentrenar con al menos 12 meses de datos del programa, validar por paciente y en el tiempo, piloto en sombra de 8 a 12 semanas y criterios de aprobación (AUC de 0.70 o más y recall de 60% o más en cada grupo). Si no se cumplen, no se despliega.

**9. ¿Dónde falla el modelo?** En adultos mayores (AUC 0.707), dentro de un mismo tramo de antelación (AUC 0.59 a 0.68) y en pacientes sin historial. Los falsos negativos típicos son personas mayores con cita cercana (mediana de 54 años y 3 días de antelación).

**10. ¿Qué harían con más tiempo?** Reentrenar con datos reales de un programa IHA/HRA; agregar variables de movilidad y apoyo familiar; medir el efecto real de la confirmación con un ensayo aleatorizado; y pasar a una reoptimización dinámica de rutas.

**11. ¿Quién es responsable si falla?** La organización que lo despliega; el sistema es de apoyo y el coordinador decide. Hay un plan de monitoreo con alertas por grupo de edad, sexo, programa social y barrio en `docs/consideraciones_eticas.md`.

**11b. ¿Hay un proceso de apelación?** Sí: cada predicción de la app tiene *Solicitar revisión*, con motivos predefinidos y un comentario sin datos identificables; la solicitud queda pendiente de revisión humana y se descarga en CSV. En producción llegaría al líder de programación y entraría en la auditoría trimestral. Lo agregamos tras el workshop de impacto social, que mostró que faltaba ese mecanismo. Ojo con el alcance: es para los coordinadores; el afiliado no ve su puntaje y apela por medio del coordinador durante la llamada. La vía formal propia del afiliado (integrada al proceso de quejas del plan) está propuesta, no implementada.

**12. ¿Por qué Streamlit?** Permite una interfaz completa en Python, con despliegue gratuito, y el mismo código del modelo (`src/`) se reutiliza sin duplicarlo.

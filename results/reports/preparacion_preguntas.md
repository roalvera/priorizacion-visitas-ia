# Preparación para el video de preguntas

Respuestas cortas y fundamentadas a las preguntas más probables. Cada una indica dónde apoyarse en el repositorio.

**1. ¿Por qué Gradient Boosting y no una red neuronal?** Datos tabulares de tamaño moderado, donde los ensambles de árboles igualan o superan a las redes profundas; además dan probabilidades calibradas y explicaciones SHAP exactas. Evidencia: `notebooks/03_modelado.ipynb`.

**2. El AUC de 0.741 es moderado; ¿sirve?** Sirve para ordenar, no para decidir. Supera a la referencia de solo antelación en 0.039 y es estable en la validación cruzada (0.735 ± 0.003). Estudios con más variables llegan a 0.9, lo que indica que el límite es la información disponible, no el método (la meseta de `docs/optimizacion.md` lo confirma).

**3. ¿Cómo evitaron la fuga de información?** Con tres medidas: historial solo con citas ya atendidas al agendar, partición por paciente y umbral elegido con predicciones fuera de muestra del entrenamiento. Hay una prueba unitaria que lo verifica: `tests/test_data_processing.py::test_historial_sin_fuga_temporal`.

**4. ¿Por qué no usaron SMOTE o pesos de clase para el desbalance?** Porque distorsionan las probabilidades, y el sistema las usa para priorizar. El desbalance se maneja con AUC-PR, Brier y la elección explícita del umbral.

**5. ¿Qué aprendieron del análisis de sensibilidad?** Que la tasa de aprendizaje domina y que interactúa con el número de árboles (H = 0.135); que el resto es casi indiferente; y que la mejor configuración encontrada no es distinguible de la elegida (0.0003 de diferencia frente a 0.003 de ruido). Figuras 11 a 14.

**5b. ¿Cómo diagnosticaron sobreajuste y subajuste (Semana 3)?** Con tracking árbol a árbol (`staged_predict_proba`) sobre una validación separada por paciente, curvas por tamaño de dataset y curvas de validación de `max_depth` y `learning_rate`, más reglas cuantitativas (brecha, subida de la pérdida de validación desde su mínimo y pérdida frente a un modelo sin información). El modelo complejo sin regularización sobreajusta, el de tocones con tasa 0.01 subajusta y la configuración final queda como óptima. Evidencia: `notebooks/03_modelado.ipynb` (figuras 21 a 24) y `src/diagnosis.py`.

**6. ¿Por qué un umbral de 0.242 y no 0.5?** Con 20% de prevalencia pocas citas superan 0.5 y el recall era 1.7%. Una falsa alarma cuesta una llamada; una inasistencia no detectada cuesta un viaje completo. Por eso se prioriza el recall (70%).

**7. ¿La mitigación por edad no es discriminación?** Es un ajuste para acercar la *cobertura* entre grupos (igualdad de oportunidades): sin él, el grupo de 65 años o más recibía muchas menos confirmaciones que los jóvenes con el mismo tipo de riesgo real. El costo está documentado: precisión de 0.334 a 0.320 y 2 puntos más de citas señaladas.

**8. ¿Los resultados de la simulación son reales?** Las ubicaciones son reales y públicas y los riesgos y desenlaces provienen de citas reales; la asociación paciente-ubicación es sintética, y así se declara. El 25% de efecto de la confirmación es un supuesto de un metaanálisis, con análisis de sensibilidad entre 15% y 50%.

**9. ¿Dónde falla el modelo?** En adultos mayores (AUC 0.707), dentro de un mismo tramo de antelación (AUC 0.59 a 0.68) y en pacientes sin historial. Los falsos negativos típicos son personas mayores con cita cercana (mediana de 54 años y 3 días de antelación).

**10. ¿Qué harían con más tiempo?** Reentrenar con datos reales de un programa IHA/HRA; agregar variables de movilidad y apoyo familiar; medir el efecto real de la confirmación con un ensayo aleatorizado; y pasar a una reoptimización dinámica de rutas.

**11. ¿Quién es responsable si falla?** La organización que lo despliega; el sistema es de apoyo y el coordinador decide. Hay un plan de monitoreo con alertas por grupo de edad en `docs/consideraciones_eticas.md`.

**11b. ¿Hay un proceso de apelación?** Sí: cada predicción de la app tiene *Solicitar revisión*, con motivos predefinidos y un comentario sin datos identificables; la solicitud queda pendiente de revisión humana y se descarga en CSV. En producción llegaría al líder de programación y entraría en la auditoría trimestral. Lo agregamos tras el workshop de impacto social, que mostró que faltaba ese mecanismo. Ojo con el alcance: es para los coordinadores; el afiliado no ve su puntaje y apela por medio del coordinador durante la llamada. La vía formal propia del afiliado (integrada al proceso de quejas del plan) está propuesta, no implementada.

**12. ¿Por qué Streamlit?** Permite una interfaz completa en Python, con despliegue gratuito, y el mismo código del modelo (`src/`) se reutiliza sin duplicarlo.

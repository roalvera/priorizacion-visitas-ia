# Guion del video pitch (5 minutos)

Ritmo de referencia: unas 140 palabras por minuto. **R** = Romel, **J** = Jhon Henry. Entre corchetes, lo que se ve en pantalla. Máximo 9 diapositivas más la grabación de la interfaz.

## Bloque 1. Introducción y problema (0:00 a 0:30) | R

[Diapositiva 1: título, nombres, logo UEES]

"Somos Romel Vera y Jhon Henry Quimi, y presentamos un sistema de IA para priorizar visitas domiciliarias de salud. En los programas de valoración en el hogar de Medicare y Medicaid, cerca de una de cada cinco visitas termina en inasistencia, y el personal se asigna solo por cercanía. Cada visita fallida es un viaje perdido de una enfermera especializada. Nuestra pregunta: ¿puede un modelo de riesgo decidir a quién confirmar primero y reducir ese desperdicio?"

## Bloque 2. Datos y metodología (0:30 a 1:30) | J

[Diapositiva 2: dataset y cifras; diapositiva 3: diagrama del pipeline]

"Usamos solo datos públicos: 110 mil citas médicas reales de Brasil, y geografía real de Ohio del registro de proveedores de Medicare y del Census Bureau. No usamos ningún dato de pacientes reales de ningún empleador.

Tres decisiones técnicas marcan la diferencia. Primera: el historial de cada paciente solo usa citas que ya habían ocurrido cuando se agendó la cita; así evitamos una fuga temporal. Segunda: separamos entrenamiento y prueba por paciente, para que nadie aparezca en ambos lados. Tercera: comparamos regresión logística, Random Forest y Gradient Boosting contra una referencia que solo usa la antelación. Elegimos Gradient Boosting porque captura relaciones no lineales, da probabilidades bien calibradas y es explicable con SHAP."

## Bloque 3. Desarrollo y optimización (1:30 a 2:15) | J

[Diapositiva 4: ranking de hiperparámetros e interacción]

"Evaluamos 68 configuraciones con validación cruzada por paciente. El hallazgo clave: el desempeño forma una meseta. La tasa de aprendizaje es de lejos el hiperparámetro más importante, e interactúa con el número de árboles. La mejor configuración de toda la búsqueda superó a la nuestra por tres diezmilésimas, menos que el ruido. El mayor desafío no fueron los hiperparámetros sino el umbral: con 0.5 el modelo detectaba solo el 2% de las inasistencias; con un umbral elegido fuera de la muestra, detecta el 71%."

## Bloque 4. La solución en acción (2:15 a 3:15) | R

[Grabación de pantalla de la app desplegada]

"Esta es la aplicación en Streamlit. Caso uno: cargo el ejemplo de riesgo alto, un joven con cita a 40 días que faltó a sus dos citas anteriores. Calculo: 53% de riesgo, categoría alta, y la sugerencia es confirmar por teléfono. Este gráfico SHAP muestra por qué: pesan la antelación, la edad y el historial.

Caso dos: una paciente de 72 años con hipertensión y diabetes. Con el umbral único saldría como riesgo moderado; con el umbral por grupo de edad, activado por defecto, queda como riesgo alto. Enseguida explicamos por qué.

Caso tres: cargo un lote de 50 visitas con sus distancias. El sistema marca el 20% que conviene confirmar primero, combinando riesgo y distancia, y permite descargar el resultado.

Y si ingreso más inasistencias que citas previas, la app lo detecta y explica el error."

## Bloque 5. Evaluación y resultados (3:15 a 4:00) | J

[Diapositiva 5: tabla de modelos; diapositiva 6: gráfico de las cinco políticas]

"En 27 mil citas de pacientes nunca vistos, el AUC es 0.741, frente a 0.702 del modelo que solo usa la antelación, con probabilidades bien calibradas. En la simulación, priorizar por riesgo por distancia redujo el desplazamiento desperdiciado un 12.6%, frente a 8.9% de usar solo la distancia y 5% al azar. Somos honestos con los límites: el modelo se apoya mucho en la antelación, y dentro de un mismo tramo de antelación discrimina poco."

## Bloque 6. Consideraciones éticas (4:00 a 4:45) | R

[Diapositiva 7: barras de recall por edad, antes y después]

"El hallazgo ético más importante: con un umbral único, el sistema detectaba solo el 31% de las inasistencias de los adultos mayores, justo la población de Medicare. Lo mitigamos con umbrales por grupo de edad: ahora todos los grupos están entre 70 y 74% de cobertura. Además, la app advierte que el riesgo solo sirve para ordenar llamadas, nunca para negar ni retrasar atención. Y SHAP explica al modelo, no causas: el SMS parece aumentar el riesgo solo porque se envía a citas lejanas."

## Bloque 7. Cierre (4:45 a 5:00) | R y J

[Diapositiva 8: QR del repositorio y de la app]

"Logramos un sistema completo, reproducible y responsable. El siguiente paso es reentrenarlo con datos reales de un programa y medir con un ensayo el efecto real de la confirmación. Todo está en nuestro repositorio y en la app: escaneen el código QR. Gracias."

---

## Lista de verificación antes de grabar
- [ ] Generar los QR: `python scripts/generar_qr.py <url_repo> <url_app>`
- [ ] Grabar la interfaz **desplegada** (no una maqueta) en al menos 720p
- [ ] Cronometrar: si pasa de 5:00, recortar primero el bloque 2 (la tercera decisión técnica)
- [ ] Verificar audio y que el enlace del repositorio se vea en pantalla

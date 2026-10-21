# Guion del video pitch (5 minutos)

Ritmo de referencia: unas 140 palabras por minuto. **R** = Romel, **J** = Jhon Henry. Entre corchetes, lo que se ve en pantalla. Máximo 9 diapositivas más la grabación de la interfaz.

## Bloque 1. Introducción y problema (0:00 a 0:30) | R

[Diapositiva 1: título, nombres, logo UEES]

"Somos Romel Vera y Jhon Henry Quimi, y presentamos nuestro Sistema Inteligente de Priorización de Visitas Domiciliarias de Salud. En los programas de valoración en el hogar de Medicare y Medicaid, parte de las visitas termina en inasistencia y el personal se asigna solo por cercanía: cada falla es un viaje perdido. Romel trabaja programando estas visitas, y de ahí nace nuestra pregunta: ¿puede un modelo de riesgo decidir a quién confirmar primero?"

## Bloque 2. Datos y metodología (0:30 a 1:30) | J

[Diapositiva 2: dataset y cifras; diapositiva 3: diagrama del pipeline]

"Usamos solo datos públicos: 110 mil citas médicas reales de Brasil y geografía real de Ohio del registro de proveedores de Medicare y del Census Bureau, sin datos de pacientes de ningún empleador. Limpiamos los datos y construimos variables como la antelación, las condiciones crónicas y el historial del paciente.

Tres decisiones técnicas marcan la diferencia. Primera: el historial solo usa citas ya ocurridas al agendar, para evitar fuga temporal. Segunda: separamos entrenamiento y prueba por paciente. Tercera: comparamos regresión logística, Random Forest y Gradient Boosting contra una referencia que solo usa la antelación; elegimos Gradient Boosting porque capta relaciones no lineales, calibra bien y es explicable con SHAP. La arquitectura une ese modelo de riesgo con un motor que asigna cada visita a la enfermera más cercana."

## Bloque 3. Desarrollo y optimización (1:30 a 2:15) | J

[Diapositiva 4: ranking de hiperparámetros e interacción]

"Primero diagnosticamos el ajuste con curvas de aprendizaje: un modelo sin regularización sobreajusta desde el árbol 25, y uno demasiado simple subajusta; nuestra configuración queda con una brecha mínima. Luego evaluamos 68 configuraciones con validación cruzada por paciente. El hallazgo clave: el desempeño forma una meseta. La tasa de aprendizaje es el hiperparámetro más importante, e interactúa con el número de árboles. La mejor configuración superó a la nuestra por tres diezmilésimas, menos que el ruido. El mayor desafío fue el umbral: con 0.5 el modelo detectaba solo el 2% de las inasistencias; con uno elegido fuera de la muestra, detecta el 71%."

## Bloque 4. La solución en acción (2:15 a 3:15) | R

[Grabación de pantalla de la app desplegada]

"Esta es la aplicación en Streamlit. Caso uno: cargo el ejemplo de riesgo alto, un joven con cita a 40 días que faltó a sus dos citas anteriores. Calculo: 53% de riesgo, categoría alta, y la sugerencia es confirmar por teléfono. Este gráfico SHAP muestra por qué: pesan la antelación, la edad y el historial.

Caso dos: una paciente de 72 años con hipertensión y diabetes. Con el umbral único saldría como riesgo moderado; con el umbral por grupo de edad, activado por defecto, queda como riesgo alto.

Caso tres: cargo un lote de 50 visitas con sus distancias. El sistema marca el 20% que conviene confirmar primero, combinando riesgo y distancia, y permite descargar el resultado.

Y si ingreso más inasistencias que citas previas, la app lo detecta y explica el error."

## Bloque 5. Evaluación y resultados (3:15 a 4:00) | J

[Diapositiva 5: tabla de modelos frente a la referencia; diapositiva 6: gráfico de las cinco políticas con la leyenda «Resultado simulado»]

"En 27 mil citas de pacientes nunca vistos, el AUC es 0.741, frente a 0.702 de la referencia que solo usa la antelación. Funciona bien para ordenar: el 20% de mayor riesgo concentra el 38% de las inasistencias. Funciona peor en adultos mayores, con AUC de 0.707, y en pacientes sin historial. Como los datos no traen distancias, simulamos con geografía real de Ohio: riesgo por distancia redujo el viaje desperdiciado 12.6%, frente a 8.9% solo por distancia y 5% al azar. Con 10% o 40% de efecto va de 5% a 20%, siempre en el mismo orden."

## Bloque 6. Consideraciones éticas (4:00 a 4:45) | R

[Diapositiva 7: barras de recall por edad antes y después, y una línea con el resultado por sexo y por nivel socioeconómico]

"En ética, el sesgo principal es por edad: con un umbral único detectábamos solo el 31% de las inasistencias de los adultos mayores, justo la población de Medicare. Lo mitigamos con umbrales por grupo de edad: todos quedan entre 70 y 74%, y la edad solo decide quién recibe primero una llamada de apoyo. Por sexo no hay brecha, y los grupos vulnerables reciben más cobertura. El impacto esperado es más visitas efectivas con el mismo personal; el riesgo es usarlo para negar atención, y la app lo prohíbe. Reconocemos límites: el AUC menor en mayores persiste y, entrenado en Brasil, debe validarse en Estados Unidos."

## Bloque 7. Cierre (4:45 a 5:00) | R y J

[Diapositiva 8: QR del repositorio y de la app, con el enlace de GitHub escrito en pantalla]

"Logramos un sistema completo, reproducible y responsable. El siguiente paso es validarlo con datos reales de un programa y medir con un ensayo el efecto real de la confirmación. Todo está en nuestro repositorio y en la app: escaneen el código QR. Gracias."

---

## Lista de verificación antes de grabar
- [ ] Generar los QR: `python scripts/generar_qr.py <url_repo> <url_app>`
- [ ] Grabar la interfaz **desplegada** (no una maqueta) en al menos 720p
- [ ] Cronometrar: si pasa de 5:00, recortar primero el bloque 2 (la tercera decisión técnica)
- [ ] Verificar audio y que el enlace del repositorio se vea en pantalla

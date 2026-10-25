# Guion del video de respuestas (10 preguntas)

**Reparto (orden del README):** Romel Alberto Vera Macías responde las impares (1, 3, 5, 7 y 9) y Jhon Henry Quimi Loza las pares (2, 4, 6, 8 y 10).

**Reglas de la docente que hay que cumplir:**
- Responder en el orden 1 a 10. Antes de cada respuesta, leer en voz alta el número y el texto de la pregunta, y luego responder.
- Cada integrante dice su nombre antes de empezar y aparece **en cámara** mientras responde sus preguntas. Si uno responde una pregunta del otro, esa pregunta vale 0.
- Máximo 2 minutos por pregunta. Pregunta leída más respuesta suman entre 220 y 260 palabras: menos de 2 minutos a ritmo normal. Si en el ensayo alguna pasa de 1:55, recorten la última frase antes de la limitación.
- La interfaz que se muestre debe ser la publicada: https://priorizacion-visitas-ia.streamlit.app
- Formato: MP4, o enlace de YouTube no listado o Google Drive con acceso para la profesora. El enlace va en el README.

**Cómo grabar:** una reunión de Zoom o Teams con los dos conectados y la cámara encendida, compartiendo pantalla. Así la cámara de quien habla queda visible mientras se muestran la app, el repositorio o las figuras. Entre corchetes está lo que debe verse en pantalla.

**Rúbrica por respuesta (10 puntos):** precisión técnica (4), defensa de decisiones y alternativas descartadas (3), evidencia en pantalla (2) y honestidad sobre limitaciones (1). Cada respuesta del guion cubre los cuatro puntos.

---

## Presentación (Romel, en cámara)

"Buenas, profesora. Soy Romel Alberto Vera Macías y respondo las preguntas impares."

## Pregunta 1 | Romel

[Pantalla: diapositiva de la pregunta 1; luego el enlace priorizacion-visitas-ia.streamlit.app/?demo=lote, que abre el lote de 50 visitas ya priorizado]

**Leer en voz alta:** "Pregunta 1: ¿Qué problema resuelve su sistema, quién es el usuario y qué haría hoy esa persona sin él?"

**Respuesta:** "Nuestro sistema ataca un problema de los programas de valoración de salud en el hogar, IHA y HRA, que las aseguradoras de Estados Unidos ofrecen a afiliados de Medicare, Medicaid y Marketplace: parte de las visitas termina en inasistencia, y la enfermera viaja a un domicilio donde nadie la recibe. El sistema estima la probabilidad de inasistencia de cada visita, la explica y la combina con la distancia para decidir a quién confirmar primero.

El usuario es el coordinador de programación, no el paciente: ve la lista priorizada y toma la decisión final; el afiliado nunca ve su puntaje.

¿Qué hace hoy sin el sistema? Lo conozco de primera mano, porque trabajo en la programación de estas visitas: asigna la enfermera más cercana y confirma en el orden de la agenda. Con capacidad limitada, una visita de bajo riesgo recibe el mismo trato que una de alto riesgo.

[Abrir el enlace ?demo=lote] Aquí, de 50 visitas, el sistema marca el 20% que conviene confirmar primero.

El beneficio es simulado, no medido: con geografía real de Ohio, riesgo por distancia redujo las millas desperdiciadas 12.6%, frente a 8.9% solo por distancia. Y la limitación principal: el modelo se entrenó con citas de Brasil, así que hay que reentrenarlo con datos del programa antes de usarlo."

## Presentación (Jhon, en cámara)

"Buenas, profesora. Soy Jhon Henry Quimi Loza y respondo las preguntas pares."

## Pregunta 2 | Jhon

[Pantalla: diapositiva de la pregunta 2. Respaldo en GitHub: `docs/analisis_datos.md` en GitHub, sección 5, tabla del experimento de control]

**Leer en voz alta:** "Pregunta 2: ¿De dónde vienen sus datos y qué limitaciones tienen (tamaño, sesgos, desbalance)? ¿Qué decisión de preprocesamiento fue la más importante y qué habría pasado sin ella?"

**Respuesta:** "Los datos son el conjunto público Medical Appointment No Shows, de Kaggle: 110,527 citas reales de 62,299 pacientes de Vitória, Brasil, en 2016, con licencia no comercial. Para la simulación usamos geografía pública de Ohio, del Census Bureau y del NPI Registry.

Limitaciones. Tamaño: suficiente para un modelo tabular, pero con pocas variables; no hay transporte ni movilidad. Desbalance: solo el 20.2% son inasistencias. Sesgos: 65% de las citas son de mujeres; los adultos de 65 años o más son apenas el 13% de la prueba; el barrio y el programa social actúan como indicadores socioeconómicos; y el SMS no se envió al azar, sino a citas con más antelación. Además, es otro país y otro tipo de cita.

La decisión de preprocesamiento más importante fue construir el historial del paciente sin fuga temporal: solo cuentan las citas cuyo resultado ya se conocía al agendar.

¿Qué habría pasado sin ella? Lo medimos con un experimento de control que está en el repositorio: el mismo modelo, con un historial ingenuo que incluye la propia cita y las futuras, logra un AUC de 0.972, frente a 0.741 del pipeline correcto. Ese 0.972 es falso: el modelo estaría viendo la respuesta. En producción esa información no existe, y el sistema habría fallado justo cuando más se confiaba en él."

## Pregunta 3 | Romel

[Pantalla: diapositiva de la pregunta 3. Respaldo en GitHub: README, sección 4, tabla de modelos; luego la figura `results/figures/09_roc.png`]

**Leer en voz alta:** "Pregunta 3: ¿Por qué eligieron este modelo y no las otras técnicas que compararon? Muestren la comparación con el baseline."

**Respuesta:** "Comparamos cinco opciones en la misma prueba: 27,631 citas de 15,662 pacientes que el modelo nunca vio. Sin información, el AUC es 0.500. Nuestro baseline, que solo usa la antelación, logra 0.702. La regresión logística, 0.665: peor que el baseline, porque la relación con la antelación y la edad no es lineal. Random Forest, 0.734. Y Gradient Boosting, el modelo final, 0.741, con AUC-PR de 0.377 y Brier de 0.142: el mejor en las tres métricas.

Lo elegimos por tres razones. Captura relaciones no lineales en datos tabulares. Sus probabilidades están bien calibradas, Brier de 0.142 frente a 0.161 sin información, y eso es indispensable porque multiplicamos la probabilidad por la distancia. Y SHAP explica cada predicción de forma exacta, como muestra la app.

Descartamos redes neuronales: en datos tabulares de este tamaño no suelen superar a los árboles y explican peor. Y la elección se hizo con validación cruzada por paciente sobre el entrenamiento, 0.736 frente a 0.734 de Random Forest, no mirando la prueba.

Con honestidad: la ganancia sobre el baseline es moderada, 0.039 de AUC. Estudios con más variables llegan a 0.9; nuestro límite es la información disponible, no el algoritmo."

## Pregunta 4 | Jhon

[Pantalla: diapositiva de la pregunta 4. Respaldo en GitHub: `docs/optimizacion.md` en GitHub, figura 12 (ranking) y tabla de la sección 10 (antes y después)]

**Leer en voz alta:** "Pregunta 4: Según el análisis de sensibilidad del Workshop S5, ¿qué hiperparámetros pesaron más y qué mejora cuantificable lograron entre antes y después?"

**Respuesta:** "Evaluamos 68 configuraciones con validación cruzada agrupada por paciente: 28 variando un hiperparámetro a la vez y 40 de una búsqueda aleatoria. Con un modelo sustituto ordenamos su importancia.

El que más pesó, por mucho, fue la tasa de aprendizaje, con 0.951; le siguen la profundidad máxima, con 0.114, y el número de árboles, con 0.088. La regularización y el tamaño de hoja casi no influyen. La interacción más fuerte fue tasa por número de árboles, con H de 0.135: con tasa baja hacen falta más árboles, y con tasa alta muchos árboles sobreajustan.

El hallazgo principal es una meseta: las 68 configuraciones quedan entre 0.714 y 0.736 de AUC. La mejor superó a la nuestra por 0.0003, diez veces menos que la variación entre pliegues, así que mantuvimos la final, que está en el centro de la meseta.

La mejora antes y después, en prueba: con valores por defecto y umbral de 0.5, AUC de 0.740 y recall de 2.2%; el modelo final, AUC de 0.741 y recall de 71.0%. Seamos claros: los hiperparámetros aportaron apenas dos milésimas de AUC. La mejora grande vino del umbral elegido fuera de muestra, a costa de bajar la precisión de 0.573 a 0.334."

## Pregunta 5 | Romel

[Pantalla: diapositiva de la pregunta 5; luego el enlace priorizacion-visitas-ia.streamlit.app/?demo=falla, que abre el caso de la mujer de 52 años ya calculado (18.2%, riesgo moderado)]

**Leer en voz alta:** "Pregunta 5: ¿Por qué la métrica que eligieron es la adecuada para su problema? Muestren un caso donde el modelo falla y expliquen por qué."

**Respuesta:** "Con 20% de inasistencias, la exactitud engaña: con umbral de 0.5 era 79.9%, pero el modelo detectaba apenas el 1.7% de las inasistencias. Por eso usamos cuatro métricas. El AUC-ROC mide si el modelo ordena bien, que es lo que hace el sistema. El AUC-PR es exigente con la clase minoritaria: 0.377 frente a 0.202 sin información. El Brier mide la calibración, porque multiplicamos la probabilidad por la distancia. Y el recall en el umbral, porque no detectar una inasistencia cuesta un viaje, y una falsa alarma, solo una llamada. Con umbral de 0.242 detectamos el 71%. Descartamos optimizar exactitud o F1, porque no reflejan ese costo.

Un caso donde falla: mujer de 52 años, cita mañana, sin historial ni SMS. El modelo da 18%, riesgo moderado, y no la marca. Pero en 412 citas de prueba con un perfil parecido faltó el 25.5%, y de 105 inasistencias detectó solo 47; el cálculo está en el script del caso de falla.

¿Por qué? Lo muestra el gráfico SHAP: la antelación de un día sube el riesgo, pero la edad de 52 lo baja, porque en promedio las personas mayores faltan menos. Sin historial no hay otra señal que distinga a quien sí faltará, y la estimación queda cerca del promedio, bajo el umbral. Dentro de un mismo tramo de antelación, el AUC cae a entre 0.59 y 0.68."

## Pregunta 6 | Jhon

[Pantalla: diapositiva de la pregunta 6. Respaldo en GitHub: `notebooks/03_modelado.ipynb` o `docs/optimizacion.md` en GitHub, figuras 21 y 22 (curvas de entrenamiento y validación)]

**Leer en voz alta:** "Pregunta 6: ¿Cómo comprobaron que el modelo no sufre overfitting y que funcionaría con datos nuevos?"

**Respuesta:** "Lo comprobamos en tres niveles.

Primero, la partición: 75% y 25%, separada por paciente. Los 15,662 pacientes de prueba nunca se vieron al entrenar; el código verifica que no haya pacientes en ambos lados, y la prueba se usó una sola vez, al final.

Segundo, la validación cruzada de cinco pliegues, agrupada por paciente: AUC de 0.735, con desviación de 0.003. En prueba obtuvimos 0.741. Que coincidan indica que el modelo generaliza y que no elegimos nada mirando la prueba.

Tercero, el diagnóstico de la Semana 3, con curvas árbol a árbol. Un modelo complejo sin regularización sobreajusta: su pérdida de validación es mínima en el árbol 25 y luego sube 8.4%, con AUC de 0.991 en entrenamiento y 0.710 en validación. Un modelo muy simple subajusta. Nuestra configuración tiene una brecha de solo 0.010, AUC de 0.760 en entrenamiento y 0.738 en validación, y su pérdida de validación no sube. Con todos los datos, la brecha en la curva por tamaño es de 0.029.

La limitación: «datos nuevos» aquí son pacientes nuevos de la misma población. No demuestra que funcione en visitas de Estados Unidos; para eso proponemos reentrenar con datos del programa y un piloto en sombra, exigiendo AUC de 0.70 o más y recall de 60% o más en cada grupo."

## Pregunta 7 | Romel

[Pantalla: diapositiva de la pregunta 7; luego el enlace priorizacion-visitas-ia.streamlit.app/?demo=adulto_unico (umbral único: moderado) y después priorizacion-visitas-ia.streamlit.app/?demo=adulto (umbral por edad: alto). Al final, priorizacion-visitas-ia.streamlit.app/?demo=acerca]

**Leer en voz alta:** "Pregunta 7: ¿Cuál es el riesgo ético o social más importante de su proyecto (sesgo, privacidad, uso indebido) y qué medida concreta implementaron? ¿En qué casos no debería usarse?"

**Respuesta:** "El riesgo más importante es el sesgo por edad. Con un umbral único, el sistema detectaba solo el 30.6% de las inasistencias de las personas de 65 años o más, frente al 90.9% del grupo de 19 a 35, y ese grupo es justamente la población de Medicare.

La medida concreta son umbrales por grupo de edad, elegidos fuera de muestra con el mismo objetivo de recall de 70%. Ahora todos los grupos quedan entre 70.3% y 74.0%, y la brecha de igualdad de oportunidades baja de 0.603 a 0.037. Aquí se ve con el ejemplo de 72 años: con el interruptor apagado, su 21.5% queda como riesgo moderado; encendido, su umbral es 18.2% y queda marcado para confirmar. El costo es explícito: la precisión baja de 0.334 a 0.320.

Usar la edad así es una corrección, no una exclusión: solo decide quién recibe primero una llamada de apoyo y nunca quita una visita. También evaluamos sexo y nivel socioeconómico: por sexo no hay brecha, y los grupos vulnerables reciben más cobertura.

¿Cuándo no debe usarse? Para negar, retrasar o cancelar atención; en otra población sin reentrenarlo, como visitas reales de Estados Unidos; con fines comerciales, por la licencia de los datos; y como prueba causal de los recordatorios. Y la mitigación no corrige el AUC menor en adultos mayores, 0.707."

## Pregunta 8 | Jhon

[Pantalla: diapositiva de la pregunta 8; luego la app publicada con los enlaces ?demo=error, ?demo=lote_errores y ?demo=columnas]

**Leer en voz alta:** "Pregunta 8: Con grabación de pantalla, muestren cómo la interfaz maneja una entrada inválida y un error. ¿Qué decisiones de diseño tomaron pensando en el usuario final?"

**Respuesta:** "Muestro tres casos en la app publicada.

Primero, una entrada inválida: con 2 citas previas y 3 inasistencias [enlace ?demo=error; si quieren, cambien un valor en vivo y pulsen Calcular] La app no calcula y explica: «Las inasistencias previas no pueden ser más que las citas previas». Además, los campos tienen límites: la edad solo acepta de 0 a 115.

Segundo, un lote con errores. [Enlace ?demo=lote_errores] Procesa las 3 filas válidas y lista las 2 excluidas con su motivo: edad de 150 en la fila 5, y SMS con valor 2 y tasa previa de 1.5 en la fila 6.

Tercero, un CSV con otro formato. [Enlace ?demo=columnas] La app no adivina: dice qué columnas faltan, y la plantilla está para descargar ahí mismo. Cualquier falla interna se registra en el log, y el usuario ve un mensaje claro, nunca un error técnico.

Diseñamos para un coordinador sin formación técnica: botones de ejemplo, una guía de uso y ayudas en cada campo, un resultado con probabilidad, categoría y acción sugerida, SHAP en lenguaje simple con la nota de que no indica causas, un aviso de que no se use para negar atención, un botón de revisión humana, español e inglés, y ningún dato guardado.

Su límite: es un prototipo, sin inicio de sesión."

## Pregunta 9 | Romel (opción A, datos tabulares)

[Pantalla: diapositiva de la pregunta 9. Respaldo en GitHub: `notebooks/05_evaluacion.ipynb`, figura 18 (resumen SHAP); luego `tests/test_data_processing.py`, función `test_historial_sin_fuga_temporal`]

**Leer en voz alta:** "Pregunta 9: Opción A, datos tabulares: ¿Qué variables resultaron más importantes y coincide eso con lo que esperaban del dominio? ¿Cómo evitaron fuga de datos (data leakage) al dividir los datos?"

**Respuesta:** "La variable más importante, con mucha diferencia, es la antelación de la cita: al permutarla, el AUC cae 0.213. Le sigue la edad, con 0.038. Después vienen la frecuencia del barrio, la tasa previa de inasistencia y el SMS, cada una con menos de 0.01. SHAP da el mismo orden en las dos primeras.

¿Coincide con el dominio? En lo principal, sí: la revisión de Dantas y colaboradores, de 2018, sobre 105 estudios, señala la antelación como el principal determinante del no-show y encuentra que los jóvenes faltan más, como nosotros. Lo que no esperábamos es que el historial pesara tan poco: lo calculamos sin fuga, y el 72% de las citas de prueba no tiene citas previas ya atendidas.

Para evitar la fuga tomamos cuatro medidas. El historial solo usa citas con resultado conocido al agendar, y una prueba unitaria lo verifica. La partición es por paciente; si fuera aleatoria, 12,062 pacientes quedarían en ambos lados. La frecuencia del barrio se calcula solo con el entrenamiento. Y el umbral se elige con predicciones fuera de muestra. El experimento de control lo confirma: con fuga, el AUC sube falsamente a 0.972.

Una limitación: esta importancia explica al modelo, no causas. El SMS parece aumentar el riesgo, pero ajustado por antelación se asocia a menos inasistencia."

## Pregunta 10 | Jhon

[Pantalla: diapositiva de la pregunta 10. Respaldo en GitHub: README, tabla «Sistema completo», y la figura `results/figures/20_simulacion.png`; luego el enlace ?demo=lote, columna de millas]

**Leer en voz alta:** "Pregunta 10: Elijan la decisión técnica más difícil o importante de su proyecto (distinta de las ya preguntadas). ¿Qué alternativas consideraron y por qué eligieron esa?"

**Respuesta:** "La decisión más importante fue cómo combinar el riesgo con la geografía. Elegimos priorizar por el desperdicio esperado, el riesgo multiplicado por la distancia, sin cambiar la asignación de la enfermera más cercana.

Consideramos cuatro alternativas: priorizar solo por riesgo; solo por distancia, sin modelo; reoptimizar rutas completas, como un problema de ruteo; o usar el riesgo para cancelar o sobreagendar.

Elegimos riesgo por distancia porque el costo de una inasistencia es el viaje: faltar a 40 millas desperdicia más que faltar a 2. En la simulación de Monte Carlo, con 2,000 réplicas, redujo las millas desperdiciadas 12.6%, frente a 9.6% solo por riesgo, 8.9% solo por distancia y 5.0% al azar. El aporte real del modelo es la diferencia con la mejor política sin modelo: 3.7 puntos.

Descartamos reoptimizar rutas porque exige datos en tiempo real y más complejidad, y la asignación por cercanía es la que ya usan los programas; queda como trabajo futuro. Cancelar o sobreagendar lo descartamos por ética.

Con honestidad: el beneficio es simulado. Los datos no traen distancias, la asociación paciente-ubicación es sintética, y el 25% de efecto es un supuesto de un metaanálisis. Con 10% de efecto la reducción es 5.0%, y con 40%, 20.0%; el orden de las políticas no cambia."

---

## Lista de verificación antes de subir el video
- [ ] Cada integrante dice su nombre y aparece en cámara en todas sus respuestas.
- [ ] Se lee el número y el texto de cada pregunta antes de responderla, en orden de la 1 a la 10.
- [ ] Ninguna respuesta pasa de 2 minutos (cronometrar).
- [ ] La app mostrada es la publicada (se ve la dirección `priorizacion-visitas-ia.streamlit.app` en el navegador).
- [ ] Antes de grabar se abrió la app para que no esté dormida.
- [ ] Tener abiertas en pestañas los enlaces de demostración de la app (README, sección 6): ?demo=lote, ?demo=falla, ?demo=adulto_unico, ?demo=adulto, ?demo=acerca, ?demo=error, ?demo=lote_errores y ?demo=columnas.
- [ ] Subir el video (YouTube no listado o Drive con acceso para la profesora) y agregar el enlace al README, sección 12.

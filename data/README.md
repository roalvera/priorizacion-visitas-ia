# Datos

## `raw/`

| Archivo | Fuente | Licencia |
|---|---|---|
| `noshow_appointments.csv` | *Medical Appointment No Shows*, Hoppen (2016), Kaggle: https://www.kaggle.com/datasets/joniarroba/noshowappointments | **CC BY-NC-SA 4.0**: uso no comercial, con atribución; las adaptaciones de los datos deben compartirse con la misma licencia |
| `ohio_zcta_centroides_2023.csv` | Centroides de ZCTA de Ohio extraídos del *2023 Gazetteer Files* del U.S. Census Bureau: https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_zcta_national.zip | Dominio público (gobierno de EE. UU.) |

**Sedes de NP (simulación).** Los 15 códigos postales de `config.yaml` (`simulacion.sedes_np`) se sortearon con semilla fija entre los 309 códigos postales de una muestra de 1,200 registros de *Nurse Practitioners* de Ohio del NPI Registry de CMS (https://npiregistry.cms.hhs.gov/, consulta del 18/09/2026). Solo se conservan los códigos postales; los registros individuales de los profesionales **no** se publican. El registro cambia con el tiempo (una consulta del 25/09/2026 devolvió 310 códigos), por eso las sedes quedan fijadas.

**Declaración sobre datos simulados.** El componente de asignación es una **simulación**: las ubicaciones son reales y públicas, pero la asociación entre un paciente y una ubicación es sintética. Ningún resultado de la simulación proviene de pacientes o visitas reales.

## `processed/`

| Archivo | Contenido | Se genera con |
|---|---|---|
| `citas_procesadas.csv` | Citas limpias con las 14 variables del modelo, la etiqueta y el conjunto (entrenamiento o prueba) | `python -m src.train` o `notebooks/02_preprocesamiento.ipynb` |
| `frecuencia_barrios.json` | Frecuencia relativa de cada barrio en entrenamiento (la usa la app) | Ídem |

## Diccionario de variables del modelo

| Variable | Tipo | Descripción |
|---|---|---|
| `gender_f` | 0/1 | Sexo femenino |
| `Age` | entero 0 a 115 | Edad en años |
| `Scholarship` | 0/1 | Participa en el programa social Bolsa Família |
| `Hipertension`, `Diabetes`, `Alcoholism` | 0/1 | Condición registrada |
| `Handcap` | 0/1 | Discapacidad registrada (binarizada) |
| `SMS_received` | 0/1 | Recibió recordatorio por SMS |
| `lead_time_days` | entero ≥ 0 | Días entre el agendamiento y la cita |
| `appt_dow` | 0 a 6 | Día de la semana de la cita (0 = lunes) |
| `chronic_count` | 0 a 4 | Suma de hipertensión, diabetes, alcoholismo y discapacidad |
| `prior_appts` | entero ≥ 0 | Citas previas del paciente ya atendidas al momento de agendar |
| `prior_noshow_rate` | 0 a 1 | Tasa de inasistencia en esas citas previas |
| `neighbourhood_freq` | 0 a 1 | Frecuencia relativa del barrio en entrenamiento |
| `no_show` | 0/1 | Variable objetivo: 1 = no asistió |

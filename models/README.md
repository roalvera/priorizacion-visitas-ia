# Modelos

| Archivo | Versión | Descripción | AUC-ROC (prueba) |
|---|---|---|---|
| `best_model.pkl` | 1.0.0 | Gradient Boosting con hiperparámetros elegidos por CV agrupada (`learning_rate=0.1`, `max_depth=5`, `max_iter=100`, `min_samples_leaf=100`), umbral global de 0.242 y umbrales por grupo de edad | 0.741 |
| `model_v1.pkl` | 0.1.0 | Gradient Boosting con valores por defecto (modelo inicial, antes de la optimización) | 0.740 |

Ambos archivos contienen un objeto `ModeloRiesgo` (`src/model.py`) con el estimador, la lista de variables, los umbrales y los metadatos.

```python
from src.model import ModeloRiesgo
modelo = ModeloRiesgo.cargar("models/best_model.pkl")
prob = modelo.predecir_probabilidad(X)          # X: DataFrame con las 14 variables
alto = modelo.clasificar(X, mitigado=True)      # 1 = confirmar primero
```

**Regenerarlos:** `python -m src.train` (unos 3 minutos en CPU). Los resultados son deterministas (semilla 42).

**Advertencia de seguridad:** `joblib`/`pickle` pueden ejecutar código al cargar. Cargue solo archivos de este repositorio.

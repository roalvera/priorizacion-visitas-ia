#!/usr/bin/env bash
# Ejecuta los notebooks en orden y guarda las salidas en el mismo archivo.
set -e
cd "$(dirname "$0")/../notebooks"
for nb in ${@:-01_exploracion 02_preprocesamiento 03_modelado 04_optimizacion 05_evaluacion}; do
  echo "Ejecutando $nb..."
  jupyter nbconvert --to notebook --execute "$nb.ipynb" --inplace --ExecutePreprocessor.timeout=3600
done

## Objetivo
Entrenar un modelo de clasificación automáticamente con GitHub Actions sin usar terminal local.

## Cómo usar desde móvil
1. Crear estos archivos en el repositorio desde GitHub web o editor móvil.
2. Subir un CSV real en `data/raw/telecom_churn_sample.csv`.
3. Ir a **Actions**.
4. Ejecutar **Train ML Model** con **Run workflow**.
5. Descargar el artifact `ml-training-artifacts`.

## Columnas requeridas del CSV
- tenure
- monthly_charges
- contract_type
- internet_service
- churn

## Salida esperada
El workflow genera `outputs/model_metrics.json` con accuracy y ROC AUC.

import pandas as pd

# Cargar datos
datos = pd.read_csv('datos.csv')

# Actualizar datos
datos['columna'] = datos['columna'].apply(lambda x: x + 1)

# Guardar datos actualizados
datos.to_csv('datos.csv', index=False)

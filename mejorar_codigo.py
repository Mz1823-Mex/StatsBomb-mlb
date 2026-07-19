import ast

# Cargar código
with open('codigo.py', 'r') as f:
    codigo = f.read()

# Mejorar código
codigo_mejorado = ast.parse(codigo)

# Guardar código mejorado
with open('codigo.py', 'w') as f:
    f.write(ast.unparse(codigo_mejorado))

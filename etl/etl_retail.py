import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: No se encontró la variable de entorno DATABASE_URL.")
    sys.exit(1)

# Cargar archivos CSV
try:
    ventas = pd.read_csv('etl/ventas.csv')
    inventario = pd.read_csv('etl/inventario.csv')
    clientes = pd.read_csv('etl/clientes.csv')
except FileNotFoundError as e:
    print(f"ERROR: No se encontró uno de los archivos CSV: {e}")
    sys.exit(1)

# Procesamiento de datos
ventas['fecha'] = pd.to_datetime(ventas['fecha'], errors='coerce')
ventas['total'] = ventas['precio_unitario'] * ventas['cantidad']

# Conexión a PostgreSQL
try:
    engine = create_engine(DATABASE_URL)
    ventas.to_sql('ventas', engine, if_exists='replace', index=False)
    inventario.to_sql('inventario', engine, if_exists='replace', index=False)
    clientes.to_sql('clientes', engine, if_exists='replace', index=False)
    print("ETL completado exitosamente.")
except Exception as e:
    print(f"ERROR al cargar los datos en la base de datos: {e}")
    sys.exit(1)

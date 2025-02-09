from sqlalchemy import create_engine, MetaData, Table, select
import pandas as pd
import polars as pl

# Definir los parámetros de conexión
DB_USER = "postgres"          # Usuario de PostgreSQL
DB_PASSWORD = "marce"         # Contraseña de PostgreSQL
DB_HOST = "localhost"         # Dirección del servidor
DB_PORT = "5432"              # Puerto por defecto de PostgreSQL
DB_NAME = "db_stat"           # Nombre de la base de datos

# Crear la URL de conexión
connection_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear el motor de conexión
conec_postgres = create_engine(connection_url)

f1_personas=pd.read_sql("SELECT * FROM endi.f1_personas", conec_postgres)

f1_personas["dcronica"].unique()
f1_personas.dtypes


dpa_provincias = pd.read_excel("DATA/FUENTE/CODIFICACIÓN_2024.xlsx", 
                                sheet_name="CODIGOS", 
                                skiprows=1,
                                usecols="B:G",
                                dtype={"DPA_PROVIN":str,
                                "DPA_CANTON":str,
                                "DPA_PARROQ":str})

# Crear la URL de conexión
connection_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Leer los datos con Polars y ConnectorX
query = "SELECT * FROM endi.f1_personas"
f1_personas = pl.read_database_uri(query, connection_url)

type(f1_personas)

# 📌 Ver las primeras filas
print(f1_personas.head())  # Similar a pandas df.head()
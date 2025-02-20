# -*- coding: utf-8 -*-
"""
ETL ENDI
Versión 1.0
Developer: Marcelo Chávez
ESPOL
Maestría en Estadística Aplicada
"""

# Borrar todas las variables en el entorno global
globals().clear()

import pyreadr
import pandas as pd
import numpy as np
from scipy.stats import kurtosis, skew
import os
from tabulate import tabulate

# Configurar el directorio de trabajo
os.chdir('C:/Users/marcelochavez/Documents/TESIS/')


# Cargar el archivo .RDS
BDD_ENDI_R1_f1_hogar = pyreadr.read_r(r'ENDI\BDD_ENDI_R1_rds\BDD_ENDI_R1_f1_hogar.rds')[None]
BDD_ENDI_R1_f1_personas = pyreadr.read_r(r'ENDI\BDD_ENDI_R1_rds\BDD_ENDI_R1_f1_personas.rds')[None]
BDD_ENDI_R1_f2_lactancia = pyreadr.read_r(r'ENDI\BDD_ENDI_R1_rds\BDD_ENDI_R1_f2_lactancia.rds')[None]
BDD_ENDI_R1_f2_mef = pyreadr.read_r(r'ENDI\BDD_ENDI_R1_rds\BDD_ENDI_R1_f2_mef.rds')[None]
BDD_ENDI_R1_f2_salud_ninez = pyreadr.read_r(r'ENDI\BDD_ENDI_R1_rds\BDD_ENDI_R1_f2_salud_ninez.rds')[None]

class Exploratorio:
    def __init__(self, df):
        self.df = df

    def get_types(self):
        return self.df.dtypes

    def get_min_values(self):
        return self.df.apply(lambda x: min(x.dropna().astype(str).str.len()) if x.dtype == 'object' else (np.min(x) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_max_values(self):
        return self.df.apply(lambda x: max(x.dropna().astype(str).str.len()) if x.dtype == 'object' else (np.max(x) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_skewness(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (round(skew(x.dropna()), 2) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_kurtosis(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (round(kurtosis(x.dropna()), 2) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_mean(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (round(np.mean(x.dropna()), 2) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_median(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (round(np.median(x.dropna()), 2) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_mode(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (x.mode()[0] if np.issubdtype(x.dtype, np.number) and not x.mode().empty else np.nan))

    def get_range(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (round(np.max(x) - np.min(x), 2) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_variance(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (round(np.var(x.dropna()), 2) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_std(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (round(np.std(x.dropna()), 2) if np.issubdtype(x.dtype, np.number) else np.nan))

    def get_coefficient_variation(self):
        return self.df.apply(lambda x: "No aplica" if x.dtype == 'object' else (round(np.std(x.dropna()) / np.mean(x.dropna()), 2) 
                             if np.issubdtype(x.dtype, np.number) and np.mean(x.dropna()) != 0 else np.nan))

    def resumen(self):
        resumen = pd.DataFrame({
            'Variable': self.df.columns,
            'Tipo': self.get_types(),
            'Minimo': self.get_min_values(),
            'Maximo': self.get_max_values(),
            'Rango': self.get_range(),
            'Promedio': self.get_mean(),
            'Mediana': self.get_median(),
            'Desviacion_Estandar': self.get_std(),
            'Coeficiente_Variacion': self.get_coefficient_variation(),
            'Moda': self.get_mode(),
            'Varianza': self.get_variance(),
            'Coeficiente_Asimetria': self.get_skewness(),
            'Curtosis': self.get_kurtosis()
        })

        resumen['Tipo'] = resumen['Tipo'].replace({
            'object': 'Categórica',
            'datetime64[ns]': 'Fecha',
            'bool': 'Booleana',
            'float64': 'Numérica',
            'int64': 'Numérica'
        })
        return resumen
    
    
# Crear una instancia de la clase con un dataframe
exploratorio_hogar = Exploratorio(BDD_ENDI_R1_f1_hogar)

# Obtener el resumen estadístico
resumen_h = exploratorio_hogar.resumen()


# Definir el nombre del archivo y las pestañas a leer
file_path = 'ENDI/Diccionario_variables_ENDI_R2.xlsx'
sheets = ['f1_personas', 
          'f1_hogar', 
          'f2_mef', 
          'f2_lactancia',
          'f2_salud_niñez']

# Lista para almacenar los DataFrames de cada pestaña
dataframes_diccionarios = []

# Leer cada pestaña, seleccionar columnas y apilar
for sheet in sheets:
    # Leer la pestaña completa con las columnas A a F y a partir de la fila 11
    df = pd.read_excel(file_path, 
                       sheet_name=sheet, 
                       usecols='A:F', 
                       skiprows=10)  # Lee desde la fila 11, columnas A a F

    # Filtrar filas hasta la primera fila vacía o que contenga la palabra "Fuente" en la primera columna
    df = df[df.iloc[:, 0].notnull() &\
            ~df.iloc[:, 0].astype(str).str.contains('Fuente:', case=False, na=False)]

    # Añadir el DataFrame procesado a la lista
    dataframes_diccionarios.append(df)

# Concatenar todos los DataFrames en uno solo
endi_diccionarios = pd.concat(dataframes_diccionarios, ignore_index=True)

endi_diccionarios.drop_duplicates(inplace=True)

# Renombrar las columnas
endi_diccionarios.columns = [
    'codigo_variable', 
    'nombre_variable', 
    'pregunta', 
    'categorias', 
    'tipo_variable', 
    'formato']

# Supongamos que `endi_diccionarios` es el DataFrame concatenado que ya tienes
valor_a_buscar = 'fexp'

# Filtrar las filas que contienen el valor en la columna 'codigo_de_la_variable'
resultados = endi_diccionarios.loc[endi_diccionarios['codigo_variable'] == valor_a_buscar]

# Comprobar si hay resultados
if not resultados.empty:
    # Usar `tabulate` para una impresión con estilo
    print(tabulate(resultados,
                   headers='keys',
                   tablefmt='fancy_grid',
                   showindex=False))
else:
    print(f"No se encontraron resultados\
          para el valor '{valor_a_buscar}'\
          en la columna 'codigo_de_la_variable'.")

from sqlalchemy import create_engine, MetaData, Table, select
import pandas as pd
import os
import polars as pl

# Cambiar el directorio de trabajo
os.chdir("C:/Users/marcelochavez/Documents/DATA_SCIENCE_ENDI/")

# Definir los parámetros de conexión
DB_USER = "postgres"
DB_PASSWORD = "marce"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "db_stat"

# Crear la URL de conexión
connection_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear el motor de conexión
engine = create_engine(connection_url)

# Crear un objeto MetaData y reflejar la tabla
metadata = MetaData(schema="endi")
f1_personas = Table("f1_personas", metadata, autoload_with=engine)

# Consultar la tabla y convertirla a DataFrame
try:
    # Crear una conexión
    with engine.connect() as connection:
        # Realizar una consulta (SELECT * FROM endi.f1_personas)
        stmt = select(f1_personas)
        results = connection.execute(stmt).fetchall()

    # Obtener los nombres de las columnas
    column_names = f1_personas.columns.keys()

    # Convertir los resultados a un DataFrame de pandas
    f1_personas = pd.DataFrame(results, columns=column_names)

except Exception as e:
    print(f"Error al transformar la tabla a DataFrame: {e}")



# Define the schema overrides for specific columns (adjust based on your data)
schema_overrides = {
    "column_name1": pl.Int64,     # Replace with the actual column name and desired dtype
    "column_name2": pl.Float64,   # Replace with the actual column name and desired dtype
    # Add more columns as needed
}

# Read the CSV file
df_cp2022 = pl.read_csv(
    "DATA/INEC/BDD_POB_CPV2022_MANLOC.csv",  # Path to your CSV file
    separator=";",                          # Specify the delimiter
    has_header=True,                       # Indicates that the first row contains headers
    schema_overrides=schema_overrides,    # Apply schema overrides
    ignore_errors=True,                    # Ignore parsing errors
    null_values=["NA", "", "010150001001001000101"]  # Include specific null values
)

# Check the first few rows of the DataFrame
print(df_cp2022.head())











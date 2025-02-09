# Limpiar todas las variables del espacio de nombres global
globals().clear()

import pandas as pd
import pyreadr
from scipy.stats import kurtosis, skew
from sqlalchemy import create_engine
import os

class ETL_ENDI:
    def __init__(self, db_user='postgres', db_password='marce', db_name='db_stat', db_host='localhost', db_port='5432'):
        self.engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    
    def leer_rds(self, ruta_archivo):
        """Leer archivo RDS y devolver DataFrame de Pandas con ajuste a la variable 'prov'."""
        df = next(iter(pyreadr.read_r(ruta_archivo).values()))
        
        if 'prov' in df.columns:
            df['prov'] = df['prov'].astype(int)
            df['prov'] = df['prov'].astype(str)
            df['prov'] = df['prov'].apply(lambda x: f"0{x}" if len(x) == 1 and x.isdigit() else x)  # Agregar "0" si es un solo dígito
        return df
    
    def exploratorio(self, df):
        """Generar resumen estadístico de un DataFrame en Pandas."""
        resumen = pd.DataFrame({
            "Variable": df.columns,
            "Tipo": df.dtypes,
            "Minimo": df.min(numeric_only=True),
            "Maximo": df.max(numeric_only=True),
            "Rango": df.max(numeric_only=True) - df.min(numeric_only=True),
            "Promedio": df.mean(numeric_only=True).round(2),
            "Mediana": df.median(numeric_only=True),
            "Moda": df.mode().iloc[0],
            "Desviacion_Estandar": df.std(numeric_only=True).round(2),
            "Coeficiente_Asimetria": df.apply(lambda x: skew(x.dropna()) if x.dtype.kind in 'biufc' else None),
            "Curtosis": df.apply(lambda x: kurtosis(x.dropna()) if x.dtype.kind in 'biufc' else None),
        })
        return resumen
    
    def almacenamiento_postgresql(self, df, table_name, schema='endi'):
        """Guardar DataFrame de Pandas en PostgreSQL."""
        try:
            df.to_sql(table_name, self.engine, schema=schema, if_exists='replace', index=False, method='multi')
            print(f"Tabla '{table_name}' almacenada en el esquema '{schema}' de la base de datos.")
        except Exception as e:
            print(f"Error al almacenar en PostgreSQL: {e}")
    
    def lectura_diccionario(self, file_path, sheets):
        """Leer múltiples pestañas de un archivo Excel y concatenarlas."""
        dataframes_diccionarios = []
        for sheet in sheets:
            df = pd.read_excel(file_path, sheet_name=sheet, usecols=[0, 1])  # Solo leer columnas Variable y Etiqueta
            df.columns = ['Variable', 'Etiqueta']  # Renombrar columnas
            df = df.dropna()  # Eliminar filas vacías
            dataframes_diccionarios.append(df)
        endi_diccionarios = pd.concat(dataframes_diccionarios, ignore_index=True).drop_duplicates()
        return endi_diccionarios
    
    def buscar_variable(self, diccionario_df, variable):
        """Buscar una variable en el diccionario y devolverla en formato tabular vertical."""
        resultado = diccionario_df[diccionario_df["Variable"] == variable]
        if not resultado.empty:
            return resultado.melt(id_vars="Variable", var_name="Campo", value_name="Valor")
        else:
            return f"No se encontraron resultados para la variable '{variable}'."

# Ejemplo de uso
etl_endi = ETL_ENDI()

# Lectura del diccionario:
file_path = 'DATA/INEC/Diccionario_ENDI.xlsx'
sheets = ['f1_personas', 'f1_hogar', 'f2_mef', 'f2_lactancia', 'f2_salud_ninez', 'f3_desarrollo_infantil']
endi_diccionarios = etl_endi.lectura_diccionario(file_path, sheets)

file_f1_personas = 'DATA/INEC/BDD_ENDI_R2_f1_personas.rds'
f1_personas = etl_endi.leer_rds(file_f1_personas)
etl_endi.almacenamiento_postgresql(f1_personas, 'f1_personas')

# Lectura de los archivos RDS.
file_f1_hogar = 'DATA/INEC/BDD_ENDI_R2_f1_hogar.rds'
f1_hogar = etl_endi.leer_rds(file_f1_hogar)
etl_endi.almacenamiento_postgresql(f1_hogar, 'f1_hogar')

file_f2_lactancia = 'DATA/INEC/BDD_ENDI_R2_f2_lactancia.rds'
f2_lactancia = etl_endi.leer_rds(file_f2_lactancia)
etl_endi.almacenamiento_postgresql(f2_lactancia, 'f2_lactancia')

file_f2_mef = 'DATA/INEC/BDD_ENDI_R2_f2_mef.rds'
f2_mef = etl_endi.leer_rds(file_f2_mef)
etl_endi.almacenamiento_postgresql(f2_mef, 'f2_mef')

file_f2_salud_ninez = 'DATA/INEC/BDD_ENDI_R2_f2_salud_ninez.rds'
f2_salud_niniez = etl_endi.leer_rds(file_f2_salud_ninez)
etl_endi.almacenamiento_postgresql(f2_salud_niniez, 'f2_salud_ninez')

file_f3_desarrollo_infantil = 'DATA/INEC/BDD_ENDI_R2_f3_desarrollo_inf.rds'
f3_desarrollo_infantil = etl_endi.leer_rds(file_f3_desarrollo_infantil)
etl_endi.almacenamiento_postgresql(f3_desarrollo_infantil, 'f3_desarrollo_infantil')

dpa_provincias = pd.read_excel("DATA/INEC/CODIFICACIÓN_2024.xlsx", 
                                sheet_name="PROVINCIAS",
                                header=1,
                                usecols="B:C",
                                dtype={"DPA_PROVIN":str,
                                       "DPA_DESPRO":str})

prov_f1_personas = pd.DataFrame(f1_personas.prov.value_counts())

dpa_provincias.rename(columns={"DPA_PROVIN":"prov","DPA_DESPRO":"provincia"}, inplace=True)

etl_endi.almacenamiento_postgresql(dpa_provincias, "dpa_provincias")

f1_personas = f1_personas.merge(dpa_provincias, on="prov", how="left")

etl_endi.almacenamiento_postgresql(f1_personas, "f1_personas")
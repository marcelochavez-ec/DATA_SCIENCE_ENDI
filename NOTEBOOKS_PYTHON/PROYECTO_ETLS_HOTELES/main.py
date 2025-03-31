# Importamos las librerías y funciones necesarias
import pandas as pd
from src.soporte_limpieza import limpieza_inicial
from src.soporte_extraccion import scrapeo_competencia, eventos_api
from src.soporte_carga import conexion_BBDD, carga_BBDD
from src.soporte_informe import big_numbers, analisis_hoteles
import os 
# from dotenv import load_dotenv

# Importamos las variables de entorno
load_dotenv()
url_api = os.getenv("url_api")
url_scrapeo = os.getenv("url_scrapeo")
archivo_raw = os.getenv("archivo_raw")

# Creamos las variables a utilizar en las 
url_scrapeo_competencia = url_scrapeo
enp = url_api
df_raw = pd.read_parquet(archivo_raw, engine='auto')
query_ciudad_madrid = "SELECT nombre_ciudad, id_ciudad FROM ciudad"
query_hoteles_carga = "SELECT nombre_hotel, id_hotel FROM hoteles"
query_clientes_carga = "SELECT mail, id_cliente FROM clientes"
     
# Creamos la función de ETL
def ETL_hoteles(endpoint, url_scrapeo, dataframe):
    """
        Función que ejecuta el proceso completo de extracción, transformación y carga (ETL) de los datos de hoteles. 
        Esta función obtiene los datos de eventos a través de una API, realiza un scrapeo de los datos de la competencia, 
        limpia y transforma los datos proporcionados en el dataframe, y luego los carga en una base de datos. 
        Además, realiza análisis posteriores sobre los datos cargados.

    Args:
        endpoint (str): URL de la API para obtener los datos de eventos.
        url_scrapeo (str): URL para realizar el scrapeo de los datos de competencia.
        dataframe (pandas.DataFrame): Dataframe que contiene los datos de reservas de los hoteles, tanto propios como de la competencia, que serán procesados.
    
    Steps:
        1. Llama a la función `eventos_api` para obtener los eventos desde la API.
        2. Llama a la función `scrapeo_competencia` para obtener los datos de la competencia desde el sitio web.
        3. Realiza la limpieza y transformación de los datos utilizando la función `limpieza_inicial`.
        4. Establece la conexión con la base de datos usando la función `conexion_BBDD`.
        5. Carga los datos limpios en la base de datos mediante la función `carga_BBDD`.
        6. Realiza un análisis de big numbers con la función `big_numbers`.
        7. Realiza el análisis de los hoteles del grupo y de la competencia con la función `analisis_hoteles`.
    Returns:
        None: La función no retorna ningún valor. Realiza las operaciones de ETL y carga directamente en la base de datos.
    """
    dataframe_eventos = eventos_api(endpoint)
    dataframe_scrapeo = scrapeo_competencia(url_scrapeo)
    dataframe_final = limpieza_inicial(dataframe, dataframe_scrapeo)
    conn = conexion_BBDD("BBDD_Hoteles")
    carga_BBDD(conn, dataframe_eventos, dataframe_final, query_ciudad_madrid, query_clientes_carga, query_hoteles_carga)
    big_numbers(conn)
    analisis_hoteles(conn)


# Llamamos a la función de ETL
if __name__ == "__main__":
    ETL_hoteles(enp, url_scrapeo_competencia, df_raw)
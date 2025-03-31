import pandas as pd
import numpy as np

# Función info de dataframes 
def info_df(dataframe):
    """
    Función que devuelve información general sobre el DatFrame que le pasemos.

    Args:
        df (DataFrame): DataFrame con información que queramos revisar

    Returns:
        DataFrame: DataFrame con información general sobre las columnas del DataFrame que se le ha pasado a la función: tipo de datos, número de
        registros, número de valores nulos, porcentaje de los valores nulos sobre el total
    """
    info_df = pd.DataFrame()
    info_df["Tipo_dato"] = dataframe.dtypes
    info_df["numero_registros"] = [dataframe[elemento].value_counts().sum() for elemento in dataframe]
    info_df["Numero_nulos"] = round(dataframe.isnull().sum())
    info_df["%_nulos"] = round((dataframe.isnull().sum()/dataframe.shape[0])*100, 2)

    return info_df

# Función para modificar el tipo de dato de las columnas que le pasemos a tipo fecha
def data_fechas(dataframe, columnas):
    """
    Convierte las columnas especificadas de un DataFrame al tipo de dato datetime.

    Args:
        dataframe (pd.DataFrame): El DataFrame que contiene las columnas a modificar.
        columnas (list): Lista de nombres de las columnas a convertir a tipo datetime.

    Returns:
        pd.DataFrame: El DataFrame con las columnas modificadas al tipo datetime.
    """
    for col in columnas:
        dataframe[col] = pd.to_datetime(dataframe[col])
    return dataframe

# Creamos una función que nos permite realizar el cambio del id creando uno nuevo que será seriado
def cambio_id(dataframe, lista_columnas, nombre_columna_nueva):
    """
    Crea una nueva columna con un identificador seriado basado en valores únicos de otra columna.

    Args:
        dataframe (pd.DataFrame): El DataFrame que contiene la columna original.
        lista_columnas (list): Lista con el nombre de la columna sobre la cual se generará el nuevo ID.
        nombre_columna_nueva (str): Nombre de la nueva columna que contendrá los IDs serializados.

    Returns:
        pd.DataFrame: El DataFrame con la nueva columna de identificadores serializados.
    """
    
    lista = dataframe[lista_columnas[0]].unique()
    diccionario = {}
    conteo = 1
    for elemento in lista:
        
        diccionario[elemento] = conteo
        conteo += 1

    dataframe[nombre_columna_nueva] = dataframe[lista_columnas[0]].map(diccionario).astype(str)
    return dataframe

def limpieza_inicial(dataframe_limpieza, dataframe_scrapeo):
    """
        Realiza una limpieza y transformación inicial de los datos de reservas de hoteles, 
        integrando información scrapeada de la competencia y generando un conjunto de datos limpio.

    Args:
    
        dataframe_limpieza (pd.DataFrame): DataFrame con los datos de reservas de hoteles, incluyendo información de hoteles del grupo y de la competencia. 
        dataframe_scrapeo (pd.DataFrame): DataFrame con los datos scrapeados de hoteles de la competencia.

     Proceso:
    
        1. **Eliminación de duplicados**: Se eliminan registros duplicados en el DataFrame de reservas.
        2. **Conversión de fechas**: Se convierten las columnas `fecha_reserva`, `inicio_estancia` y `final_estancia` a tipo fecha.
        3. **Relleno de valores nulos**: Se asignan fechas predeterminadas a valores nulos en `inicio_estancia` y `final_estancia`.
        4. **Separación de datos**:
            - Se divide el conjunto de datos en hoteles del grupo y hoteles de la competencia.
        5. **Cálculo de precios y estrellas promedio**:
            - Se calculan los precios medios y la valoración media de estrellas por hotel para los hoteles del grupo.
        6. **Integración de datos scrapeados**:
            - Se asigna un ID único a los hoteles scrapeados y se unen con los datos originales de la competencia.
            - Se eliminan columnas redundantes y se homogeniza la estructura de datos.
        7. **Concatenación de datos**:
            - Se concatenan los hoteles del grupo con los de la competencia en un único DataFrame.
        8. **Transformaciones finales**:
            - Se genera un ID único para clientes y hoteles.
            - Se ajustan los tipos de datos de las columnas `id_hotel` e `id_cliente` para coincidir con la base de datos.
        9. **Exportación de datos**:
            - Se guarda el DataFrame limpio en un archivo CSV en la carpeta `data/`.

    Returns:
        Archivo CSV y pd.Dataframe: se genera un archivo CSV llamado `reservas_hoteles_limpio.csv` con la información procesada
        y se imprime la estructura del DataFrame final.

     Nota:
    
        - Se usa `info_df(data)` para visualizar la estructura de los datos antes y después de la limpieza.
        - Las funciones `data_fechas()` y `cambio_id()` deben estar definidas previamente para la conversión de fechas y la generación de IDs únicos.
    """
    
    data = dataframe_limpieza.copy() # creamos una copia del dataframe recibido sobre el cual vamos a trabajar

    data = data.drop_duplicates() # eliminamos los duplicados iguales en el dataframe
    if data.duplicated().sum() == 0: # comprobamos que se han eliminado correctamente
        print("Duplicados iguales eliminados")

    print(f"La estructura inicial del dataframe es: \n {info_df(data)}") # Revisamos la información general del dataframe
    
    data = data_fechas(data, ["fecha_reserva", "inicio_estancia", "final_estancia"]) # modificamos las columnas que queremos a tipo fecha llamando a la funcon de modificacion de fechas
    
    data["inicio_estancia"] = data["inicio_estancia"].fillna("2025-03-01") # Realizamos la modificación de los valores nulos de las columnas reemplazándolas por los valores de las fechas del fin de semana correspondientes
    data["final_estancia"] = data["final_estancia"].fillna("2025-03-02")


    grupo = data[data["competencia"] == False] # Creamos un dataframe para los hoteles del grupo 
    competencia =  data[data["competencia"] == True] # Creamos un dataframe para los hoteles de la competencia

    # Calculamos los precios medios de los hoteles del grupo

    precios_grupo = grupo[["nombre_hotel", "precio_noche"]] # creamos un dataframe solo con los hoteles y el precio correspondiente de cada uno 
    estadisticos_precio = precios_grupo.groupby("nombre_hotel")["precio_noche"].describe() # calculamos los estadíticos de los precios por hotel para revisar con que calcular el precio medio. Es como pasarle una lista de funciones de agregacion con el agg al groupby
    estadisticos_precio = estadisticos_precio.reset_index() # creamos un dataframe a partir de los estadistcios
    precios_medios_grupo = estadisticos_precio[["nombre_hotel", "mean"]] # nos quedamos solo con los precios medios

    # Calulamos las estrellas medias por hotel

    estrellas_grupo = grupo[["nombre_hotel", "estrellas"]]
    estadisticos_estrellas = estrellas_grupo.groupby("nombre_hotel")["estrellas"].describe() # calculamos los estadíticos de las estrellas por hotel para revisar con que calcular la valoracion media. Es como pasarle una lista de funciones de agregacion con el agg al groupby
    estadisticos_estrellas = estadisticos_estrellas.reset_index()
    estrellas_medias_grupo = estadisticos_estrellas[["nombre_hotel", "mean"]]
    estrellas_medias_grupo["mean"] = pd.Series([round(val, 2) for val in estrellas_medias_grupo["mean"]]) # redoneamos los valores a 2 decimales

    grupo_con_precio = grupo.merge(precios_medios_grupo, on = "nombre_hotel") #unimos el df de grupo con el de precios
    grupo_final = grupo_con_precio.merge(estrellas_medias_grupo, on = "nombre_hotel") #unimos el df de grupo con el de estrellas
    grupo_final = grupo_final.drop(columns = ["precio_noche", "estrellas"]) # eliminamos las columnas con los precios y las estrellas incorrectos
    grupo_final = grupo_final.rename(columns = {'mean_x': 'precio_noche', 'mean_y': 'estrellas'}) # renombramos las columnas de medias a los precios y las estrellas medias
    
    competencia_scrapeado = dataframe_scrapeo # nos traemos la información scrapeada
    competencia_scrapeado["id_hotel"] = competencia["id_hotel"].unique() # Asignamos un id de competencia a los hoteles scrapeados

    competencia_final = competencia.merge(competencia_scrapeado, on = "id_hotel") # Unimos los datos scrapeados con los de la competencia original
    competencia_final = competencia_final.drop(columns = ["fecha_reserva_x", "precio_noche", "nombre_hotel_x", "estrellas_x"]) # eliminamos las columns con la información antigua y erronea 
    competencia_final["ciudad"] = "Madrid" # rellenamos la columna de ciudad con Madrid, ya que todos los hoteles son de Madrid
    competencia_final = competencia_final.rename(columns = {'fecha_reserva_y': 'fecha_reserva', 'nombre_hotel_y': 'nombre_hotel', 'estrellas_y': 'estrellas','precio': 'precio_noche'}) # renombramos las columnas con los nombres correctos
    competencia_final = competencia_final.reindex(['id_reserva', 'id_cliente', 'nombre', 'apellido', 'mail', 'competencia',
       'fecha_reserva', 'inicio_estancia', 'final_estancia', 'id_hotel',
       'nombre_hotel', 'estrellas', 'ciudad', 'precio_noche'], axis = 1) # reindexamos las columnas del dataframe para que estén en el mismo orden que el dataframe de grupo, ya que sino el concat se realizará de forma incorrecta
    
    df_final = pd.concat([grupo_final, competencia_final], axis = 0) # Concatenamos ambos dataframes uno encima de otro
    df_final["fecha_reserva"] = pd.to_datetime(df_final["fecha_reserva"]) # modificamos el tipo de dato de la columna de fecha de reserva ahora que la tenemos completa

    columnas_cliente = ["mail", "id_cliente"]
    cambio_id(df_final, columnas_cliente, "id_cliente_nuevo") # Modificamos los id de cliente para que sean únicos

    columnas_hoteles = ["nombre_hotel", "id_hotel"]
    cambio_id(df_final, columnas_hoteles, "id_hotel_nuevo") # Modificamos los id de hotel para que sean únicos

    df_final["id_hotel"] = df_final["id_hotel_nuevo"] 
    df_final["id_cliente"] = df_final["id_cliente_nuevo"]
    df_final = df_final.drop(columns = ["id_hotel_nuevo", "id_cliente_nuevo"])

    df_final["id_hotel"] = df_final["id_hotel"].astype(str) # modificamos el tipo de dato al correspondiente con el de la abse de datos
    df_final["id_cliente"] = df_final["id_cliente"].astype(str) # modificamos el tipo de dato al correspondiente con el de la abse de datos

    df_final.to_csv("data/reservas_hoteles_limpio.csv", index = False) # guardamos el dataframe limpio
    print(f"La estructura final del dataframe es: \n {info_df(df_final)}") # Revisamos la información general del dataframe
    return df_final 


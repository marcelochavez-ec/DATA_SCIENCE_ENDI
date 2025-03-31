# Importamos las librerías necesarias
import pandas as pd
import numpy as np
import psycopg2 as ps
import os
from dotenv import load_dotenv

load_dotenv()
nombre_BBDD = os.getenv("db_stat")
usuario_BBDD = os.getenv("postgres")
contraseña_BBDD = os.getenv("marce")
host_BBDD = os.getenv("localhost")
port_BBDD = os.getenv("5432")
schema_BBDD = os.getenv("schema_hoteles", "hoteles")  # Obtiene el valor del esquema desde el .env (por defecto "hoteles")

def conexion_BBDD(nombre_BBDD=nombre_BBDD, usuario=usuario_BBDD, contraseña=contraseña_BBDD, anfitrion=host_BBDD, puerto=port_BBDD, schema=schema_BBDD):
    """
    Establece una conexión a la base de datos utilizando los parámetros proporcionados. Esta función utiliza la librería `psycopg2` para conectarse a una base de datos PostgreSQL. Los parámetros incluyen
    el nombre de la base de datos, el usuario, la contraseña, el anfitrión, el puerto y el esquema. Si no se proporciona el esquema, por defecto será "hoteles".

    Args:
        nombre_BBDD (str): Nombre de la base de datos a la que se desea conectar.
        usuario (str, opcional): Nombre de usuario para la conexión. Por defecto es `usuario_BBDD`.
        contraseña (str, opcional): Contraseña del usuario para la conexión. Por defecto es `contraseña_BBDD`.
        anfitrion (str, opcional): Dirección del servidor de base de datos. Por defecto es `host_BBDD`.
        puerto (int, opcional): Puerto para la conexión a la base de datos. Por defecto es `port_BBDD`.
        schema (str, opcional): Esquema al que se desea acceder en la base de datos. Por defecto es `hoteles`.

    Returns:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.

    Ejemplo:
        conn = conexion_BBDD("mi_base_de_datos")
    """
    conn = ps.connect(
        dbname=nombre_BBDD, 
        user=usuario, 
        password=contraseña, 
        host=anfitrion, 
        port=puerto
    )
    
    # Crear un cursor para poder ejecutar comandos SQL
    cursor = conn.cursor()

    # Establecer el esquema predeterminado
    cursor.execute(f"SET search_path TO {schema};")
    
    return conn
    
# Carga tabla ciudad
def carga_tabla_ciudad(conn, ciudad = "Madrid"):
    """
    Inserta una nueva ciudad en la tabla 'ciudad' de la base de datos.

    Esta función utiliza un cursor de la conexión a la base de datos para ejecutar una consulta SQL que inserta
    el nombre de una ciudad en la tabla 'ciudad'. Si no se proporciona un nombre de ciudad, el valor predeterminado
    será "Madrid".

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.
        ciudad (str, opcional): El nombre de la ciudad a insertar en la tabla. Por defecto es "Madrid".

    Returns:
        None

    Ejemplo:
        carga_tabla_ciudad(conn, "Barcelona")
    """
    
    cur = conn.cursor()

    data_to_insert = [ciudad]
    insert_query = """ 
                        INSERT INTO ciudad (nombre_ciudad)
                        VALUES (%s) 
                    """
    cur.execute(insert_query, data_to_insert)
    conn.commit()


# Carga tabla eventos
# la query será tal que así: "SELECT nombre_ciudad, id_ciudad FROM ciudad"
def carga_tabla_eventos(dataframe, query_ciudad, conn):

    """
    Inserta eventos desde un DataFrame en la tabla 'eventos' de la base de datos.

    Esta función toma un DataFrame que contiene información sobre eventos y los inserta en la tabla 'eventos' 
    de la base de datos. Primero, ejecuta una consulta para obtener el id de la ciudad (por defecto "Madrid") 
    y luego, para cada fila del DataFrame, extrae los valores correspondientes para cada columna del evento. 
    Si algún valor es nulo o no válido, se reemplaza por `None`.

    Args:
        dataframe (pandas.DataFrame): El DataFrame que contiene los eventos a insertar. Debe tener las columnas
                                      "nombre_evento", "url_evento", "codigo_postal", "direccion", "horario", 
                                      "fecha_inicio", "fecha_fin", y "organizacion".
        query_ciudad (str): Consulta SQL para obtener el id de la ciudad desde la base de datos. 
                             Se asume que esta consulta devolverá un diccionario con el nombre de la ciudad como clave.
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.

    Returns:
        None

    Ejemplo:
        carga_tabla_eventos(df_eventos, "SELECT id FROM ciudad WHERE nombre_ciudad = 'Madrid'", conn)
    """
    cur = conn.cursor()
    
    cur.execute(query_ciudad)
    dictio = dict(cur.fetchall())

    data_to_insert = []


    for i, row in dataframe.iterrows():
        nombre_evento = row["nombre_evento"]
        url_evento = row["url_evento"]
        codigo_postal = row["codigo_postal"] if row["codigo_postal"] != 0 else None # en este caso los valores que son igual a 0 se corresponden con valores nulos, por lo que le indicamos que si el valor es igual a 0 nos ponga un nulo
        direccion = row["direccion"] if pd.notna(row["direccion"]) else None # tenemos valores nulos en esta columna, de manera que le indicamos, que si el elemento no es nulo nos lo coja, y si es nulo, nos incluya un None, ya que sql no acepta valores nulos que no sean None
        horario = row["horario"] if pd.notna(row["horario"]) else None
        fecha_inicio = row["fecha_inicio"]
        fecha_fin = row["fecha_fin"]
        organizacion = row["organizacion"] if pd.notna(row["organizacion"]) else None
        id_ciudad = dictio.get("Madrid")

        data_to_insert.append((nombre_evento, url_evento, codigo_postal, direccion, horario, fecha_inicio, fecha_fin, organizacion, id_ciudad))
        
    insert_query = """ 
                    INSERT INTO eventos (nombre_evento, url_evento, codigo_postal, direccion, horario,
                    fecha_inicio, fecha_fin,organizacion, id_ciudad)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
    cur.executemany(insert_query, data_to_insert)
    conn.commit()


# Carga tabla hoteles
# la query será tal que así: "SELECT nombre_ciudad, id_ciudad FROM ciudad"
def carga_tabla_hoteles(dataframe, query_ciudad, conn):
    """
        Inserta información de hoteles desde un DataFrame en la tabla 'hoteles' de la base de datos.

        Esta función toma un DataFrame que contiene información sobre hoteles y los inserta en la tabla 'hoteles' 
        de la base de datos. Primero, ejecuta una consulta para obtener el id de la ciudad (por defecto "Madrid"). 
        Luego, para cada fila del DataFrame, extrae los valores correspondientes para cada columna del hotel. 
        Si el hotel ya está en la lista de inserción, no lo vuelve a agregar.

    Args:
        dataframe (pandas.DataFrame): El DataFrame que contiene los hoteles a insertar. Debe tener las columnas 
                                      "id_hotel", "nombre_hotel", "competencia", y "estrellas".
        query_ciudad (str): Consulta SQL para obtener el id de la ciudad desde la base de datos. 
                             Se asume que esta consulta devolverá un diccionario con el nombre de la ciudad como clave.
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.

    Returns:
        None

    Ejemplo:
        carga_tabla_hoteles(df_hoteles, "SELECT id FROM ciudad WHERE nombre_ciudad = 'Madrid'", conn)
    """

    cur = conn.cursor()

    data_to_insert = []

    cur.execute(query_ciudad)
    dictio = dict(cur.fetchall())

    for _, row in dataframe.iterrows():
        id_hotel = row["id_hotel"]
        nombre_hotel = row["nombre_hotel"] 
        competencia = row["competencia"] 
        valoracion = row["estrellas"] 
        id_ciudad = dictio.get("Madrid") 

        tupla = (id_hotel, nombre_hotel, competencia, valoracion, id_ciudad)

        if tupla not in data_to_insert:
            data_to_insert.append(tupla)
    
    insert_query = """ 
                        INSERT INTO hoteles (id_hotel, nombre_hotel, competencia, valoracion, id_ciudad)
                        VALUES (%s, %s, %s, %s, %s)
            """
    cur.executemany(insert_query, data_to_insert)
    conn.commit()

# Carga tabla clientes
def carga_tabla_clientes(dataframe, conn):
    """
    Inserta información de clientes desde un DataFrame en la tabla 'clientes' de la base de datos.

    Esta función toma un DataFrame que contiene información sobre clientes y la inserta en la tabla 'clientes'
    de la base de datos. Se extraen los valores correspondientes para cada columna del cliente. Si el cliente ya 
    está en la lista de inserción, no se vuelve a agregar.

    Args:
        dataframe (pandas.DataFrame): El DataFrame que contiene los clientes a insertar. Debe tener las columnas 
                                      "id_cliente", "nombre", "apellido" y "mail".
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.

    Returns:
        None

    Ejemplo:
        carga_tabla_clientes(df_clientes, conn)
    """
    cur = conn.cursor()

    data_to_insert = []

    for _, row in dataframe.iterrows():

        id_cliente = row["id_cliente"]
        nombre = row["nombre"],
        apellido = row["apellido"],
        mail = row["mail"]

        tupla = (id_cliente, nombre, apellido, mail)

        if tupla not in data_to_insert:
            data_to_insert.append(tupla)
    
    insert_query = """ 
                        INSERT INTO clientes (id_cliente, nombre, apellido, mail)
                        VALUES (%s, %s, %s, %s)
                        """
    cur.executemany(insert_query, data_to_insert)
    conn.commit()

# Carga tabla reservas
# La query de clientes será así: "SELECT nombre, id_cliente FROM clientes"
# la query de hoteles será así: "SELECT nombre_hotel, id_hotel FROM hoteles"
def carga_tabla_reservas(dataframe, query_clientes, query_hoteles, conn):
    """
    Inserta información sobre reservas desde un DataFrame en la tabla 'reservas' de la base de datos.

    Esta función toma un DataFrame que contiene información sobre reservas de clientes y hoteles, y la inserta 
    en la tabla 'reservas' de la base de datos. Los identificadores de los clientes y hoteles se obtienen a partir 
    de las consultas proporcionadas (`query_clientes` y `query_hoteles`). Luego, se realizan inserciones de manera
    eficiente para cada reserva.

    Args:
        dataframe (pandas.DataFrame): El DataFrame que contiene las reservas a insertar. Debe tener las columnas 
                                      "id_reserva", "fecha_reserva", "inicio_estancia", "final_estancia", 
                                      "precio_noche", "nombre" (cliente) y "nombre_hotel".
        query_clientes (str): Consulta SQL que devuelve el `id_cliente` asociado al nombre del cliente.
        query_hoteles (str): Consulta SQL que devuelve el `id_hotel` asociado al nombre del hotel.
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.

    Returns:
        None

    Ejemplo:
        carga_tabla_reservas(df_reservas, query_clientes, query_hoteles, conn)
    """
    cur = conn.cursor()
    
    cur.execute(query_clientes)
    dictio_clientes = dict(cur.fetchall())

    cur.execute(query_hoteles)
    dictio_hoteles = dict(cur.fetchall())

    data_to_insert = []

    for _, row in dataframe.iterrows():
        id_reserva = row["id_reserva"]
        fecha_reserva = row["fecha_reserva"]
        inicio_estancia = row["inicio_estancia"]
        final_estancia = row["final_estancia"]
        precio_noche = row["precio_noche"]
        id_cliente = dictio_clientes.get(row["mail"])
        id_hotel = dictio_hoteles.get(row["nombre_hotel"])
        
        tupla_reserva = (id_reserva, fecha_reserva, inicio_estancia, final_estancia, precio_noche, id_cliente, id_hotel)

        if tupla_reserva not in data_to_insert:
            data_to_insert.append(tupla_reserva)

    
    insert_query = """ 
                        INSERT INTO reservas (id_reserva, fecha_reserva, inicio_estancia, final_estancia, precio_noche, id_cliente, id_hotel)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
    
    cur.executemany(insert_query, data_to_insert)
    conn.commit()

def carga_BBDD(conn, df_eventos, df_hoteles, query_ciudad, query_clientes, query_hoteles):
    
    """
    Carga los datos de eventos, hoteles, clientes y reservas en la base de datos.

    Esta función orquesta el proceso de carga de datos en varias tablas de la base de datos:
    - Tabla 'ciudad': Inserta información de la ciudad.
    - Tabla 'eventos': Inserta eventos relacionados con la ciudad.
    - Tabla 'hoteles': Inserta información de hoteles.
    - Tabla 'clientes': Inserta clientes asociados a los hoteles.
    - Tabla 'reservas': Inserta reservas realizadas por los clientes en los hoteles.

    Para ello, la función utiliza las funciones auxiliares `carga_tabla_ciudad`, `carga_tabla_eventos`, 
    `carga_tabla_hoteles`, `carga_tabla_clientes` y `carga_tabla_reservas`.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.
        df_eventos (pandas.DataFrame): DataFrame que contiene los eventos a insertar en la base de datos.
        df_hoteles (pandas.DataFrame): DataFrame que contiene los hoteles y las reservas asociadas a los mismos.
        query_ciudad (str): Consulta SQL que devuelve el `id_ciudad` para la ciudad asociada.
        query_clientes (str): Consulta SQL que devuelve el `id_cliente` asociado al nombre del cliente.
        query_hoteles (str): Consulta SQL que devuelve el `id_hotel` asociado al nombre del hotel.

    Returns:
        None

    Ejemplo:
        carga_BBDD(conn, df_eventos, df_hoteles, query_ciudad, query_clientes, query_hoteles)
    """
    carga_tabla_ciudad(conn)
    carga_tabla_eventos(df_eventos, query_ciudad, conn)
    carga_tabla_hoteles(df_hoteles, query_ciudad, conn)
    carga_tabla_clientes(df_hoteles, conn)
    carga_tabla_reservas(df_hoteles, query_clientes, query_hoteles, conn)
# Importamos las librerías necesarias
import pandas as pd
import numpy as np
import psycopg2 as ps
from src.soporte_limpieza import info_df
from src.soporte_carga import conexion_BBDD, carga_tabla_ciudad, carga_tabla_clientes, carga_tabla_eventos, carga_tabla_hoteles, carga_tabla_reservas
import os
from dotenv import load_dotenv

load_dotenv()
archivo_limpio = os.getenv("archivo_limpio")
archivo_extraccion = os.getenv("archivo_extraccion")


data_hoteles = pd.read_csv(archivo_limpio, parse_dates=['fecha_reserva', 'inicio_estancia', 'final_estancia'], dtype={'id_cliente': str, 'id_hotel': str})
data_eventos = pd.read_csv(archivo_extraccion, parse_dates=['fecha_inicio', 'fecha_fin'])
query_ciudad_madrid = "SELECT nombre_ciudad, id_ciudad FROM ciudad"
query_hoteles_carga = "SELECT nombre_hotel, id_hotel FROM hoteles"
query_clientes_carga = "SELECT nombre, id_cliente FROM clientes"

print(info_df(data_hoteles))
print(info_df(data_eventos))


if __name__ == "__main__":
    conn = conexion_BBDD("BBDD_Hoteles")
    carga_tabla_ciudad(conn)
    carga_tabla_eventos(data_eventos, query_ciudad_madrid, conn)
    carga_tabla_hoteles(data_hoteles, query_ciudad_madrid, conn)
    carga_tabla_clientes(data_hoteles, conn)
    carga_tabla_reservas(data_hoteles, query_clientes_carga, query_hoteles_carga, conn)
    conn.close()

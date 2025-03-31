# Importamos las librerías necesarias
import pandas as pd
import numpy as np
import psycopg2 as ps
from src.soporte_carga import conexion_BBDD
from src.soporte_informe import big_numbers, analisis_hoteles


if __name__ == "__main__":
    conn = conexion_BBDD("BBDD_Hoteles")
    big_numbers(conn)
    analisis_hoteles(conn)



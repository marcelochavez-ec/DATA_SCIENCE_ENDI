import pandas as pd
import numpy as np
from src.soporte_limpieza import info_df, data_fechas, cambio_id, limpieza_inicial
import os
from dotenv import load_dotenv

load_dotenv()
archivo_raw = os.getenv("archivo_raw")
archivo_scrapeo = os.getenv("archivo_scrapeo")

df_raw = pd.read_parquet(archivo_raw, engine='auto')
hoteles_competencia_scrapeado = pd.read_csv(archivo_scrapeo)


if __name__ == "__main__":
    limpieza_inicial(df_raw, hoteles_competencia_scrapeado)
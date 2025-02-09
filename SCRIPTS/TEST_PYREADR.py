# Limpiar todas las variables del espacio de nombres global
globals().clear()

import pyreadr
import pandas as pd


def leer_rds(ruta_archivo):
    """Leer archivo RDS y devolver DataFrame de Pandas con ajuste a la variable 'prov'."""
    df = next(iter(pyreadr.read_r(ruta_archivo).values()))
    
    if 'prov' in df.columns:
        df['prov'] = df['prov'].astype(str)
        df['prov'].str.replace('.0', '', regex=True, inplace=True)
        df['prov'] = df['prov'].apply(lambda x: "0" + x if len(x) == 1 and x[0] in "123456789" else x)
    return df

# Llamar a la función y almacenar el DataFrame
f1_personas = leer_rds("C:/Users/marcelochavez/Documents/DATA_SCIENCE_ENDI/DATA/INEC/BDD_ENDI_R2_f1_hogar.rds")
var_f1_personas = pd.DataFrame(f1_personas.dtypes)

f1_personas['prov'] = f1_personas['prov'].astype(str)
f1_personas['prov'] = f1_personas['prov'].str.replace('.0', '', regex=True)
f1_personas['prov'] = f1_personas['prov'].apply(lambda x: "0" + x if len(x) == 1 and x[0] in "123456789" else x)

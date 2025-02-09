# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 21:45:22 2025

@author: marcelochavez
"""

import pandas as pd

df_cp2022 = pd.read_csv("C:/Users/marcelochavez/Documents/DATA_SCIENCE_ENDI/DATA/INEC/BDD_POB_CPV2022_MANLOC.csv", sep=";")

GEDAD = pd.DataFrame(df_cp2022["GEDAD"].value_counts()).reset_index().rename(columns={"count":"GEDAD"})

GEDAD = df_cp2022["GEDAD"].value_counts().reset_index().set_axis(["GRUPOS_EDAD", "TOTAL_POBLACION"], axis=1).sort_values("GRUPOS_EDAD")

GEDAD["TOTAL_POBLACION"].sum()





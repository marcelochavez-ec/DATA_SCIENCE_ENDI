rm(list=ls(all.names = T))

library(readxl)
library(dplyr)
library(tidyr)

setwd("C:/Users/marcelochavez/Documents/TESIS/KARINA/")

filtrar_datos_por_variable <- function(nombre_archivo, 
                                       nombre_hoja,
                                       variable_filtro) {
    # Leer los datos del archivo Excel
    indices_fq <- readxl::read_excel(nombre_archivo,
                                     sheet = nombre_hoja)
    
    # Transformación
    df_largo <- indices_fq %>%
        pivot_longer(cols = -codigo, 
                     names_to = c(".value", "anio"), 
                     names_pattern = "(.*)_(\\d{4})")
    
    # Filtrar los datos según la variable
    datos_filtrados <- df_largo %>%
        pivot_longer(cols = c(ancho,
                              profundidad,
                              velocidad,
                              descarga,
                              ph,
                              temperatura,
                              sta_oxigeno,
                              oxigeno_disuelto,
                              cond_us_cm),
                     names_to = "variable",
                     values_to = "valor") %>% 
        filter(anio == variable_filtro)
    
    return(datos_filtrados)
}

datos_filtrados <- filtrar_datos_por_variable("Datasets/DatosFisicoQuimicos_KHC 13_02_2024.xlsx",
                                              "1995_2021",
                                              1995)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

filtrar_datos_por_variable <- function(nombre_archivo,
                                       nombre_hoja,
                                       variable_filtro) {
    # Leer los datos del archivo Excel
    indices_fq <- readxl::read_excel(nombre_archivo, sheet = nombre_hoja)
    
    # Transformación
    df_largo <- indices_fq %>%
        pivot_longer(cols = -codigo, 
                     names_to = c(".value", "anio"), 
                     names_pattern = "(.*)_(\\d{4})")
    
    # Filtrar los datos en varios data frames según los valores únicos de la variable
    lista_dataframes <- df_largo %>%
        pivot_longer(cols = c(ancho,
                              profundidad,
                              velocidad,
                              descarga,
                              ph,
                              temperatura,
                              sta_oxigeno,
                              oxigeno_disuelto,
                              cond_us_cm),
                     names_to = "variable",
                     values_to = "valor") %>% 
        group_split({{ variable_filtro }})
    
    return(list(lista_dataframes = lista_dataframes,
                df_original = df_largo))
}

# Instanciamiento de la función:
df_reportes <- filtrar_datos_por_variable("Datasets/DatosFisicoQuimicos_KHC 13_02_2024.xlsx",
                                              "1995_2021",
                                              anio)

df_fq_1995 <- df_reportes$lista_dataframes[[1]] # Llamas al objeto del df para el 95 
df_fq_2021 <- df_reportes$lista_dataframes[[2]] # Llamas al objeto del df para el 21

df_indices_fq <- df_reportes$df_original # Llamas al objeto del df orignial de las variables

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

filtrar_datos_por_variable <- function(nombre_archivo, nombre_hoja, variable_filtro) {
    # Leer los datos del archivo Excel
    indices_fq <- readxl::read_excel(nombre_archivo, sheet = nombre_hoja)
    
    # Transformación
    df_largo <- indices_fq %>%
        pivot_longer(cols = -codigo, 
                     names_to = c(".value", "anio"), 
                     names_pattern = "(.*)_(\\d{4})")
    
    # Filtrar los datos en varios data frames según los valores únicos de la variable
    lista_dataframes <- df_largo %>%
        pivot_longer(cols = c(ancho,
                              profundidad,
                              velocidad,
                              descarga,
                              ph,
                              temperatura,
                              sta_oxigeno,
                              oxigeno_disuelto,
                              cond_us_cm),
                     names_to = "variable",
                     values_to = "valor") %>% 
        group_split({{ variable_filtro }})
    
    return(lista_dataframes)
}

# Ejemplo de uso
datos_filtrados <- filtrar_datos_por_variable("Datasets/DatosFisicoQuimicos_KHC 13_02_2024.xlsx",
                                              "1995_2021",
                                              anio)
datos_filtrados[[1]]

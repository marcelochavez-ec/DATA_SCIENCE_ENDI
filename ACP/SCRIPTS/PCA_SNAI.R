
# Librerías y directorio de trabajo---------------------------------------------

rm(list=ls(all.names = T))

setwd("D:/DATA_SCIENCE_ENDI/ACP/")

library(tidyverse)
library(highcharter)
library(cellWise)
library(gridExtra)
library(glue)
library(reshape2)  # Para usar la función melt()
library(e1071)
library(stargazer)
library(factoextra)
library(FactoMineR)
library(knitr)
library(psych)

variables_snai <- readxl::read_excel("VARIABLES_SEGURIDAD_SNAI.xlsx", sheet = "DB_VARIABLES") %>%
  mutate_if(is.numeric, ~ round(., 2)) %>%
  as.data.frame() %>%
  { 
    rownames(.) <- .$CPL_CODIGO
    select(., -CPL_CODIGO)
  }

KMO(variables_snai)

# Realizar la prueba de Bartlett sobre la matriz de correlación de las variables cuantitativas
bartlett_test <- cortest.bartlett(variables_snai)

# Ver el resultado de la prueba de Bartlett
bartlett_test

# Realizar PCA
pca_result <- PCA(variables_snai,
                  scale.unit = TRUE, 
                  ncp = 5, 
                  graph = FALSE)

# Ver el resumen del PCA
summary(pca_result)

# Gráfico del codo para determinar el número de componentes:
scree(variables_snai,
      main ="Gráfico de Sedimentación")
# En este gráfico puedes saber hasta cuantas componentes debe tener tu índice, en este caso son 5

# Gráfico de la varianza explicada por cada componente principal
fviz_eig(pca_result, addlabels = TRUE, ylim = c(0, 50))

# Gráfico de los individuos (observaciones) proyectados en los dos primeros componentes principales
fviz_pca_ind(pca_result, geom = "point", col.ind = "blue", palette = "jco", addEllipses = TRUE)

# Gráfico de las variables (carga en los primeros dos componentes)
fviz_pca_var(pca_result, col.var = "black", alpha.var = 0.5)

# Biplot de individuos y variables
fviz_pca_biplot(pca_result, axes = c(1, 2), geom = c("point", "text"), col.ind = "blue", col.var = "red")

# Extraer las coordenadas de los individuos:

ind_coord <- as.data.frame(pca_result$ind$coord)  # Coordenadas de individuos
ind_coord$CPL_CODIGO <- rownames(ind_coord)  # Agregar nombres

head(ind_coord)  # Ver las primeras filas

# contribuciones de las variables a cada componente

var_contrib <- as.data.frame(pca_result$var$contrib)  # Contribución de variables
var_contrib$VARIABLE <- rownames(var_contrib)  # Agregar nombres

# Ordenar por mayor contribución en el primer componente
var_contrib <- var_contrib %>% arrange(desc(Dim.1))

head(var_contrib)  # Ver las principales variables del PC1

var_contrib_top <- var_contrib %>% pivot_longer(cols = starts_with("Dim"), names_to = "Componente", values_to = "Contribucion")

var_contrib_top %>%
    group_by(Componente) %>%
    slice_max(Contribucion, n = 5) %>%
    arrange(Componente, desc(Contribucion)) %>%
    print(n = 15)  # Muestra las 5 más relevantes por componente

# Relacionar el codigo con las variables más importantes:
# Unir contribuciones de variables y coordenadas de individuos
relevancia <- ind_coord %>%
    pivot_longer(cols = starts_with("Dim"), names_to = "Componente", values_to = "Valor") %>%
    left_join(var_contrib_top, by = "Componente")

# Filtrar para ver las variables más importantes por CPL_CODIGO
relevancia %>%
    group_by(CPL_CODIGO, Componente) %>%
    slice_max(Contribucion, n = 3) %>%  # Tomar las 3 más relevantes
    arrange(CPL_CODIGO, Componente, desc(Contribucion)) %>%
    print(n = 30)  # Mostrar resultados

# Visualizacion
# Obtener la contribución de variables a cada componente
var_contrib_top <- var_contrib %>%
    pivot_longer(cols = starts_with("Dim"), names_to = "Componente", values_to = "Contribucion")

# Para cada componente, genera un gráfico
for (comp in unique(var_contrib_top$Componente)) {
    plot_data <- var_contrib_top %>%
        filter(Componente == comp) %>%
        slice_max(Contribucion, n = 5)  # Tomar las 5 variables más importantes
    
    p <- ggplot(plot_data, aes(x = reorder(VARIABLE, Contribucion), y = Contribucion, fill = VARIABLE)) +
        geom_bar(stat = "identity", show.legend = FALSE) +
        coord_flip() +
        theme_minimal() +
        labs(title = paste("Variables más relevantes en", comp),
             x = "Variable",
             y = "Contribución (%)") +
        scale_fill_brewer(palette = "Set2")
    
    print(p)  # Imprimir gráfico
}

# Construcción del índice:

## Extraer la contribución de cada variable en las primeras 5 dimensiones
var_contrib <- as.data.frame(pca_result$var$contrib[, 1:5])
var_contrib$VARIABLE <- rownames(var_contrib)  # Agregar nombres de variables

# Obtener el máximo valor de contribución por fila (variable)
var_contrib$Max_Varianza <- apply(var_contrib[, 1:5], 1, max)

# Reordenar columnas: variables como filas, dimensiones en columnas, y la varianza máxima al final
varianza_df <- var_contrib %>% select(VARIABLE, everything()) %>% arrange(desc(Max_Varianza))

# ------------------------------------------------------------------------------
# CONSTRUCCIÓN DEL ÍNDICE MULTIVARIANTE:
# ------------------------------------------------------------------------------

# Función para escalar valores entre 0 y 1
scale_values <- function(x) {
    round((x - min(x)) / (max(x) - min(x)), 2)
}

# Obtener el peso máximo por variable
max_varianza <- var_contrib %>%
    pivot_longer(cols = starts_with("Dim"), names_to = "Componente", values_to = "Contribucion") %>%
    group_by(VARIABLE) %>%
    summarise(Max_Varianza = max(Contribucion)) 

# Unir con la base original según el nombre de la variable
variables_snai_pesos <- variables_snai %>%
    rownames_to_column("CPL_CODIGO") %>% 
    pivot_longer(cols = -CPL_CODIGO, names_to = "VARIABLE", values_to = "VALOR") %>%
    left_join(max_varianza, by = "VARIABLE") %>%
    mutate(PONDERADO = VALOR * Max_Varianza) %>%
    group_by(CPL_CODIGO) %>%
    summarise(INDICE_SEGURIDAD_SNAI = sum(PONDERADO, na.rm = TRUE)) %>%
    mutate(IMCS = scale_values(INDICE_SEGURIDAD_SNAI))  # Escalar índice

# Categorizar el índice de seguridad
variables_snai_pesos$CATEGORIA_SNAI <- cut(variables_snai_pesos$IMCS,
                                           breaks = c(-Inf, 0.27, 0.43, Inf),  # Solo 3 intervalos
                                           labels = c("Baja Inseguirdad",
                                                      "Media Inseguridad",
                                                      "Alta Inseguridad"),
                                           right = FALSE)

# Unir el índice con el dataset original
variables_snai_final <- variables_snai %>%
    rownames_to_column("CPL_CODIGO") %>%
    left_join(variables_snai_pesos, by = "CPL_CODIGO") 

# Visualización de los índices
ggplot(variables_snai_pesos, aes(x = reorder(CPL_CODIGO, IMCS), y = IMCS, fill = CATEGORIA_SNAI)) +
    geom_bar(stat = "identity", show.legend = FALSE) +
    coord_flip() +
    theme_minimal() +
    labs(title = "Índice de Seguridad SNAI",
         x = "CPL_CODIGO",
         y = "Índice Normalizado") +
    scale_fill_brewer(palette = "Set2")














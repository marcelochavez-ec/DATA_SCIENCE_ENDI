
# Librerías y directorio de trabajo---------------------------------------------

rm(list=ls(all.names = T))

library(tidyverse)
library(highcharter)
library(cellWise)
library(gridExtra)
library(glue)
library(factoextra)
library(reshape2)  # Para usar la función melt()
library(e1071)
library(stargazer)
library(factoextra)
library(FactoMineR)
library(knitr)

setwd("D:/DATA_SCIENCE_ENDI/ACP/")

# Carga del DataSet ------------------------------------------------------------

indices_fq <- readxl::read_excel("DATASETS/DatosMacroinvertebrados.xlsx") %>% 
    mutate_if(is.numeric, ~ round(., 2))

# Transformaciones de datos ----------------------------------------------------

cols <- c("RIOS","ANIO")

df_largo <- indices_fq %>%
    pivot_longer(cols = -RIOS, 
                 names_to = c(".value", "ANIO"), 
                 names_pattern = "(.*)_(\\d{4})") %>% 
  mutate_at(.vars = cols, .funs = factor)

estadisticos_boxplot <- function(df) {
  
  # Filtra solo las columnas numéricas
  df_numericas <- df[sapply(df, is.numeric)]
  
  # Calcula los cuartiles, mínimo y máximo para cada columna numérica
  cuartiles <- lapply(df_numericas, function(x) round(quantile(x, probs = c(0.25, 0.5, 0.75)), 2))
  minimos <- sapply(df_numericas, function(x) round(min(x), 2))
  maximos <- sapply(df_numericas, function(x) round(max(x), 2))
  
  # Crea un data frame con los resultados
  estadisticos_df <- data.frame(
    VARIABLE = rep(names(df_numericas), each = 5),
    ESTADÍSTICOS = rep(c("Q1", 
                         "Q2",
                         "Q3", 
                         "MÍNIMO",
                         "MÁXIMO"), 
                       times = length(df_numericas)),
    VALOR = c(unlist(cuartiles),
              minimos,
              maximos)
  )
  
  estadisticos_df <- pivot_wider(estadisticos_df,
                                 names_from = VARIABLE, 
                                 values_from = VALOR)
  
  return(estadisticos_df)
}

# Calcula los estadísticos para graficar un boxplot
boxplot_95 <- estadisticos_boxplot(subset(df_largo, ANIO=="1995"))


df_largo_scale <- as.data.frame(lapply(df_largo, function(x) if(is.numeric(x)) scale(x) else x))

df_fq_1995 <- pivot_longer(df_largo_scale,
                                cols = c(ANCHO,
                                         PROFUNDIDAD,
                                         VELOCIDAD,
                                         DESCARGA,
                                         PH,
                                         TEMPERATURA,
                                         OXIGENO_DISUELTO,
                                         CONDUCTIVIDAD,
                                         RIQUEZA,
                                         ABUNDANCIA,
                                         DIVERSIDAD,
                                         ABI,
                                         BMWP,
                                         IBF),
                                names_to = "VARIABLE",
                                values_to = "VALOR") %>% 
    filter(ANIO=="1995")

df_fq_2021 <- pivot_longer(df_largo_scale, 
                           cols = c(ANCHO,
                                    PROFUNDIDAD,
                                    VELOCIDAD,
                                    DESCARGA,
                                    PH,
                                    TEMPERATURA,
                                    OXIGENO_DISUELTO,
                                    CONDUCTIVIDAD,
                                    RIQUEZA,
                                    ABUNDANCIA,
                                    DIVERSIDAD,
                                    ABI,
                                    BMWP,
                                    IBF),
                           names_to = "VARIABLE",
                           values_to = "VALOR") %>% 
    filter(ANIO=="2021")


# Data para BoxPlot:

df_bx_95 <- data_to_boxplot(
    df_fq_1995,
    variable = VALOR,
    group_var = VARIABLE,
    # group_var2 = codigo,
    add_outliers = T
)

df_bx_21 <- data_to_boxplot(
    df_fq_2021,
    variable = VALOR,
    group_var = VARIABLE,
    # group_var2 = codigo,
    add_outliers = T
)


highchart() %>%
    hc_xAxis(type = "category",
             labels = list(
                 rotation = 270
             )) %>%
    hc_add_series_list(df_bx_21) %>%
    hc_xAxis(title = list(text = "VARIABLES")) %>%
    hc_yAxis(title = list(text = "VALORES")) %>%
    hc_title(text = "BOXPLOT COMPARATIVO ENTRE ÍNDICES FÍSICO QUÍMICOS y ECOLÓGICOS") %>%
    hc_subtitle(text = "AÑO 1995", align="left") %>%
    hc_caption(text = "ELABORADO POR: Karina Hernández") %>%
    hc_legend(enabled = F, title = list(text = "<b>ESTACIONES DE MONITOREO:</b>")) %>%
    hc_tooltip(formatter = JS("function() {
    var tooltip = '';
    if (this.point.low && this.point.q1 && this.point.median && this.point.q3 && this.point.high) {
        tooltip += '<b>Variable: </b>' + this.point.name + '<br/>' +
                   '<b>Mínimo: </b>' + this.point.low.toFixed(2) + '</b><br/>' +
                   '<b>Q1: </b>' + this.point.q1.toFixed(2) + '</b><br/>' +
                   '<b>Mediana: </b>' + this.point.median.toFixed(2) + '</b><br/>' +
                   '<b>Q3: </b>' + this.point.q3.toFixed(2) + '</b><br/>' +
                   '<b>Máximo: </b>' + this.point.high.toFixed(2) + '</b><br/>';
    }
    if (this.point.y && !(this.point.low && this.point.q1 && this.point.median && this.point.q3 && this.point.high)) { 
        tooltip += '<b>Valor Atípico: </b>' + this.point.y.toFixed(2) + '<br/>';
    }
    return tooltip;}")) %>% 
    hc_add_theme(hc_theme_gridlight())

# Exploratorio de los datos -----------------------------------------------

exploratorio <- function(df) {
    tipos <- sapply(df, class)
    valores_min <- sapply(df, function(x) ifelse(is.numeric(x), min(x[complete.cases(x)]), NA))
    valores_max <- sapply(df, function(x) ifelse(is.numeric(x), max(x[complete.cases(x)]), NA))
    coeficientes_asimetria <- sapply(df, function(x) ifelse(is.numeric(x), round(e1071::skewness(x[complete.cases(x)]), 2), NA))
    curtosis <- sapply(df, function(x) ifelse(is.numeric(x), round(kurtosis(x[complete.cases(x)]), 2), NA))
    promedio <- sapply(df, function(x) ifelse(is.numeric(x), round(mean(x[complete.cases(x)]), 2), NA))
    medianas <- sapply(df, function(x) ifelse(is.numeric(x), round(median(x[complete.cases(x)]), 2), NA))
    modas <- sapply(df, function(x) ifelse(is.numeric(x), {
        tab <- table(x[complete.cases(x)])
        as.numeric(names(tab)[tab == max(tab)])}, NA))
    rangos <- sapply(df, function(x) ifelse(is.numeric(x), round(max(x[complete.cases(x)]) - min(x[complete.cases(x)]), 2), NA))
    varianzas <- sapply(df, function(x) ifelse(is.numeric(x), round(var(x[complete.cases(x)]), 2), NA))
    desviaciones <- sapply(df, function(x) ifelse(is.numeric(x), round(sd(x[complete.cases(x)]), 2), NA))
    coeficientes_variacion <- sapply(df, function(x) ifelse(is.numeric(x), round(sd(x[complete.cases(x)]) / mean(x[complete.cases(x)]), 2), NA))
    
    resumen <- data.frame(Variable = names(df),
                          Tipo = tipos,
                          Mínimo = valores_min,
                          Máximo = valores_max,
                          Coeficiente_Asimetría = coeficientes_asimetria,
                          Curtósis = curtosis,
                          Promedio = promedio,
                          Mediana = medianas,
                          Moda = modas,
                          Rango = rangos,
                          Varianza = varianzas,
                          Desviación_Estándar = desviaciones,
                          Coeficiente_Variación = coeficientes_variacion,
                          stringsAsFactors = FALSE)
    
    resumen$Tipo <- ifelse(resumen$Tipo == "factor", "Categórica", resumen$Tipo)
    resumen$Tipo <- ifelse(resumen$Tipo == "POSIXct", "Fecha", resumen$Tipo)
    resumen$Tipo <- ifelse(resumen$Tipo == "logical", "Booleana", resumen$Tipo)
    resumen$Tipo <- ifelse(resumen$Tipo == "numeric", "Numérica", resumen$Tipo)
    
    # Elimina los nombres de las etiquetas de las filas
    rownames(resumen) <- NULL
    
    return(resumen)
}

df_exploratorio <- exploratorio(df_largo)


# Función genérica para Boxplot -------------------------------------------

# df_largo <- indices_fq %>%
#     pivot_longer(cols = -codigo, 
#                  names_to = c(".value", "ANIO"), 
#                  names_pattern = "(.*)_(\\d{4})")
# 
# df_transformado <- pivot_longer(df_largo, 
#                                 cols = c(ANCHO,
#                                          PROFUNDIDAD,
#                                          VELOCIDAD,
#                                          DESCARGA,
#                                          PH,
#                                          TEMPERATURA,
#                                          STA_OXIGENO,
#                                          OXIGENO_DISUELTO,
#                                          CONDUCTIVIDAD),
#                                 names_to = "VARIABLE",
#                                 values_to = "VALOR") %>% 
#     filter(codigo=="PMB_1")
# 
# df_transformado %>% 
#     hchart(type = 'column',
#            hcaes(x = 'VARIABLE',
#                  y = 'VALOR',
#                  group = 'ANIO')) %>% 
#     hc_xAxis(title = list(text = "VARIABLES")) %>%
#     hc_yAxis(title = list(text = "VALOR")) %>%
#     hc_title(text = "Comparativo entre Indicadores Físico-Químicos Años 1995-2021") %>%
#     hc_subtitle(text = "Estación de medición: PMB 1", align = "left") %>%
#     hc_caption(text = "Elaborado por: Karina Hernández") %>%
#     hc_legend(enabled = TRUE, title = list(text = "<b>AÑOS:</b>")) %>%
#     hc_tooltip(formatter = JS("function() { 
#                              return '<b>AÑO: </b>' + this.series.name + '<br><b>INDICADOR: </b>' + this.point.y.toFixed(2) + ' %'; 
#                              }")) %>%
#     hc_add_theme(hc_theme_elementary())


# ******************************************************************************
# ******************************************************************************

# Detección de outliers ---------------------------------------------------

# indices_fq_ddc <- df_largo %>%
#     mutate(NRO = sprintf("%02d",
#                          seq_len(n())),
#            ID = glue("{RIOS}_{ANIO}_{NRO}")) %>%
#     select(-RIOS,
#            -ANIO,
#            -NRO) %>%
#     column_to_rownames(var = "ID")

indices_fq_ddc <- df_largo %>%
    mutate(ID = glue("{RIOS}_{ANIO}")) %>%
    column_to_rownames(var = "ID") %>% 
    select(-RIOS,
           -ANIO)


# Tabla de QQPLOT ---------------------------------------------------------

estadisticos_boxplot <- function(df, year) {
  
  df <- subset(df, ANIO == year)
  df <- df[sapply(df, is.numeric)]
  
  cuartiles <- as.data.frame(apply(df, 2, quantile, probs = c(0.25, 0.5, 0.75)))
  rownames(cuartiles) <- c("Q1", "Q2", "Q3")
  
  minimos <- as.data.frame(t(apply(df, 2, min)))
  rownames(minimos) <- "Mínimo"
  
  maximos <- as.data.frame(t(apply(df, 2, max)))
  rownames(maximos) <- "Máximo"
  
  estadisticos <- rbind(cuartiles,
                        minimos,
                        maximos)
  
  # Redondear los valores
  estadisticos <- round(estadisticos, 2)
  
  # Añadir los nombres de las estadísticas como una columna
  estadisticos$ESTADISTICOS <- rownames(estadisticos)
  
  # Reorganizar las columnas
  estadisticos <- estadisticos %>%
    select(ESTADISTICOS, everything())
  
  return(estadisticos)
  
}

# Ejemplo de uso
cuartiles <- estadisticos_boxplot(df_largo, "1995")






























# Componentes Principales -------------------------------------------------
library(psych)

var_scale <- as.data.frame(lapply(indices_fq_ddc, function(x) if(is.numeric(x)) scale(x) else x))

pca <- principal(indices_fq_ddc,
                 nfactors = 5,
                 rotate = "varimax",
                 scores = TRUE)

# Suponiendo que 'pca' es el objeto resultante del análisis factorial con psych
eigenvalues <- 

# Crear un dataframe con los valores propios y las etiquetas de las variables o dimensiones
eigen_df <- data.frame(Values = pca$values,
                       Variables = paste0("Dim.",
                                          1:length(pca$values)))

# Visualizar los valores propios junto con las etiquetas de las variables o dimensiones
print(eigen_df)




# Cálculo de los autovalores y autovectores:
value_pro<-eigen(cor(indices_fq_ddc))
(value_pro$values)
(value_pro$vectors)

Acumulado <- cumsum(value_pro$values)

Prop.acumulado <- Acumulado/sum(value_pro$values)

val.prop.porce <- data.frame(value_pro$values,
                             Acumulado,
                             Prop.acumulado)

row.names(val.prop.porce) = c(expression(lambda[1]),
                              expression(lambda[2]),
                              expression(lambda[3]),
                              expression(lambda[4]),
                              expression(lambda[5]),
                              expression(lambda[6]),
                              expression(lambda[7]),
                              expression(lambda[8]),
                              expression(lambda[9]),
                              expression(lambda[10]),
                              expression(lambda[11]),
                              expression(lambda[12]),
                              expression(lambda[13]),
                              expression(lambda[14]))

colnames(val.prop.porce) <- c("Valor Propio",
                              "Acumulado",
                              "Prop. Acumulado")
kable(val.prop.porce,
      caption = "Valores propios desde la matriz de covarianza",
      digits = 2,
      format.args = list(decimal.mark =","))


# Cos2 de los individuos --------------------------------------------------

# Redondear a dos decimales
round(abs((pca$rotation * (pca$rotation > -0.1))[, 1:5]), 2)

pca$rotation

# Correlaciones -----------------------------------------------------------

# Calcular correlaciones y p-values
correlation_matrix <- cor(indices_fq_ddc)
p_values <- cor.mtest(indices_fq_ddc)$p

# Convertir p-values en asteriscos de acuerdo con el nivel de significancia
significant_level <- ifelse(p_values < 0.001, "***",
                            ifelse(p_values < 0.01, "**",
                                   ifelse(p_values < 0.05, "*", "")))

significant_level

# Crear gráfico
ggplot(data = melt(round(correlation_matrix, 2)), aes(x = Var1, y = Var2, fill = value)) +
    geom_tile() +
    geom_text(aes(label = paste(round(value, 2), significant_level)), color = "black", size = 4) +
    labs(
        title = "Mapa de calor de correlaciones",
        x = "",
        y = "",
        fill = "Nivel de Correlación",
        caption = "Elaborado por: Karina Hernández"
    ) +
    scale_fill_gradient(low = "lightblue", high = "darkblue") +
    theme_minimal() +
    theme(
        axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1),
        axis.title.x = element_text(angle = 90),
        axis.title.y = element_text(angle = 0),
        panel.grid = element_line(color = "#e9ecef", linewidth = 0.5),  # Cambio a linewidth
        panel.border = element_rect(color = "black", fill = NA),
        axis.ticks = element_line(color = "black"),
        axis.line = element_blank(),
        plot.title = element_text(hjust = 0.5),
        plot.caption = element_text(hjust = 0),
        axis.ticks.length = unit(-0.1, "cm")
    )
                                                        
# Clústers ----------------------------------------------------------------

# Método de Codo

var_scale <- as.data.frame(lapply(indices_fq_ddc, function(x) if(is.numeric(x)) scale(x) else x))

algoritmo <- as.data.frame(kmeans(var_scale,
                                  centers = 4,
                                  algorithm = "Hartigan-Wong",
                                  iter.max = 100)$cluster) %>% 
  rename("CLUSTER"="kmeans(var_scale, centers = 4, algorithm = \"Hartigan-Wong\", iter.max = 100)$cluster") %>% 
  mutate(ID = seq_len(nrow(.)))
  
  algoritmo$cluster

fviz_nbclust(var_scale,
             kmeans, 
             method = "wss")+
    labs(subtitle = "Elbow Method") +
    geom_vline(xintercept = 4)


fviz_cluster(algoritmo,
             data = var_scale) +
    theme_minimal()
    
# Configuración del Algoritmo DDC ------------------------------------------

DDCpars = list(fracNA = 0.5,
               numDiscrete = 3,
               precScale = 1e-12,
               cleanNAfirst = "automatic", 
               tolProb = 0.99, 
               corrlim = 0.5,
               combinRule = "wmean",
               returnBigXimp = FALSE,
               silent = FALSE,
               nLocScale = 25000,
               fastDDC = FALSE,
               standType = "1stepM", 
               corrType = "gkwls",
               transFun = "wrap",
               nbngbrs = 100,
               fastDDC = TRUE)

# Aplicación del Algoritmo DDC -----------------------------------------------

DDC_dataframe = DDC(indices_fq_ddc,
                    DDCpars) # Aplicación de la configuración al dataframe

remX = DDC_dataframe$remX # Obtención de la matriz resultante del DDC

cellMap(D=remX, # Obtención del mapa de celdas
        R=DDC_dataframe$stdResid, 
        rowlabels = 1:nrow(remX), 
        columnlabels = colnames(remX), 
        mTitle="Mapa de Celdas para Índices Físico-Químicos y Ecológicos",
        columntitle = "Variables\n
        Elaborado por: Karina Hernández",
        rowtitle = "Mediciones")

# ******************************************************************************
# ******************************************************************************

# Test de Shapito Wilk:

ks.test(indices_fq_ddc$ANCHO,
        "pnorm", 
        mean=mean(indices_fq_ddc$ANCHO),
        sd=sd(indices_fq_ddc$ANCHO))

shapiro.test(indices_fq_ddc$ANCHO)

# QQPLOT para una sola variable:
# ggplot(indices_fq_ddc, aes(sample = ANCHO)) +
#     geom_qq(color = "#003049") +
#     stat_qq_line(color="#fcbf49") +
#     labs(
#         title = "Q-Q Plot del Índice FQ: ANCHO",
#         subtitle = "Para los años 1995 y 2021",
#         x = "Cuantiles teóricos",
#         y = "Cuantiles observados",
#         caption = "Elaborado por: Karina Hernández"
#     ) +
#     theme_minimal() +
#     
#     theme(
#         panel.grid = element_line(color = "#e9ecef", size = 0.5),  # Añadir grid
#         panel.border = element_rect(color = "black", fill = NA),  # Añadir recuadro
#         axis.ticks = element_line(color = "black"),  # Añadir ticks en los ejes
#         axis.line = element_blank(),  # Eliminar líneas de ejes interiores
#         plot.title = element_text(hjust = 0.5),  # Centrar el título
#         plot.caption = element_text(hjust = 0)  # Alinear el footnote a la izquierda
#     ) + 
#     theme(axis.ticks.length = unit(-0.1, "cm")) 
    
# Filtrar solo las variables numéricas
numeric_vars <- indices_fq_ddc[sapply(indices_fq_ddc, is.numeric)]

# Convertir el dataframe en formato largo (long format) para usar facet_wrap
df_long <- tidyr::pivot_longer(numeric_vars, cols = everything())

# Crear el Q-Q plot con facet_wrap
ggplot(df_long, aes(sample = value)) +
    geom_qq(color = "#003049") +
    stat_qq_line(color = "#fcbf49") +
    labs(
        title = "Q-Q Plot para los Índices Físico-Químicos",
        subtitle = "Estaciones de Monitoreo para los años 1995 y 2021",
        x = "Cuantiles teóricos",
        y = "Cuantiles observados",
        caption = "Elaborado por: Karina Hernández"
    ) +
    facet_wrap(~ name, scales = "free") +
    theme_minimal() +
    theme(
        panel.grid = element_line(color = "#e9ecef", size = 0.5),  # Añadir grid
        panel.border = element_rect(color = "black", fill = NA),  # Añadir recuadro
        axis.ticks = element_line(color = "black"),  # Añadir ticks en los ejes
        axis.line = element_blank(),  # Eliminar líneas de ejes interiores
        plot.title = element_text(hjust = 0.5),  # Centrar el título
        plot.caption = element_text(hjust = 0),  # Alinear el footnote a la izquierda
        axis.ticks.length = unit(-0.1, "cm")  # Ajustar longitud de los ticks hacia adentro
    )


ggplot(df_long, aes(x = name, y = value)) +
    geom_boxplot(color = "#0077b6", fill = "#0077b6", alpha = 0.7) +
    labs(
        title = "Comparación de Índices Físico-Químicos",
        x = "INDICADORES",
        y = "VALOR",
        caption = "Elaborado por: Karina Hernández"
    ) +
    theme_minimal(base_size = 12) +  # Establecer el tamaño base de la letra
    theme(
        panel.grid = element_line(color = "#e9ecef", size = 0.5),  # Añadir grid
        panel.border = element_rect(color = "black", fill = NA),  # Añadir recuadro
        axis.ticks = element_line(color = "black"),  # Añadir ticks en los ejes
        axis.line = element_blank(),  # Eliminar líneas de ejes interiores
        plot.title = element_text(hjust = 0.5),  # Centrar el título
        plot.caption = element_text(hjust = 0),  # Alinear el footnote a la izquierda
        axis.ticks.length = unit(-0.1, "cm"),  # Ajustar longitud de los ticks hacia adentro
        axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1)  # Rotar texto del eje x
    )


# PCA ---------------------------------------------------------------------

pca <- prcomp(indices_fq_ddc,
              scale=TRUE,
              center = TRUE,
              method = "varimax")

# INDICE ------------------------------------------------------------------

scale_values <- function(x) {
  round((x - min(x)) / (max(x) - min(x)),2)
}

indices_mcm <- indices_fq_ddc %>%
  mutate(
    INDICE = round(
      0.43 * ANCHO +
        0.42 * PROFUNDIDAD +
        0.30 * VELOCIDAD +
        0.31 * DESCARGA +
        0.05 * PH +
        0.24 * TEMPERATURA +
        0.25 * OXIGENO_DISUELTO +
        0.26 * CONDUCTIVIDAD +
        0.10 * RIQUEZA +
        0.26 * ABUNDANCIA +
        0.25 * DIVERSIDAD +
        0.05 * ABI +
        0.08 * BMWP +
        0.45 * IBF, 2),
    IMCM =  scale_values(INDICE),
    RIOS = row.names(indices_fq_ddc))

# Categorización del I_MCM con etiquetas personalizadas
indices_mcm$IMCM_CATEGORIA <- cut(indices_mcm$IMCM,
                                  breaks = c(-Inf, 
                                             0.29,
                                             0.30,
                                             0.49,
                                             0.62,
                                             Inf),  # Definición de intervalos
                                  labels = c("IMCM Bajo",
                                             "IMCM Bajo",
                                             "IMCM Medio", 
                                             "IMCM Medio", 
                                             "IMCM Alto"),
                                  right = FALSE)

# Calcular el porcentaje de IMCM para cada categoría
# Calcular el porcentaje de IMCM para cada categoría
porcentaje_imcm <- prop.table(table(indices_mcm$IMCM_CATEGORIA)) * 100

library(highcharter)

# Calcular el porcentaje de IMCM para cada categoría
porcentaje_imcm <- prop.table(table(indices_mcm$IMCM_CATEGORIA)) * 100

# Crear el gráfico
highchart() %>%
  hc_chart(type = "pie",
           options3d = list(enabled = TRUE, alpha = 45, beta = 0)) %>%  # Activar el efecto 3D
  hc_add_series(
    type = "pie",
    data = data.frame(name = names(porcentaje_imcm), y = porcentaje_imcm),
    innerSize = "50%",  # Tamaño interior para crear el donut
    name = "Porcentaje",  # Nombre de la serie
    dataLabels = list(format = "{point.name}: {point.percentage:.1f}%"),  # Etiquetas de datos
    center = c("50%", "50%"),  # Centro del donut
    size = "75%",  # Tamaño del donut
    depth = 35  # Profundidad del gráfico 3D
  ) %>%
  hc_legend(enabled = TRUE) %>%  # Habilitar la leyenda
  hc_title(text = "Porcentaje del Índice Multidimensional de las Comunidades de Macroinvertebrados por Categoría") %>%
  hc_subtitle(text = "Elaborado por: Karina Hernández") %>%
  hc_tooltip(formatter = JS("function() {
                              return '<b>Categoría: </b>' + this.point.name + '<br/>' +
                                     '<b>Porcentaje: </b>' + this.percentage.toFixed(2) + '%';
                            }"))


# indices_fq_ddc <- df_largo %>%
#     mutate(ID = glue("{RIOS}_{ANIO}")) %>%
#     column_to_rownames(var = "ID") %>% 
#     select(-RIOS,
#            -ANIO)

# Calcula la matriz de correlación
correlaciones <- round(cor(indices_fq_ddc),2)

df_cor <- melt(correlaciones)

ggplot(data = df_cor,
       aes(x = Var1,
           y = Var2,
           fill = value)) +
    geom_tile() +
    geom_text(aes(label = value),  
              color = "black", size = 4) +
    labs(
        title = "Mapa de calor de correlaciones",
        x = "Variables",
        y = "Variables",
        fill = "Correlación"
    ) +
    scale_fill_gradient(low = "lightblue", high = "darkblue") +
    theme_minimal() +
    theme(
        axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1), 
        axis.title.x = element_text(angle = 90),
        axis.title.y = element_text(angle = 0)  # Mantener etiqueta del eje y en horizontal
    )

# Componentes Principales:

pca <- prcomp(indices_fq_ddc,
              scale = TRUE,
              center = TRUE)

fviz_pca_var(pca,
             col.var = "cos2",
             geom.var = "arrow",
             labelsize = 2,
             repel = TRUE,
             label.var = colnames(pca$coord),
             size.var = pca$var$contrib[, "cos2"]^2) # Ajusta el tamaño de las flechas según la contribución al cuadrado





library(psych)

df_scale <- scale(indices_fq_ddc)

KMO(indices_fq_ddc)

names(pca)

cortest.bartlett(cor(indices_fq_ddc),n=850)

pca$rotation

biplot(x = pca, scale = 0, cex = 0.6, col = c("blue4", "brown3"))



fviz_pca_var(pca, col.var = "cos2",
             geom.var = "arrow",
             labelsize = 2, repel = FALSE)

fviz_screeplot(pca, addlabels = TRUE, ylim = c(0, 100))


#Estandarización de los datos
df <- scale(indices_fq_ddc)


#Primera muestra de un cluster#
#PCA#
p1 <- princomp(df)
fviz_pca_ind(p1)
# plot3d(p1$scores[,1:3])

#Kmeans#

k2<-kmeans(df, centers = 2, iter.max = 100) #se cambia center por el numero de cluster
k2
fviz_cluster(k2, data = df)

k3<-kmeansruns(df,krange = 3, runs = 100)
k3
fviz_cluster(k3, data = df)

k4<-kmeansruns(df,krange = 4, runs = 100)
k4
fviz_cluster(k4, data = df)

#Evaluar numero de cluster#

plot3d(p1$scores[,1:3], col = k2$cluster, size = 6)
#Metodo de Codo#

fviz_nbclust(df,kmeans, method = "wss")+
    labs(subtitle = "Elbow Method")#+geom_vline(xintercept = 4)

#metodo de Silueta#

fviz_nbclust(df, kmeans, method = "silhouette")+
    labs(subtitle = "Silhouette Method")

#Metodo Gad Statistic
set.seed(246)
fviz_nbclust(df, kmeans, nstart=25, method = "gap_stat", nboot = 100)+
    labs(subtitle = "Gap Statistic Metodo")

#Metodo Completo
set.seed(246)
res.nbclust<- NbClust(df, distance = "euclidean", min.nc = 2, max.nc = 4, method = "complete",
                      index = "all")

factoextra::fviz_nbclust(res.nbclust)+ theme_minimal()+
    ggtitle("Numero de Cluster Optimo")+
    theme_classic()































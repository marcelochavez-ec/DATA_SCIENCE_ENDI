

> *Creamos una función genérica que filtre los datos por cada año*
    
    
    ```{r}
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
```

### Filtrado de tablas Boxplot

```{r}
# Instanciamiento de la función:
df_reportes <- filtrar_datos_por_variable("Datasets/DatosFisicoQuimicos_KHC 13_02_2024.xlsx",
                                          "1995_2021",
                                          anio)

df_fq_95 <- df_reportes$lista_dataframes[[1]] # Llamas al objeto del df para el 95 
df_fq_21 <- df_reportes$lista_dataframes[[2]] # Llamas al objeto del df para el 21

df_indices_fq <- df_reportes$df_original # Llamas al objeto del df orignial de las variables

DT::datatable(df_indices_fq <- df_reportes$df_original, options = list(scrollX = TRUE))

# Estructura para los BoxPlot:

df_bx_95 <- data_to_boxplot(
    df_fq_95,
    variable = valor,
    group_var = variable,
    # group_var2 = codigo,
    add_outliers = T
)

df_bx_21 <- data_to_boxplot(
    df_fq_21,
    variable = valor,
    group_var = variable,
    # group_var2 = codigo,
    add_outliers = T
)

```

#### Función genérica para los Boxplot

```{r}
highchart() %>%
    hc_xAxis(type = "category",
             labels = list(
                 rotation = 270
             )) %>%
    hc_add_series_list(df_bx_95) %>%
    hc_xAxis(title = list(text = "VARIABLES")) %>%
    hc_yAxis(title = list(text = "VALORES EN ESCALA ORIGINAL")) %>%
    hc_title(text = "BOXPLOT COMPARATIVO ENTRE ÍNDICES FÍSICO QUÍMICOS PARA EL AÑO 1995") %>%
    hc_subtitle(text = "MAESTRÍA EN BIODIVERSIDAD Y CAMBIO CLIMÁTICO", align="left") %>%
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
        tooltip += '<b>Valor Atípico: </b>' + this.point.y + '<br/>';
    }
    return tooltip;}")) %>% 
    hc_add_theme(hc_theme_gridlight())
```

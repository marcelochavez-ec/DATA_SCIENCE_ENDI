# Limpiar el espacio de trabajo
rm(list = ls(all.names = TRUE))

# Cargar paquetes necesarios
pacman::p_load(
    tidyverse, 
    highcharter,
    glue,
    e1071,
    reshape2, 
    srvyr,
    RPostgreSQL, 
    gt,
    gtExtras,
    data.table)

# Conectar a PostgreSQL
postgresql_conex <- dbConnect(PostgreSQL(),
                              dbname = "db_stat",
                              host = "localhost", 
                              port = 5432,
                              user = "postgres",
                              password = "marce")

# Leer datos desde PostgreSQL
f1_personas <- dbGetQuery(postgresql_conex, "SELECT * FROM endi.f1_personas")

pob_menor5anios <- dbGetQuery(postgresql_conex, "SELECT * FROM endi.censo_pob2022")

# Crear el objeto de diseño de encuesta
f1_personas_diseño <- f1_personas %>%
    as_survey_design(ids = 1, weights = fexp)

# Convertir los datos a diseño de encuesta
reporte_dci <- f1_personas_diseño %>%
    filter(f1_s1_3_1 < 5) %>%
    group_by(prov,provincia) %>%
    summarise(
        indicador_dci = survey_mean(dcronica == 1, na.rm = TRUE),  # Indicador de DCI (%)
        total_con_dci = round(survey_total(dcronica == 1, na.rm = TRUE), 2),  # Total niños con DCI
        total_ninios = round(survey_total(fexp, na.rm = TRUE), 2),  # Total niños menores de 5 años
        total_sin_dci = total_ninios - total_con_dci,  # Total niños sin DCI
        .groups = "drop") %>% 
    arrange(desc(indicador_dci)) %>% 
    inner_join(pob_menor5anios, by="prov") %>% 
    select(-ends_with("_se"), -prov)

# Calcular los límites de los intervalos a partir de 'indicador_dci'
# limites <- quantile(reporte_dci$indicador_dci, probs = seq(0, 1, by = 1/3), na.rm = TRUE)

# Definir etiquetas para los intervalos
# etiquetas <- c(
#     paste0("[", round(limites[1], 2), ", ", round(limites[2], 2), "]"),
#     paste0("[", round(limites[2], 2), ", ", round(limites[3], 2), "]"),
#     paste0("[", round(limites[3], 2), ", ", round(limites[4], 2), "]"))

# Dividir la variable continua 'indicador_dci' en intervalos cerrados
# reporte_dci$intervalos_cerrados <- cut(reporte_dci$indicador_dci, 
#                                        breaks = limites, 
#                                        labels = etiquetas, 
#                                        include.lowest = TRUE, 
#                                        right = TRUE)  # Right = TRUE indica intervalos cerrados a la derecha

# Ver los resultados
# table(reporte_dci$intervalos_cerrados)

# Crear la tabla de reporte con estilos mejorados
tabla_reporte <- reporte_dci %>%
    gt() %>%
    tab_header(
        title = md("**Reporte de Desnutrición Crónica Infantil por Provincia**"),
        subtitle = md("Total de población y DCI en niños menores de 5 años")
    ) %>%
    cols_label(
        provincia = "Provincia",
        total_ninios = "Total Niños Menores de 5 Años",
        total_con_dci = "Total Niños con DCI",
        total_sin_dci = "Total Niños sin DCI",
        indicador_dci = "Indicador DCI (%)"
    ) %>%
    fmt_number(
        columns = vars(total_ninios, total_con_dci, total_sin_dci),
        decimals = 0,
        sep_mark = "."
    ) %>%
    fmt_percent(
        columns = indicador_dci,
        decimals = 1
    ) %>%
    tab_options(
        table.font.size = 14,
        table.border.top.color = "black",
        table.border.bottom.color = "black",
        table.border.left.color = "black",
        table.border.right.color = "black"
    ) %>%
    # Añadir iconos de flechas según el valor de DCI
    text_transform(
        locations = cells_body(columns = vars(indicador_dci)),
        fn = function(x) {
            dplyr::case_when(
                x >= 23 ~ paste0("↑ ", x),  # Nivel alto (flecha arriba)
                x < 23 & x > 16 ~ paste0("⇄ ", x),  # Nivel medio (flecha derecha)
                TRUE ~ paste0("↓ ", x)  # Nivel bajo (flecha abajo)
            )
        }
    ) %>%
    # Mejorar la apariencia de las celdas de la tabla
    tab_style(
        style = list(
            cell_fill(color = "#f5f5f5"),
            cell_text(weight = "bold", color = "black")
        ),
        locations = cells_column_labels()
    ) %>%
    tab_style(
        style = list(
            cell_fill(color = "#e0f7fa")
        ),
        locations = cells_body(columns = vars(provincia))
    )

# Mostrar la tabla mejorada
tabla_reporte

# Reportes estadísticos específicos:

library(psych)
describe(reporte_dci)


library(Hmisc)
describe(reporte_dci)


library(purrr)


map(reporte_dci, ~ if (is.numeric(.x)) { 
    sum(.x, na.rm = TRUE) 
} else { 
    "Variable Categórica No Aplica" 
})






# Tabulado de la pob menor de 5 años de la base del CPV 2022:

censo_pob2022 <- fread("DATA/INEC/BDD_POB_CPV2022_MANLOC.csv", sep = ";")

censo_pob2022 <- censo_pob2022 %>% 
    mutate(I01 = if_else(nchar(I01) == 1 & grepl("^[0-9]+$", I01), paste0("0", I01), as.character(I01))) %>% 
    filter(P03<5) %>% 
    group_by(I01) %>% 
    summarise(pob_menor5anios=n()) %>% 
    rename("prov"="I01")

# Escribir en PostgreSQL con tipos de datos explícitos
dbWriteTable(postgresql_conex, 
             name = c("endi", "censo_pob2022"),  # Esquema y nombre de tabla
             value = censo_pob2022, 
             row.names = FALSE, 
             overwrite = TRUE,  # Sobrescribe la tabla si ya existe
             field.types = c(prov = "VARCHAR(2)", pob_menor5anios = "INTEGER"))  # Definir tipos









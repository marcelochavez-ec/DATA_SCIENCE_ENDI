library(DT)
library(htmltools)

generar_tabla_dt <- function(data,
                             colnames,
                             title,
                             subtitle = NULL, 
                             footnote = NULL, 
                             percentage_col = NULL, 
                             header_color = "#03346E",
                             text_color = "#fff", 
                             border_color = "white", 
                             height = 500) {
    
    # Crear la tabla con opciones personalizadas
    tabla <- DT::datatable(
        data,
        class = 'cell-border stripe',
        caption = tags$caption(
            style = 'caption-side: bottom; text-align: left;',
            strong(title), br(), em(subtitle) # Título y subtítulo
        ),
        extensions = c('Buttons', 'Scroller'),
        rownames = FALSE,
        colnames = colnames,
        options = list(
            scrollX = TRUE,
            scrollY = height,
            scroller = TRUE,
            deferRender = TRUE,
            dom = 'Bfrtip',
            buttons = c('excel'),
            initComplete = DT::JS(
                "function(settings, json) {",
                sprintf("$(this.api().table().header()).css({'background-color': '%s', 'color': '%s'});", header_color, text_color),
                sprintf("$(this.api().table().header()).find('th').css({'border-right': '2px solid %s', 'text-align': 'center'});", border_color),
                "}"
            )
        )
    )
    
    # Aplicar formato de porcentaje si la variable es especificada
    if (!is.null(percentage_col)) {
        tabla <- tabla %>% formatPercentage(percentage_col, 2)
    }
    
    # Agregar el footnote si se proporciona
    if (!is.null(footnote)) {
        tabla <- tabla %>% tagList(
            tags$footer(
                style = "text-align: left; font-style: italic; margin-top: 10px;",
                footnote
            )
        )
    }
    
    return(tabla)
}

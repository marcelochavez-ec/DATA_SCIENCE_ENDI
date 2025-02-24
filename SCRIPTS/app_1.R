library(shiny)
library(shinydashboard)
library(DBI)
library(RPostgres)
library(DT)
library(dplyr)
library(data.table)

# Conexión a PostgreSQL
con <- dbConnect(RPostgres::Postgres(),
                 dbname = "db_stat",
                 host = "localhost",   # Cambia según tu configuración
                 user = "postgres",
                 password = "marce",
                 port = 5432)

ui <- dashboardPage(
    dashboardHeader(title = "Análisis de Datos"),
    dashboardSidebar(
        selectInput("tabla", "Seleccionar Tabla", choices = NULL),
        uiOutput("columnas"),
        uiOutput("filtrar_columnas"),
        actionButton("generar_pivot", "Generar Tabla Dinámica")
    ),
    dashboardBody(
        tabsetPanel(
            tabPanel("Vista de Datos", DTOutput("tabla_datos")),
            tabPanel("Tabla Dinámica", DTOutput("pivot_table"))
        )
    )
)

server <- function(input, output, session) {
    
    # Cargar nombres de tablas
    observe({
        tablas <- dbGetQuery(con, "SELECT table_name FROM information_schema.tables WHERE table_schema = 'endi'")
        updateSelectInput(session, "tabla", choices = tablas$table_name)
    })
    
    # Cargar nombres de columnas dinámicamente
    output$columnas <- renderUI({
        req(input$tabla)
        columnas <- dbGetQuery(con, paste0("SELECT column_name FROM information_schema.columns WHERE table_name = '", input$tabla, "' AND table_schema = 'endi'"))
        checkboxGroupInput("vars", "Seleccionar Variables", choices = columnas$column_name, selected = columnas$column_name)
    })
    
    # Filtrar datos dinámicamente
    output$filtrar_columnas <- renderUI({
        req(input$tabla, input$vars)
        selectInput("filtro", "Filtrar por", choices = c("Ninguno", input$vars), selected = "Ninguno")
    })
    
    # Mostrar datos en DT
    output$tabla_datos <- renderDT({
        req(input$tabla, input$vars)
        query <- paste0("SELECT ", paste(input$vars, collapse = ", "), " FROM endi.", input$tabla)
        df <- dbGetQuery(con, query)
        datatable(df, options = list(pageLength = 10))
    })
    
    # Crear tabla dinámica con totales
    observeEvent(input$generar_pivot, {
        req(input$tabla, input$vars)
        query <- paste0("SELECT ", paste(input$vars, collapse = ", "), " FROM endi.", input$tabla)
        df <- dbGetQuery(con, query)
        
        # Aplicar filtro si se selecciona
        if (input$filtro != "Ninguno") {
            filtro_col <- input$filtro
            df <- df[!is.na(get(filtro_col)), ]  # Reemplaza esto con la lógica de filtrado adecuada
        }
        
        # Agregar totales
        df <- as.data.table(df)
        df[, Total := .N, by = input$vars]
        
        output$pivot_table <- renderDT({
            datatable(df, options = list(
                dom = 'Bfrtip',
                buttons = c('copy', 'csv', 'excel', 'pdf', 'print'),
                scrollX = TRUE,
                paging = FALSE
            ))
        })
    })
    
    # Limpiar la conexión a la base de datos al cerrar la aplicación
    session$onSessionEnded(function() {
        dbDisconnect(con)
    })
}

shinyApp(ui, server)

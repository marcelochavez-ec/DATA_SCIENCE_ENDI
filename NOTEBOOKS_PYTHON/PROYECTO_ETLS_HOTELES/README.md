# Transformando datos en valor: ETL de hoteles 🏨

## 📖 Descripción
Nuestra empresa, dedicada al sector hotelero en Madrid, busca mejorar la toma de decisiones mediante el análisis de datos relevantes de la compañía. Por ello, se nos ha proporcionado un archivo en formato Parquet que contiene información sobre reservas de hoteles del grupo. Nuestro objetivo es realizar una ETL (extraer, transformar y cargar) de estos datos para generar insights relevantes sobre la ocupación hotelera de Madrid y sobre los precios en el mercado hotelero de Madrid. 

## 🗂️ Estructura del Proyecto

```  
/Proyecto_ETL_Hoteles
│
├── /data/                                      # Carpeta para almacenar los datos crudos y procesados.
|        ├── hoteles_competencia.csv            # Datos de eventos de Madrid obtenidos desde una API.
|        ├── hoteles_competencia.csv            # Datos de hoteles de la competencia obtenidos por scraping.
|        ├── reservas_hoteles_limpio.csv        # Datos de hoteles del grupo y de la competencia limpios.
|        └── reservas_hoteles.parquet           # Datos de hoteles del grupo.
|
├── /notebooks/                                  # Notebooks de Jupyter con con análisis preliminares, pruebas de código y exploración de datos.
|        ├── Análisis_inicial.ipynb             # Análisis y limpieza de los datos obtenidos.
|        ├── Scrapeo_info.ipynb                 # Web scraping de los hoteles de la competencia.
|        ├── Extraccion_api.ipynb               # Extracción de información de eventos de una API.
|        ├── Carga_BBDD_Hoteles.ipynb           # Conexión y carga de los datos a la base de datos.
|        ├── Bonus_track.ipynb                  # Análisis de la información de la base de datos.
|        └──  Script_Creacion_BBDD_Hoteles.sql  # Script de creación de la base de datos.
|        
├── /src/                                       # Scripts de procesamiento y modelado
|        ├── soporte_carga.py                   # Funciones auxiliares para la carga de datos a la base.
|        ├── soporte_limpieza.py                # Funciones auxiliares para la limpieza y el procesamiento de datos.
|        ├── soporte_extraccion.py              # Funciones auxiliares para la extraccion de datos mediante web scraping y APIs.
|        └── soporte_informe.py                 # Funciones auxiliares para generar visualizaciones e insights.
|
├── main_carga.py                               # Script para realizar la carga de datos a la base.
├── main_extraccion.py                          # Script para realizar el scraping de datos de la competencia y las llamadas a la API. 
├── main_informe.py                             # Script para realizar el scraping de datos de la competencia
├── main_limpieza.py                            # Script para realizar la limpieza de los datos.
├── main.py                                     # Script para realizar el proceso de ETL y la generación de insights.
├── app.py                                      # Script de creación de un dashbaord interactivo
├── README.md                                   # Descripción del proyecto
├── /requirements.txt                           # Archivo de dependencias para el proyecto
├── .env                                        # Archivo de variables de entorno (no debe subirse al repositorio)
```
  
## 🛠️ Instalación y Requisitos
    
Este proyecto usa Python y PostgreSQL, y requiere las siguientes librerías:

- **pandas**: manejo y análisis de datos estructurados.
- **numpy**: cálculos numéricos y operaciones con arrays.
- **matplotlib**: visualización 
- **seaborn**: visualización avanzada en matplotlib.
- **psycopg2**: conexión y manipulación a bases de datos PostgreSQL en Python.
- **requests**: realización de peticiones para consumir APIs y realizar Web Scraping.
- **selenium**: realización de web scraping.
- **webdriver_manager**: gestión del WebDriver para selenium.
- **Dbeaver (opcional)**: gestión de bases de datos.

## 📊 Resultados y Conclusiones

- Los hoteles del grupo han obtenido una recaudación superior a los de la competencia, además de tener unos precios medios superiores. 
- La valoración media de los hoteles del grupo es inferior a la de los hoteles de la competencia.

Para ver los resultados completos revisar el dashboard creado en Streamlit (app.py) o el siguiente enlace con el dashbaord creado en PowerBi: https://app.powerbi.com/groups/me/reports/5f585c08-83f5-4f5f-b86d-56056d27f027/73a9ce60d0593b3d4860?experience=power-bi&bookmarkGuid=288992a06a124c61ad18

## 🔄 Próximos Pasos
- Obtener información sobre la asistencia de los clientes a los eventos en las fechas de estancia.
- Implementar control de errores y mejorar el código para que sea más eficiente.
- Crear flujos para que cada mes se proporcione un informe similar al obtenido en este proyecto, lo que incluiría realizar scrapeos de la competencia, así como consultas a la API de forma regular.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar el proyecto, por favor abre un pull request o una issue.

## ✒️ Autores
**Gabriela Jiménez Conde** - [gabrielajimenezconde@gmail.com](https://github.com/Gabijc)
        
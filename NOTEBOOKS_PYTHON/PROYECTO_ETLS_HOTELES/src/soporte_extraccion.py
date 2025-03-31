# Importamos las librerías necesarias
import pandas as pd 
import numpy as np 
import requests
from selenium import webdriver # esto nos permite controlar navegadores web mediante código
# from webdriver_manager.chrome import ChromeDriverManager # administra la instalación de chromedriver, que es necesario para controlar google chrome
from selenium.webdriver.chrome.service import Service # permite gestionar el servicio del driver de chrome
import time

def scrapeo_competencia(url):
    """
        Realiza web scraping de información sobre hoteles desde la URL especificada.

        Extrae datos como el nombre del hotel, la cantidad de estrellas y el precio,
        y los almacena en un archivo CSV.

    Args:
        url (str): URL de la página web de donde se extraerán los datos.

    Proceso:
        - Usa Selenium para abrir la página web.
        - Extrae la información de los hoteles mediante selectores CSS.
        - Almacena los datos en un DataFrame de pandas.
        - Guarda los datos en un archivo CSV en la carpeta 'data'.
    
    Salida:
        - Se genera un archivo CSV llamado 'hoteles_competencia.csv' con la siguiente información:
        - Nombre del hotel
        - Cantidad de estrellas
        - Precio por noche (convertido a float)
        - Fecha de reserva 

    Nota:
        - La función introduce un `time.sleep(10)` para esperar la carga de la página.
        - Se cierra el navegador al finalizar.
    """
    
    chromeService = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chromeService)

    driver.get(url)

    time.sleep(10)

    nombre_hotel = driver.find_elements("css selector", "div.hotelblock__content")
    estrellas_hotel = driver.find_elements("css selector", "div.hotelblock__content-ratings")
    precios_hotel = driver.find_elements("css selector", "div.rate-details__price-wrapper")

    diccionario_hoteles = {"nombre_hotel": [],
                "estrellas": [],
                "precio": []}
    
    for hotel in nombre_hotel:
        diccionario_hoteles["nombre_hotel"].append(hotel.text.split("\n")[0])
    
    for estrella in estrellas_hotel:
        diccionario_hoteles["estrellas"].append(estrella.text.split("\n")[1].strip("/"))
    
    for precio in precios_hotel:
        diccionario_hoteles["precio"].append(precio.text.split("\n")[1])

    hoteles_competencia = pd.DataFrame(diccionario_hoteles)
    hoteles_competencia["precio"] = hoteles_competencia["precio"].str.replace("€", "").astype(float)
    hoteles_competencia["estrellas"] = hoteles_competencia["estrellas"].astype(float)
    hoteles_competencia["fecha_reserva"] = pd.to_datetime("2025-02-21")
    
    hoteles_competencia.to_csv("data/hoteles_competencia.csv", index = False)

    print("Scrapeo realizado con éxito")
    driver.close()
    return hoteles_competencia
    

def eventos_api(endpoint): 
    """
    Realiza una solicitud a una API para obtener información sobre eventos y almacena los datos en un archivo CSV.

    La función extrae información de los eventos desde la API especificada en el `endpoint`, 
    la organiza en un diccionario y la convierte en un DataFrame de pandas. 
    Luego, filtra los eventos según su fecha de inicio y fin, y guarda los datos en un archivo CSV.

    Args:
        endpoint (str): URL del endpoint de la API desde donde se extraerán los datos.

    
    Proceso:

        - Realiza una solicitud GET al endpoint.
        - Si la solicitud es exitosa (código 200), convierte los datos en formato JSON.
        - Extrae información relevante de los eventos, incluyendo:
        - Nombre del evento
        - URL del evento
        - Código postal
        - Dirección
        - Horario
        - Organización
        - Fecha de inicio
        - Fecha de fin
        - Almacena la información en un diccionario y la transforma en un DataFrame.
        - Filtra los eventos que ocurran entre el 1 y el 2 de marzo de 2025.
        - Convierte las columnas de fecha a tipo `datetime` y ajusta el tipo de dato del código postal.
        - Guarda los datos en un archivo CSV en la carpeta 'data'.
    
     Salida:

        - Se genera un archivo CSV llamado 'eventos_madrid.csv' con la información extraída y filtrada.

    Nota:

        - Si la solicitud a la API no es exitosa, la función no devuelve ningún resultado.
        - Se eliminan las horas de las columnas de fecha, dejando solo la parte de la fecha.
        - Se usa `errors="coerce"` en la conversión de fechas para evitar errores si los datos son inválidos.
    """
    
    response = requests.get(endpoint) # Creamos la request con la librería requests
    
    if response.status_code == 200: # Comprobamos si la request ha sido exsitosa
         
        data = response.json() # Convertimos la información en un json para poder trabajar con ella

        # Creamos un diccionario en el que meteremos todos los eventos que encontremos
        diccionario = {
            "nombre_evento" : [],
            "url_evento": [],
            "codigo_postal": [],
            "direccion": [],
            "horario": [],
            "organizacion": [],
            "fecha_inicio": [],
            "fecha_fin": []  
        }

        for i in data.get('@graph', []): # accedemos a la clave @graph y a la lista que contiene en su interior, para poder acceder a los eventos dentro de la lista 
            diccionario["nombre_evento"].append(i.get('title', None))
            diccionario["url_evento"].append(i.get('link', None))
            diccionario["codigo_postal"].append(i.get('address', {}).get('area', {}).get('postal-code', 0)) # vamos accediendo a las claves, las cuales si no encuentra devolverá un None
            diccionario["direccion"].append(i.get('address', {}).get('area', {}).get('street-address', None))
            diccionario["horario"].append(i.get('time', None))
            diccionario["organizacion"].append(i.get('organization', {}).get('organization-name', None))
            diccionario["fecha_inicio"].append(i.get('dtstart', None))
            diccionario["fecha_fin"].append(i.get('dtend', None)) 
        
        dataframe = pd.DataFrame(diccionario) # creamos un dataframe a partir del diccionario
        dataframe["fecha_inicio"] = dataframe["fecha_inicio"].apply(lambda x: x.split(" ")[0]) # modificamos las columnas de fecha de inicio y fecha de fin para que solo contengan la fecha y que no tengan la hora
        dataframe["fecha_fin"] = dataframe["fecha_fin"].apply(lambda x: x.split(" ")[0])

        dataframe = dataframe[(dataframe["fecha_inicio"] <= '2025-03-01') & (dataframe["fecha_fin"] >= '2025-03-02')] # Aplicamos el filtro para que nos coja solo los eventos que se encuentren en las fechas indicadas anteriormente

        # Modificamos el tipo de dato de las columnas que nos interesa modificar

        dataframe["codigo_postal"] = dataframe["codigo_postal"].astype(int)
        dataframe["fecha_inicio"] = pd.to_datetime(dataframe["fecha_inicio"], errors = "coerce")
        dataframe["fecha_fin"] = pd.to_datetime(dataframe["fecha_fin"], errors =  "coerce")

        dataframe.to_csv("data/eventos_madrid.csv", index = False)
        print("Extracción de la API realizada con éxito")
        return dataframe
        
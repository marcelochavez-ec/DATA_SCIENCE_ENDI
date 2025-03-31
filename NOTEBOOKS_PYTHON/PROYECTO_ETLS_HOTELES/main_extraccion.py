# Importamos las librerías necesarias
import pandas as pd 
import numpy as np 
import requests
from selenium import webdriver # esto nos permite controlar navegadores web mediante código
from webdriver_manager.chrome import ChromeDriverManager # administra la instalación de chromedriver, que es necesario para controlar google chrome
from selenium.webdriver.chrome.service import Service # permite gestionar el servicio del driver de chrome
import time
from src.soporte_extraccion import scrapeo_competencia, eventos_api
import os 
from dotenv import load_dotenv

load_dotenv()
url_api = os.getenv("url_api")
url_scrapeo = os.getenv("url_scrapeo")

url_scrapeo_competencia = url_scrapeo

enp = url_api

if __name__ == "__main__":
    scrapeo_competencia(url_scrapeo_competencia)
    eventos_api(enp)
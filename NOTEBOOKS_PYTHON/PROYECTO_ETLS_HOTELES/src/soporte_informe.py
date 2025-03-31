import pandas as pd
import numpy as np
from IPython.display import Markdown, display
import seaborn as sns
import matplotlib.pyplot as plt
import time


def creacion_vista(conn, nombre_vista, com_gr):
    """
    Crea una vista en la base de datos con información sobre hoteles, reservas y clientes.

    Esta función crea una vista en la base de datos que une las tablas 'hoteles', 'reservas' y 'clientes', 
    proporcionando información detallada sobre las reservas realizadas en los hoteles. La vista contiene 
    los siguientes campos: id del hotel, nombre del hotel, valoración del hotel, id de la reserva, fecha de 
    la reserva, precio por noche, id del cliente y el nombre completo del cliente. La vista se crea solo para 
    los hoteles que tienen un valor en la columna 'competencia' igual al parámetro `com_gr`.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.
        nombre_vista (str): Nombre que se asignará a la vista que se va a crear.
        com_gr (str): Valor de competencia de los hoteles que se incluirán en la vista.

    Returns:
        str: Mensaje indicando que la vista ha sido creada correctamente.

    Ejemplo:
        creacion_vista(conn, "vista_hoteles_reservas", "Alta")
    """
    cur = conn.cursor()

    query = f""" 
        CREATE VIEW "{nombre_vista}" AS
        SELECT 
            h.id_hotel ,
            h.nombre_hotel,
            h.valoracion,
            r.id_reserva,
            r.fecha_reserva,
            r.precio_noche,
            c.id_cliente,
            concat(c."nombre", ' ', c."apellido")
        FROM hoteles as h
            INNER JOIN  reservas AS r ON h.id_hotel = r.id_hotel
            INNER JOIN  clientes AS c ON r.id_cliente = c.id_cliente
        WHERE h.competencia = {com_gr}; 
        """

    cur.execute(query)
    conn.commit()

    return f"Vista_creada_correctamente"

# Recaudacion total anual
def recaudacion_anual(conn, vista):
    """
    Calcula la recaudación anual total a partir de los datos en una vista.

    Esta función calcula la recaudación total por las reservas realizadas, sumando los precios por noche 
    de todas las reservas en la vista proporcionada. El resultado es redondeado a dos decimales.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.
        vista (str): El nombre de la vista que contiene los datos de las reservas.

    Returns:
        float: La recaudación anual total redondeada a dos decimales.

    Ejemplo:
        recaudacion_anual(conn, "vista_hoteles_reservas")
    """
    cur = conn.cursor()

    query_rec_grupo = f""" 
                SELECT 
                    SUM(precio_noche)
                FROM "{vista}"; 
        """

    cur.execute(query_rec_grupo)
    rec_total = cur.fetchall()
    return round(rec_total[0][0], 2)

# Precio medio noche
def precio_medio(conn, vista):
    """
    Calcula el precio medio por noche de las reservas en una vista.

    Esta función calcula el precio promedio por noche de todas las reservas contenidas en la vista proporcionada. 
    El resultado es redondeado a dos decimales.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.
        vista (str): El nombre de la vista que contiene los datos de las reservas.

    Returns:
        float: El precio medio por noche redondeado a dos decimales.

    Ejemplo:
        precio_medio(conn, "vista_hoteles_reservas")
    """
    cur = conn.cursor()

    query_p_medio = f""" 
            SELECT AVG(precio_noche)
            FROM "{vista}"; 
    """

    cur.execute(query_p_medio)
    p_medio = cur.fetchall()
    return round(p_medio[0][0], 2)

# Nº de reservas totales
def n_reservas(conn, vista):
    """
    Obtiene el número total de reservas en una vista.

    Esta función cuenta el número total de reservas presentes en la vista proporcionada 
    y devuelve ese número.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.
        vista (str): El nombre de la vista que contiene los datos de las reservas.

    Returns:
        int: El número total de reservas en la vista.

    Ejemplo:
        n_reservas(conn, "vista_hoteles_reservas")
    """
    cur = conn.cursor()

    query_n_reservas = f""" 
            SELECT count(id_reserva)
            FROM "{vista}"; 
    """

    cur.execute(query_n_reservas)
    reservas_tot = cur.fetchall()
    return reservas_tot[0][0]

# Valoracion media
def valoracion_media(conn, vista):
    """
    Calcula la valoración media de los hoteles en una vista.

    Esta función calcula el promedio de la valoración de los hoteles en la vista proporcionada
    y devuelve el valor redondeado a dos decimales.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.
        vista (str): El nombre de la vista que contiene los datos de las valoraciones de los hoteles.

    Returns:
        float: La valoración media de los hoteles en la vista, redondeada a dos decimales.

    Ejemplo:
        valoracion_media(conn, "vista_hoteles_reservas")
    """
    cur = conn.cursor()

    query_v_media = f""" 
            SELECT AVG(valoracion)
            FROM "{vista}"; 
    """

    cur.execute(query_v_media)
    v_media = cur.fetchall()
    return round(v_media[0][0], 2)

# Nº de hoteles totales
def n_hoteles(conn, vista):
    cur = conn.cursor()

    query_n_hoteles = f""" 
            SELECT count(distinct id_hotel)
            FROM "{vista}"; 
    """

    cur.execute(query_n_hoteles)
    n_hoteles = cur.fetchall()
    return n_hoteles[0][0]

def n_clientes(conn, tabla):
    cur = conn.cursor()

    query_n_clientes = f""" 
            SELECT count(distinct id_cliente)
            FROM "{tabla}"; 
    """

    cur.execute(query_n_clientes)
    n_clientes = cur.fetchall()
    return n_clientes[0][0]

def recurrencia_clientes(conn, tabla, parametro = "clientes recurrentes"):
    cur = conn.cursor()
    if parametro == "clientes recurrentes":

        query = f"""
            WITH cte_recurrencia_clientes AS (
            SELECT 
                    id_cliente,
                    count(DISTINCT id_reserva) AS numero_reservas
            FROM "{tabla}"
            GROUP BY  id_cliente
                    HAVING count(DISTINCT id_reserva) > 1
            ORDER BY 2 desc
            )
            SELECT 
                    count(DISTINCT id_cliente)
            FROM cte_recurrencia_clientes;
            """
    elif parametro == "clientes no recurrentes":
            query = f"""
            WITH cte_recurrencia_clientes AS (
            SELECT 
                    id_cliente,
                    count(DISTINCT id_reserva) AS numero_reservas
            FROM "{tabla}"
            GROUP BY  id_cliente
                    HAVING count(DISTINCT id_reserva) <= 1
            ORDER BY 2 desc
            )
            SELECT 
                    count(DISTINCT id_cliente)
            FROM cte_recurrencia_clientes;
            """

    cur.execute(query)
    n_clientes = cur.fetchall()
    return n_clientes[0][0]

def cuota_mercado(conn, tabla):
   
    cur = conn.cursor()
    # Vamos a analizar los ingresos por hotel, y el numero de reservas por hotel
    query = f""" SELECT 
	                competencia,
	                count(DISTINCT id_hotel) AS Nº_hoteles
                FROM {tabla} 
                GROUP BY competencia;
            """

    cur.execute(query)
    q = cur.fetchall()
    dataframe = pd.DataFrame(q)
    dataframe = dataframe.rename(columns = {0: "Competencia", 1: "Nº_hoteles"})
    dataframe["Competencia"] = dataframe["Competencia"].apply(lambda x: "Hoteles de la competencia" if x == True else "Hoteles del grupo")
    dataframe["Cuota de mercado"] = round(dataframe['Nº_hoteles']/29, 2)*100
    
    return dataframe

def cuota_clientes(conn, tabla_1, tabla_2):
   
    cur = conn.cursor()
    # Vamos a analizar los ingresos por hotel, y el numero de reservas por hotel
    query = f""" SELECT 
	                competencia,
	                count(DISTINCT r.id_cliente) AS Nº_clientes
                FROM {tabla_1} as r
	                JOIN  {tabla_2} as h ON r.id_hotel = h.id_hotel 
                GROUP BY competencia ;
            """

    cur.execute(query)
    q = cur.fetchall()
    dataframe = pd.DataFrame(q)
    dataframe = dataframe.rename(columns = {0: "Competencia", 1: "Nº_clientes"})
    dataframe["Competencia"] = dataframe["Competencia"].apply(lambda x: "Clientes de la competencia" if x == True else "Clientes del grupo")
    dataframe["Cuota clientes"] = round((dataframe['Nº_clientes']/dataframe["Nº_clientes"].sum())*100, 2)
    
    return dataframe

def ticket_medio(ingresos, reservas):
    
    ticket_medio_calc = ingresos/reservas
    return ticket_medio_calc

def reservas_medias(reservas, hoteles):
    
    reservas_medias_hotel = reservas/hoteles
    return reservas_medias_hotel

def ingresos_medios_hotel(ingresos, hoteles):
    
    ingresos_medios = ingresos/hoteles
    return ingresos_medios

def info_hoteles(conn, parámetro = "mercado"):
    cur = conn.cursor()

    if parámetro == "mercado":
        query = """ SELECT 
	                    nombre_hotel,
	                    sum(precio_noche) AS "Ingresos",
	                    count(DISTINCT id_reserva) AS "Nº_reservas",
                        avg(h.valoracion) AS "Valoracion_media"
                    FROM hoteles h 
	                    JOIN reservas r ON h.id_hotel = r.id_hotel	
                    GROUP BY nombre_hotel
                    ORDER BY 2 DESC;
                    """ 
        
    elif parámetro == "grupo":
        query = """ 
                SELECT 
                    nombre_hotel,
                    sum(precio_noche),
                    count(id_reserva),
                    avg(valoracion)
                FROM "Vista_hoteles_grupo"
                GROUP BY nombre_hotel
                ORDER BY 2 DESC; 
                """
    elif parámetro == "competencia":
        query = """ 
                SELECT 
                    nombre_hotel,
                    sum(precio_noche),
                    count(id_reserva),
                    avg(valoracion)
                FROM "Vista_hoteles_competencia"
                GROUP BY nombre_hotel
                ORDER BY 2 DESC; 
                """
    cur.execute(query)
    q = cur.fetchall()
    dataframe = pd.DataFrame(q)
    dataframe = dataframe.rename(columns = {0: "Hotel", 1: "Ingresos", 2: "Nº reservas", 3:"Valoracion media"})
    return dataframe

def info_temporales(conn, parámetro = "mercado"):
    cur = conn.cursor()

    if parámetro == "mercado":
        query = """ 
                SELECT 
	                fecha_reserva ,
	                sum(precio_noche) AS "Ingresos_por_fecha",
	                count(DISTINCT id_reserva) AS "Nº_reservas"
                FROM reservas r 
                GROUP BY fecha_reserva ;
                """ 
        
    elif parámetro == "grupo":
        query = """ 
                SELECT 
	                fecha_reserva ,
	                sum(precio_noche) AS "Ingresos_por_fecha",
	                count(DISTINCT id_reserva) AS "Nº_reservas"
                FROM "Vista_hoteles_grupo"
                GROUP BY fecha_reserva;
                """
    elif parámetro == "competencia":
        query = """ 
                SELECT 
                    fecha_reserva ,
                    sum(precio_noche) AS "Ingresos_por_fecha",
                    count(DISTINCT id_reserva) AS "Nº_reservas"
                FROM "Vista_hoteles_competencia"
                GROUP BY fecha_reserva;
                """
    cur.execute(query)
    q = cur.fetchall()
    dataframe = pd.DataFrame(q)
    dataframe = dataframe.rename(columns = {0: "fecha_reserva", 1: "Ingresos", 2: "Nº reservas"})
    return dataframe

def info_clientes(conn):
    cur = conn.cursor()

    query = """ 
                SELECT 
	                concat(c.nombre, ' ', c.apellido) AS "Nombre_cliente",
	                sum(r.precio_noche) AS "Gasto_total",
	                count(DISTINCT r.id_reserva)
                FROM clientes c 
	                JOIN reservas r ON c.id_cliente = r.id_cliente 
                GROUP BY concat(c.nombre, ' ',c.apellido);
                """ 
    cur.execute(query)
    q = cur.fetchall()
    dataframe = pd.DataFrame(q)
    dataframe = dataframe.rename(columns = {0: "Cliente", 1: "Gasto", 2: "Nº reservas"})
    return dataframe   


# Aquí están los gráficos no usados para el dashboard en streamlit

def grafico_hoteles(conn, vista, titulo_recaudacion, titulo_reservas):
    """
    Genera un gráfico de barras para analizar los ingresos y el número de reservas por hotel.

    Esta función ejecuta una consulta SQL para obtener los ingresos y el número de reservas
    por hotel, y luego genera dos gráficos de barras utilizando `seaborn`. El primer gráfico
    muestra la recaudación por hotel y el segundo el número de reservas por hotel.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.
        vista (str): El nombre de la vista que contiene los datos de reservas y precios.
        titulo_recaudacion (str): Título para el gráfico de recaudación.
        titulo_reservas (str): Título para el gráfico de número de reservas.

    Returns:
        None: Muestra los gráficos generados sin retornar ningún valor.

    Ejemplo:
        grafico_hoteles(conn, "vista_hoteles_reservas", "Recaudación por Hotel", "Número de Reservas por Hotel")
    """
    cur = conn.cursor()
    # Vamos a analizar los ingresos por hotel, y el numero de reservas por hotel
    query = f""" 
        SELECT 
                nombre_hotel,
                sum(precio_noche),
                count(id_reserva)
        FROM "{vista}"
        GROUP BY nombre_hotel
        ORDER BY 2 DESC; 
"""

    cur.execute(query)
    q = cur.fetchall()
    dataframe = pd.DataFrame(q)

    fig, axes = plt.subplots(nrows = 1, ncols = 2, figsize = (20, 5))

    sns.barplot(x = 0, 
                y = 1,
                data = dataframe,
                ax = axes[0])
    sns.barplot(x = 0, 
                y = 2,
                data = dataframe, 
                ax = axes[1])

    axes[0].set_title(titulo_recaudacion, fontsize = 10)
    axes[0].set_xlabel("Nombre_hotel", fontsize = 10)
    axes[0].set_ylabel("Recaudacion", fontsize = 10)
    axes[0].spines['right'].set_visible(False)
    axes[0].spines['top'].set_visible(False)
    axes[0].set_xticklabels(labels = dataframe[0], rotation=45, ha='right')


    axes[1].set_title(titulo_reservas, fontsize = 10)
    axes[1].set_ylabel("Nº_reservas", fontsize = 10)
    axes[1].set_xlabel("Nombre_hotel", fontsize = 10)
    axes[1].spines['right'].set_visible(False)
    axes[1].spines['top'].set_visible(False)
    axes[1].set_xticklabels(labels = dataframe[0], rotation=45, ha='right')

    plt.show()
    plt.close(fig)

def grafico_temporal(conn):
    cur = conn.cursor()
    query = """ 

        SELECT 
                fecha_reserva,
                sum(precio_noche)
        FROM "Vista_hoteles_grupo"
        GROUP BY fecha_reserva
        ORDER BY 2 DESC; 
"""

    cur.execute(query)
    q = cur.fetchall()
    df = pd.DataFrame(q)
    fig, ax = plt.subplots(figsize=(10, 5))

    sns.lineplot(x=0,
                y=1,
                data=df)

    ax.set_title(f"Recaudación Temporal Hoteles del grupo", fontsize=10)
    ax.set_xlabel("Fecha", fontsize=10)
    ax.set_ylabel("Recaudación", fontsize=10)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_xticks(df[0])
    ax.set_xticklabels(df[0], rotation=45, ha='right')

    plt.show()


def big_numbers(conn):
    """
    Calcula y muestra las métricas clave para el análisis de los hoteles del grupo y su competencia.

    Esta función crea dos vistas en la base de datos: una para los hoteles del grupo y otra para los hoteles de la competencia. 
    Luego, calcula varias métricas como la recaudación total, el precio medio, el número de reservas totales y la valoración media 
    tanto para los hoteles del grupo como para los de la competencia, utilizando las vistas creadas. Finalmente, imprime una tabla 
    con los resultados de las métricas calculadas.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.

    Returns:
        None: Muestra la tabla con las métricas calculadas en la consola. No retorna ningún valor.

    Ejemplo:
        big_numbers(conn)
    """
    try:

        creacion_vista(conn, "Vista_hoteles_grupo", False)
        creacion_vista(conn, "Vista_hoteles_competencia", True)

        rec_total = recaudacion_anual(conn, "Vista_hoteles_grupo")
        rec_total_c = recaudacion_anual(conn, "Vista_hoteles_competencia")
        p_medio = precio_medio(conn, "Vista_hoteles_grupo")
        p_medio_c = precio_medio(conn, "Vista_hoteles_competencia")
        reservas_tot = n_reservas(conn, "Vista_hoteles_grupo")
        reservas_tot_c = n_reservas(conn, "Vista_hoteles_competencia")
        v_media = valoracion_media(conn, "Vista_hoteles_grupo")
        v_media_c = valoracion_media(conn, "Vista_hoteles_competencia")

        tabla_bn = f"""
        | Metrica            | Hoteles_Grupo | Hoteles_Competencia  |
        |--------------------|---------------|--------------------- |
        | Recaudacion Total  |{rec_total}    |  {rec_total_c}       |
        | Precio Medio       |{p_medio}      |  {p_medio_c}         |
        | Reservas Totales   |{reservas_tot} |  {reservas_tot_c}    |
        | Valoracion Media   |{v_media}      |  {v_media_c}         | 
        """
        print(tabla_bn)

    except Exception as e:
        print(f"Error: {e}")

def analisis_hoteles(conn):
    """
    Realiza un análisis gráfico de los datos relacionados con los hoteles del grupo y su competencia.

    Esta función genera varios gráficos que permiten analizar visualmente el comportamiento de los hoteles del grupo y de la competencia. 
    Incluye un gráfico temporal de la recaudación a lo largo del tiempo y gráficos de recaudación y número de reservas por hotel, tanto 
    para los hoteles del grupo como para los de la competencia.

    Args:
        conn (psycopg2.connection): Objeto de conexión a la base de datos PostgreSQL.

    Returns:
        None: La función genera y muestra gráficos visuales, pero no retorna ningún valor.

    Ejemplo:
        analisis_hoteles(conn)
    """
    grafico_temporal(conn)
    grafico_hoteles(conn, "Vista_hoteles_grupo", "Recaudacion por hotel del grupo", "Numero de reservas por hotel del grupo")
    grafico_hoteles(conn, "Vista_hoteles_competencia", "Recaudacion por hotel de la competencia", "Numero de reservas por hotel de la competencia")

CREATE TABLE ciudad (
    id_ciudad SERIAL PRIMARY KEY,
    nombre_ciudad TEXT
);

CREATE TABLE eventos (
	id_evento SERIAL PRIMARY KEY,
    nombre_evento TEXT,
    url_evento TEXT,
    codigo_postal INT,
    direccion TEXT,
    horario TEXT,
    organizacion TEXT,
    id_ciudad INT REFERENCES ciudad(id_ciudad) ON DELETE CASCADE
); 

CREATE TABLE clientes (
    "id_cliente" VARCHAR(255) PRIMARY KEY,
    "nombre" TEXT,
    "apellido" TEXT,
    "mail" TEXT UNIQUE CHECK (mail LIKE '%@%')
);

CREATE TABLE hoteles (
	"id_hotel" VARCHAR(255) PRIMARY KEY, 
	"Nombre_hotel" TEXT,
	"estrellas" INT CHECK ("estrellas" BETWEEN 1 AND 5),
	"id_ciudad" INT REFERENCES ciudad(id_ciudad) ON DELETE CASCADE,
	"Competencia" BOOL 
);

CREATE TABLE reservas (
	"id_reserva" VARCHAR(50) PRIMARY KEY,
    "fecha_reserva" DATE,
    "inicio_estancia" DATE,
    "final_estancia" DATE,
    "precio_noche" FLOAT CHECK ("precio_noche" >= 0),
    "id_cliente" VARCHAR(50) REFERENCES clientes("id_cliente") ON DELETE CASCADE,
    "id_hotel" INT REFERENCES hoteles("id_hotel") ON DELETE CASCADE
);


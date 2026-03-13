import sqlite3
import json
import config


def listar_ciclos(handler):

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("SELECT ciclo FROM cicloescolar ORDER BY ciclo")

    datos = cursor.fetchall()
    conexion.close()

    lista=[]

    for c in datos:
        lista.append(c[0])

    handler.send_response(200)
    handler.send_header("Content-type","application/json")
    handler.end_headers()

    handler.wfile.write(json.dumps(lista).encode())


def crear_ciclo(handler):

    longitud = int(handler.headers['Content-Length'])
    datos = handler.rfile.read(longitud).decode()
    datos_json = json.loads(datos)

    ciclo = datos_json["ciclo"]

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("""
    INSERT INTO cicloescolar(ciclo)
    VALUES(?)
    """,(ciclo,))

    conexion.commit()
    conexion.close()

    handler.send_response(200)
    handler.end_headers()

    handler.wfile.write(b"Ciclo creado")


def eliminar_ciclo(handler):

    longitud = int(handler.headers['Content-Length'])
    datos = handler.rfile.read(longitud).decode()
    datos_json = json.loads(datos)

    ciclo = datos_json["ciclo"]

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("""
    DELETE FROM cicloescolar
    WHERE ciclo=?
    """,(ciclo,))

    conexion.commit()
    conexion.close()

    handler.send_response(200)
    handler.end_headers()

    handler.wfile.write(b"Ciclo eliminado")
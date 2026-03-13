import sqlite3
import json
import config

def listar_programas(handler):

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT DISTINCT programa
    FROM usuarios
    WHERE programa != 'sistema'
    ORDER BY programa
    """)

    datos = cursor.fetchall()
    conexion.close()

    lista = []

    for p in datos:
        lista.append(p[0])

    handler.send_response(200)
    handler.send_header("Content-type","application/json")
    handler.end_headers()

    handler.wfile.write(json.dumps(lista).encode())
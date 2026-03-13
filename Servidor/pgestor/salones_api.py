import sqlite3
import json
import config
import cgi
import openpyxl
import os
import io


def listar_salones(handler):

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id, programa, edificio, salon, capacidad
    FROM salones
    """)

    datos = cursor.fetchall()

    conexion.close()

    lista=[]

    for s in datos:

        lista.append({

        "id":s[0],
        "programa":s[1],
        "edificio":s[2],
        "salon":s[3],
        "capacidad":s[4]

        })

    handler.send_response(200)
    handler.send_header("Content-type","application/json")
    handler.end_headers()

    handler.wfile.write(json.dumps(lista).encode())
    

def agregar_salon(handler):

    longitud = int(handler.headers['Content-Length'])

    datos = handler.rfile.read(longitud).decode()

    datos_json = json.loads(datos)

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    programa = (datos_json["programa"] or "").strip()
    edificio = (datos_json["edificio"] or "").strip()
    salon = (datos_json["salon"] or "").strip()
    capacidad = datos_json["capacidad"] or 0
    
    if not programa or not salon:
        handler.send_response(400)
        handler.end_headers()
        handler.wfile.write(b"Programa y salon son obligatorios")
        return

    cursor.execute("""
    INSERT INTO salones
    (programa,edificio,salon,capacidad)
    VALUES (?,?,?,?)
    """,(programa,edificio,salon,capacidad))

    conexion.commit()
    conexion.close()

    handler.send_response(200)
    handler.end_headers()

    handler.wfile.write(b"Salon agregado")


def eliminar_salon(handler):

    longitud = int(handler.headers['Content-Length'])

    datos = handler.rfile.read(longitud).decode()

    datos_json = json.loads(datos)

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    cursor.execute(
    "DELETE FROM salones WHERE id=?",
    (datos_json["id"],)
    )

    conexion.commit()
    conexion.close()

    handler.send_response(200)
    handler.end_headers()

    handler.wfile.write(b"Salon eliminado")


def editar_salon(handler):

    longitud = int(handler.headers['Content-Length'])

    datos = handler.rfile.read(longitud).decode()

    datos_json = json.loads(datos)

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    programa = (datos_json["programa"] or "").strip()
    edificio = (datos_json["edificio"] or "").strip()
    salon = (datos_json["salon"] or "").strip()
    capacidad = datos_json["capacidad"] or 0
    salon_id = datos_json["id"]
    
    if not programa or not salon:
        handler.send_response(400)
        handler.end_headers()
        handler.wfile.write(b"Programa y salon son obligatorios")
        return

    cursor.execute("""

    UPDATE salones
    SET programa=?, edificio=?, salon=?, capacidad=?
    WHERE id=?

    """,(programa,edificio,salon,capacidad,salon_id))

    conexion.commit()
    conexion.close()

    handler.send_response(200)
    handler.end_headers()

    handler.wfile.write(b"Salon actualizado")
    
def importar_salones(handler):

    form = cgi.FieldStorage(
        fp=handler.rfile,
        headers=handler.headers,
        environ={
            'REQUEST_METHOD':'POST',
            'CONTENT_TYPE':handler.headers['Content-Type']
        }
    )

    archivo = form['archivo']

    if not archivo.filename:
        handler.send_response(400)
        handler.end_headers()
        handler.wfile.write(b"No se envio archivo")
        return

    contenido = archivo.file.read()

    wb = openpyxl.load_workbook(io.BytesIO(contenido))
    hoja = wb.active

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    insertados = 0

    for fila in hoja.iter_rows(min_row=2, values_only=True):

        programa = str(fila[0] or "").strip() if len(fila) > 0 else ""
        edificio = str(fila[1] or "").strip() if len(fila) > 1 else ""
        salon = str(fila[2] or "").strip() if len(fila) > 2 else ""
        capacidad = int(fila[3] or 0) if len(fila) > 3 else 0

        if not programa or not salon:
            continue

        cursor.execute("""
        INSERT INTO salones
        (programa,edificio,salon,capacidad)
        VALUES (?,?,?,?)
        """,(programa,edificio,salon,capacidad))

        insertados += 1

    conexion.commit()
    conexion.close()

    handler.send_response(200)
    handler.end_headers()

    mensaje = f"{insertados} salones importados"
    handler.wfile.write(mensaje.encode())
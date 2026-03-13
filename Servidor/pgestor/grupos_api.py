from openpyxl import load_workbook
import cgi
import io
import sqlite3
import json
import config

def listar_grupos(handler):

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT id,programa,semestre,grupo,tipo,alumnos
    FROM grupos
    """)

    datos = cursor.fetchall()
    conexion.close()

    lista=[]

    for g in datos:
        lista.append({
        "id":g[0],
        "programa":g[1],
        "semestre":g[2],
        "grupo":g[3],
        "tipo":g[4],
        "alumnos":g[5]
        })

    handler.send_response(200)
    handler.send_header("Content-type","application/json")
    handler.end_headers()

    handler.wfile.write(json.dumps(lista).encode())
    
def agregar_grupo(handler):
    longitud = int(handler.headers['Content-Length'])
    datos = handler.rfile.read(longitud).decode()
    datos_json = json.loads(datos)
    programa = datos_json["programa"]
    semestre = datos_json["semestre"]
    grupo = datos_json["grupo"]
    tipo = datos_json["tipo"]
    alumnos = datos_json["alumnos"]

    conexion = sqlite3.connect(config.DB_PATH)

    cursor = conexion.cursor()

    try:

        cursor.execute("""
        INSERT INTO grupos
        (programa,semestre,grupo,tipo,alumnos)
        VALUES (?,?,?,?,?)
        """,(programa,semestre,grupo,tipo,alumnos))

        conexion.commit()

    except sqlite3.IntegrityError:

        handler.send_response(409)
        handler.end_headers()
        handler.wfile.write(b"El grupo ya existe")
        conexion.close()
        return

    conexion.close()

    handler.send_response(200)
    handler.end_headers()
    handler.wfile.write(b"Grupo agregado")


def eliminar_grupo(handler):

    longitud = int(handler.headers['Content-Length'])

    datos = handler.rfile.read(longitud).decode()

    datos_json = json.loads(datos)

    grupo_id = datos_json["id"]

    conexion = sqlite3.connect(config.DB_PATH)

    cursor = conexion.cursor()

    cursor.execute("DELETE FROM grupos WHERE id=?", (grupo_id,))

    conexion.commit()

    conexion.close()

    handler.send_response(200)
    handler.end_headers()
    handler.wfile.write(b"Grupo eliminado")
    
def importar_grupos(handler):

    form = cgi.FieldStorage(
        fp=handler.rfile,
        headers=handler.headers,
        environ={
            'REQUEST_METHOD':'POST',
            'CONTENT_TYPE':handler.headers['Content-Type']
        }
    )

    archivo=form['archivo']

    contenido=archivo.file.read()

    archivo_excel=io.BytesIO(contenido)

    wb=load_workbook(archivo_excel)

    hoja=wb.active

    conexion=sqlite3.connect(config.DB_PATH)
    cursor=conexion.cursor()

    agregados=0

    for fila in hoja.iter_rows(min_row=2,values_only=True):

        programa,semestre,grupo,tipo,alumnos=fila

        try:

            cursor.execute("""
            INSERT INTO grupos
            (programa,semestre,grupo,tipo,alumnos)
            VALUES (?,?,?,?,?)
            """,(programa,semestre,grupo,tipo,alumnos))

            agregados+=1

        except sqlite3.IntegrityError:
            pass

    conexion.commit()
    conexion.close()

    handler.send_response(200)
    handler.end_headers()

    handler.wfile.write(f"{agregados} grupos importados".encode())
    

def editar_grupo(handler):
    longitud = int(handler.headers['Content-Length'])
    datos = handler.rfile.read(longitud).decode()
    datos_json = json.loads(datos)

    grupo_id = datos_json["id"]
    programa = datos_json["programa"]
    semestre = datos_json["semestre"]
    grupo = datos_json["grupo"]
    tipo = datos_json["tipo"]
    alumnos = datos_json["alumnos"]

    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            UPDATE grupos
            SET programa=?, semestre=?, grupo=?, tipo=?, alumnos=?
            WHERE id=?
        """, (programa, semestre, grupo, tipo, alumnos, grupo_id))

        conexion.commit()
        respuesta = "Grupo actualizado"
    except sqlite3.IntegrityError:
        respuesta = "Error: el grupo ya existe"

    conexion.close()
    handler.send_response(200)
    handler.end_headers()
    handler.wfile.write(respuesta.encode())
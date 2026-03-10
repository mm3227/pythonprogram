import http.server
import socketserver
import socket
import sys
import urllib.parse
from crear_db import crear_base_datos
import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import json
import secrets

PUERTO = 8000
sesiones = {}


def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def verificar_usuario(usuario, password):

    hash_password = hashlib.sha256(password.encode()).hexdigest()

    conexion = sqlite3.connect("data/gestor.db")
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT tipo_usuario FROM usuarios WHERE usuario=? AND password=?",
        (usuario, hash_password)
    )

    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        return resultado[0]  # devuelve "admin" o "usuario"
    else:
        return None
    
def obtener_sesion(handler):
    cookie = handler.headers.get("Cookie")
    if not cookie:
        return None
    partes = cookie.split("=")
    if len(partes) < 2:
        return None
    token = partes[1]
    return sesiones.get(token)
    
class MiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):

        rol = obtener_sesion(self)

        # proteger paginas de admin
        if self.path.startswith("/admin"):

            if rol != "admin":

                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Acceso restringido")
                return

        # listar usuarios
        if self.path == "/listar_usuarios":

            conexion = sqlite3.connect("data/gestor.db")
            cursor = conexion.cursor()

            cursor.execute(
                "SELECT id, usuario, programa, tipo_usuario FROM usuarios"
            )

            filas = cursor.fetchall()
            conexion.close()

            datos = []

            for f in filas:
                datos.append({
                    "id": f[0],
                    "usuario": f[1],
                    "programa": f[2],
                    "tipo_usuario": f[3]
                })

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(datos).encode())

        else:

            super().do_GET()

    def do_POST(self):
        # -------------------------
        # LOGIN
        # -------------------------
        if self.path == "/login":

            longitud = int(self.headers['Content-Length'])
            datos = self.rfile.read(longitud).decode()

            campos = urllib.parse.parse_qs(datos)

            usuario = campos.get("usuario", [""])[0]
            password = campos.get("password", [""])[0]

            rol = verificar_usuario(usuario, password)

            if rol:

                token = secrets.token_hex(16)
                sesiones[token] = rol

                if rol == "admin":
                    destino = "/admin.html"
                else:
                    destino = "/users.html"

                self.send_response(302)

                self.send_header(
                    "Set-Cookie",
                    f"session={token}; HttpOnly"
                )

                self.send_header("Location", destino)
                self.end_headers()

            else:

                self.send_response(302)
                self.send_header("Location", "/index.html?error=1")
                self.end_headers()
        

        # -------------------------
        # AGREGAR USUARIO
        # -------------------------
        elif self.path == "/agregar_usuario":

            longitud = int(self.headers['Content-Length'])
            datos = self.rfile.read(longitud).decode()

            datos_json = json.loads(datos)

            usuario = datos_json["usuario"]
            programa = datos_json["programa"]
            password = datos_json["password"]

            # SOLO cifrar contraseña
            hash_password = hashlib.sha256(password.encode()).hexdigest()

            conexion = sqlite3.connect("data/gestor.db")
            cursor = conexion.cursor()

            try:

                cursor.execute("""
                INSERT INTO usuarios (usuario, programa, password)
                VALUES (?, ?, ?)
                """, (usuario, programa, hash_password))

                conexion.commit()

                respuesta = "Usuario agregado correctamente"

            except sqlite3.IntegrityError:

                respuesta = "El usuario ya existe"

            conexion.close()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(respuesta.encode())

        # -------------------------
        # IMPORTAR USUARIOS
        # -------------------------
        elif self.path == "/importar_usuarios":

            import cgi
            from openpyxl import load_workbook
            import io

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers['Content-Type']
                }
            )

            archivo = form['archivo']

            if not archivo.file:

                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No se recibio archivo")
                return

            contenido = archivo.file.read()

            archivo_excel = io.BytesIO(contenido)

            wb = load_workbook(archivo_excel)
            hoja = wb.active

            conexion = sqlite3.connect("data/gestor.db")
            cursor = conexion.cursor()

            agregados = 0

            for fila in hoja.iter_rows(min_row=2, values_only=True):

                usuario, programa, password = fila

                if not usuario:
                    continue

                hash_password = hashlib.sha256(str(password).encode()).hexdigest()

                try:

                    cursor.execute("""
                    INSERT INTO usuarios (usuario, programa, password, tipo_usuario)
                    VALUES (?, ?, ?, ?)
                    """, (usuario, programa, hash_password, "usuario"))

                    agregados += 1

                except sqlite3.IntegrityError:
                    pass

            conexion.commit()
            conexion.close()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"{agregados} usuarios importados".encode())
        # -------------------------
        # Reiniciar Contraseñas
        # -------------------------
        elif self.path == "/reset_password":

            longitud = int(self.headers['Content-Length'])
            datos = self.rfile.read(longitud).decode()

            datos_json = json.loads(datos)

            user_id = datos_json["id"]

            nueva_password = secrets.token_hex(4)

            hash_password = hashlib.sha256(nueva_password.encode()).hexdigest()

            conexion = sqlite3.connect("data/gestor.db")
            cursor = conexion.cursor()

            cursor.execute("""
            UPDATE usuarios
            SET password=?
            WHERE id=?
            """, (hash_password, user_id))

            conexion.commit()
            conexion.close()

            respuesta = {
                "password": nueva_password
            }

            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()

            self.wfile.write(json.dumps(respuesta).encode())
        
        # -------------------------
        # Eliminar usuario
        # -------------------------
        elif self.path == "/eliminar_usuario":

            longitud = int(self.headers['Content-Length'])
            datos = self.rfile.read(longitud).decode()

            datos_json = json.loads(datos)

            user_id = datos_json["id"]

            conexion = sqlite3.connect("data/gestor.db")
            cursor = conexion.cursor()

            # verificar tipo de usuario
            cursor.execute("SELECT tipo_usuario FROM usuarios WHERE id=?", (user_id,))
            tipo = cursor.fetchone()

            # si no existe el usuario
            if not tipo:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Usuario no encontrado")
                conexion.close()
                return

            # bloquear eliminación del admin
            if tipo[0] == "admin":

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"No se puede eliminar el administrador")
                conexion.close()
                return

            # eliminar usuario
            cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
            conexion.commit()
            conexion.close()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Usuario eliminado")
    
def mostrar_info(ip_local, puerto, admin_creado, password):
    root = tk.Tk()
    root.withdraw()
    mensaje = f"Servidor iniciado\n\n"
    mensaje += f"Local:\nhttp://localhost:{puerto}\n\n"
    mensaje += f"Red:\nhttp://{ip_local}:{puerto}\n"
    if admin_creado:
        mensaje += "\nADMIN CREADO\n"
        mensaje += "usuario: admin\n"
        mensaje += f"password: {password}\n"
        mensaje += "\nGuarda esta contraseña."
    messagebox.showinfo("Servidor Web", mensaje)
    root.destroy()


def main():
    admin_creado, password = crear_base_datos()

    ip_local = obtener_ip_local()

    mostrar_info(ip_local, PUERTO, admin_creado, password)

    handler = MiHandler
    httpd = socketserver.ThreadingTCPServer(("", PUERTO), handler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
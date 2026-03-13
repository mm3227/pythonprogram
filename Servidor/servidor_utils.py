import socket
import sqlite3
import hashlib
import config

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
    conexion = sqlite3.connect(config.DB_PATH)
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT tipo_usuario FROM usuarios WHERE usuario=? AND password=?",
        (usuario, hash_password)
    )

    resultado = cursor.fetchone()
    conexion.close()
    if resultado:
        return resultado[0]
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

    sesion = sesiones.get(token)

    if not sesion:
        return None

    return sesion["rol"]
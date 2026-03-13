import os
import sqlite3
import hashlib
import secrets

RUTA_DB = "data/gestor.db"


def hash_texto(texto):
    return hashlib.sha256(texto.encode()).hexdigest()


def crear_base_datos():

    if not os.path.exists("data"):
        os.makedirs("data")

    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()

    # -------------------------
    # TABLA USUARIOS
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        programa TEXT,
        password TEXT NOT NULL,
        tipo_usuario TEXT DEFAULT 'usuario'
    )
    """)

    # -------------------------
    # TABLA MATERIAS
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materias (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        programa TEXT,
        materia TEXT,
        continuidad TEXT,
        creditos INTEGER,
        UNIQUE(materia, programa)
    )
    """)

    # -------------------------
    # TABLA PROFESORES
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profesores (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        programa TEXT,
        nombre TEXT,
        contratacion TEXT,
        telefono TEXT,
        email TEXT,
        UNIQUE(nombre, programa)
    )
    """)

    # -------------------------
    # TABLA SALONES
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salones (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        programa TEXT,
        edificio TEXT,
        salon TEXT,
        capacidad INTEGER,
        UNIQUE(programa, edificio, salon)
    )
    """)
    
    # -------------------------
    # TABLA CICLOS
    # -------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cicloescolar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ciclo TEXT UNIQUE
    )
    """)
    
   
    # -------------------------
    # VERIFICAR ADMIN
    # -------------------------
    usuario_admin = "admin"

    cursor.execute("SELECT * FROM usuarios WHERE usuario=?", (usuario_admin,))
    admin = cursor.fetchone()
    admin_creado = False
    password_plano = None

    if not admin:

        admin_creado = True
        password_plano = secrets.token_hex(4)

        password_hash = hash_texto(password_plano)

        cursor.execute("""
        INSERT INTO usuarios (usuario, programa, password, tipo_usuario)
        VALUES (?, ?, ?, ?)
        """, (usuario_admin, "sistema", password_hash, "admin"))

    conexion.commit()
    conexion.close()

    return admin_creado, password_plano
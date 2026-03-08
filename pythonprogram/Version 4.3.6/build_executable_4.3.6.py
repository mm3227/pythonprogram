#!/usr/bin/env python3
"""
Constructor de ejecutable
GESTOR DE HORARIOS 4.3.6
Arquitectura modular con carpeta core/
"""

import os
import sys
import subprocess
import shutil
import platform


VERSION = "4.3.6"
NOMBRE_APP = "GestorHorarios4.3.6"


# =====================================================
# VERIFICACIÓN DE ARCHIVOS
# =====================================================

def verificar_archivos():
    print("\nVerificando estructura del proyecto...\n")

    archivos_necesarios = [
        "main.py",
        "config.py",
        "manage_ciclo_escolar.py",
        "manage_materias.py",
        "manage_profesores.py",
        "manage_programas.py",
        "manage_salones.py",
        "config_email.key",
        "config_email.enc",
        "core",              # carpeta
        "icono.ico",
        "logo.jpg"
    ]

    errores = []

    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            errores.append(f"✗ Faltante: {archivo}")
        else:
            print(f"✓ Encontrado: {archivo}")

    return errores


# =====================================================
# INSTALAR DEPENDENCIAS
# =====================================================

def instalar_dependencias():
    print("\nVerificando dependencias...\n")

    dependencias = [
        "cryptography",
        "reportlab",
        "pyinstaller"
    ]

    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✓ {dep} ya está instalado")
        except ImportError:
            print(f"Instalando {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

    return True


# =====================================================
# CREAR EJECUTABLE
# =====================================================

def crear_ejecutable():
    print("\nConstruyendo ejecutable...\n")
    
    # 🔥 LIMPIEZA PREVIA MANUAL
    for carpeta in ["build", "dist"]:
        if os.path.exists(carpeta):
            try:
                shutil.rmtree(carpeta)
                print(f"✓ Carpeta eliminada: {carpeta}")
            except Exception as e:
                print(f"No se pudo eliminar {carpeta}: {e}")
                return False

    sistema = platform.system()
    add_data_sep = ";" if sistema == "Windows" else ":"

    comando = [
        sys.executable,
        "-m",
        "PyInstaller",

        "--onefile",
        "--windowed",

        "--name", "GestorHorarios4.3.6",
        "--icon", "icono.ico",

        # Incluir recursos
        "--add-data", f"logo.jpg{add_data_sep}.",
        "--add-data", f"core{add_data_sep}core",

        # Incluir paquete completo core como código
        "--collect-all", "core",

        # Dependencias externas
        "--collect-all", "openpyxl",
        "--collect-all", "cryptography",
        "--collect-all", "reportlab",
        "--hidden-import", "reportlab.graphics",
        "--hidden-import", "reportlab.pdfgen",
        "--hidden-import", "reportlab.lib",
        "--hidden-import", "reportlab.platypus",
        "--hidden-import", "reportlab.lib.styles",
        "--hidden-import", "reportlab.lib.units",
        "--hidden-import", "reportlab.lib.colors",
        "main.py"
    ]

    print("Ejecutando:")
    print(" ".join(comando))
    print()

    try:
        subprocess.run(comando, check=True)
        print("\n✅ Ejecutable creado correctamente en carpeta dist/")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Error al crear el ejecutable")
        return False



# =====================================================
# OCULTAR ARCHIVO (multiplataforma)
# =====================================================
def ocultar_archivo(ruta):
    """
    Marca un archivo como oculto según el sistema operativo:
    - Windows: atributo +h
    - macOS:  chflags hidden (sin renombrar)
    - Linux:  no hace nada (podría renombrar con punto, pero se omite)
    """
    sistema = platform.system()
    if sistema == "Windows":
        try:
            subprocess.run(["attrib", "+h", ruta], check=True, capture_output=True)
            print(f"   Ocultado (Windows): {os.path.basename(ruta)}")
        except Exception as e:
            print(f"   No se pudo ocultar {ruta} en Windows: {e}")
    elif sistema == "Darwin":  # macOS
        try:
            subprocess.run(["chflags", "hidden", ruta], check=True, capture_output=True)
            print(f"   Ocultado (macOS): {os.path.basename(ruta)}")
        except Exception as e:
            print(f"   No se pudo ocultar {ruta} en macOS: {e}")
    else:
        # En Linux podrías renombrar a .archivo, pero afectaría la carga.
        # Por simplicidad, no hacemos nada.
        pass


# =====================================================
# CREAR PAQUETE PORTABLE
# =====================================================
def crear_portable():
    print("\nCreando versión portable...\n")

    sistema = platform.system()

    exe_nombre = f"{NOMBRE_APP}.exe" if sistema == "Windows" else NOMBRE_APP
    exe_origen = os.path.join("dist", exe_nombre)

    if not os.path.exists(exe_origen):
        print("❌ Primero debes construir el ejecutable (opción 2).")
        return

    carpeta_portable = f"{NOMBRE_APP}_Portable"

    if os.path.exists(carpeta_portable):
        shutil.rmtree(carpeta_portable)

    os.makedirs(carpeta_portable)

    # Copiar ejecutable
    shutil.copy2(exe_origen, carpeta_portable)
    print(f"✓ Copiado: {exe_nombre}")

    # Crear carpeta basedatos externa (vacía)
    basedatos_path = os.path.join(carpeta_portable, "basedatos")
    os.makedirs(basedatos_path, exist_ok=True)
    print("✓ Creada carpeta: basedatos/")

    # Copiar archivos de configuración
    for archivo in ["config_email.key", "config_email.enc"]:
        if os.path.exists(archivo):
            destino = os.path.join(carpeta_portable, archivo)
            shutil.copy2(archivo, destino)
            print(f"✓ Copiado: {archivo}")
            # Ocultar el archivo recién copiado
            ocultar_archivo(destino)
        else:
            print(f"⚠ Advertencia: {archivo} no encontrado, no se incluirá.")

    print("\n✅ Portable creado correctamente.")
    print(f"Carpeta: {carpeta_portable}/")
    print("Incluye:")
    print(f"- {exe_nombre}")
    print("- basedatos/ (vacía)")
    print("- config_email.key (oculto)")
    print("- config_email.enc (oculto)")


# =====================================================
# LIMPIAR
# =====================================================

def limpiar():
    print("\nLimpiando archivos temporales...\n")

    for carpeta in ["build", "dist", "__pycache__"]:
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
            print(f"✓ Eliminado: {carpeta}")

    for archivo in os.listdir():
        if archivo.endswith(".spec"):
            os.remove(archivo)
            print(f"✓ Eliminado: {archivo}")

    print("✓ Limpieza completada")


# =====================================================
# MENÚ PRINCIPAL
# =====================================================

def main():

    print("=" * 60)
    print(f"CONSTRUCTOR - GESTOR DE HORARIOS {VERSION}")
    print("=" * 60)

    while True:
        print("\n1. Verificar proyecto")
        print("2. Construir ejecutable")
        print("3. Crear versión portable")
        print("4. Limpiar temporales")
        print("5. Salir")

        opcion = input("\nSeleccione opción: ").strip()

        if opcion == "1":
            errores = verificar_archivos()
            instalar_dependencias()

            if errores:
                print("\n⚠ Errores encontrados:")
                for e in errores:
                    print(e)
            else:
                print("\n✅ Proyecto listo para compilar.")

        elif opcion == "2":
            crear_ejecutable()

        elif opcion == "3":
            crear_portable()

        elif opcion == "4":
            limpiar()

        elif opcion == "5":
            break

        else:
            print("Opción inválida")


if __name__ == "__main__":
    main()
import os
import sys

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

BASE_DIR = get_base_dir()

RUTA_BASEDATOS = os.path.join(BASE_DIR, "basedatos")
RUTA_CICLOS = os.path.join(RUTA_BASEDATOS, "ciclos")
RUTA_HORARIOS = os.path.join(RUTA_BASEDATOS, "horarios")
KEY_PATH = os.path.join(BASE_DIR, "config_email.key")
ENC_PATH = os.path.join(BASE_DIR, "config_email.enc")

os.makedirs(RUTA_BASEDATOS, exist_ok=True)
os.makedirs(RUTA_CICLOS, exist_ok=True)
os.makedirs(RUTA_HORARIOS, exist_ok=True)

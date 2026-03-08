#core/control/funciones/guardar_horarios.py
import sqlite3
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from config import RUTA_BASEDATOS


def guardar_horarios(win):

    if not hasattr(win, "_filas_por_programa"):
        messagebox.showerror("Error", "No hay datos para guardar.")
        return

    filas_por_programa = win._filas_por_programa
    db_ciclo_path = win._db_ciclo_path

    # ===============================
    # Obtener nombre del ciclo
    # ===============================
    nombre_ciclo = os.path.splitext(os.path.basename(db_ciclo_path))[0]

    # ===============================
    # Ruta de guardado
    # ===============================
   
    carpeta_horarios = os.path.join(RUTA_BASEDATOS, "horarios")
    
    os.makedirs(carpeta_horarios, exist_ok=True)

    ruta_db = os.path.join(carpeta_horarios, f"{nombre_ciclo}_horario.db")

    # ===============================
    # Crear / Sobrescribir base
    # ===============================
    con = sqlite3.connect(ruta_db)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS horarios")

    cur.execute("""
        CREATE TABLE horarios (
            programa TEXT,
            grupo TEXT,
            modalidad TEXT,
            materia TEXT,
            salon TEXT,
            profesor TEXT,
            L TEXT,
            M TEXT,
            X TEXT,
            J TEXT,
            V TEXT,
            S TEXT,
            horas TEXT
        )
    """)

    # ===============================
    # Insertar TODAS las filas
    # ===============================
    for programa, filas in filas_por_programa.items():
        for fila in filas:

            programa_txt = fila[0].cget("text")
            grupo_txt = fila[1].cget("text")
            modalidad_txt = fila[2].cget("text")

            materia = fila[3].get()
            salon = fila[4].get()
            profesor = fila[5].get()

            dias = [fila[i].get() for i in range(6, 12)]
            horas = fila[12].get()

            cur.execute("""
                INSERT INTO horarios
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                programa_txt,
                grupo_txt,
                modalidad_txt,
                materia,
                salon,
                profesor,
                *dias,
                horas
            ))

    con.commit()
    con.close()

    mostrar_mensaje_guardado(win, ruta_db)


# ==================================================
# MENSAJE SOBRE PUESTO (NO MINIMIZA)
# ==================================================
def mostrar_mensaje_guardado(parent, ruta):

    popup = tk.Toplevel(parent)
    popup.title("Guardado exitoso")
    popup.transient(parent)
    popup.grab_set()
    popup.resizable(False, False)
    popup.configure(bg="#f2f4f8")

    frame = tk.Frame(popup, bg="#f2f4f8", padx=25, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="✅ Horario guardado correctamente",
        font=("Segoe UI", 12, "bold"),
        bg="#f2f4f8"
    ).pack(pady=(0, 12))

    tk.Label(
        frame,
        text="Guardado en:",
        font=("Segoe UI", 10, "bold"),
        bg="#f2f4f8"
    ).pack(anchor="w")

    tk.Label(
        frame,
        text=ruta,
        bg="#f2f4f8",
        fg="#444",
        wraplength=480,
        justify="left"
    ).pack(anchor="w", pady=(0, 15))

    ttk.Button(
        frame,
        text="Aceptar",
        command=popup.destroy
    ).pack()

    # 🔹 Ajustar tamaño automáticamente
    popup.update_idletasks()

    width = popup.winfo_width()
    height = popup.winfo_height()

    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)

    popup.geometry(f"{width}x{height}+{x}+{y}")


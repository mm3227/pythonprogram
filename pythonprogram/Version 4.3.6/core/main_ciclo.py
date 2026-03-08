# core/main_ciclo.py
import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from config import RUTA_BASEDATOS
# ==============================
# IMPORTS
# ==============================
from core.pestaña_grupos import cargar_pestana_grupos
from core.pestaña_horarios_grupos import cargar_pestana_horarios_grupos
from core.pestaña_profesores import cargar_pestana_profesores

# ==============================
# RUTAS
# ==============================

DB_PROGRAMAS = os.path.join(RUTA_BASEDATOS, "programas.db")

# ==============================
# CARGAR PROGRAMAS ACTIVOS
# ==============================
def obtener_programas_activos():
    if not os.path.exists(DB_PROGRAMAS):
        return []

    conn = sqlite3.connect(DB_PROGRAMAS)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT nombre
            FROM programas
            WHERE activo = 1
            ORDER BY nombre
        """)
        programas = [r[0] for r in c.fetchall()]
    except sqlite3.Error:
        programas = []

    conn.close()
    return programas

# ==============================
# LIMPIAR PESTAÑAS
# ==============================
def limpiar_pestana(frame):
    for w in frame.winfo_children():
        w.destroy()

# ==============================
# VENTANA PRINCIPAL DEL CICLO
# ==============================
def abrir_main_ciclo(ruta_db_ciclo):
    nombre_ciclo = os.path.basename(ruta_db_ciclo)

    root = tk.Toplevel()
    root.title(f"Ciclo escolar: {nombre_ciclo}")
    root.geometry("1200x750")
    root.configure(bg="#f2f4f8")

    # ==============================
    # HEADER
    # ==============================
    header = tk.Frame(root, bg="#4a6fa5", height=60)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text=f"Ciclo escolar: {nombre_ciclo}",
        fg="white",
        bg="#4a6fa5",
        font=("Segoe UI", 18, "bold")
    ).pack(side="left", padx=20)

    tk.Button(
        header,
        text="🔙",
        bg="#607D8B",
        fg="white",
        font=("Segoe UI", 12),
        width=4,
        command=root.destroy
    ).pack(side="right", padx=20)

    # ==============================
    # SELECTOR DE PROGRAMA
    # ==============================
    top = tk.Frame(root, bg="#f2f4f8", pady=10)
    top.pack(fill="x")

    tk.Label(
        top,
        text="Programa académico:",
        bg="#f2f4f8",
        font=("Segoe UI", 12)
    ).pack(side="left", padx=(20, 8))

    programa_actual = tk.StringVar()

    cmb_programas = ttk.Combobox(
        top,
        textvariable=programa_actual,
        state="readonly",
        width=40
    )
    cmb_programas.pack(side="left")

    programas = obtener_programas_activos()
    cmb_programas["values"] = programas

    if programas:
        programa_actual.set(programas[0])

    # ==============================
    # PESTAÑAS
    # ==============================
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    tab_grupos = tk.Frame(notebook, bg="#f2f4f8")
    tab_hor_grupos = tk.Frame(notebook, bg="#f2f4f8")
    tab_hor_prof = tk.Frame(notebook, bg="#f2f4f8")


    notebook.add(tab_grupos, text="📚 Grupos")
    notebook.add(tab_hor_grupos, text="🕒 Horarios Grupos")
    notebook.add(tab_hor_prof, text="👨‍🏫 Horarios Profesores")

    # ==============================
    # CONTEXTO POR PROGRAMA
    # ==============================
    def actualizar_contexto(event=None):
        prog = programa_actual.get()
        if not prog:
            return

        limpiar_pestana(tab_grupos)
        cargar_pestana_grupos(tab_grupos, ruta_db_ciclo, prog)

        limpiar_pestana(tab_hor_grupos)
        cargar_pestana_horarios_grupos(tab_hor_grupos, ruta_db_ciclo, prog)

        limpiar_pestana(tab_hor_prof)
        cargar_pestana_profesores(tab_hor_prof, ruta_db_ciclo, prog)
    
    cmb_programas.bind("<<ComboboxSelected>>", actualizar_contexto)
    actualizar_contexto()

# ==============================
# FUNCIÓN PÚBLICA (PUENTE)
# ==============================
def abrir_ciclo(ruta_db_ciclo):
    abrir_main_ciclo(ruta_db_ciclo)

#core/control/funciones/cargarhorarios.py
import sqlite3
import os
import tkinter as tk
from tkinter import filedialog, messagebox


def cargar_horarios(win):

    if not hasattr(win, "_filas_por_programa"):
        messagebox.showerror("Error", "No hay tabla cargada.")
        return

    # ===============================
    # Seleccionar archivo
    # ===============================
    ruta_db = filedialog.askopenfilename(
        title="Seleccionar archivo de horario",
        filetypes=[("Base de datos SQLite", "*.db")],
    )

    if not ruta_db:
        return

    # ===============================
    # Leer base
    # ===============================
    try:
        con = sqlite3.connect(ruta_db)
        cur = con.cursor()
        cur.execute("SELECT * FROM horarios")
        datos = cur.fetchall()
        con.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")
        return

    # ===============================
    # Obtener todas las filas actuales (incluidas ocultas)
    # ===============================
    filas_por_programa = win._filas_por_programa

    todas_filas = []
    for programa, filas in filas_por_programa.items():
        for fila in filas:
            todas_filas.append(fila)

    # Validación básica
    if len(datos) != len(todas_filas):
        messagebox.showwarning(
            "Advertencia",
            "La cantidad de filas no coincide con la estructura actual.\n"
            "Se cargará hasta donde sea posible."
        )

    # ===============================
    # Cargar datos en la tabla
    # ===============================
    for i, registro in enumerate(datos):
        if i >= len(todas_filas):
            break

        fila = todas_filas[i]

        # registro:
        # 0 programa
        # 1 grupo
        # 2 modalidad
        # 3 materia
        # 4 salon
        # 5 profesor
        # 6-11 dias
        # 12 horas

        # Materia
        fila[3].delete(0, "end")
        fila[3].insert(0, registro[3] or "")

        # Salon
        fila[4].delete(0, "end")
        fila[4].insert(0, registro[4] or "")

        # Profesor
        fila[5].delete(0, "end")
        fila[5].insert(0, registro[5] or "")

        # Días
        for d in range(6, 12):
            fila[d].delete(0, "end")
            fila[d].insert(0, registro[d] or "")

        # Horas (readonly)
        fila[12].configure(state="normal")
        fila[12].delete(0, "end")
        fila[12].insert(0, registro[12] or "")
        fila[12].configure(state="readonly")

    mostrar_mensaje_cargado(win, ruta_db)


# =====================================================
# Popup elegante
# =====================================================
def mostrar_mensaje_cargado(parent, ruta):

    popup = tk.Toplevel(parent)
    popup.title("Carga exitosa")
    popup.transient(parent)
    popup.resizable(False, False)
    popup.configure(bg="#f2f4f8")

    # Forzar que esté encima sin minimizar la ventana principal
    popup.lift()
    popup.focus_force()
    popup.attributes("-topmost", True)

    frame = tk.Frame(popup, bg="#f2f4f8", padx=25, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="📂 Horario cargado correctamente",
        font=("Segoe UI", 12, "bold"),
        bg="#f2f4f8"
    ).pack(pady=(0, 12))

    tk.Label(
        frame,
        text="Archivo:",
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

    tk.Button(frame, text="Aceptar", command=popup.destroy).pack()

    popup.update_idletasks()

    width = popup.winfo_width()
    height = popup.winfo_height()

    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)

    popup.geometry(f"{width}x{height}+{x}+{y}")

    # Quitar topmost después de mostrar
    popup.after(100, lambda: popup.attributes("-topmost", False))


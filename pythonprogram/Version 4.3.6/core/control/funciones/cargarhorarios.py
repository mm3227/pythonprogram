#core/control/funciones/cargarhorarios.py
import sqlite3
import os
import tkinter as tk
from tkinter import ttk,filedialog, messagebox


def cargar_horarios(win):

    if not hasattr(win, "_filas_por_programa"):
        messagebox.showerror("Error", "No hay tabla cargada.")
        return

    programa_actual = getattr(win, "_programa_actual", None)

    ruta_db = filedialog.askopenfilename(
        title="Seleccionar archivo de horario",
        filetypes=[("Base de datos SQLite", "*.db")],
    )

    if not ruta_db:
        return

    try:
        con = sqlite3.connect(ruta_db)
        cur = con.cursor()
        cur.execute("""
            SELECT programa, grupo, modalidad,
                   materia, salon, profesor,
                   L, M, X, J, V, S, horas
            FROM horarios
        """)
        datos = cur.fetchall()
        con.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")
        return

    # ===============================
    # Agrupar datos del archivo
    # ===============================
    datos_archivo = {}

    for registro in datos:
        prog, grupo, modalidad = registro[0], registro[1], registro[2]

        if prog != programa_actual:
            continue

        clave = (grupo, modalidad)
        datos_archivo.setdefault(clave, []).append(registro)

    filas_por_programa = win._filas_por_programa
    filas_actuales = filas_por_programa.get(programa_actual, [])

    estructura_actual = {}

    for fila in filas_actuales:
        grupo = fila[1].cget("text")
        modalidad = fila[2].cget("text")
        estructura_actual.setdefault((grupo, modalidad), []).append(fila)

    frame = filas_actuales[0][0].master if filas_actuales else None
    siguiente_row = max(
        [w.grid_info()["row"] for fila in filas_actuales for w in fila if "row" in w.grid_info()],
        default=0
    ) + 1

    grupos_faltantes = []

    # ===============================
    # Cargar datos
    # ===============================
    for clave, registros_grupo in datos_archivo.items():

        if clave not in estructura_actual:

            grupos_faltantes.append(clave)

            estructura_actual[clave] = []

            for registro in registros_grupo:

                fila_widgets = []

                # Labels fijos
                lbl_prog = tk.Label(frame, text=programa_actual)
                lbl_grupo = tk.Label(frame, text=clave[0])
                lbl_mod = tk.Label(frame, text=clave[1])

                lbl_prog.grid(row=siguiente_row, column=0)
                lbl_grupo.grid(row=siguiente_row, column=1)
                lbl_mod.grid(row=siguiente_row, column=2)

                fila_widgets.extend([lbl_prog, lbl_grupo, lbl_mod])

                # Entradas editables
                for col in range(3, 13):
                    e = ttk.Entry(frame)

                    if col == 12:
                        e.configure(state="readonly")

                    e.grid(row=siguiente_row, column=col, padx=1, pady=1)
                    fila_widgets.append(e)

                filas_por_programa[programa_actual].append(fila_widgets)
                estructura_actual[clave].append(fila_widgets)

                siguiente_row += 1

        filas_grupo = estructura_actual[clave]

        for i, registro in enumerate(registros_grupo):

            fila = filas_grupo[i]

            fila[3].delete(0, "end")
            fila[3].insert(0, registro[3] or "")

            fila[4].delete(0, "end")
            fila[4].insert(0, registro[4] or "")

            fila[5].delete(0, "end")
            fila[5].insert(0, registro[5] or "")

            for d in range(6, 12):
                fila[d].delete(0, "end")
                fila[d].insert(0, registro[d] or "")

            fila[12].configure(state="normal")
            fila[12].delete(0, "end")
            fila[12].insert(0, registro[12] or "")
            fila[12].configure(state="readonly")

    if grupos_faltantes:

        mensaje = "Se cargaron grupos que no existen en la pestaña 'Grupos':\n\n"

        for g, m in grupos_faltantes:
            mensaje += f"- {g} ({m})\n"

        mensaje += "\nDebe registrarlos oficialmente en la pestaña Grupos, para poderlos editar\nPuede Seguir trabajando así de momento."

        messagebox.showwarning("Grupos no registrados", mensaje)

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


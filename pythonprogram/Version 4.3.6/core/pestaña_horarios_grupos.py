#core/pestaña_horarios_grupos.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from config import RUTA_HORARIOS

# ================================
# IMPORTS CONTROL
# ================================
from core.control.horarios_editor import abrir_editor_horarios
from core.control.exportar_resumen import (
    exportar_excel_resumen,
    exportar_pdf_resumen
)


def obtener_ruta_horario(db_path):
    nombre_ciclo = os.path.splitext(os.path.basename(db_path))[0]

    ruta_horario = os.path.join(
        RUTA_HORARIOS,
        f"{nombre_ciclo}_horario.db"
    )

    os.makedirs(RUTA_HORARIOS, exist_ok=True)

    return ruta_horario


def asegurar_base_horarios(ruta_horarios):
    conn = sqlite3.connect(ruta_horarios)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programa TEXT,
            grupo TEXT,
            modalidad TEXT,
            materia TEXT,
            profesor TEXT,
            salon TEXT,
            L TEXT,
            M TEXT,
            X TEXT,
            J TEXT,
            V TEXT,
            S TEXT,
            horas INTEGER
        )
    """)

    conn.commit()
    conn.close()

# ================================
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]

# ==================================================
# BOTÓN CANVAS CON TOOLTIP
# ==================================================
class CanvasButton(tk.Canvas):
    def __init__(self, parent, emoji, tooltip, color, command=None):
        super().__init__(
            parent,
            width=60,
            height=60,
            bg=parent.cget("bg"),
            highlightthickness=0,
            cursor="hand2"
        )

        self.command = command
        self.tooltip_text = tooltip
        self.tooltip = None

        self._rounded_rect(5, 5, 55, 55, 12, fill=color, outline="")
        self.create_text(30, 30, text=emoji, font=("Segoe UI", 22))

        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", self._show_tooltip)
        self.bind("<Leave>", self._hide_tooltip)

    def _click(self, event):
        if self.command:
            self.command()

    def _show_tooltip(self, event=None):
        if self.tooltip:
            return
        self.tooltip = tk.Toplevel(self)
        self.tooltip.overrideredirect(True)
        self.tooltip.configure(bg="#333")

        tk.Label(
            self.tooltip,
            text=self.tooltip_text,
            bg="#333",
            fg="white",
            font=("Segoe UI", 10),
            padx=8,
            pady=4
        ).pack()

        x = self.winfo_rootx() + 10
        y = self.winfo_rooty() + 65
        self.tooltip.geometry(f"+{x}+{y}")

    def _hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        points = [
            x1+r, y1, x2-r, y1,
            x2, y1, x2, y1+r,
            x2, y2-r, x2, y2,
            x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r,
            x1, y1+r, x1, y1
        ]
        self.create_polygon(points, smooth=True, **kw)


# ==================================================
# MODAL SIMPLE
# ==================================================
def mostrar_aviso_modal(titulo, mensaje):
    ventana = tk.Toplevel()
    ventana.title(titulo)
    ventana.geometry("400x150")
    ventana.resizable(False, False)
    ventana.grab_set()
    ventana.transient()
    ventana.configure(bg="#f2f4f8")

    tk.Label(
        ventana,
        text=mensaje,
        bg="#f2f4f8",
        font=("Segoe UI", 11),
        wraplength=350
    ).pack(pady=25)

    tk.Button(
        ventana,
        text="Aceptar",
        relief="flat",
        width=12,
        command=ventana.destroy
    ).pack()

    ventana.wait_window()


# ==================================================
# PESTAÑA HORARIOS POR GRUPO
# ==================================================
def cargar_pestana_horarios_grupos(frame, db_path, programa):

    for w in frame.winfo_children():
        w.destroy()

    root = tk.Frame(frame, bg="#f2f4f8")
    root.pack(fill="both", expand=True)

    top = tk.Frame(root, bg="#f2f4f8")
    top.pack(fill="x", padx=15, pady=10)

    tk.Label(
        top,
        text=f"Horarios por grupo – {programa}",
        font=("Segoe UI", 16, "bold"),
        bg="#f2f4f8"
    ).pack(side="left")

    botones = tk.Frame(top, bg="#f2f4f8")
    botones.pack(side="right")

    # ================= SCROLL =================
    canvas = tk.Canvas(root, bg="#f2f4f8", highlightthickness=0)
    scroll_y = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_x = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)

    canvas.configure(
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )

    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    interior = tk.Frame(canvas, bg="#f2f4f8")
    window_id = canvas.create_window((0, 0), window=interior, anchor="nw")

    def actualizar_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(window_id,
                          width=max(canvas.winfo_width(), interior.winfo_reqwidth()))

    interior.bind("<Configure>", actualizar_scroll)
    canvas.bind("<Configure>", actualizar_scroll)

    # ================= VARIABLES COMPARTIDAS =================
    treeviews = []
    info_grupos = []

    # ==================================================
    # CONSTRUIR TABLAS (BOTÓN ACTUALIZAR)
    # ==================================================
    def construir_tablas():

        treeviews.clear()
        info_grupos.clear()

        for widget in interior.winfo_children():
            widget.destroy()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("""
            SELECT semestre, grupo, modalidad, materias
            FROM grupos
            WHERE programa = ?
            ORDER BY semestre, grupo
        """, (programa,))

        grupos = c.fetchall()

        if not grupos:
            conn.close()
            mostrar_aviso_modal("Información", "No hay grupos registrados.")
            return

        for semestre, grupo, modalidad, total_materias in grupos:

            nombre_grupo = f"{semestre}° {grupo}"

            tk.Label(
                interior,
                text=f"Grupo: {nombre_grupo}   |   Modalidad: {modalidad}",
                font=("Segoe UI", 14, "bold"),
                bg="#f2f4f8"
            ).pack(anchor="w", padx=12, pady=(20, 6))

            columnas = (
                "materia", "profesor", "salon",
                *DIAS_SEMANA, "horas"
            )

            tree = ttk.Treeview(
                interior,
                columns=columnas,
                show="headings",
                height=total_materias if total_materias > 0 else 1
            )

            for col in columnas:
                tree.heading(col, text=col.capitalize())
                tree.column(col, width=110, anchor="center")

            tree.pack(fill="x", padx=12)

            treeviews.append(tree)

            info_grupos.append((semestre, grupo, modalidad))

        conn.close()

        interior.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        mostrar_aviso_modal("Actualización", "Estructura actualizada correctamente.")

    # ==================================================
    # CARGAR DATOS (BOTÓN CARGAR)
    # ==================================================
    def cargar_datos():
        ruta_horarios = obtener_ruta_horario(db_path)

        asegurar_base_horarios(ruta_horarios)

        conn = sqlite3.connect(ruta_horarios)
        c = conn.cursor()

        c.execute("""
            SELECT grupo, modalidad, materia, profesor, salon,
                   L, M, X, J, V, S, horas
            FROM horarios
            WHERE programa = ?
            ORDER BY grupo
        """, (programa,))

        registros = c.fetchall()
        conn.close()

        if not registros:
            messagebox.showinfo("Información", "No hay registros guardados.")
            return

        datos_por_grupo = {}

        for fila in registros:
            grupo = fila[0]
            modalidad = fila[1]
            resto = fila[2:]
            datos_por_grupo.setdefault((grupo, modalidad), []).append(resto)

        for widget in interior.winfo_children():
            widget.destroy()

        for (grupo, modalidad), filas in datos_por_grupo.items():

            tk.Label(
                interior,
                text=f"Grupo: {grupo}   |   Modalidad: {modalidad}",
                font=("Segoe UI", 14, "bold"),
                bg="#f2f4f8"
            ).pack(anchor="w", padx=12, pady=(20, 6))

            columnas = (
                "materia", "profesor", "salon",
                *DIAS_SEMANA, "horas"
            )

            tree = ttk.Treeview(
                interior,
                columns=columnas,
                show="headings",
                height=len(filas)
            )

            for col in columnas:
                tree.heading(col, text=col.capitalize())
                tree.column(col, width=110, anchor="center")

            tree.pack(fill="x", padx=12)

            for fila in filas:
                tree.insert("", "end", values=fila)

        mostrar_aviso_modal("Carga completa", "Horarios cargados correctamente.")

        conn = sqlite3.connect(ruta_horarios)
        c = conn.cursor()

        c.execute("""
            SELECT grupo, modalidad, materia, profesor, salon,
                   L, M, X, J, V, S, horas
            FROM horarios
            WHERE programa = ?
            ORDER BY grupo
        """, (programa,))

        registros = c.fetchall()
        conn.close()

        if not registros:
            messagebox.showinfo("Información", "No hay registros guardados.")
            return

        # Agrupar por grupo
        datos_por_grupo = {}

        for fila in registros:
            grupo = fila[0]
            modalidad = fila[1]
            resto = fila[2:]
            datos_por_grupo.setdefault((grupo, modalidad), []).append(resto)

        # Limpiar vista
        for widget in interior.winfo_children():
            widget.destroy()

        # Reconstruir dinámicamente
        for (grupo, modalidad), filas in datos_por_grupo.items():

            tk.Label(
                interior,
                text=f"Grupo: {grupo}   |   Modalidad: {modalidad}",
                font=("Segoe UI", 14, "bold"),
                bg="#f2f4f8"
            ).pack(anchor="w", padx=12, pady=(20, 6))

            columnas = (
                "materia", "profesor", "salon",
                *DIAS_SEMANA, "horas"
            )

            tree = ttk.Treeview(
                interior,
                columns=columnas,
                show="headings",
                height=len(filas)
            )

            tree.heading("materia", text="Materia")
            tree.column("materia", width=250)

            tree.heading("profesor", text="Profesor")
            tree.column("profesor", width=200)

            tree.heading("salon", text="Salón")
            tree.column("salon", width=120)

            for dia in DIAS_SEMANA:
                tree.heading(dia, text=dia)
                tree.column(dia, width=90)

            tree.heading("horas", text="Horas")
            tree.column("horas", width=80)

            tree.pack(fill="x", padx=12)

            for fila in filas:
                tree.insert("", "end", values=fila)

        mostrar_aviso_modal("Carga completa", "Horarios cargados correctamente.")

    def obtener_datos_para_exportar():

        datos_por_grupo = {}

        widgets = interior.winfo_children()

        i = 0
        while i < len(widgets):

            widget = widgets[i]

            if isinstance(widget, tk.Label) and "Grupo:" in widget.cget("text"):

                titulo = widget.cget("text")

                if i + 1 < len(widgets) and isinstance(widgets[i+1], ttk.Treeview):

                    tree = widgets[i+1]

                    filas = []

                    for item in tree.get_children():
                        valores = tree.item(item)["values"]
                        filas.append(valores)

                    if filas:
                        partes = titulo.replace("Grupo:", "").split("|")
                        nombre_grupo = partes[0].strip()
                        modalidad = partes[1].replace("Modalidad:", "").strip()
                        datos_por_grupo[(nombre_grupo, modalidad)] = filas

            i += 1

        return datos_por_grupo

    # ================= BOTONES (todos con tooltips) =================
    CanvasButton(botones, "✏", "Editar horarios", "#FFE082",
                 command=lambda: abrir_editor_horarios(programa, db_path)).pack(side="left", padx=6)

    CanvasButton(botones, "🔄", "Actualizar estructura", "#BBDEFB",
                 command=construir_tablas).pack(side="left", padx=6)

    CanvasButton(botones, "📂", "Cargar datos", "#B2DFDB",
                 command=cargar_datos).pack(side="left", padx=6)

    CanvasButton(
        botones,
        "📄",
        "Exportar PDF",
        "#F8BBD0",
        command=lambda: exportar_pdf_resumen(
            programa,
            os.path.splitext(os.path.basename(db_path))[0],
            db_path,
            obtener_datos_para_exportar()
        )
    ).pack(side="left", padx=6)

    CanvasButton(
        botones,
        "📊",
        "Exportar Excel",
        "#C8E6C9",
        command=lambda: exportar_excel_resumen(
            programa,
            os.path.splitext(os.path.basename(db_path))[0],
            db_path,
            obtener_datos_para_exportar()
        )
    ).pack(side="left", padx=6)

#core/control/horarios_editor.py
import tkinter as tk
from tkinter import ttk
import sqlite3
import os

from core.control.asignador_horarios import abrir_asignador_horarios
from core.control.funciones.guardar_horarios import guardar_horarios
from core.control.funciones.exportar_horarios import exportar_pdf, exportar_excel
from core.control.funciones.cargarhorarios import cargar_horarios

# ==================================================
# BOTÓN EMOJI CON TOOLTIP
# ==================================================
class EmojiButton(tk.Canvas):
    def __init__(self, parent, emoji, texto, color, command=None):
        super().__init__(
            parent,
            width=55,
            height=55,
            bg=parent.cget("bg"),
            highlightthickness=0,
            cursor="hand2"
        )

        self.command = command
        self.tooltip_text = texto
        self.tooltip = None

        self._rounded_rect(5, 5, 50, 50, 12, fill=color, outline="")
        self.create_text(27, 27, text=emoji, font=("Segoe UI", 22))

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
        y = self.winfo_rooty() + 60
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
# CONFIGURACIÓN
# ==================================================
COL_WIDTHS = [12, 10, 14, 18, 18, 18, 10, 10, 10, 10, 10, 10, 8]
HEADERS = [
    "Programa", "Grupo", "Modalidad",
    "Materia", "Salón", "Profesor",
    "L", "M", "X", "J", "V", "S", "Horas"
]


# ==================================================
# EDITOR DE HORARIOS
# ==================================================
def abrir_editor_horarios(programa, db_ciclo_path):

    win = tk.Toplevel()
    win.title(f"Editor de horarios – {programa}")
    win.geometry("1400x700")
    win.configure(bg="#f2f4f8")
   
    # ==================================================
    # BARRA SUPERIOR
    # ==================================================
    barra = tk.Frame(win, bg="#f2f4f8")
    barra.pack(fill="x", padx=15, pady=10)

    tk.Label(
        barra,
        text=f"Editor de horarios – {programa}",
        font=("Segoe UI", 16, "bold"),
        bg="#f2f4f8"
    ).pack(side="left")

    acciones = tk.Frame(barra, bg="#f2f4f8")
    acciones.pack(side="right")

    # Botones emoji
    EmojiButton(
        acciones,
        "💾",
        "Guardar horarios",
        "#A5D6A7",
        command=lambda: guardar_horarios(win)
    ).pack(side="left", padx=6)
    
    EmojiButton(
        acciones,
        "📂",
        "Cargar horarios",
        "#FFE082",
        command=lambda: cargar_horarios(win)
    ).pack(side="left", padx=6)


    EmojiButton(
        acciones,
        "📄",
        "Exportar a PDF",
        "#FFCCBC",
        command=lambda: exportar_pdf(win)
    ).pack(side="left", padx=6)

    EmojiButton(
        acciones,
        "📊",
        "Exportar a Excel",
        "#C5E1A5",
        command=lambda: exportar_excel(win)
    ).pack(side="left", padx=6)
    
    EmojiButton(
        acciones,
        "❌",
        "Cerrar editor",
        "#EF9A9A",
        command=lambda: confirmar_cierre(win)
    ).pack(side="left", padx=6)
    
    # ==================================================
    # OBTENER GRUPOS
    # ==================================================
    con = sqlite3.connect(db_ciclo_path)
    cur = con.cursor()
    cur.execute("""
        SELECT programa, semestre, grupo, materias, modalidad, alumnos
        FROM grupos
        ORDER BY programa, semestre, grupo
    """)
    grupos = cur.fetchall()
    con.close()

    # ==================================================
    # CANVAS CON SCROLL VERTICAL Y HORIZONTAL
    # ==================================================
    contenedor = tk.Frame(win, bg="#f2f4f8")
    contenedor.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        contenedor,
        bg="#f2f4f8",
        highlightthickness=0
    )
    canvas.pack(side="left", fill="both", expand=True)

    scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
    scroll_y.pack(side="right", fill="y")

    scroll_x = ttk.Scrollbar(win, orient="horizontal", command=canvas.xview)
    scroll_x.pack(fill="x")

    canvas.configure(
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )

    frame = tk.Frame(canvas, bg="#f2f4f8")

    # ⚠️ IMPORTANTE: guardar referencia del window interno
    canvas_window = canvas.create_window((0, 0), window=frame, anchor="nw")

    def on_configure(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_mousewheel(event):
        if canvas.winfo_exists():
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")

    def _on_shift_mousewheel(event):
        if canvas.winfo_exists():
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            
    def _on_button4(event):
        if canvas.winfo_exists():
            canvas.yview_scroll(-1, "units")

    def _on_button5(event):
        if canvas.winfo_exists():
            canvas.yview_scroll(1, "units")

    """
    canvas.bind("<MouseWheel>", _on_mousewheel)
    canvas.bind("<Shift-MouseWheel>", _on_shift_mousewheel)}
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
    canvas.bind_all("<Button-4>", _on_button4)
    canvas.bind_all("<Button-5>", _on_button5)
    """
    def activar_scroll():
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
        canvas.bind_all("<Button-4>", _on_button4)
        canvas.bind_all("<Button-5>", _on_button5)

    def desactivar_scroll():
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Shift-MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
    
    activar_scroll()
   
    """
    def cerrar_ventana():
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Shift-MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
        win.destroy()
    """
   
    # ==================================================
    # CABECERAS
    # ==================================================
    for c, h in enumerate(HEADERS):
        tk.Label(
            frame,
            text=h,
            width=COL_WIDTHS[c],
            bg="#dde3ec",
            font=("Segoe UI", 10, "bold"),
            anchor="center"
        ).grid(row=0, column=c, padx=1, pady=1)

    # ==================================================
    # FILAS
    # ==================================================
    filas_por_programa = {}
    row = 1

    for prog, semestre, grupo, num_materias, modalidad, alumnos in grupos:
        grupo_txt = f"{semestre}°{grupo}"
        modalidad = modalidad or "Escolarizada"

        filas_por_programa.setdefault(prog, [])

        for _ in range(num_materias):
            fila_widgets = []

            # Columnas fijas
            lbl_prog = tk.Label(frame, text=prog, width=COL_WIDTHS[0])
            lbl_grupo = tk.Label(frame, text=grupo_txt, width=COL_WIDTHS[1])
            lbl_mod = tk.Label(frame, text=modalidad, width=COL_WIDTHS[2])

            lbl_prog.grid(row=row, column=0)
            lbl_grupo.grid(row=row, column=1)
            lbl_mod.grid(row=row, column=2)

            fila_widgets.extend([lbl_prog, lbl_grupo, lbl_mod])

            # Columnas editables
            for col in range(3, len(HEADERS)):
                e = ttk.Entry(frame, width=COL_WIDTHS[col])

                if HEADERS[col] == "Horas":
                    e.configure(state="readonly")

                e.grid(row=row, column=col, padx=1, pady=1)
                fila_widgets.append(e)

            # Botón asignador
            btn_asignar = ttk.Button(
                frame,
                text="🧩",
                width=3,
                command=lambda fw=fila_widgets, fpp=filas_por_programa, db=db_ciclo_path, prog=programa:
                    abrir_asignador_horarios(fw, fpp, db, prog)
            )
            btn_asignar.grid(row=row, column=len(HEADERS), padx=4)
            fila_widgets.append(btn_asignar)

            filas_por_programa[prog].append(fila_widgets)
            row += 1
            
    
    # ==================================================
    # MOSTRAR SOLO PROGRAMA ACTIVO
    # ==================================================
    for prog, filas in filas_por_programa.items():
        if prog != programa:
            for fila in filas:
                for w in fila:
                    w.grid_remove()

    # Guardar referencias en ventana
    win._filas_por_programa = filas_por_programa
    win._db_ciclo_path = db_ciclo_path
    win._programa_actual = programa
    win.protocol("WM_DELETE_WINDOW", lambda: confirmar_cierre(win))
    win._activar_scroll = activar_scroll
    win._desactivar_scroll = desactivar_scroll
    
    
def confirmar_cierre(parent):

    popup = tk.Toplevel(parent)
    popup.title("Confirmar cierre")
    popup.transient(parent)
    popup.grab_set()
    parent._desactivar_scroll()
    popup.resizable(False, False)
    popup.configure(bg="#f2f4f8")

    frame = tk.Frame(popup, bg="#f2f4f8", padx=30, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="⚠ ¿Desea cerrar el editor?",
        font=("Segoe UI", 12, "bold"),
        bg="#f2f4f8"
    ).pack(pady=(0, 10))

    tk.Label(
        frame,
        text="Todo lo que no se haya guardado se perderá.",
        bg="#f2f4f8",
        fg="#444"
    ).pack(pady=(0, 15))

    botones = tk.Frame(frame, bg="#f2f4f8")
    botones.pack()

    """
    ttk.Button(
        botones,
        text="Cancelar",
        command=popup.destroy
    ).pack(side="left", padx=10)
    """
    def cancelar():
        popup.destroy()
        parent._activar_scroll()

    ttk.Button(
        botones,
        text="Cancelar",
        command=cancelar
    ).pack(side="left", padx=10)

    def cerrar():
        popup.destroy()
        # Desactivar eventos globales correctamente
        parent.unbind_all("<MouseWheel>")
        parent.unbind_all("<Shift-MouseWheel>")
        parent.unbind_all("<Button-4>")
        parent.unbind_all("<Button-5>")
        parent.destroy()

    ttk.Button(
        botones,
        text="Cerrar sin guardar",
        command=cerrar
    ).pack(side="left", padx=10)

    popup.update_idletasks()

    # Centrar
    width = popup.winfo_width()
    height = popup.winfo_height()
    x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")
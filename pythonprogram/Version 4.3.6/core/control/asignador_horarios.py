# core/control/asignador_horarios.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from collections import defaultdict
from config import RUTA_BASEDATOS

# Importar el módulo de sugerencias
from core.control.validaciones.sugerenciasalon import (
    sugerir_salones,
    obtener_alumnos_por_grupo
)

from core.control.validaciones.validarhoras_salones import (
    verificar_choques_para_nuevo_horario,
    HORAS_POR_MODALIDAD,
    minutos,
)

# ==================================================
# CONSTANTES
# ==================================================
DIAS = ["L", "M", "X", "J", "V", "S"]
DIAS_COMPLETOS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]


def generar_horas():
    horas = []
    h, m = 7, 0
    while h < 21 or (h == 21 and m == 0):
        horas.append(f"{h:02d}:{m:02d}")
        m += 30
        if m == 60:
            m = 0
            h += 1
    return horas

HORAS = generar_horas()

def mostrar_confirmacion_horas(parent, mensaje, titulo="Confirmación"):
    """
    Muestra una ventana de confirmación personalizada.
    Retorna True si el usuario presiona "Sí", False si presiona "No" o cierra la ventana.
    """
    confirm_win = tk.Toplevel(parent)
    confirm_win.title(titulo)
    confirm_win.configure(bg="#f0f0f0")
    confirm_win.resizable(False, False)
    confirm_win.transient(parent)
    confirm_win.grab_set()  # Hace la ventana modal

    # Centrar la ventana sobre la ventana padre
    confirm_win.update_idletasks()
    parent_x = parent.winfo_rootx()
    parent_y = parent.winfo_rooty()
    parent_width = parent.winfo_width()
    parent_height = parent.winfo_height()
    win_width = 450
    win_height = 220
    x = parent_x + (parent_width // 2) - (win_width // 2)
    y = parent_y + (parent_height // 2) - (win_height // 2)
    confirm_win.geometry(f"{win_width}x{win_height}+{x}+{y}")

    # Frame principal con padding
    main_frame = tk.Frame(confirm_win, bg="#f0f0f0", padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    # Icono de advertencia grande
    icon_label = tk.Label(main_frame, text="⚠️", font=("Arial", 36), bg="#f0f0f0", fg="#f39c12")
    icon_label.pack(pady=(0, 10))

    # Mensaje en negrita
    msg_label = tk.Label(main_frame, text=mensaje, font=("Arial", 11, "bold"),
                         bg="#f0f0f0", wraplength=380, justify="center")
    msg_label.pack(pady=(0, 20))

    # Frame para botones
    btn_frame = tk.Frame(main_frame, bg="#f0f0f0")
    btn_frame.pack()

    resultado = tk.BooleanVar(value=False)

    def on_yes():
        resultado.set(True)
        confirm_win.destroy()

    def on_no():
        resultado.set(False)
        confirm_win.destroy()

    # Botón Sí (verde con texto blanco)
    btn_si = tk.Button(btn_frame, text="Sí, guardar", font=("Arial", 10, "bold"),
                       bg="#27ae60", fg="white", activebackground="#2ecc71",
                       activeforeground="white", relief="flat", padx=20, pady=5,
                       command=on_yes)
    btn_si.pack(side="left", padx=10)

    # Botón No (rojo con texto blanco)
    btn_no = tk.Button(btn_frame, text="No, cancelar", font=("Arial", 10, "bold"),
                       bg="#e74c3c", fg="white", activebackground="#c0392b",
                       activeforeground="white", relief="flat", padx=20, pady=5,
                       command=on_no)
    btn_no.pack(side="left", padx=10)

    # Si el usuario cierra la ventana con la X, se considera "No"
    confirm_win.protocol("WM_DELETE_WINDOW", on_no)

    parent.wait_window(confirm_win)  # Espera hasta que la ventana se cierre
    return resultado.get()


def calcular_diferencia_horas(hora_inicio, hora_fin):
    if not hora_inicio or not hora_fin:
        return 0
    inicio_min = minutos(hora_inicio)
    fin_min = minutos(hora_fin)
    if fin_min <= inicio_min:
        return 0
    return (fin_min - inicio_min) / 60.0

# ==================================================
# CARGA DE DATOS DESDE BD
# ==================================================
def cargar_materias():
    con = sqlite3.connect(os.path.join(RUTA_BASEDATOS, "materias.db"))
    cur = con.cursor()
    cur.execute("SELECT materia FROM materias ORDER BY materia")
    data = [r[0] for r in cur.fetchall()]
    con.close()
    return data

def cargar_profesores():
    con = sqlite3.connect(os.path.join(RUTA_BASEDATOS, "profesores.db"))
    cur = con.cursor()
    cur.execute("SELECT nombre FROM profesores ORDER BY nombre")
    data = [r[0] for r in cur.fetchall()]
    con.close()
    return data

# ==================================================
# FUNCIONES DE USO DE SALONES (sin cambios)
# ==================================================
def calcular_uso_salones_horas(filas_por_programa):
    uso = defaultdict(float)
    for programa, filas in filas_por_programa.items():
        for fila in filas:
            if len(fila) > 4:
                salon = ""
                if hasattr(fila[4], 'get'):
                    salon = fila[4].get().strip()
                elif hasattr(fila[4], 'cget'):
                    salon = fila[4].cget("text").strip()
                if not salon:
                    continue
                horas_dia = 0
                for col in range(6, 12):
                    if col < len(fila):
                        horario = ""
                        if hasattr(fila[col], 'get'):
                            horario = fila[col].get().strip()
                        if horario and "-" in horario:
                            try:
                                h_ini, h_fin = horario.split("-")
                                horas_dia += calcular_diferencia_horas(h_ini.strip(), h_fin.strip())
                            except:
                                continue
                uso[salon] += horas_dia
    return uso

def mostrar_uso_salones(parent, filas_por_programa):
    uso = calcular_uso_salones_horas(filas_por_programa)
    con = sqlite3.connect(os.path.join(RUTA_BASEDATOS, "salones.db"))
    cur = con.cursor()
    cur.execute("SELECT edificio, salon FROM salones ORDER BY edificio, salon")
    todos = [f"{e} {s}" for e, s in cur.fetchall()]
    con.close()

    win = tk.Toplevel(parent)
    win.title("Uso de salones (Horas)")
    win.geometry("500x500")
    win.transient(parent)
    win.grab_set()

    tk.Label(win, text="Uso de salones (8 horas diarias = 100%)",
             font=("Arial", 12, "bold")).pack(pady=10)

    canvas = tk.Canvas(win)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    tk.Label(frame, text="Salón", font=("Arial", 10, "bold"),
             width=20, anchor="w").grid(row=0, column=0, padx=5, pady=2, sticky="w")
    tk.Label(frame, text="Horas", font=("Arial", 10, "bold"),
             width=10, anchor="w").grid(row=0, column=1, padx=5, pady=2, sticky="w")
    tk.Label(frame, text="Porcentaje", font=("Arial", 10, "bold"),
             width=15, anchor="w").grid(row=0, column=2, padx=5, pady=2, sticky="w")

    for i, salon in enumerate(todos, 1):
        horas = uso.get(salon, 0)
        porcentaje = (horas / 48.0) * 100 if horas > 0 else 0
        tk.Label(frame, text=salon, width=20, anchor="w").grid(row=i, column=0, padx=5, pady=2, sticky="w")
        tk.Label(frame, text=f"{horas:.1f} h", width=10, anchor="w").grid(row=i, column=1, padx=5, pady=2, sticky="w")
        tk.Label(frame, text=f"{porcentaje:.1f} %", width=15, anchor="w",
                 fg="red" if porcentaje > 100 else "black").grid(row=i, column=2, padx=5, pady=2, sticky="w")

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# ==================================================
# VERIFICACIÓN DE DUPLICADOS
# ==================================================
def verificar_duplicado_materia_grupo(filas_por_programa, programa_actual, grupo_actual, materia_actual, fila_a_excluir=None):
    filas = filas_por_programa.get(programa_actual, [])
    for fila in filas:
        if fila_a_excluir and fila is fila_a_excluir:
            continue
        grupo = ""
        if hasattr(fila[1], 'cget'):
            grupo = fila[1].cget("text").strip()
        elif hasattr(fila[1], 'get'):
            grupo = fila[1].get().strip()
        materia = ""
        if len(fila) > 3 and hasattr(fila[3], 'get'):
            materia = fila[3].get().strip()
        if grupo == grupo_actual and materia == materia_actual and grupo and materia:
            return True, programa_actual, fila
    return False, None, None

# ==================================================
# CLASE TOOLTIP (sin cambios)
# ==================================================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind('<Enter>', self.show_tip)
        widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 9))
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ==================================================
# FUNCIÓN PARA COMBOBOX CON BÚSQUEDA
# ==================================================
def crear_combobox_con_busqueda(parent, valores_completos, width=30):
    var = tk.StringVar()
    cb = ttk.Combobox(parent, textvariable=var, values=valores_completos, width=width)
    cb._valores_completos = valores_completos

    def on_keyrelease(event):
        value = event.widget.get()
        if value == '':
            event.widget['values'] = valores_completos
        else:
            filtered = [v for v in valores_completos if value.lower() in v.lower()]
            event.widget['values'] = filtered
        # Forzar la apertura del desplegable
        # event.widget.event_generate('<Down>')

    def on_focusout(event):
        value = event.widget.get().strip()
        if value and value not in valores_completos:
            event.widget.set('')

    cb.bind('<KeyRelease>', on_keyrelease)
    cb.bind('<FocusOut>', on_focusout)
    return cb

# ==================================================
# VENTANA PRINCIPAL DE ASIGNACIÓN
# ==================================================
def abrir_asignador_horarios(fila_widgets, filas_por_programa, db_ciclo_path, programa_actual):
    win = tk.Toplevel()
    win.title("Editar Asignación")
    win.configure(bg="#f0f0f0")
    win.resizable(True, True)

    main_frame = tk.Frame(win, bg="#f0f0f0")
    main_frame.pack(fill="both", expand=True, padx=15, pady=15)

    # ---------- Información del grupo ----------
    info_frame = tk.Frame(main_frame, bg="#f0f0f0", relief="solid", borderwidth=1)
    info_frame.pack(fill="x", pady=(0, 15))

    programa_text = fila_widgets[0].cget("text") if hasattr(fila_widgets[0], 'cget') else ""
    grupo_text = fila_widgets[1].cget("text") if hasattr(fila_widgets[1], 'cget') else ""
    modalidad_text = fila_widgets[2].cget("text") if hasattr(fila_widgets[2], 'cget') else ""

    tk.Label(info_frame, text=f"Programa: {programa_text}",
             bg="#f0f0f0", anchor="w", font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=5)
    tk.Label(info_frame, text=f"Grupo: {grupo_text}",
             bg="#f0f0f0", anchor="w", font=("Arial", 9)).pack(anchor="w", padx=10, pady=2)
    tk.Label(info_frame, text=f"Modalidad: {modalidad_text}",
             bg="#f0f0f0", anchor="w", font=("Arial", 9)).pack(anchor="w", padx=10, pady=2)

    # ---------- Variables de control ----------
    hay_duplicado_materia = False
    hay_choques_horario = False
    hay_rangos_invalidos = False

    # ---------- Etiquetas de advertencia ----------
    warning_frame = tk.Frame(main_frame, bg="#f0f0f0")
    warning_frame.pack(fill="x", pady=(0, 5))
    warning_label = tk.Label(warning_frame, text="", fg="red", bg="#f0f0f0",
                             font=("Arial", 9), wraplength=450, justify="left")
    warning_label.pack(anchor="w")

    warning_frame_choques = tk.Frame(main_frame, bg="#f0f0f0")
    warning_frame_choques.pack(fill="x", pady=(0, 5))
    warning_label_choques = tk.Label(warning_frame_choques, text="", fg="red", bg="#f0f0f0",
                                     font=("Arial", 9), wraplength=450, justify="left")
    warning_label_choques.pack(anchor="w")

    warning_frame_rangos = tk.Frame(main_frame, bg="#f0f0f0")
    warning_frame_rangos.pack(fill="x", pady=(0, 5))
    warning_label_rangos = tk.Label(warning_frame_rangos, text="", fg="red", bg="#f0f0f0",
                                    font=("Arial", 9), wraplength=450, justify="left")
    warning_label_rangos.pack(anchor="w")

    # ---------- Campos principales con búsqueda ----------
    campos_frame = tk.Frame(main_frame, bg="#f0f0f0")
    campos_frame.pack(fill="x", pady=(0, 15))
    campos_frame.columnconfigure(1, weight=1)

    materias = cargar_materias()
    cb_materia = crear_combobox_con_busqueda(campos_frame, materias, width=30)
    tk.Label(campos_frame, text="Materia:", bg="#f0f0f0", anchor="w").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
    cb_materia.grid(row=0, column=1, sticky="ew", pady=5)

    profesores = cargar_profesores()
    cb_profesor = crear_combobox_con_busqueda(campos_frame, profesores, width=30)
    tk.Label(campos_frame, text="Profesor:", bg="#f0f0f0", anchor="w").grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
    cb_profesor.grid(row=1, column=1, sticky="ew", pady=5)

    # ---------- Combobox de salón (con búsqueda y sugerencias) ----------
    tk.Label(campos_frame, text="Salón:", bg="#f0f0f0", anchor="w").grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
    salon_var = tk.StringVar()
    cb_salon = ttk.Combobox(campos_frame, textvariable=salon_var, state="normal", width=30)
    cb_salon.grid(row=2, column=1, sticky="ew", pady=5)
    cb_salon._valores_completos = []

    def filtrar_salones(event):
        value = event.widget.get()
        completos = getattr(event.widget, '_valores_completos', [])
        if value == '':
            event.widget['values'] = completos
        else:
            filtered = [v for v in completos if value.lower() in v.lower()]
            event.widget['values'] = filtered
        #event.widget.event_generate('<Down>')

    def validar_salon_focusout(event):
        value = event.widget.get().strip()
        completos = getattr(event.widget, '_valores_completos', [])
        if value and value not in completos:
            event.widget.set('')

    cb_salon.bind('<KeyRelease>', filtrar_salones)
    cb_salon.bind('<FocusOut>', validar_salon_focusout)

    # ---------- Función para obtener valor real del salón ----------
    def obtener_valor_real_salon(etiqueta_seleccionada):
        if not etiqueta_seleccionada:
            return ""
        materia_seleccionada = cb_materia.get().strip()
        if materia_seleccionada and grupo_text:
            sugerencias = sugerir_salones(db_ciclo_path, programa_text, grupo_text, filas_por_programa)
            for etiqueta, valor in sugerencias:
                if etiqueta == etiqueta_seleccionada:
                    return valor
        partes = etiqueta_seleccionada.split()
        if len(partes) >= 2:
            return f"{partes[0]} {partes[1]}"
        return etiqueta_seleccionada

    # ---------- Funciones de validación en tiempo real ----------
    def actualizar_estado_guardar():
        # Esta función se definirá después de crear btn_guardar, por ahora placeholder
        pass

    def verificar_duplicado_tiempo_real(*args):
        nonlocal hay_duplicado_materia
        materia_seleccionada = cb_materia.get().strip()
        if not materia_seleccionada or not grupo_text:
            warning_label.config(text="")
            hay_duplicado_materia = False
            cb_materia.config(style="TCombobox")
            actualizar_estado_guardar()
            return

        es_duplicado, programa_duplicado, fila_duplicada = verificar_duplicado_materia_grupo(
            filas_por_programa, programa_text, grupo_text, materia_seleccionada, fila_widgets
        )

        if es_duplicado:
            salon_duplicado = ""
            profesor_duplicado = ""
            horarios_duplicados = []
            if fila_duplicada:
                if len(fila_duplicada) > 4 and hasattr(fila_duplicada[4], 'get'):
                    salon_duplicado = fila_duplicada[4].get().strip()
                if len(fila_duplicada) > 5 and hasattr(fila_duplicada[5], 'get'):
                    profesor_duplicado = fila_duplicada[5].get().strip()
                for i, d in enumerate(DIAS):
                    col_index = 6 + i
                    if len(fila_duplicada) > col_index and hasattr(fila_duplicada[col_index], 'get'):
                        horario = fila_duplicada[col_index].get().strip()
                        if horario:
                            horarios_duplicados.append(f"{DIAS_COMPLETOS[i]}: {horario}")

            warning_text = f"⚠️ ADVERTENCIA: La materia '{materia_seleccionada}' ya está asignada a este grupo.\n"
            warning_text += f"Programa: {programa_duplicado} | Grupo: {grupo_text}\n"
            if salon_duplicado:
                warning_text += f"Salón: {salon_duplicado}\n"
            if profesor_duplicado:
                warning_text += f"Profesor: {profesor_duplicado}\n"
            if horarios_duplicados:
                warning_text += "Horarios existentes:\n"
                for horario in horarios_duplicados[:2]:
                    warning_text += f"  • {horario}\n"
                if len(horarios_duplicados) > 2:
                    warning_text += f"  ... y {len(horarios_duplicados) - 2} más"
            warning_label.config(text=warning_text)

            style = ttk.Style()
            style.configure("Advertencia.TCombobox", fieldbackground="#ffcccc", foreground="red")
            cb_materia.config(style="Advertencia.TCombobox")
            hay_duplicado_materia = True
        else:
            warning_label.config(text="")
            cb_materia.config(style="TCombobox")
            hay_duplicado_materia = False

        actualizar_sugerencias_salon()
        actualizar_estado_guardar()

    cb_materia.bind("<<ComboboxSelected>>", verificar_duplicado_tiempo_real)
    cb_materia.bind("<FocusOut>", lambda e: win.after(100, verificar_duplicado_tiempo_real))
    cb_materia.bind("<Return>", lambda e: win.after(100, verificar_duplicado_tiempo_real))

    ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

    # ---------- Horarios ----------
    horarios_frame = tk.Frame(main_frame, bg="#f0f0f0")
    horarios_frame.pack(fill="x", pady=(0, 10))

    tk.Label(horarios_frame, text="Horarios por día:", font=("Arial", 10, "bold"),
             bg="#f0f0f0").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 10))

    horarios = {}
    horas_var = tk.StringVar(value="0.0 h")

    def validar_rangos_horarios_tiempo_real():
        nonlocal hay_rangos_invalidos
        dias_invalidos = []
        for d in DIAS:
            ini, fin, _ = horarios[d]
            ini_val = ini.get().strip()
            fin_val = fin.get().strip()
            if ini_val and fin_val:
                if minutos(fin_val) <= minutos(ini_val):
                    dias_invalidos.append(DIAS_COMPLETOS[DIAS.index(d)])
        if dias_invalidos:
            dias_str = ", ".join(dias_invalidos)
            warning_label_rangos.config(
                text=f"⚠️ ADVERTENCIA: En los días {dias_str} la hora de fin debe ser mayor que la de inicio."
            )
            hay_rangos_invalidos = True
        else:
            warning_label_rangos.config(text="")
            hay_rangos_invalidos = False
        actualizar_estado_guardar()

    def actualizar_total_horas(*_):
        total = 0
        for d in DIAS:
            ini, fin, _ = horarios[d]
            ini_val = ini.get().strip()
            fin_val = fin.get().strip()
            if ini_val and fin_val:
                total += calcular_diferencia_horas(ini_val, fin_val)
        horas_var.set(f"{total:.1f} h")
        horas_requeridas = HORAS_POR_MODALIDAD.get(modalidad_text, 5.0)
        if abs(total - horas_requeridas) < 0.1:
            horas_label.config(fg="green")
        else:
            horas_label.config(fg="red")
        validar_rangos_horarios_tiempo_real()

    def verificar_choques_tiempo_real(*_):
        nonlocal hay_choques_horario
        nuevos_horarios = {}
        for d in DIAS:
            ini, fin, _ = horarios[d]
            ini_val = ini.get().strip()
            fin_val = fin.get().strip()
            if ini_val and fin_val:
                nuevos_horarios[d] = f"{ini_val}-{fin_val}"
        profesor_actual = cb_profesor.get().strip()
        salon_actual = obtener_valor_real_salon(cb_salon.get())
        choques = verificar_choques_para_nuevo_horario(
            filas_por_programa, grupo_text, salon_actual, profesor_actual, nuevos_horarios, fila_widgets
        )
        if choques:
            mensaje = "⚠️ ADVERTENCIA! Posibles choques de horario:\n"
            choques_grupo = [c for c in choques if c['tipo'] == 'GRUPO']
            choques_profesor = [c for c in choques if c['tipo'] == 'PROFESOR']
            choques_salon = [c for c in choques if c['tipo'] == 'SALÓN']
            if choques_grupo:
                mensaje += "\n• Mismo grupo en horario superpuesto:"
                for choque in choques_grupo[:2]:
                    mensaje += f"\n  - {choque['dia']}: {choque['horario_nuevo']} choca con {choque['horario_existente']}"
                if len(choques_grupo) > 2:
                    mensaje += f"\n  ... y {len(choques_grupo) - 2} más"
            if choques_profesor:
                mensaje += "\n• Mismo profesor en horario superpuesto:"
                for choque in choques_profesor[:2]:
                    mensaje += f"\n  - {choque['dia']}: {choque['horario_nuevo']} choca con {choque['horario_existente']}"
                if len(choques_profesor) > 2:
                    mensaje += f"\n  ... y {len(choques_profesor) - 2} más"
            if choques_salon:
                mensaje += "\n• Mismo salón en horario superpuesto:"
                for choque in choques_salon[:2]:
                    mensaje += f"\n  - {choque['dia']}: {choque['horario_nuevo']} choca con {choque['horario_existente']}"
                if len(choques_salon) > 2:
                    mensaje += f"\n  ... y {len(choques_salon) - 2} más"
            warning_label_choques.config(text=mensaje, fg="orange")
            hay_choques_horario = True
        else:
            warning_label_choques.config(text="")
            hay_choques_horario = False
        actualizar_estado_guardar()

    def on_cambio_horario(*args):
        actualizar_total_horas()
        verificar_choques_tiempo_real()

    def borrar_horario_dia(dia):
        ini, fin, _ = horarios[dia]
        ini.set('')
        fin.set('')
        on_cambio_horario()

    for i, (d_short, d_long) in enumerate(zip(DIAS, DIAS_COMPLETOS)):
        row = i + 1
        tk.Label(horarios_frame, text=d_long, width=12, anchor="w",
                 bg="#f0f0f0").grid(row=row, column=0, sticky="w", padx=(0, 5), pady=2)
        ini = ttk.Combobox(horarios_frame, values=HORAS, width=8, state="readonly")
        ini.grid(row=row, column=1, padx=2, pady=2)
        tk.Label(horarios_frame, text="a", bg="#f0f0f0").grid(row=row, column=2, padx=2, pady=2)
        fin = ttk.Combobox(horarios_frame, values=HORAS, width=8, state="readonly")
        fin.grid(row=row, column=3, padx=2, pady=2)
        btn_borrar = ttk.Button(horarios_frame, text="🗑", width=3,
                                command=lambda d=d_short: borrar_horario_dia(d))
        btn_borrar.grid(row=row, column=4, padx=(10, 0), pady=2)
        ToolTip(btn_borrar, f"Borrar horario del {d_long}")
        ini.bind("<<ComboboxSelected>>", on_cambio_horario)
        fin.bind("<<ComboboxSelected>>", on_cambio_horario)
        horarios[d_short] = (ini, fin, btn_borrar)

    # ---------- Total de horas ----------
    horas_frame = tk.Frame(main_frame, bg="#f0f0f0")
    horas_frame.pack(fill="x", pady=(10, 5))
    tk.Label(horas_frame, text="Total de horas:", font=("Arial", 10, "bold"),
             bg="#f0f0f0").pack(side="left")
    horas_label = tk.Label(horas_frame, textvariable=horas_var, font=("Arial", 11, "bold"),
                           bg="#f0f0f0", fg="#2c3e50")
    horas_label.pack(side="left", padx=(10, 20))
    horas_requeridas = HORAS_POR_MODALIDAD.get(modalidad_text, 5.0)
    horas_requeridas_text = f"Requeridas: {horas_requeridas}h ({modalidad_text})"
    tk.Label(horas_frame, text=horas_requeridas_text, font=("Arial", 9),
             bg="#f0f0f0", fg="#666666").pack(side="left")

    # ---------- Función guardar (definida antes de usarla) ----------
    def guardar():
        # Validaciones finales (similares a las de tiempo real, pero con confirmación)
        materia_seleccionada = cb_materia.get().strip()
        if not materia_seleccionada:
            warning_label.config(text="⚠️ ADVERTENCIA: Debe seleccionar una materia.")
            return

        salon_seleccionado = obtener_valor_real_salon(cb_salon.get())
        profesor_seleccionado = cb_profesor.get().strip()

        # Verificar duplicado (última oportunidad)
        es_duplicado, prog_dup, fila_dup = verificar_duplicado_materia_grupo(
            filas_por_programa, programa_text, grupo_text, materia_seleccionada, fila_widgets
        )
        if es_duplicado:
            warning_label.config(text="No se puede guardar: materia duplicada para este grupo.")
            return

        # Verificar rangos inválidos
        rangos_invalidos = []
        for d in DIAS:
            ini, fin, _ = horarios[d]
            ini_val = ini.get().strip()
            fin_val = fin.get().strip()
            if ini_val and fin_val and minutos(fin_val) <= minutos(ini_val):
                rangos_invalidos.append(DIAS_COMPLETOS[DIAS.index(d)])
        if rangos_invalidos:
            warning_label_rangos.config(text=f"Corrija los rangos en: {', '.join(rangos_invalidos)}")
            return

        # Verificar choques
        nuevos_horarios = {}
        for d in DIAS:
            ini, fin, _ = horarios[d]
            ini_val = ini.get().strip()
            fin_val = fin.get().strip()
            if ini_val and fin_val:
                nuevos_horarios[d] = f"{ini_val}-{fin_val}"
        choques = verificar_choques_para_nuevo_horario(
            filas_por_programa, grupo_text, salon_seleccionado, profesor_seleccionado,
            nuevos_horarios, fila_widgets
        )
        if choques:
            warning_label_choques.config(text="Existen choques de horario, no se puede guardar.", fg="red")
            return

        # Verificar horas según modalidad
        total_horas = 0
        for d in DIAS:
            ini, fin, _ = horarios[d]
            ini_val = ini.get().strip()
            fin_val = fin.get().strip()
            if ini_val and fin_val:
                total_horas += calcular_diferencia_horas(ini_val, fin_val)
        horas_requeridas = HORAS_POR_MODALIDAD.get(modalidad_text, 5.0)
        if abs(total_horas - horas_requeridas) > 0.1:
            mensaje = (f"El grupo requiere {horas_requeridas}h ({modalidad_text}), "
                       f"pero se asignaron {total_horas:.1f}h.\n¿Guardar de todas formas?")
            if not mostrar_confirmacion_horas(win, mensaje):
                return

        # Guardar datos en la fila
        # Materia
        if len(fila_widgets) > 3 and hasattr(fila_widgets[3], 'delete'):
            fila_widgets[3].delete(0, tk.END)
            fila_widgets[3].insert(0, materia_seleccionada)
        # Salón
        if len(fila_widgets) > 4 and hasattr(fila_widgets[4], 'delete'):
            fila_widgets[4].delete(0, tk.END)
            fila_widgets[4].insert(0, salon_seleccionado)
        # Profesor
        if len(fila_widgets) > 5 and hasattr(fila_widgets[5], 'delete'):
            fila_widgets[5].delete(0, tk.END)
            fila_widgets[5].insert(0, profesor_seleccionado)
        # Horarios
        for i, d in enumerate(DIAS):
            ini, fin, _ = horarios[d]
            txt = ""
            ini_val = ini.get().strip()
            fin_val = fin.get().strip()
            if ini_val and fin_val:
                txt = f"{ini_val}-{fin_val}"
            col_index = 6 + i
            if len(fila_widgets) > col_index and hasattr(fila_widgets[col_index], 'delete'):
                fila_widgets[col_index].delete(0, tk.END)
                fila_widgets[col_index].insert(0, txt)
        # Total horas
        if len(fila_widgets) > 12 and hasattr(fila_widgets[12], 'configure'):
            fila_widgets[12].configure(state="normal")
            fila_widgets[12].delete(0, tk.END)
            fila_widgets[12].insert(0, horas_var.get())
            fila_widgets[12].configure(state="readonly")

        win.destroy()

    # ---------- Botones inferiores ----------
    footer = tk.Frame(main_frame, bg="#f0f0f0")
    footer.pack(fill="x", pady=(15, 0))

    def borrar_todos_horarios():
        for d in DIAS:
            borrar_horario_dia(d)

    left_btn_frame = tk.Frame(footer, bg="#f0f0f0")
    left_btn_frame.pack(side="left", fill="x", expand=True)

    btn_borrar_todos = ttk.Button(left_btn_frame, text="🗑️ Borrar todos los horarios",
                                   command=borrar_todos_horarios)
    btn_borrar_todos.pack(side="left", padx=(0, 10))
    ToolTip(btn_borrar_todos, "Eliminar todos los horarios de todos los días")

    btn_uso_salones = ttk.Button(left_btn_frame, text="📊 Uso de salones",
                                  command=lambda: mostrar_uso_salones(win, filas_por_programa))
    btn_uso_salones.pack(side="left")
    ToolTip(btn_uso_salones, "Ver estadísticas de uso de salones")

    right_btn_frame = tk.Frame(footer, bg="#f0f0f0")
    right_btn_frame.pack(side="right")

    btn_cancelar = ttk.Button(right_btn_frame, text="Cancelar", command=win.destroy)
    btn_cancelar.pack(side="left", padx=5)
    ToolTip(btn_cancelar, "Cancelar y cerrar sin guardar")

    btn_guardar = ttk.Button(right_btn_frame, text="Guardar", command=guardar,
                             style="Accent.TButton")
    btn_guardar.pack(side="left", padx=5)
    ToolTip(btn_guardar, "Guardar los cambios realizados")

    # Configurar estilo para botón de guardar
    style = ttk.Style()
    style.configure("Accent.TButton", foreground="white", background="#2c3e50")

    # ---------- Redefinir actualizar_estado_guardar ahora que btn_guardar existe ----------
    def actualizar_estado_guardar():
        nonlocal hay_duplicado_materia, hay_choques_horario, hay_rangos_invalidos
        if hay_duplicado_materia or hay_choques_horario or hay_rangos_invalidos:
            btn_guardar.config(state="disabled")
        else:
            btn_guardar.config(state="normal")

    # Llamar a actualizar_estado_guardar una vez para establecer estado inicial
    actualizar_estado_guardar()

    # ---------- Funciones auxiliares para salones ----------
    def actualizar_sugerencias_salon():
        nonlocal warning_label
        materia_seleccionada = cb_materia.get().strip()
        if not materia_seleccionada or not grupo_text:
            con = sqlite3.connect(os.path.join(RUTA_BASEDATOS, "salones.db"))
            cur = con.cursor()
            cur.execute("SELECT edificio, salon FROM salones ORDER BY edificio, salon")
            salones_todos = [f"{e} {s}" for e, s in cur.fetchall()]
            con.close()
            cb_salon['values'] = salones_todos
            cb_salon._valores_completos = salones_todos
            warning_label.config(text="")
            return

        sugerencias = sugerir_salones(db_ciclo_path, programa_text, grupo_text, filas_por_programa)
        if sugerencias:
            etiquetas = [s[0] for s in sugerencias]
            cb_salon['values'] = etiquetas
            cb_salon._valores_completos = etiquetas
            warning_label.config(text="")
            salon_actual = cb_salon.get()
            if salon_actual:
                for etiqueta, valor in sugerencias:
                    if valor in salon_actual:
                        cb_salon.set(etiqueta)
                        break
        else:
            alumnos = obtener_alumnos_por_grupo(db_ciclo_path, programa_text, grupo_text)
            max_capacidad = 0
            con = sqlite3.connect(os.path.join(RUTA_BASEDATOS, "salones.db"))
            cur = con.cursor()
            cur.execute("SELECT MAX(capacidad) FROM salones")
            row = cur.fetchone()
            if row and row[0]:
                max_capacidad = row[0]
            if alumnos > 0 and max_capacidad < alumnos:
                cb_salon['values'] = []
                cb_salon._valores_completos = []
                cb_salon.set('')
                warning_label.config(
                    text=f"⚠️ ADVERTENCIA CRÍTICA: Ningún salón tiene capacidad para {alumnos} alumnos. "
                         f"Capacidad máxima disponible: {max_capacidad}. No se puede asignar salón.",
                    fg="red"
                )
            else:
                cur.execute("SELECT edificio, salon FROM salones ORDER BY edificio, salon")
                salones_todos = [f"{e} {s}" for e, s in cur.fetchall()]
                cb_salon['values'] = salones_todos
                cb_salon._valores_completos = salones_todos
                warning_label.config(
                    text="⚠️ No se encontraron sugerencias automáticas. Mostrando todos los salones.",
                    fg="orange"
                )
            con.close()

    cb_materia.bind("<<ComboboxSelected>>", lambda e: actualizar_sugerencias_salon())
    cb_materia.bind("<FocusOut>", lambda e: win.after(100, actualizar_sugerencias_salon))

    # ---------- Cargar datos existentes ----------
    if len(fila_widgets) > 3 and hasattr(fila_widgets[3], 'get'):
        materia_actual = fila_widgets[3].get().strip()
        if materia_actual:
            cb_materia.set(materia_actual)
            win.after(100, verificar_duplicado_tiempo_real)

    if len(fila_widgets) > 5 and hasattr(fila_widgets[5], 'get'):
        profesor_actual = fila_widgets[5].get().strip()
        if profesor_actual:
            cb_profesor.set(profesor_actual)

    if len(fila_widgets) > 4 and hasattr(fila_widgets[4], 'get'):
        salon_actual = fila_widgets[4].get().strip()
        if salon_actual:
            actualizar_sugerencias_salon()
            cb_salon.set(salon_actual)

    for i, d in enumerate(DIAS):
        col_index = 6 + i
        if len(fila_widgets) > col_index and hasattr(fila_widgets[col_index], 'get'):
            horario_text = fila_widgets[col_index].get().strip()
            if horario_text and "-" in horario_text:
                try:
                    ini_text, fin_text = horario_text.split("-")
                    ini, fin, _ = horarios[d]
                    ini.set(ini_text.strip())
                    fin.set(fin_text.strip())
                except:
                    pass

    actualizar_total_horas()
    verificar_duplicado_tiempo_real()
    verificar_choques_tiempo_real()

    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')
    win.lift()
    win.focus_force()
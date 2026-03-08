# manage_profesores.py - UI moderna y compatible
import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config import RUTA_BASEDATOS

# ==================================================
# CLASE ToolTip (para mostrar ayuda al pasar el mouse)
# ==================================================
class ToolTip:
    def __init__(self, widget, texto):
        self.widget = widget
        self.texto = texto
        self.tip_ventana = None
        widget.bind('<Enter>', self.mostrar)
        widget.bind('<Leave>', self.ocultar)
        widget.bind('<ButtonPress>', self.ocultar)

    def mostrar(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tip_ventana = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.texto, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack()

    def ocultar(self, event=None):
        if self.tip_ventana:
            self.tip_ventana.destroy()
            self.tip_ventana = None

# ==================================================
# RUTAS
# ==================================================

DB = os.path.join(RUTA_BASEDATOS, "profesores.db")
# ==================================================
# DB
# ==================================================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profesores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contratacion TEXT,
            telefono TEXT,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()

# ==================================================
# CRUD
# ==================================================
def listar_profesores():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT id, nombre, contratacion, telefono, email
        FROM profesores
        ORDER BY nombre
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def agregar_profesor(nombre, contratacion, telefono, email):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO profesores (nombre, contratacion, telefono, email)
        VALUES (?, ?, ?, ?)
    """, (nombre, contratacion, telefono, email))
    conn.commit()
    conn.close()

def actualizar_profesor(pid, nombre, contratacion, telefono, email):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        UPDATE profesores
        SET nombre=?, contratacion=?, telefono=?, email=?
        WHERE id=?
    """, (nombre, contratacion, telefono, email, pid))
    conn.commit()
    conn.close()

def borrar_profesor(pid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM profesores WHERE id=?", (pid,))
    conn.commit()
    conn.close()

# ==================================================
# IMPORTAR EXCEL
# ==================================================
def importar_excel(refresh_cb):
    try:
        import pandas as pd
    except ImportError:
        # Ventana personalizada en lugar de messagebox
        win = tk.Toplevel()
        win.title("Error")
        win.geometry("400x150")
        win.resizable(False, False)
        win.grab_set()
        
        tk.Label(win, text="Error", font=("Segoe UI", 14, "bold")).pack(pady=10)
        tk.Label(win, text="Instala pandas y openpyxl para importar archivos Excel").pack(pady=5)
        tk.Label(win, text="pip install pandas openpyxl").pack(pady=5)
        tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=10)
        return

    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Excel", "*.xlsx")]
    )
    if not ruta:
        return

    df = pd.read_excel(ruta)
    columnas = [c.lower() for c in df.columns]

    requeridas = ["nombre", "contratacion", "telefono", "email"]
    if not all(col in columnas for col in requeridas):
        # Ventana personalizada
        win = tk.Toplevel()
        win.title("Formato incorrecto")
        win.geometry("500x200")
        win.resizable(False, False)
        win.grab_set()
        
        tk.Label(win, text="Formato incorrecto", font=("Segoe UI", 14, "bold"), fg="red").pack(pady=10)
        tk.Label(win, text="El Excel debe tener las columnas:").pack(pady=5)
        tk.Label(win, text="nombre | contratacion | telefono | email", font=("Courier", 10)).pack(pady=5)
        tk.Label(win, text="(las columnas pueden estar en cualquier orden)").pack(pady=5)
        tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=10)
        return

    errores = 0
    for _, fila in df.iterrows():
        nombre = str(fila["nombre"]).strip()
        if not nombre:
            errores += 1
            continue

        agregar_profesor(
            nombre,
            str(fila["contratacion"]).strip(),
            str(fila["telefono"]).strip(),
            str(fila["email"]).strip()
        )

    refresh_cb()
    
    # Ventana personalizada para mostrar resultados
    win = tk.Toplevel()
    win.title("Importación finalizada")
    win.geometry("400x150")
    win.resizable(False, False)
    win.grab_set()
    
    tk.Label(win, text="Importación finalizada", font=("Segoe UI", 14, "bold")).pack(pady=10)
    tk.Label(win, text=f"Filas procesadas: {len(df) - errores}").pack(pady=5)
    tk.Label(win, text=f"Filas omitidas: {errores}").pack(pady=5)
    tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=10)

# ==================================================
# VENTANA FORMATO EXCEL
# ==================================================
def mostrar_formato_excel(continuar_cb):
    win = tk.Toplevel()
    win.title("Formato Excel - Profesores")
    win.geometry("520x300")
    win.resizable(False, False)
    win.grab_set()

    frame = tk.Frame(win, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="Formato requerido del archivo Excel",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=6)

    tabla = ttk.Treeview(
        frame,
        columns=("nombre", "contratacion", "telefono", "email"),
        show="headings",
        height=3
    )

    for col, w in zip(
        ("nombre", "contratacion", "telefono", "email"),
        (140, 120, 120, 180)
    ):
        tabla.heading(col, text=col)
        tabla.column(col, width=w)

    tabla.insert(
        "", "end",
        values=("Juan Pérez", "Tiempo completo", "4921234567", "juan@correo.com")
    )

    tabla.pack(pady=8)

    tk.Label(
        frame,
        text="• Columnas exactas\n• Archivo .xlsx",
        fg="#555555",
        justify="left"
    ).pack()

    btns = tk.Frame(frame)
    btns.pack(pady=10)

    tk.Button(btns, text="Cancelar", width=10, command=win.destroy).grid(row=0, column=0, padx=6)
    tk.Button(
        btns,
        text="Continuar",
        width=10,
        bg="#2E7D32",
        fg="white",
        command=lambda: (win.destroy(), continuar_cb())
    ).grid(row=0, column=1, padx=6)

# ==================================================
# FUNCIONES PARA MOSTRAR VENTANAS DE DIÁLOGO
# ==================================================
def mostrar_aviso(parent, titulo, mensaje):
    win = tk.Toplevel(parent)
    win.title(titulo)
    win.geometry("400x150")
    win.resizable(False, False)
    win.grab_set()
    
    tk.Label(win, text=titulo, font=("Segoe UI", 14, "bold")).pack(pady=10)
    tk.Label(win, text=mensaje).pack(pady=5)
    tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=10)
    
def mostrar_info(parent, titulo, mensaje):
    win = tk.Toplevel(parent)
    win.title(titulo)
    win.geometry("400x150")
    win.resizable(False, False)
    win.grab_set()
    
    tk.Label(win, text=titulo, font=("Segoe UI", 14, "bold"), fg="#2E7D32").pack(pady=10)
    tk.Label(win, text=mensaje).pack(pady=5)
    tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=10)
    
def mostrar_confirmacion(parent, titulo, mensaje, callback_si, callback_no=None):
    win = tk.Toplevel(parent)
    win.title(titulo)
    win.geometry("450x180")
    win.resizable(False, False)
    win.grab_set()
    
    tk.Label(win, text=titulo, font=("Segoe UI", 14, "bold"), fg="#D32F2F").pack(pady=10)
    tk.Label(win, text=mensaje).pack(pady=10)
    
    btns = tk.Frame(win)
    btns.pack(pady=10)
    
    def si():
        win.destroy()
        callback_si()
    
    def no():
        win.destroy()
        if callback_no:
            callback_no()
    
    tk.Button(btns, text="Sí", bg="#D32F2F", fg="white", command=si, width=8).grid(row=0, column=0, padx=10)
    tk.Button(btns, text="No", bg="#757575", fg="white", command=no, width=8).grid(row=0, column=1, padx=10)

# ==================================================
# UI
# ==================================================
def abrir_profesores():
    init_db()
    profesor_editando_id = {"id": None}

    root = tk.Toplevel()
    root.title("Gestor de Profesores")
    root.geometry("850x580")
    root.configure(bg="#f0f5ff")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=26)

    main = tk.Frame(root, bg="#f0f5ff", padx=10, pady=10)
    main.pack(fill="both", expand=True)

    tk.Label(
        main,
        text="Gestión de Profesores",
        bg="#4a6fa5",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        height=2
    ).pack(fill="x")

    tree = ttk.Treeview(
        main,
        columns=("id", "nombre", "contratacion", "telefono", "email"),
        show="headings"
    )

    for col, w in zip(
        ("nombre", "contratacion", "telefono", "email"),
        (200, 140, 140, 240)
    ):
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=w)

    tree.column("id", width=0, stretch=False)
    tree.pack(fill="both", expand=True, pady=6)

    def refresh():
        tree.delete(*tree.get_children())
        for r in listar_profesores():
            tree.insert("", "end", values=r)

    refresh()

    # ================= FORM =================
    form = tk.LabelFrame(main, text="Datos del Profesor", bg="#f0f5ff")
    form.pack(fill="x", pady=6)

    ttk.Label(form, text="Nombre:").grid(row=0, column=0, padx=6, pady=6)
    ent_nom = ttk.Entry(form, width=30)
    ent_nom.grid(row=0, column=1)

    ttk.Label(form, text="Contratación:").grid(row=0, column=2, padx=6)
    ent_con = ttk.Entry(form, width=20)
    ent_con.grid(row=0, column=3)

    ttk.Label(form, text="Teléfono:").grid(row=1, column=0, padx=6)
    ent_tel = ttk.Entry(form, width=20)
    ent_tel.grid(row=1, column=1)

    ttk.Label(form, text="E-mail:").grid(row=1, column=2, padx=6)
    ent_mail = ttk.Entry(form, width=30)
    ent_mail.grid(row=1, column=3)

    def limpiar_form():
        for e in (ent_nom, ent_con, ent_tel, ent_mail):
            e.delete(0, tk.END)
        profesor_editando_id["id"] = None
        btn_agregar.config(state="normal")
        btn_guardar.config(state="disabled")
        ent_nom.focus()

    # ================= BOTONES =================
    btns = tk.Frame(main, bg="#f0f5ff")
    btns.pack(pady=8)

    def agregar_ui():
        if not ent_nom.get().strip():
            mostrar_aviso(root, "Aviso", "El nombre es obligatorio")
            return
        
        try:
            agregar_profesor(
                ent_nom.get().strip(),
                ent_con.get().strip(),
                ent_tel.get().strip(),
                ent_mail.get().strip()
            )
            mostrar_info(root, "Éxito", "Profesor agregado correctamente")
            limpiar_form()
            refresh()
        except Exception as e:
            mostrar_aviso(root, "Error", f"Error al agregar: {str(e)}")

    def editar_ui():
        sel = tree.selection()
        if not sel:
            mostrar_aviso(root, "Aviso", "Selecciona un profesor")
            return

        valores = tree.item(sel[0])["values"]
        
        # Limpiar campos primero
        for entrada in (ent_nom, ent_con, ent_tel, ent_mail):
            entrada.delete(0, tk.END)
        
        # Llenar con valores actuales
        profesor_editando_id["id"] = valores[0]
        ent_nom.insert(0, valores[1])
        ent_con.insert(0, valores[2])
        ent_tel.insert(0, valores[3])
        ent_mail.insert(0, valores[4])

        # Cambiar estados de botones
        btn_agregar.config(state="disabled")
        btn_guardar.config(state="normal")
        
        # Enfocar el primer campo
        ent_nom.focus()

    def guardar_ui():
        pid = profesor_editando_id["id"]
        if pid is None:
            mostrar_aviso(root, "Aviso", "No hay profesor seleccionado para editar")
            return
        
        if not ent_nom.get().strip():
            mostrar_aviso(root, "Aviso", "El nombre es obligatorio")
            return
        
        try:
            actualizar_profesor(
                pid,
                ent_nom.get().strip(),
                ent_con.get().strip(),
                ent_tel.get().strip(),
                ent_mail.get().strip()
            )
            mostrar_info(root, "Éxito", "Profesor actualizado correctamente")
            limpiar_form()
            refresh()
        except Exception as e:
            mostrar_aviso(root, "Error", f"Error al actualizar: {str(e)}")

    def eliminar_ui():
        sel = tree.selection()
        if not sel:
            mostrar_aviso(root, "Aviso", "Selecciona un profesor")
            return
        
        pid = tree.item(sel[0])["values"][0]
        nombre = tree.item(sel[0])["values"][1]
        
        def confirmar_eliminar():
            try:
                borrar_profesor(pid)
                mostrar_info(root, "Éxito", f"Profesor '{nombre}' eliminado correctamente")
                refresh()
            except Exception as e:
                mostrar_aviso(root, "Error", f"Error al eliminar: {str(e)}")
        
        mostrar_confirmacion(
            root, 
            "Confirmar eliminación", 
            f"¿Eliminar al profesor '{nombre}'?", 
            confirmar_eliminar
        )

    # BOTONES CON EMOJIS (asignamos variable a todos para los tooltips)
    btn_agregar = tk.Button(btns, text="➕", bg="#4CAF50", fg="white",
                            command=agregar_ui, width=4, font=("Segoe UI", 12))
    btn_agregar.grid(row=0, column=0, padx=10)

    btn_editar = tk.Button(btns, text="✏", bg="#FF9800", fg="white",
                           command=editar_ui, width=4, font=("Segoe UI", 12))
    btn_editar.grid(row=0, column=1, padx=10)

    btn_guardar = tk.Button(btns, text="💾", bg="#64B5F6", fg="black",
                            command=guardar_ui, width=4,
                            font=("Segoe UI", 12), state="disabled")
    btn_guardar.grid(row=0, column=2, padx=10)

    btn_eliminar = tk.Button(btns, text="🗑", bg="#E53935", fg="white",
                             command=eliminar_ui, width=4, font=("Segoe UI", 12))
    btn_eliminar.grid(row=0, column=3, padx=10)

    btn_importar = tk.Button(btns, text="📥", bg="#2E7D32", fg="white",
                             command=lambda: mostrar_formato_excel(lambda: importar_excel(refresh)),
                             width=4, font=("Segoe UI", 12))
    btn_importar.grid(row=0, column=4, padx=10)

    btn_volver = tk.Button(btns, text="🔙", bg="#607D8B", fg="white",
                           command=root.destroy, width=4, font=("Segoe UI", 12))
    btn_volver.grid(row=0, column=5, padx=10)

    # Asignar tooltips a los botones
    ToolTip(btn_agregar, "Agregar profesor")
    ToolTip(btn_editar, "Editar profesor seleccionado")
    ToolTip(btn_guardar, "Guardar cambios")
    ToolTip(btn_eliminar, "Eliminar profesor seleccionado")
    ToolTip(btn_importar, "Importar desde Excel")
    ToolTip(btn_volver, "Volver")

    # Configurar evento de doble clic en la tabla para editar
    def on_double_click(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            editar_ui()
    
    tree.bind("<Double-1>", on_double_click)
    
    # Inicializar formulario
    limpiar_form()
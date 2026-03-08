# manage_materias.py - Gestor de Materias (UI moderna y simplificada)
import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog
from config import RUTA_BASEDATOS

# ==================================================
# RUTAS
# ==================================================
DB = os.path.join(RUTA_BASEDATOS, "materias.db")

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
# DB
# ==================================================
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia TEXT NOT NULL,
            creditos INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ==================================================
# CRUD
# ==================================================
def listar_materias():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, materia, creditos FROM materias ORDER BY materia")
    rows = cur.fetchall()
    conn.close()
    return rows

def agregar_materia(materia, creditos):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO materias (materia, creditos) VALUES (?, ?)",
        (materia, creditos)
    )
    conn.commit()
    conn.close()

def actualizar_materia(mid, materia, creditos):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "UPDATE materias SET materia=?, creditos=? WHERE id=?",
        (materia, creditos, mid)
    )
    conn.commit()
    conn.close()

def borrar_materia(mid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM materias WHERE id=?", (mid,))
    conn.commit()
    conn.close()

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
# IMPORTACIÓN GUIADA
# ==================================================
def importar_excel(refresh_cb):
    try:
        import pandas as pd
    except ImportError:
        mostrar_aviso(None, "Error", "Instala pandas y openpyxl para importar archivos Excel")
        return

    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Excel", "*.xlsx")]
    )
    if not ruta:
        return

    df = pd.read_excel(ruta)
    columnas = [c.lower() for c in df.columns]

    if "materia" not in columnas or "creditos" not in columnas:
        mostrar_aviso(None, "Error", "Columnas requeridas: materia | creditos")
        return

    errores = 0
    for _, fila in df.iterrows():
        materia = str(fila["materia"]).strip()
        creditos = str(fila["creditos"]).strip()
        if not materia or not creditos.isdigit():
            errores += 1
            continue
        agregar_materia(materia, int(creditos))

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
# VENTANA ILUSTRATIVA
# ==================================================
def mostrar_formato_excel(continuar_cb):
    win = tk.Toplevel()
    win.title("Formato requerido del Excel")
    win.geometry("420x300")
    win.resizable(False, False)
    win.grab_set()

    frame = tk.Frame(win, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Formato del archivo Excel", font=("Segoe UI", 12, "bold")).pack(pady=6)

    tabla = ttk.Treeview(frame, columns=("materia", "creditos"), show="headings", height=4)
    tabla.heading("materia", text="materia")
    tabla.heading("creditos", text="creditos")
    tabla.column("materia", width=220)
    tabla.column("creditos", width=80, anchor="center")

    tabla.insert("", "end", values=("Matemáticas I", "5"))
    tabla.insert("", "end", values=("Física", "6"))
    tabla.insert("", "end", values=("Programación", "8"))
    tabla.pack(pady=8)

    tk.Label(
        frame,
        text="• Las columnas deben llamarse exactamente así\n• El archivo debe ser .xlsx",
        fg="#555555",
        justify="left"
    ).pack(pady=6)

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
# UI
# ==================================================
def abrir_materias():
    init_db()
    materia_editando_id = {"id": None}  # Para guardar la materia en edición

    root = tk.Toplevel()
    root.title("Gestor de Materias")
    root.geometry("850x580")  # más ancho y alto
    root.minsize(760, 520)
    root.configure(bg="#f0f5ff")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=26)

    main = tk.Frame(root, bg="#f0f5ff", padx=10, pady=10)
    main.pack(fill="both", expand=True)

    # HEADER
    header = tk.Frame(main, bg="#4a6fa5", height=55)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="Gestión de Materias",
        bg="#4a6fa5",
        fg="white",
        font=("Segoe UI", 18, "bold")
    ).pack(expand=True)

    # TABLA (ID OCULTO)
    tree = ttk.Treeview(main, columns=("id", "materia", "creditos"), show="headings")
    tree.heading("materia", text="Materia")
    tree.heading("creditos", text="Créditos")
    tree.column("id", width=0, stretch=False)
    tree.column("materia", width=500)
    tree.column("creditos", width=120, anchor="center")
    tree.pack(fill="both", expand=True, pady=6)

    def refresh():
        tree.delete(*tree.get_children())
        for r in listar_materias():
            tree.insert("", "end", values=r)

    refresh()

    # FORM
    form = tk.LabelFrame(main, text="Datos de la materia", bg="#f0f5ff")
    form.pack(fill="x", pady=6)

    tk.Label(form, text="Materia:", bg="#f0f5ff").grid(row=0, column=0, padx=6, pady=6)
    ent_materia = ttk.Entry(form, width=45)
    ent_materia.grid(row=0, column=1, padx=6, pady=6)

    tk.Label(form, text="Créditos:", bg="#f0f5ff").grid(row=1, column=0, padx=6, pady=6)
    ent_creditos = ttk.Entry(form, width=10)
    ent_creditos.grid(row=1, column=1, padx=6, pady=6, sticky="w")

    # FUNCIONES DE FORM
    def limpiar_form():
        ent_materia.delete(0, tk.END)
        ent_creditos.delete(0, tk.END)
        materia_editando_id["id"] = None
        btn_guardar.config(state="disabled")
        btn_agregar.config(state="normal")
        ent_materia.focus()

    def agregar_ui():
        materia = ent_materia.get().strip()
        creditos = ent_creditos.get().strip()
        
        if not materia:
            mostrar_aviso(root, "Aviso", "Ingrese el nombre de la materia")
            return
            
        if not creditos.isdigit():
            mostrar_aviso(root, "Aviso", "Los créditos deben ser un número entero")
            return
            
        try:
            agregar_materia(materia, int(creditos))
            mostrar_info(root, "Éxito", "Materia agregada correctamente")
            limpiar_form()
            refresh()
        except Exception as e:
            mostrar_aviso(root, "Error", f"Error al agregar: {str(e)}")

    def editar_ui():
        sel = tree.selection()
        if not sel:
            mostrar_aviso(root, "Aviso", "Selecciona una materia")
            return
            
        valores = tree.item(sel[0])["values"]
        materia_editando_id["id"] = valores[0]
        
        # Limpiar campos primero
        ent_materia.delete(0, tk.END)
        ent_creditos.delete(0, tk.END)
        
        # Llenar con valores actuales
        ent_materia.insert(0, valores[1])
        ent_creditos.insert(0, valores[2])
        
        # Cambiar estados de botones
        btn_agregar.config(state="disabled")
        btn_guardar.config(state="normal")
        
        # Enfocar el primer campo
        ent_materia.focus()

    def guardar_ui():
        mid = materia_editando_id["id"]
        if mid is None:
            mostrar_aviso(root, "Aviso", "No hay materia seleccionada para editar")
            return
            
        materia = ent_materia.get().strip()
        creditos = ent_creditos.get().strip()
        
        if not materia:
            mostrar_aviso(root, "Aviso", "Ingrese el nombre de la materia")
            return
            
        if not creditos.isdigit():
            mostrar_aviso(root, "Aviso", "Los créditos deben ser un número entero")
            return
            
        try:
            actualizar_materia(mid, materia, int(creditos))
            mostrar_info(root, "Éxito", "Materia actualizada correctamente")
            limpiar_form()
            refresh()
        except Exception as e:
            mostrar_aviso(root, "Error", f"Error al actualizar: {str(e)}")

    def eliminar_ui():
        sel = tree.selection()
        if not sel:
            mostrar_aviso(root, "Aviso", "Selecciona una materia")
            return
            
        mid = tree.item(sel[0])["values"][0]
        materia = tree.item(sel[0])["values"][1]
        
        def confirmar_eliminar():
            try:
                borrar_materia(mid)
                mostrar_info(root, "Éxito", f"Materia '{materia}' eliminada correctamente")
                refresh()
            except Exception as e:
                mostrar_aviso(root, "Error", f"Error al eliminar: {str(e)}")
        
        mostrar_confirmacion(
            root, 
            "Confirmar eliminación", 
            f"¿Eliminar la materia '{materia}'?", 
            confirmar_eliminar
        )

    # BOTONES
    btns = tk.Frame(main, bg="#f0f5ff")
    btns.pack(pady=8)

    btn_agregar = tk.Button(btns, text="➕", bg="#4CAF50", fg="white", 
                           command=agregar_ui, width=6, font=("Segoe UI", 12))
    btn_guardar = tk.Button(btns, text="💾", bg="#64B5F6", fg="black", 
                           command=guardar_ui, width=6, font=("Segoe UI", 12), state="disabled")
    btn_editar = tk.Button(btns, text="✏", bg="#FF9800", fg="white", 
                          command=editar_ui, width=6, font=("Segoe UI", 12))
    btn_eliminar = tk.Button(btns, text="🗑", bg="#E53935", fg="white", 
                            command=eliminar_ui, width=6, font=("Segoe UI", 12))
    btn_importar = tk.Button(btns, text="📥", bg="#2E7D32", fg="white", 
                            command=lambda: mostrar_formato_excel(lambda: importar_excel(refresh)), 
                            width=6, font=("Segoe UI", 12))
    btn_back = tk.Button(btns, text="🔙", bg="#607D8B", fg="white", 
                        command=root.destroy, width=6, font=("Segoe UI", 12))

    btn_agregar.grid(row=0, column=0, padx=8)
    btn_editar.grid(row=0, column=1, padx=8)
    btn_guardar.grid(row=0, column=2, padx=8)
    btn_eliminar.grid(row=0, column=3, padx=8)
    btn_importar.grid(row=0, column=4, padx=8)
    btn_back.grid(row=0, column=5, padx=8)

    # Asignar tooltips a los botones
    ToolTip(btn_agregar, "Agregar materia")
    ToolTip(btn_editar, "Editar materia seleccionada")
    ToolTip(btn_guardar, "Guardar cambios")
    ToolTip(btn_eliminar, "Eliminar materia seleccionada")
    ToolTip(btn_importar, "Importar desde Excel")
    ToolTip(btn_back, "Volver")

    # Configurar evento de doble clic en la tabla para editar
    def on_double_click(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            editar_ui()
    
    tree.bind("<Double-1>", on_double_click)
    
    # Inicializar formulario
    limpiar_form()
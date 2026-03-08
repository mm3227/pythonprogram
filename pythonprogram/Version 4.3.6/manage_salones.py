# manage_salones.py - Gestor de Salones (UI moderna y estable)
import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, filedialog
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
DB = os.path.join(RUTA_BASEDATOS,"salones.db")

# ==================================================
# DB
# ==================================================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS salones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edificio TEXT NOT NULL,
            salon TEXT NOT NULL,
            capacidad INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ==================================================
# CRUD
# ==================================================
def listar_salones():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, edificio, salon, capacidad FROM salones ORDER BY edificio, salon")
    rows = c.fetchall()
    conn.close()
    return rows

def agregar_salon(edificio, salon, capacidad):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO salones (edificio, salon, capacidad) VALUES (?, ?, ?)",
        (edificio, salon, capacidad)
    )
    conn.commit()
    conn.close()

def actualizar_salon(sid, edificio, salon, capacidad):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "UPDATE salones SET edificio=?, salon=?, capacidad=? WHERE id=?",
        (edificio, salon, capacidad, sid)
    )
    conn.commit()
    conn.close()

def borrar_salon(sid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM salones WHERE id=?", (sid,))
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
# IMPORTAR EXCEL
# ==================================================
def importar_excel(refresh_cb):
    try:
        import pandas as pd
    except ImportError:
        # Corregido: usar None en lugar de root (no definido)
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

    if not all(c in columnas for c in ("edificio", "salon", "capacidad")):
        mostrar_aviso(None, "Formato incorrecto",
            "El Excel debe tener las columnas:\n\nedificio | salon | capacidad")
        return

    errores = 0
    for _, fila in df.iterrows():
        edificio = str(fila["edificio"]).strip()
        salon = str(fila["salon"]).strip()
        capacidad = str(fila["capacidad"]).strip()
        if not edificio or not salon or not capacidad.isdigit():
            errores += 1
            continue
        agregar_salon(edificio, salon, int(capacidad))

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
    win.title("Formato Excel - Salones")
    win.geometry("420x300")
    win.resizable(False, False)
    win.grab_set()

    frame = tk.Frame(win, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="Formato requerido del Excel",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=6)

    tabla = ttk.Treeview(
        frame,
        columns=("edificio", "salon", "capacidad"),
        show="headings",
        height=3
    )
    for col in ("edificio", "salon", "capacidad"):
        tabla.heading(col, text=col.capitalize())
        tabla.column(col, width=120, anchor="center")

    tabla.insert("", "end", values=("A", "101", "30"))
    tabla.insert("", "end", values=("B", "204", "45"))
    tabla.pack(pady=6)

    tk.Label(
        frame,
        text="• Columnas exactas\n• Archivo .xlsx",
        fg="#555555",
        justify="left"
    ).pack(pady=4)

    btns = tk.Frame(frame)
    btns.pack(side="bottom", pady=10)

    tk.Button(btns, text="Cancelar", width=10, command=win.destroy).grid(row=0, column=0, padx=6)
    tk.Button(btns, text="Continuar", width=10, bg="#2E7D32", fg="white",
              command=lambda: (win.destroy(), continuar_cb())).grid(row=0, column=1, padx=6)

# ==================================================
# UI
# ==================================================
def abrir_salones():
    init_db()
    salon_editando_id = {"id": None}

    root = tk.Toplevel()
    root.title("Gestor de Salones")
    root.geometry("850x580")
    root.configure(bg="#f0f5ff")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=26)

    main = tk.Frame(root, bg="#f0f5ff", padx=10, pady=10)
    main.pack(fill="both", expand=True)

    header = tk.Frame(main, bg="#4a6fa5", height=55)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="Gestión de Salones", bg="#4a6fa5",
             fg="white", font=("Segoe UI", 18, "bold")).pack(expand=True)

    # TABLA
    tree = ttk.Treeview(main, columns=("id", "edificio", "salon", "capacidad"), show="headings")
    tree.heading("edificio", text="Edificio")
    tree.heading("salon", text="Salón")
    tree.heading("capacidad", text="Capacidad")

    tree.column("id", width=0, stretch=False)
    tree.column("edificio", width=200)
    tree.column("salon", width=200, anchor="center")
    tree.column("capacidad", width=120, anchor="center")

    tree.pack(fill="both", expand=True, pady=6)

    def refresh():
        tree.delete(*tree.get_children())
        for r in listar_salones():
            tree.insert("", "end", values=r)

    refresh()

    # FORMULARIO
    form = tk.LabelFrame(main, text="Datos del Salón", bg="#f0f5ff")
    form.pack(fill="x", pady=6)

    tk.Label(form, text="Edificio:", bg="#f0f5ff").grid(row=0, column=0, padx=6, pady=6)
    ent_ed = ttk.Entry(form, width=20)
    ent_ed.grid(row=0, column=1, padx=6)

    tk.Label(form, text="Salón:", bg="#f0f5ff").grid(row=0, column=2, padx=6)
    ent_sa = ttk.Entry(form, width=20)
    ent_sa.grid(row=0, column=3, padx=6)

    tk.Label(form, text="Capacidad:", bg="#f0f5ff").grid(row=1, column=0, padx=6)
    ent_ca = ttk.Entry(form, width=10)
    ent_ca.grid(row=1, column=1, padx=6, sticky="w")

    # FUNCIONES
    def limpiar_form():
        for e in (ent_ed, ent_sa, ent_ca):
            e.delete(0, tk.END)
        salon_editando_id["id"] = None
        btn_guardar.config(state="disabled")
        btn_agregar.config(state="normal")
        ent_ed.focus()

    def agregar_ui():
        edificio = ent_ed.get().strip()
        salon = ent_sa.get().strip()
        capacidad = ent_ca.get().strip()
        
        if not edificio or not salon:
            mostrar_aviso(root, "Aviso", "El edificio y salón son obligatorios")
            return
            
        if not capacidad.isdigit():
            mostrar_aviso(root, "Aviso", "La capacidad debe ser un número entero")
            return
            
        try:
            agregar_salon(edificio, salon, int(capacidad))
            mostrar_info(root, "Éxito", "Salón agregado correctamente")
            limpiar_form()
            refresh()
        except Exception as e:
            mostrar_aviso(root, "Error", f"Error al agregar: {str(e)}")

    def editar_ui():
        sel = tree.selection()
        if not sel:
            mostrar_aviso(root, "Aviso", "Selecciona un salón")
            return
            
        valores = tree.item(sel[0])["values"]
        salon_editando_id["id"] = valores[0]
        
        # Limpiar campos primero
        ent_ed.delete(0, tk.END)
        ent_sa.delete(0, tk.END)
        ent_ca.delete(0, tk.END)
        
        # Llenar con valores actuales
        ent_ed.insert(0, valores[1])
        ent_sa.insert(0, valores[2])
        ent_ca.insert(0, valores[3])
        
        # Cambiar estados de botones
        btn_agregar.config(state="disabled")
        btn_guardar.config(state="normal")
        
        # Enfocar el primer campo
        ent_ed.focus()

    def guardar_ui():
        sid = salon_editando_id["id"]
        if sid is None:
            mostrar_aviso(root, "Aviso", "No hay salón seleccionado para editar")
            return
            
        edificio = ent_ed.get().strip()
        salon = ent_sa.get().strip()
        capacidad = ent_ca.get().strip()
        
        if not edificio or not salon:
            mostrar_aviso(root, "Aviso", "El edificio y salón son obligatorios")
            return
            
        if not capacidad.isdigit():
            mostrar_aviso(root, "Aviso", "La capacidad debe ser un número entero")
            return
            
        try:
            actualizar_salon(sid, edificio, salon, int(capacidad))
            mostrar_info(root, "Éxito", "Salón actualizado correctamente")
            limpiar_form()
            refresh()
        except Exception as e:
            mostrar_aviso(root, "Error", f"Error al actualizar: {str(e)}")

    def eliminar_ui():
        sel = tree.selection()
        if not sel:
            mostrar_aviso(root, "Aviso", "Selecciona un salón")
            return
            
        sid = tree.item(sel[0])["values"][0]
        edificio = tree.item(sel[0])["values"][1]
        salon = tree.item(sel[0])["values"][2]
        
        def confirmar_eliminar():
            try:
                borrar_salon(sid)
                mostrar_info(root, "Éxito", f"Salón '{edificio}-{salon}' eliminado correctamente")
                refresh()
            except Exception as e:
                mostrar_aviso(root, "Error", f"Error al eliminar: {str(e)}")
        
        mostrar_confirmacion(
            root, 
            "Confirmar eliminación", 
            f"¿Eliminar el salón '{edificio}-{salon}'?", 
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
    ToolTip(btn_agregar, "Agregar salón")
    ToolTip(btn_editar, "Editar salón seleccionado")
    ToolTip(btn_guardar, "Guardar cambios")
    ToolTip(btn_eliminar, "Eliminar salón seleccionado")
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
# manage_programas.py - Gestor de Programas Académicos (estilo unificado)
import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk
from config import RUTA_BASEDATOS

# =====================================================
# CLASE ToolTip (para mostrar ayuda al pasar el mouse)
# =====================================================
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

# =====================================================
# RUTAS
# =====================================================

DB = os.path.join(RUTA_BASEDATOS,"programas.db")

# =====================================================
# BASE DE DATOS
# =====================================================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS programas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            clave TEXT,
            descripcion TEXT,
            activo INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

def listar_programas():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT id, nombre, clave, descripcion, activo
        FROM programas
        ORDER BY nombre
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def agregar_programa(nombre, clave, descripcion, activo):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO programas (nombre, clave, descripcion, activo)
        VALUES (?, ?, ?, ?)
    """, (nombre, clave, descripcion, activo))
    conn.commit()
    conn.close()

def actualizar_programa(pid, nombre, clave, descripcion, activo):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        UPDATE programas
        SET nombre=?, clave=?, descripcion=?, activo=?
        WHERE id=?
    """, (nombre, clave, descripcion, activo, pid))
    conn.commit()
    conn.close()

def eliminar_programa(pid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM programas WHERE id=?", (pid,))
    conn.commit()
    conn.close()

# =====================================================
# FUNCIONES PARA MOSTRAR VENTANAS DE DIÁLOGO
# =====================================================
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

# =====================================================
# VENTANA EDITAR
# =====================================================
def ventana_editar(root, pid, valores, refresh):
    win = tk.Toplevel(root)
    win.title("Editar Programa Académico")
    win.geometry("500x320")
    win.resizable(False, False)
    win.grab_set()

    ttk.Label(win, text="Nombre del Programa:").pack(pady=4)
    ent_nombre = ttk.Entry(win)
    ent_nombre.pack(fill="x", padx=20)
    ent_nombre.insert(0, valores[1])

    ttk.Label(win, text="Clave:").pack(pady=4)
    ent_clave = ttk.Entry(win)
    ent_clave.pack(fill="x", padx=20)
    ent_clave.insert(0, valores[2])

    ttk.Label(win, text="Descripción:").pack(pady=4)
    ent_desc = tk.Text(win, height=4)
    ent_desc.pack(fill="x", padx=20)
    ent_desc.insert("1.0", valores[3])

    ttk.Label(win, text="Estado:").pack(pady=4)
    cmb_estado = ttk.Combobox(
        win, state="readonly",
        values=["Activo", "Inactivo"]
    )
    cmb_estado.pack(padx=20)
    cmb_estado.set("Activo" if valores[4] == "Activo" else "Inactivo")

    def guardar():
        if not ent_nombre.get().strip():
            mostrar_aviso(win, "Dato requerido", "El nombre es obligatorio")
            return

        activo = 1 if cmb_estado.get() == "Activo" else 0

        try:
            actualizar_programa(
                pid,
                ent_nombre.get().strip(),
                ent_clave.get().strip(),
                ent_desc.get("1.0", "end").strip(),
                activo
            )
            mostrar_info(root, "Éxito", "Programa actualizado correctamente")
            refresh()
            win.destroy()
        except sqlite3.IntegrityError:
            mostrar_aviso(win, "Error", "Ya existe un programa con ese nombre")
        except Exception as e:
            mostrar_aviso(win, "Error", f"Error al actualizar: {str(e)}")

    btns_frame = tk.Frame(win)
    btns_frame.pack(pady=10)
    
    tk.Button(btns_frame, text="Guardar", bg="#4CAF50", fg="white", 
              command=guardar, width=12).pack(side="left", padx=5)
    tk.Button(btns_frame, text="Cancelar", bg="#757575", fg="white", 
              command=win.destroy, width=12).pack(side="left", padx=5)

# =====================================================
# INTERFAZ PRINCIPAL
# =====================================================
def abrir_programas():
    init_db()

    root = tk.Toplevel()
    root.title("Gestión de Programas Académicos")
    root.geometry("1000x650")
    root.configure(bg="#f0f5ff")

    # ================= HEADER =================
    header = tk.Frame(root, bg="#4f6fa3", height=55)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="Gestión de Programas Académicos",
        bg="#4f6fa3",
        fg="white",
        font=("Segoe UI", 18, "bold")
    ).pack(expand=True)

    # ================= ESTILO TABLA =================
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=26)

    main = tk.Frame(root, bg="#f0f5ff", padx=10, pady=10)
    main.pack(fill="both", expand=True)

    # ================= TABLA =================
    cols = ("id", "nombre", "clave", "descripcion", "activo")
    tree = ttk.Treeview(main, columns=cols, show="headings")

    tree.heading("nombre", text="Programa Académico")
    tree.heading("clave", text="Clave")
    tree.heading("descripcion", text="Descripción")
    tree.heading("activo", text="Estado")

    tree.column("id", width=0, stretch=False)
    tree.column("nombre", width=280)
    tree.column("clave", width=120)
    tree.column("descripcion", width=450)
    tree.column("activo", width=100, anchor="center")

    # Scrollbar para la tabla
    scrollbar = ttk.Scrollbar(main, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.grid(row=0, column=0, sticky="nsew", pady=10)
    scrollbar.grid(row=0, column=1, sticky="ns", pady=10)
    
    # Configurar expansión de la tabla
    main.grid_rowconfigure(0, weight=1)
    main.grid_columnconfigure(0, weight=1)

    def refresh():
        tree.delete(*tree.get_children())
        for p in listar_programas():
            estado = "Activo" if p[4] == 1 else "Inactivo"
            tree.insert("", "end", values=(p[0], p[1], p[2], p[3], estado))

    refresh()

    # ================= AGREGAR =================
    frm_add = tk.LabelFrame(main, text="Agregar Programa Académico", bg="#f0f5ff")
    frm_add.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 5))
    
    # Configurar columnas para el formulario
    frm_add.grid_columnconfigure(1, weight=1)
    frm_add.grid_columnconfigure(3, weight=1)
    frm_add.grid_columnconfigure(5, weight=1)

    tk.Label(frm_add, text="Nombre:", bg="#f0f5ff").grid(row=0, column=0, padx=6, pady=6, sticky="w")
    ent_nombre = ttk.Entry(frm_add, width=40)
    ent_nombre.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

    tk.Label(frm_add, text="Clave:", bg="#f0f5ff").grid(row=0, column=2, padx=6, pady=6, sticky="w")
    ent_clave = ttk.Entry(frm_add, width=15)
    ent_clave.grid(row=0, column=3, padx=6, pady=6, sticky="w")

    tk.Label(frm_add, text="Estado:", bg="#f0f5ff").grid(row=0, column=4, padx=6, pady=6, sticky="w")
    cmb_estado = ttk.Combobox(
        frm_add, state="readonly",
        values=["Activo", "Inactivo"], width=15
    )
    cmb_estado.grid(row=0, column=5, padx=6, pady=6, sticky="w")
    cmb_estado.set("Activo")

    tk.Label(frm_add, text="Descripción:", bg="#f0f5ff").grid(row=1, column=0, padx=6, pady=6, sticky="nw")
    ent_desc = tk.Text(frm_add, height=4, width=80)
    ent_desc.grid(row=1, column=1, columnspan=5, padx=6, pady=6, sticky="ew")

    def agregar():
        if not ent_nombre.get().strip():
            mostrar_aviso(root, "Dato requerido", "El nombre es obligatorio")
            return

        activo = 1 if cmb_estado.get() == "Activo" else 0

        try:
            agregar_programa(
                ent_nombre.get().strip(),
                ent_clave.get().strip(),
                ent_desc.get("1.0", "end").strip(),
                activo
            )
            mostrar_info(root, "Éxito", "Programa agregado correctamente")
            
            # Limpiar campos
            ent_nombre.delete(0, tk.END)
            ent_clave.delete(0, tk.END)
            ent_desc.delete("1.0", tk.END)
            cmb_estado.set("Activo")
            refresh()
        except sqlite3.IntegrityError:
            mostrar_aviso(root, "Error", "Ya existe un programa con ese nombre")
        except Exception as e:
            mostrar_aviso(root, "Error", f"Error al agregar: {str(e)}")

    # ================= BOTONES =================
    btns = tk.Frame(main, bg="#f0f5ff")
    btns.grid(row=2, column=0, columnspan=2, pady=(10, 0))

    def editar():
        sel = tree.selection()
        if not sel:
            mostrar_aviso(root, "Aviso", "Selecciona un programa")
            return
        valores = tree.item(sel[0])["values"]
        ventana_editar(root, valores[0], valores, refresh)

    def eliminar():
        sel = tree.selection()
        if not sel:
            mostrar_aviso(root, "Aviso", "Selecciona un programa")
            return
        pid = tree.item(sel[0])["values"][0]
        nombre = tree.item(sel[0])["values"][1]
        
        def confirmar_eliminar():
            try:
                eliminar_programa(pid)
                mostrar_info(root, "Éxito", f"Programa '{nombre}' eliminado correctamente")
                refresh()
            except Exception as e:
                mostrar_aviso(root, "Error", f"Error al eliminar: {str(e)}")
        
        mostrar_confirmacion(
            root, 
            "Confirmar eliminación", 
            f"¿Eliminar el programa '{nombre}'?", 
            confirmar_eliminar
        )

    # BOTONES CON EMOJIS (asignamos variable a cada botón para tooltips)
    btn_agregar = tk.Button(btns, text="➕", bg="#4CAF50", fg="white",
                            command=agregar, width=4, font=("Segoe UI", 12))
    btn_agregar.grid(row=0, column=0, padx=10)

    btn_editar = tk.Button(btns, text="✏", bg="#FF9800", fg="white",
                           command=editar, width=4, font=("Segoe UI", 12))
    btn_editar.grid(row=0, column=1, padx=10)

    btn_eliminar = tk.Button(btns, text="🗑", bg="#E53935", fg="white",
                             command=eliminar, width=4, font=("Segoe UI", 12))
    btn_eliminar.grid(row=0, column=2, padx=10)

    btn_volver = tk.Button(btns, text="🔙", bg="#607D8B", fg="white",
                           command=root.destroy, width=4, font=("Segoe UI", 12))
    btn_volver.grid(row=0, column=3, padx=10)

    # Asignar tooltips a los botones
    ToolTip(btn_agregar, "Agregar programa")
    ToolTip(btn_editar, "Editar programa seleccionado")
    ToolTip(btn_eliminar, "Eliminar programa seleccionado")
    ToolTip(btn_volver, "Volver")

    # Configurar evento de doble clic en la tabla para editar
    def on_double_click(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            editar()
    
    tree.bind("<Double-1>", on_double_click)

# =====================================================
# ENTRADA (opcional)
# =====================================================
"""def abrir_programas_main():
    app = tk.Tk()
    app.withdraw()
    abrir_programas()
    app.mainloop()"""
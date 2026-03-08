# manage_ciclo_escolar.py - Gestor de Ciclos Escolares (UI idéntica a la imagen con distribución modificada)
import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ==================================================
# RUTAS
# ==================================================
import os
from config import RUTA_BASEDATOS

BASE_DIR = RUTA_BASEDATOS
CICLOS_DIR = os.path.join(BASE_DIR, "ciclos")
os.makedirs(CICLOS_DIR, exist_ok=True)

HORARIOS_DIR = os.path.join(BASE_DIR, "horarios")
os.makedirs(HORARIOS_DIR, exist_ok=True)

# ==================================================
# CRUD CICLOS
# ==================================================
def listar_ciclos():
    ciclos = []
    for f in os.listdir(CICLOS_DIR):
        if f.lower().endswith(".db"):
            ciclos.append(f.replace('.db', ''))
    return sorted(ciclos)

def crear_ciclo(nombre, parent):
    if not nombre:
        messagebox.showwarning("Aviso", "El nombre es obligatorio", parent=parent)
        return False

    ruta_ciclo = os.path.join(CICLOS_DIR, f"{nombre}.db")

    if os.path.exists(ruta_ciclo):
        messagebox.showwarning("Aviso", "Ya existe un ciclo con ese nombre", parent=parent)
        return False

    # ============================================
    # CREAR BASE DEL CICLO (estructura mínima)
    # ============================================
    conn = sqlite3.connect(ruta_ciclo)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programa TEXT,
            semestre INTEGER,
            grupo TEXT,
            materias INTEGER,
            modalidad TEXT,
            alumnos INTEGER
        )
    """)

    conn.commit()
    conn.close()

    # ============================================
    # CREAR BASE DE HORARIOS ASOCIADA
    # ============================================
    ruta_horario = os.path.join(
        HORARIOS_DIR,
        f"{nombre}_horario.db"
    )

    conn_h = sqlite3.connect(ruta_horario)
    c_h = conn_h.cursor()

    c_h.execute("""
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

    conn_h.commit()
    conn_h.close()

    return True


def borrar_ciclo(nombre, parent):
    if not nombre:
        messagebox.showwarning("Aviso", "Selecciona un ciclo", parent=parent)
        return False
    ruta = os.path.join(CICLOS_DIR, f"{nombre}.db")
    if not os.path.exists(ruta):
        messagebox.showerror("Error", "No se encontró el archivo", parent=parent)
        return False
    if messagebox.askyesno("Confirmar", f"¿Eliminar ciclo {nombre}?", parent=parent):
        os.remove(ruta)
        return True
    return False

def editar_ciclo(nombre_actual, nuevo_nombre, parent):
    if not nombre_actual:
        messagebox.showwarning("Aviso", "Selecciona un ciclo", parent=parent)
        return False
    if not nuevo_nombre:
        messagebox.showwarning("Aviso", "El nuevo nombre es obligatorio", parent=parent)
        return False
    ruta_actual = os.path.join(CICLOS_DIR, f"{nombre_actual}.db")
    ruta_nueva = os.path.join(CICLOS_DIR, f"{nuevo_nombre}.db")
    if os.path.exists(ruta_nueva):
        messagebox.showwarning("Aviso", "Ya existe un ciclo con ese nombre", parent=parent)
        return False
    os.rename(ruta_actual, ruta_nueva)
    return True

# ==================================================
# UI CON DISTRIBUCIÓN CORREGIDA
# ==================================================
def abrir_ciclo_escolar():
    root = tk.Toplevel()
    root.title("Gestión de Ciclos Escolares")
    root.geometry("800x600")
    root.configure(bg="#f5f5f5")
    root.resizable(False, False)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'800x600+{x}+{y}')

    # TÍTULO SUPERIOR
    title_frame = tk.Frame(root, bg="#2196F3", height=60)
    title_frame.pack(fill="x")
    title_frame.pack_propagate(False)
    
    tk.Label(title_frame, text="Gestión de Ciclos Escolares", 
             font=("Arial", 16, "bold"), bg="#2196F3", fg="white").pack(pady=18)

    # CONTENIDO PRINCIPAL CON DOS COLUMNAS
    main_frame = tk.Frame(root, bg="#f5f5f5")
    main_frame.pack(fill="both", expand=True, padx=30, pady=20)

    # COLUMNA IZQUIERDA - Lista de ciclos
    left_frame = tk.Frame(main_frame, bg="#f5f5f5")
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

    # Subtítulo "Ciclos Disponibles"
    tk.Label(left_frame, text="Ciclos Disponibles", 
             font=("Arial", 12, "bold"), bg="#f5f5f5", fg="#333333").pack(anchor="w", pady=(0, 10))

    # MARCO DOBLE para la lista de ciclos
    # Marco exterior (primera línea del doble marco)
    outer_frame = tk.Frame(left_frame, bg="#999999", relief="flat", borderwidth=2)
    outer_frame.pack(fill="both", expand=True)
    
    # Marco interior (segunda línea del doble marco)
    inner_frame = tk.Frame(outer_frame, bg="#666666", relief="flat", borderwidth=1)
    inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
    
    # Frame principal para la lista dentro del doble marco
    list_frame = tk.Frame(inner_frame, bg="white", relief="flat")
    list_frame.pack(fill="both", expand=True, padx=1, pady=1)

    # Canvas para scrollbar
    canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    cycles_frame = tk.Frame(canvas, bg="white")

    cycles_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=cycles_frame, anchor="nw", width=400)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Variable para ciclo seleccionado
    selected_cycle = tk.StringVar()
    cycle_buttons = []  # Para guardar referencias de los botones de ciclo

    def refresh():
        # Limpiar frame existente
        for widget in cycles_frame.winfo_children():
            widget.destroy()
        cycle_buttons.clear()
        
        # Obtener ciclos
        ciclos = listar_ciclos()
        
        if not ciclos:
            # Mostrar mensaje si no hay ciclos
            empty_label = tk.Label(cycles_frame, text="No hay ciclos escolares creados", 
                                  font=("Arial", 10), bg="white", fg="#666666")
            empty_label.pack(pady=50)
        else:
            for ciclo in ciclos:
                # Crear un botón para cada ciclo (como en la imagen)
                cycle_btn = tk.Button(cycles_frame, 
                                     text=ciclo,
                                     font=("Arial", 11, "bold"),
                                     bg="#E3F2FD",  # Azul claro
                                     fg="#1565C0",  # Azul oscuro
                                     relief="flat",
                                     width=35,
                                     height=1,
                                     anchor="center",
                                     padx=10,
                                     pady=12,
                                     cursor="hand2")
                
                # Configurar el comando para seleccionar
                def make_command(c=ciclo):
                    return lambda: select_cycle(c)
                
                cycle_btn.config(command=make_command())
                cycle_btn.pack(pady=8, padx=10, fill="x")
                cycle_buttons.append((cycle_btn, ciclo))

    def select_cycle(cycle_name):
        selected_cycle.set(cycle_name)
        # Resaltar el botón seleccionado
        for btn, ciclo in cycle_buttons:
            if ciclo == cycle_name:
                btn.config(bg="#2196F3", fg="white")  # Resaltado azul
            else:
                btn.config(bg="#E3F2FD", fg="#1565C0")  # Normal

    # COLUMNA DERECHA - Botones con emojis
    right_frame = tk.Frame(main_frame, bg="#f5f5f5")
    right_frame.pack(side="right", fill="y", padx=(20, 0))

    # Espacio en la parte superior para alinear visualmente
    tk.Frame(right_frame, height=40, bg="#f5f5f5").pack()

    # Funciones para botones
    def crear_nuevo_ciclo():
        nombre = simpledialog.askstring("Crear Nuevo Ciclo", 
                                        "Nombre del ciclo escolar:", 
                                        parent=root)
        if nombre and crear_ciclo(nombre, root):
            refresh()

    def abrir_ciclo():
        ciclo = selected_cycle.get()
        if not ciclo:
            messagebox.showwarning("Aviso", "Seleccione un ciclo para abrir", parent=root)
            return
        
        ruta = os.path.join(CICLOS_DIR, f"{ciclo}.db")
        if not os.path.exists(ruta):
            messagebox.showerror("Error", "Archivo no encontrado", parent=root)
            return

        # Cerrar esta ventana y abrir core/main_ciclo.py
        root.destroy()
        try:
            import core.main_ciclo as main_ciclo
            main_ciclo.abrir_ciclo(ruta)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_ciclo():
        ciclo = selected_cycle.get()
        if not ciclo:
            messagebox.showwarning("Aviso", "Seleccione un ciclo para eliminar", parent=root)
            return
        
        if borrar_ciclo(ciclo, root):
            selected_cycle.set("")
            refresh()

    def actualizar_ciclo():
        refresh()
        messagebox.showinfo("Actualizado", "Lista de ciclos actualizada", parent=root)

    # Crear botones con emojis como en tu código original
    botones_data = [
        ("➕", "Crear Nuevo Ciclo", "#4CAF50", crear_nuevo_ciclo),
        ("📂", "Abrir Ciclo", "#2196F3", abrir_ciclo),
        ("❌", "Eliminar Ciclo", "#F44336", eliminar_ciclo),
        ("🔄", "Actualizar", "#FF9800", actualizar_ciclo),
        ("🔙", "Cerrar", "#607D8B", root.destroy)
    ]

    for emoji, texto, color, comando in botones_data:
        # Frame para cada botón
        btn_frame = tk.Frame(right_frame, bg="#f5f5f5")
        btn_frame.pack(pady=8, fill="x")
        
        # Botón con emoji grande
        btn = tk.Button(btn_frame,
                       text=emoji,
                       font=("Segoe UI Emoji", 16),
                       bg=color,
                       fg="white",
                       relief="flat",
                       width=4,
                       height=1,
                       cursor="hand2",
                       command=comando)
        btn.pack(side="left", padx=(0, 10))
        
        # Etiqueta con el texto
        tk.Label(btn_frame,
                text=texto,
                font=("Arial", 10, "bold"),
                bg="#f5f5f5",
                fg="#333333").pack(side="left", anchor="w")
        
        # Efecto hover para el botón
        def on_enter(e, b=btn, c=color):
            b.config(relief="raised")
        
        def on_leave(e, b=btn, c=color):
            b.config(relief="flat")
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # Configurar el canvas y scrollbar en la columna izquierda
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    
    # Configurar scroll con rueda del mouse (CORREGIDO)
    def on_mouse_wheel(event):
        try:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except tk.TclError:
            # El canvas ya no existe, se ignora el error
            pass

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # Función para manejar el cierre correctamente
    def on_closing():
        try:
            canvas.unbind_all("<MouseWheel>")
        except:
            pass
        root.destroy()

    # Configurar el protocolo de cierre
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Asegurar que los frames se expandan correctamente
    main_frame.pack_propagate(False)
    left_frame.pack_propagate(False)
    right_frame.pack_propagate(False)

    # Establecer tamaños mínimos
    left_frame.config(width=450)
    right_frame.config(width=250)

    # Cargar ciclos iniciales
    refresh()

    root.mainloop()

"""# Para probar directamente
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    abrir_ciclo_escolar()"""
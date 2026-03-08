# main.py - Gestor de Horarios 4.3 (estable y corregido)
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from config import BASE_DIR, resource_path


# ==============================
#   BOTONES
# ==============================
def abrir_profesores():
    import manage_profesores
    manage_profesores.abrir_profesores()

def abrir_materias():
    import manage_materias
    manage_materias.abrir_materias()

def abrir_salones():
    import manage_salones
    manage_salones.abrir_salones()

def abrir_programas():
    import manage_programas
    manage_programas.abrir_programas()

def abrir_ciclo_escolar():
    import manage_ciclo_escolar
    manage_ciclo_escolar.abrir_ciclo_escolar()

def mostrar_info():
    messagebox.showinfo(
        "Información del Sistema",
        "Programa en fase de pruebas\n"f"Directorio base:\n{BASE_DIR}\n\n¿Ejecutable?: {getattr(sys,'frozen',False)},\n Si detecta algun fallo comunicarse con:\n mmolina@uaz.edu.mx"
    )

def salir():
    root.destroy()

# ==============================
#   SPLASH
# ==============================
def mostrar_pantalla_inicio():
    for w in root.winfo_children():
        w.destroy()

    root.title("Universidad Autónoma de Zacatecas")
    root.geometry("1000x760")
    root.configure(bg="#002a5c")

    try:
        from PIL import Image, ImageTk
        try:
            img = Image.open(resource_path("logo.jpg")).resize((300, 300))
        except Exception:
            img = Image.open(resource_path("centro.png")).resize((300, 300))
        logo = ImageTk.PhotoImage(img)
        lbl = tk.Label(root, image=logo, bg="#002a5c")
        lbl.image = logo
        lbl.pack(pady=40)
    except Exception:
        tk.Label(root, text="UAZ",
                 font=("Segoe UI", 36, "bold"),
                 fg="white", bg="#002a5c").pack(pady=40)

    tk.Label(root, text="Universidad Autónoma de Zacatecas",
             font=("Segoe UI", 28, "bold"),
             fg="white", bg="#002a5c").pack()

    tk.Label(root, text="Gestor Académico de Horarios",
             font=("Segoe UI", 22),
             fg="white", bg="#002a5c").pack(pady=40)

    # Botón mejorado con gradiente simulado
    btn_frame = tk.Frame(root, bg="#002a5c")
    btn_frame.pack()
    
    btn = tk.Button(
        btn_frame, text="CONTINUAR",
        command=mostrar_ventana_principal,
        font=("Segoe UI", 20, "bold"),
        bg="#2E7D32", fg="white",
        activebackground="#1B5E20", activeforeground="white",
        relief="raised", bd=4,
        width=15, height=2,
        cursor="hand2",
        padx=20, pady=10
    )
    
    # Aplicar efectos visuales
    btn.config(
        highlightbackground="#4CAF50",
        highlightcolor="#4CAF50",
        highlightthickness=2
    )
    btn.pack()
    
    # Efecto hover
    def on_enter(e):
        btn.config(bg="#1B5E20", relief="sunken")
    
    def on_leave(e):
        btn.config(bg="#2E7D32", relief="raised")
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    tk.Label(root,
             text="Versión 4.3.6 - Sistema de Gestión Escolar",
             font=("Segoe UI", 10),
             fg="#ccc", bg="#002a5c").pack(side="bottom", pady=20)

# ==============================
#   FUNCIONES PARA BOTONES MEJORADOS
# ==============================
def create_modern_button(parent, text, command, color1, color2, icon=None):
    """Crea un botón moderno con efecto de gradiente y hover"""
    btn_frame = tk.Frame(parent, bg="#f2f4f8")
    
    # Frame principal del botón con borde redondeado
    main_btn = tk.Frame(btn_frame, bg=color1, bd=0, relief="flat", 
                       highlightbackground="#cccccc", highlightthickness=1)
    
    # Efecto de gradiente (simulado con dos frames)
    gradient_frame = tk.Frame(main_btn, bg=color1, height=2)
    gradient_frame.pack(fill="x", side="top")
    
    # Botón interior
    inner_btn = tk.Button(
        main_btn, text=text,
        command=command,
        font=("Segoe UI", 11, "bold"),
        bg=color1, fg="white",
        activebackground=color2, activeforeground="white",
        relief="flat", bd=0,
        cursor="hand2",
        padx=30, pady=15
    )
    inner_btn.pack(fill="both", expand=True)
    
    # Icono si se proporciona
    if icon:
        icon_label = tk.Label(main_btn, text=icon, font=("Segoe UI", 16), 
                             bg=color1, fg="white")
        icon_label.place(x=20, y=20)
    
    # Efectos hover
    def on_enter(e):
        main_btn.config(bg=color2)
        inner_btn.config(bg=color2)
        gradient_frame.config(bg=color2)
        if icon:
            icon_label.config(bg=color2)
    
    def on_leave(e):
        main_btn.config(bg=color1)
        inner_btn.config(bg=color1)
        gradient_frame.config(bg=color1)
        if icon:
            icon_label.config(bg=color1)
    
    def on_press(e):
        main_btn.config(relief="sunken")
    
    def on_release(e):
        main_btn.config(relief="flat")
    
    inner_btn.bind("<Enter>", on_enter)
    inner_btn.bind("<Leave>", on_leave)
    inner_btn.bind("<ButtonPress-1>", on_press)
    inner_btn.bind("<ButtonRelease-1>", on_release)
    
    main_btn.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Sombra inferior
    shadow = tk.Frame(btn_frame, height=3, bg=color2)
    shadow.pack(fill="x", padx=5)
    
    return btn_frame

def create_circle_button(parent, text, command, color1, color2):
    """Crea un botón circular moderno"""
    btn_frame = tk.Frame(parent, bg="#f2f4f8")
    
    # Botón circular principal
    btn_canvas = tk.Canvas(btn_frame, width=80, height=80, 
                          bg="#f2f4f8", highlightthickness=0)
    btn_canvas.pack()
    
    # Círculo exterior
    circle = btn_canvas.create_oval(5, 5, 75, 75, fill=color1, outline="", width=0)
    
    # Texto en el centro
    text_id = btn_canvas.create_text(40, 40, text=text, fill="white", 
                                    font=("Segoe UI", 16, "bold"))
    
    # Efectos hover
    def on_enter(e):
        btn_canvas.itemconfig(circle, fill=color2)
    
    def on_leave(e):
        btn_canvas.itemconfig(circle, fill=color1)
    
    def on_click(e):
        command()
    
    btn_canvas.bind("<Enter>", on_enter)
    btn_canvas.bind("<Leave>", on_leave)
    btn_canvas.bind("<Button-1>", on_click)
    
    # Sombra
    shadow = tk.Frame(btn_frame, width=80, height=5, bg=color2)
    shadow.pack()
    
    return btn_frame

# ==============================
#   VENTANA PRINCIPAL
# ==============================
def mostrar_ventana_principal():
    for w in root.winfo_children():
        w.destroy()

    root.title("Gestor de Horarios 4.3.6")
    root.configure(bg="#f2f4f8")

    # -------- LOGO --------
    try:
        from PIL import Image, ImageTk
        try:
            img = Image.open(resource_path("logo.jpg")).resize((200, 200))
        except Exception:
            img = Image.open(resource_path("centro.png")).resize((200, 200))
        logo = ImageTk.PhotoImage(img)
        lbl = tk.Label(root, image=logo, bg="#f2f4f8")
        lbl.image = logo
        lbl.pack(pady=20)
    except Exception:
        pass

    tk.Label(root, text="Sistema de Gestión Académica",
             font=("Segoe UI", 20, "bold"),
             bg="#f2f4f8").pack()

    tk.Label(root, text="Unidad Académica de Ingeniería Eléctrica",
             font=("Segoe UI", 14),
             fg="#555", bg="#f2f4f8").pack(pady=(0, 30))

    # ==============================
    #   BOTONES MEJORADOS
    # ==============================
    
    # Contenedor principal para botones
    main_container = tk.Frame(root, bg="#f2f4f8")
    main_container.pack(expand=True, fill="both", padx=20, pady=10)
    
    # Primera fila de botones
    row1 = tk.Frame(main_container, bg="#f2f4f8")
    row1.pack(fill="x", pady=10)
    
    # Botón Profesores
    btn_profesores = create_modern_button(
        row1, "Profesores", abrir_profesores, 
        "#8E44AD", "#6C3483", "👨‍🏫"
    )
    btn_profesores.pack(side="left", expand=True, fill="both", padx=10)
    
    # Botón Materias
    btn_materias = create_modern_button(
        row1, "Materias", abrir_materias,
        "#E67E22", "#D35400", "📚"
    )
    btn_materias.pack(side="left", expand=True, fill="both", padx=10)
    
    # Botón Salones
    btn_salones = create_modern_button(
        row1, "Salones", abrir_salones,
        "#2980B9", "#1F618D", "🏫"
    )
    btn_salones.pack(side="left", expand=True, fill="both", padx=10)
    
    # Segunda fila de botones (más anchos)
    row2 = tk.Frame(main_container, bg="#f2f4f8")
    row2.pack(fill="x", pady=20)
    
    # Botón Programas Académicos
    btn_programas = create_modern_button(
        row2, "Programas Académicos", abrir_programas,
        "#F1C40F", "#D4AC0D", "🎓"
    )
    btn_programas.pack(side="left", expand=True, fill="both", padx=10)
    
    # Botón Ciclo Escolar
    btn_ciclo = create_modern_button(
        row2, "Ciclo Escolar", abrir_ciclo_escolar,
        "#1ABC9C", "#16A085", "📅"
    )
    btn_ciclo.pack(side="left", expand=True, fill="both", padx=10)
    
    # Tercera fila (botones circulares)
    row3 = tk.Frame(main_container, bg="#f2f4f8")
    row3.pack(pady=30)
    
    # Contenedor para centrar los botones circulares
    center_container = tk.Frame(row3, bg="#f2f4f8")
    center_container.pack()
    
    # Botón Información (circular)
    btn_info = create_circle_button(
        center_container, "ⓘ", mostrar_info,
        "#2ECC71", "#27AE60"
    )
    btn_info.pack(side="left", padx=40)
    
    # Botón Salir (circular)
    btn_salir = create_circle_button(
        center_container, "⏻", salir,
        "#E74C3C", "#C0392B"
    )
    btn_salir.pack(side="left", padx=40)

    # FOOTER
    tk.Label(
        root,
        text="Versión 4.3.6 - Sistema de Gestión Escolar - Autor: MMA",
        font=("Segoe UI", 9),
        fg="gray",
        bg="#f2f4f8"
    ).pack(side="bottom", pady=7)

# ==============================
#   MAIN
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    
    # Establecer estilo moderno
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configurar la ventana principal
    root.title("Gestor de Horarios 4.3.6")
    
    # Centrar ventana en pantalla
    window_width = 1200
    window_height = 900
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Icono de la ventana (si existe)
    try:
        root.iconbitmap(resource_path("logo.ico"))
    except:
        pass
    
    mostrar_pantalla_inicio()
    root.mainloop()

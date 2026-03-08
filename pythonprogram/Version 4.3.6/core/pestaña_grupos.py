# core/pestaña_grupos.py - Control de grupos escolares por programa académico
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ==================================================
# TOOLTIP (clase para mostrar ayuda contextual)
# ==================================================
class ToolTip:
    """Muestra un tooltip al pasar el mouse sobre un widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        widget.bind('<Enter>', self.enter)
        widget.bind('<Leave>', self.leave)
        widget.bind('<Motion>', self.motion)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def motion(self, event):
        self.x = event.x_root + 20
        self.y = event.y_root + 10

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self):
        if self.tip_window or not self.text:
            return
        x = self.x
        y = self.y
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", "10", "normal"))
        label.pack()

    def hidetip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ==================================================
# DB
# ==================================================
def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programa TEXT NOT NULL,
            semestre INTEGER NOT NULL,
            grupo TEXT NOT NULL,
            modalidad TEXT NOT NULL,
            materias INTEGER NOT NULL,
            alumnos INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ==================================================
# CARGAR PESTAÑA
# ==================================================
def cargar_pestana_grupos(frame, db_path, programa_actual):
    init_db(db_path)

    # ==============================
    # ESTILOS (EXCEL)
    # ==============================
    style = ttk.Style()
    style.configure(
        "Treeview.Heading",
        background="#1976D2",
        foreground="white",
        font=("Segoe UI", 11, "bold")
    )
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
    style.map("Treeview", background=[("selected", "#BBDEFB")])

    # ==============================
    # CONTENEDOR
    # ==============================
    cont = tk.Frame(frame, bg="#f2f4f8", padx=15, pady=15)
    cont.pack(fill="both", expand=True)

    tk.Label(
        cont,
        text=f"Grupos – {programa_actual}",
        font=("Segoe UI", 16, "bold"),
        bg="#f2f4f8"
    ).pack(anchor="w", pady=(0, 10))

    # ==============================
    # TABLA
    # ==============================
    tabla_frame = tk.Frame(cont, bg="#f2f4f8")
    tabla_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(
        tabla_frame,
        columns=("id", "semestre", "grupo", "modalidad", "materias", "alumnos"),
        show="headings"
    )

    tree.heading("semestre", text="Semestre")
    tree.heading("grupo", text="Grupo")
    tree.heading("modalidad", text="Modalidad")
    tree.heading("materias", text="Materias")
    tree.heading("alumnos", text="Alumnos")

    tree.column("id", width=0, stretch=False)
    tree.column("semestre", width=90, anchor="center")
    tree.column("grupo", width=90, anchor="center")
    tree.column("modalidad", width=150, anchor="center")
    tree.column("materias", width=90, anchor="center")
    tree.column("alumnos", width=90, anchor="center")

    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # ==============================
    # DB HELPERS
    # ==============================
    def cargar_grupos():
        tree.delete(*tree.get_children())
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            SELECT id, semestre, grupo, modalidad, materias, alumnos
            FROM grupos
            WHERE programa = ?
            ORDER BY semestre, grupo
        """, (programa_actual,))
        for r in c.fetchall():
            tree.insert("", "end", values=r)
        conn.close()

    cargar_grupos()

    # ==============================
    # FORMULARIO
    # ==============================
    form = tk.LabelFrame(
        cont,
        text="Datos del grupo",
        font=("Segoe UI", 11, "bold"),
        bg="#f2f4f8",
        padx=10,
        pady=10
    )
    form.pack(fill="x", pady=12)

    ttk.Label(form, text="Semestre:").grid(row=0, column=0, padx=8)
    ent_sem = ttk.Entry(form, width=8)
    ent_sem.grid(row=0, column=1, padx=8)

    ttk.Label(form, text="Grupo:").grid(row=0, column=2, padx=8)
    ent_gru = ttk.Entry(form, width=8)
    ent_gru.grid(row=0, column=3, padx=8)

    ttk.Label(form, text="Modalidad:").grid(row=0, column=4, padx=8)
    cmb_mod = ttk.Combobox(
        form,
        values=["Escolarizado", "Semiescolarizado"],
        state="readonly",
        width=16
    )
    cmb_mod.grid(row=0, column=5, padx=8)
    cmb_mod.set("Escolarizado")

    ttk.Label(form, text="Materias:").grid(row=0, column=6, padx=8)
    ent_mat = ttk.Entry(form, width=8)
    ent_mat.grid(row=0, column=7, padx=8)

    ttk.Label(form, text="Alumnos:").grid(row=0, column=8, padx=8)
    ent_alu = ttk.Entry(form, width=8)
    ent_alu.grid(row=0, column=9, padx=8)

    grupo_editando = {"id": None}

    def limpiar():
        for e in (ent_sem, ent_gru, ent_mat, ent_alu):
            e.delete(0, "end")
        cmb_mod.set("Escolarizado")
        grupo_editando["id"] = None
        btn_guardar.config(state="disabled")
        btn_agregar.config(state="normal")

    # ==============================
    # CRUD
    # ==============================
    def agregar():
        if not all([
            ent_sem.get().isdigit(),
            ent_mat.get().isdigit(),
            ent_alu.get().isdigit(),
            ent_gru.get().strip()
        ]):
            messagebox.showwarning(
                "Datos inválidos",
                "Semestre, materias y alumnos deben ser numéricos",
                parent=frame
            )
            return

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # -------- VALIDACIÓN DUPLICADOS --------
        c.execute("""
            SELECT COUNT(*)
            FROM grupos
            WHERE programa = ?
              AND semestre = ?
              AND grupo = ?
              AND modalidad = ?
        """, (
            programa_actual,
            int(ent_sem.get()),
            ent_gru.get().strip(),
            cmb_mod.get()
        ))

        if c.fetchone()[0] > 0:
            conn.close()
            messagebox.showwarning(
                "Grupo duplicado",
                f"Ya existe el grupo {ent_sem.get()}° {ent_gru.get()} "
                f"({cmb_mod.get()}) en este programa.",
                parent=frame
            )
            return

        # -------- INSERT --------
        c.execute("""
            INSERT INTO grupos
            (programa, semestre, grupo, modalidad, materias, alumnos)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            programa_actual,
            int(ent_sem.get()),
            ent_gru.get().strip(),
            cmb_mod.get(),
            int(ent_mat.get()),
            int(ent_alu.get())
        ))
        conn.commit()
        conn.close()

        limpiar()
        cargar_grupos()

    def editar():
        sel = tree.selection()
        if not sel:
            return
        
        limpiar()

        vals = tree.item(sel[0])["values"]
        grupo_editando["id"] = vals[0]

        ent_sem.insert(0, vals[1])
        ent_gru.insert(0, vals[2])
        cmb_mod.set(vals[3])
        ent_mat.insert(0, vals[4])
        ent_alu.insert(0, vals[5])

        btn_agregar.config(state="disabled")
        btn_guardar.config(state="normal")

    def guardar():
        if grupo_editando["id"] is None:
            return

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            UPDATE grupos
            SET semestre=?, grupo=?, modalidad=?, materias=?, alumnos=?
            WHERE id=?
        """, (
            int(ent_sem.get()),
            ent_gru.get().strip(),
            cmb_mod.get(),
            int(ent_mat.get()),
            int(ent_alu.get()),
            grupo_editando["id"]
        ))
        conn.commit()
        conn.close()

        limpiar()
        cargar_grupos()

    def eliminar():
        sel = tree.selection()
        if not sel:
            return

        gid = tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirmar", "¿Eliminar grupo?", parent=frame):
            return

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("DELETE FROM grupos WHERE id=?", (gid,))
        conn.commit()
        conn.close()

        cargar_grupos()

    # ==================================================
    # BOTÓN PREDEFINIDO
    # ==================================================
    def predefinido():
        """Abre diálogo para elegir modalidad y genera 20 grupos."""
        # Crear ventana emergente
        dialogo = tk.Toplevel(frame)
        dialogo.title("Generar grupos predefinidos")
        dialogo.geometry("320x150")
        dialogo.resizable(False, False)
        dialogo.transient(frame)
        dialogo.grab_set()

        tk.Label(dialogo, text="Seleccione la modalidad:", font=("Segoe UI", 11)).pack(pady=(20, 5))

        modalidad_var = tk.StringVar(value="Escolarizado")
        cmb_modal = ttk.Combobox(
            dialogo,
            textvariable=modalidad_var,
            values=["Escolarizado", "Semiescolarizado"],
            state="readonly",
            width=20
        )
        cmb_modal.pack(pady=5)

        def generar():
            modalidad = modalidad_var.get()
            if not modalidad:
                return

            # Confirmar reemplazo
            if not messagebox.askyesno(
                "Confirmar",
                "Esta acción eliminará TODOS los grupos existentes del programa "
                f"'{programa_actual}' y los reemplazará por los 20 grupos predefinidos.\n"
                "¿Desea continuar?",
                parent=frame
            ):
                dialogo.destroy()
                return

            # Conectar a la base de datos
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            # Eliminar grupos actuales del programa
            c.execute("DELETE FROM grupos WHERE programa = ?", (programa_actual,))

            # Insertar los 20 grupos
            for semestre in range(1, 11):
                for grupo in ("A", "B"):
                    c.execute("""
                        INSERT INTO grupos (programa, semestre, grupo, modalidad, materias, alumnos)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (programa_actual, semestre, grupo, modalidad, 6, 25))

            conn.commit()
            conn.close()

            # Actualizar la tabla y cerrar diálogo
            cargar_grupos()
            dialogo.destroy()
            messagebox.showinfo("Éxito", "Se han generado los 20 grupos correctamente.", parent=frame)

        btn_ok = tk.Button(dialogo, text="Generar", bg="#2196F3", fg="white",
                           font=("Segoe UI", 10), width=10, command=generar)
        btn_ok.pack(pady=10)

        # Cerrar con la 'X' sin hacer cambios
        dialogo.protocol("WM_DELETE_WINDOW", dialogo.destroy)

    # ==============================
    # BOTONES (con tooltips)
    # ==============================
    btns = tk.Frame(cont, bg="#f2f4f8")
    btns.pack(pady=10)

    btn_agregar = tk.Button(btns, text="➕", width=5, font=("Segoe UI", 13),
                            bg="#4CAF50", fg="white", command=agregar)
    btn_editar = tk.Button(btns, text="✏", width=5, font=("Segoe UI", 13),
                           bg="#FF9800", fg="white", command=editar)
    btn_guardar = tk.Button(btns, text="💾", width=5, font=("Segoe UI", 13),
                            bg="#64B5F6", fg="black", command=guardar, state="disabled")
    btn_eliminar = tk.Button(btns, text="🗑", width=5, font=("Segoe UI", 13),
                             bg="#E53935", fg="white", command=eliminar)
    btn_predefinido = tk.Button(btns, text="⚡", width=5, font=("Segoe UI", 13),
                                bg="#9C27B0", fg="white", command=predefinido)

    btn_agregar.grid(row=0, column=0, padx=8)
    btn_editar.grid(row=0, column=1, padx=8)
    btn_guardar.grid(row=0, column=2, padx=8)
    btn_eliminar.grid(row=0, column=3, padx=8)
    btn_predefinido.grid(row=0, column=4, padx=8)

    # Asignar tooltips a cada botón
    ToolTip(btn_agregar, "Agregar nuevo grupo")
    ToolTip(btn_editar, "Editar grupo seleccionado")
    ToolTip(btn_guardar, "Guardar cambios del grupo")
    ToolTip(btn_eliminar, "Eliminar grupo seleccionado")
    ToolTip(btn_predefinido, "Generar 20 grupos predefinidos (1°A a 10°B)")
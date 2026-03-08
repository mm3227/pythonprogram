import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import smtplib
from email.message import EmailMessage
from cryptography.fernet import Fernet

from config import RUTA_BASEDATOS, KEY_PATH, ENC_PATH, RUTA_HORARIOS
from core.control.exportar_pdf_profesor import exportar_pdf_profesor


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

DIAS = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"]
EMAIL_REMITENTE = "envioshorariosuaz@gmail.com"


# ==========================================================
# OBTENER PASSWORD DESDE ARCHIVOS EXTERNOS
# ==========================================================

def obtener_password():
    try:
        if not os.path.exists(KEY_PATH) or not os.path.exists(ENC_PATH):
            messagebox.showerror(
                "Error",
                "No se encontraron los archivos de configuración de correo\n"
                "(config_email.key / config_email.enc)"
            )
            return None

        with open(KEY_PATH, "rb") as f:
            key = f.read()

        with open(ENC_PATH, "rb") as f:
            encrypted = f.read()

        cipher = Fernet(key)
        return cipher.decrypt(encrypted).decode()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descifrar la contraseña:\n{e}")
        return None


# ==========================================================
# AUTOCOMPLETE COMBOBOX
# ==========================================================

class AutocompleteCombobox(ttk.Combobox):

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self._check_input)

    def _check_input(self, event):
        value = self.get().lower()
        if value == '':
            self['values'] = self._completion_list
        else:
            data = [item for item in self._completion_list
                    if value in item.lower()]
            self['values'] = data


# ==========================================================
# CARGAR PESTAÑA
# ==========================================================

def cargar_pestana_profesores(frame, ruta_db_ciclo, programa):

    for w in frame.winfo_children():
        w.destroy()

    frame.configure(bg="#f2f4f8")

    nombre_ciclo = os.path.splitext(os.path.basename(ruta_db_ciclo))[0]
    db_horarios = os.path.join(RUTA_HORARIOS, f"{nombre_ciclo}_horario.db")
    db_profesores = os.path.join(RUTA_BASEDATOS, "profesores.db")

    # =====================================================
    # TOOLTIP
    # =====================================================

    class ToolTip:
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            self.tipwindow = None
            widget.bind("<Enter>", self.show)
            widget.bind("<Leave>", self.hide)

        def show(self, event=None):
            if self.tipwindow:
                return
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + 20
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(
                tw,
                text=self.text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", 9)
            )
            label.pack()

        def hide(self, event=None):
            if self.tipwindow:
                self.tipwindow.destroy()
                self.tipwindow = None

    # =====================================================
    # BARRA SUPERIOR
    # =====================================================

    top = tk.Frame(frame, bg="#f2f4f8")
    top.pack(fill="x", pady=10)

    tk.Label(top, text="Seleccionar Profesor:",
             font=("Segoe UI", 12),
             bg="#f2f4f8").pack(side="left", padx=10)

    combo = AutocompleteCombobox(top, width=35)
    combo.pack(side="left", padx=5)

    # =====================================================
    # TABLA
    # =====================================================

    columnas = ("grupo","materia","salon",*DIAS,"horas")

    tree_frame = tk.Frame(frame, bg="#f2f4f8")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    tree = ttk.Treeview(tree_frame, columns=columnas, show="headings")

    for col in columnas:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=110, anchor="center")

    tree.pack(fill="both", expand=True)

    # =====================================================
    # FUNCIÓN CARGAR HORARIOS
    # =====================================================

    def cargar_horarios_profesor(event=None):

        profesor = combo.get()

        if not profesor:
            return

        if not os.path.exists(db_horarios):
            messagebox.showerror("Error", f"No existe base de horarios:\n{db_horarios}")
            return

        conn = sqlite3.connect(db_horarios)
        c = conn.cursor()

        try:
            c.execute("""
                SELECT grupo, materia, salon,
                       L, M, X, J, V, S, horas
                FROM horarios
                WHERE profesor = ?
                AND programa = ?
                ORDER BY grupo
            """, (profesor, programa))

            registros = c.fetchall()

        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar horarios:\n{e}")
            conn.close()
            return

        conn.close()

        # Limpiar tabla
        for item in tree.get_children():
            tree.delete(item)

        for fila in registros:
            tree.insert("", "end", values=fila)

    # =====================================================
    # GENERAR PDF
    # =====================================================

    def generar_pdf_profesor():
        profesor = combo.get()

        if not profesor:
            messagebox.showwarning("Aviso", "Seleccione un profesor")
            return

        if not os.path.exists(db_horarios):
            messagebox.showerror("Error", "No existe base de horarios")
            return

        exportar_pdf_profesor(db_horarios, profesor)

    # =====================================================
    # ENVIAR CORREO
    # =====================================================

    def enviar_por_correo():

        profesor = combo.get()

        if not profesor:
            messagebox.showwarning("Aviso", "Seleccione un profesor")
            return

        conn = sqlite3.connect(db_profesores)
        c = conn.cursor()
        c.execute("SELECT email FROM profesores WHERE nombre = ?", (profesor,))
        row = c.fetchone()
        conn.close()

        if not row or not row[0]:
            messagebox.showerror("Error", "Profesor sin correo registrado")
            return

        email_destino = row[0]

        ruta_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
            initialfile=f"Horario_{profesor}.pdf"
        )

        if not ruta_pdf:
            return

        try:
            ruta_generada = exportar_pdf_profesor(
                db_horarios,
                profesor,
                ruta_pdf
            )

            if not ruta_generada or os.path.getsize(ruta_generada) == 0:
                messagebox.showerror("Error", "El PDF se generó vacío")
                return

            password = obtener_password()
            if not password:
                return

            msg = EmailMessage()
            msg["Subject"] = "Horario Asignado"
            msg["From"] = EMAIL_REMITENTE
            msg["To"] = email_destino

            msg.set_content(
                f"Estimado(a) {profesor},\n\n"
                "Adjunto encontrará su horario correspondiente al ciclo actual.\n\n"
                "Atentamente,\nCoordinación Académica"
            )

            with open(ruta_generada, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="pdf",
                    filename=os.path.basename(ruta_generada)
                )

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_REMITENTE, password)
                smtp.send_message(msg)

            messagebox.showinfo("Éxito", f"Correo enviado a:\n{email_destino}")

        except Exception as e:
            messagebox.showerror("Error al enviar correo", str(e))

    # =====================================================
    # BOTONES
    # =====================================================

    btn_pdf = tk.Button(top, text="📄",
                        bg="#4a6fa5", fg="white",
                        command=generar_pdf_profesor)
    btn_pdf.pack(side="left", padx=10)
    ToolTip(btn_pdf, "Generar PDF del horario completo del profesor")

    btn_mail = tk.Button(top, text="📧",
                         bg="#2e7d32", fg="white",
                         command=enviar_por_correo)
    btn_mail.pack(side="left", padx=5)
    ToolTip(btn_mail, "Enviar el horario en PDF al correo del profesor")

    # =====================================================
    # CARGAR PROFESORES
    # =====================================================

    if not os.path.exists(db_profesores):
        messagebox.showerror("Error", "No existe profesores.db")
        return

    conn = sqlite3.connect(db_profesores)
    c = conn.cursor()
    c.execute("SELECT nombre FROM profesores ORDER BY nombre")
    profesores = [r[0] for r in c.fetchall()]
    conn.close()

    combo.set_completion_list(profesores)
    combo.bind("<<ComboboxSelected>>", cargar_horarios_profesor)

    # Cargar automáticamente el primero
    if profesores:
        combo.set(profesores[0])
        cargar_horarios_profesor()

#core/control/exportar_pdf_profesores.py
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from tkinter import messagebox, filedialog
from config import resource_path
import sqlite3
import os
import sys


def exportar_pdf_profesor(ruta_db_ciclo, profesor, ruta_guardado=None):

    if not os.path.exists(ruta_db_ciclo):
        messagebox.showerror("Error", "No existe base de horarios")
        return

    nombre_ciclo = os.path.splitext(os.path.basename(ruta_db_ciclo))[0]

    conn = sqlite3.connect(ruta_db_ciclo)
    c = conn.cursor()

    c.execute("""
        SELECT programa, materia, salon,
               L, M, X, J, V, S
        FROM horarios
        WHERE profesor = ?
        ORDER BY programa, materia
    """, (profesor,))

    registros = c.fetchall()
    conn.close()

    if not registros:
        messagebox.showwarning("Aviso", "No hay materias para este profesor")
        return

    if ruta_guardado:
        nombre_archivo = ruta_guardado
    else:
        nombre_archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
            initialfile=f"{profesor}_{nombre_ciclo}.pdf",
            title="Guardar horario del profesor"
        )

        if not nombre_archivo:
            return

    if not nombre_archivo:
        return

    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=A5,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    elementos = []

    # ==========================
    # IMAGEN ENCABEZADO
    # ==========================
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    ruta_imagen = resource_path("core/control/esquina.jpg")

    if os.path.exists(ruta_imagen):
        ancho = doc.width
        proporcion = 160 / 686
        alto = ancho * proporcion

        img = Image(ruta_imagen, width=ancho, height=alto)
        elementos.append(img)
        elementos.append(Spacer(1, 10))

    # ==========================
    # TITULO
    # ==========================
    estilo_titulo = ParagraphStyle(
        name='Titulo',
        fontSize=11,
        leading=14,
        spaceAfter=6
    )

    elementos.append(Paragraph(f"<b>Horario del Profesor:</b> {profesor}", estilo_titulo))
    elementos.append(Paragraph(f"<b>Ciclo:</b> {nombre_ciclo}", estilo_titulo))
    elementos.append(Spacer(1, 10))

    # ==========================
    # ESTILOS
    # ==========================
    estilo_encabezado = ParagraphStyle(
        name='Encabezado',
        fontSize=8,
        leading=10,
        alignment=1,  # 1 = CENTER
        textColor=colors.white,
        spaceBefore=2,
        spaceAfter=2
    )

    estilo_celda = ParagraphStyle(
        name='Celda',
        fontSize=7,
        leading=9,
        alignment=1  # 1 = CENTER
    )

    # ==========================
    # DATOS TABLA
    # ==========================
    datos = [[
        Paragraph("<b>Programa</b>", estilo_encabezado),
        Paragraph("<b>Materia</b>", estilo_encabezado),
        Paragraph("<b>Salón</b>", estilo_encabezado),
        Paragraph("<b>Lu</b>", estilo_encabezado),
        Paragraph("<b>Ma</b>", estilo_encabezado),
        Paragraph("<b>Mi</b>", estilo_encabezado),
        Paragraph("<b>Ju</b>", estilo_encabezado),
        Paragraph("<b>Vi</b>", estilo_encabezado),
        Paragraph("<b>Sá</b>", estilo_encabezado),
    ]]

    for fila in registros:

        nueva_fila = []

        for celda in fila:

            texto = str(celda) if celda else ""

            # 🔵 Formato profesional de horario
            if "-" in texto:
                partes = texto.split("-")
                if len(partes) == 2:
                    inicio = partes[0].strip().zfill(5)
                    fin = partes[1].strip().zfill(5)
                    texto = f"{inicio} – {fin}"

            nueva_fila.append(Paragraph(texto, estilo_celda))

        datos.append(nueva_fila)

    # ==========================
    # AJUSTE PROPORCIONAL A A5
    # ==========================
    ancho_total = doc.width

    anchos = [
        ancho_total * 0.13,  # Programa
        ancho_total * 0.22,  # Materia
        ancho_total * 0.10,  # Salon
        ancho_total * 0.09,  # Lu
        ancho_total * 0.09,
        ancho_total * 0.09,
        ancho_total * 0.09,
        ancho_total * 0.09,
        ancho_total * 0.10,
    ]

    tabla = Table(datos, colWidths=anchos, repeatRows=1)

    estilo_tabla = TableStyle([

        # ===== ENCABEZADO =====
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1f4e79")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('VALIGN',(0,0),(-1,0),'MIDDLE'),

        # ===== CUERPO =====
        ('ALIGN',(0,1),(-1,-1),'CENTER'),
        ('VALIGN',(0,1),(-1,-1),'MIDDLE'),

        # ===== BORDES =====
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),

        # ===== ESPACIADO =====
        ('LEFTPADDING',(0,0),(-1,-1),4),
        ('RIGHTPADDING',(0,0),(-1,-1),4),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
    ])


    tabla.setStyle(estilo_tabla)

    # Filas alternadas
    for i in range(1, len(datos)):
        if i % 2 == 0:
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0,i), (-1,i), colors.whitesmoke),
            ]))

    elementos.append(tabla)

    doc.build(elementos)

    messagebox.showinfo("PDF generado", f"Archivo creado:\n{nombre_archivo}")
    return nombre_archivo
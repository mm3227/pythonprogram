#core/control/exportar_resumen.py
import pandas as pd
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import os
from config import resource_path


# ============================================================
# EXPORTAR A EXCEL
# ============================================================
def exportar_excel_resumen(programa, ciclo, db_path, datos_por_grupo):

    if not datos_por_grupo:
        messagebox.showerror("Error", "No hay datos para exportar.")
        return

    nombre_archivo = f"horarios_{ciclo}".replace(" ", "_")

    archivo = filedialog.asksaveasfilename(
        initialfile=nombre_archivo,
        defaultextension=".xlsx",
        filetypes=[("Archivo Excel", "*.xlsx")],
        title="Guardar resumen de horarios"
    )

    if not archivo:
        return

    try:
       with pd.ExcelWriter(archivo, engine='openpyxl') as writer:

        fila_inicio = 0
        #hoja = "Resumen"
        hoja= nombre_archivo

        for (grupo, modalidad), filas in datos_por_grupo.items():

            df = pd.DataFrame(filas, columns=[
                "Materia", "Profesor", "Salón",
                "Lunes", "Martes", "Miércoles",
                "Jueves", "Viernes", "Sábado", "Horas"
            ])

            # Escribir título del grupo
            titulo_df = pd.DataFrame([[f"Grupo: {grupo} - Modalidad: {modalidad}"]])
            titulo_df.to_excel(writer, sheet_name=hoja,
                               startrow=fila_inicio, index=False, header=False)

            fila_inicio += 2  # espacio después del título

            # Escribir tabla
            df.to_excel(writer, sheet_name=hoja,
                        startrow=fila_inicio, index=False)

            fila_inicio += len(df) + 3  # espacio entre tablas

        messagebox.showinfo("Éxito", f"Archivo Excel guardado en:\n{archivo}")

    except Exception as e:
        messagebox.showerror("Error al exportar Excel", str(e))

# ============================================================
# EXPORTAR A PDF
# ============================================================# ============================================================
# EXPORTAR A PDF (MODIFICADO)
# ============================================================
def exportar_pdf_resumen(programa, ciclo, db_path, datos_por_grupo):

    if not datos_por_grupo:
        messagebox.showerror("Error", "No hay datos para exportar.")
        return

    nombre_archivo = f"horarios_{ciclo}".replace(" ", "_")

    archivo = filedialog.asksaveasfilename(
        initialfile=nombre_archivo,
        defaultextension=".pdf",
        filetypes=[("Archivo PDF", "*.pdf")],
        title="Guardar resumen de horarios"
    )

    if not archivo:
        return

    doc = SimpleDocTemplate(
        archivo,
        pagesize=landscape(letter),
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=1.3 * inch,
        bottomMargin=0.5 * inch
    )

    story = []
    styles = getSampleStyleSheet()

    # Estilo para el título principal
    titulo_style = styles['Title']

    # Estilo para los títulos de grupo
    grupo_style = ParagraphStyle(
        'GrupoStyle',
        parent=styles['Heading2'],
        spaceAfter=10,
        textColor=colors.HexColor('#1f4e79')
    )

    # Estilo para las celdas de la tabla (texto centrado con wrap)
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,            # interlineado
        alignment=1,           # centrado
        wordWrap='LTR'         # permite saltos de línea automáticos
    )

    # ---------------- TÍTULO ----------------
    story.append(Paragraph(f"Resumen de Horarios - {programa} - {ciclo}", titulo_style))
    story.append(Spacer(1, 0.3 * inch))

    # ---------------- TABLAS ----------------
    for (grupo, modalidad), filas in datos_por_grupo.items():

        story.append(Paragraph(
            f"Grupo: {grupo}  -  Modalidad: {modalidad}",
            grupo_style
        ))
        story.append(Spacer(1, 0.15 * inch))

        # Procesar filas para PDF:
        # 1. Dividir el salón en dos líneas (edificio y salón)
        # 2. Dividir cada horario (Lun a Sáb) en dos líneas (inicio y fin)
        # 3. Eliminar la última columna (Horas)
        # 4. Convertir cada campo en un Paragraph con el estilo definido
        filas_pdf = []
        for fila in filas:
            # fila: [Materia, Profesor, Salón, Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Horas]
            materia, profesor, salon, lun, mar, mie, jue, vie, sab, _ = fila

            # Procesar salón
            partes_salon = salon.split(maxsplit=1)
            if len(partes_salon) == 2:
                salon_texto = f"{partes_salon[0]}\n{partes_salon[1]}"
            else:
                salon_texto = salon

            # Función para dividir un horario "12:00-14:00" en "12:00\n14:00"
            def formatear_horario(h):
                if '-' in h:
                    inicio, fin = h.split('-', 1)
                    return f"{inicio}\n{fin}"
                return h

            # Aplicar a cada día
            lun_texto = formatear_horario(lun)
            mar_texto = formatear_horario(mar)
            mie_texto = formatear_horario(mie)
            jue_texto = formatear_horario(jue)
            vie_texto = formatear_horario(vie)
            sab_texto = formatear_horario(sab)

            # Crear Paragraph para cada campo (para que el texto se ajuste)
            fila_con_paragraphs = [
                Paragraph(materia, cell_style),
                Paragraph(profesor, cell_style),
                Paragraph(salon_texto, cell_style),
                Paragraph(lun_texto, cell_style),
                Paragraph(mar_texto, cell_style),
                Paragraph(mie_texto, cell_style),
                Paragraph(jue_texto, cell_style),
                Paragraph(vie_texto, cell_style),
                Paragraph(sab_texto, cell_style)
            ]
            filas_pdf.append(fila_con_paragraphs)

        # Encabezados (strings simples, el estilo de la tabla les dará formato)
        encabezados = [
            "Materia", "Profesor", "Salón",
            "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"
        ]

        # Construir datos de la tabla: encabezados + filas
        data = [encabezados] + filas_pdf

        # Definir anchos de columna para que la tabla se ajuste a los márgenes
        # Ancho disponible: 720 puntos (10 pulgadas) menos márgenes (ya considerados en doc)
        # Distribución ajustada para dar más espacio a Profesor
        colWidths = [
            160,   # Materia
            170,   # Profesor (más ancho para nombres largos)
            70,    # Salón
            48,    # Lun
            48,    # Mar
            48,    # Mié
            48,    # Jue
            48,    # Vie
            48     # Sáb
        ]  # Suma: 160+170+70+48*6 = 160+170+70+288 = 688 (caja dentro del margen)

        tabla = Table(data, colWidths=colWidths, repeatRows=1)

        tabla.setStyle(TableStyle([
            # ENCABEZADO AZUL
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # CUERPO BLANCO
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),

            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

            # Las celdas ya contienen Paragraphs, el estilo de fuente se hereda del Paragraph
            # pero podemos forzar tamaño por si acaso (aunque el Paragraph ya lo define)
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        story.append(tabla)
        story.append(Spacer(1, 0.4 * inch))

    # ---------------- IMAGEN DE ENCABEZADO ----------------
    def dibujar_encabezado(canvas, doc):
        ruta_imagen = resource_path("core/control/esquina.jpg")
        if os.path.isfile(ruta_imagen):
            try:
                img = ImageReader(ruta_imagen)
                ancho_pdf = 240
                alto_pdf = 55
                x = doc.pagesize[0] - ancho_pdf - 30
                y = doc.pagesize[1] - alto_pdf - 20
                canvas.drawImage(img, x, y, width=ancho_pdf, height=alto_pdf,
                                 preserveAspectRatio=True, mask='auto')
            except Exception:
                pass
        else:
            print("No se encontró la imagen en:", ruta_imagen)

    try:
        doc.build(
            story,
            onFirstPage=dibujar_encabezado,
            onLaterPages=dibujar_encabezado
        )
        messagebox.showinfo("Éxito", f"Archivo PDF guardado en:\n{archivo}")
    except Exception as e:
        messagebox.showerror("Error al exportar PDF", str(e))
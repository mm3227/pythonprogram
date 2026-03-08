# ver_estructura_bds.py
# Script TEMPORAL para inspeccionar la estructura REAL de las bases de datos
# No forma parte del sistema

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BD_DIR = os.path.join(BASE_DIR, "basedatos")

DBS = [
    "materias.db",
    "profesores.db",
    "salones.db"
]

OUTPUT = os.path.join(BD_DIR, "_estructura_bds.txt")


def analizar_db(nombre_db):
    ruta = os.path.join(BD_DIR, nombre_db)
    lineas = []

    lineas.append("\n" + "=" * 70)
    lineas.append(f"BASE DE DATOS: {nombre_db}")
    lineas.append("=" * 70)

    if not os.path.exists(ruta):
        lineas.append("❌ NO EXISTE EL ARCHIVO")
        return lineas

    conn = sqlite3.connect(ruta)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [r[0] for r in c.fetchall()]

    if not tablas:
        lineas.append("(No contiene tablas)")
        conn.close()
        return lineas

    for tabla in tablas:
        lineas.append(f"\nTabla: {tabla}")
        lineas.append("-" * 40)

        c.execute(f"PRAGMA table_info({tabla})")
        columnas = c.fetchall()

        if not columnas:
            lineas.append("  (Sin columnas)")
            continue

        for cid, nombre, tipo, notnull, default, pk in columnas:
            lineas.append(
                f"  - {nombre:<22} | {tipo:<10} | PK={pk} | NOT NULL={notnull}"
            )

    conn.close()
    return lineas


def main():
    reporte = []
    reporte.append("REPORTE DE ESTRUCTURA DE BASES DE DATOS")
    reporte.append(f"Directorio: {BD_DIR}")
    reporte.append("=" * 70)

    for db in DBS:
        reporte.extend(analizar_db(db))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(reporte))

    print("\n✔ Reporte generado correctamente")
    print(f"📄 Archivo creado en: {OUTPUT}\n")


if __name__ == "__main__":
    main()

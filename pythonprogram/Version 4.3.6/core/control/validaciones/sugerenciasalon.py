#core/control/validaciones/sugerenciasalon.pu
"""
Módulo de sugerencia inteligente de salones
Filtra salones por capacidad y uso, sugiriendo los más adecuados
"""

import sqlite3
import os
import re
from collections import defaultdict
from config import RUTA_BASEDATOS

# ==================================================
# RUTAS - CORREGIDAS Y CON VERIFICACIÓN
# ==================================================
# Obtener la raíz del proyecto de forma robusta
RUTA_SALONES = os.path.join(RUTA_BASEDATOS, "salones.db")

# ==================================================
# FUNCIÓN AUXILIAR: NORMALIZAR GRUPO
# ==================================================
def normalizar_grupo(grupo_completo):
    """
    Normaliza el formato del grupo:
    - Elimina espacios alrededor del símbolo °
    - Elimina espacios al inicio y final
    - Convierte a mayúsculas (opcional, según convención)
    """
    if not grupo_completo:
        return ""
    grupo = grupo_completo.strip().upper()
    # Eliminar espacios alrededor de '°'
    grupo = re.sub(r'\s*°\s*', '°', grupo)
    return grupo


# ==================================================
# FUNCIONES DE BASE DE DATOS (CON VERIFICACIÓN)
# ==================================================
def obtener_capacidad_salones():
    """Obtiene todos los salones con su capacidad desde la base de datos"""
    salones_con_capacidad = {}

    if not os.path.exists(RUTA_SALONES):
        print(f"[ERROR] No se encuentra salones.db en: {RUTA_SALONES}")
        return {}

    try:
        con = sqlite3.connect(RUTA_SALONES)
        cur = con.cursor()
        cur.execute("""
            SELECT edificio, salon, capacidad 
            FROM salones 
            ORDER BY edificio, salon
        """)
        filas = cur.fetchall()
        con.close()

        for edificio, salon, capacidad in filas:
            salones_con_capacidad[f"{edificio} {salon}"] = capacidad

    except Exception as e:
        print(f"[ERROR] al cargar salones.db: {e}")
        return {}

    return salones_con_capacidad


def obtener_alumnos_por_grupo(db_ciclo_path, programa, grupo_completo):
    """
    Obtiene el número de alumnos de un grupo específico.
    Maneja formatos: "1°A", "1° A", "1°  A", "1°B", "1° B", etc.
    """
    if not grupo_completo:
        print("[WARNING] grupo_completo vacío")
        return 0

    # 1. Normalizar grupo de entrada
    grupo_normalizado = normalizar_grupo(grupo_completo)

    # 2. Extraer semestre y letra del grupo
    semestre = 1
    grupo_letra = grupo_normalizado

    if "°" in grupo_normalizado:
        partes = grupo_normalizado.split("°", 1)
        semestre_str = partes[0].strip()
        grupo_letra = partes[1].strip() if len(partes) > 1 else ""
        try:
            semestre = int(semestre_str)
        except ValueError:
            print(f"[WARNING] No se pudo convertir semestre: '{semestre_str}'")
            semestre = 1
    else:
        # Si no tiene °, asumimos que es un grupo sin semestre (ej. SA°1 ya fue procesado)
        grupo_letra = grupo_normalizado

    # 3. Verificar existencia de la BD
    if not os.path.exists(db_ciclo_path):
        print(f"[ERROR] No se encuentra la base de datos del ciclo: {db_ciclo_path}")
        return 0

    try:
        con = sqlite3.connect(db_ciclo_path)
        cur = con.cursor()

        # --- Intento 1: Comparación exacta ignorando espacios (usando REPLACE) ---
        cur.execute("""
            SELECT alumnos 
            FROM grupos 
            WHERE programa = ? 
              AND semestre = ? 
              AND REPLACE(grupo, ' ', '') = REPLACE(?, ' ', '')
        """, (programa, semestre, grupo_letra))
        resultado = cur.fetchone()
        if resultado:
            con.close()
            return resultado[0]

        # --- Intento 2: Sin filtrar por semestre (solo programa y grupo normalizado) ---
        cur.execute("""
            SELECT alumnos, semestre 
            FROM grupos 
            WHERE programa = ? 
              AND REPLACE(grupo, ' ', '') = REPLACE(?, ' ', '')
            ORDER BY semestre
        """, (programa, grupo_letra))
        fila = cur.fetchone()
        if fila:
            print(f"[INFO] Grupo encontrado con semestre {fila[1]} (se esperaba {semestre})")
            con.close()
            return fila[0]

        # --- Intento 3: Búsqueda con LIKE (por si hay caracteres extraños) ---
        cur.execute("""
            SELECT alumnos 
            FROM grupos 
            WHERE programa = ? 
              AND semestre = ? 
              AND (grupo LIKE ? OR grupo LIKE ?)
        """, (programa, semestre, f"%{grupo_letra}%", f"%{grupo_letra.strip()}%"))
        resultado = cur.fetchone()
        if resultado:
            con.close()
            return resultado[0]

        # --- Intento 4: Primer grupo del semestre (fallback) ---
        cur.execute("""
            SELECT alumnos 
            FROM grupos 
            WHERE programa = ? 
              AND semestre = ?
            LIMIT 1
        """, (programa, semestre))
        fila = cur.fetchone()
        if fila:
            print(f"[INFO] Usando alumnos del primer grupo del semestre {semestre}")
            con.close()
            return fila[0]

        con.close()
    except Exception as e:
        print(f"[ERROR] en obtener_alumnos_por_grupo: {e}")
        return 0

    print(f"[WARNING] No se encontró el grupo '{grupo_completo}' (normalizado: '{grupo_normalizado}') en {db_ciclo_path}")
    return 0


def calcular_uso_salones_horas(filas_por_programa):
    """Calcula el uso de salones en horas para ordenarlos por disponibilidad"""
    uso = defaultdict(float)

    for filas in filas_por_programa.values():
        for fila in filas:
            if len(fila) > 4:
                salon = ""
                if hasattr(fila[4], 'get'):
                    salon = fila[4].get().strip()
                elif hasattr(fila[4], 'cget'):
                    salon = fila[4].cget("text").strip()

                if not salon:
                    continue

                horas_totales = 0
                for col in range(6, 12):
                    if col < len(fila):
                        horario = ""
                        if hasattr(fila[col], 'get'):
                            horario = fila[col].get().strip()

                        if horario and "-" in horario:
                            try:
                                hora_inicio, hora_fin = horario.split("-")
                                h1, m1 = map(int, hora_inicio.split(":"))
                                h2, m2 = map(int, hora_fin.split(":"))
                                horas = (h2 - h1) + (m2 - m1) / 60.0
                                horas_totales += horas
                            except:
                                continue

                uso[salon] += horas_totales

    return uso


# ==================================================
# SISTEMA DE SUGERENCIAS PRINCIPAL
# ==================================================
def sugerir_salones(db_ciclo_path, programa, grupo_completo, filas_por_programa=None):
    """
    Sugiere salones apropiados para un grupo.
    Siempre devuelve una lista (puede ser vacía si no hay salones).
    """
    # 1. Obtener capacidades
    capacidad_salones = obtener_capacidad_salones()
    if not capacidad_salones:
        print("[ERROR] No hay salones disponibles para sugerir.")
        return []

    # 2. Obtener número de alumnos del grupo
    alumnos = obtener_alumnos_por_grupo(db_ciclo_path, programa, grupo_completo)
    if alumnos == 0:
        print(f"[INFO] No se encontraron alumnos para '{grupo_completo}'. Se usarán todos los salones.")
        alumnos = 1  # Mostrar todos los salones

    # 3. Calcular uso si hay datos
    uso_salones = {}
    if filas_por_programa:
        uso_salones = calcular_uso_salones_horas(filas_por_programa)

    # 4. Filtrar y puntuar
    salones_filtrados = []
    for salon, capacidad in capacidad_salones.items():
        if capacidad >= alumnos:
            puntuacion = 0
            sobrante = capacidad - alumnos

            # Puntos por capacidad
            if sobrante <= 5:
                puntuacion += 30
            elif sobrante <= 10:
                puntuacion += 20
            elif sobrante <= 20:
                puntuacion += 10
            else:
                puntuacion += 5

            # Puntos por bajo uso
            uso_actual = uso_salones.get(salon, 0)
            if uso_actual == 0:
                puntuacion += 50
            elif uso_actual <= 10:
                puntuacion += 30
            elif uso_actual <= 20:
                puntuacion += 15
            elif uso_actual <= 30:
                puntuacion += 5

            salones_filtrados.append({
                'salon': salon,
                'capacidad': capacidad,
                'alumnos': alumnos,
                'uso_actual': uso_actual,
                'sobrante': sobrante,
                'puntuacion': puntuacion,
                'disponibilidad': max(0, 100 - (uso_actual / 48 * 100))
            })

    # 5. Ordenar
    salones_filtrados.sort(key=lambda x: (-x['puntuacion'], x['capacidad']))

    # 6. Construir etiquetas descriptivas
    sugerencias = []
    for info in salones_filtrados:
        etiqueta = f"{info['salon']}"

        # Capacidad
        if info['sobrante'] <= 5:
            etiqueta += " 🎯 (Ajustado)"
        elif info['sobrante'] <= 10:
            etiqueta += " ✅ (Óptimo)"
        elif info['sobrante'] <= 20:
            etiqueta += " 👍 (Bueno)"
        else:
            etiqueta += " 💺 (Amplio)"

        # Uso
        if info['uso_actual'] == 0:
            etiqueta += " 🆕 (Libre)"
        elif info['disponibilidad'] > 70:
            etiqueta += " 📈 (Muy disponible)"
        elif info['disponibilidad'] > 40:
            etiqueta += " 📊 (Disponible)"
        else:
            etiqueta += " ⚠️ (Ocupado)"

        # Datos
        etiqueta += f" | Cap: {info['capacidad']} | Alumnos: {alumnos} | Uso: {info['uso_actual']:.1f}h"

        sugerencias.append((etiqueta, info['salon']))

    return sugerencias


def obtener_salones_por_capacidad(db_ciclo_path, programa, grupo_completo):
    """Versión simple: solo salones con capacidad suficiente"""
    capacidad_salones = obtener_capacidad_salones()
    if not capacidad_salones:
        return []

    alumnos = obtener_alumnos_por_grupo(db_ciclo_path, programa, grupo_completo)
    if alumnos == 0:
        alumnos = 1

    salones_filtrados = []
    for salon, capacidad in capacidad_salones.items():
        if capacidad >= alumnos:
            sobrante = capacidad - alumnos
            if sobrante == 0:
                etiqueta = f"{salon} (Cap: {capacidad} - Ajustado perfecto)"
            elif sobrante <= 5:
                etiqueta = f"{salon} (Cap: {capacidad} - +{sobrante} asientos)"
            elif sobrante <= 10:
                etiqueta = f"{salon} (Cap: {capacidad} - Buena capacidad)"
            else:
                etiqueta = f"{salon} (Cap: {capacidad} - Amplio)"
            salones_filtrados.append((etiqueta, salon))

    salones_filtrados.sort(key=lambda x: capacidad_salones[x[1]])
    return salones_filtrados
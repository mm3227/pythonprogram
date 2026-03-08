#core/control/validaciones/validarhoras_salones.py
"""
Módulo de validación de horarios para evitar choques y validar horas por modalidad
"""

import sqlite3
import os
from collections import defaultdict

# ==================================================
# RUTAS
# ==================================================
"""
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
BD_DIR = os.path.join(BASE_DIR, "basedatos")
"""
# ==================================================
# CONSTANTES DE HORAS POR MODALIDAD
# ==================================================
HORAS_POR_MODALIDAD = {
    "Escolarizado": 5.0,
    "Semiescolarizado": 7.0,
    "Escolarizada": 5.0,  # Compatibilidad con variantes
    "Semiescolarizada": 7.0
}

# ==================================================
# FUNCIONES DE CONVERSIÓN DE HORAS
# ==================================================
def hora_a_minutos(hora_str):
    """Convierte una hora en formato HH:MM a minutos desde las 00:00"""
    if not hora_str:
        return 0
    try:
        horas, minutos = map(int, hora_str.split(":"))
        return horas * 60 + minutos
    except:
        return 0
# Alias para compatibilidad con código existente
def minutos(hora_str):
    """Alias de hora_a_minutos para compatibilidad"""
    return hora_a_minutos(hora_str)

def minutos_a_hora(minutos):
    """Convierte minutos a formato HH:MM"""
    horas = minutos // 60
    minutos = minutos % 60
    return f"{horas:02d}:{minutos:02d}"

def parsear_rango_horario(horario_str):
    """Convierte un string 'HH:MM-HH:MM' a tupla de minutos (inicio, fin)"""
    if not horario_str or "-" not in horario_str:
        return (0, 0)
    
    try:
        inicio_str, fin_str = horario_str.split("-")
        inicio = hora_a_minutos(inicio_str.strip())
        fin = hora_a_minutos(fin_str.strip())
        return (inicio, fin)
    except:
        return (0, 0)

def rangos_se_superponen(rango1, rango2):
    """Verifica si dos rangos de tiempo se superponen"""
    inicio1, fin1 = rango1
    inicio2, fin2 = rango2
    
    # Si alguno no es válido, no hay superposición
    if inicio1 == 0 and fin1 == 0 or inicio2 == 0 and fin2 == 0:
        return False
    
    # Verificar superposición
    return max(inicio1, inicio2) < min(fin1, fin2)

def calcular_horas_totales(rangos):
    """Calcula el total de horas a partir de una lista de rangos en minutos"""
    total_minutos = 0
    for inicio, fin in rangos:
        if fin > inicio:  # Solo rangos válidos
            total_minutos += (fin - inicio)
    return total_minutos / 60.0  # Convertir a horas

# ==================================================
# VALIDACIÓN DE CHOQUES DE HORARIOS
# ==================================================
def detectar_choques_horarios(filas_por_programa, fila_actual=None):
    """
    Detecta todos los choques de horarios en la matriz completa.
    Retorna una lista de diccionarios con información de cada choque.
    
    Args:
        filas_por_programa: Diccionario con todas las filas de horarios
        fila_actual: Fila que se está editando (para excluir de auto-choque)
    
    Returns:
        Lista de choques encontrados con detalles
    """
    choques = []
    
    # Estructuras para almacenar horarios por entidad
    horarios_por_grupo = defaultdict(lambda: defaultdict(list))  # grupo -> día -> [rangos]
    horarios_por_profesor = defaultdict(lambda: defaultdict(list))  # profesor -> día -> [rangos]
    horarios_por_salon = defaultdict(lambda: defaultdict(list))  # salon -> día -> [rangos]
    
    # Recolectar todos los horarios
    for programa, filas in filas_por_programa.items():
        for fila in filas:
            # Si esta es la fila actual, no la comparamos consigo misma
            es_fila_actual = (fila is fila_actual)
            
            # Obtener información de la fila
            grupo = ""
            profesor = ""
            salon = ""
            
            if len(fila) > 1:
                if hasattr(fila[1], 'cget'):
                    grupo = fila[1].cget("text").strip()
                elif hasattr(fila[1], 'get'):
                    grupo = fila[1].get().strip()
            
            if len(fila) > 5:
                if hasattr(fila[5], 'get'):
                    profesor = fila[5].get().strip()
            
            if len(fila) > 4:
                if hasattr(fila[4], 'get'):
                    salon = fila[4].get().strip()
            
            # Procesar horarios por día (columnas 6-11: L a S)
            for dia_idx, dia in enumerate(["L", "M", "X", "J", "V", "S"]):
                col_idx = 6 + dia_idx
                if col_idx < len(fila):
                    horario_str = ""
                    if hasattr(fila[col_idx], 'get'):
                        horario_str = fila[col_idx].get().strip()
                    
                    if horario_str and "-" in horario_str:
                        rango = parsear_rango_horario(horario_str)
                        inicio, fin = rango
                        
                        if fin > inicio:  # Solo rangos válidos
                            # Agregar a las estructuras con información de la fila
                            info_fila = {
                                'programa': programa,
                                'grupo': grupo,
                                'profesor': profesor,
                                'salon': salon,
                                'horario': horario_str,
                                'dia': dia,
                                'fila': fila
                            }
                            
                            # Verificar choques para cada entidad
                            if grupo:
                                for otro_rango, otra_info in horarios_por_grupo[grupo][dia]:
                                    if rangos_se_superponen(rango, otro_rango) and not (es_fila_actual and otra_info['fila'] is fila):
                                        choques.append({
                                            'tipo': 'GRUPO',
                                            'entidad': grupo,
                                            'dia': dia,
                                            'horario1': otra_info['horario'],
                                            'horario2': horario_str,
                                            'info1': otra_info,
                                            'info2': info_fila
                                        })
                                horarios_por_grupo[grupo][dia].append((rango, info_fila))
                            
                            if profesor:
                                for otro_rango, otra_info in horarios_por_profesor[profesor][dia]:
                                    if rangos_se_superponen(rango, otro_rango) and not (es_fila_actual and otra_info['fila'] is fila):
                                        choques.append({
                                            'tipo': 'PROFESOR',
                                            'entidad': profesor,
                                            'dia': dia,
                                            'horario1': otra_info['horario'],
                                            'horario2': horario_str,
                                            'info1': otra_info,
                                            'info2': info_fila
                                        })
                                horarios_por_profesor[profesor][dia].append((rango, info_fila))
                            
                            if salon:
                                for otro_rango, otra_info in horarios_por_salon[salon][dia]:
                                    if rangos_se_superponen(rango, otro_rango) and not (es_fila_actual and otra_info['fila'] is fila):
                                        choques.append({
                                            'tipo': 'SALÓN',
                                            'entidad': salon,
                                            'dia': dia,
                                            'horario1': otra_info['horario'],
                                            'horario2': horario_str,
                                            'info1': otra_info,
                                            'info2': info_fila
                                        })
                                horarios_por_salon[salon][dia].append((rango, info_fila))
    
    return choques

def verificar_choques_para_nuevo_horario(filas_por_programa, grupo_actual, salon_actual, 
                                        profesor_actual, nuevos_horarios, fila_a_excluir):
    """
    Verifica choques específicos para un nuevo horario que se está asignando.
    
    Args:
        filas_por_programa: Todas las filas existentes
        grupo_actual: Grupo que se está editando
        salon_actual: Salón que se está asignando
        profesor_actual: Profesor que se está asignando
        nuevos_horarios: Diccionario con días y horarios nuevos
        fila_a_excluir: Fila actual (para no comparar consigo misma)
    
    Returns:
        Lista de choques potenciales
    """
    choques_potenciales = []
    
    # Si no hay horarios nuevos, no hay choques
    if not nuevos_horarios:
        return choques_potenciales
    
    # Verificar choques para cada día con horario nuevo
    for dia, horario_str in nuevos_horarios.items():
        if not horario_str or "-" not in horario_str:
            continue
            
        nuevo_rango = parsear_rango_horario(horario_str)
        inicio_nuevo, fin_nuevo = nuevo_rango
        
        # Solo considerar rangos válidos
        if fin_nuevo <= inicio_nuevo:
            continue
        
        # Buscar choques en todas las filas (todos los programas)
        for programa, filas in filas_por_programa.items():
            for fila in filas:
                # Saltar la fila actual
                if fila is fila_a_excluir:
                    continue
                
                # Obtener información de la otra fila
                otro_grupo = ""
                otro_profesor = ""
                otro_salon = ""
                
                # Obtener grupo (índice 1)
                if len(fila) > 1:
                    if hasattr(fila[1], 'cget'):
                        otro_grupo = fila[1].cget("text").strip()
                    elif hasattr(fila[1], 'get'):
                        otro_grupo = fila[1].get().strip()
                
                # Obtener profesor (índice 5)
                if len(fila) > 5:
                    if hasattr(fila[5], 'get'):
                        otro_profesor = fila[5].get().strip()
                
                # Obtener salón (índice 4)
                if len(fila) > 4:
                    if hasattr(fila[4], 'get'):
                        otro_salon = fila[4].get().strip()
                    elif hasattr(fila[4], 'cget'):
                        otro_salon = fila[4].cget("text").strip()
                
                # Obtener horario del mismo día en la otra fila
                dia_idx = ["L", "M", "X", "J", "V", "S"].index(dia)
                col_idx = 6 + dia_idx
                
                if col_idx < len(fila):
                    otro_horario_str = ""
                    if hasattr(fila[col_idx], 'get'):
                        otro_horario_str = fila[col_idx].get().strip()
                    
                    if otro_horario_str and "-" in otro_horario_str:
                        otro_rango = parsear_rango_horario(otro_horario_str)
                        
                        # Verificar superposición de horarios
                        if rangos_se_superponen(nuevo_rango, otro_rango):
                            # REGLA 1: Mismo grupo no puede tener 2 materias a la misma hora
                            if grupo_actual and otro_grupo and grupo_actual == otro_grupo:
                                choques_potenciales.append({
                                    'tipo': 'GRUPO',
                                    'entidad': grupo_actual,
                                    'dia': dia,
                                    'horario_existente': otro_horario_str,
                                    'horario_nuevo': horario_str,
                                    'programa_conflicto': programa,
                                    'info_conflicto': f"Grupo {otro_grupo} en programa {programa}"
                                })
                            
                            # REGLA 2: Mismo profesor no puede estar en 2 lugares a la vez
                            if profesor_actual and otro_profesor and profesor_actual == otro_profesor:
                                choques_potenciales.append({
                                    'tipo': 'PROFESOR',
                                    'entidad': profesor_actual,
                                    'dia': dia,
                                    'horario_existente': otro_horario_str,
                                    'horario_nuevo': horario_str,
                                    'programa_conflicto': programa,
                                    'info_conflicto': f"Profesor {otro_profesor} en programa {programa}"
                                })
                            
                            # REGLA 3: Mismo salón no puede tener 2 grupos a la misma hora
                            if salon_actual and otro_salon and salon_actual == otro_salon:
                                choques_potenciales.append({
                                    'tipo': 'SALÓN',
                                    'entidad': salon_actual,
                                    'dia': dia,
                                    'horario_existente': otro_horario_str,
                                    'horario_nuevo': horario_str,
                                    'programa_conflicto': programa,
                                    'info_conflicto': f"Salón {otro_salon} en programa {programa}"
                                })
    
    return choques_potenciales

# ==================================================
# VALIDACIÓN DE HORAS POR MODALIDAD
# ==================================================
def validar_horas_por_modalidad(filas_por_programa, fila_actual=None):
    """
    Valida que cada grupo cumpla con las horas requeridas según su modalidad.
    
    Args:
        filas_por_programa: Todas las filas de horarios
        fila_actual: Fila específica a validar (si es None, valida todas)
    
    Returns:
        Diccionario con resultados de validación por grupo
    """
    resultados = {}
    
    # Recolectar horas por grupo
    horas_por_grupo = defaultdict(float)
    modalidad_por_grupo = {}
    
    for programa, filas in filas_por_programa.items():
        for fila in filas:
            # Obtener información del grupo
            grupo = ""
            modalidad = ""
            
            if len(fila) > 1:
                if hasattr(fila[1], 'cget'):
                    grupo = fila[1].cget("text").strip()
                elif hasattr(fila[1], 'get'):
                    grupo = fila[1].get().strip()
            
            if len(fila) > 2:
                if hasattr(fila[2], 'cget'):
                    modalidad = fila[2].cget("text").strip()
                elif hasattr(fila[2], 'get'):
                    modalidad = fila[2].get().strip()
            
            if not grupo or not modalidad:
                continue
            
            # Guardar modalidad del grupo
            modalidad_por_grupo[grupo] = modalidad
            
            # Calcular horas de esta fila
            horas_fila = 0
            for dia_idx in range(6):  # Días L a S
                col_idx = 6 + dia_idx
                if col_idx < len(fila):
                    horario_str = ""
                    if hasattr(fila[col_idx], 'get'):
                        horario_str = fila[col_idx].get().strip()
                    
                    if horario_str and "-" in horario_str:
                        rango = parsear_rango_horario(horario_str)
                        inicio, fin = rango
                        if fin > inicio:
                            horas_fila += (fin - inicio) / 60.0
            
            # Sumar horas al grupo
            horas_por_grupo[grupo] += horas_fila
    
    # Validar cada grupo
    for grupo, horas_totales in horas_por_grupo.items():
        modalidad = modalidad_por_grupo.get(grupo, "Escolarizado")
        horas_requeridas = HORAS_POR_MODALIDAD.get(modalidad, 5.0)
        
        # Determinar si cumple
        cumple = abs(horas_totales - horas_requeridas) < 0.1  # Margen de error de 0.1 horas
        
        resultados[grupo] = {
            'horas_totales': horas_totales,
            'horas_requeridas': horas_requeridas,
            'modalidad': modalidad,
            'cumple': cumple,
            'diferencia': horas_totales - horas_requeridas
        }
    
    return resultados

def obtener_horas_grupo_actual(fila_actual):
    """
    Obtiene las horas totales del grupo en la fila actual.
    
    Args:
        fila_actual: La fila que se está editando
    
    Returns:
        Tupla (horas_totales, modalidad, cumple)
    """
    # Obtener información del grupo
    grupo = ""
    modalidad = ""
    
    if len(fila_actual) > 1:
        if hasattr(fila_actual[1], 'cget'):
            grupo = fila_actual[1].cget("text").strip()
    
    if len(fila_actual) > 2:
        if hasattr(fila_actual[2], 'cget'):
            modalidad = fila_actual[2].cget("text").strip()
    
    if not grupo or not modalidad:
        return 0.0, "Desconocida", False
    
    # Calcular horas de esta fila
    horas_fila = 0
    for dia_idx in range(6):  # Días L a S
        col_idx = 6 + dia_idx
        if col_idx < len(fila_actual):
            horario_str = ""
            if hasattr(fila_actual[col_idx], 'get'):
                horario_str = fila_actual[col_idx].get().strip()
            
            if horario_str and "-" in horario_str:
                rango = parsear_rango_horario(horario_str)
                inicio, fin = rango
                if fin > inicio:
                    horas_fila += (fin - inicio) / 60.0
    
    # Obtener horas requeridas
    horas_requeridas = HORAS_POR_MODALIDAD.get(modalidad, 5.0)
    cumple = abs(horas_fila - horas_requeridas) < 0.1
    
    return horas_fila, modalidad, cumple, horas_requeridas

# ==================================================
# FUNCIÓN PRINCIPAL DE VALIDACIÓN
# ==================================================
def validar_todo(filas_por_programa, fila_actual=None):
    """
    Realiza todas las validaciones y retorna un resumen.
    
    Args:
        filas_por_programa: Todas las filas de horarios
        fila_actual: Fila específica a validar
    
    Returns:
        Diccionario con resultados de todas las validaciones
    """
    # Detectar choques
    choques = detectar_choques_horarios(filas_por_programa, fila_actual)
    
    # Validar horas por modalidad
    validacion_horas = validar_horas_por_modalidad(filas_por_programa, fila_actual)
    
    # Contar resultados
    total_choques = len(choques)
    choques_grupo = sum(1 for c in choques if c['tipo'] == 'GRUPO')
    choques_profesor = sum(1 for c in choques if c['tipo'] == 'PROFESOR')
    choques_salon = sum(1 for c in choques if c['tipo'] == 'SALÓN')
    
    grupos_validados = len(validacion_horas)
    grupos_cumplen = sum(1 for v in validacion_horas.values() if v['cumple'])
    
    return {
        'choques': {
            'total': total_choques,
            'grupo': choques_grupo,
            'profesor': choques_profesor,
            'salon': choques_salon,
            'detalles': choques
        },
        'horas': {
            'total_grupos': grupos_validados,
            'grupos_cumplen': grupos_cumplen,
            'detalles': validacion_horas
        },
        'resumen': f"Choques: {total_choques} | Grupos válidos: {grupos_cumplen}/{grupos_validados}"
    }
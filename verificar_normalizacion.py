"""
Script de Verificación de Normalización para Spaced Repetition

Este script verifica que todas las preguntas en el sistema tengan los campos
necesarios para repetición espaciada.

Uso:
    python verificar_normalizacion.py
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

# Campos requeridos para Spaced Repetition
CAMPOS_REQUERIDOS = {
    'id': str,
    'ease_factor': (int, float),
    'interval': (int, float),
    'repetitions': int,
    'last_review': (type(None), str),
    'next_review': (type(None), str),
    'state': str
}

# Campos básicos de pregunta (deben existir también)
CAMPOS_BASICOS = ['tipo', 'pregunta', 'puntos']


def verificar_pregunta(pregunta: dict, index: int, contexto: str) -> Tuple[bool, List[str]]:
    """
    Verifica que una pregunta tenga todos los campos necesarios.
    
    Returns:
        (valida, errores) - Tupla con booleano y lista de errores
    """
    errores = []
    
    # Verificar campos básicos
    for campo in CAMPOS_BASICOS:
        if campo not in pregunta:
            errores.append(f"  ❌ Falta campo básico '{campo}' en pregunta #{index} de {contexto}")
    
    # Verificar campos de Spaced Repetition
    for campo, tipo_esperado in CAMPOS_REQUERIDOS.items():
        if campo not in pregunta:
            errores.append(f"  ❌ Falta campo SR '{campo}' en pregunta #{index} de {contexto}")
        else:
            # Verificar tipo
            valor = pregunta[campo]
            if not isinstance(valor, tipo_esperado):
                errores.append(
                    f"  ⚠️  Campo '{campo}' tiene tipo incorrecto en pregunta #{index} de {contexto}: "
                    f"{type(valor).__name__} (esperado: {tipo_esperado})"
                )
    
    return len(errores) == 0, errores


def verificar_archivo_practicas(archivo_path: Path) -> Tuple[int, int, List[str]]:
    """
    Verifica todas las preguntas en un archivo de prácticas.
    
    Returns:
        (total_preguntas, preguntas_validas, errores)
    """
    total_preguntas = 0
    preguntas_validas = 0
    todos_errores = []
    
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            practicas = json.load(f)
        
        if not isinstance(practicas, list):
            todos_errores.append(f"❌ {archivo_path} no es un array válido")
            return 0, 0, todos_errores
        
        for idx_practica, practica in enumerate(practicas):
            practica_id = practica.get('id', f'practica_{idx_practica}')
            
            if 'preguntas' not in practica:
                todos_errores.append(f"⚠️  Práctica {practica_id} no tiene campo 'preguntas'")
                continue
            
            if not isinstance(practica['preguntas'], list):
                todos_errores.append(f"❌ Práctica {practica_id} tiene 'preguntas' no-array")
                continue
            
            for idx_pregunta, pregunta in enumerate(practica['preguntas']):
                total_preguntas += 1
                contexto = f"{archivo_path.parent.name}/{practica_id}"
                valida, errores = verificar_pregunta(pregunta, idx_pregunta + 1, contexto)
                
                if valida:
                    preguntas_validas += 1
                else:
                    todos_errores.extend(errores)
    
    except json.JSONDecodeError as e:
        todos_errores.append(f"❌ Error JSON en {archivo_path}: {e}")
    except Exception as e:
        todos_errores.append(f"❌ Error leyendo {archivo_path}: {e}")
    
    return total_preguntas, preguntas_validas, todos_errores


def verificar_sistema():
    """Verifica todo el sistema de prácticas y exámenes."""
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE NORMALIZACIÓN PARA SPACED REPETITION")
    print("=" * 80)
    print()
    
    extracciones_path = Path("extracciones")
    
    if not extracciones_path.exists():
        print("❌ Carpeta 'extracciones' no encontrada")
        return
    
    # Estadísticas globales
    total_archivos = 0
    total_preguntas_global = 0
    total_validas_global = 0
    todos_errores_global = []
    
    # 1. Verificar practicas.json
    print("📁 Buscando archivos practicas.json...")
    archivos_practicas = list(extracciones_path.rglob("practicas.json"))
    print(f"   Encontrados: {len(archivos_practicas)}")
    print()
    
    for archivo in archivos_practicas:
        total_archivos += 1
        print(f"📄 Verificando: {archivo}")
        total, validas, errores = verificar_archivo_practicas(archivo)
        total_preguntas_global += total
        total_validas_global += validas
        
        if total > 0:
            porcentaje = (validas / total) * 100
            print(f"   ✅ {validas}/{total} preguntas válidas ({porcentaje:.1f}%)")
        else:
            print(f"   ⚠️  Sin preguntas")
        
        if errores:
            todos_errores_global.extend(errores)
            print(f"   ⚠️  {len(errores)} errores encontrados")
            for error in errores[:3]:  # Mostrar solo los primeros 3
                print(error)
            if len(errores) > 3:
                print(f"   ... y {len(errores) - 3} errores más")
        
        print()
    
    # 2. Verificar examenes.json
    print("📁 Buscando archivos examenes.json...")
    archivos_examenes = list(extracciones_path.rglob("examenes.json"))
    print(f"   Encontrados: {len(archivos_examenes)}")
    print()
    
    for archivo in archivos_examenes:
        total_archivos += 1
        print(f"📄 Verificando: {archivo}")
        total, validas, errores = verificar_archivo_practicas(archivo)  # Usa la misma función
        total_preguntas_global += total
        total_validas_global += validas
        
        if total > 0:
            porcentaje = (validas / total) * 100
            print(f"   ✅ {validas}/{total} preguntas válidas ({porcentaje:.1f}%)")
        else:
            print(f"   ⚠️  Sin preguntas")
        
        if errores:
            todos_errores_global.extend(errores)
            print(f"   ⚠️  {len(errores)} errores encontrados")
            for error in errores[:3]:
                print(error)
            if len(errores) > 3:
                print(f"   ... y {len(errores) - 3} errores más")
        
        print()
    
    # Resumen final
    print("=" * 80)
    print("📊 RESUMEN GLOBAL")
    print("=" * 80)
    print(f"📁 Archivos analizados: {total_archivos}")
    print(f"📝 Total preguntas: {total_preguntas_global}")
    print(f"✅ Preguntas válidas: {total_validas_global}")
    
    if total_preguntas_global > 0:
        porcentaje_global = (total_validas_global / total_preguntas_global) * 100
        print(f"📈 Porcentaje de normalización: {porcentaje_global:.1f}%")
        
        if porcentaje_global == 100:
            print()
            print("🎉 ¡PERFECTO! Todas las preguntas están normalizadas para Spaced Repetition")
        elif porcentaje_global >= 90:
            print()
            print("✅ Excelente - La mayoría de preguntas están normalizadas")
        elif porcentaje_global >= 70:
            print()
            print("⚠️  Advertencia - Algunas preguntas necesitan normalización")
        else:
            print()
            print("❌ Crítico - Muchas preguntas faltan normalizar")
    
    if todos_errores_global:
        print()
        print(f"⚠️  Total de errores: {len(todos_errores_global)}")
        print()
        print("🔧 RECOMENDACIONES:")
        print("   1. Reinicia el servidor para aplicar los cambios")
        print("   2. Genera una nueva práctica o examen")
        print("   3. Carga las prácticas desde el frontend")
        print("   4. Las preguntas se normalizarán automáticamente")
    
    print("=" * 80)


if __name__ == "__main__":
    verificar_sistema()

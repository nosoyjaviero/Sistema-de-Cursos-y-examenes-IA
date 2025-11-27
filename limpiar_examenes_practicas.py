"""
Script para eliminar TODOS los exámenes y prácticas del sistema
ADVERTENCIA: Esta acción NO se puede deshacer
"""

import json
from pathlib import Path
import shutil

EXTRACCIONES_PATH = Path("extracciones")

def limpiar_todo():
    """Elimina todos los archivos de exámenes y prácticas"""
    
    print("\n" + "="*70)
    print("⚠️  ELIMINACIÓN MASIVA DE EXÁMENES Y PRÁCTICAS")
    print("="*70)
    
    confirmacion = input("\n¿Estás SEGURO de eliminar TODOS los exámenes y prácticas? (escribe 'SI' para confirmar): ")
    
    if confirmacion != "SI":
        print("❌ Operación cancelada")
        return
    
    archivos_eliminados = 0
    carpetas_limpiadas = 0
    
    if not EXTRACCIONES_PATH.exists():
        print("📁 No existe la carpeta extracciones/")
        return
    
    print(f"\n🔍 Buscando archivos en: {EXTRACCIONES_PATH.absolute()}")
    
    # Buscar y eliminar recursivamente
    for carpeta in EXTRACCIONES_PATH.rglob("*"):
        if carpeta.is_dir():
            try:
                # 1. Eliminar exámenes individuales (examen_*.json)
                for archivo in carpeta.glob("examen_*.json"):
                    print(f"   🗑️  Eliminando: {archivo.relative_to(EXTRACCIONES_PATH)}")
                    archivo.unlink()
                    archivos_eliminados += 1
                
                # 2. Eliminar ExamenGeneral.json
                examen_general = carpeta / "ExamenGeneral.json"
                if examen_general.exists():
                    print(f"   🗑️  Eliminando: {examen_general.relative_to(EXTRACCIONES_PATH)}")
                    examen_general.unlink()
                    archivos_eliminados += 1
                
                # 3. Eliminar examenes.json (legacy)
                examenes_json = carpeta / "examenes.json"
                if examenes_json.exists():
                    print(f"   🗑️  Eliminando: {examenes_json.relative_to(EXTRACCIONES_PATH)}")
                    examenes_json.unlink()
                    archivos_eliminados += 1
                
                # 4. Eliminar practicasArchivos.json
                practicas_archivos = carpeta / "practicasArchivos.json"
                if practicas_archivos.exists():
                    print(f"   🗑️  Eliminando: {practicas_archivos.relative_to(EXTRACCIONES_PATH)}")
                    practicas_archivos.unlink()
                    archivos_eliminados += 1
                
                # 5. Eliminar practicas.json (legacy)
                practicas_json = carpeta / "practicas.json"
                if practicas_json.exists():
                    print(f"   🗑️  Eliminando: {practicas_json.relative_to(EXTRACCIONES_PATH)}")
                    practicas_json.unlink()
                    archivos_eliminados += 1
                
                # 6. Eliminar carpeta resultados_examenes/
                resultados_examenes = carpeta / "resultados_examenes"
                if resultados_examenes.exists() and resultados_examenes.is_dir():
                    print(f"   📂 Eliminando carpeta: {resultados_examenes.relative_to(EXTRACCIONES_PATH)}")
                    shutil.rmtree(resultados_examenes)
                    carpetas_limpiadas += 1
                
                # 7. Eliminar carpeta resultados_practicas/
                resultados_practicas = carpeta / "resultados_practicas"
                if resultados_practicas.exists() and resultados_practicas.is_dir():
                    print(f"   📂 Eliminando carpeta: {resultados_practicas.relative_to(EXTRACCIONES_PATH)}")
                    shutil.rmtree(resultados_practicas)
                    carpetas_limpiadas += 1
                
                # 8. Eliminar carpeta examenes_progreso/
                examenes_progreso = carpeta / "examenes_progreso"
                if examenes_progreso.exists() and examenes_progreso.is_dir():
                    print(f"   📂 Eliminando carpeta: {examenes_progreso.relative_to(EXTRACCIONES_PATH)}")
                    shutil.rmtree(examenes_progreso)
                    carpetas_limpiadas += 1
                    
            except Exception as e:
                print(f"   ❌ Error procesando {carpeta}: {e}")
    
    # Eliminar carpeta Examenes_Generales completa si existe
    examenes_generales = EXTRACCIONES_PATH / "Examenes_Generales"
    if examenes_generales.exists():
        print(f"\n📂 Eliminando carpeta completa: Examenes_Generales/")
        shutil.rmtree(examenes_generales)
        carpetas_limpiadas += 1
    
    # Eliminar carpeta Practicas_Generales completa si existe
    practicas_generales = EXTRACCIONES_PATH / "Practicas_Generales"
    if practicas_generales.exists():
        print(f"📂 Eliminando carpeta completa: Practicas_Generales/")
        shutil.rmtree(practicas_generales)
        carpetas_limpiadas += 1
    
    print("\n" + "="*70)
    print("✅ LIMPIEZA COMPLETADA")
    print("="*70)
    print(f"📊 Archivos eliminados: {archivos_eliminados}")
    print(f"📊 Carpetas eliminadas: {carpetas_limpiadas}")
    print("\n💡 Recarga el calendario en la aplicación para ver los cambios")
    print("="*70 + "\n")

if __name__ == "__main__":
    limpiar_todo()

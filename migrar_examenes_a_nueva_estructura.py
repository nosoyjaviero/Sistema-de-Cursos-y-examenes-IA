"""
Script para migrar exámenes de la estructura antigua a la nueva

ANTIGUA: extracciones/{carpeta}/resultados_examenes/examen_*.json
NUEVA:   examenes/{carpeta}/examen_*.json

Uso:
    python migrar_examenes_a_nueva_estructura.py
"""

import json
import shutil
from pathlib import Path

EXTRACCIONES_PATH = Path("extracciones")
EXAMENES_PATH = Path("examenes")

def migrar_examenes():
    """Migra todos los exámenes de resultados_examenes/ a examenes/"""
    
    examenes_migrados = 0
    errores = 0
    
    print("🔄 Iniciando migración de exámenes...")
    print(f"   Desde: extracciones/{{carpeta}}/resultados_examenes/")
    print(f"   Hacia: examenes/{{carpeta}}/\n")
    
    # Buscar todas las carpetas resultados_examenes
    for resultados_examenes in EXTRACCIONES_PATH.rglob("resultados_examenes"):
        if not resultados_examenes.is_dir():
            continue
        
        # Obtener la carpeta padre (la carpeta del curso)
        carpeta_curso = resultados_examenes.parent.relative_to(EXTRACCIONES_PATH)
        carpeta_destino = EXAMENES_PATH / carpeta_curso
        
        print(f"\n📂 Procesando: {carpeta_curso}")
        
        # Crear carpeta destino si no existe
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        
        # Migrar todos los archivos examen_*.json
        for archivo_examen in resultados_examenes.glob("examen_*.json"):
            try:
                # Leer el examen
                with open(archivo_examen, "r", encoding="utf-8") as f:
                    examen = json.load(f)
                
                # Verificar que NO sea práctica
                if examen.get("es_practica"):
                    print(f"   ⏭️  Omitiendo práctica: {archivo_examen.name}")
                    continue
                
                # Archivo destino
                archivo_destino = carpeta_destino / archivo_examen.name
                
                # Verificar si ya existe
                if archivo_destino.exists():
                    print(f"   ⚠️  Ya existe: {archivo_examen.name}")
                    continue
                
                # Copiar el archivo
                shutil.copy2(archivo_examen, archivo_destino)
                print(f"   ✅ Migrado: {archivo_examen.name}")
                examenes_migrados += 1
                
            except Exception as e:
                print(f"   ❌ Error migrando {archivo_examen.name}: {e}")
                errores += 1
    
    print(f"\n{'='*70}")
    print(f"✅ Migración completada!")
    print(f"   📊 Exámenes migrados: {examenes_migrados}")
    if errores > 0:
        print(f"   ❌ Errores: {errores}")
    print(f"{'='*70}\n")
    
    if examenes_migrados > 0:
        print("⚠️  NOTA: Los archivos originales NO se eliminaron.")
        print("   Puedes eliminarlos manualmente después de verificar que todo funciona.")
        print(f"   Carpetas antiguas: extracciones/*/resultados_examenes/\n")

if __name__ == "__main__":
    migrar_examenes()

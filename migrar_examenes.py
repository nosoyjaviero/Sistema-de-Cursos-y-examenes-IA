"""
Script para migrar exámenes de extracciones/ a examenes/
Mantiene la misma estructura de carpetas
"""
from pathlib import Path
import shutil
import json

def migrar_examenes():
    """Migra todos los exámenes a la nueva estructura"""
    extracciones = Path("extracciones")
    examenes_base = Path("examenes")
    
    total_completados = 0
    total_progreso = 0
    
    print("🔄 Iniciando migración de exámenes...")
    print("=" * 60)
    
    # Buscar todos los exámenes completados directamente
    for archivo_examen in extracciones.rglob("examen_*.json"):
        try:
            # Obtener carpeta del examen
            carpeta = archivo_examen.parent
            
            # Obtener ruta relativa desde extracciones/
            ruta_relativa = carpeta.relative_to(extracciones)
            
            # Si está en resultados_examenes o examenes_progreso, subir un nivel
            if carpeta.name in ["resultados_examenes", "examenes_progreso", "resultados"]:
                ruta_relativa = ruta_relativa.parent
            
            # Crear carpeta destino en examenes/
            carpeta_destino = examenes_base / ruta_relativa
            carpeta_destino.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivo
            destino = carpeta_destino / archivo_examen.name
            if not destino.exists():  # Evitar duplicados
                shutil.copy2(archivo_examen, destino)
                total_completados += 1
                print(f"✅ Completado: {ruta_relativa} / {archivo_examen.name}")
        except Exception as e:
            print(f"❌ Error con {archivo_examen}: {e}")
    
    # Buscar exámenes en progreso
    for archivo_progreso in extracciones.rglob("examen_progreso_*.json"):
        try:
            # Obtener carpeta del examen
            carpeta = archivo_progreso.parent
            
            # Obtener ruta relativa desde extracciones/
            ruta_relativa = carpeta.relative_to(extracciones)
            
            # Si está en examenes_progreso, subir un nivel
            if carpeta.name == "examenes_progreso":
                ruta_relativa = ruta_relativa.parent
            
            # Crear carpeta destino
            carpeta_destino = examenes_base / ruta_relativa / "examenes_progreso"
            carpeta_destino.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivo
            destino = carpeta_destino / archivo_progreso.name
            if not destino.exists():  # Evitar duplicados
                shutil.copy2(archivo_progreso, destino)
                total_progreso += 1
                print(f"📝 En progreso: {ruta_relativa} / {archivo_progreso.name}")
        except Exception as e:
            print(f"❌ Error con {archivo_progreso}: {e}")
    
    print("=" * 60)
    print(f"✅ Migración completada!")
    print(f"   📊 {total_completados} exámenes completados migrados")
    print(f"   📝 {total_progreso} exámenes en progreso migrados")
    print(f"\n💡 Los archivos originales se mantienen en extracciones/")
    print(f"   Puedes eliminarlos manualmente si lo deseas")

if __name__ == "__main__":
    migrar_examenes()

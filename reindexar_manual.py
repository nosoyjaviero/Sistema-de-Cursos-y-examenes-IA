#!/usr/bin/env python3
"""
Script para reindexar manualmente el buscador IA
Útil cuando cambias la carpeta de indexación o necesitas limpiar índices
"""
import os
import shutil
from buscador_ia import ConfigBuscador, IndexadorLocal

def limpiar_indices():
    """Elimina todos los índices existentes"""
    config = ConfigBuscador()
    
    if os.path.exists(config.RUTA_INDICE):
        print(f"🗑️  Eliminando índices en: {config.RUTA_INDICE}")
        shutil.rmtree(config.RUTA_INDICE)
        print("   ✓ Índices eliminados")
    else:
        print("   ℹ️  No había índices previos")

def reindexar_todo():
    """Reindexación completa desde cero"""
    config = ConfigBuscador()
    
    print("\n" + "="*60)
    print("🔄 REINDEXACIÓN COMPLETA DEL BUSCADOR IA")
    print("="*60)
    print()
    
    # Mostrar configuración
    print("📂 Carpetas configuradas para indexar:")
    for carpeta in config.CARPETAS_RAIZ:
        if os.path.exists(carpeta):
            print(f"   ✓ {carpeta}")
        else:
            print(f"   ❌ {carpeta} (NO EXISTE)")
    print()
    
    print(f"📄 Extensiones de archivo: {config.EXTENSIONES_TEXTO}")
    print(f"🤖 Modelo: {config.MODELO_EMBEDDINGS}")
    print(f"⚡ GPU: {'Sí' if config.USAR_GPU else 'No'}")
    print()
    
    # Eliminar índices viejos
    limpiar_indices()
    print()
    
    # Crear indexador y ejecutar indexación completa
    print("🔍 Iniciando indexación completa...")
    indexador = IndexadorLocal(config)
    
    archivos_procesados, chunks_indexados = indexador.indexar(incremental=False)
    
    print()
    print("="*60)
    print("✅ REINDEXACIÓN COMPLETADA")
    print("="*60)
    print()
    print(f"📊 Estadísticas finales:")
    print(f"   • Archivos indexados: {archivos_procesados}")
    print(f"   • Fragmentos de texto: {chunks_indexados}")
    print(f"   • Carpetas escaneadas: {len(config.CARPETAS_RAIZ)}")
    print()
    print("💡 Ahora puedes buscar en el frontend sin necesidad de 'Actualizar Índice'")
    print()

if __name__ == "__main__":
    try:
        reindexar_todo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Reindexación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

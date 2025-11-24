"""
Script para crear el índice inicial del buscador
Ejecuta esto UNA VEZ antes de usar el buscador
"""

from buscador_ia import ConfigBuscador, IndexadorLocal

print("=" * 60)
print("🚀 CREANDO ÍNDICE INICIAL PARA BUSCADOR IA")
print("=" * 60)

# Crear configuración
config = ConfigBuscador()

print("\n📂 Carpetas a indexar:")
for carpeta in config.CARPETAS_RAIZ:
    print(f"  - {carpeta}")

print(f"\n🧠 Modelo: {config.MODELO_EMBEDDINGS}")
print(f"📦 Chunk size: {config.CHUNK_SIZE} caracteres")
print(f"💾 Índice se guardará en: {config.RUTA_INDICE}")

input("\n⏸️  Presiona ENTER para continuar o CTRL+C para cancelar...")

# Crear indexador
indexador = IndexadorLocal(config)

# Indexar todo (primera vez)
print("\n🔄 Iniciando indexación...")
archivos, chunks = indexador.indexar(incremental=False)

print("\n" + "=" * 60)
print("✅ INDEXACIÓN COMPLETADA")
print("=" * 60)
print(f"📁 Archivos procesados: {archivos}")
print(f"📦 Chunks indexados: {chunks}")
print(f"\n💡 Ahora puedes iniciar el servidor:")
print("   python api_buscador.py")
print("\n🔍 Y usar el buscador desde la interfaz web")

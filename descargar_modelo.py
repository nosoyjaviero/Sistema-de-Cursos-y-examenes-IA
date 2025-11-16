"""
Script para descargar modelos LLM para Examinator
"""
import urllib.request
import sys
from pathlib import Path
import os


MODELOS_RECOMENDADOS = {
    "1": {
        "nombre": "Llama 3.2 3B Instruct (Recomendado - 2.0 GB)",
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "archivo": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "tamaño": "2.0 GB",
        "descripcion": "Modelo pequeño y rápido, ideal para generar preguntas y evaluar respuestas",
        "requiere_auth": False
    },
    "2": {
        "nombre": "Llama 3.1 8B Instruct (Mejor calidad - 4.9 GB) ⭐",
        "url": "https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF/resolve/main/Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "archivo": "Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "tamaño": "4.9 GB",
        "descripcion": "Modelo más grande y preciso, mejor para evaluaciones detalladas",
        "requiere_auth": True
    },
    "3": {
        "nombre": "Qwen 2.5 3B Instruct (Rápido - 2.0 GB)",
        "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
        "archivo": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "tamaño": "2.0 GB",
        "descripcion": "Modelo alternativo excelente para español y tareas educativas",
        "requiere_auth": False
    }
}


def mostrar_progreso(bloque_num, tamaño_bloque, tamaño_total):
    """Muestra barra de progreso de descarga"""
    descargado = bloque_num * tamaño_bloque
    porcentaje = min(100, (descargado / tamaño_total) * 100)
    barra_len = 50
    barra_completa = int(barra_len * porcentaje / 100)
    barra = '█' * barra_completa + '░' * (barra_len - barra_completa)
    
    mb_descargado = descargado / (1024 * 1024)
    mb_total = tamaño_total / (1024 * 1024)
    
    print(f'\r[{barra}] {porcentaje:.1f}% ({mb_descargado:.1f}/{mb_total:.1f} MB)', end='', flush=True)


def descargar_modelo(opcion: str, token: str = None):
    """Descarga el modelo seleccionado"""
    if opcion not in MODELOS_RECOMENDADOS:
        print("Opción inválida")
        return False
    
    modelo = MODELOS_RECOMENDADOS[opcion]
    
    # Crear carpeta de modelos
    carpeta_modelos = Path("modelos")
    carpeta_modelos.mkdir(exist_ok=True)
    
    ruta_destino = carpeta_modelos / modelo["archivo"]
    
    # Verificar si ya existe
    if ruta_destino.exists():
        print(f"\n✓ El modelo ya existe en: {ruta_destino}")
        respuesta = input("¿Descargar de nuevo? (s/n): ")
        if respuesta.lower() != 's':
            return str(ruta_destino)
    
    print(f"\nDescargando: {modelo['nombre']}")
    print(f"Tamaño: {modelo['tamaño']}")
    print(f"Destino: {ruta_destino}\n")
    
    # Verificar si requiere autenticación
    if modelo.get("requiere_auth", False) and not token:
        print("⚠️  Este modelo requiere autenticación de HuggingFace")
        print("\nOpciones:")
        print("1. Descarga manual (Recomendado):")
        print(f"   - Ve a: https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF")
        print(f"   - Haz clic en 'Files and versions'")
        print(f"   - Busca: {modelo['archivo']}")
        print(f"   - Haz clic en el icono de descarga (↓)")
        print(f"   - Guárdalo en: {ruta_destino}")
        print("\n2. Usar huggingface-cli (Más fácil):")
        print("   pip install huggingface-hub")
        print(f"   huggingface-cli download bartowski/Llama-3.1-8B-Instruct-GGUF {modelo['archivo']} --local-dir modelos")
        return None
    
    try:
        # Preparar request con autenticación si es necesaria
        opener = urllib.request.build_opener()
        if token:
            opener.addheaders = [('Authorization', f'Bearer {token}')]
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(
            modelo["url"],
            ruta_destino,
            reporthook=mostrar_progreso
        )
        print(f"\n\n✓ Descarga completada exitosamente!")
        print(f"Modelo guardado en: {ruta_destino}")
        return str(ruta_destino)
    except Exception as e:
        print(f"\n\n✗ Error al descargar: {e}")
        print("\n📥 DESCARGA MANUAL (Más confiable):")
        print(f"1. Ve a: https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF/tree/main")
        print(f"2. Busca el archivo: {modelo['archivo']}")
        print(f"3. Haz clic en el botón de descarga")
        print(f"4. Guárdalo en: {ruta_destino}")
        return None


def main():
    print("="*80)
    print("DESCARGADOR DE MODELOS PARA EXAMINATOR")
    print("="*80)
    print("\nModelos disponibles:\n")
    
    for num, modelo in MODELOS_RECOMENDADOS.items():
        print(f"{num}. {modelo['nombre']}")
        print(f"   Tamaño: {modelo['tamaño']}")
        print(f"   {modelo['descripcion']}\n")
    
    print("Recomendación para tu sistema (24 GB RAM):")
    print("  → Opción 1 para velocidad")
    print("  → Opción 2 para mejor calidad (Tu elección ⭐)\n")
    
    opcion = input("Selecciona una opción (1-3) o 'q' para salir: ").strip()
    
    if opcion.lower() == 'q':
        print("Descarga cancelada")
        return
    
    modelo = MODELOS_RECOMENDADOS.get(opcion)
    if not modelo:
        print("Opción inválida")
        return
    
    # Si es Llama 3.1 8B, usar huggingface-hub
    if opcion == "2":
        print("\n🚀 Descargando con huggingface-hub...")
        try:
            from huggingface_hub import hf_hub_download
            
            carpeta_modelos = Path("modelos")
            carpeta_modelos.mkdir(exist_ok=True)
            ruta_destino = carpeta_modelos / modelo["archivo"]
            
            if ruta_destino.exists():
                print(f"\n✓ El modelo ya existe en: {ruta_destino}")
                respuesta = input("¿Descargar de nuevo? (s/n): ")
                if respuesta.lower() != 's':
                    print(f"\nUsa el modelo con:")
                    print(f'python examinator_interactivo.py "documento.txt" --modelo "{ruta_destino}"')
                    return
            
            print(f"\nDescargando: {modelo['nombre']}")
            print(f"Tamaño: {modelo['tamaño']}")
            print("Esto puede tomar varios minutos...\n")
            
            # Descargar usando huggingface-hub
            archivo_descargado = hf_hub_download(
                repo_id="bartowski/Llama-3.1-8B-Instruct-GGUF",
                filename=modelo["archivo"],
                local_dir=str(carpeta_modelos),
                local_dir_use_symlinks=False
            )
            
            print(f"\n✓ Descarga completada exitosamente!")
            print(f"Modelo guardado en: {archivo_descargado}")
            
            print("\n" + "="*80)
            print("CÓMO USAR EL MODELO")
            print("="*80)
            print("\n1. Extraer PDF:")
            print('   python examinator.py "documento.pdf" --auto-save -v')
            print("\n2. Generar y tomar examen con IA:")
            print(f'   python examinator_interactivo.py "extracciones/2025-11-16/documento.txt" --modelo "{archivo_descargado}"')
            print("\n¡Listo para usar! 🎓")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("\n📥 DESCARGA MANUAL:")
            print("1. Ve a: https://huggingface.co/bartowski/Llama-3.1-8B-Instruct-GGUF")
            print("2. Haz clic en 'Files and versions'")
            print(f"3. Busca: {modelo['archivo']}")
            print("4. Haz clic en el botón de descarga (↓)")
            print(f"5. Guarda el archivo en: modelos\\{modelo['archivo']}")
    else:
        # Para otros modelos, usar el método anterior
        ruta_modelo = descargar_modelo(opcion)
        
        if ruta_modelo:
            print("\n" + "="*80)
            print("CÓMO USAR EL MODELO")
            print("="*80)
            print("\n1. Extraer PDF:")
            print('   python examinator.py "documento.pdf" --auto-save -v')
            print("\n2. Generar y tomar examen con IA:")
            print(f'   python examinator_interactivo.py "extracciones/2025-11-16/documento.txt" --modelo "{ruta_modelo}"')
            print("\n¡Listo para usar! 🎓")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDescarga cancelada por el usuario.")
        sys.exit(1)

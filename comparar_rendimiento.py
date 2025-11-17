"""
Script para comparar rendimiento: Ollama vs llama-cpp-python
"""
import time
import requests
from pathlib import Path


def test_ollama():
    """Test de velocidad con Ollama"""
    print("\n" + "="*60)
    print("🧪 TEST: Ollama (GPU automática)")
    print("="*60)
    
    try:
        # Verificar conexión
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            print("❌ Ollama no está corriendo")
            return None
        
        modelos = response.json().get('models', [])
        if not modelos:
            print("❌ No hay modelos en Ollama")
            return None
        
        modelo = modelos[0]['name']
        print(f"📦 Modelo: {modelo}")
        
        # Test de generación
        prompt = """<|begin_of_text|><|start_header_id|>user<|end_header_id|>

Escribe una lista de 3 conceptos clave sobre Python.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        print("⏱️  Generando...")
        inicio = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": modelo,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 100
                }
            },
            timeout=60
        )
        
        fin = time.time()
        duracion = fin - inicio
        
        if response.status_code == 200:
            respuesta = response.json()['response']
            tokens = len(respuesta.split())
            tokens_por_segundo = tokens / duracion
            
            print(f"\n✅ Generación exitosa")
            print(f"⏱️  Tiempo: {duracion:.2f} segundos")
            print(f"📝 Tokens: ~{tokens}")
            print(f"🚀 Velocidad: {tokens_por_segundo:.2f} tokens/s")
            print(f"\n💬 Respuesta:\n{respuesta[:200]}...")
            
            # Verificar uso de GPU
            ps_response = requests.get("http://localhost:11434/api/ps", timeout=2)
            if ps_response.status_code == 200:
                procesos = ps_response.json().get('models', [])
                if procesos:
                    for proc in procesos:
                        if proc.get('name') == modelo:
                            print(f"\n🎮 GPU: {proc.get('details', {}).get('parameter_size', 'N/A')}")
            
            return duracion
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_llama_cpp():
    """Test de velocidad con llama-cpp-python"""
    print("\n" + "="*60)
    print("🧪 TEST: llama-cpp-python")
    print("="*60)
    
    try:
        from llama_cpp import Llama
        
        # Buscar modelo
        modelos_dir = Path("modelos")
        modelos = list(modelos_dir.glob("*.gguf"))
        
        if not modelos:
            print("❌ No hay modelos GGUF en carpeta modelos/")
            return None
        
        modelo_path = str(modelos[0])
        print(f"📦 Modelo: {modelo_path}")
        
        # Cargar con GPU
        print("🔄 Cargando modelo con GPU...")
        inicio_carga = time.time()
        
        llm = Llama(
            model_path=modelo_path,
            n_ctx=2048,
            n_threads=6,
            n_gpu_layers=35,  # Usar GPU
            verbose=False
        )
        
        fin_carga = time.time()
        print(f"✅ Modelo cargado en {fin_carga - inicio_carga:.2f}s")
        
        # Test de generación
        prompt = "Escribe una lista de 3 conceptos clave sobre Python."
        
        print("⏱️  Generando...")
        inicio = time.time()
        
        respuesta = llm(
            prompt,
            max_tokens=100,
            temperature=0.7,
            stop=["<|eot_id|>"]
        )
        
        fin = time.time()
        duracion = fin - inicio
        
        texto = respuesta['choices'][0]['text']
        tokens = len(texto.split())
        tokens_por_segundo = tokens / duracion
        
        print(f"\n✅ Generación exitosa")
        print(f"⏱️  Tiempo: {duracion:.2f} segundos")
        print(f"📝 Tokens: ~{tokens}")
        print(f"🚀 Velocidad: {tokens_por_segundo:.2f} tokens/s")
        print(f"\n💬 Respuesta:\n{texto[:200]}...")
        
        del llm  # Liberar memoria
        return duracion
        
    except ImportError:
        print("❌ llama-cpp-python no está instalado")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("\n" + "="*60)
    print("⚡ COMPARACIÓN DE RENDIMIENTO: GPU vs CPU")
    print("="*60)
    
    print("\n📊 Este test compara:")
    print("  • Ollama: Detecta y usa GPU automáticamente")
    print("  • llama-cpp-python: Requiere configuración manual")
    
    # Test Ollama
    tiempo_ollama = test_ollama()
    
    # Pausa
    print("\n" + "-"*60)
    input("Presiona Enter para continuar con llama-cpp-python...")
    
    # Test llama-cpp-python
    tiempo_llama = test_llama_cpp()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    if tiempo_ollama:
        print(f"✅ Ollama: {tiempo_ollama:.2f}s")
    else:
        print("❌ Ollama: No disponible")
    
    if tiempo_llama:
        print(f"✅ llama-cpp-python: {tiempo_llama:.2f}s")
    else:
        print("❌ llama-cpp-python: No disponible")
    
    if tiempo_ollama and tiempo_llama:
        if tiempo_ollama < tiempo_llama:
            mejora = ((tiempo_llama - tiempo_ollama) / tiempo_llama) * 100
            print(f"\n🏆 Ollama es {mejora:.1f}% más rápido")
        else:
            mejora = ((tiempo_ollama - tiempo_llama) / tiempo_ollama) * 100
            print(f"\n🏆 llama-cpp-python es {mejora:.1f}% más rápido")
    
    print("\n💡 RECOMENDACIÓN:")
    if tiempo_ollama:
        print("   Usa Ollama para:")
        print("   ✅ GPU automática (sin configuración)")
        print("   ✅ Mejor gestión de modelos")
        print("   ✅ Más fácil de usar")
    
    if tiempo_llama:
        print("\n   Usa llama-cpp-python para:")
        print("   ✅ Control fino sobre parámetros")
        print("   ✅ Integración directa en Python")
        print("   ✅ Offline sin servicios externos")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

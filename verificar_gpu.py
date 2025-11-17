"""
Script para verificar si la GPU está disponible y configurada correctamente
"""

print("="*60)
print("🔍 DIAGNÓSTICO DE GPU PARA LLAMA-CPP-PYTHON")
print("="*60)

# 1. Verificar llama-cpp-python
print("\n1️⃣ Verificando llama-cpp-python...")
try:
    import llama_cpp
    print(f"   ✅ llama-cpp-python instalado")
    print(f"   📦 Versión: {llama_cpp.__version__}")
    
    # Verificar si fue compilado con CUDA
    try:
        # Intentar acceder a funciones CUDA
        from llama_cpp import llama_cpp
        print(f"   ℹ️  Módulo llama_cpp importado correctamente")
    except Exception as e:
        print(f"   ⚠️  No se pudo importar llama_cpp: {e}")
        
except ImportError:
    print(f"   ❌ llama-cpp-python NO está instalado")
    print(f"   💡 Instalar con: pip install llama-cpp-python")

# 2. Verificar PyTorch y CUDA
print("\n2️⃣ Verificando PyTorch y CUDA...")
try:
    import torch
    print(f"   ✅ PyTorch instalado")
    print(f"   📦 Versión: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"   ✅ CUDA disponible")
        print(f"   🎮 GPU: {torch.cuda.get_device_name(0)}")
        print(f"   📊 VRAM Total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        print(f"   🔢 Compute Capability: {torch.cuda.get_device_capability(0)}")
        print(f"   📍 CUDA Version: {torch.version.cuda}")
    else:
        print(f"   ⚠️  CUDA NO disponible en PyTorch")
        print(f"   💡 Puede que PyTorch esté instalado sin CUDA")
        
except ImportError:
    print(f"   ℹ️  PyTorch no está instalado (no es obligatorio)")

# 3. Verificar variables de entorno
print("\n3️⃣ Verificando variables de entorno...")
import os

cuda_vars = ['CUDA_PATH', 'CUDA_HOME', 'CUDA_VISIBLE_DEVICES']
for var in cuda_vars:
    valor = os.environ.get(var)
    if valor:
        print(f"   ✅ {var}: {valor}")
    else:
        print(f"   ⚠️  {var} no está configurada")

# 4. Intentar cargar un modelo con GPU
print("\n4️⃣ Probando carga de modelo con GPU...")
try:
    from llama_cpp import Llama
    from pathlib import Path
    
    # Buscar un modelo
    modelo_path = None
    modelos_dir = Path("modelos")
    if modelos_dir.exists():
        modelos = list(modelos_dir.glob("*.gguf"))
        if modelos:
            modelo_path = str(modelos[0])
            print(f"   📁 Modelo encontrado: {modelo_path}")
            
            print(f"   🔄 Intentando cargar con n_gpu_layers=1...")
            try:
                llm = Llama(
                    model_path=modelo_path,
                    n_ctx=512,
                    n_gpu_layers=1,
                    verbose=True
                )
                print(f"   ✅ Modelo cargado con GPU")
                
                # Hacer una inferencia de prueba
                print(f"   🧪 Probando inferencia...")
                respuesta = llm("Hola", max_tokens=5)
                print(f"   ✅ Inferencia exitosa")
                
                del llm  # Liberar memoria
                
            except Exception as e:
                print(f"   ❌ Error cargando con GPU: {e}")
                print(f"   💡 Probablemente llama-cpp-python no fue compilado con CUDA")
        else:
            print(f"   ⚠️  No se encontraron modelos .gguf en {modelos_dir}")
    else:
        print(f"   ⚠️  Carpeta 'modelos' no existe")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Recomendaciones
print("\n" + "="*60)
print("📋 RECOMENDACIONES")
print("="*60)

print("""
Para usar GPU con llama-cpp-python necesitas:

1. Tener una GPU NVIDIA con CUDA instalado
2. Instalar llama-cpp-python compilado con CUDA:
   
   OPCIÓN A (precompilado con CUDA):
   pip uninstall llama-cpp-python -y
   pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
   
   OPCIÓN B (compilar desde código):
   $env:CMAKE_ARGS="-DLLAMA_CUBLAS=on"
   pip install llama-cpp-python --force-reinstall --no-cache-dir

3. Verificar que CUDA funciona:
   nvidia-smi

Si ves tu GPU en nvidia-smi pero llama-cpp no la usa,
probablemente necesitas reinstalar llama-cpp-python con soporte CUDA.
""")

print("="*60)

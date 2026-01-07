# Instalación de llama-cpp-python con GPU

## Opción 1: Wheel precompilado (MÁS FÁCIL)

```powershell
# Desinstalar versión actual
pip uninstall llama-cpp-python -y

# Instalar versión precompilada con CUDA 11.8
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu118

# O con CUDA 12.1
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
```

## Opción 2: Compilar desde código (requiere Visual Studio)

```powershell
# 1. Instalar herramientas de compilación
# Descargar: https://visualstudio.microsoft.com/downloads/
# Instalar "Desktop development with C++"

# 2. Configurar variables
$env:CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_COMPILER='C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin/nvcc.exe'"

# 3. Instalar
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

## Verificar instalación

```python
from llama_cpp import Llama

# Si carga sin error y n_gpu_layers > 0, está usando GPU
llm = Llama(
    model_path="modelos/tu_modelo.gguf",
    n_ctx=2048,
    n_gpu_layers=35,  # Prueba con 1 primero
    verbose=True
)
```

## Habilitar GPU en tu código actual

Editar `generador_examenes.py` línea 63:

```python
# ANTES
n_gpu_layers=0,

# DESPUÉS  
n_gpu_layers=35,  # O -1 para todas las capas
```

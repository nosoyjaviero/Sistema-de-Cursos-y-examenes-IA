# 🎮 Estado del Soporte GPU

## ❌ Problema Actual

Tu sistema tiene:
- ✅ GPU: NVIDIA GeForce RTX 4050 (6GB VRAM)
- ✅ CUDA 12.6 instalado
- ❌ llama-cpp-python **NO** tiene soporte GPU habilitado

## 🔍 Diagnóstico

Cuando ejecutas el modelo, verás en la consola:
```
load_tensors: layer 0 assigned to device CPU
load_tensors: layer 1 assigned to device CPU
...
```

Todas las capas se asignan a **CPU** aunque hayas configurado `n_gpu_layers=35`.

## ⚠️ Por Qué No Funciona

`llama-cpp-python` en Windows necesita ser **compilado** con soporte CUDA, pero:

1. No hay binarios precompilados con CUDA para Windows
2. Compilar requiere tener Visual Studio Build Tools configurado correctamente
3. El error actual: "No CUDA toolset found" indica que CMake no encuentra el compilador CUDA

## 🛠️ Soluciones Posibles

### Opción 1: Usar Ollama (Recomendado ⭐)

[Ollama](https://ollama.ai/) soporta GPU automáticamente en Windows:

```powershell
# Instalar Ollama desde https://ollama.ai/download
# Luego descargar modelos:
ollama pull llama3.1:8b
ollama pull qwen2.5:3b
```

Ventajas:
- ✅ GPU funciona automáticamente
- ✅ Más rápido que llama-cpp-python
- ✅ API compatible con OpenAI
- ✅ No requiere compilación

### Opción 2: Compilar llama-cpp-python con CUDA

Requiere:
1. Visual Studio 2022 Build Tools completo
2. CUDA Toolkit 12.x correctamente configurado
3. Configurar variables de entorno

```powershell
# 1. Asegurarse que nvcc funciona
nvcc --version

# 2. Configurar variables
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6"
$env:CUDA_HOME = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6"
$env:CMAKE_ARGS = "-DGGML_CUDA=on"

# 3. Compilar
pip uninstall llama-cpp-python -y
pip install llama-cpp-python --force-reinstall --no-cache-dir
```

### Opción 3: Usar llama.cpp directamente

Descargar binarios precompilados con CUDA:
https://github.com/ggerganov/llama.cpp/releases

```powershell
# Ejecutar directamente
.\llama-server.exe --model modelo.gguf --n-gpu-layers 35
```

### Opción 4: Usar LM Studio (Más Simple)

[LM Studio](https://lmstudio.ai/) tiene GPU habilitado por defecto:
- ✅ Interfaz gráfica
- ✅ GPU automático
- ✅ Servidor API local
- ✅ Sin compilación

## 📊 Rendimiento Actual

Con CPU (sin GPU):
- 🐌 ~2-5 tokens/segundo
- 💻 100% uso CPU
- 🔋 Consumo alto

Con GPU (si funcionara):
- ⚡ ~20-50 tokens/segundo
- 🎮 Uso GPU
- 🔋 Consumo menor en CPU

## 🎯 Recomendación

Para usar GPU sin complicaciones, te sugiero:

1. **Corto plazo**: Sigue usando CPU (actual) - funciona pero es lento
2. **Mediano plazo**: Instalar **Ollama** - GPU automático, fácil de usar
3. **Largo plazo**: Si necesitas control total, compilar llama-cpp-python con CUDA

## 📝 Configuración Actual

El código ya está preparado para GPU:
- ✅ `generador_dos_pasos.py` acepta `n_gpu_layers`
- ✅ `api_server.py` pasa el parámetro
- ✅ UI tiene slider para ajustar capas GPU
- ⚠️ Solo falta que llama-cpp-python tenga soporte CUDA

Cuando instales una versión con GPU, todo funcionará automáticamente.

## 🔗 Referencias

- llama-cpp-python: https://github.com/abetlen/llama-cpp-python
- llama.cpp releases: https://github.com/ggerganov/llama.cpp/releases
- Ollama: https://ollama.ai/
- LM Studio: https://lmstudio.ai/

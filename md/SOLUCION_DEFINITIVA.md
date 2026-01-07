# 🎯 SOLUCIÓN DEFINITIVA: Instalar integración CUDA con Visual Studio

## El Problema Real

CMake busca archivos específicos de integración CUDA que **NO están instalados**:
```
C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Microsoft\VC\v170\BuildCustomizations\CUDA 12.2.props
```

Estos archivos se instalan cuando:
1. Instalas CUDA Toolkit **DESPUÉS** de Visual Studio, O
2. Seleccionas "Visual Studio Integration" durante instalación de CUDA

## ✅ SOLUCIÓN (15 minutos)

### Opción A: Reinstalar CUDA con integración VS

1. **Descargar CUDA 12.2**:
   - https://developer.nvidia.com/cuda-12-2-0-download-archive
   - Seleccionar: Windows > x86_64 > 10/11 > exe (network)

2. **Ejecutar instalador**:
   - **IMPORTANTE**: Seleccionar "Custom (Advanced)"
   - Marcar: ✅ **Visual Studio Integration**
   - Marcar: ✅ **Development**
   - Marcar: ✅ **Runtime**
   - Siguiente → Instalar

3. **Verificar instalación**:
   ```powershell
   Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Microsoft\VC\v170\BuildCustomizations\CUDA 12.2.props"
   ```
   Debe devolver: `True`

4. **Compilar llama-cpp-python**:
   ```powershell
   .\instalar_llama_cuda_avanzado.ps1
   ```

### Opción B: Copiar archivos manualmente (más rápido)

Si ya tienes CUDA instalado, solo faltan los archivos de integración:

1. **Descargar solo el instalador** (no ejecutar instalación completa)
2. **Extraer archivos**:
   ```powershell
   # Los instaladores CUDA son archivos 7z
   # Extraer en carpeta temporal
   ```
3. **Copiar archivos de integración**:
   ```
   Desde: CUDAVisualStudioIntegration\extras\visual_studio_integration\MSBuildExtensions\
   Hacia: C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Microsoft\VC\v170\BuildCustomizations\
   ```
   Archivos necesarios:
   - CUDA 12.2.props
   - CUDA 12.2.targets
   - CUDA 12.2.xml
   - Nvda.Build.CudaTasks.v12.2.dll

### Opción C: Usar binarios precompilados de llama.cpp (RECOMENDADO)

**La forma MÁS RÁPIDA de tener GPU funcionando AHORA**:

1. **Descargar llama.cpp con CUDA**:
   - https://github.com/ggerganov/llama.cpp/releases/latest
   - Buscar: `llama-*-bin-win-cuda-cu12.2.0-x64.zip`
   - Descargar y extraer

2. **Ejecutar servidor**:
   ```powershell
   cd llama-cpp-extracted
   .\llama-server.exe --model "C:\Users\Fela\Documents\Proyectos\Examinator\modelos\qwen2.5-3b-instruct-q4_k_m.gguf" --n-gpu-layers 35 --port 8080 --host 0.0.0.0
   ```

3. **Modificar tu código para usar el servidor**:
   - En lugar de cargar modelo con Llama()
   - Hacer peticiones HTTP a http://localhost:8080/completion

**Ventajas**:
- ✅ GPU funciona inmediatamente
- ✅ No requiere compilación
- ✅ Mismo rendimiento
- ✅ Mismo formato de modelo (.gguf)

## 🚀 Mi Recomendación Final

**AHORA MISMO** (2 minutos):
1. Descarga binarios precompilados de llama.cpp
2. Ejecuta llama-server.exe con --n-gpu-layers 35
3. GPU funcionará inmediatamente

**DESPUÉS** (si quieres):
1. Reinstala CUDA con Visual Studio Integration
2. Compila llama-cpp-python
3. Integra directamente en tu código

## 📦 Script para usar binarios precompilados

Voy a crear un adaptador para que uses llama-server.exe con tu código actual:

```python
# generador_llama_server.py
import requests
from typing import List, Dict
from generador_dos_pasos import PreguntaExamen

class GeneradorLlamaServer:
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
    
    def _generate(self, prompt: str, temperature: float, max_tokens: int):
        response = requests.post(
            f"{self.server_url}/completion",
            json={
                "prompt": prompt,
                "temperature": temperature,
                "n_predict": max_tokens,
                "stop": ["<|eot_id|>", "<|end_of_text|>"]
            }
        )
        return response.json()["content"]
    
    # Resto igual que GeneradorDosPasos
    # Solo cambia self.llm() por self._generate()
```

¿Quieres que:
1. Reinstalemos CUDA con integración VS?
2. Usemos binarios precompilados (más rápido)?
3. Probemos Ollama (más simple)?

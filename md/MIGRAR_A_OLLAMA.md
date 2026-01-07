# 🚀 Migrar a Ollama para Usar GPU

## ❌ Problema Actual

La compilación de llama-cpp-python con CUDA falla porque CMake no encuentra el toolset CUDA de Visual Studio. Este es un problema común en Windows.

## ✅ Solución: Ollama

Ollama es más simple y **detecta GPU automáticamente**.

### Paso 1: Instalar Ollama

1. Descarga desde: https://ollama.ai/download
2. Ejecuta el instalador (OllamaSetup.exe)
3. Espera a que termine (~2 minutos)

### Paso 2: Descargar Modelos

```powershell
# Modelo similar a tu Qwen 2.5 3B
ollama pull qwen2.5:3b

# O el modelo Llama que usas
ollama pull llama3.1:8b
```

### Paso 3: Verificar GPU

```powershell
# Iniciar Ollama (se inicia automáticamente al instalar)
# Verificar que usa GPU con nvidia-smi

# Terminal 1: Ejecutar modelo
ollama run qwen2.5:3b "Hola"

# Terminal 2: Ver GPU activa
nvidia-smi
```

Deberías ver uso de GPU en la segunda terminal.

### Paso 4: Adaptar Tu Código (Opcional)

Si quieres usar Ollama API con tu sistema actual, necesitas:

1. **Instalar cliente Ollama para Python**:
```powershell
pip install ollama
```

2. **Crear adaptador** (generador_ollama.py):
```python
import ollama
from typing import List, Dict
from generador_dos_pasos import PreguntaExamen

class GeneradorOllama:
    def __init__(self, modelo: str = "qwen2.5:3b"):
        self.modelo = modelo
        
    def generar_examen(self, contenido: str, num_preguntas: Dict[str, int], 
                      ajustes_modelo: dict = None) -> List[PreguntaExamen]:
        # Mismo método que GeneradorDosPasos
        # Pero usa ollama.generate() en lugar de self.llm()
        
        # Paso 1: Generar preguntas
        response = ollama.generate(
            model=self.modelo,
            prompt=prompt_paso1,
            options={
                'temperature': ajustes_modelo.get('temperature', 0.7),
                'num_ctx': ajustes_modelo.get('n_ctx', 8192),
            }
        )
        
        # Paso 2: Formatear JSON
        # ... similar
```

## 🎯 Alternativa Más Simple: LM Studio

Si prefieres interfaz gráfica:

1. Descarga LM Studio: https://lmstudio.ai/
2. Instala y abre
3. Descarga modelos desde la app
4. Inicia servidor local
5. GPU se activa automáticamente

LM Studio tiene servidor API compatible con OpenAI, fácil de integrar.

## 🔧 Alternativa Técnica: Binarios Precompilados

Si insistes en llama.cpp:

1. Descarga binarios con CUDA: https://github.com/ggerganov/llama.cpp/releases
2. Busca archivo: `llama-cpp-*-cuda-12.2-win-amd64.zip`
3. Extrae y ejecuta:

```powershell
.\llama-server.exe --model modelos\qwen2.5-3b-instruct-q4_k_m.gguf --n-gpu-layers 35 --port 8080
```

4. Tu código puede conectarse a http://localhost:8080

## 📊 Comparación

| Característica | llama-cpp-python | Ollama | LM Studio |
|----------------|------------------|--------|-----------|
| Instalación | ❌ Compleja | ✅ Simple | ✅ Muy simple |
| GPU Windows | ❌ Requiere compilar | ✅ Automático | ✅ Automático |
| Velocidad | ⚡ Rápido | ⚡ Rápido | ⚡ Rápido |
| Integración código | ✅ Directa | 🔄 API | 🔄 API |
| UI | ❌ No | ⚠️ CLI | ✅ GUI |
| Recomendado para ti | ❌ | ✅ | ✅ |

## 🎯 Mi Recomendación

**Usa Ollama** porque:
1. Instalación en 2 minutos
2. GPU funciona de inmediato
3. Puedes seguir usando tus modelos GGUF
4. API simple para integrar
5. No requiere compilación ni configuración

**O usa LM Studio** si prefieres:
1. Interfaz gráfica
2. Todo en una aplicación
3. Descarga modelos desde la app
4. Servidor API incluido

## 📝 Siguiente Paso

Elige una opción:

**A) Ollama (recomendado)**
```powershell
# 1. Instalar desde https://ollama.ai/download
# 2. Ejecutar:
ollama pull qwen2.5:3b
ollama run qwen2.5:3b "Genera 3 preguntas sobre Python"
```

**B) LM Studio**
```
1. Descargar desde https://lmstudio.ai/
2. Instalar y abrir
3. Descargar modelo desde la app
4. Iniciar servidor local
```

**C) Compilar (solo si eres técnico)**
```
Necesitas:
- Visual Studio 2022 Build Tools COMPLETO
- CUDA Toolkit 12.2 con integration para VS
- Configurar VCTargetsPath
```

¿Quieres ayuda para configurar Ollama o LM Studio?

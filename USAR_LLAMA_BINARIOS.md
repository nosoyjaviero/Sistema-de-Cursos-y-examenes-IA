# 🚀 Guía de Uso: llama.cpp binarios precompilados

## Paso 1: Extraer archivo

1. Extrae `llama-b7084-bin-win-cuda-12.4-x64.zip` en una carpeta
2. Por ejemplo: `C:\llama-cpp\`

## Paso 2: Probar GPU

Abre PowerShell en la carpeta extraída y ejecuta:

```powershell
cd C:\llama-cpp\  # o donde lo hayas extraído

# Probar que funciona
.\llama-cli.exe --version

# Ejecutar servidor con GPU
.\llama-server.exe `
  --model "C:\Users\Fela\Documents\Proyectos\Examinator\modelos\qwen2.5-3b-instruct-q4_k_m.gguf" `
  --n-gpu-layers 30 `
  --port 8080 `
  --host 0.0.0.0 `
  --ctx-size 8192

# En otra terminal, ver uso de GPU:
nvidia-smi
```

Deberías ver en nvidia-smi que `llama-server.exe` está usando la GPU.

## Paso 3: Probar desde tu código Python

El servidor estará disponible en `http://localhost:8080`

Puedes hacer peticiones HTTP:

```python
import requests

response = requests.post(
    "http://localhost:8080/completion",
    json={
        "prompt": "¿Qué es Python?",
        "n_predict": 100,
        "temperature": 0.7
    }
)

print(response.json()["content"])
```

## Paso 4: Integrar con tu aplicación

Opción A: Crear un adaptador que tu código use el servidor llama.cpp
Opción B: Iniciar llama-server automáticamente desde Python
Opción C: Usar como servicio Windows que inicia con el sistema

¿Quieres que cree el adaptador para tu código actual?

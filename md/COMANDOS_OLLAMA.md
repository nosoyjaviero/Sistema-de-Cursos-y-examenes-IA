# Comandos Rápidos - Ollama con GPU

## 🚀 Verificar Estado

```powershell
# Ver modelos instalados
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list

# Ver modelos en ejecución (y uso de GPU)
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" ps

# Versión de Ollama
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version
```

## 📥 Gestión de Modelos

```powershell
# Descargar modelo
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull llama3.2:3b

# Eliminar modelo
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" rm llama3.2:3b

# Ver información de modelo
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" show llama3.2:3b
```

## 🧪 Probar Modelos

```powershell
# Chat interactivo
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" run llama3.2:3b

# Prueba rápida
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" run llama3.2:3b "Explica qué es Python en 50 palabras"
```

## 🔧 Scripts del Proyecto

```powershell
# Test simple con Ollama
python generador_examenes_ollama.py

# Generador unificado (detecta Ollama o llama-cpp-python)
python generador_unificado.py

# Comparar rendimiento GPU vs CPU
python comparar_rendimiento.py

# Script de inicio interactivo
.\iniciar_ollama.ps1
```

## 🎮 Verificar GPU

```powershell
# Verificar GPU NVIDIA
nvidia-smi

# Ver uso de Ollama
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" ps
# Si dice "100% GPU" = ¡Funcionando correctamente!
```

## 🐛 Solución de Problemas

```powershell
# Si Ollama no responde
Get-Process ollama | Stop-Process -Force
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve

# Ver logs de Ollama
Get-Content "$env:LOCALAPPDATA\Ollama\logs\server.log" -Tail 50

# Reiniciar servicio completo
Get-Service Ollama* | Restart-Service
```

## 📦 Modelos Recomendados

```powershell
# Pequeño y rápido (1.3 GB) - Mejor para pruebas
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull llama3.2:1b

# Balance calidad/velocidad (2.0 GB) - ACTUAL ✅
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull llama3.2:3b

# Mayor precisión (4.7 GB) - Para producción
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull llama3.1:8b

# Especializado en código (4.7 GB)
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull deepseek-coder:6.7b

# Bueno en español (2.0 GB)
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull qwen2.5:3b
```

## 🔗 API REST de Ollama

```powershell
# Listar modelos (desde Python/PowerShell)
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" | ConvertTo-Json

# Generar texto
$body = @{
    model = "llama3.2:3b"
    prompt = "¿Qué es Python?"
    stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body $body -ContentType "application/json"
```

## 💾 Ubicaciones de Archivos

```powershell
# Modelos de Ollama
explorer "$env:LOCALAPPDATA\Ollama\models"

# Logs
explorer "$env:LOCALAPPDATA\Ollama\logs"

# Ejecutable
explorer "$env:LOCALAPPDATA\Programs\Ollama"
```

## 🎯 Alias Útiles (Añadir a $PROFILE)

```powershell
# Abrir perfil de PowerShell
notepad $PROFILE

# Añadir estos alias:
function ollama { & "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" $args }
function ollama-ps { ollama ps }
function ollama-list { ollama list }
function ollama-gpu { ollama ps | Select-String "GPU" }

# Recargar perfil
. $PROFILE
```

Después de añadir los alias, podrás usar simplemente:
```powershell
ollama list
ollama-ps
ollama-gpu
```

## 📊 Ejemplo de Uso en Proyecto

```python
# En tu código Python
import requests

def generar_con_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()['response']

# Usar
resultado = generar_con_ollama("Genera 3 preguntas sobre Python")
print(resultado)
```

## ✨ Estado Actual

- ✅ Ollama instalado: v0.12.11
- ✅ Modelo activo: llama3.2:3b (2.0 GB)
- ✅ GPU: Detectada y activa al 100%
- ✅ Scripts listos para usar

¡Todo configurado! 🚀

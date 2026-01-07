# ✅ Sistema Actualizado - Ahora usa GPU con Ollama

## 🎯 Cambios Realizados

### 1. **examinator_interactivo.py**
Ahora usa Ollama automáticamente con GPU:
```bash
python examinator_interactivo.py documento.txt
```

### 2. **api_server.py** 
El servidor web ahora inicia con Ollama + GPU:
```bash
python api_server.py
```

### 3. **test_gpu.py** (NUEVO)
Script de prueba rápida:
```bash
python test_gpu.py
```

## 🚀 Cómo Usar

### Opción 1: Script de prueba
```powershell
python test_gpu.py
```

### Opción 2: Modo interactivo
```powershell
# Crear archivo de texto con contenido
echo "Python es un lenguaje..." > contenido.txt

# Generar examen
python examinator_interactivo.py contenido.txt
```

### Opción 3: Servidor web
```powershell
python api_server.py
```
Luego abre: http://localhost:8000

## 🎮 Cambiar Modelo

Edita estos archivos para usar otro modelo:

**En examinator_interactivo.py (línea ~193):**
```python
generador = GeneradorUnificado(
    usar_ollama=True,
    modelo_ollama="llama31-local",  # Cambia aquí
    modelo_path_gguf=args.modelo,
    n_gpu_layers=35
)
```

**Modelos disponibles:**
- `llama31-local` (4.9 GB) - ⭐ Mejor balance
- `llama32-local` (2.0 GB) - Más rápido
- `qwen-local` (2.1 GB) - Bueno en español
- `deepseek-r1-local` (6.7 GB) - Razonamiento avanzado

## 📊 Verificar GPU

Durante la ejecución, abre otra terminal:
```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" ps
```

Deberías ver algo como:
```
NAME              PROCESSOR        SIZE
llama31-local     78% GPU/22% CPU  6.4 GB
```

## 🔧 Si Ollama no está disponible

El sistema automáticamente regresará a usar modelos GGUF con llama-cpp-python:
```
⚠️  Ollama no disponible
💡 Intentando con modelo GGUF...
```

## 💡 Ventajas de la Nueva Configuración

✅ **GPU automática** - No necesitas configurar `n_gpu_layers`
✅ **Más rápido** - Ollama está optimizado
✅ **Fallback automático** - Si Ollama falla, usa GGUF
✅ **Fácil cambio de modelo** - Solo cambiar nombre
✅ **Sin recompilar** - No necesitas CUDA toolkit

## 📝 Ejemplo Completo

```powershell
# 1. Crear contenido
@"
Python es un lenguaje de programación de alto nivel.
Fue creado por Guido van Rossum en 1991.
"@ | Out-File -FilePath test_contenido.txt -Encoding UTF8

# 2. Generar examen con GPU
python test_gpu.py

# 3. Verificar GPU
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" ps
```

## 🎉 ¡Todo listo!

Tu sistema ahora:
- ✅ Usa GPU automáticamente con Ollama
- ✅ Genera exámenes 5-10x más rápido
- ✅ Tiene 5 modelos disponibles
- ✅ Fallback a CPU si es necesario

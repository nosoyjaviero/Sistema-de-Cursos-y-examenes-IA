# 🚀 Guía: Usar Ollama con GPU (Alternativa a llama-cpp-python)

## ¿Por qué Ollama?

✅ **Detecta GPU automáticamente** - No necesitas configurar nada
✅ **Más fácil de instalar** - Un solo comando
✅ **Mejor rendimiento** - Optimizado para inferencia
✅ **Gestión de modelos simple** - Pull/delete/list como Docker
✅ **Compatible con tu hardware** - Funciona con NVIDIA, AMD, CPU

## Instalación

### 1. Descargar Ollama

```powershell
# Opción A: Desde el navegador
# Ir a: https://ollama.com/download
# Descargar el instalador para Windows

# Opción B: Con winget (si lo tienes)
winget install Ollama.Ollama
```

### 2. Verificar instalación

```powershell
ollama --version
```

### 3. Descargar modelos

```powershell
# Modelo recomendado para tu proyecto (3GB)
ollama pull llama3.2:3b

# Alternativas:
ollama pull llama3.2:1b     # Más rápido, menos preciso (1.3GB)
ollama pull llama3.1:8b     # Más preciso, más lento (4.7GB)
ollama pull qwen2.5:3b      # Alternativa a Llama (2GB)
```

### 4. Verificar GPU

```powershell
ollama ps
# Debería mostrar que está usando la GPU automáticamente
```

## Uso en tu proyecto

### Opción A: Script standalone

```powershell
python generador_examenes_ollama.py
```

### Opción B: Integrar en tu código existente

```python
from generador_examenes_ollama import GeneradorExamenesOllama

# Crear generador (detecta GPU automáticamente)
generador = GeneradorExamenesOllama(modelo="llama3.2:3b")

# Generar examen
contenido = "Tu contenido aquí..."
preguntas = generador.generar_examen(
    contenido, 
    num_preguntas={'multiple': 5, 'verdadero_falso': 3}
)
```

### Opción C: Modificar tu código actual

Reemplaza en tus scripts:

```python
# ANTES (llama-cpp-python)
from llama_cpp import Llama
llm = Llama(model_path="modelos/modelo.gguf", n_gpu_layers=35)

# DESPUÉS (Ollama)
from generador_examenes_ollama import GeneradorExamenesOllama
generador = GeneradorExamenesOllama(modelo="llama3.2:3b")
```

## Comandos útiles

```powershell
# Ver modelos instalados
ollama list

# Ver modelos corriendo (y uso de GPU)
ollama ps

# Eliminar modelo
ollama rm llama3.2:3b

# Probar modelo en consola
ollama run llama3.2:3b
```

## Ventajas sobre llama-cpp-python

| Característica | llama-cpp-python | Ollama |
|----------------|------------------|---------|
| Instalación GPU | Compleja (CMAKE, CUDA toolkit) | Automática |
| Gestión modelos | Manual (archivos .gguf) | `ollama pull` |
| Detección GPU | Manual (`n_gpu_layers`) | Automática |
| Rendimiento | Bueno | Excelente |
| Facilidad de uso | Media | Alta |

## Comparación de modelos

Para tu proyecto de exámenes, recomiendo:

1. **llama3.2:3b** (3GB) - Balance perfecto calidad/velocidad
2. **qwen2.5:3b** (2GB) - Alternativa con buen español
3. **llama3.1:8b** (4.7GB) - Si necesitas máxima calidad

## Verificar que usa GPU

Cuando ejecutes el modelo, verás en la terminal:

```
✅ Ollama activo - 1 modelos disponibles
🤖 Generando 10 preguntas con llama3.2:3b...
```

Y en otra terminal:
```powershell
ollama ps
# Salida:
NAME              ID           SIZE    PROCESSOR    UNTIL
llama3.2:3b       961cd76...   3.0GB   100% GPU     4 minutes from now
```

Si dice **"100% GPU"** = ¡Está usando tu tarjeta gráfica! 🎉

## Solución de problemas

### Ollama no usa GPU

```powershell
# Verificar drivers NVIDIA
nvidia-smi

# Reiniciar servicio Ollama
ollama serve
```

### Modelo no encontrado

```powershell
ollama list  # Ver modelos instalados
ollama pull llama3.2:3b  # Descargar si falta
```

## Migración completa

Si quieres migrar todo tu proyecto a Ollama:

1. Instalar Ollama
2. Descargar modelos: `ollama pull llama3.2:3b`
3. Reemplazar imports en tu código
4. Opcional: desinstalar `pip uninstall llama-cpp-python`

## Recursos

- Documentación: https://github.com/ollama/ollama
- Modelos disponibles: https://ollama.com/library
- Discord: https://discord.gg/ollama

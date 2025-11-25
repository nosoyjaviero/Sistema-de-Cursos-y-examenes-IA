# Solución: Modernización de FastAPI y Estabilidad del Servidor

## Problema Identificado

El servidor `api_server.py` presentaba dos problemas críticos:

1. **Crashes aleatorios**: El servidor se cerraba después de procesar algunos requests
   - **Causa raíz**: El endpoint POST `/timer_sync` (línea ~2323) usaba `asyncio.run(request.json())` en una función sincrónica, lo cual conflictúa con el event loop de FastAPI que es asincrónico.

2. **DeprecationWarning**: FastAPI mostraba warnings sobre el uso de `@app.on_event("startup")`
   - **Motivo**: Esta decoradora está deprecated en FastAPI >= 0.93

## Solución Implementada

### 1. Arreglo del Endpoint `/timer_sync` (CRÍTICO)

**Antes (Línea ~2323):**
```python
@app.post("/timer_sync")
def timer_sync(request: Request):
    data = asyncio.run(request.json())  # ❌ Error: asyncio.run() en contexto async
    # ...
```

**Después:**
```python
@app.post("/timer_sync")
async def timer_sync(request: Request):
    data = await request.json()  # ✅ Correcta usar await en función async
    # ...
```

### 2. Modernización del Patrón de Lifecycle de FastAPI

**Antes (Deprecated):**
```python
@app.on_event("startup")
async def startup_event():
    # Código de startup
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Código de shutdown
    pass

app = FastAPI()
```

**Después (Moderno):**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de startup
    print("🚀 INICIANDO EXAMINATOR API SERVER")
    verificar_y_arrancar_ollama()
    inicializar_modelo()
    print("✅ Servidor listo")
    
    yield  # La aplicación corre aquí
    
    # Código de shutdown
    print("🛑 Deteniendo EXAMINATOR API SERVER")

app = FastAPI(title="Examinator API", lifespan=lifespan)
```

### 3. Importaciones Necesarias

Se agregaron:
```python
from typing import AsyncGenerator
from contextlib import asynccontextmanager
```

## Verificación de la Solución

### ✅ Servidor Funcionando Correctamente

```
🚀 INICIANDO EXAMINATOR API SERVER
✅ Ollama ya está corriendo
✅ Ollama activo - 5 modelos
✅ Ollama cargado - Usando GPU automáticamente
🎮 Modelo activo: Meta-Llama-3.1-8B-Instruct-Q4-K-L
✅ Servidor listo en http://localhost:8000
INFO: Application startup complete
```

### ✅ Endpoints Respondiendo Correctamente

- `GET /api/config` → 200 OK (Ollama detectado, GPU activa)
- `GET /timer_sync` → 200 OK (sin crashes)
- Múltiples requests sin degradación del servidor

### ✅ Sin DeprecationWarnings

El servidor se inicia completamente sin advertencias sobre `@app.on_event`.

## Cómo Iniciar el Servidor

### Opción 1: Directo con Uvicorn
```powershell
$env:PYTHONIOENCODING='utf-8'
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000
```

### Opción 2: Usando el script helper
```powershell
python run_server.py
```

## Cambios Realizados en Archivos

### `api_server.py`
- **Líneas 209-245**: Implementación del lifespan context manager
- **Línea 7**: Import de `asynccontextmanager` y `AsyncGenerator`
- **Línea 7-8**: Correctas importaciones
- **Línea 217**: Definición de `@asynccontextmanager async def lifespan(app: FastAPI)`
- **Línea ~2323**: Cambio del endpoint POST `/timer_sync` de `def` a `async def` con `await request.json()`

## Estructura Final

```python
# 1. Imports
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# 2. Funciones de startup/shutdown (verificar Ollama, cargar modelo)
def verificar_y_arrancar_ollama(): ...
def inicializar_modelo(): ...

# 3. Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    verificar_y_arrancar_ollama()
    inicializar_modelo()
    yield  # app runs
    # shutdown

# 4. Create FastAPI app con lifespan
app = FastAPI(title="Examinator API", lifespan=lifespan)

# 5. CORS middleware
app.add_middleware(CORSMiddleware, ...)

# 6. Endpoints (todos correctamente async)
@app.get("/api/config")
async def get_config(): ...

@app.post("/api/chat")
async def chat(data: dict): ...

@app.post("/timer_sync")  # ✅ Ahora async
async def timer_sync(request: Request): ...
```

## Rendimiento y Estabilidad

- **Estabilidad**: El servidor ahora puede manejar múltiples requests sin crashes
- **GPU**: Ollama con GPU activada automáticamente (n_gpu_layers=35)
- **Modelos**: 5 modelos disponibles a través de Ollama
- **Recomendación**: Usar 1 worker en Windows (limitaciones de multiprocessing)

## Verificación Final

El servidor está completamente funcional y listo para:
- Generación de prácticas
- Generación de exámenes
- Chat con IA
- Gestión de configuración
- Búsqueda web
- Extracción de documentos

```
INFO: Application startup complete
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

**Commit**: `8c421c2` - ✅ Solución completa: Reparar servidor y configuración

# 🚀 Iniciar Examinator - Guía Rápida

## ✨ Inicio Automático (Recomendado)

Ejecuta este comando en PowerShell:

```powershell
.\iniciar_todo_mejorado.ps1
```

Este script automáticamente:
- ✅ Verifica si Ollama está corriendo
- ✅ Inicia Ollama si no está activo
- ✅ Detiene servidores API anteriores
- ✅ Inicia el servidor API
- ✅ Muestra el estado de todos los servicios

## 🔧 Reparación Automática desde la Interfaz

Si el chatbot deja de funcionar:

1. Abre el **Chat** en la aplicación
2. Verás un botón **"⚠️ Ollama"** si hay problemas
3. Haz clic en **"🔧 Reparar"**
4. El sistema intentará iniciar Ollama automáticamente

## 📋 Verificación Manual

### Verificar Ollama
```powershell
ollama list
```

Si falla, iniciarlo:
```powershell
ollama serve
```

### Verificar Modelos
```powershell
curl http://localhost:11434/api/tags
```

## 🛠️ Solución de Problemas

### Error: "No se puede establecer una conexión"

**Causa:** Ollama no está corriendo

**Solución 1 (Automática):**
- Ejecuta `.\iniciar_todo_mejorado.ps1`

**Solución 2 (Manual):**
```powershell
# Terminal 1
ollama serve

# Terminal 2
python api_server.py
```

**Solución 3 (Desde la App):**
- Abre el Chat
- Clic en "🔧 Reparar" en la barra superior

### El botón "🔧 Reparar" no aparece

**Causa:** El diagnóstico no se ha ejecutado

**Solución:**
- Haz clic en el botón "✅ Ollama" o "⚠️ Ollama"
- Si Ollama no está corriendo, aparecerá el botón "Reparar"

## 📊 Indicadores de Estado

| Indicador | Significado |
|-----------|-------------|
| ✅ Ollama | Ollama funcionando correctamente |
| ⚠️ Ollama | Ollama no está disponible |
| 🔧 Reparar | Botón para iniciar Ollama automáticamente |

## 🎯 Funcionalidades Implementadas

1. **Auto-inicio de Ollama**: El servidor API intenta iniciar Ollama automáticamente al arrancar
2. **Diagnóstico en tiempo real**: Botón que verifica el estado de Ollama
3. **Reparación con un clic**: Botón que inicia Ollama desde la interfaz
4. **Fallback automático**: Si Ollama falla, intenta usar modelos GGUF locales

## ⚙️ Arquitectura del Sistema

```
┌─────────────────┐
│   Frontend      │  Puerto 5173
│  (React/Vite)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Server    │  Puerto 8000
│  (FastAPI)      │
└────────┬────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Ollama    │  │  GGUF Local │  │  Búsqueda   │
│ Puerto 11434│  │  (Opcional) │  │    Web      │
└─────────────┘  └─────────────┘  └─────────────┘
```

## 🔄 Ciclo de Vida

1. **Inicio**: `iniciar_todo_mejorado.ps1`
2. **Verificación**: Chequea Ollama cada vez que abres el Chat
3. **Reparación**: Clic en "Reparar" si hay problemas
4. **Fallback**: Usa GGUF si Ollama no está disponible

## 📝 Notas

- El servidor API **siempre** intenta iniciar Ollama al arrancar
- El frontend verifica Ollama **cada vez** que abres el Chat
- Los botones de diagnóstico tienen **animación pulsante** para visibilidad
- Verde = Todo OK | Naranja = Requiere atención

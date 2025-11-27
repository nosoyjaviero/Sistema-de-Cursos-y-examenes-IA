# 🔧 Fix: Exámenes No Detectados en Pestaña

## 🐛 Problema

Los exámenes no aparecían en la pestaña "📋 Exámenes" del explorador de archivos en la interfaz.

## 🔍 Causa Raíz

1. **Estructura antigua vs nueva:**
   - Antigua: `extracciones/{carpeta}/resultados_examenes/examen_*.json`
   - Nueva: `examenes/{carpeta}/examen_*.json`

2. **Endpoint desactualizado:**
   - El endpoint `/api/archivos/explorar` para tipo `examenes` buscaba en `examenes/*.json` (raíz)
   - No exploraba subcarpetas ni soportaba navegación por carpetas

## ✅ Solución Implementada

### 1️⃣ Migración de Exámenes

**Script:** `migrar_examenes_a_nueva_estructura.py`

```bash
python migrar_examenes_a_nueva_estructura.py
```

**Resultado:**
```
✅ 4 exámenes migrados
   examenes/Platzi/Prueba/eeeee/examen_20251126_233956.json
   examenes/Platzi/Prueba/eeeee/examen_20251126_234229.json
   examenes/Platzi/Prueba/sadas/examen_20251126_231507.json
   examenes/Platzi/Prueba/sadas/examen_20251126_233540.json
```

### 2️⃣ Actualización del Endpoint

**Archivo:** `api_server.py` líneas ~1580-1660

**Cambios:**
- ✅ Soporta navegación por carpetas (igual que notas/prácticas)
- ✅ Lista carpetas disponibles cuando `ruta=""` 
- ✅ Lista exámenes de carpeta específica cuando `ruta="Platzi/Prueba/sadas"`
- ✅ Lee metadatos de cada examen (título, porcentaje, fecha)
- ✅ Ordena por fecha descendente

**Comportamiento:**

```python
# GET /api/archivos/explorar?tipo=examenes&ruta=
# Respuesta: Lista de carpetas con número de exámenes
{
  "carpetas": [
    {"nombre": "Platzi", "ruta": "Platzi", "num_archivos": 4}
  ],
  "archivos": [],
  "ruta_actual": "",
  "tipo": "examenes"
}

# GET /api/archivos/explorar?tipo=examenes&ruta=Platzi/Prueba/sadas
# Respuesta: Lista de exámenes en esa carpeta
{
  "carpetas": [],
  "archivos": [
    {
      "nombre": "Examen 3/10.json",
      "ruta_completa": "examenes/Platzi/Prueba/sadas/examen_20251126_231507.json",
      "tipo": "Examen",
      "tamaño": 4876,
      "modificado": 1732671307.123,
      "carpeta": "Platzi/Prueba/sadas"
    }
  ],
  "ruta_actual": "Platzi/Prueba/sadas",
  "tipo": "examenes"
}
```

## 🚀 Pasos para Activar

### Opción 1: Reinicio Manual del Servidor

```bash
# Detener servidor actual
Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process

# Reiniciar
.\iniciar_todo.ps1
# O
python api_server.py
```

### Opción 2: Auto-Reload (si está activo)

Si el servidor usa `uvicorn` con `--reload`, los cambios se aplicarán automáticamente al guardar `api_server.py`.

## ✅ Verificación

Después de reiniciar el servidor:

1. **Abrir interfaz web**
2. **Ir a pestaña Chat/Explorador**
3. **Clic en "📋 Exámenes"**
4. **Deberías ver:**
   - 📁 Platzi (4 archivos)
   - Al hacer clic en Platzi → más subcarpetas
   - Al llegar a carpeta final → lista de exámenes con fechas

## 📊 Estructura Final

```
examenes/
├── Platzi/
│   └── Prueba/
│       ├── eeeee/
│       │   ├── examen_20251126_233956.json
│       │   └── examen_20251126_234229.json
│       └── sadas/
│           ├── examen_20251126_231507.json ✅ Normalizado
│           └── examen_20251126_233540.json
├── error_bank/          (vacía)
└── Examenes_Generales/  (vacía)
```

## 🔗 Archivos Relacionados

- `api_server.py` - Endpoint corregido
- `migrar_examenes_a_nueva_estructura.py` - Script de migración
- `normalizar_examen_existente.py` - Normalización de JSON
- `CORRECCIONES_COMPLETAS_SISTEMA_EXAMENES.md` - Documentación completa

---

**Estado:** ✅ Corrección implementada, requiere reinicio de servidor  
**Fecha:** 26 de Noviembre 2024

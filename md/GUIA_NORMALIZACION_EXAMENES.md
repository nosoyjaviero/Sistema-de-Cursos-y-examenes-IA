# 🔧 Guía de Normalización de Exámenes

## 📋 Descripción

Sistema completo para normalizar arrays de exámenes (`examenes.json`) con tres correcciones principales:

1. **Tipos de preguntas:** `"verdadero-falso"` → `"verdadero_falso"`, `"multiple"` → `"mcq"`
2. **Intervalos de repetición:** `0.5` → `1` (asegura enteros >= 1)
3. **Rutas de carpetas:** `"Platzi\\Prueba"` → `"Platzi/Prueba"`

---

## 🐍 Backend (Python/FastAPI)

### Función Principal

```python
from normalizar_examenes_array import normalizar_examenes

# Leer examenes.json
with open("examenes.json", 'r', encoding='utf-8') as f:
    examenes = json.load(f)

# 🔥 NORMALIZAR ANTES DE USAR
examenes_normalizados = normalizar_examenes(examenes)

# Guardar normalizado
with open("examenes.json", 'w', encoding='utf-8') as f:
    json.dump(examenes_normalizados, f, ensure_ascii=False, indent=2)
```

### Endpoint API

```bash
# Normalizar TODOS los exámenes en el sistema
curl -X POST http://localhost:8000/datos/examenes/normalizar
```

**Respuesta:**
```json
{
  "success": true,
  "archivos_normalizados": 5,
  "examenes_normalizados": 23
}
```

### Script Standalone

```bash
python normalizar_examenes_array.py
```

**Salida:**
```
🔄 Normalizando 10 exámenes...

📊 Resumen de normalización:
   ✅ Exámenes procesados: 10
   ✅ Rutas normalizadas: 10
   ✅ Tipos normalizados: 45
   ✅ Intervalos corregidos: 45

✅ examenes.json normalizado guardado
```

---

## ⚛️ Frontend (React/JavaScript)

### Importar Función

```javascript
import { normalizarExamenes } from './utils/normalizarExamenes';
```

### Uso en getDatos (Automático)

**Ya integrado en `App.jsx`:**

```javascript
async function getDatos(tipo) {
  const response = await fetch(`${API_URL}/datos/${tipo}`);
  let data = await response.json();
  
  // 🔥 NORMALIZAR EXÁMENES AUTOMÁTICAMENTE
  if (tipo === 'examenes' && Array.isArray(data)) {
    data = normalizarExamenes(data);
  }
  
  return data;
}
```

### Uso Manual

```javascript
// Después de recibir datos del backend
const examenes = await getDatos('examenes');

// O normalizar manualmente
const examenesNormalizados = normalizarExamenes(examenes);
```

---

## 📊 Estructura de Examen

### Antes de Normalizar

```json
{
  "id": 1764220507355,
  "carpeta": "Platzi\\Prueba\\sadas",
  "carpeta_ruta": "Platzi\\Prueba\\sadas",
  "intervalo": 0.5,
  "preguntas": [
    {
      "tipo": "verdadero-falso",
      "pregunta": "¿React es un framework?",
      "intervalo": 0.5
    },
    {
      "tipo": "multiple",
      "pregunta": "¿Qué es JSX?",
      "intervalo": 1.7
    }
  ],
  "resultado": {
    "resultados": [
      {
        "tipo": "verdadero-falso",
        "intervalo": 0.5
      }
    ]
  }
}
```

### Después de Normalizar

```json
{
  "id": 1764220507355,
  "carpeta": "Platzi/Prueba/sadas",
  "carpeta_ruta": "Platzi/Prueba/sadas",
  "intervalo": 1,
  "facilidad": 2.5,
  "repeticiones": 0,
  "estadoRevision": "nueva",
  "preguntas": [
    {
      "tipo": "verdadero_falso",
      "pregunta": "¿React es un framework?",
      "intervalo": 1,
      "facilidad": 2.5,
      "repeticiones": 0,
      "estadoRevision": "nueva"
    },
    {
      "tipo": "mcq",
      "pregunta": "¿Qué es JSX?",
      "intervalo": 2,
      "facilidad": 2.5,
      "repeticiones": 0,
      "estadoRevision": "nueva"
    }
  ],
  "resultado": {
    "resultados": [
      {
        "tipo": "verdadero_falso",
        "intervalo": 1,
        "facilidad": 2.5,
        "repeticiones": 0,
        "estadoRevision": "nueva"
      }
    ]
  }
}
```

---

## 🔧 Reglas de Normalización

### 1️⃣ Tipos de Preguntas

| Tipo Original | Tipo Normalizado | Descripción |
|--------------|------------------|-------------|
| `"verdadero-falso"` | `"verdadero_falso"` | Verdadero/Falso |
| `"multiple"` | `"mcq"` | Opción múltiple |
| `"corta"` | `"short_answer"` | Respuesta corta |
| `"desarrollo"` | `"open_question"` | Pregunta abierta |

### 2️⃣ Intervalos de Repetición (SM-2)

| Intervalo Original | Intervalo Normalizado |
|-------------------|----------------------|
| `0.5` | `1` |
| `0.8` | `1` |
| `1.7` | `2` |
| `2.3` | `2` |
| `5.9` | `6` |

**Regla:** `intervalo = max(1, Math.round(intervalo_original))`

### 3️⃣ Rutas de Carpetas

| Ruta Original | Ruta Normalizada |
|--------------|------------------|
| `"Platzi\\Prueba\\sadas"` | `"Platzi/Prueba/sadas"` |
| `"React\\Hooks\\useState"` | `"React/Hooks/useState"` |

**Regla:** Reemplazar `\\` con `/` (compatible Windows/Linux)

### 4️⃣ Campos SM-2 Obligatorios

Si no existen, se añaden automáticamente:

```json
{
  "facilidad": 2.5,
  "intervalo": 1,
  "repeticiones": 0,
  "estadoRevision": "nueva"
}
```

---

## 🧪 Casos de Prueba

### Test 1: Normalización de Tipos

```javascript
const examen = {
  preguntas: [
    { tipo: "verdadero-falso" },
    { tipo: "multiple" },
    { tipo: "corta" }
  ]
};

normalizarExamenes([examen]);

// Resultado:
// preguntas[0].tipo === "verdadero_falso"
// preguntas[1].tipo === "mcq"
// preguntas[2].tipo === "short_answer"
```

### Test 2: Corrección de Intervalos

```javascript
const examen = {
  intervalo: 0.5,
  preguntas: [
    { intervalo: 0.8 },
    { intervalo: 1.7 },
    { intervalo: 2.3 }
  ]
};

normalizarExamenes([examen]);

// Resultado:
// examen.intervalo === 1
// preguntas[0].intervalo === 1
// preguntas[1].intervalo === 2
// preguntas[2].intervalo === 2
```

### Test 3: Normalización de Rutas

```javascript
const examen = {
  carpeta: "Platzi\\Prueba\\sadas",
  carpeta_ruta: "React\\Hooks\\useState"
};

normalizarExamenes([examen]);

// Resultado:
// examen.carpeta === "Platzi/Prueba/sadas"
// examen.carpeta_ruta === "React/Hooks/useState"
```

---

## 🚀 Integración en Flujo Completo

### Opción 1: Normalización Automática (Frontend)

**Ya implementado** - Cada vez que se cargan exámenes desde el backend, se normalizan automáticamente.

```javascript
// En App.jsx
const examenes = await getDatos('examenes'); // ✅ Ya normalizados
```

### Opción 2: Normalización en Backend (API)

```javascript
// Llamar endpoint de normalización masiva
const response = await fetch('http://localhost:8000/datos/examenes/normalizar', {
  method: 'POST'
});

const result = await response.json();
console.log(`✅ ${result.examenes_normalizados} exámenes normalizados`);
```

### Opción 3: Script Manual (Python)

```bash
# Normalizar examenes.json directamente
python normalizar_examenes_array.py
```

---

## 📁 Archivos Creados

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `normalizar_examenes_array.py` | `/` | Script Python standalone + función para FastAPI |
| `normalizarExamenes.js` | `/examinator-web/src/utils/` | Función JavaScript/React |
| `GUIA_NORMALIZACION_EXAMENES.md` | `/` | Esta guía |

---

## ✅ Checklist de Validación

Después de normalizar, verifica:

- [ ] Todos los tipos son: `verdadero_falso`, `mcq`, `short_answer`, `open_question`
- [ ] Todos los intervalos son enteros >= 1
- [ ] Todas las rutas usan `/` en lugar de `\\`
- [ ] Todos los exámenes tienen campos SM-2: `facilidad`, `intervalo`, `repeticiones`, `estadoRevision`
- [ ] No hay errores en consola del frontend
- [ ] El sistema de Spaced Repetition funciona correctamente

---

## 🐛 Troubleshooting

### Problema: "examenes no es un array"

**Solución:**
```javascript
// Verificar que getDatos retorna array
const examenes = await getDatos('examenes');
console.log(Array.isArray(examenes)); // Debe ser true
```

### Problema: Intervalos siguen siendo decimales

**Solución:**
```python
# Verificar que se llama a normalizar_examenes DESPUÉS de leer JSON
examenes = normalizar_examenes(examenes)  # ✅ Correcto

# NO hacer:
normalizar_examenes(examenes)  # ❌ Sin asignar resultado
```

### Problema: Rutas con backslash en Windows

**Solución:**
```javascript
// La normalización se aplica automáticamente en getDatos
// Si persiste, verificar que App.jsx importa correctamente:
import { normalizarExamenes } from './utils/normalizarExamenes';
```

---

## 📞 Soporte

- **Documentación completa:** `CORRECCIONES_COMPLETAS_SISTEMA_EXAMENES.md`
- **Migración de carpetas:** `FIX_SUBCARPETA_EXAMENES.md`
- **Sistema de errores:** `COMO_USAR_SISTEMA_ERRORES.md`

---

**Autor:** GitHub Copilot  
**Modelo:** Claude Sonnet 4.5  
**Fecha:** 26 de Noviembre 2024

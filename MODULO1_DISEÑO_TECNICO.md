# 🔍 MÓDULO 1: Detector de Errores - Diseño Técnico

## 📋 Resumen Ejecutivo

Este documento describe el diseño del **Módulo 1: Detector de Errores por Pregunta**, primer componente del sistema de análisis de patrones de error para Examinator.

**Objetivo:** Clasificar automáticamente cada pregunta de exámenes completados en `acierto`, `fallo` o `respuesta_debil` para análisis posterior.

---

## 🎯 Requisitos Funcionales

### RF-1: Lectura de Exámenes Completados
- Leer archivos JSON de `examenes/{carpeta}/`
- Validar que sean exámenes tipo `"completado"`
- Mantener compatibilidad con estructura existente

### RF-2: Clasificación por Tipo de Pregunta

#### Preguntas Objetivas (`multiple`, `verdadero_falso`, `flashcard`)
- **Método primario:** Comparación directa `respuesta_usuario == respuesta_correcta`
- **Método fallback:** Ratio de puntos (cuando `respuesta_correcta` es `null`)

#### Preguntas Subjetivas (`corta`, `desarrollo`)
- **Método:** Ratio `puntos / puntos_maximos`
- **Umbrales:**
  - `< 0.7` → `fallo`
  - `0.7 - 0.89` → `respuesta_debil`
  - `≥ 0.9` → `acierto`

### RF-3: Estructura de Salida
Cada pregunta debe incluir:
```python
{
  "id_pregunta": str | None,          # Identificador único (puede no existir)
  "tipo": str,                        # multiple | verdadero_falso | flashcard | corta | desarrollo
  "pregunta": str,                    # Texto de la pregunta
  "respuesta_usuario": any,           # Respuesta dada por el usuario
  "respuesta_correcta": any | None,   # Respuesta correcta (null en subjetivas)
  "puntos": float,                    # Puntos obtenidos
  "puntos_maximos": float,            # Puntos máximos posibles
  "feedback": str,                    # Retroalimentación de la IA
  "estado_respuesta": str             # ← NUEVO: "acierto" | "fallo" | "respuesta_debil"
}
```

### RF-4: No Romper Sistema Existente
- **No modificar** archivos JSON originales de exámenes
- **No interferir** con flujos actuales de generación/evaluación
- **Operar como módulo independiente** de análisis

---

## 🏗️ Arquitectura del Módulo

```
┌─────────────────────────────────────────────────────────────┐
│                  DETECTOR DE ERRORES                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │  DetectorErrores (Clase Principal)             │         │
│  │  ├─ analizar_examen(ruta_json)                 │         │
│  │  ├─ analizar_multiples_examenes([rutas])       │         │
│  │  ├─ filtrar_por_estado(resultados, estado)     │         │
│  │  └─ generar_reporte_texto(analisis)            │         │
│  └────────────────────────────────────────────────┘         │
│                       ↓                                      │
│  ┌────────────────────────────────────────────────┐         │
│  │  ResultadoPreguntaExtendido (Modelo de Datos)  │         │
│  │  ├─ Campos originales del examen               │         │
│  │  ├─ estado_respuesta (NUEVO)                   │         │
│  │  └─ _clasificar_respuesta() → EstadoRespuesta  │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                        ↓
            ┌──────────────────────┐
            │  JSON Examen         │
            │  examenes/.../       │
            │  examen_xxx.json     │
            └──────────────────────┘
```

---

## 📊 Algoritmo de Clasificación

### Pseudocódigo

```python
función clasificar_respuesta(pregunta):
    ratio = pregunta.puntos / pregunta.puntos_maximos
    
    SI pregunta.tipo EN ["multiple", "verdadero_falso", "flashcard"]:
        # Preguntas objetivas
        
        SI pregunta.respuesta_correcta NO ES null:
            # Comparación directa
            SI normalizar(pregunta.respuesta_usuario) == normalizar(pregunta.respuesta_correcta):
                RETORNAR "acierto"
            SINO:
                RETORNAR "fallo"
        SINO:
            # Fallback a ratio (flashcards evaluadas por IA)
            SI ratio >= 0.9:
                RETORNAR "acierto"
            SINO SI ratio >= 0.7:
                RETORNAR "respuesta_debil"
            SINO:
                RETORNAR "fallo"
    
    SINO SI pregunta.tipo EN ["corta", "desarrollo"]:
        # Preguntas subjetivas
        SI ratio >= 0.9:
            RETORNAR "acierto"
        SINO SI ratio >= 0.7:
            RETORNAR "respuesta_debil"
        SINO:
            RETORNAR "fallo"
    
    SINO:
        # Tipo desconocido: usar ratio conservador
        SI ratio >= 0.9:
            RETORNAR "acierto"
        SINO SI ratio >= 0.7:
            RETORNAR "respuesta_debil"
        SINO:
            RETORNAR "fallo"
```

### Ejemplo de Aplicación

#### Caso 1: Pregunta de Opción Múltiple
```json
{
  "tipo": "multiple",
  "respuesta_usuario": "B",
  "respuesta_correcta": "A",
  "puntos": 0,
  "puntos_maximos": 3
}
```
**Clasificación:** `fallo` (comparación directa: B ≠ A)

#### Caso 2: Pregunta de Desarrollo
```json
{
  "tipo": "desarrollo",
  "respuesta_usuario": "El diseño influye en la percepción...",
  "respuesta_correcta": null,
  "puntos": 2.5,
  "puntos_maximos": 3
}
```
**Clasificación:** `respuesta_debil` (ratio: 2.5/3 = 0.833, que está en [0.7, 0.89])

#### Caso 3: Flashcard Evaluada por IA
```json
{
  "tipo": "flashcard",
  "respuesta_usuario": "Relación y jerarquía",
  "respuesta_correcta": null,
  "puntos": 0.5,
  "puntos_maximos": 1
}
```
**Clasificación:** `fallo` (ratio: 0.5/1 = 0.5, que es < 0.7)

---

## 🔌 API del Módulo

### Clase `DetectorErrores`

#### `analizar_examen(ruta_json: str) -> Dict`

Analiza un examen completado y retorna análisis completo.

**Parámetros:**
- `ruta_json`: Ruta al JSON del examen (ej: `"examenes/Platzi/examen_20251120_134728.json"`)

**Retorna:**
```python
{
  "metadata": {
    "id": str,
    "carpeta": str,
    "carpeta_ruta": str,
    "fecha_completado": str,
    "puntos_obtenidos": float,
    "puntos_totales": float,
    "porcentaje": float
  },
  "resultados_clasificados": [
    {
      # Campos originales + estado_respuesta
      "estado_respuesta": "acierto" | "fallo" | "respuesta_debil"
    }
  ],
  "resumen_estados": {
    "total_preguntas": int,
    "aciertos": int,
    "fallos": int,
    "respuestas_debiles": int,
    "porcentaje_aciertos": float,
    "porcentaje_fallos": float,
    "porcentaje_debiles": float
  }
}
```

**Excepciones:**
- `FileNotFoundError`: Archivo no existe
- `json.JSONDecodeError`: JSON malformado
- `KeyError`: Faltan campos requeridos
- `ValueError`: Examen no completado

**Ejemplo de uso:**
```python
detector = DetectorErrores()
analisis = detector.analizar_examen("examenes/Platzi/examen_20251120_134728.json")

print(f"Fallos: {analisis['resumen_estados']['fallos']}")
```

---

#### `analizar_multiples_examenes(rutas_json: List[str]) -> List[Dict]`

Analiza múltiples exámenes en batch.

**Parámetros:**
- `rutas_json`: Lista de rutas a archivos JSON

**Retorna:**
- Lista de diccionarios de análisis (mismo formato que `analizar_examen()`)

**Manejo de errores:**
- Errores individuales se imprimen y se omite el examen problemático
- Continúa con los demás exámenes

**Ejemplo:**
```python
rutas = [
    "examenes/Platzi/examen_20251120_134728.json",
    "examenes/Platzi/examen_20251120_133845.json"
]

resultados = detector.analizar_multiples_examenes(rutas)
print(f"Se analizaron {len(resultados)} exámenes")
```

---

#### `filtrar_por_estado(resultados_clasificados: List[Dict], estado: EstadoRespuesta) -> List[Dict]`

Filtra preguntas por estado de respuesta.

**Parámetros:**
- `resultados_clasificados`: Lista de preguntas del análisis
- `estado`: `"acierto"` | `"fallo"` | `"respuesta_debil"`

**Retorna:**
- Lista filtrada de preguntas

**Ejemplo:**
```python
analisis = detector.analizar_examen("examenes/Platzi/examen_20251120_134728.json")

# Obtener solo los fallos
fallos = detector.filtrar_por_estado(
    analisis["resultados_clasificados"], 
    "fallo"
)

print(f"Preguntas falladas: {len(fallos)}")
for fallo in fallos:
    print(f"- {fallo['pregunta'][:50]}...")
```

---

#### `generar_reporte_texto(analisis: Dict) -> str`

Genera reporte formateado en texto plano.

**Parámetros:**
- `analisis`: Resultado de `analizar_examen()`

**Retorna:**
- String con reporte formateado con emojis y tablas ASCII

**Ejemplo:**
```python
analisis = detector.analizar_examen("examenes/Platzi/examen_20251120_134728.json")
reporte = detector.generar_reporte_texto(analisis)

print(reporte)
# O guardar en archivo
with open("reporte.txt", "w", encoding="utf-8") as f:
    f.write(reporte)
```

---

### Clase `ResultadoPreguntaExtendido`

Modelo de datos para una pregunta clasificada.

**Atributos públicos:**
- `id_pregunta: str | None`
- `pregunta: str`
- `tipo: str`
- `opciones: List[str]`
- `respuesta_usuario: any`
- `respuesta_correcta: any | None`
- `puntos: float`
- `puntos_maximos: float`
- `feedback: str`
- `estado_respuesta: EstadoRespuesta` ← **NUEVO**

**Métodos:**
- `to_dict() -> Dict`: Convierte a diccionario

**Uso:**
```python
pregunta_data = {
    "pregunta": "¿Qué es Python?",
    "tipo": "corta",
    "puntos": 2.5,
    "puntos_maximos": 3,
    ...
}

pregunta = ResultadoPreguntaExtendido(pregunta_data)
print(pregunta.estado_respuesta)  # "respuesta_debil"
```

---

## 📁 Estructura de Archivos

```
Examinator/
├── detector_errores.py              # ← NUEVO: Módulo principal
├── MODULO1_DISEÑO_TECNICO.md        # ← NUEVO: Este documento
├── test_detector_errores.py         # ← NUEVO: Tests unitarios (próximo paso)
│
├── api_server.py                    # Sin modificar
├── generador_unificado.py           # Sin modificar
├── examinator.py                    # Sin modificar
├── ...                              # Resto del sistema intacto
│
└── examenes/                        # Datos de entrada (sin modificar)
    ├── Platzi/
    │   ├── examen_20251120_134728.json
    │   └── ...
    └── .../
```

---

## 🧪 Casos de Prueba

### Test 1: Pregunta Múltiple Correcta
```python
{
  "tipo": "multiple",
  "respuesta_usuario": "A",
  "respuesta_correcta": "A",
  "puntos": 3,
  "puntos_maximos": 3
}
```
**Esperado:** `"acierto"`

### Test 2: Pregunta Múltiple Incorrecta
```python
{
  "tipo": "multiple",
  "respuesta_usuario": "B",
  "respuesta_correcta": "A",
  "puntos": 0,
  "puntos_maximos": 3
}
```
**Esperado:** `"fallo"`

### Test 3: Verdadero/Falso con respuesta_correcta null
```python
{
  "tipo": "verdadero_falso",
  "respuesta_usuario": "falso",
  "respuesta_correcta": null,
  "puntos": 2,
  "puntos_maximos": 2
}
```
**Esperado:** `"acierto"` (ratio: 2/2 = 1.0 >= 0.9)

### Test 4: Desarrollo - Respuesta Parcial
```python
{
  "tipo": "desarrollo",
  "puntos": 2.5,
  "puntos_maximos": 3
}
```
**Esperado:** `"respuesta_debil"` (ratio: 0.833 está en [0.7, 0.89])

### Test 5: Corta - Fallo
```python
{
  "tipo": "corta",
  "puntos": 0.5,
  "puntos_maximos": 3
}
```
**Esperado:** `"fallo"` (ratio: 0.166 < 0.7)

### Test 6: Flashcard - Respuesta Débil
```python
{
  "tipo": "flashcard",
  "respuesta_correcta": null,
  "puntos": 0.8,
  "puntos_maximos": 1
}
```
**Esperado:** `"respuesta_debil"` (ratio: 0.8 está en [0.7, 0.89])

### Test 7: Caso Borde - Puntos Máximos = 0
```python
{
  "tipo": "multiple",
  "puntos": 0,
  "puntos_maximos": 0
}
```
**Esperado:** `"fallo"` (ratio: 0 < 0.7)

---

## ⚠️ Consideraciones Especiales

### 1. Normalización de Respuestas
Para preguntas objetivas con comparación directa:
```python
resp_usuario = str(respuesta_usuario).strip().lower()
resp_correcta = str(respuesta_correcta).strip().lower()
```
Evita falsos negativos por espacios/mayúsculas.

### 2. Manejo de respuesta_correcta = null
- Común en: `flashcard`, `verdadero_falso`, `corta`, `desarrollo`
- Razón: Evaluadas por IA, no tienen "respuesta exacta"
- Solución: Usar ratio de puntos

### 3. Compatibilidad Retroactiva
- `id_pregunta` puede no existir en exámenes antiguos
- Se maneja con `.get("id_pregunta", None)`

### 4. Validación de Entrada
- Verifica que el examen sea tipo `"completado"`
- Lanza excepciones descriptivas para debugging

---

## 🚀 Próximos Pasos (Fuera del Alcance del Módulo 1)

1. **Módulo 2:** Agrupador de Errores por Tema
2. **Módulo 3:** Generador de Prácticas Focalizadas
3. **Integración con API:** Endpoints REST en `api_server.py`
4. **Dashboard Visual:** Gráficas de patrones de error
5. **Histórico de Progreso:** Análisis longitudinal

---

## 📚 Referencias

- **Sistema Examinator:** `DOCUMENTACION_COMPLETA_SISTEMA.md`
- **Estructura JSON de Exámenes:** `examenes/**/*.json`
- **Generador de Exámenes:** `generador_unificado.py`
- **API Principal:** `api_server.py`

---

## ✅ Checklist de Implementación

- [x] Diseñar estructura de clases
- [x] Implementar `ResultadoPreguntaExtendido`
- [x] Implementar `DetectorErrores.analizar_examen()`
- [x] Implementar clasificación por tipo de pregunta
- [x] Implementar filtrado por estado
- [x] Implementar generación de reportes
- [x] Documentar API completa
- [ ] Tests unitarios (siguiente tarea)
- [ ] Integración con sistema existente
- [ ] Documentación de usuario

---

**Versión:** 1.0  
**Fecha:** 22 de noviembre de 2025  
**Autor:** GitHub Copilot  
**Estado:** ✅ Diseño Completo - Listo para Testing

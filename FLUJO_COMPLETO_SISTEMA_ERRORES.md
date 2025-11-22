# 🔄 FLUJO COMPLETO: Del Examen al Banco de Errores

## 📋 Visión General

Este documento explica paso a paso cómo funcionan juntos el **Módulo 1 (Detector de Errores)** y el **Módulo 2 (Banco de Errores)** cuando un usuario completa un examen en Examinator.

---

## 🎯 Flujo Completo Paso a Paso

### FASE 1: Usuario Completa un Examen

```
Usuario → Examinator Web → API Server
```

**Acciones:**
1. Usuario responde todas las preguntas del examen
2. Frontend envía respuestas al backend (`POST /api/evaluar-examen`)
3. Backend evalúa cada pregunta (IA para subjetivas, comparación para objetivas)
4. Backend calcula puntuación total

**Resultado:**
```json
// examenes/Platzi/examen_20251122_143000.json
{
  "id": "20251122_143000",
  "fecha_completado": "2025-11-22T14:30:00",
  "carpeta_ruta": "Platzi/Diseño UX",
  "carpeta_nombre": "Diseño UX",
  "puntos_obtenidos": 5.5,
  "puntos_totales": 10,
  "porcentaje": 55.0,
  "resultados": [
    {
      "pregunta": "¿Qué es el diseño centrado en el usuario?",
      "tipo": "corta",
      "respuesta_usuario": "Un enfoque",
      "respuesta_correcta": null,
      "puntos": 1.0,
      "puntos_maximos": 3,
      "feedback": "Incompleto. Necesitas desarrollar más..."
    },
    {
      "pregunta": "Explica la jerarquía visual",
      "tipo": "desarrollo",
      "respuesta_usuario": "Es organizar elementos por importancia...",
      "respuesta_correcta": null,
      "puntos": 4.5,
      "puntos_maximos": 5,
      "feedback": "¡Excelente respuesta! Comprendes bien el concepto..."
    }
  ],
  "tipo": "completado"
}
```

**📝 Estado:** Examen guardado en disco, usuario ve su puntuación.

---

### FASE 2: Detector de Errores Analiza (Módulo 1)

```python
from detector_errores import DetectorErrores

detector = DetectorErrores()
analisis = detector.analizar_examen("examenes/Platzi/examen_20251122_143000.json")
```

**Proceso:**
1. Lee el JSON del examen completado
2. Para cada pregunta en `resultados[]`:
   - Calcula ratio: `puntos / puntos_maximos`
   - Aplica reglas de clasificación según tipo
   - Asigna `estado_respuesta`: "acierto" | "fallo" | "respuesta_debil"

**Resultado:**
```python
{
  "metadata": {
    "id": "20251122_143000",
    "carpeta": "Diseño UX",
    "fecha_completado": "2025-11-22T14:30:00",
    "puntos_obtenidos": 5.5,
    "puntos_totales": 10,
    "porcentaje": 55.0
  },
  "resultados_clasificados": [
    {
      "pregunta": "¿Qué es el diseño centrado en el usuario?",
      "tipo": "corta",
      "puntos": 1.0,
      "puntos_maximos": 3,
      "estado_respuesta": "fallo"  # ← 1.0/3.0 = 0.33 < 0.7
    },
    {
      "pregunta": "Explica la jerarquía visual",
      "tipo": "desarrollo",
      "puntos": 4.5,
      "puntos_maximos": 5,
      "estado_respuesta": "acierto"  # ← 4.5/5.0 = 0.9 >= 0.9
    }
  ],
  "resumen_estados": {
    "total_preguntas": 2,
    "aciertos": 1,
    "fallos": 1,
    "respuestas_debiles": 0
  }
}
```

**📊 Estado:** Cada pregunta tiene clasificación de desempeño.

---

### FASE 3: Filtrar Errores para el Banco

```python
errores_a_procesar = [
    pregunta for pregunta in analisis["resultados_clasificados"]
    if pregunta["estado_respuesta"] in ["fallo", "respuesta_debil"]
]
```

**Lógica:**
- Solo se procesan preguntas con `fallo` o `respuesta_debil`
- Los `aciertos` se descartan (no necesitan refuerzo)

**En nuestro ejemplo:**
```python
errores_a_procesar = [
    {
      "pregunta": "¿Qué es el diseño centrado en el usuario?",
      "estado_respuesta": "fallo",
      ...
    }
]
# Total: 1 error para agregar al banco
```

**📌 Estado:** Identificados 1 error que necesita refuerzo.

---

### FASE 4: Actualizar Banco de Errores (Módulo 2)

```python
from banco_errores import BancoErrores

banco = BancoErrores()
resultado = banco.actualizar_banco_desde_examen(
    "examenes/Platzi/examen_20251122_143000.json"
)
```

#### Subproceso 4.1: Calcular Hash de Pregunta

```python
hash_pregunta = sha256("¿qué es el diseño centrado en el usuario?")
# hash_pregunta = "7f8e9a3b2c1d..."
```

**Propósito:** Detectar si la misma pregunta ya falló antes.

#### Subproceso 4.2: Buscar en Banco Existente

```python
error_existente = buscar_por_hash(banco["errores"], hash_pregunta)
```

**Escenario A: Error NUEVO (no existe en banco)**

```python
# Crear nueva entrada
nuevo_error = {
  "id_error": "uuid-generado",
  "hash_pregunta": "7f8e9a3b2c1d...",
  "examen_origen": {
    "id": "20251122_143000",
    "carpeta_ruta": "Platzi/Diseño UX"
  },
  "pregunta": {
    "texto": "¿Qué es el diseño centrado en el usuario?",
    "tipo": "corta"
  },
  "historial_respuestas": [
    {
      "fecha": "2025-11-22T14:30:00",
      "respuesta_usuario": "Un enfoque",
      "puntos": 1.0,
      "puntos_maximos": 3,
      "estado": "fallo",
      "examen_id": "20251122_143000"
    }
  ],
  "veces_fallada": 1,
  "veces_practicada": 1,
  "ultima_vez_practicada": "2025-11-22T14:30:00",
  "fecha_primer_error": "2025-11-22T14:30:00",
  "estado_refuerzo": "nuevo_error",
  "prioridad": "media"
}

# Agregar al banco
banco["errores"].append(nuevo_error)
```

**Escenario B: Error EXISTENTE (pregunta repetida)**

```python
# La pregunta ya existe en el banco
error_existente = {
  "id_error": "abc123...",
  "hash_pregunta": "7f8e9a3b2c1d...",
  "historial_respuestas": [
    {
      "fecha": "2025-11-20T10:00:00",
      "estado": "fallo",
      "puntos": 0.5
    }
  ],
  "veces_fallada": 1,
  "veces_practicada": 1,
  "estado_refuerzo": "nuevo_error"
}

# Actualizar con nuevo intento
error_existente["historial_respuestas"].append({
  "fecha": "2025-11-22T14:30:00",
  "respuesta_usuario": "Un enfoque",
  "puntos": 1.0,
  "estado": "fallo"
})

error_existente["veces_fallada"] = 2
error_existente["veces_practicada"] = 2
error_existente["estado_refuerzo"] = "en_refuerzo"
error_existente["prioridad"] = "media"  # o "alta" si veces_fallada >= 3
```

#### Subproceso 4.3: Guardar Banco Actualizado

```python
# examenes/error_bank/banco_errores_global.json
{
  "version": "2.0",
  "fecha_ultima_actualizacion": "2025-11-22T14:30:15",
  "total_errores_registrados": 1,
  "errores": [
    {
      "id_error": "uuid-generado",
      "hash_pregunta": "7f8e9a3b2c1d...",
      "examen_origen": {...},
      "pregunta": {...},
      "historial_respuestas": [...],
      "veces_fallada": 1,
      "estado_refuerzo": "nuevo_error",
      "prioridad": "media"
    }
  ]
}
```

#### Subproceso 4.4: Actualizar Estadísticas

```python
# examenes/error_bank/estadisticas_resumen.json
{
  "fecha_actualizacion": "2025-11-22T14:30:15",
  "total_errores": 1,
  "por_estado": {
    "nuevos": 1,
    "en_refuerzo": 0,
    "resueltos": 0
  },
  "por_prioridad": {
    "alta": 0,
    "media": 1,
    "baja": 0
  },
  "errores_activos": 1,
  "tasa_resolucion": 0.0
}
```

**✅ Estado:** Banco actualizado y guardado en disco.

---

### FASE 5: Notificación al Usuario (Opcional)

```python
print(f"✅ {resultado['mensaje']}")
print(f"   Se agregaron {resultado['nuevos']} errores nuevos")
print(f"   Se actualizaron {resultado['actualizados']} errores existentes")
print(f"   Tienes {resultado['errores_activos']} errores pendientes de refuerzo")
```

**Salida:**
```
✅ Banco de errores actualizado exitosamente
   Se agregaron 1 errores nuevos
   Se actualizados 0 errores existentes
   Tienes 1 errores pendientes de refuerzo
```

**💬 Estado:** Usuario informado sobre errores que necesita reforzar.

---

## 🔀 Casos Especiales

### Caso 1: Examen Sin Errores (Todo Aciertos)

```
Usuario → Completa examen → 10/10 puntos

Detector → Analiza → 5 aciertos, 0 fallos, 0 débiles

Banco → Nada que agregar

Resultado: "✅ No hay errores que agregar al banco"
```

### Caso 2: Pregunta Repetida que Mejoró

```
Primera vez:
  Pregunta X → fallo (1.0/3.0 puntos)
  Banco → Agrega error nuevo

Segunda vez:
  Pregunta X → respuesta_debil (2.5/3.0 puntos)
  Banco → Actualiza historial, cambia estado a "en_refuerzo"

Tercera vez:
  Pregunta X → acierto (3.0/3.0 puntos)
  Banco → Actualiza historial, cambia estado a "resuelto"
```

### Caso 3: Recaída (Error Resuelto Vuelve a Fallar)

```
Historial:
  Intento 1: fallo
  Intento 2: acierto
  Intento 3: acierto → Estado: "resuelto"
  
Nuevo examen:
  Intento 4: fallo

Banco → 
  - Cambia estado: "resuelto" → "en_refuerzo"
  - Incrementa veces_fallada
  - Aumenta prioridad: "baja" → "alta" (recaída es grave)
```

---

## 📊 Diagrama de Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│  1. USUARIO COMPLETA EXAMEN                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  2. SISTEMA GUARDA RESULTADO                                │
│     examenes/{carpeta}/examen_{timestamp}.json              │
│     • resultados[] con respuestas y puntos                  │
│     • tipo: "completado"                                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  3. DETECTOR DE ERRORES (Módulo 1)                          │
│     detector.analizar_examen(ruta)                          │
│                                                              │
│     Para cada pregunta:                                     │
│       ratio = puntos / puntos_maximos                       │
│       IF tipo objetiva Y respuesta_correcta existe:         │
│         comparar respuestas                                 │
│       ELSE:                                                 │
│         usar ratio                                          │
│                                                              │
│     Output: resultados_clasificados[]                       │
│             con estado_respuesta                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  4. FILTRAR ERRORES                                         │
│     errores = filter(estado IN ["fallo", "respuesta_debil"])│
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  5. BANCO DE ERRORES (Módulo 2)                             │
│     banco.actualizar_banco_desde_examen(ruta)               │
│                                                              │
│     Para cada error:                                        │
│       hash = sha256(pregunta.texto)                         │
│       error_existente = buscar_por_hash(hash)               │
│                                                              │
│       IF error_existente:                                   │
│         • Agregar a historial_respuestas[]                  │
│         • Incrementar contadores                            │
│         • Recalcular estado_refuerzo                        │
│         • Recalcular prioridad                              │
│       ELSE:                                                 │
│         • Crear nuevo error                                 │
│         • estado_refuerzo = "nuevo_error"                   │
│         • prioridad = calcular_inicial()                    │
│                                                              │
│     Guardar: examenes/error_bank/                           │
│              banco_errores_global.json                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  6. ACTUALIZAR ESTADÍSTICAS                                 │
│     examenes/error_bank/estadisticas_resumen.json           │
│     • Total errores                                         │
│     • Por estado (nuevo/refuerzo/resuelto)                  │
│     • Por prioridad (alta/media/baja)                       │
│     • Tasa de resolución                                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  7. USUARIO VE FEEDBACK                                     │
│     • "Se agregaron 2 errores al banco"                     │
│     • "Tienes 15 errores pendientes de refuerzo"            │
│     • "Recuerda practicar las preguntas de alta prioridad"  │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Integración en el Sistema Existente

### Opción 1: Llamada Manual

```python
# En el backend, después de guardar examen
from banco_errores import BancoErrores

# Guardar examen (código existente)
guardar_examen(examen_data)

# Actualizar banco (NUEVO)
banco = BancoErrores()
resultado = banco.actualizar_banco_desde_examen(ruta_examen)

# Retornar al frontend
return {
    "examen_guardado": True,
    "banco_actualizado": True,
    "errores_nuevos": resultado['nuevos'],
    "errores_activos": resultado['errores_activos']
}
```

### Opción 2: Endpoint Dedicado

```python
@app.post("/api/actualizar-banco-errores")
async def actualizar_banco_errores(data: dict):
    """
    Endpoint para actualizar el banco después de completar un examen.
    Se puede llamar desde el frontend después de guardar el examen.
    """
    ruta_examen = data.get("ruta_examen")
    
    banco = BancoErrores()
    resultado = banco.actualizar_banco_desde_examen(ruta_examen)
    
    return resultado
```

### Opción 3: Proceso Automático (Recomendado)

```python
@app.post("/api/evaluar-examen")
async def evaluar_examen(data: dict):
    """
    Endpoint existente modificado para incluir actualización del banco.
    """
    # Código existente: evaluar y guardar examen
    examen_guardado = guardar_examen_completado(data)
    ruta_examen = examen_guardado["archivo"]
    
    # NUEVO: Actualizar banco automáticamente
    try:
        banco = BancoErrores()
        resultado_banco = banco.actualizar_banco_desde_examen(ruta_examen)
    except Exception as e:
        # No fallar si hay error en banco (no es crítico)
        print(f"⚠️ Error actualizando banco: {e}")
        resultado_banco = None
    
    return {
        "examen": examen_guardado,
        "banco": resultado_banco
    }
```

---

## 🎯 Beneficios del Sistema Integrado

✅ **Automático:** Se actualiza sin intervención manual  
✅ **No invasivo:** No rompe flujo existente  
✅ **Historial completo:** Rastrea progreso a lo largo del tiempo  
✅ **Detección inteligente:** Identifica preguntas repetidas  
✅ **Priorización:** Enfoca en errores más críticos  
✅ **Preparado para siguiente módulo:** Datos listos para generar prácticas personalizadas  

---

## 🚀 Próximos Pasos

1. **Módulo 3:** Generador de prácticas personalizadas basadas en errores
2. **Dashboard:** Visualización de progreso y estadísticas
3. **Notificaciones:** Alertas cuando hay muchos errores acumulados
4. **Exportación:** Generar PDFs con errores pendientes

---

**Versión:** 1.0  
**Fecha:** 22 de noviembre de 2025  
**Estado:** ✅ Flujo Completo Documentado

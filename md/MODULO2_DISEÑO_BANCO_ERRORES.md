# 🏦 MÓDULO 2: Banco de Errores - Diseño Técnico

## 📋 Resumen Ejecutivo

El **Banco de Errores (Error Bank)** es un repositorio centralizado que almacena todas las preguntas falladas o respondidas débilmente por el usuario, permitiendo seguimiento personalizado y generación de prácticas de refuerzo.

**Propósito:** Crear un sistema de memoria persistente de errores para:
- Identificar patrones de error recurrentes
- Priorizar temas que necesitan refuerzo
- Generar prácticas personalizadas
- Rastrear progreso de mejora

---

## 🗂️ Estructura de Archivos Propuesta

### Opción Elegida: **Archivo Único Global**

```
examenes/
└── error_bank/
    ├── banco_errores_global.json      # Todos los errores del usuario
    ├── estadisticas_resumen.json       # Estadísticas agregadas (cache)
    └── backups/                        # Copias de seguridad (opcional)
        ├── banco_errores_20251122.json
        └── banco_errores_20251121.json
```

### Razones de la Elección:

✅ **Simplicidad:** Un solo archivo para consultar todo  
✅ **Búsqueda eficiente:** No hay que recorrer múltiples archivos  
✅ **Estadísticas globales:** Fácil calcular métricas agregadas  
✅ **Portable:** Se puede exportar/importar fácilmente  
✅ **Sin fragmentación:** Todos los datos en un lugar  

### Alternativas Descartadas:

❌ **Un archivo por carpeta:** Dificulta análisis global  
❌ **Un archivo por examen:** Demasiada fragmentación  
❌ **Un archivo por tipo de pregunta:** Complica mantenimiento  

---

## 📊 Estructura del JSON del Banco de Errores

### `banco_errores_global.json`

```json
{
  "version": "2.0",
  "fecha_creacion": "2025-11-22T10:00:00",
  "fecha_ultima_actualizacion": "2025-11-22T14:30:00",
  "total_errores_registrados": 45,
  "errores": [
    {
      // === IDENTIFICACIÓN ===
      "id_error": "uuid-generado",
      "hash_pregunta": "sha256-de-pregunta",  // Para detectar duplicados
      
      // === REFERENCIA AL EXAMEN ===
      "examen_origen": {
        "id": "20251120_134728",
        "archivo": "examen_20251120_134728.json",
        "fecha_completado": "2025-11-20T13:47:28",
        "carpeta_ruta": "Platzi/Diseño UX/Fundamentos",
        "carpeta_nombre": "Fundamentos"
      },
      
      // === DATOS DE LA PREGUNTA ===
      "pregunta": {
        "texto": "¿Qué categoría de principios jurídicos...",
        "tipo": "flashcard",
        "opciones": [],
        "respuesta_correcta": null
      },
      
      // === HISTORIAL DE INTENTOS ===
      "historial_respuestas": [
        {
          "fecha": "2025-11-20T13:47:28",
          "respuesta_usuario": "Relación y jerarquía",
          "puntos": 0.5,
          "puntos_maximos": 1,
          "estado": "fallo",
          "examen_id": "20251120_134728"
        },
        {
          "fecha": "2025-11-21T10:15:00",
          "respuesta_usuario": "Percepción y comportamiento",
          "puntos": 0.8,
          "puntos_maximos": 1,
          "estado": "respuesta_debil",
          "examen_id": "20251121_101500"
        }
      ],
      
      // === CAMPOS DE SEGUIMIENTO ===
      "veces_fallada": 2,
      "veces_practicada": 2,
      "ultima_vez_practicada": "2025-11-21T10:15:00",
      "fecha_primer_error": "2025-11-20T13:47:28",
      "estado_refuerzo": "en_refuerzo",  // "nuevo_error" | "en_refuerzo" | "resuelto"
      
      // === METADATOS ADICIONALES ===
      "prioridad": "alta",  // "alta" | "media" | "baja" (calculado automáticamente)
      "tema_detectado": null,  // Para Módulo 3 (futuro)
      "etiquetas": ["diseño", "principios", "UX"],  // Para Módulo 3 (futuro)
      "nota_usuario": ""  // El usuario puede agregar notas manuales
    }
  ]
}
```

---

## 🔑 Campos Clave Explicados

### `id_error`
- **Tipo:** UUID v4
- **Propósito:** Identificador único del error en el banco
- **Ejemplo:** `"550e8400-e29b-41d4-a716-446655440000"`

### `hash_pregunta`
- **Tipo:** SHA-256 hash del texto de la pregunta
- **Propósito:** Detectar si la misma pregunta se falló en múltiples exámenes
- **Cálculo:** `sha256(pregunta.texto.strip().lower())`
- **Ejemplo:** `"a3c7f8e9b2d1..."`

### `historial_respuestas[]`
- **Propósito:** Rastrear todas las veces que se intentó responder esta pregunta
- **Permite:** Ver progreso de mejora (de "fallo" → "respuesta_debil" → "acierto")

### `estado_refuerzo`

| Estado | Descripción | Cuándo |
|--------|-------------|--------|
| `nuevo_error` | Primera vez que se falla | `veces_fallada == 1` |
| `en_refuerzo` | Se está practicando | `veces_practicada >= 2 && último_intento != "acierto"` |
| `resuelto` | Ya se domina | Último intento fue "acierto" + criterio temporal |

### `prioridad`

**Cálculo automático:**
```python
if veces_fallada >= 3:
    prioridad = "alta"
elif veces_fallada >= 2 or ultima_vez_practicada < hace_7_dias:
    prioridad = "media"
else:
    prioridad = "baja"
```

---

## 🔄 Flujo Completo de Actualización

### Cuando se Completa un Examen:

```
┌─────────────────────────────────────────────────────────────┐
│  1. USUARIO COMPLETA EXAMEN                                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  2. GUARDAR RESULTADO HABITUAL                              │
│     • Archivo: examenes/{carpeta}/examen_{timestamp}.json   │
│     • Estructura original del sistema                       │
│     • NO SE MODIFICA                                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  3. EJECUTAR DETECTOR DE ERRORES (Módulo 1)                 │
│     • Leer JSON del examen                                  │
│     • Clasificar cada pregunta:                             │
│       - acierto                                             │
│       - fallo                                               │
│       - respuesta_debil                                     │
│     • Generar análisis extendido                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  4. FILTRAR ERRORES PARA EL BANCO                           │
│     • Seleccionar preguntas con:                            │
│       - estado_respuesta == "fallo"                         │
│       - estado_respuesta == "respuesta_debil"               │
│     • Descartar aciertos                                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  5. ACTUALIZAR BANCO DE ERRORES (Módulo 2)                  │
│                                                              │
│  Para cada pregunta con error:                              │
│                                                              │
│  5.1. Calcular hash_pregunta                                │
│       • hash = sha256(pregunta.texto)                       │
│                                                              │
│  5.2. Buscar en banco existente                             │
│       • ¿Existe error con mismo hash?                       │
│                                                              │
│       SI EXISTE (pregunta repetida):                        │
│       ├─ Agregar entrada a historial_respuestas[]           │
│       ├─ Incrementar veces_fallada                          │
│       ├─ Incrementar veces_practicada                       │
│       ├─ Actualizar ultima_vez_practicada                   │
│       ├─ Recalcular estado_refuerzo                         │
│       └─ Recalcular prioridad                               │
│                                                              │
│       NO EXISTE (error nuevo):                              │
│       ├─ Generar nuevo id_error (UUID)                      │
│       ├─ Crear estructura completa del error                │
│       ├─ veces_fallada = 1                                  │
│       ├─ estado_refuerzo = "nuevo_error"                    │
│       ├─ prioridad = calcular_prioridad()                   │
│       └─ Agregar a errores[]                                │
│                                                              │
│  5.3. Guardar banco actualizado                             │
│       • Escribir banco_errores_global.json                  │
│       • Actualizar fecha_ultima_actualizacion               │
│       • Incrementar total_errores_registrados               │
│                                                              │
│  5.4. Actualizar estadísticas (opcional)                    │
│       • Calcular resumen para cache                         │
│       • Guardar estadisticas_resumen.json                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  6. NOTIFICAR AL USUARIO (Opcional)                         │
│     • "Se agregaron 3 errores al banco de refuerzo"         │
│     • "Tienes 12 errores pendientes de práctica"            │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Pseudocódigo de Alto Nivel

### Función Principal: `actualizar_banco_errores()`

```python
función actualizar_banco_errores(ruta_examen_json):
    """
    Actualiza el banco de errores después de completar un examen.
    
    Args:
        ruta_examen_json: Ruta al JSON del examen completado
    
    Returns:
        dict: Resumen de la actualización
    """
    
    # ===== PASO 1: ANALIZAR EXAMEN CON DETECTOR DE ERRORES =====
    detector = DetectorErrores()
    analisis = detector.analizar_examen(ruta_examen_json)
    
    # ===== PASO 2: FILTRAR SOLO ERRORES Y DÉBILES =====
    errores_a_agregar = []
    
    PARA CADA pregunta EN analisis["resultados_clasificados"]:
        SI pregunta["estado_respuesta"] EN ["fallo", "respuesta_debil"]:
            errores_a_agregar.append(pregunta)
    
    SI errores_a_agregar está vacío:
        RETORNAR {"mensaje": "No hay errores que agregar", "nuevos": 0, "actualizados": 0}
    
    # ===== PASO 3: CARGAR BANCO EXISTENTE =====
    ruta_banco = "examenes/error_bank/banco_errores_global.json"
    
    SI archivo existe:
        banco = leer_json(ruta_banco)
    SINO:
        banco = crear_banco_vacio()
    
    # ===== PASO 4: PROCESAR CADA ERROR =====
    contador_nuevos = 0
    contador_actualizados = 0
    
    PARA CADA error EN errores_a_agregar:
        
        # Calcular hash único de la pregunta
        hash_pregunta = calcular_hash(error["pregunta"])
        
        # Buscar si ya existe en el banco
        error_existente = buscar_por_hash(banco["errores"], hash_pregunta)
        
        SI error_existente EXISTE:
            # Actualizar error existente
            actualizar_error_existente(
                error_existente,
                error,
                analisis["metadata"]
            )
            contador_actualizados += 1
        SINO:
            # Crear nuevo error
            nuevo_error = crear_nuevo_error(
                error,
                analisis["metadata"],
                hash_pregunta
            )
            banco["errores"].append(nuevo_error)
            contador_nuevos += 1
    
    # ===== PASO 5: ACTUALIZAR METADATOS DEL BANCO =====
    banco["fecha_ultima_actualizacion"] = ahora()
    banco["total_errores_registrados"] = len(banco["errores"])
    
    # ===== PASO 6: GUARDAR BANCO ACTUALIZADO =====
    crear_directorio_si_no_existe("examenes/error_bank/")
    guardar_json(ruta_banco, banco)
    
    # ===== PASO 7: ACTUALIZAR CACHE DE ESTADÍSTICAS =====
    actualizar_estadisticas_resumen(banco)
    
    # ===== PASO 8: RETORNAR RESUMEN =====
    RETORNAR {
        "mensaje": "Banco de errores actualizado",
        "nuevos": contador_nuevos,
        "actualizados": contador_actualizados,
        "total_banco": len(banco["errores"]),
        "errores_activos": contar_errores_activos(banco),
        "errores_resueltos": contar_errores_resueltos(banco)
    }


# ===== FUNCIONES AUXILIARES =====

función calcular_hash(texto_pregunta):
    """Calcula SHA-256 hash de la pregunta para detectar duplicados."""
    texto_normalizado = texto_pregunta.strip().lower()
    RETORNAR sha256(texto_normalizado)


función crear_banco_vacio():
    """Crea estructura inicial del banco."""
    RETORNAR {
        "version": "2.0",
        "fecha_creacion": ahora(),
        "fecha_ultima_actualizacion": ahora(),
        "total_errores_registrados": 0,
        "errores": []
    }


función crear_nuevo_error(pregunta, metadata_examen, hash_pregunta):
    """Crea una nueva entrada de error en el banco."""
    
    RETORNAR {
        "id_error": generar_uuid(),
        "hash_pregunta": hash_pregunta,
        
        "examen_origen": {
            "id": metadata_examen["id"],
            "archivo": metadata_examen["archivo"],
            "fecha_completado": metadata_examen["fecha_completado"],
            "carpeta_ruta": metadata_examen["carpeta_ruta"],
            "carpeta_nombre": metadata_examen["carpeta_nombre"]
        },
        
        "pregunta": {
            "texto": pregunta["pregunta"],
            "tipo": pregunta["tipo"],
            "opciones": pregunta["opciones"],
            "respuesta_correcta": pregunta["respuesta_correcta"]
        },
        
        "historial_respuestas": [
            {
                "fecha": metadata_examen["fecha_completado"],
                "respuesta_usuario": pregunta["respuesta_usuario"],
                "puntos": pregunta["puntos"],
                "puntos_maximos": pregunta["puntos_maximos"],
                "estado": pregunta["estado_respuesta"],
                "examen_id": metadata_examen["id"]
            }
        ],
        
        "veces_fallada": 1,
        "veces_practicada": 1,
        "ultima_vez_practicada": metadata_examen["fecha_completado"],
        "fecha_primer_error": metadata_examen["fecha_completado"],
        "estado_refuerzo": "nuevo_error",
        "prioridad": "media",  # Inicial, se recalcula después
        "tema_detectado": null,
        "etiquetas": [],
        "nota_usuario": ""
    }


función actualizar_error_existente(error_existente, nuevo_intento, metadata_examen):
    """Actualiza un error que ya existe en el banco."""
    
    # Agregar nuevo intento al historial
    error_existente["historial_respuestas"].append({
        "fecha": metadata_examen["fecha_completado"],
        "respuesta_usuario": nuevo_intento["respuesta_usuario"],
        "puntos": nuevo_intento["puntos"],
        "puntos_maximos": nuevo_intento["puntos_maximos"],
        "estado": nuevo_intento["estado_respuesta"],
        "examen_id": metadata_examen["id"]
    })
    
    # Actualizar contadores
    SI nuevo_intento["estado_respuesta"] == "fallo":
        error_existente["veces_fallada"] += 1
    
    error_existente["veces_practicada"] += 1
    error_existente["ultima_vez_practicada"] = metadata_examen["fecha_completado"]
    
    # Recalcular estado de refuerzo
    ultimo_estado = nuevo_intento["estado_respuesta"]
    
    SI ultimo_estado == "acierto":
        # Verificar si se considera resuelto
        SI criterio_resolucion_cumplido(error_existente):
            error_existente["estado_refuerzo"] = "resuelto"
        SINO:
            error_existente["estado_refuerzo"] = "en_refuerzo"
    SINO:
        error_existente["estado_refuerzo"] = "en_refuerzo"
    
    # Recalcular prioridad
    error_existente["prioridad"] = calcular_prioridad(error_existente)


función calcular_prioridad(error):
    """Calcula la prioridad del error basándose en historial."""
    
    veces_fallada = error["veces_fallada"]
    dias_sin_practica = dias_desde(error["ultima_vez_practicada"])
    
    SI veces_fallada >= 3:
        RETORNAR "alta"
    SINO SI veces_fallada >= 2 O dias_sin_practica > 7:
        RETORNAR "media"
    SINO:
        RETORNAR "baja"


función criterio_resolucion_cumplido(error):
    """Determina si un error se considera resuelto."""
    
    # Criterio: Último intento fue acierto Y han pasado al menos 2 intentos desde el último fallo
    
    historial = error["historial_respuestas"]
    ultimo_intento = historial[-1]
    
    SI ultimo_intento["estado"] != "acierto":
        RETORNAR False
    
    # Contar intentos consecutivos sin fallos
    intentos_consecutivos_sin_fallos = 0
    PARA i DESDE len(historial)-1 HASTA 0:
        SI historial[i]["estado"] == "fallo":
            BREAK
        intentos_consecutivos_sin_fallos += 1
    
    RETORNAR intentos_consecutivos_sin_fallos >= 2


función actualizar_estadisticas_resumen(banco):
    """Genera cache de estadísticas para consultas rápidas."""
    
    total_errores = len(banco["errores"])
    errores_nuevos = contar_por_estado(banco["errores"], "nuevo_error")
    errores_en_refuerzo = contar_por_estado(banco["errores"], "en_refuerzo")
    errores_resueltos = contar_por_estado(banco["errores"], "resuelto")
    
    errores_alta_prioridad = contar_por_prioridad(banco["errores"], "alta")
    errores_media_prioridad = contar_por_prioridad(banco["errores"], "media")
    errores_baja_prioridad = contar_por_prioridad(banco["errores"], "baja")
    
    estadisticas = {
        "fecha_actualizacion": ahora(),
        "total_errores": total_errores,
        "por_estado": {
            "nuevos": errores_nuevos,
            "en_refuerzo": errores_en_refuerzo,
            "resueltos": errores_resueltos
        },
        "por_prioridad": {
            "alta": errores_alta_prioridad,
            "media": errores_media_prioridad,
            "baja": errores_baja_prioridad
        },
        "errores_activos": errores_nuevos + errores_en_refuerzo,
        "tasa_resolucion": (errores_resueltos / total_errores * 100) SI total_errores > 0 SINO 0
    }
    
    guardar_json("examenes/error_bank/estadisticas_resumen.json", estadisticas)
```

---

## 🔍 Ejemplo de Uso Completo

### Paso 1: Usuario Completa Examen

```json
// examenes/Platzi/examen_20251122_143000.json
{
  "id": "20251122_143000",
  "fecha_completado": "2025-11-22T14:30:00",
  "carpeta_ruta": "Platzi/Diseño UX",
  "carpeta_nombre": "Diseño UX",
  "puntos_obtenidos": 5.5,
  "puntos_totales": 10,
  "resultados": [
    {
      "pregunta": "¿Qué es el diseño centrado en el usuario?",
      "tipo": "corta",
      "respuesta_usuario": "Un enfoque",
      "puntos": 1.0,
      "puntos_maximos": 3
    },
    {
      "pregunta": "Explica la jerarquía visual",
      "tipo": "desarrollo",
      "respuesta_usuario": "Es organizar elementos por importancia...",
      "puntos": 4.5,
      "puntos_maximos": 5
    }
  ]
}
```

### Paso 2: Detector de Errores Analiza

```python
analisis = {
  "resultados_clasificados": [
    {
      "pregunta": "¿Qué es el diseño centrado en el usuario?",
      "estado_respuesta": "fallo"  # 1.0/3.0 = 0.33 < 0.7
    },
    {
      "pregunta": "Explica la jerarquía visual",
      "estado_respuesta": "acierto"  # 4.5/5.0 = 0.9 >= 0.9
    }
  ]
}
```

### Paso 3: Banco de Errores se Actualiza

```python
resultado = actualizar_banco_errores("examenes/Platzi/examen_20251122_143000.json")

# Salida:
{
  "mensaje": "Banco de errores actualizado",
  "nuevos": 1,  # La pregunta sobre diseño centrado en el usuario
  "actualizados": 0,
  "total_banco": 46,
  "errores_activos": 32,
  "errores_resueltos": 14
}
```

### Paso 4: Banco Resultante

```json
// examenes/error_bank/banco_errores_global.json
{
  "version": "2.0",
  "fecha_ultima_actualizacion": "2025-11-22T14:30:15",
  "total_errores_registrados": 46,
  "errores": [
    // ... errores anteriores ...
    {
      "id_error": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "hash_pregunta": "7f8e9a3b2c1d...",
      "examen_origen": {
        "id": "20251122_143000",
        "carpeta_ruta": "Platzi/Diseño UX",
        "carpeta_nombre": "Diseño UX"
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
          "estado": "fallo"
        }
      ],
      "veces_fallada": 1,
      "veces_practicada": 1,
      "ultima_vez_practicada": "2025-11-22T14:30:00",
      "estado_refuerzo": "nuevo_error",
      "prioridad": "media"
    }
  ]
}
```

---

## 🎯 Casos Especiales

### Caso 1: Pregunta Repetida (Mejoró)

**Primera vez (fallo):**
```json
{
  "fecha": "2025-11-20T10:00:00",
  "estado": "fallo",
  "puntos": 0.5
}
```

**Segunda vez (respuesta_debil):**
```json
{
  "fecha": "2025-11-21T15:00:00",
  "estado": "respuesta_debil",
  "puntos": 2.5
}
```

**Actualización:**
- `veces_practicada`: 1 → 2
- `estado_refuerzo`: "nuevo_error" → "en_refuerzo"
- `prioridad`: Se mantiene o ajusta según lógica

---

### Caso 2: Pregunta Resuelta

**Historial:**
```json
[
  {"fecha": "2025-11-20", "estado": "fallo"},
  {"fecha": "2025-11-21", "estado": "respuesta_debil"},
  {"fecha": "2025-11-22", "estado": "acierto"},
  {"fecha": "2025-11-23", "estado": "acierto"}
]
```

**Resultado:**
- `estado_refuerzo`: "resuelto"
- `prioridad`: "baja"
- **No se elimina del banco** (para estadísticas y seguimiento histórico)

---

### Caso 3: Recaída (Era Resuelto, Vuelve a Fallar)

**Antes:**
```json
{
  "estado_refuerzo": "resuelto",
  "historial_respuestas": [
    {"fecha": "2025-11-20", "estado": "fallo"},
    {"fecha": "2025-11-22", "estado": "acierto"},
    {"fecha": "2025-11-23", "estado": "acierto"}
  ]
}
```

**Nuevo intento falla:**
```json
{
  "fecha": "2025-11-25",
  "estado": "fallo"
}
```

**Actualización:**
- `estado_refuerzo`: "resuelto" → "en_refuerzo"
- `veces_fallada`: 1 → 2
- `prioridad`: "baja" → "alta" (recaída es grave)

---

## 📈 Ventajas del Diseño

✅ **Historial completo:** Se conserva todo el progreso  
✅ **Detección de duplicados:** Mediante hash_pregunta  
✅ **Priorización automática:** Basada en frecuencia y tiempo  
✅ **Sin pérdida de datos:** Errores resueltos se mantienen  
✅ **Estadísticas rápidas:** Cache en archivo separado  
✅ **Extensible:** Preparado para Módulo 3 (agrupación por temas)  

---

## 🚀 Próximos Pasos (Fuera del Alcance del Módulo 2)

1. **Módulo 3:** Agrupador de errores por tema (usando `tema_detectado` y `etiquetas`)
2. **Generador de prácticas personalizadas** basadas en el banco
3. **Visualización** de progreso en frontend
4. **Exportación** de banco a CSV/Excel para análisis

---

**Versión:** 2.0  
**Fecha:** 22 de noviembre de 2025  
**Estado:** ✅ Diseño Completo - Listo para Implementación

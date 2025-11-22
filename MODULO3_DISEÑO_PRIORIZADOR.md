# 🎯 MÓDULO 3: Priorizador de Errores - Diseño Técnico

## 📋 Resumen Ejecutivo

El **Priorizador de Errores** es un motor de recomendaciones que selecciona inteligentemente qué errores debe practicar el usuario hoy, basándose en criterios pedagógicos de prioridad y espaciado temporal.

**Propósito:** Optimizar el tiempo de estudio enfocándose en los errores más críticos y que más necesitan refuerzo.

---

## 🎯 Objetivos

1. **Priorización inteligente** de errores según múltiples criterios
2. **Recomendación personalizada** de N errores para practicar
3. **Optimización pedagógica** usando espaciado temporal
4. **Integración fluida** con sesiones de estudio

---

## 📊 Reglas de Prioridad (Algoritmo de Ordenamiento)

### Nivel 1: Estado de Refuerzo (Máxima Prioridad)

```
PRIMERO: estado_refuerzo == "nuevo_error"
  ↓
  Razón: Errores recién descubiertos necesitan atención inmediata
  para evitar consolidación de conceptos incorrectos
```

### Nivel 2: Frecuencia de Fallos

```
LUEGO: veces_fallada >= 2
  ↓
  Razón: Patrones de error recurrentes indican dificultad conceptual
  que requiere refuerzo intensivo
```

### Nivel 3: Antigüedad Sin Práctica

```
LUEGO: dias_desde_ultima_practica (mayor → menor)
  ↓
  Razón: Aplicación del "Spacing Effect" - errores sin reforzar
  durante mucho tiempo corren riesgo de olvidarse
```

### Nivel 4: Prioridad Calculada

```
FINALMENTE: prioridad (alta → media → baja)
  ↓
  Razón: Desempate final usando la prioridad automática del banco
```

---

## 🧮 Algoritmo Detallado

### Pseudocódigo de Alto Nivel

```python
función priorizar_errores_para_estudio(banco, hoy, max_errores):
    """
    Selecciona y ordena errores para sesión de estudio.
    
    Args:
        banco: Banco de errores completo
        hoy: Fecha actual (para calcular días sin práctica)
        max_errores: Número máximo de errores a retornar
    
    Returns:
        Lista ordenada de errores priorizados
    """
    
    # ===== PASO 1: FILTRAR ERRORES ACTIVOS =====
    errores_activos = filtrar_por_estado(
        banco.errores,
        ["nuevo_error", "en_refuerzo"]
    )
    
    SI errores_activos está vacío:
        RETORNAR []  # No hay nada que practicar
    
    # ===== PASO 2: CALCULAR MÉTRICAS PARA CADA ERROR =====
    PARA CADA error EN errores_activos:
        error.dias_sin_practica = calcular_dias(
            hoy - error.ultima_vez_practicada
        )
        
        # Calcular puntuación de prioridad compuesta
        error.puntuacion_prioridad = calcular_puntuacion(error)
    
    # ===== PASO 3: ORDENAR POR CRITERIOS MÚLTIPLES =====
    errores_ordenados = ordenar_multi_criterio(errores_activos, [
        # Criterio 1: Nuevos errores primero
        ("estado_refuerzo == 'nuevo_error'", DESCENDENTE),
        
        # Criterio 2: Frecuencia de fallos (≥2)
        ("veces_fallada >= 2", DESCENDENTE),
        
        # Criterio 3: Días sin práctica
        ("dias_sin_practica", DESCENDENTE),
        
        # Criterio 4: Prioridad
        ("prioridad_numerica", DESCENDENTE)  # alta=3, media=2, baja=1
    ])
    
    # ===== PASO 4: LIMITAR A N ERRORES =====
    errores_seleccionados = errores_ordenados[:max_errores]
    
    # ===== PASO 5: ENRIQUECER CON METADATOS =====
    PARA CADA error EN errores_seleccionados:
        error.razon_seleccion = generar_razon(error)
        error.recomendacion_estudio = generar_recomendacion(error)
    
    RETORNAR errores_seleccionados


# ===== FUNCIÓN AUXILIAR: CALCULAR PUNTUACIÓN =====

función calcular_puntuacion(error):
    """Calcula puntuación compuesta de prioridad."""
    
    puntuacion = 0
    
    # Factor 1: Estado (nuevo = urgente)
    SI error.estado_refuerzo == "nuevo_error":
        puntuacion += 100  # Máxima prioridad
    SINO SI error.estado_refuerzo == "en_refuerzo":
        puntuacion += 50
    
    # Factor 2: Frecuencia de fallos
    puntuacion += error.veces_fallada * 10
    
    # Factor 3: Días sin práctica (espaciado temporal)
    puntuacion += error.dias_sin_practica * 2
    
    # Factor 4: Prioridad del banco
    SI error.prioridad == "alta":
        puntuacion += 30
    SINO SI error.prioridad == "media":
        puntuacion += 15
    SINO:
        puntuacion += 5
    
    RETORNAR puntuacion


# ===== FUNCIÓN AUXILIAR: GENERAR RAZÓN =====

función generar_razon(error):
    """Explica por qué se seleccionó este error."""
    
    razones = []
    
    SI error.estado_refuerzo == "nuevo_error":
        razones.append("⚠️ Error nuevo que necesita atención inmediata")
    
    SI error.veces_fallada >= 3:
        razones.append(f"🔴 Fallada {error.veces_fallada} veces - concepto difícil")
    SINO SI error.veces_fallada >= 2:
        razones.append(f"🟡 Fallada {error.veces_fallada} veces - necesita refuerzo")
    
    SI error.dias_sin_practica > 7:
        razones.append(f"📅 {error.dias_sin_practica} días sin practicar - riesgo de olvido")
    
    SI error.prioridad == "alta":
        razones.append("🎯 Alta prioridad")
    
    RETORNAR " | ".join(razones)


# ===== FUNCIÓN AUXILIAR: GENERAR RECOMENDACIÓN =====

función generar_recomendacion(error):
    """Sugiere estrategia de estudio."""
    
    SI error.veces_fallada >= 3:
        RETORNAR "Dedica tiempo extra a entender el concepto fundamental"
    SINO SI error.estado_refuerzo == "nuevo_error":
        RETORNAR "Estudia la teoría antes de practicar de nuevo"
    SINO SI error.dias_sin_practica > 14:
        RETORNAR "Revisa los apuntes antes de intentar resolver"
    SINO:
        RETORNAR "Practica con atención a los detalles"
```

---

## 📐 Ejemplo de Ordenamiento

### Banco de Entrada

```json
{
  "errores": [
    {
      "id": "A",
      "pregunta": "¿Qué es una derivada?",
      "estado_refuerzo": "nuevo_error",
      "veces_fallada": 1,
      "ultima_vez_practicada": "2025-11-20T10:00:00",
      "prioridad": "media"
    },
    {
      "id": "B",
      "pregunta": "Explica el diseño centrado en el usuario",
      "estado_refuerzo": "en_refuerzo",
      "veces_fallada": 3,
      "ultima_vez_practicada": "2025-11-15T14:00:00",
      "prioridad": "alta"
    },
    {
      "id": "C",
      "pregunta": "¿Qué es un algoritmo?",
      "estado_refuerzo": "en_refuerzo",
      "veces_fallada": 1,
      "ultima_vez_practicada": "2025-11-10T09:00:00",
      "prioridad": "baja"
    },
    {
      "id": "D",
      "pregunta": "Principios de UX",
      "estado_refuerzo": "nuevo_error",
      "veces_fallada": 1,
      "ultima_vez_practicada": "2025-11-22T08:00:00",
      "prioridad": "media"
    },
    {
      "id": "E",
      "pregunta": "Jerarquía visual",
      "estado_refuerzo": "resuelto",
      "veces_fallada": 1,
      "ultima_vez_practicada": "2025-11-21T16:00:00",
      "prioridad": "baja"
    }
  ]
}
```

**Fecha de hoy:** 2025-11-22  
**Max errores:** 4

### Paso 1: Filtrar Activos

```
Excluir: E (estado = "resuelto")
Activos: [A, B, C, D]
```

### Paso 2: Calcular Métricas

| ID | Estado | Veces Fallada | Días Sin Práctica | Prioridad | Puntuación |
|----|--------|---------------|-------------------|-----------|------------|
| A | nuevo_error | 1 | 2 | media | 100 + 10 + 4 + 15 = **129** |
| B | en_refuerzo | 3 | 7 | alta | 50 + 30 + 14 + 30 = **124** |
| C | en_refuerzo | 1 | 12 | baja | 50 + 10 + 24 + 5 = **89** |
| D | nuevo_error | 1 | 0 | media | 100 + 10 + 0 + 15 = **125** |

### Paso 3: Ordenar por Criterios

1. **Nuevos errores primero:** A, D (estado = "nuevo_error")
2. **Entre nuevos, ordenar por puntuación:** D (125) > A (129)... **¡ERROR!**

**Corrección:** Ordenamiento multi-nivel:

```
Nivel 1: estado == "nuevo_error"
  → A, D (ambos son nuevos)
  
  Dentro de nuevos, ordenar por:
    Nivel 2: veces_fallada >= 2
      → Ninguno cumple
    
    Nivel 3: dias_sin_practica
      → A (2 días) > D (0 días)
  
  Resultado parcial: [A, D]

Nivel 1: estado == "en_refuerzo"
  → B, C
  
  Dentro de en_refuerzo, ordenar por:
    Nivel 2: veces_fallada >= 2
      → B cumple (3 fallos)
    
    Nivel 3: dias_sin_practica
      → C (12 días) > B (7 días)... 
      → Pero B tiene veces_fallada >= 2, va primero
  
  Resultado parcial: [B, C]

Resultado final: [A, D, B, C]
```

### Paso 4: Limitar a 4 Errores

```
Seleccionados: [A, D, B, C]
```

### Paso 5: Enriquecer con Metadatos

```json
[
  {
    "id": "A",
    "pregunta": "¿Qué es una derivada?",
    "razon_seleccion": "⚠️ Error nuevo que necesita atención inmediata",
    "recomendacion_estudio": "Estudia la teoría antes de practicar de nuevo"
  },
  {
    "id": "D",
    "pregunta": "Principios de UX",
    "razon_seleccion": "⚠️ Error nuevo que necesita atención inmediata",
    "recomendacion_estudio": "Estudia la teoría antes de practicar de nuevo"
  },
  {
    "id": "B",
    "pregunta": "Explica el diseño centrado en el usuario",
    "razon_seleccion": "🔴 Fallada 3 veces - concepto difícil | 🎯 Alta prioridad",
    "recomendacion_estudio": "Dedica tiempo extra a entender el concepto fundamental"
  },
  {
    "id": "C",
    "pregunta": "¿Qué es un algoritmo?",
    "razon_seleccion": "📅 12 días sin practicar - riesgo de olvido",
    "recomendacion_estudio": "Revisa los apuntes antes de intentar resolver"
  }
]
```

---

## 🔄 Integración en el Flujo del Sistema

### Momento de Invocación: Al Iniciar Sesión de Estudio

```
Usuario → Click en "Iniciar Sesión de Estudio"
         ↓
Frontend → POST /api/iniciar-sesion-estudio
         ↓
Backend → Priorizador.obtener_errores_para_hoy(max=10)
         ↓
Priorizador → Lee banco_errores_global.json
             → Aplica algoritmo de priorización
             → Retorna lista ordenada
         ↓
Backend → Genera examen de práctica personalizado
         ↓
Frontend → Muestra examen al usuario con feedback pedagógico
```

### Flujo Detallado

```
┌─────────────────────────────────────────────────────────────┐
│  1. USUARIO INICIA SESIÓN DE ESTUDIO                        │
│     • Click en botón "Practicar errores"                    │
│     • O botón "Sesión de refuerzo"                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  2. FRONTEND SOLICITA ERRORES PRIORIZADOS                   │
│     POST /api/sesion-estudio/iniciar                        │
│     {                                                        │
│       "max_errores": 10,                                    │
│       "incluir_resueltos": false                            │
│     }                                                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  3. BACKEND INVOCA PRIORIZADOR (Módulo 3)                   │
│     from priorizador_errores import Priorizador             │
│                                                              │
│     priorizador = Priorizador()                             │
│     errores_hoy = priorizador.obtener_errores_para_hoy(     │
│         max_errores=10                                      │
│     )                                                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  4. PRIORIZADOR EJECUTA ALGORITMO                           │
│     • Carga banco de errores                                │
│     • Filtra errores activos                                │
│     • Calcula días sin práctica                             │
│     • Aplica ordenamiento multi-criterio:                   │
│       1. Nuevos errores                                     │
│       2. Veces fallada >= 2                                 │
│       3. Días sin práctica                                  │
│       4. Prioridad                                          │
│     • Limita a N errores                                    │
│     • Enriquece con razones y recomendaciones               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  5. BACKEND GENERA EXAMEN DE PRÁCTICA                       │
│     • Toma las preguntas de los errores seleccionados       │
│     • Mezcla orden (opcional)                               │
│     • Genera estructura de examen                           │
│     • Guarda sesión temporal                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  6. FRONTEND MUESTRA SESIÓN DE ESTUDIO                      │
│     • Presenta preguntas una por una                        │
│     • Muestra razón de selección (pedagogía)                │
│     • Muestra recomendación de estudio                      │
│     • Permite responder y avanzar                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  7. USUARIO COMPLETA SESIÓN                                 │
│     • Responde cada pregunta                                │
│     • Recibe feedback inmediato                             │
│     • Ve progreso (X de N completadas)                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  8. SISTEMA ACTUALIZA BANCO (Módulo 2)                      │
│     • Guarda resultados de la sesión                        │
│     • Actualiza historial de cada error                     │
│     • Recalcula estados y prioridades                       │
│     • Usuario ve resumen de mejora                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Estructura de Salida

### Formato de Retorno

```python
{
  "fecha_sesion": "2025-11-22T14:30:00",
  "total_errores_seleccionados": 4,
  "errores": [
    {
      # ===== DATOS ORIGINALES DEL ERROR =====
      "id_error": "uuid-abc123",
      "hash_pregunta": "sha256...",
      
      "pregunta": {
        "texto": "¿Qué es una derivada?",
        "tipo": "corta",
        "opciones": [],
        "respuesta_correcta": null
      },
      
      "examen_origen": {
        "carpeta_ruta": "Matematicas/Calculo",
        "carpeta_nombre": "Calculo"
      },
      
      # ===== MÉTRICAS DE SEGUIMIENTO =====
      "veces_fallada": 1,
      "veces_practicada": 1,
      "ultima_vez_practicada": "2025-11-20T10:00:00",
      "estado_refuerzo": "nuevo_error",
      "prioridad": "media",
      
      # ===== METADATOS DE PRIORIZACIÓN (NUEVO) =====
      "dias_sin_practica": 2,
      "puntuacion_prioridad": 129,
      "razon_seleccion": "⚠️ Error nuevo que necesita atención inmediata",
      "recomendacion_estudio": "Estudia la teoría antes de practicar de nuevo",
      
      # ===== HISTORIAL (para contexto) =====
      "ultimo_intento": {
        "fecha": "2025-11-20T10:00:00",
        "puntos": 0.5,
        "estado": "fallo"
      }
    },
    # ... más errores ...
  ],
  
  "estadisticas_sesion": {
    "errores_nuevos_incluidos": 2,
    "errores_alta_frecuencia": 1,
    "errores_antiguos": 1,
    "promedio_dias_sin_practica": 5.25
  },
  
  "mensaje_motivacional": "Hoy practicarás 4 conceptos clave. ¡Vamos a dominarlos! 💪"
}
```

---

## 🎨 UX/UI Recomendado

### Pantalla: Inicio de Sesión de Estudio

```
╔══════════════════════════════════════════════════════════════╗
║            🎯 SESIÓN DE ESTUDIO PERSONALIZADA               ║
╚══════════════════════════════════════════════════════════════╝

📊 TU PROGRESO HOY
  • Errores activos: 30
  • Recomendado practicar: 10 errores
  • Tiempo estimado: ~25 minutos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎓 ¿QUÉ VAMOS A PRACTICAR?

1. ⚠️ 2 ERRORES NUEVOS
   → Conceptos recién descubiertos que necesitan atención

2. 🔴 1 ERROR DE ALTA FRECUENCIA
   → Fallado 3+ veces - concepto difícil que requiere refuerzo

3. 📅 1 ERROR ANTIGUO
   → 12 días sin practicar - riesgo de olvido

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ Iniciar Sesión (10 preguntas) ]  [ Personalizar ]  [ Cancelar ]

💡 Tip: Dedica 15-20 minutos diarios para mejores resultados
```

### Pantalla: Durante la Sesión

```
╔══════════════════════════════════════════════════════════════╗
║              PREGUNTA 1 DE 10                                ║
╚══════════════════════════════════════════════════════════════╝

⚠️ ESTE ES UN ERROR NUEVO
📝 Recomendación: Estudia la teoría antes de responder

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Qué es una derivada en cálculo?

[                                                               ]
[                                                               ]
[                 Área de respuesta libre                      ]
[                                                               ]
[                                                               ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Origen: Matematicas/Calculo
🔢 Primera vez fallada: hace 2 días

[ Anterior ]              [ Enviar Respuesta ]         [ Saltar ]

Progreso: ████████░░░░░░░░░░ 40%
```

---

## ⚙️ Casos Especiales

### Caso 1: Banco Vacío

```python
SI banco.errores está vacío O todos están resueltos:
    RETORNAR {
        "mensaje": "🎉 ¡No tienes errores pendientes!",
        "sugerencia": "Continúa con nuevos temas o repasa conceptos antiguos",
        "errores": []
    }
```

### Caso 2: Pocos Errores Activos

```python
SI len(errores_activos) < max_errores:
    # Retornar todos los disponibles
    RETORNAR errores_activos
    
    MENSAJE: "Practicarás todos tus errores pendientes (X preguntas)"
```

### Caso 3: Todos los Errores Son Antiguos

```python
SI todos los errores tienen dias_sin_practica > 30:
    # Priorizar por veces_fallada primero
    ORDENAR por: veces_fallada DESC, dias_sin_practica DESC
    
    MENSAJE: "Tiempo de refrescar conceptos antiguos 📚"
```

### Caso 4: Usuario Quiere Práctica Personalizada

```python
# Parámetros opcionales:
priorizador.obtener_errores_para_hoy(
    max_errores=20,           # Más preguntas
    solo_tipo="multiple",     # Solo opción múltiple
    solo_carpeta="Matematicas", # Solo de una carpeta
    incluir_resueltos=True    # Para repaso
)
```

---

## 📈 Métricas de Éxito

### Indicadores Clave

1. **Tasa de resolución post-sesión:** ¿Cuántos errores se resuelven después de practicar?
2. **Tiempo hasta resolución:** Días promedio desde primer fallo hasta resolución
3. **Adherencia:** ¿Cuántos usuarios completan las sesiones recomendadas?
4. **Mejora en puntuación:** Comparar puntos antes/después de sesiones

---

## 🚀 Ventajas del Algoritmo

✅ **Pedagógicamente sólido:** Basado en principios de aprendizaje espaciado  
✅ **Priorización clara:** Criterios objetivos y ordenados  
✅ **Adaptativo:** Se ajusta automáticamente según progreso  
✅ **Transparente:** Usuario ve por qué se seleccionó cada error  
✅ **Eficiente:** Optimiza tiempo de estudio  
✅ **Motivacional:** Mensajes contextuales y feedback positivo  

---

**Versión:** 3.0  
**Fecha:** 22 de noviembre de 2025  
**Estado:** ✅ Diseño Completo - Listo para Implementación

# 🎯 EJEMPLOS PRÁCTICOS - Módulo 1: Detector de Errores

Este documento muestra ejemplos visuales de cómo usar el detector de errores en diferentes escenarios.

---

## 📊 Ejemplo 1: Análisis Básico de un Examen

### Código:
```python
from detector_errores import DetectorErrores

# Crear instancia del detector
detector = DetectorErrores()

# Analizar un examen
analisis = detector.analizar_examen(
    "examenes/Platzi/examen_20251120_134728.json"
)

# Mostrar estadísticas
print(f"📋 Examen ID: {analisis['metadata']['id']}")
print(f"📁 Carpeta: {analisis['metadata']['carpeta']}")
print(f"📊 Puntuación: {analisis['metadata']['puntos_obtenidos']}/{analisis['metadata']['puntos_totales']}")
print(f"\n✅ Aciertos: {analisis['resumen_estados']['aciertos']}")
print(f"⚠️  Débiles: {analisis['resumen_estados']['respuestas_debiles']}")
print(f"❌ Fallos: {analisis['resumen_estados']['fallos']}")
```

### Salida:
```
📋 Examen ID: 20251120_134728
📁 Carpeta: Platzi
📊 Puntuación: 1.0/2

✅ Aciertos: 0
⚠️  Débiles: 0
❌ Fallos: 2
```

---

## 🔍 Ejemplo 2: Filtrar Preguntas por Estado

### Código:
```python
from detector_errores import DetectorErrores

detector = DetectorErrores()
analisis = detector.analizar_examen("examenes/Platzi/examen_20251120_134728.json")

# Obtener solo las preguntas falladas
fallos = detector.filtrar_por_estado(
    analisis["resultados_clasificados"], 
    "fallo"
)

# Mostrar cada fallo
print(f"🔴 Se encontraron {len(fallos)} preguntas falladas:\n")
for i, fallo in enumerate(fallos, 1):
    print(f"{i}. {fallo['pregunta']}")
    print(f"   Tipo: {fallo['tipo']}")
    print(f"   Tu respuesta: {fallo['respuesta_usuario']}")
    print(f"   Puntos: {fallo['puntos']}/{fallo['puntos_maximos']}\n")
```

### Salida:
```
🔴 Se encontraron 2 preguntas falladas:

1. ¿Qué categoría de principios jurídicos en el diseño se enfoca en cómo los usuarios interactúan con un producto?
   Tipo: flashcard
   Tu respuesta: Relación y jerarquía
   Puntos: 0.5/1

2. ¿Qué principio jurídico en el diseño sugiere que un diseño visualmente atractivo puede influir en la percepción de su usabilidad?
   Tipo: flashcard
   Tu respuesta: Forma e interacción
   Puntos: 0.5/1
```

---

## 📈 Ejemplo 3: Análisis de Múltiples Exámenes

### Código:
```python
from detector_errores import DetectorErrores
from pathlib import Path

detector = DetectorErrores()

# Obtener todos los exámenes de una carpeta
examenes_dir = Path("examenes/Platzi")
rutas_examenes = [str(f) for f in examenes_dir.glob("examen_*.json")]

# Analizar todos
resultados = detector.analizar_multiples_examenes(rutas_examenes)

# Calcular estadísticas globales
total_preguntas = sum(r["resumen_estados"]["total_preguntas"] for r in resultados)
total_aciertos = sum(r["resumen_estados"]["aciertos"] for r in resultados)
total_fallos = sum(r["resumen_estados"]["fallos"] for r in resultados)
total_debiles = sum(r["resumen_estados"]["respuestas_debiles"] for r in resultados)

print(f"📊 ANÁLISIS DE {len(resultados)} EXÁMENES\n")
print(f"Total preguntas analizadas: {total_preguntas}")
print(f"✅ Aciertos: {total_aciertos} ({total_aciertos/total_preguntas*100:.1f}%)")
print(f"⚠️  Débiles: {total_debiles} ({total_debiles/total_preguntas*100:.1f}%)")
print(f"❌ Fallos: {total_fallos} ({total_fallos/total_preguntas*100:.1f}%)")
```

### Salida:
```
📊 ANÁLISIS DE 3 EXÁMENES

Total preguntas analizadas: 15
✅ Aciertos: 5 (33.3%)
⚠️  Débiles: 3 (20.0%)
❌ Fallos: 7 (46.7%)
```

---

## 📄 Ejemplo 4: Generar Reporte Completo

### Código:
```python
from detector_errores import DetectorErrores

detector = DetectorErrores()
analisis = detector.analizar_examen("examenes/Platzi/examen_20251120_134728.json")

# Generar reporte formateado
reporte = detector.generar_reporte_texto(analisis)

# Mostrar en consola
print(reporte)

# Guardar en archivo
with open("reporte_examen.txt", "w", encoding="utf-8") as f:
    f.write(reporte)

print("\n💾 Reporte guardado en: reporte_examen.txt")
```

### Salida:
```
╔══════════════════════════════════════════════════════════════╗
║          REPORTE DE ANÁLISIS DE ERRORES - EXAMINATOR        ║
╚══════════════════════════════════════════════════════════════╝

📋 INFORMACIÓN DEL EXAMEN
  • ID: 20251120_134728
  • Carpeta: Platzi
  • Fecha: 2025-11-20T13:47:28
  • Puntuación: 1.0/2 (50.0%)

📊 RESUMEN DE ESTADOS
  • Total preguntas: 2
  • ✅ Aciertos: 0 (0.0%)
  • ⚠️  Respuestas débiles: 0 (0.0%)
  • ❌ Fallos: 2 (100.0%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 DETALLE POR PREGUNTA:

1. ❌ [FLASHCARD] FALLO
   Pregunta: ¿Qué categoría de principios jurídicos en el diseño se enfoca en ...
   Puntuación: 0.5/1
   Tu respuesta: Relación y jerarquía

2. ❌ [FLASHCARD] FALLO
   Pregunta: ¿Qué principio jurídico en el diseño sugiere que un diseño visual...
   Puntuación: 0.5/1
   Tu respuesta: Forma e interacción

💾 Reporte guardado en: reporte_examen.txt
```

---

## 🎯 Ejemplo 5: Identificar Preguntas Débiles para Repasar

### Código:
```python
from detector_errores import DetectorErrores

detector = DetectorErrores()
analisis = detector.analizar_examen("examenes/Matematicas/examen_calculo.json")

# Filtrar preguntas débiles
debiles = detector.filtrar_por_estado(
    analisis["resultados_clasificados"], 
    "respuesta_debil"
)

if debiles:
    print("⚠️  PREGUNTAS QUE NECESITAS REPASAR:\n")
    for pregunta in debiles:
        print(f"📌 {pregunta['pregunta']}")
        print(f"   Tipo: {pregunta['tipo']}")
        print(f"   Puntuación: {pregunta['puntos']}/{pregunta['puntos_maximos']}")
        print(f"   💡 {pregunta['feedback'][:100]}...\n")
else:
    print("✅ ¡No hay preguntas débiles! Buen trabajo.")
```

### Salida:
```
⚠️  PREGUNTAS QUE NECESITAS REPASAR:

📌 Explica el concepto de límite en cálculo
   Tipo: desarrollo
   Puntuación: 2.5/3
   💡 Tu respuesta es correcta pero falta profundizar en el concepto de épsilon-delta...

📌 ¿Qué es una derivada?
   Tipo: corta
   Puntuación: 2.2/3
   💡 Correcto, pero podrías mencionar también la interpretación geométrica como pendiente de...
```

---

## 💾 Ejemplo 6: Guardar Análisis para Uso Posterior

### Código:
```python
from detector_errores import DetectorErrores
import json
from datetime import datetime

detector = DetectorErrores()
analisis = detector.analizar_examen("examenes/Platzi/examen_20251120_134728.json")

# Agregar timestamp al análisis
analisis["fecha_analisis"] = datetime.now().isoformat()

# Guardar como JSON
output_file = f"analisis_{analisis['metadata']['id']}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(analisis, f, indent=2, ensure_ascii=False)

print(f"✅ Análisis guardado en: {output_file}")
print(f"📊 Total preguntas: {analisis['resumen_estados']['total_preguntas']}")
print(f"❌ Fallos detectados: {analisis['resumen_estados']['fallos']}")
```

### Salida:
```
✅ Análisis guardado en: analisis_20251120_134728.json
📊 Total preguntas: 2
❌ Fallos detectados: 2
```

### Archivo generado (`analisis_20251120_134728.json`):
```json
{
  "metadata": {
    "id": "20251120_134728",
    "carpeta": "Platzi",
    "puntos_obtenidos": 1.0,
    "puntos_totales": 2,
    "porcentaje": 50.0
  },
  "resultados_clasificados": [
    {
      "pregunta": "¿Qué categoría de principios...",
      "tipo": "flashcard",
      "estado_respuesta": "fallo"
    }
  ],
  "resumen_estados": {
    "total_preguntas": 2,
    "aciertos": 0,
    "fallos": 2,
    "respuestas_debiles": 0
  },
  "fecha_analisis": "2025-11-22T14:30:00"
}
```

---

## 🔬 Ejemplo 7: Análisis Detallado por Tipo de Pregunta

### Código:
```python
from detector_errores import DetectorErrores

detector = DetectorErrores()
analisis = detector.analizar_examen("examenes/Historia/examen_completo.json")

# Agrupar por tipo de pregunta
tipos = {}
for resultado in analisis["resultados_clasificados"]:
    tipo = resultado["tipo"]
    estado = resultado["estado_respuesta"]
    
    if tipo not in tipos:
        tipos[tipo] = {"aciertos": 0, "fallos": 0, "debiles": 0}
    
    tipos[tipo][estado + "s"] += 1

# Mostrar estadísticas por tipo
print("📊 ANÁLISIS POR TIPO DE PREGUNTA\n")
for tipo, stats in tipos.items():
    total = stats["aciertos"] + stats["fallos"] + stats["debiles"]
    print(f"📌 {tipo.upper()}:")
    print(f"   Total: {total}")
    print(f"   ✅ Aciertos: {stats['aciertos']} ({stats['aciertos']/total*100:.1f}%)")
    print(f"   ⚠️  Débiles: {stats['debiles']} ({stats['debiles']/total*100:.1f}%)")
    print(f"   ❌ Fallos: {stats['fallos']} ({stats['fallos']/total*100:.1f}%)\n")
```

### Salida:
```
📊 ANÁLISIS POR TIPO DE PREGUNTA

📌 MULTIPLE:
   Total: 5
   ✅ Aciertos: 3 (60.0%)
   ⚠️  Débiles: 0 (0.0%)
   ❌ Fallos: 2 (40.0%)

📌 VERDADERO_FALSO:
   Total: 3
   ✅ Aciertos: 2 (66.7%)
   ⚠️  Débiles: 1 (33.3%)
   ❌ Fallos: 0 (0.0%)

📌 DESARROLLO:
   Total: 2
   ✅ Aciertos: 0 (0.0%)
   ⚠️  Débiles: 1 (50.0%)
   ❌ Fallos: 1 (50.0%)

📌 CORTA:
   Total: 4
   ✅ Aciertos: 2 (50.0%)
   ⚠️  Débiles: 1 (25.0%)
   ❌ Fallos: 1 (25.0%)
```

---

## 🎓 Ejemplo 8: Identificar Áreas de Mejora

### Código:
```python
from detector_errores import DetectorErrores

detector = DetectorErrores()

# Analizar varios exámenes de diferentes temas
examenes = {
    "Matemáticas": "examenes/Matematicas/examen_final.json",
    "Historia": "examenes/Historia/examen_revolucion.json",
    "Programación": "examenes/Python/examen_poo.json"
}

print("📊 ÁREAS QUE NECESITAN MEJORA\n")

for tema, ruta in examenes.items():
    analisis = detector.analizar_examen(ruta)
    porcentaje_fallos = analisis["resumen_estados"]["porcentaje_fallos"]
    porcentaje_debiles = analisis["resumen_estados"]["porcentaje_debiles"]
    
    necesita_mejora = porcentaje_fallos + porcentaje_debiles
    
    if necesita_mejora > 50:
        emoji = "🔴"
        nivel = "CRÍTICO"
    elif necesita_mejora > 30:
        emoji = "🟡"
        nivel = "MODERADO"
    else:
        emoji = "🟢"
        nivel = "BIEN"
    
    print(f"{emoji} {tema}: {necesita_mejora:.1f}% necesita mejora - {nivel}")
    print(f"   ❌ Fallos: {porcentaje_fallos:.1f}%")
    print(f"   ⚠️  Débiles: {porcentaje_debiles:.1f}%\n")
```

### Salida:
```
📊 ÁREAS QUE NECESITAN MEJORA

🔴 Matemáticas: 65.0% necesita mejora - CRÍTICO
   ❌ Fallos: 45.0%
   ⚠️  Débiles: 20.0%

🟡 Historia: 35.0% necesita mejora - MODERADO
   ❌ Fallos: 20.0%
   ⚠️  Débiles: 15.0%

🟢 Programación: 25.0% necesita mejora - BIEN
   ❌ Fallos: 15.0%
   ⚠️  Débiles: 10.0%
```

---

## 🚀 Casos de Uso Avanzados

### 1. Script de Análisis Automático Nocturno
```python
from detector_errores import DetectorErrores
from pathlib import Path
import json
from datetime import datetime

def analisis_nocturno():
    """Analiza todos los exámenes y genera reporte diario."""
    detector = DetectorErrores()
    
    # Obtener todos los exámenes
    todos_examenes = list(Path("examenes").rglob("examen_*.json"))
    
    # Analizar
    resultados = detector.analizar_multiples_examenes([str(e) for e in todos_examenes])
    
    # Guardar reporte
    reporte = {
        "fecha": datetime.now().isoformat(),
        "total_examenes": len(resultados),
        "resumen_global": {
            "total_preguntas": sum(r["resumen_estados"]["total_preguntas"] for r in resultados),
            "total_fallos": sum(r["resumen_estados"]["fallos"] for r in resultados),
            "total_debiles": sum(r["resumen_estados"]["respuestas_debiles"] for r in resultados),
        }
    }
    
    with open(f"reporte_diario_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
        json.dump(reporte, f, indent=2)
    
    print("✅ Análisis nocturno completado")

# Ejecutar como tarea programada
analisis_nocturno()
```

### 2. Integración con Sistema de Notificaciones
```python
def notificar_si_muchos_fallos(umbral=70):
    """Envía alerta si hay demasiados fallos."""
    detector = DetectorErrores()
    analisis = detector.analizar_examen("examenes/reciente.json")
    
    porcentaje_fallos = analisis["resumen_estados"]["porcentaje_fallos"]
    
    if porcentaje_fallos > umbral:
        print(f"🚨 ALERTA: {porcentaje_fallos}% de fallos detectados!")
        print(f"   Examen: {analisis['metadata']['id']}")
        print(f"   Carpeta: {analisis['metadata']['carpeta']}")
        # Aquí integrarías con email, Telegram, etc.
```

---

## 📖 Notas Importantes

### ⚠️ El módulo NO modifica:
- Los archivos JSON originales de exámenes
- La estructura del sistema Examinator
- Ningún dato existente

### ✅ El módulo SÍ genera:
- Nuevos archivos de análisis (opcional)
- Reportes en texto
- Estadísticas agregadas

### 🔧 Personalización:
Puedes modificar los umbrales de clasificación editando las constantes en `detector_errores.py`:
```python
# Umbrales actuales
UMBRAL_ACIERTO = 0.9     # ≥ 90%
UMBRAL_DEBIL = 0.7       # 70-89%
# < 70% = fallo
```

---

**¿Siguiente paso?** Explorar el archivo `MODULO1_DISEÑO_TECNICO.md` para detalles técnicos completos.

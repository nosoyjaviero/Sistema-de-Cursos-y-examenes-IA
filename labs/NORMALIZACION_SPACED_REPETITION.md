# 🔄 Normalización Automática para Spaced Repetition

## 📋 Resumen

Se ha implementado un sistema de normalización automática que agrega campos de repetición espaciada a **TODAS** las preguntas del sistema, sin importar su origen o tipo.

---

## 🎯 Objetivo

Asegurar que toda pregunta en el sistema (prácticas, exámenes, flashcards) tenga los campos necesarios para funcionar con el algoritmo de repetición espaciada SM-2, eliminando la necesidad de migraciones manuales.

---

## 📦 Campos Agregados Automáticamente

Cada pregunta ahora incluye estos campos (si no los tiene ya):

```json
{
  "id": "flashcard_20241126101530123456_a1b2c3d4",
  "tipo": "flashcard",
  "pregunta": "¿Qué es...?",
  "respuesta": "Es...",
  "opciones": [],
  "puntos": 10,
  
  // 🔥 Campos de Spaced Repetition (agregados automáticamente)
  "ease_factor": 2.5,      // Factor de facilidad inicial
  "interval": 0,           // Intervalo en días (0 = nueva)
  "repetitions": 0,        // Número de repeticiones exitosas
  "last_review": null,     // Última fecha de revisión (ISO string)
  "next_review": null,     // Próxima revisión (ISO string)
  "state": "new"          // Estado: new, learning, review, relearning
}
```

---

## 🔧 Implementación

### Función Principal: `normalizar_pregunta_spaced_repetition()`

**Ubicación:** `api_server.py` línea ~48

```python
def normalizar_pregunta_spaced_repetition(pregunta_dict: dict) -> dict:
    """
    Normaliza una pregunta para incluir todos los campos necesarios para Spaced Repetition.
    
    Reglas:
    1. Si los campos ya existen, los respeta
    2. Si faltan, los agrega con valores por defecto
    3. Mantiene intacta la estructura original de la pregunta
    4. Genera ID único si no existe
    """
    # Generar ID único si no existe
    if 'id' not in pregunta_dict or not pregunta_dict['id']:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        tipo = pregunta_dict.get('tipo', pregunta_dict.get('type', 'question'))
        pregunta_dict['id'] = f"{tipo}_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    # Agregar campos de Spaced Repetition solo si no existen
    if 'ease_factor' not in pregunta_dict:
        pregunta_dict['ease_factor'] = 2.5
    
    if 'interval' not in pregunta_dict:
        pregunta_dict['interval'] = 0
    
    if 'repetitions' not in pregunta_dict:
        pregunta_dict['repetitions'] = 0
    
    if 'last_review' not in pregunta_dict:
        pregunta_dict['last_review'] = None
    
    if 'next_review' not in pregunta_dict:
        pregunta_dict['next_review'] = None
    
    if 'state' not in pregunta_dict:
        pregunta_dict['state'] = 'new'
    
    return pregunta_dict
```

---

## 📍 Puntos de Aplicación

La normalización se aplica **automáticamente** en:

### 1. ✅ Generación de Prácticas

**Endpoint:** `POST /api/generar_practica`
**Ubicación:** `api_server.py` línea ~2950

```python
# Después de generar y post-procesar las preguntas
print(f"🔄 Normalizando {len(preguntas_json)} preguntas para Spaced Repetition...")
preguntas_json = [normalizar_pregunta_spaced_repetition(p) for p in preguntas_json]
print(f"✅ Preguntas normalizadas con campos de repetición espaciada")
```

**Aplica a:**
- Preguntas generadas por IA (MCQ, flashcard, cloze, open, etc.)
- Todas las cantidades y tipos solicitados
- Prompt personalizado o contenido de documentos

---

### 2. ✅ Generación de Exámenes

**Endpoint:** `POST /api/generar-examen`
**Ubicación:** `api_server.py` línea ~2575

```python
# Después de convertir a JSON y mapear tipos
print(f"🔄 Normalizando {len(preguntas_json)} preguntas para Spaced Repetition...")
preguntas_json = [normalizar_pregunta_spaced_repetition(p) for p in preguntas_json]
print(f"✅ Preguntas normalizadas con campos de repetición espaciada")
```

**Aplica a:**
- Exámenes generados desde documentos
- Exámenes desde notas convertidas
- Exámenes desde casos de estudio

---

### 3. ✅ Guardar Práctica

**Endpoint:** `POST /datos/practicas/carpeta`
**Ubicación:** `api_server.py` línea ~4173

```python
# ANTES DE GUARDAR: Normalizar la práctica nueva
if 'preguntas' in practica and isinstance(practica['preguntas'], list):
    print(f"🔄 Normalizando {len(practica['preguntas'])} preguntas de la práctica...")
    practica['preguntas'] = [
        normalizar_pregunta_spaced_repetition(p) 
        for p in practica['preguntas']
    ]

# BONUS: Normalizar todas las prácticas existentes en el archivo
print(f"🔄 Normalizando preguntas de {len(practicas)} prácticas existentes...")
for practica_existente in practicas:
    if 'preguntas' in practica_existente and isinstance(practica_existente['preguntas'], list):
        practica_existente['preguntas'] = [
            normalizar_pregunta_spaced_repetition(p)
            for p in practica_existente['preguntas']
        ]
```

**Aplica a:**
- Práctica nueva que se está guardando
- **TODAS las prácticas existentes en el archivo** (migración automática)
- Prácticas importadas desde otras fuentes
- Prácticas creadas manualmente en el frontend

---

### 4. ✅ Cargar Prácticas

**Endpoint:** `GET /datos/practicas`
**Ubicación:** `api_server.py` línea ~4245

```python
# Después de cargar todas las prácticas
print(f"🔄 Normalizando preguntas en {len(todas_practicas)} prácticas...")
for practica in todas_practicas:
    if 'preguntas' in practica and isinstance(practica['preguntas'], list):
        practica['preguntas'] = [
            normalizar_pregunta_spaced_repetition(p)
            for p in practica['preguntas']
        ]
print(f"✅ Todas las prácticas normalizadas para Spaced Repetition")
```

**Aplica a:**
- Prácticas desde `practicas.json`
- Prácticas desde `resultados_practicas/*.json`
- Prácticas de todas las carpetas
- Migración en tiempo real al cargar

---

### 5. ✅ Guardar Examen

**Endpoint:** `POST /datos/examenes/carpeta`
**Ubicación:** `api_server.py` línea ~4038

```python
# ANTES DE GUARDAR: Normalizar el examen nuevo
if 'preguntas' in examen and isinstance(examen['preguntas'], list):
    print(f"🔄 Normalizando {len(examen['preguntas'])} preguntas del examen...")
    examen['preguntas'] = [
        normalizar_pregunta_spaced_repetition(p) 
        for p in examen['preguntas']
    ]

# BONUS: Normalizar todos los exámenes existentes
print(f"🔄 Normalizando preguntas de {len(examenes)} exámenes existentes...")
for examen_existente in examenes:
    if 'preguntas' in examen_existente and isinstance(examen_existente['preguntas'], list):
        examen_existente['preguntas'] = [
            normalizar_pregunta_spaced_repetition(p)
            for p in examen_existente['preguntas']
        ]
```

**Aplica a:**
- Examen nuevo que se está guardando
- **TODOS los exámenes existentes en el archivo** (migración automática)
- Exámenes completados
- Exámenes parciales

---

### 6. ✅ Cargar Exámenes

**Endpoint:** `GET /datos/examenes`
**Ubicación:** `api_server.py` línea ~4105

```python
# Después de cargar todos los exámenes
print(f"🔄 Normalizando preguntas en {len(todos_examenes)} exámenes...")
for examen in todos_examenes:
    if 'preguntas' in examen and isinstance(examen['preguntas'], list):
        examen['preguntas'] = [
            normalizar_pregunta_spaced_repetition(p)
            for p in examen['preguntas']
        ]
print(f"✅ Todos los exámenes normalizados para Spaced Repetition")
```

**Aplica a:**
- Exámenes desde `examenes.json`
- Exámenes desde `resultados_examenes/*.json`
- Exámenes de todas las carpetas
- Migración en tiempo real al cargar

---

## 🛡️ Reglas de Seguridad

### 1. **Respeto a Datos Existentes**
```python
if 'ease_factor' not in pregunta_dict:
    pregunta_dict['ease_factor'] = 2.5
```
**Solo agrega** si el campo no existe. **Nunca sobrescribe** valores existentes.

### 2. **Preservación de Estructura**
```python
return pregunta_dict  # Retorna el mismo objeto modificado
```
Mantiene intacta toda la estructura original:
- `pregunta`, `respuesta`, `opciones`
- `metadata` (con toda su complejidad)
- `puntos`, `tipo`, `explicacion`
- Cualquier otro campo personalizado

### 3. **Generación de ID Único**
```python
timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")  # Incluye microsegundos
tipo = pregunta_dict.get('tipo', pregunta_dict.get('type', 'question'))
pregunta_dict['id'] = f"{tipo}_{timestamp}_{uuid.uuid4().hex[:8]}"
```
**Formato:** `tipo_AAAAMMDDHHMMSSΜΜΜΜΜΜ_hash8`

**Ejemplo:** `flashcard_20241126101530123456_a1b2c3d4`

### 4. **Compatibilidad con Frontend**
- No modifica tipos de preguntas
- No cambia rutas ni títulos
- No altera IDs existentes
- No rompe `practicas.json` (sigue siendo array válido)

---

## 📊 Ejemplo de Transformación

### Antes (Pregunta Original)
```json
{
  "tipo": "mcq",
  "pregunta": "¿Qué es Python?",
  "opciones": ["Lenguaje", "Framework", "Base de datos", "IDE"],
  "respuestas_correctas": [0],
  "puntos": 10,
  "metadata": {
    "dificultad": "easy",
    "tags": ["python", "programación"]
  }
}
```

### Después (Pregunta Normalizada)
```json
{
  "id": "mcq_20241126101530123456_a1b2c3d4",
  "tipo": "mcq",
  "pregunta": "¿Qué es Python?",
  "opciones": ["Lenguaje", "Framework", "Base de datos", "IDE"],
  "respuestas_correctas": [0],
  "puntos": 10,
  "metadata": {
    "dificultad": "easy",
    "tags": ["python", "programación"]
  },
  
  "ease_factor": 2.5,
  "interval": 0,
  "repetitions": 0,
  "last_review": null,
  "next_review": null,
  "state": "new"
}
```

**Cambios:**
- ✅ Se agregó `id` único
- ✅ Se agregaron 6 campos de Spaced Repetition
- ✅ Se mantuvo toda la estructura original
- ✅ Se preservó `metadata` completo

---

## 🔄 Migración Automática

### Sin Intervención Manual

Cada vez que se **guarda** o **carga** un archivo:
1. Se normaliza el item nuevo
2. Se normalizan TODOS los items existentes en el archivo
3. Se guarda el archivo actualizado

**Resultado:** Migración progresiva sin scripts externos.

### Ejemplo de Log
```
🔄 Normalizando 5 preguntas de la práctica...
✅ Preguntas normalizadas para Spaced Repetition
🔄 Normalizando preguntas de 12 prácticas existentes...
✅ Todas las prácticas normalizadas
✅ Práctica guardada en: extracciones/Platzi/practicas.json
```

---

## 🎯 Casos Cubiertos

### ✅ Generación con IA
- Flashcards de respuesta corta
- Flashcards de selección múltiple
- MCQ (opción múltiple)
- Verdadero/Falso
- Cloze (relleno de huecos)
- Pregunta abierta
- Caso de estudio
- Reading comprehension
- Writing tasks

### ✅ Importación
- Desde documentos PDF
- Desde archivos TXT
- Desde notas convertidas
- Desde HTML

### ✅ Creación Manual
- Preguntas creadas en frontend
- Preguntas editadas
- Preguntas duplicadas

### ✅ Archivos Existentes
- `practicas.json` antiguos
- `examenes.json` antiguos
- `resultados_practicas/*.json`
- `resultados_examenes/*.json`

---

## 🚀 Beneficios

### 1. **Cero Migraciones Manuales**
No se requieren scripts de migración. Todo se normaliza automáticamente.

### 2. **Retrocompatibilidad Total**
Archivos antiguos siguen funcionando y se normalizan al cargar.

### 3. **Preparado para el Futuro**
Toda pregunta nueva ya tiene los campos necesarios para Spaced Repetition.

### 4. **Sin Riesgo de Pérdida de Datos**
Solo agrega campos, nunca modifica o elimina datos existentes.

### 5. **Consistencia Garantizada**
Todas las preguntas, sin importar su origen, tienen la misma estructura.

---

## 🧪 Testing

### Verificar Normalización

```bash
# Ver estructura de pregunta normalizada
python -c "
import json
with open('extracciones/Platzi/practicas.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    if data and data[0]['preguntas']:
        print('Campos en primera pregunta:')
        for key in sorted(data[0]['preguntas'][0].keys()):
            val = data[0]['preguntas'][0][key]
            print(f'  {key}: {val if not isinstance(val, (list, dict)) else type(val).__name__}')
"
```

**Output Esperado:**
```
Campos en primera pregunta:
  ease_factor: 2.5
  id: flashcard_20241126101530123456_a1b2c3d4
  interval: 0
  last_review: None
  next_review: None
  pregunta: ¿Qué es...?
  puntos: 10
  repetitions: 0
  respuesta: Es...
  state: new
  tipo: flashcard
```

---

## 📝 Logs de Debug

Los logs muestran claramente cuándo se normaliza:

```
🔄 Normalizando 5 preguntas para Spaced Repetition...
✅ Preguntas normalizadas con campos de repetición espaciada

🔄 Normalizando 3 preguntas de la práctica...
✅ Preguntas normalizadas para Spaced Repetition

🔄 Normalizando preguntas de 12 prácticas existentes...
✅ Todas las prácticas normalizadas

🔄 Normalizando preguntas en 8 exámenes...
✅ Todos los exámenes normalizados para Spaced Repetition
```

---

## 🎓 Conclusión

Con este sistema, **TODA pregunta** en Examinator está lista para trabajar con el algoritmo de repetición espaciada SM-2, sin importar:
- Cuándo fue creada
- Cómo fue creada
- Dónde está almacenada
- Qué tipo de pregunta es

**Resultado:** Sistema unificado y preparado para features avanzadas de aprendizaje espaciado.

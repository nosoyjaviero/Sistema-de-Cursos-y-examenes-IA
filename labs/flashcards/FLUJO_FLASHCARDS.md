# 🃏 SISTEMA DE FLASHCARDS - DOCUMENTACIÓN COMPLETA

## 📋 ÍNDICE

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Tipos de Flashcards](#tipos-de-flashcards)
4. [Algoritmo de Repetición Espaciada (SM-2)](#algoritmo-de-repetición-espaciada-sm-2)
5. [Ciclo de Vida de una Flashcard](#ciclo-de-vida-de-una-flashcard)
6. [Flujo de Creación](#flujo-de-creación)
7. [Flujo de Repaso](#flujo-de-repaso)
8. [Sistema de Almacenamiento](#sistema-de-almacenamiento)
9. [Integración con Sesiones de Estudio](#integración-con-sesiones-de-estudio)
10. [Estados y Filtros](#estados-y-filtros)
11. [Interfaz de Usuario](#interfaz-de-usuario)
12. [API Backend](#api-backend)
13. [Casos de Uso](#casos-de-uso)

---

## 🎯 INTRODUCCIÓN

El sistema de flashcards de Examinator es una implementación avanzada de **Repetición Espaciada** basada en el algoritmo **SM-2 (SuperMemo 2)**, diseñado para optimizar la retención de memoria a largo plazo.

### Características Principales

✅ **Algoritmo SM-2**: Programa automáticamente las revisiones según tu desempeño  
✅ **Límite de Revisiones Diarias**: Máximo 2 revisiones por flashcard por día (estilo Anki)  
✅ **Organización por Carpetas**: Estructura jerárquica para organizar contenido  
✅ **Múltiples Tipos**: Clásicas, Cloze, Código, y más (extensibles)  
✅ **Integración con Sesiones**: Fase dedicada de flashcards en sesiones Pomodoro  
✅ **Vista Completa y Edición**: CRUD completo de flashcards  
✅ **Conversión de Texto**: Genera flashcards automáticamente desde texto seleccionado  
✅ **Sincronización Backend**: Persistencia en archivos JSON por carpeta  

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Estructura de Carpetas

```
extracciones/
├── flashcards/              # Carpeta central (legacy)
│   └── flashcards.json
├── Platzi/                  # Ejemplo de carpeta de curso
│   ├── flashcards.json      # Flashcards de este curso
│   ├── notas.json
│   └── practicas.json
└── MisCursos/
    ├── JavaScript/
    │   └── flashcards.json
    └── Python/
        └── flashcards.json
```

### Modelo de Datos (Flashcard)

```javascript
{
  // Identificación
  "id": 1764102152719,                    // Timestamp único
  "tipo": "clasica",                       // clasica, cloze, codigo, etc.
  "carpeta": "Platzi",                     // Organización jerárquica
  
  // Contenido
  "titulo": "¿Qué es el Virtual DOM?",     // Pregunta/Frente
  "contenido": "Copia ligera del DOM...",  // Respuesta/Reverso
  "opciones": [],                          // Para MCQ (opcional)
  "respuestaCorrecta": "",                 // Para validación (opcional)
  "explicacion": "",                       // Contexto adicional
  "tema": "React",                         // Categoría
  "subtema": "Conceptos Core",             // Subcategoría
  
  // Fechas
  "fecha": "2025-11-25T20:22:32.719Z",          // Creación original
  "fecha_creacion": "2025-11-25T20:22:32.719Z", // Duplicado por compatibilidad
  "fechaRevision": "2025-11-26T01:09:29.749Z",  // Última revisión general
  "ultima_revision": "2025-11-26T01:09:29.749Z",// Para control diario
  "proximaRevision": "2025-12-12T01:09:29.749Z",// Cuándo repasar
  
  // Repetición Espaciada (SM-2)
  "intervalo": 16,              // Días hasta próxima revisión
  "repeticiones": 3,            // Veces recordada correctamente
  "facilidad": 2.8,             // Factor de facilidad (1.3-2.5+)
  "estadoRevision": "dominada", // nueva, en_progreso, dominada
  "revisionesHoy": 1,           // Contador diario (máx 2)
  
  // Recursos (opcional)
  "archivos": [],               // PDFs, docs relacionados
  "imagenes": [],               // URLs de imágenes
  "latex": false,               // Tiene LaTeX?
  
  // Metadatos por tipo (flashcards especializadas)
  "lenguaje": "javascript",     // Para código
  "dificultad": "medio",        // facil, medio, dificil
  "patronCodigo": "comprension" // Para flashcards de código
  
  // ... más campos especializados según tipo
}
```

---

## 🎴 TIPOS DE FLASHCARDS

### 1. **Clásica** (tipo: "clasica")

La más común. Pregunta en el frente, respuesta en el reverso.

```javascript
{
  tipo: "clasica",
  titulo: "¿Qué es un closure en JavaScript?",
  contenido: "Función que tiene acceso a variables de su scope externo..."
}
```

**Uso**: Conceptos, definiciones, hechos

---

### 2. **Cloze** (tipo: "cloze")

Texto con palabras ocultas para completar.

```javascript
{
  tipo: "cloze",
  titulo: "El patrón {{Observer}} permite que...",
  contenido: "Observer" // Palabra oculta
}
```

**Uso**: Completar información, vocabulario técnico

---

### 3. **Código** (tipo: "codigo")

Para snippets de código con sintaxis highlighting.

```javascript
{
  tipo: "codigo",
  lenguaje: "python",
  titulo: "¿Qué imprime este código?",
  contenido: "for i in range(3):\n  print(i)",
  respuestaCorrecta: "0\n1\n2"
}
```

**Uso**: Ejercicios de programación, debugging

---

### 4. **Imagen** (tipo: "imagen")

Flashcard centrada en contenido visual.

```javascript
{
  tipo: "imagen",
  titulo: "¿Qué patrón de diseño representa este diagrama?",
  imagenes: ["url/diagrama.png"],
  contenido: "Factory Pattern"
}
```

**Uso**: Diagramas, arquitecturas, arte, anatomía

---

## 🧠 ALGORITMO DE REPETICIÓN ESPACIADA (SM-2)

### Concepto

El algoritmo SM-2 (SuperMemo 2) calcula **cuándo** debes repasar una flashcard basándose en **qué tan bien** la recordaste.

### Fórmula de Intervalos

```javascript
// Primera vez: 1 día
if (repeticiones === 0) {
  intervalo = 1
}
// Segunda vez: 6 días
else if (repeticiones === 1) {
  intervalo = 6
}
// Tercera en adelante: intervalo * facilidad
else {
  intervalo = Math.round(intervaloAnterior * facilidad)
}
```

### Factor de Facilidad

Se ajusta según tu calificación (1-5):

| Calificación | Dificultad | Calidad | Ajuste Facilidad |
|-------------|------------|---------|------------------|
| 5           | Fácil      | Perfecto| +0.1             |
| 4           | Fácil      | Correcto| +0.0             |
| 3           | Medio      | Correcto| -0.14            |
| 2           | Difícil    | Incorrecto | -0.32         |
| 1           | Difícil    | Completo fallo | -0.54    |

```javascript
// Fórmula de ajuste
nuevaFacilidad = facilidad + (0.1 - (5 - calidad) * (0.08 + (5 - calidad) * 0.02))

// Límite mínimo
if (nuevaFacilidad < 1.3) nuevaFacilidad = 1.3
```

### Implementación en Código

**Archivo**: `App.jsx` (líneas 2610-2695)

```javascript
const calcularProximaRevision = (item, dificultad) => {
  // dificultad: 'facil', 'medio', 'dificil'
  
  let { intervalo, repeticiones, facilidad } = item;
  let nuevoIntervalo = intervalo || 1;
  let nuevasRepeticiones = repeticiones || 0;
  let nuevaFacilidad = facilidad || 2.5;
  
  // Convertir dificultad a calidad SM-2
  const calidad = dificultad === 'facil' ? 5 
                : dificultad === 'medio' ? 3 
                : 1;
  
  if (calidad >= 3) {
    // Respuesta correcta
    if (nuevasRepeticiones === 0) {
      nuevoIntervalo = 1; // 1 día
    } else if (nuevasRepeticiones === 1) {
      nuevoIntervalo = 6; // 6 días
    } else {
      nuevoIntervalo = Math.round(intervalo * nuevaFacilidad);
    }
    nuevasRepeticiones += 1;
  } else {
    // Respuesta incorrecta - reiniciar
    nuevasRepeticiones = 0;
    nuevoIntervalo = 1;
  }
  
  // Actualizar facilidad
  nuevaFacilidad = nuevaFacilidad + (0.1 - (5 - calidad) * (0.08 + (5 - calidad) * 0.02));
  if (nuevaFacilidad < 1.3) nuevaFacilidad = 1.3;
  
  // Calcular próxima fecha
  const proximaFecha = new Date();
  proximaFecha.setDate(proximaFecha.getDate() + nuevoIntervalo);
  
  return {
    ...item,
    ultima_revision: new Date().toISOString(),
    proximaRevision: proximaFecha.toISOString(),
    intervalo: nuevoIntervalo,
    repeticiones: nuevasRepeticiones,
    facilidad: nuevaFacilidad,
    estadoRevision: nuevasRepeticiones >= 3 ? 'dominada' 
                  : nuevasRepeticiones > 0 ? 'en_progreso' 
                  : 'nueva',
    revisionesHoy: (item.revisionesHoy || 0) + 1
  };
};
```

### Límite de Revisiones Diarias

**Regla Importante**: Máximo 2 revisiones por flashcard por día (sistema Anki)

```javascript
const filtrarItemsParaRepasar = (items) => {
  const ahora = new Date();
  const hoyInicio = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate(), 0, 0, 0);
  
  return items.filter(item => {
    // REGLA 1: Máximo 2 revisiones por día
    if ((item.revisionesHoy || 0) >= 2) {
      console.log('❌ EXCLUIDO: Ya revisado 2 veces hoy');
      return false;
    }
    
    // REGLA 2: ¿Ya vence para revisión?
    const proximaRevision = new Date(item.proximaRevision);
    if (proximaRevision > ahora) {
      console.log('❌ EXCLUIDO: Aún no vence (próxima revisión en el futuro)');
      return false;
    }
    
    // ✅ Incluir en repaso
    return true;
  });
};
```

---

## 🔄 CICLO DE VIDA DE UNA FLASHCARD

### Estados

```
┌─────────────┐
│   NUEVA     │ ← Primera vez creada
│ (repeticiones: 0) │
└──────┬──────┘
       │ Revisión 1: Correcta (calidad ≥ 3)
       ▼
┌─────────────┐
│ EN_PROGRESO │ ← Recordada al menos 1 vez
│ (repeticiones: 1-2) │
└──────┬──────┘
       │ Revisión 2-3: Correctas
       ▼
┌─────────────┐
│  DOMINADA   │ ← Recordada 3+ veces
│ (repeticiones: ≥ 3) │
└─────────────┘
       │
       │ Revisión: Incorrecta (calidad < 3)
       ▼
   (Vuelve a NUEVA)
```

### Transiciones

| De Estado | A Estado | Condición |
|-----------|----------|-----------|
| nueva | en_progreso | Primera revisión correcta |
| en_progreso | dominada | 3+ revisiones correctas |
| dominada | dominada | Revisión correcta (mantiene) |
| cualquiera | nueva | Revisión incorrecta (reset) |

---

## 📝 FLUJO DE CREACIÓN

### Método 1: Creación Manual

**Ubicación UI**: Pestaña "Flashcards" → Botón "Nueva Flashcard"

**Proceso**:

1. **Navegar a carpeta** destino
2. **Click** en botón "+ Nueva Flashcard"
3. **Completar formulario**:
   - Tipo (clasica, cloze, codigo)
   - Título/Pregunta
   - Contenido/Respuesta
   - Tema/Subtema (opcional)
   - Recursos (imágenes, archivos)
4. **Guardar**

**Código** (`App.jsx`, líneas 9990-10050):

```javascript
const crearNuevaFlashcard = () => {
  const carpetaActual = carpetaFlashcardActual?.ruta || rutaFlashcardsActual || '';
  
  setFormDataFlashcard({
    id: null,
    tipo: 'clasica',
    titulo: '',
    contenido: '',
    tema: '',
    carpeta: carpetaActual,
    // Campos de repetición espaciada inicializados
    proximaRevision: new Date().toISOString(),
    intervalo: 1,
    repeticiones: 0,
    facilidad: 2.5,
    estadoRevision: 'nueva'
  });
  
  setModalNuevaFlashcard(true);
};
```

**Backend** (`api_server.py`, líneas 3873-3932):

```python
@app.post("/datos/flashcards/carpeta")
async def guardar_flashcard_carpeta(request: Request):
    data = await request.json()
    flashcard = data.get("flashcard")
    carpeta_ruta = data.get("carpeta", "")
    
    # Determinar carpeta destino
    if carpeta_ruta:
        carpeta_destino = EXTRACCIONES_PATH / carpeta_ruta
    else:
        carpeta_destino = EXTRACCIONES_PATH / "flashcards"
    
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    archivo_flashcards = carpeta_destino / "flashcards.json"
    
    # Leer flashcards existentes
    flashcards_existentes = []
    if archivo_flashcards.exists():
        with open(archivo_flashcards, "r", encoding="utf-8") as f:
            flashcards_existentes = json.load(f)
    
    # Actualizar o agregar
    flashcard_id = flashcard.get("id")
    if flashcard_id:
        # Buscar y actualizar
        for i, f in enumerate(flashcards_existentes):
            if f.get("id") == flashcard_id:
                flashcards_existentes[i] = flashcard
                break
        else:
            flashcards_existentes.append(flashcard)
    else:
        flashcards_existentes.append(flashcard)
    
    # Guardar archivo
    with open(archivo_flashcards, "w", encoding="utf-8") as f:
        json.dump(flashcards_existentes, f, ensure_ascii=False, indent=2)
    
    return {"ok": True, "count": len(flashcards_existentes)}
```

---

### Método 2: Conversión desde Texto

**Ubicación UI**: Fase "Contenido" → Seleccionar texto → Menú contextual → "Crear Flashcards"

**Proceso**:

1. **Seleccionar** texto en el visor de documentos
2. **Click derecho** → "Convertir en Flashcards"
3. **Elegir modo**:
   - **Por línea**: Cada línea numerada (ej: "1. Texto") → 1 flashcard
   - **Por párrafo**: Cada párrafo → 1 flashcard
4. **Confirmar**

**Código** (`App.jsx`, líneas 3758-3830):

```javascript
const convertirTextoEnFlashcards = async () => {
  const flashcardsNuevas = [];
  
  if (modoConversionFlashcard === 'linea') {
    // Dividir por líneas numeradas
    const lineas = textoSeleccionadoFlashcard.split('\n').filter(l => l.trim());
    
    lineas.forEach((linea, index) => {
      const match = linea.match(/^\d+\.\s*(.+)$/);
      if (match) {
        flashcardsNuevas.push({
          id: `fc_${Date.now()}_${index}`,
          frente: `¿Cuál es el punto ${index + 1}?`,
          reverso: match[1].trim(),
          tema: editorNotaTitulo || 'General',
          tipo: 'clasica',
          carpeta: cursoActual?.nombre || 'General',
          fecha_creacion: new Date().toISOString(),
          // Campos SM-2 inicializados
          proximaRevision: new Date().toISOString(),
          intervalo: 1,
          repeticiones: 0,
          facilidad: 2.5,
          estadoRevision: 'nueva'
        });
      }
    });
  } else if (modoConversionFlashcard === 'parrafo') {
    // Dividir por párrafos
    const parrafos = textoSeleccionadoFlashcard.split('\n\n').filter(p => p.trim());
    
    parrafos.forEach((parrafo, index) => {
      flashcardsNuevas.push({
        id: `fc_${Date.now()}_${index}`,
        frente: `Explica el concepto ${index + 1}`,
        reverso: parrafo.trim(),
        // ... mismos campos que arriba
      });
    });
  }
  
  // Guardar todas las flashcards en su carpeta
  for (const flashcard of flashcardsNuevas) {
    await guardarFlashcardEnCarpeta(flashcard);
  }
  
  setMensaje({
    tipo: 'success',
    texto: `✅ ${flashcardsNuevas.length} flashcards creadas`
  });
};
```

---

### Método 3: Generación desde Prácticas (DESHABILITADO)

**Anteriormente**: Las preguntas tipo "flashcard" en prácticas se convertían automáticamente.

**Estado Actual**: ❌ **Deshabilitado** por solicitud del usuario.

**Código removido** (líneas 7475-7523):

```javascript
// 🃏 CONVERTIR PREGUNTAS TIPO FLASHCARD A FLASHCARDS REALES
// ❌ CÓDIGO ELIMINADO - El usuario no quiere conversión automática
```

---

## 🔁 FLUJO DE REPASO

### Durante una Sesión de Estudio

**Ubicación**: Menú "Calendario" → Configurar Sesión → Fase "Flashcards"

**Proceso**:

1. **Configurar sesión** con prioridad en flashcards
2. **Iniciar sesión** → Sistema carga flashcards pendientes
3. **Fase Flashcards activa**:
   - Muestra flashcard (frente)
   - Usuario reflexiona
   - Click "Mostrar respuesta" (reverso)
   - Evaluar dificultad: Fácil / Medio / Difícil
4. **Algoritmo SM-2 calcula** próxima revisión
5. **Guarda** cambios en archivo
6. **Siguiente flashcard** o avanzar a siguiente fase

**Código de Evaluación** (`App.jsx`, líneas 3074-3174):

```javascript
const evaluarFlashcard = async (dificultad) => {
  // dificultad: 'facil', 'medio', 'dificil'
  const flashcardActual = flashcardsSesion[indiceFlashcardActual];
  
  console.log('🔍 EVALUANDO FLASHCARD:', {
    id: flashcardActual?.id,
    titulo: flashcardActual?.titulo,
    dificultad
  });
  
  // 1. Cargar flashcard actual desde archivo
  const flashcardsGuardadas = await cargarTodasFlashcards();
  const flashcardActualizada = flashcardsGuardadas.find(f => f.id === flashcardActual.id);
  
  // 2. Calcular próxima revisión con SM-2
  const flashcardConNuevosDatos = calcularProximaRevision(flashcardActualizada, dificultad);
  
  console.log('📊 Nuevos datos calculados:', {
    proximaRevision: flashcardConNuevosDatos.proximaRevision,
    intervalo: flashcardConNuevosDatos.intervalo,
    repeticiones: flashcardConNuevosDatos.repeticiones,
    estadoRevision: flashcardConNuevosDatos.estadoRevision
  });
  
  // 3. Guardar en su carpeta
  await guardarFlashcardEnCarpeta(flashcardConNuevosDatos);
  
  // 4. Recargar flashcards para actualizar filtro
  const flashcardsReacargadas = await cargarTodasFlashcards();
  const flashcardsParaRepasar = filtrarItemsParaRepasar(flashcardsReacargadas);
  
  setFlashcardsSesion(flashcardsParaRepasar);
  setFlashcardsActuales(flashcardsReacargadas);
  
  // 5. Actualizar estadísticas
  setEstadisticasSesion(prev => ({
    ...prev,
    flashcardsRepasadas: prev.flashcardsRepasadas + 1
  }));
  
  // 6. Avanzar a siguiente
  if (indiceFlashcardActual >= flashcardsSesion.length - 1) {
    avanzarFase(); // Terminar fase
  } else {
    setIndiceFlashcardActual(prev => prev + 1);
  }
};
```

---

### Fuera de Sesión (Vista Independiente)

**Ubicación**: Menú "Flashcards" → Ver flashcard → Evaluar

**Proceso similar** pero sin contexto de sesión Pomodoro.

---

## 💾 SISTEMA DE ALMACENAMIENTO

### Arquitectura Distribuida

**Modelo**: Cada carpeta tiene su propio `flashcards.json`

**Ventajas**:
- ✅ Organización por tema/curso
- ✅ Backups selectivos
- ✅ Menor riesgo de corrupción total
- ✅ Portable (mover carpeta = mover flashcards)

**Ejemplo Estructura**:

```
extracciones/
├── Platzi/
│   └── flashcards.json ← 246 flashcards de Platzi
├── Udemy/
│   ├── JavaScript/
│   │   └── flashcards.json ← 50 flashcards de JS
│   └── Python/
│       └── flashcards.json ← 30 flashcards de Python
└── Personal/
    └── flashcards.json ← 10 flashcards personales
```

**Total**: 336 flashcards distribuidas en 4 archivos

---

### Carga Consolidada

El backend **agrega** todas las flashcards de todas las carpetas en una sola respuesta:

**Endpoint**: `GET /datos/flashcards`

**Código Backend** (`api_server.py`, líneas 3712-3738):

```python
@app.get("/datos/flashcards")
def get_flashcards():
    """Lee flashcards de TODAS las carpetas y las agrega"""
    todas_flashcards = []
    
    # 1. Leer flashcards.json central (legacy)
    archivo_central = EXTRACCIONES_PATH / "flashcards" / "flashcards.json"
    if archivo_central.exists():
        with open(archivo_central, "r", encoding="utf-8") as f:
            flashcards_central = json.load(f)
            todas_flashcards.extend(flashcards_central)
    
    # 2. Leer flashcards.json de cada carpeta recursivamente
    for archivo_flashcard in EXTRACCIONES_PATH.rglob("flashcards.json"):
        # Evitar duplicados del central
        if archivo_flashcard == archivo_central:
            continue
        
        try:
            with open(archivo_flashcard, "r", encoding="utf-8") as f:
                flashcards_carpeta = json.load(f)
                todas_flashcards.extend(flashcards_carpeta)
        except Exception as e:
            print(f"⚠️ Error leyendo {archivo_flashcard}: {e}")
    
    print(f"📚 Flashcards cargadas: {len(todas_flashcards)} total")
    return JSONResponse(content=todas_flashcards)
```

---

### Guardado Selectivo

Cada flashcard se guarda **solo** en el archivo de su carpeta:

**Endpoint**: `POST /datos/flashcards/carpeta`

```python
{
  "flashcard": { ... datos completos ... },
  "carpeta": "Platzi/JavaScript"
}
```

**Proceso**:
1. Determina ruta: `extracciones/Platzi/JavaScript/`
2. Lee `flashcards.json` existente (si existe)
3. Actualiza o agrega nueva flashcard
4. Guarda solo ese archivo

**No afecta** a flashcards de otras carpetas.

---

## 🎓 INTEGRACIÓN CON SESIONES DE ESTUDIO

### Fase de Flashcards

Las sesiones Pomodoro tienen una fase dedicada a flashcards:

**Configuración**:

```javascript
// Sesión con prioridad "flashcards"
{
  duracion: 45, // minutos
  prioridad: 'flashcards',
  fases: [
    { tipo: 'calentamiento', duracion: 5, emoji: '🔥' },
    { tipo: 'flashcards', duracion: 22.5, emoji: '🃏' }, // 50% del tiempo
    { tipo: 'contenido', duracion: 13.5, emoji: '📖' },
    { tipo: 'cierre', duracion: 4, emoji: '📝' }
  ]
}
```

**Distribución de Tiempo según Prioridad**:

| Prioridad | Flashcards % | Errores % | Contenido % |
|-----------|-------------|-----------|-------------|
| flashcards | 50% | 0-20% | 30% |
| errores | 30% | 50% | 20% |
| contenido | 25% | 25% | 50% |

---

### Carga de Flashcards para Sesión

**Código** (`App.jsx`, líneas 2087-2110):

```javascript
const cargarFlashcardsAsync = async () => {
  // 1. Cargar todas las flashcards
  const todasFlashcards = await cargarTodasFlashcards();
  
  // 2. Filtrar las que necesitan repaso (SM-2)
  const flashcardsParaRepasar = filtrarItemsParaRepasar(todasFlashcards);
  
  // 3. Si hay carpeta seleccionada, filtrar solo de esa carpeta
  const flashcardsFiltradas = rutaActual 
    ? flashcardsParaRepasar.filter(f => f.carpeta === rutaActual)
    : flashcardsParaRepasar;
  
  console.log('📚 Flashcards para repasar:', {
    total: todasFlashcards.length,
    paraRepasar: flashcardsParaRepasar.length,
    enCarpeta: flashcardsFiltradas.length,
    nuevas: flashcardsParaRepasar.filter(f => !f.fechaRevision).length,
    enProgreso: flashcardsParaRepasar.filter(f => f.estadoRevision === 'en_progreso').length
  });
  
  setFlashcardsSesion(flashcardsFiltradas);
  setIndiceFlashcardActual(0);
};
```

---

### Estadísticas de Sesión

Durante la sesión, se trackean:

```javascript
{
  flashcardsRepasadas: 12,      // Contador de evaluaciones
  tiempoFaseFlashcards: 1350,   // Segundos dedicados
  flashcardsDominadas: 3,       // Pasaron a "dominada" esta sesión
  flashcardsRevisadas: 12       // Total procesadas
}
```

Al finalizar, se guarda en `mi_sesion_estudio.json`:

```json
{
  "sesion_id": "session_1732584920000",
  "actividades": {
    "flashcards_repasadas": 12,
    "tiempo_flashcards_min": 22.5,
    "nuevas_dominadas": 3
  }
}
```

---

## 🎛️ ESTADOS Y FILTROS

### Estados de Revisión

| Estado | Descripción | Repeticiones | Color UI |
|--------|-------------|--------------|----------|
| `nueva` | Nunca repasada o falló última vez | 0 | 🔵 Azul |
| `en_progreso` | Recordada 1-2 veces | 1-2 | 🟡 Amarillo |
| `dominada` | Recordada 3+ veces consecutivas | ≥ 3 | 🟢 Verde |

---

### Filtros de Visualización

**En Pestaña Flashcards** (`filtroTipoFlashcard`):

```javascript
const filtros = [
  { id: 'todas', nombre: 'Todas' },
  { id: 'nuevas', nombre: 'Nuevas', condicion: f => f.estadoRevision === 'nueva' },
  { id: 'en_progreso', nombre: 'En Progreso', condicion: f => f.estadoRevision === 'en_progreso' },
  { id: 'dominadas', nombre: 'Dominadas', condicion: f => f.estadoRevision === 'dominada' },
  { id: 'pendientes', nombre: 'Pendientes Hoy', condicion: f => new Date(f.proximaRevision) <= new Date() },
  { id: 'clasica', nombre: 'Clásicas', condicion: f => f.tipo === 'clasica' },
  { id: 'cloze', nombre: 'Cloze', condicion: f => f.tipo === 'cloze' }
];
```

**Aplicación**:

```javascript
const flashcardsFiltradas = flashcardsActuales.filter(fc => {
  if (filtroTipoFlashcard === 'todas') return true;
  const filtro = filtros.find(f => f.id === filtroTipoFlashcard);
  return filtro.condicion(fc);
});
```

---

### Filtro de Repaso (SM-2)

**Función Principal** (`App.jsx`, líneas 2699-2790):

```javascript
const filtrarItemsParaRepasar = (items) => {
  const ahora = new Date();
  const hoyInicio = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate(), 0, 0, 0);
  
  return items.filter(item => {
    // REGLA 1: Máximo 2 revisiones por día
    if ((item.revisionesHoy || 0) >= 2) {
      console.log(`❌ EXCLUIDO (2 revisiones hoy): ${item.titulo}`);
      return false;
    }
    
    // REGLA 2: ¿Fecha de revisión ya pasó?
    const proximaRevision = new Date(item.proximaRevision);
    if (proximaRevision > ahora) {
      console.log(`❌ EXCLUIDO (vence ${proximaRevision.toLocaleDateString()}): ${item.titulo}`);
      return false;
    }
    
    // ✅ INCLUIR en repaso
    console.log(`✅ INCLUIR: ${item.titulo} (vence hoy)`);
    return true;
  });
};
```

**Resultado**: Solo muestra flashcards que:
- Vencen hoy o antes
- No han sido revisadas 2 veces hoy

---

## 🎨 INTERFAZ DE USUARIO

### Vista de Lista (Pestaña Flashcards)

```
┌─────────────────────────────────────────────┐
│  🃏 FLASHCARDS                         [+]  │
├─────────────────────────────────────────────┤
│  📁 Platzi/JavaScript        (12 flashcards)│
│    ┌────────────────────────────────┐       │
│    │ 🔵 ¿Qué es el Virtual DOM?    │ [👁️]  │
│    │ Próxima revisión: Hoy          │ [✏️]  │
│    │ Repeticiones: 0 | Intervalo: 1 │ [🗑️] │
│    └────────────────────────────────┘       │
│    ┌────────────────────────────────┐       │
│    │ 🟢 ¿Qué es JSX?                │ [👁️]  │
│    │ Próxima revisión: 15/12/2025   │ [✏️]  │
│    │ Repeticiones: 5 | Intervalo: 20│ [🗑️] │
│    └────────────────────────────────┘       │
├─────────────────────────────────────────────┤
│  Filtros: [Todas] [Nuevas] [Pendientes]    │
└─────────────────────────────────────────────┘
```

**Componentes**:
- Color del círculo = Estado
- Botón 👁️ = Ver completa (modal)
- Botón ✏️ = Editar
- Botón 🗑️ = Eliminar

---

### Vista de Repaso (Durante Sesión)

**Modo Frente**:

```
┌─────────────────────────────────────────────┐
│      FLASHCARD 3 de 12                      │
├─────────────────────────────────────────────┤
│                                             │
│           ¿Qué es un closure                │
│          en JavaScript?                     │
│                                             │
│                                             │
│                                             │
│         [Mostrar Respuesta]                 │
│                                             │
└─────────────────────────────────────────────┘
```

**Modo Reverso**:

```
┌─────────────────────────────────────────────┐
│      FLASHCARD 3 de 12                      │
├─────────────────────────────────────────────┤
│  Pregunta:                                  │
│  ¿Qué es un closure en JavaScript?          │
│                                             │
│  Respuesta:                                 │
│  Una función que tiene acceso a variables   │
│  de su scope externo, incluso después de    │
│  que la función externa haya terminado.     │
│                                             │
│  ¿Qué tan bien lo recordaste?               │
│   [😰 Difícil]  [😐 Medio]  [😄 Fácil]     │
└─────────────────────────────────────────────┘
```

**Interacción**:
1. Leer pregunta
2. Reflexionar sobre respuesta
3. Click "Mostrar Respuesta"
4. Evaluar dificultad
5. Sistema calcula próxima revisión
6. Avanza a siguiente

---

### Modal de Creación/Edición

```
┌─────────────────────────────────────────────┐
│  ✨ Nueva Flashcard                    [X]  │
├─────────────────────────────────────────────┤
│  Tipo: [Clásica ▼]                          │
│                                             │
│  Pregunta/Título:                           │
│  ┌───────────────────────────────────────┐ │
│  │ ¿Qué es el patrón Observer?          │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Respuesta/Contenido:                       │
│  ┌───────────────────────────────────────┐ │
│  │ Permite que un objeto notifique       │ │
│  │ automáticamente a sus dependientes... │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Tema: [Patrones de Diseño]                 │
│  Subtema: [Behavioral Patterns]             │
│                                             │
│  📎 Archivos: [Adjuntar...]                 │
│  🖼️ Imágenes: [Subir...]                   │
│                                             │
│        [Cancelar]  [Guardar]                │
└─────────────────────────────────────────────┘
```

---

### Vista Completa (Modal de Revisión)

Muestra **todos** los datos de la flashcard, incluyendo:
- Metadatos (fecha creación, carpeta)
- Estadísticas SM-2 (intervalo, repeticiones, facilidad)
- Historial de revisiones (si existe)
- Archivos adjuntos
- Imágenes

---

## 🔌 API BACKEND

### Endpoints Principales

#### 1. **GET /datos/flashcards**

Obtiene **todas** las flashcards de todas las carpetas.

**Request**:
```http
GET /datos/flashcards?_t=1732584920000
```

**Response**:
```json
[
  {
    "id": 1764102152719,
    "tipo": "clasica",
    "titulo": "¿Qué es React?",
    "contenido": "Librería de JavaScript...",
    "carpeta": "Platzi/React",
    "proximaRevision": "2025-11-27T10:00:00.000Z",
    "intervalo": 1,
    "repeticiones": 0,
    "facilidad": 2.5,
    "estadoRevision": "nueva"
  },
  // ... más flashcards
]
```

---

#### 2. **POST /datos/flashcards/carpeta**

Guarda una flashcard en su carpeta específica.

**Request**:
```http
POST /datos/flashcards/carpeta
Content-Type: application/json

{
  "flashcard": {
    "id": 1764102152719,
    "tipo": "clasica",
    "titulo": "¿Qué es React?",
    "contenido": "Librería de JavaScript...",
    "carpeta": "Platzi/React",
    "proximaRevision": "2025-11-27T10:00:00.000Z",
    "intervalo": 1,
    "repeticiones": 0,
    "facilidad": 2.5,
    "estadoRevision": "nueva"
  },
  "carpeta": "Platzi/React"
}
```

**Response**:
```json
{
  "ok": true,
  "count": 15,
  "archivo": "extracciones/Platzi/React/flashcards.json"
}
```

---

#### 3. **GET /datos/flashcards/carpeta/{carpeta_ruta}**

Obtiene flashcards de una carpeta específica.

**Request**:
```http
GET /datos/flashcards/carpeta/Platzi/React
```

**Response**:
```json
[
  { "id": 1, "titulo": "¿Qué es React?" },
  { "id": 2, "titulo": "¿Qué son los hooks?" }
]
```

---

#### 4. **DELETE /datos/flashcards/{flashcard_id}**

Elimina una flashcard.

**Request**:
```http
DELETE /datos/flashcards/1764102152719?carpeta=Platzi/React
```

**Response**:
```json
{
  "ok": true,
  "message": "Flashcard eliminada"
}
```

---

### Código Backend Completo

**Archivo**: `api_server.py` (líneas 3706-3952)

```python
# ============================================
# GESTIÓN DE DATOS PERSISTENTES (FLASHCARDS)
# ============================================

@app.get("/datos/flashcards")
def get_flashcards():
    """Lee flashcards desde archivos JSON de todas las carpetas"""
    try:
        todas_flashcards = []
        
        # Leer flashcards.json central (legacy)
        archivo_central = EXTRACCIONES_PATH / "flashcards" / "flashcards.json"
        if archivo_central.exists():
            with open(archivo_central, "r", encoding="utf-8") as f:
                flashcards_central = json.load(f)
                todas_flashcards.extend(flashcards_central)
        
        # Leer flashcards.json de cada carpeta recursivamente
        for archivo_flashcard in EXTRACCIONES_PATH.rglob("flashcards.json"):
            if archivo_flashcard == archivo_central:
                continue
            
            try:
                with open(archivo_flashcard, "r", encoding="utf-8") as f:
                    flashcards_carpeta = json.load(f)
                    todas_flashcards.extend(flashcards_carpeta)
            except Exception as e:
                print(f"⚠️ Error leyendo {archivo_flashcard}: {e}")
        
        print(f"📚 Flashcards cargadas: {len(todas_flashcards)} total")
        return JSONResponse(content=todas_flashcards)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/datos/flashcards/carpeta")
async def guardar_flashcard_carpeta(request: Request):
    """Guarda una flashcard en el archivo flashcards.json de su carpeta específica"""
    try:
        data = await request.json()
        flashcard = data.get("flashcard")
        carpeta_ruta = data.get("carpeta", "")
        
        if not flashcard:
            raise HTTPException(status_code=400, detail="Falta flashcard en los datos")
        
        # Determinar ruta del archivo
        if carpeta_ruta:
            carpeta_destino = EXTRACCIONES_PATH / carpeta_ruta
        else:
            carpeta_destino = EXTRACCIONES_PATH / "flashcards"
        
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        archivo_flashcards = carpeta_destino / "flashcards.json"
        
        # Leer flashcards existentes de esta carpeta
        flashcards_existentes = []
        if archivo_flashcards.exists():
            with open(archivo_flashcards, "r", encoding="utf-8") as f:
                flashcards_existentes = json.load(f)
        
        # Buscar si ya existe (por ID)
        flashcard_id = flashcard.get("id")
        if flashcard_id:
            # Actualizar existente
            encontrada = False
            for i, f in enumerate(flashcards_existentes):
                if f.get("id") == flashcard_id:
                    flashcards_existentes[i] = flashcard
                    encontrada = True
                    break
            if not encontrada:
                flashcards_existentes.append(flashcard)
        else:
            # Nueva flashcard
            flashcards_existentes.append(flashcard)
        
        # Guardar
        with open(archivo_flashcards, "w", encoding="utf-8") as f:
            json.dump(flashcards_existentes, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Flashcard guardada en: {archivo_flashcards}")
        print(f"   Total flashcards en carpeta: {len(flashcards_existentes)}")
        
        return JSONResponse(content={
            "ok": True,
            "count": len(flashcards_existentes),
            "archivo": str(archivo_flashcards)
        })
    except Exception as e:
        print(f"❌ Error guardando flashcard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/datos/flashcards/carpeta/{carpeta_ruta:path}")
def get_flashcards_carpeta(carpeta_ruta: str):
    """Obtiene flashcards de una carpeta específica"""
    try:
        if carpeta_ruta:
            archivo = EXTRACCIONES_PATH / carpeta_ruta / "flashcards.json"
        else:
            archivo = EXTRACCIONES_PATH / "flashcards" / "flashcards.json"
        
        if archivo.exists():
            with open(archivo, "r", encoding="utf-8") as f:
                flashcards = json.load(f)
            return JSONResponse(content=flashcards)
        return JSONResponse(content=[])
    except Exception as e:
        print(f"❌ Error leyendo flashcards de {carpeta_ruta}: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.delete("/datos/flashcards/{flashcard_id}")
def delete_flashcard(flashcard_id: str, carpeta: str = ""):
    """Elimina una flashcard de su archivo correspondiente"""
    try:
        # Determinar archivo
        if carpeta:
            archivo = EXTRACCIONES_PATH / carpeta / "flashcards.json"
        else:
            archivo = EXTRACCIONES_PATH / "flashcards" / "flashcards.json"
        
        if not archivo.exists():
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        # Leer flashcards
        with open(archivo, "r", encoding="utf-8") as f:
            flashcards = json.load(f)
        
        # Filtrar (eliminar la que coincide con ID)
        flashcards_filtradas = [f for f in flashcards if str(f.get("id")) != str(flashcard_id)]
        
        # Guardar
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(flashcards_filtradas, f, ensure_ascii=False, indent=2)
        
        print(f"🗑️ Flashcard {flashcard_id} eliminada de {archivo}")
        return JSONResponse(content={"ok": True})
    except Exception as e:
        print(f"❌ Error eliminando flashcard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 CASOS DE USO

### Caso 1: Estudiante Aprende React por Primera Vez

**Escenario**:
- Usuario toma curso de React
- Quiere memorizar conceptos clave

**Flujo**:

1. **Navega** a carpeta "Platzi/React"
2. **Lee documentación** sobre Hooks
3. **Selecciona** párrafos importantes
4. **Click derecho** → "Convertir en Flashcards" → Por párrafo
5. Sistema crea **5 flashcards** con preguntas sobre Hooks
6. **Configuran sesión** de 30 min con prioridad "flashcards"
7. **Repasan** las 5 flashcards
   - Nuevas → Repiten mañana (intervalo: 1 día)
   - Si aciertan → Repiten en 6 días (intervalo: 6 días)
8. **Siguen repasando** siguiendo el algoritmo SM-2
9. **Después de 3 semanas**, dominan los conceptos

**Resultado**:
- 5 flashcards en estado "dominada"
- Próxima revisión: en 30 días
- Retención a largo plazo garantizada

---

### Caso 2: Preparación para Entrevista Técnica

**Escenario**:
- Desarrollador se prepara para entrevista en 2 semanas
- Necesita refrescar estructuras de datos

**Flujo**:

1. **Crea carpeta** "Entrevistas/DataStructures"
2. **Crea manualmente** 50 flashcards:
   - "¿Complejidad de inserción en Array?"
   - "¿Diferencia entre Stack y Queue?"
   - "¿Cuándo usar HashMap vs TreeMap?"
3. **Configura sesiones diarias** de 45 min con prioridad "flashcards"
4. **Primera semana**:
   - Día 1: Repasan 50 flashcards (todas nuevas)
   - Día 2: Repasan 30 flashcards (algunas vencen, otras no)
   - Día 3-7: Repasan solo las que vencen cada día
5. **Segunda semana**:
   - Solo repasan las difíciles (algoritmo las programa más seguido)
   - Las fáciles ya tienen intervalos de 6-10 días
6. **Día de entrevista**:
   - 40 flashcards en estado "dominada"
   - 10 en "en_progreso"

**Resultado**:
- Confianza en 80% de los conceptos
- Identificación clara de debilidades

---

### Caso 3: Repaso a Largo Plazo de Idioma

**Escenario**:
- Usuario aprende japonés
- Usa flashcards para vocabulario

**Flujo**:

1. **Crea carpeta** "Idiomas/Japones/Vocabulario"
2. **Crea 1000 flashcards** con palabras japonesas
3. **Repasa 20 flashcards diarias** en sesiones cortas (10 min)
4. **Algoritmo SM-2 distribuye** las revisiones:
   - Palabras fáciles → Se ven cada 30-60 días
   - Palabras difíciles → Se ven cada 1-3 días
5. **Después de 6 meses**:
   - 800 flashcards dominadas
   - 150 en progreso
   - 50 aún difíciles

**Ventaja**: El sistema optimiza el tiempo de repaso, solo muestra lo que necesitas ver.

---

### Caso 4: Estudio de Medicina (Anatomía)

**Escenario**:
- Estudiante de medicina estudia huesos del cuerpo humano

**Flujo**:

1. **Crea carpeta** "Medicina/Anatomia/Huesos"
2. **Crea flashcards con imágenes**:
   - Frente: Imagen de hueso
   - Reverso: Nombre + función
3. **Repasa con sesiones de 60 min**
4. **Algoritmo ajusta** según dificultad:
   - Huesos comunes (fémur) → Rápido a "dominada"
   - Huesos raros (estribo) → Más revisiones

**Resultado**:
- Memorización efectiva de 206 huesos
- Sin olvidar con el tiempo (revisiones espaciadas)

---

## 🔧 MEJORAS FUTURAS

### En Desarrollo

- [ ] **Sincronización en la nube** (Google Drive, Dropbox)
- [ ] **Compartir mazos** entre usuarios
- [ ] **Estadísticas avanzadas** (gráficos de progreso)
- [ ] **Modo quiz** (MCQ generadas desde flashcards)
- [ ] **Tags automáticos** con IA
- [ ] **Flashcards colaborativas** (edición múltiple)
- [ ] **Exportar/Importar Anki** (formato .apkg)
- [ ] **Audio TTS** para escuchar flashcards
- [ ] **Gamificación** (rachas, logros, niveles)

---

## 📚 REFERENCIAS

- [Algoritmo SM-2 Original](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2)
- [Anki Manual](https://docs.ankiweb.net/)
- [Spaced Repetition Research](https://www.gwern.net/Spaced-repetition)
- [SuperMemo Forgetting Curve](https://supermemo.guru/wiki/Forgetting_curve)

---

## 💡 CONSEJOS DE USO

### Para Máxima Efectividad

✅ **Repasa todos los días** (aunque sean 5 min)  
✅ **Sé honesto** al evaluar dificultad  
✅ **Crea flashcards concisas** (1 concepto = 1 flashcard)  
✅ **Usa imágenes** cuando sea posible  
✅ **Organiza por temas** en carpetas  
✅ **No acumules** flashcards sin repasar  
✅ **Confía en el algoritmo** (no fuerces revisiones)  

❌ **No crees flashcards muy largas**  
❌ **No marques todo como "fácil"**  
❌ **No ignores las difíciles**  
❌ **No estudies solo la noche antes del examen**  

---

## 🎓 CONCLUSIÓN

El sistema de flashcards de Examinator es una herramienta poderosa para:
- **Estudiantes** que preparan exámenes
- **Profesionales** que aprenden nuevas tecnologías
- **Desarrolladores** que memorizan APIs
- **Cualquier persona** que quiera retener información a largo plazo

**El secreto**: Repetición espaciada + Consistencia = Memoria a largo plazo 🧠✨

---

**Autor**: Sistema Examinator  
**Versión**: 1.0  
**Última actualización**: 26 de noviembre de 2025

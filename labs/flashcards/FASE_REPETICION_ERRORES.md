# 🎯 FASE DE REPETICIÓN DE ERRORES - DOCUMENTACIÓN COMPLETA

## 📋 ÍNDICE

1. [Introducción](#introducción)
2. [Concepto y Filosofía](#concepto-y-filosofía)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Extracción de Errores](#extracción-de-errores)
5. [Ciclo de Corrección](#ciclo-de-corrección)
6. [Evaluación con IA](#evaluación-con-ia)
7. [Actualización del Examen Original](#actualización-del-examen-original)
8. [Integración con Sesiones](#integración-con-sesiones)
9. [Estados y Flujos](#estados-y-flujos)
10. [Interfaz de Usuario](#interfaz-de-usuario)
11. [Casos de Uso](#casos-de-uso)

---

## 🎯 INTRODUCCIÓN

La **Fase de Repetición de Errores** es un componente central del sistema de aprendizaje de Examinator que se basa en el principio pedagógico de **aprender de los errores**.

### Propósito

Permitir a los estudiantes **revisar y corregir** las preguntas que respondieron incorrectamente en exámenes o prácticas anteriores, con el objetivo de:
- ✅ Reforzar conceptos débiles
- ✅ Identificar patrones de error
- ✅ Mejorar la retención a largo plazo
- ✅ Aumentar la calificación de exámenes pasados

---

## 💡 CONCEPTO Y FILOSOFÍA

### Principios Pedagógicos

1. **Aprendizaje Basado en Errores**
   - Los errores son oportunidades de aprendizaje
   - La repetición espaciada refuerza la memoria
   - La corrección activa mejora la comprensión

2. **Feedback Inmediato**
   - Evaluación instantánea con IA
   - Explicaciones detalladas
   - Sugerencias de mejora

3. **Persistencia de Progreso**
   - Los errores corregidos actualizan el examen original
   - Se eleva la calificación del examen
   - El error desaparece de la lista de pendientes

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Componentes Principales

```
┌──────────────────────────────────────────────────────────┐
│                  FASE DE ERRORES                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. EXTRACCIÓN                                           │
│     ↓                                                    │
│     extraerErroresDeExamenes()                           │
│     - Lee exámenes completados                           │
│     - Filtra preguntas con < 60%                         │
│     - Excluye ya corregidos                              │
│                                                          │
│  2. PRESENTACIÓN                                         │
│     ↓                                                    │
│     Wizard de Error Actual                               │
│     - Muestra pregunta                                   │
│     - Opciones (si es MCQ)                               │
│     - Campo texto (si es abierta)                        │
│                                                          │
│  3. EVALUACIÓN                                           │
│     ↓                                                    │
│     - MCQ: Verificación directa                          │
│     - Abierta: evaluarRespuestaTextual() con IA          │
│                                                          │
│  4. ACTUALIZACIÓN                                        │
│     ↓                                                    │
│     marcarErrorComprendido()                             │
│     - Actualiza examen/práctica original                 │
│     - Recalcula puntos totales                           │
│     - Elimina de lista de errores                        │
│                                                          │
│  5. PROGRESO                                             │
│     ↓                                                    │
│     siguienteError() → avanzarFase()                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Estados del Sistema

```javascript
// Estados principales de la fase
const [erroresActuales, setErroresActuales] = useState([])           // Lista de errores
const [indiceErrorActual, setIndiceErrorActual] = useState(0)        // Índice actual
const [respuestaErrorSeleccionada, setRespuestaErrorSeleccionada] = useState(null) // MCQ
const [respuestaTextual, setRespuestaTextual] = useState('')         // Abierta
const [errorYaRespondido, setErrorYaRespondido] = useState(false)    // Estado UI
const [feedbackIA, setFeedbackIA] = useState(null)                   // Evaluación IA
const [historialIntentos, setHistorialIntentos] = useState([])       // Intentos previos
const [evaluandoRespuesta, setEvaluandoRespuesta] = useState(false)  // Loading
```

---

## 🔍 EXTRACCIÓN DE ERRORES

### Función Principal

**Ubicación**: `App.jsx` líneas 2121-2172

```javascript
const extraerErroresDeExamenes = (examenes) => {
  const errores = [];
  
  console.log('🔍 Extrayendo errores de', examenes.length, 'exámenes/prácticas');
  
  examenes.forEach(examen => {
    // 🔥 BUSCAR EN AMBAS ESTRUCTURAS: resultados directos Y resultado.resultados
    let resultados = null;
    
    // Estructura 1: examen.resultados (array directo)
    if (examen.resultados && Array.isArray(examen.resultados)) {
      resultados = examen.resultados;
    } 
    // Estructura 2: examen.resultado.resultados (nested)
    else if (examen.resultado?.resultados && Array.isArray(examen.resultado.resultados)) {
      resultados = examen.resultado.resultados;
    }
    
    if (resultados) {
      resultados.forEach(resultado => {
        const porcentaje = (resultado.puntos / resultado.puntos_maximos) * 100;
        
        // Considerar error si obtuvo menos del 60% Y no ha sido corregido
        if (porcentaje < 60 && !resultado.corregido) {
          console.log('❌ Error encontrado:', {
            examen_id: examen.id,
            archivo: examen.archivo,
            pregunta: resultado.pregunta.substring(0, 50) + '...',
            porcentaje: porcentaje.toFixed(2) + '%',
            puntos: resultado.puntos,
            maximos: resultado.puntos_maximos,
            corregido: resultado.corregido
          });
          
          errores.push({
            ...resultado,                      // Todos los datos de la pregunta
            examen_id: examen.id,              // ID del examen padre
            archivo: examen.archivo,            // Archivo individual (si existe)
            carpeta_ruta: examen.carpeta_ruta || examen.carpeta,
            fecha: examen.fecha_completado,
            carpeta: examen.carpeta_nombre,
            es_practica: examen.es_practica,   // Distinguir examen/práctica
            porcentaje_obtenido: porcentaje
          });
        } else if (porcentaje < 60 && resultado.corregido) {
          console.log('✅ Error ya corregido (ignorado):', {
            examen_id: examen.id,
            pregunta: resultado.pregunta.substring(0, 50) + '...',
            corregido: resultado.corregido,
            fechaCorreccion: resultado.fechaCorreccion
          });
        }
      });
    }
  });
  
  console.log('📊 Total errores encontrados:', errores.length);
  
  // Ordenar por peor rendimiento primero
  return errores.sort((a, b) => a.porcentaje_obtenido - b.porcentaje_obtenido);
};
```

### Criterios de Extracción

| Condición | Descripción | Acción |
|-----------|-------------|--------|
| `porcentaje < 60` | Pregunta mal respondida | ✅ Incluir como error |
| `porcentaje >= 60` | Pregunta bien respondida | ❌ Ignorar |
| `corregido === true` | Ya fue corregida en sesión anterior | ❌ Ignorar |
| `corregido === false` o `undefined` | No corregida | ✅ Incluir |

### Estructura de un Error

```javascript
{
  // Datos de la pregunta original
  "pregunta": "¿Qué es el Virtual DOM?",
  "respuesta_usuario": "No sé",
  "respuesta_correcta": "Una representación...",
  "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "puntos": 2,
  "puntos_maximos": 10,
  "feedback": "Respuesta incorrecta...",
  "tipo": "mcq",
  
  // Metadatos del examen padre
  "examen_id": "exam_20241126101530123456_a1b2c3d4",
  "archivo": "resultados_examenes/examen_20241126.json",
  "carpeta_ruta": "Platzi/React",
  "carpeta": "React",
  "fecha": "2025-11-25T20:22:32.719Z",
  "es_practica": false,
  
  // Cálculos
  "porcentaje_obtenido": 20,  // 2/10 = 20%
  
  // Estado de corrección
  "corregido": false,          // Aún no corregido
  "fechaCorreccion": null      // Cuándo se corrigió
}
```

---

## 🔁 CICLO DE CORRECCIÓN

### 1. Presentación del Error

**Interfaz**:

```
┌─────────────────────────────────────────────────────────┐
│  🎯 ERROR 1 de 5                               [Salir]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ❌ Obtenido: 20% (2/10 puntos)                         │
│  📅 Examen: React Basics - 25/11/2025                   │
│  📁 Carpeta: Platzi/React                               │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                         │
│  ❓ Pregunta:                                           │
│  ¿Qué es el Virtual DOM en React?                      │
│                                                         │
│  📝 Opciones:                                           │
│  ⚪ A) Una base de datos virtual                        │
│  ⚪ B) Una representación en memoria del DOM real       │
│  ⚪ C) Un servidor virtual                              │
│  ⚪ D) Un componente de React                           │
│                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                         │
│  💭 Tu respuesta anterior: "A) Una base de datos..."   │
│  ✅ Respuesta correcta: "B) Una representación..."     │
│                                                         │
│  📚 Feedback:                                           │
│  El Virtual DOM es una copia ligera del DOM real que    │
│  React mantiene en memoria para optimizar las          │
│  actualizaciones...                                     │
│                                                         │
│            [Siguiente Error]  [Marcar Comprendido]      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### 2. Respuesta del Usuario

**Para MCQ (Opción Múltiple)**:

**Código** (`App.jsx`, líneas 2293-2305):

```javascript
const seleccionarRespuestaError = (opcion) => {
  setRespuestaErrorSeleccionada(opcion);
  setErrorYaRespondido(true);
  
  const errorActual = erroresActuales[indiceErrorActual];
  const esCorrecta = opcion.startsWith(errorActual.respuesta_correcta);
  
  if (esCorrecta) {
    console.log('✅ ¡Respuesta correcta! El error fue comprendido.');
  } else {
    console.log('❌ Respuesta incorrecta. Intenta nuevamente.');
  }
};
```

**Flujo**:
1. Usuario selecciona opción
2. Se compara con `respuesta_correcta`
3. Feedback inmediato (visual)
4. Habilita botón "Marcar Comprendido"

---

**Para Preguntas Abiertas**:

**Código** (`App.jsx`, líneas 2307-2398):

```javascript
const evaluarRespuestaTextual = async () => {
  if (!respuestaTextual.trim()) {
    alert('Por favor escribe una respuesta antes de enviar');
    return;
  }

  const errorActual = erroresActuales[indiceErrorActual];
  setEvaluandoRespuesta(true);

  try {
    // Obtener el modelo activo desde la configuración
    const modelo = configuracion?.modelo_ollama_activo || modeloSeleccionado;
    
    if (!modelo) {
      alert('⚠️ No hay un modelo seleccionado.');
      setEvaluandoRespuesta(false);
      return;
    }
    
    console.log('🤖 Evaluando con modelo:', modelo);
    console.log('   📝 Pregunta:', errorActual.pregunta);
    console.log('   💭 Respuesta usuario:', respuestaTextual);
    
    // Llamar al backend que usa el modelo configurado
    const response = await fetch(`${API_URL}/api/evaluar-respuesta-textual`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pregunta: errorActual.pregunta,
        respuesta_usuario: respuestaTextual,
        respuesta_correcta: errorActual.respuesta_correcta,
        intentos_previos: historialIntentos,
        modelo: modelo
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Error del servidor: ${response.status}`);
    }

    const data = await response.json();
    const evaluacion = data.evaluacion;
    
    console.log('✅ Evaluación recibida:', evaluacion);

    // Convertir puntuación 0-10 a 0-100
    const puntaje = Math.round((evaluacion.puntuacion / 10) * 100);
    
    // Construir feedback
    const feedbackTexto = `Puntaje: ${puntaje}/100 (${evaluacion.puntuacion}/10)

${evaluacion.feedback}

${evaluacion.sugerencias ? `💡 Sugerencias: ${evaluacion.sugerencias}` : ''}`;

    // Guardar en historial
    setHistorialIntentos(prev => [...prev, {
      respuesta: respuestaTextual,
      feedback: feedbackTexto,
      puntaje: puntaje,
      timestamp: new Date().toISOString()
    }]);

    setFeedbackIA({
      texto: feedbackTexto,
      puntaje: puntaje,
      esSuficiente: evaluacion.aprobada || puntaje >= 70
    });

    // Si la respuesta fue aprobada, marcar como respondido
    if (evaluacion.aprobada || puntaje >= 70) {
      setRespuestaErrorSeleccionada(respuestaTextual);
      setErrorYaRespondido(true);
    }

  } catch (error) {
    console.error('❌ Error al evaluar respuesta:', error);
    
    let mensajeError = 'Error al evaluar con el modelo.';
    
    if (error.message.includes('conectar') || error.message.includes('503')) {
      mensajeError = '❌ No se pudo conectar con Ollama. Verifica que esté corriendo.';
    } else if (error.message.includes('modelo')) {
      mensajeError = '❌ Error con el modelo. Verifica que esté correctamente configurado.';
    } else {
      mensajeError = `❌ ${error.message}`;
    }
    
    alert(mensajeError);
  } finally {
    setEvaluandoRespuesta(false);
  }
};
```

**Flujo**:
1. Usuario escribe respuesta textual
2. Click en "Evaluar con IA"
3. Backend llama a Ollama con prompt especializado
4. IA retorna:
   - `puntuacion`: 0-10
   - `feedback`: Explicación detallada
   - `sugerencias`: Cómo mejorar
   - `aprobada`: Boolean (≥ 7/10)
5. Frontend muestra feedback
6. Si aprobada, habilita "Marcar Comprendido"
7. Guarda en historial de intentos

---

### 3. Marcar Error Comprendido

**Código** (`App.jsx`, líneas 2407-2598):

```javascript
const marcarErrorComprendido = async () => {
  const errorActual = erroresActuales[indiceErrorActual];
  let esCorrecta = false;
  
  console.log('🔍 MARCANDO ERROR COMPRENDIDO:', {
    pregunta: errorActual.pregunta.substring(0, 50) + '...',
    respuestaSeleccionada: respuestaErrorSeleccionada,
    respuestaTextual: respuestaTextual,
    feedbackIA: feedbackIA
  });
  
  // Verificar si la respuesta es correcta
  if (respuestaErrorSeleccionada && respuestaErrorSeleccionada.startsWith(errorActual.respuesta_correcta)) {
    esCorrecta = true;
    console.log('✅ Respuesta de opción múltiple CORRECTA');
  } else if (feedbackIA && (feedbackIA.porcentaje_similitud >= 70 || feedbackIA.puntos >= 2)) {
    esCorrecta = true;
    console.log('✅ Respuesta de texto CORRECTA (similitud:', feedbackIA.porcentaje_similitud, '%)');
  }
  
  // Si el usuario respondió correctamente, actualizar el examen/práctica original
  if (esCorrecta) {
    console.log('✅ Error corregido. Actualizando examen/práctica original...');
    
    try {
      // 1️⃣ BUSCAR EXAMEN/PRÁCTICA ORIGINAL
      const esExamen = !errorActual.es_practica;
      const listaABuscar = esExamen ? await getDatos('examenes') : await getDatos('practicas');
      
      console.log(`📦 Buscando en ${listaABuscar.length} ${esExamen ? 'exámenes' : 'prácticas'}`);
      console.log('   🔍 Buscando ID:', errorActual.examen_id);
      
      // Buscar por ID
      const itemEncontrado = listaABuscar.find(item => item.id === errorActual.examen_id);
      
      if (!itemEncontrado) {
        throw new Error(`Item con ID ${errorActual.examen_id} no encontrado`);
      }
      
      console.log('✅ Item encontrado:', {
        id: itemEncontrado.id,
        archivo: itemEncontrado.archivo,
        carpeta_ruta: itemEncontrado.carpeta_ruta
      });
      
      // 2️⃣ OBTENER ESTRUCTURA DE RESULTADOS
      let resultados = null;
      let esEstructuraDirecta = false;
      
      if (itemEncontrado.resultado?.resultados) {
        resultados = itemEncontrado.resultado.resultados;
        esEstructuraDirecta = false;
      } else if (itemEncontrado.resultados && Array.isArray(itemEncontrado.resultados)) {
        resultados = itemEncontrado.resultados;
        esEstructuraDirecta = true;
      }
      
      if (!resultados) {
        throw new Error('No se encontraron resultados');
      }
      
      // 3️⃣ BUSCAR LA PREGUNTA ESPECÍFICA
      const preguntaIndex = resultados.findIndex(r => r.pregunta === errorActual.pregunta);
      
      if (preguntaIndex === -1) {
        throw new Error('Pregunta no encontrada');
      }
      
      console.log(`📝 Pregunta encontrada en índice ${preguntaIndex}`);
      
      // 4️⃣ ACTUALIZAR LA RESPUESTA A CORRECTA
      if (respuestaErrorSeleccionada) {
        resultados[preguntaIndex].respuesta_usuario = errorActual.respuesta_correcta;
      } else if (respuestaTextual) {
        resultados[preguntaIndex].respuesta_usuario = respuestaTextual;
      }
      resultados[preguntaIndex].puntos = resultados[preguntaIndex].puntos_maximos;
      resultados[preguntaIndex].corregido = true;
      resultados[preguntaIndex].fechaCorreccion = new Date().toISOString();
      
      console.log('   ✅ Pregunta marcada como corregida:', {
        corregido: resultados[preguntaIndex].corregido,
        fechaCorreccion: resultados[preguntaIndex].fechaCorreccion,
        puntos_antes: errorActual.puntos,
        puntos_despues: resultados[preguntaIndex].puntos
      });
      
      // 5️⃣ RECALCULAR PUNTOS TOTALES
      const nuevosPuntosObtenidos = resultados.reduce((sum, r) => sum + (r.puntos || 0), 0);
      const puntosTotales = esEstructuraDirecta ? itemEncontrado.puntos_totales : itemEncontrado.resultado.puntos_totales;
      const nuevoPorcentaje = (nuevosPuntosObtenidos / puntosTotales) * 100;
      
      if (esEstructuraDirecta) {
        itemEncontrado.puntos_obtenidos = nuevosPuntosObtenidos;
        itemEncontrado.porcentaje = nuevoPorcentaje;
      } else {
        itemEncontrado.resultado.puntos_obtenidos = nuevosPuntosObtenidos;
        itemEncontrado.resultado.porcentaje = nuevoPorcentaje;
      }
      
      // 6️⃣ GUARDAR EN ARCHIVO
      console.log('   💾 Guardando item actualizado...');
      if (esExamen) {
        await guardarExamenEnCarpeta(itemEncontrado);
      } else {
        await guardarPracticaEnCarpeta(itemEncontrado);
      }
      
      console.log('✅ Item actualizado - Nuevo porcentaje:', nuevoPorcentaje.toFixed(2) + '%');
      
      // 7️⃣ VERIFICAR QUE SE GUARDÓ
      console.log('🔄 Recargando desde backend...');
      const itemsActualizados = esExamen ? await getDatos('examenes') : await getDatos('practicas');
      
      // Refiltrar errores
      const todosItems = [...await getDatos('examenes'), ...await getDatos('practicas')];
      const erroresRefrescados = extraerErroresDeExamenes(todosItems);
      console.log('🔍 Errores después de recargar:', erroresRefrescados.length);
      
      // Verificar que la pregunta ya NO esté en la lista
      const preguntaAunEnLista = erroresRefrescados.find(e => 
        e.pregunta === errorActual.pregunta && e.examen_id === errorActual.examen_id
      );
      if (preguntaAunEnLista) {
        console.error('❌ ERROR: La pregunta sigue en la lista después de marcarla como corregida!');
      } else {
        console.log('✅ VERIFICADO: La pregunta ya NO está en la lista de errores');
      }
      
    } catch (error) {
      console.error('❌ Error actualizando item:', error);
    }
  } else {
    console.log('⚠️ El usuario no respondió correctamente, no se actualiza el examen.');
    
    // Si respondió mal, programar para mañana (Spaced Repetition)
    const errorConRevision = calcularProximaRevision(errorActual, 'dificil');
    console.log('📅 Error mal respondido, revisión para:', errorConRevision.proximaRevision);
  }
  
  // 8️⃣ ELIMINAR DE LISTA DE ERRORES ACTUALES
  if (esCorrecta) {
    const nuevosErrores = erroresActuales.filter((_, idx) => idx !== indiceErrorActual);
    setErroresActuales(nuevosErrores);
    
    // Si ya no quedan errores, avanzar fase
    if (nuevosErrores.length === 0) {
      setMensaje({
        tipo: 'success',
        texto: '🎉 ¡Felicidades! Has corregido todos los errores'
      });
      setRespuestaErrorSeleccionada(null);
      setErrorYaRespondido(false);
      setRespuestaTextual('');
      setHistorialIntentos([]);
      setFeedbackIA(null);
      avanzarFase();
      return;
    }
    
    // Ajustar índice si es necesario
    if (indiceErrorActual >= nuevosErrores.length) {
      setIndiceErrorActual(nuevosErrores.length - 1);
    }
  }
  
  // 9️⃣ RESETEAR ESTADOS
  setRespuestaErrorSeleccionada(null);
  setErrorYaRespondido(false);
  setRespuestaTextual('');
  setHistorialIntentos([]);
  setFeedbackIA(null);
  
  // Si no fue corregido, pasar al siguiente
  if (!esCorrecta) {
    siguienteError();
  }
};
```

**Proceso Detallado**:

1. **Validar Respuesta**: MCQ o IA aprobada
2. **Buscar Examen Original**: Por `examen_id`
3. **Obtener Estructura**: Detectar si es `resultados` o `resultado.resultados`
4. **Localizar Pregunta**: Buscar por texto de pregunta
5. **Actualizar Respuesta**: Cambiar a respuesta correcta
6. **Marcar Corregido**: `corregido = true`, `fechaCorreccion = now()`
7. **Recalcular Puntos**: Sumar todos los `resultado.puntos`
8. **Guardar Archivo**: Usando `guardarExamenEnCarpeta()` o `guardarPracticaEnCarpeta()`
9. **Verificar**: Recargar y confirmar que desapareció de errores
10. **Actualizar UI**: Eliminar de `erroresActuales`

---

## 🤖 EVALUACIÓN CON IA

### Backend Endpoint

**Archivo**: `api_server.py` (no mostrado en contexto, pero referenciado)

**Endpoint**: `POST /api/evaluar-respuesta-textual`

**Request**:
```json
{
  "pregunta": "¿Qué es el Virtual DOM?",
  "respuesta_usuario": "Es una copia del DOM que React usa para optimizar",
  "respuesta_correcta": "Una representación en memoria del DOM real...",
  "intentos_previos": [
    {
      "respuesta": "No sé",
      "puntaje": 0,
      "timestamp": "2025-11-25T20:00:00Z"
    }
  ],
  "modelo": "llama3.1:8b"
}
```

**Response**:
```json
{
  "evaluacion": {
    "puntuacion": 8.5,
    "feedback": "Buena respuesta. Has capturado la idea principal del Virtual DOM como una copia optimizada. Sin embargo, podrías ser más específico mencionando que se usa para minimizar manipulaciones directas del DOM real.",
    "sugerencias": "Agrega que React compara (diff) el Virtual DOM con el DOM real para hacer solo los cambios necesarios.",
    "aprobada": true
  }
}
```

### Prompt Utilizado (Inferido)

```
Eres un evaluador experto en educación. Evalúa la siguiente respuesta:

Pregunta: {pregunta}
Respuesta del estudiante: {respuesta_usuario}
Respuesta correcta esperada: {respuesta_correcta}

Intentos previos del estudiante:
{intentos_previos}

Proporciona:
1. Puntuación (0-10)
2. Feedback constructivo
3. Sugerencias de mejora
4. Indicar si la respuesta es aprobada (≥ 7/10)

Responde en formato JSON:
{
  "puntuacion": float,
  "feedback": string,
  "sugerencias": string,
  "aprobada": boolean
}
```

### Criterios de Evaluación

| Puntaje | Calificación | Descripción |
|---------|--------------|-------------|
| 0-3 | Insuficiente | Respuesta completamente incorrecta |
| 4-6 | Regular | Respuesta parcialmente correcta, faltan conceptos clave |
| 7-8 | Bueno | Respuesta correcta con pequeños detalles faltantes |
| 9-10 | Excelente | Respuesta completa y precisa |

**Umbral de Aprobación**: ≥ 7/10 (70%)

---

## 🔄 ACTUALIZACIÓN DEL EXAMEN ORIGINAL

### Estructuras Soportadas

El sistema maneja **dos estructuras** de almacenamiento de resultados:

#### Estructura 1: Directa (Práctica)
```json
{
  "id": "practice_123",
  "titulo": "Práctica de React",
  "carpeta": "Platzi/React",
  "fecha_completado": "2025-11-25T20:00:00Z",
  "puntos_obtenidos": 50,
  "puntos_totales": 100,
  "porcentaje": 50,
  "resultados": [
    {
      "pregunta": "¿Qué es React?",
      "respuesta_usuario": "Un framework",
      "respuesta_correcta": "Una librería de JavaScript",
      "puntos": 0,
      "puntos_maximos": 10,
      "corregido": false
    }
  ]
}
```

#### Estructura 2: Anidada (Examen)
```json
{
  "id": "exam_456",
  "titulo": "Examen Final React",
  "carpeta": "Platzi/React",
  "fecha_completado": "2025-11-25T20:00:00Z",
  "resultado": {
    "puntos_obtenidos": 50,
    "puntos_totales": 100,
    "porcentaje": 50,
    "resultados": [
      {
        "pregunta": "¿Qué es React?",
        "respuesta_usuario": "Un framework",
        "respuesta_correcta": "Una librería de JavaScript",
        "puntos": 0,
        "puntos_maximos": 10,
        "corregido": false
      }
    ]
  }
}
```

### Detección Automática

```javascript
// Detectar estructura
let resultados = null;
let esEstructuraDirecta = false;

if (itemEncontrado.resultado?.resultados) {
  resultados = itemEncontrado.resultado.resultados;  // Estructura 2
  esEstructuraDirecta = false;
} else if (itemEncontrado.resultados && Array.isArray(itemEncontrado.resultados)) {
  resultados = itemEncontrado.resultados;            // Estructura 1
  esEstructuraDirecta = true;
}
```

### Recalculo de Puntos

```javascript
// Sumar todos los puntos de todas las preguntas
const nuevosPuntosObtenidos = resultados.reduce((sum, r) => sum + (r.puntos || 0), 0);

// Obtener total según estructura
const puntosTotales = esEstructuraDirecta 
  ? itemEncontrado.puntos_totales 
  : itemEncontrado.resultado.puntos_totales;

// Calcular nuevo porcentaje
const nuevoPorcentaje = (nuevosPuntosObtenidos / puntosTotales) * 100;

// Actualizar según estructura
if (esEstructuraDirecta) {
  itemEncontrado.puntos_obtenidos = nuevosPuntosObtenidos;
  itemEncontrado.porcentaje = nuevoPorcentaje;
} else {
  itemEncontrado.resultado.puntos_obtenidos = nuevosPuntosObtenidos;
  itemEncontrado.resultado.porcentaje = nuevoPorcentaje;
}
```

### Guardado

```javascript
// Guardar usando función especializada
if (esExamen) {
  await guardarExamenEnCarpeta(itemEncontrado);
} else {
  await guardarPracticaEnCarpeta(itemEncontrado);
}
```

**Estas funciones**:
- Detectan si es archivo individual (`resultados_examenes/examen_*.json`) o carpeta (`examenes.json`)
- Actualizan el archivo correcto
- Preservan otros exámenes/prácticas en el mismo archivo

---

## 🔗 INTEGRACIÓN CON SESIONES

### Configuración de Sesión

La fase de errores se incluye en sesiones de estudio Pomodoro:

```javascript
// Distribución de tiempo según prioridad
if (prioridadSesion === 'errores') {
  // Sesión de 45 minutos con prioridad en errores
  fases = [
    { tipo: 'calentamiento', duracion: 216, emoji: '🔥' },  // 8% = 3.6 min
    { tipo: 'errores', duracion: 945, emoji: '🎯' },        // 35% = 15.75 min
    { tipo: 'flashcards', duracion: 675, emoji: '🃏' },     // 25% = 11.25 min
    { tipo: 'contenido', duracion: 675, emoji: '📚' },      // 25% = 11.25 min
    { tipo: 'cierre', duracion: 189, emoji: '✅' }          // 7% = 3.15 min
  ];
}
```

### Carga de Errores en Sesión

**Código** (`App.jsx`, líneas 2070-2085):

```javascript
const cargarDatosSesion = async () => {
  try {
    // Cargar exámenes completados
    const responseExamenes = await fetch(`${API_URL}/api/examenes/listar`);
    const dataExamenes = await responseExamenes.json();
    
    setDatosCalentamiento({
      ultimosExamenes: dataExamenes.completados?.slice(0, 5) || [],
      carpetaActual: rutaActual
    });
    
    // 🔥 Extraer errores de exámenes y prácticas
    const errores = extraerErroresDeExamenes(dataExamenes.completados || []);
    setErroresActuales(errores);
    setIndiceErrorActual(0);
    
    // ... más carga de datos
  } catch (error) {
    console.error('Error cargando datos de sesión:', error);
  }
};
```

### Estadísticas de Sesión

```javascript
const [estadisticasSesion, setEstadisticasSesion] = useState({
  erroresReforzados: 0,      // Contador de errores revisados
  flashcardsRepasadas: 0,
  practicasHechas: 0,
  notasTomadas: 0
});

// Al marcar error comprendido o pasar al siguiente
setEstadisticasSesion(prev => ({
  ...prev,
  erroresReforzados: prev.erroresReforzados + 1
}));
```

### Finalización de Fase

```javascript
const siguienteError = () => {
  if (indiceErrorActual < erroresActuales.length - 1) {
    // Hay más errores, continuar
    setIndiceErrorActual(indiceErrorActual + 1);
    setEstadisticasSesion(prev => ({
      ...prev,
      erroresReforzados: prev.erroresReforzados + 1
    }));
  } else {
    // No hay más errores, avanzar a siguiente fase
    avanzarFase();
  }
};
```

---

## 🎨 ESTADOS Y FLUJOS

### Diagrama de Estados

```
┌─────────────────────────────────────────────────────────┐
│                   FASE DE ERRORES                       │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │ Cargar Errores  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Mostrar Error   │◄───────────┐
              │ (indice actual) │            │
              └────────┬────────┘            │
                       │                     │
        ┌──────────────┴──────────────┐     │
        │                             │     │
        ▼                             ▼     │
┌───────────────┐           ┌────────────────┐
│ MCQ: Selec.   │           │ Abierta: Eval. │
│ Opción        │           │ con IA         │
└───────┬───────┘           └────────┬───────┘
        │                            │
        │  ┌─────────────────────────┘
        │  │
        ▼  ▼
┌─────────────────┐
│ ¿Correcta?      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ✅        ❌
    │         │
    ▼         ▼
┌─────────┐ ┌───────────┐
│ Marcar  │ │ Siguiente │
│ Compren-│ │ Error     │────┐
│ dido    │ └───────────┘    │
└────┬────┘                  │
     │                       │
     ▼                       │
┌─────────────┐              │
│ Actualizar  │              │
│ Examen      │              │
└─────┬───────┘              │
      │                      │
      ▼                      │
┌─────────────┐              │
│ Eliminar de │              │
│ Lista       │              │
└─────┬───────┘              │
      │                      │
      └──────────────────────┘
                │
                ▼
         ┌──────────────┐
         │ ¿Más errores?│
         └──────┬───────┘
                │
         ┌──────┴──────┐
         │             │
         SI            NO
         │             │
         └──────┐      │
                │      ▼
                │  ┌────────────┐
                │  │ Avanzar    │
                │  │ Fase       │
                │  └────────────┘
                │
                └──► (Loop)
```

### Estados de UI

| Estado | Variable | Valores | Uso |
|--------|----------|---------|-----|
| Error actual | `indiceErrorActual` | 0 - N-1 | Qué error se muestra |
| Respuesta MCQ | `respuestaErrorSeleccionada` | null, "A) ..." | Opción seleccionada |
| Respuesta abierta | `respuestaTextual` | string | Texto escrito |
| Ya respondido | `errorYaRespondido` | boolean | Habilitar botones |
| Feedback IA | `feedbackIA` | null, object | Mostrar evaluación |
| Evaluando | `evaluandoRespuesta` | boolean | Loading spinner |
| Historial | `historialIntentos` | array | Intentos previos |

---

## 🖼️ INTERFAZ DE USUARIO

### Vista Principal

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 REFUERZO DE ERRORES                            [Salir]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Progreso: 3 de 12 errores corregidos                    │
│  ⏱️ Tiempo restante: 12:45                                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ERROR 4 de 12                                      │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                     │   │
│  │  ❌ Rendimiento anterior: 20% (2/10 puntos)        │   │
│  │  📅 Examen: React Hooks - 25/11/2025               │   │
│  │  📁 Carpeta: Platzi/React/Avanzado                 │   │
│  │                                                     │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │   │
│  │                                                     │   │
│  │  ❓ Pregunta:                                       │   │
│  │  ¿Cuál es la diferencia entre useState y          │   │
│  │  useReducer en React?                              │   │
│  │                                                     │   │
│  │  📝 Tu respuesta anterior:                         │   │
│  │  "No hay diferencia"                               │   │
│  │                                                     │   │
│  │  ✅ Respuesta correcta:                            │   │
│  │  "useState es para estado simple, useReducer       │   │
│  │  para estado complejo con múltiples acciones"     │   │
│  │                                                     │   │
│  │  📚 Explicación:                                   │   │
│  │  useState es ideal para valores simples como      │   │
│  │  booleanos o strings. useReducer es mejor para    │   │
│  │  objetos complejos donde múltiples acciones...    │   │
│  │                                                     │   │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │   │
│  │                                                     │   │
│  │  💭 Escribe tu nueva respuesta:                    │   │
│  │  ┌───────────────────────────────────────────┐    │   │
│  │  │ useState maneja estado simple, mientras    │    │   │
│  │  │ useReducer es útil para estado complejo   │    │   │
│  │  │ con múltiples acciones y transiciones     │    │   │
│  │  └───────────────────────────────────────────┘    │   │
│  │                                                     │   │
│  │          [Evaluar con IA]  [Siguiente]             │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📊 Estadísticas de la sesión:                              │
│  • Errores revisados: 3                                     │
│  • Errores corregidos: 2                                    │
│  • Tasa de éxito: 66.7%                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Feedback de IA

```
┌─────────────────────────────────────────────────────────┐
│  🤖 EVALUACIÓN DE IA                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📊 Puntaje: 85/100 (8.5/10)                            │
│  ✅ Estado: APROBADA                                    │
│                                                         │
│  💬 Feedback:                                           │
│  Excelente respuesta. Has identificado correctamente    │
│  las diferencias clave entre useState y useReducer.     │
│  Tu explicación es clara y concisa.                     │
│                                                         │
│  💡 Sugerencias de mejora:                              │
│  Podrías mencionar que useReducer es preferible        │
│  cuando el próximo estado depende del anterior,        │
│  o cuando tienes lógica compleja de actualización.     │
│                                                         │
│  📚 Recursos recomendados:                              │
│  • React Docs: useState vs useReducer                   │
│  • Cuándo usar useReducer                               │
│                                                         │
│       [Marcar Comprendido]  [Intentar de Nuevo]         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Historial de Intentos

```
┌─────────────────────────────────────────────────────────┐
│  📜 HISTORIAL DE INTENTOS                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Intento 1 (20:05):                                     │
│  "No hay diferencia"                                    │
│  Puntaje: 0/100 - ❌ Incorrecto                         │
│                                                         │
│  Intento 2 (20:07):                                     │
│  "useState es más simple"                               │
│  Puntaje: 40/100 - ❌ Insuficiente                      │
│                                                         │
│  Intento 3 (20:10): ← Actual                            │
│  "useState maneja estado simple, mientras useReducer    │
│  es útil para estado complejo..."                       │
│  Puntaje: 85/100 - ✅ APROBADO                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 CASOS DE USO

### Caso 1: Estudiante Repasa Errores de Examen de React

**Escenario**:
- Estudiante completó examen de React con 65%
- Tiene 7 preguntas con menos de 60%
- Quiere mejorar su calificación

**Flujo**:

1. **Configura sesión** de 30 min con prioridad "errores"
2. **Fase de errores** (15 min asignados)
3. **Carga automática**: 7 errores detectados
4. **Error 1**: "¿Qué es JSX?" (obtuvo 10%)
   - Lee pregunta y respuesta correcta
   - Selecciona opción correcta
   - Click "Marcar Comprendido"
   - ✅ Examen actualizado: 65% → 67%
5. **Error 2**: "Explica el Virtual DOM" (obtuvo 20%)
   - Escribe respuesta textual
   - Click "Evaluar con IA"
   - IA retorna: 75/100 - Aprobado
   - ✅ Examen actualizado: 67% → 70%
6. **Continúa** con los 5 errores restantes
7. **Termina fase**: 7/7 errores corregidos
8. **Resultado final**: Examen actualizado a 88%

**Beneficios**:
- Aprendió de sus errores
- Mejoró calificación en 23 puntos
- Reforzó conceptos débiles

---

### Caso 2: Repaso de Errores Antiguos

**Escenario**:
- Estudiante tiene errores de hace 2 semanas
- Quiere verificar si ya los domina

**Flujo**:

1. **Inicia sesión** de 15 min (solo errores)
2. **Carga**: 15 errores de exámenes antiguos
3. **Repasa rápidamente** MCQs (ya los recuerda)
4. **Marca 10 como comprendidos** en 8 minutos
5. **5 errores difíciles** quedan pendientes
6. **Sesión termina**: 10/15 corregidos (66%)
7. **Los 5 restantes** quedan para próxima sesión

**Resultado**:
- Errores actualizados: 15 → 5
- Exámenes mejorados: 3 exámenes pasaron de 50% a 75%

---

### Caso 3: Preparación para Re-Examen

**Escenario**:
- Estudiante reprobó examen final (55%)
- Tiene derecho a re-examen en 3 días
- Quiere corregir todos sus errores

**Flujo**:

**Día 1**:
1. Sesión de 60 min con prioridad "errores"
2. 20 errores detectados del examen
3. Corrige 12 errores en la sesión
4. Examen actualizado: 55% → 72%

**Día 2**:
1. Sesión de 45 min
2. 8 errores restantes
3. Corrige 6 errores
4. Examen actualizado: 72% → 82%

**Día 3**:
1. Sesión de 30 min
2. 2 errores finales (los más difíciles)
3. Consulta recursos adicionales
4. Corrige ambos
5. Examen actualizado: 82% → 90%

**Re-Examen**:
- Estudiante domina todos los conceptos
- Aprueba con 92%
- Sin errores pendientes

---

### Caso 4: Error de Pregunta Abierta con Múltiples Intentos

**Escenario**:
- Pregunta: "Explica el patrón Observer"
- Primera respuesta: "Es un patrón de diseño" (20%)

**Flujo de Intentos**:

**Intento 1**:
```
Usuario: "Es un patrón de diseño"
IA: 20/100 - Muy vaga. Explica QUÉ hace el patrón.
```

**Intento 2**:
```
Usuario: "Permite que objetos se comuniquen"
IA: 45/100 - Mejor, pero falta detalle sobre CÓMO.
Sugerencia: Menciona los roles de Subject y Observer.
```

**Intento 3**:
```
Usuario: "El patrón Observer tiene un Subject que notifica 
a múltiples Observers cuando cambia su estado"
IA: 75/100 - ✅ APROBADO
Feedback: Excelente. Has capturado la idea principal.
```

**Resultado**:
- Error corregido después de 3 intentos
- Estudiante aprendió progresivamente
- Examen actualizado

---

## 🎓 MEJORES PRÁCTICAS

### Para Estudiantes

✅ **Repasa errores lo antes posible** después del examen  
✅ **Lee la explicación completa** antes de responder  
✅ **Intenta responder sin ver la respuesta correcta** primero  
✅ **Usa tus propias palabras** en preguntas abiertas  
✅ **Revisa recursos adicionales** si no entiendes  
✅ **No marques como comprendido** si aún tienes dudas  

❌ **No copies textualmente** la respuesta correcta  
❌ **No marques todo como comprendido** sin intentar  
❌ **No ignores el feedback de IA**  
❌ **No dejes errores acumulados** por semanas  

---

### Para el Sistema

**Configuración Recomendada**:

```javascript
// Umbral de error
const UMBRAL_ERROR = 60; // < 60% = error

// Máximo de intentos antes de sugerir ayuda
const MAX_INTENTOS = 3;

// Puntaje mínimo para aprobar pregunta abierta
const PUNTAJE_APROBADO = 70; // ≥ 70/100

// Tiempo sugerido por error (segundos)
const TIEMPO_POR_ERROR = 180; // 3 minutos
```

---

## 🚀 CARACTERÍSTICAS AVANZADAS

### Implementadas

✅ **Doble estructura de datos** (directo y anidado)  
✅ **Evaluación con IA** para preguntas abiertas  
✅ **Historial de intentos** con feedback acumulativo  
✅ **Actualización persistente** del examen original  
✅ **Verificación de guardado** (refetch y validación)  
✅ **Integración con Spaced Repetition** (errores mal respondidos)  
✅ **Soporte MCQ y abiertas**  
✅ **Estadísticas de sesión**  

---

### Futuras Mejoras

🔮 **Análisis de patrones de error** (¿siempre fallas en un tema?)  
🔮 **Recomendaciones personalizadas** ("Repasa capítulo 3")  
🔮 **Gamificación** (rachas de corrección, logros)  
🔮 **Comparación con otros** (anónima)  
🔮 **Exportar informe de errores** (PDF)  
🔮 **Video-explicaciones** para errores comunes  
🔮 **Chat con IA** para profundizar en el error  

---

## 📝 RESUMEN TÉCNICO

### Endpoints Utilizados

| Método | Endpoint | Propósito |
|--------|----------|-----------|
| GET | `/api/examenes/listar` | Obtener exámenes completados |
| GET | `/datos/examenes` | Cargar exámenes para actualizar |
| GET | `/datos/practicas` | Cargar prácticas para actualizar |
| POST | `/api/evaluar-respuesta-textual` | Evaluar con IA |
| POST | `/datos/examenes/carpeta` | Guardar examen actualizado |
| POST | `/datos/practicas/carpeta` | Guardar práctica actualizada |

---

### Funciones Clave

| Función | Archivo | Líneas | Propósito |
|---------|---------|--------|-----------|
| `extraerErroresDeExamenes()` | App.jsx | 2121-2172 | Extrae errores de exámenes |
| `seleccionarRespuestaError()` | App.jsx | 2293-2305 | Maneja selección MCQ |
| `evaluarRespuestaTextual()` | App.jsx | 2307-2398 | Evalúa con IA |
| `marcarErrorComprendido()` | App.jsx | 2407-2598 | Actualiza examen y elimina error |
| `siguienteError()` | App.jsx | 2282-2291 | Avanza al siguiente |
| `cargarDatosSesion()` | App.jsx | 2070-2119 | Carga datos de sesión |

---

## 🎯 CONCLUSIÓN

La **Fase de Repetición de Errores** es un componente fundamental del sistema de aprendizaje de Examinator que:

1. **Identifica automáticamente** preguntas mal respondidas
2. **Guía al estudiante** a corregirlas con feedback inteligente
3. **Actualiza persistentemente** los exámenes originales
4. **Mejora las calificaciones** retroactivamente
5. **Integra con Spaced Repetition** para retención a largo plazo

**Resultado**: Aprendizaje efectivo basado en la corrección activa de errores, con mejora medible de las calificaciones y comprensión profunda de los conceptos.

---

**Autor**: Sistema Examinator  
**Versión**: 1.0  
**Última actualización**: 26 de noviembre de 2025

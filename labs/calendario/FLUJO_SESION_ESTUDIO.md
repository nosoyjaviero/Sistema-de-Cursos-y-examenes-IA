# 🎯 DOCUMENTACIÓN COMPLETA - PESTAÑA "SESIÓN DE ESTUDIO"

## 📋 ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura General](#arquitectura-general)
3. [Ciclo de Vida de una Sesión](#ciclo-de-vida)
4. [Configuración de Sesión](#configuración)
5. [Sistema de Fases](#sistema-de-fases)
6. [Sistema de Descansos (Pomodoro)](#sistema-descansos)
7. [Persistencia de Sesión](#persistencia)
8. [Estados y Datos](#estados-y-datos)
9. [Flujo Completo](#flujo-completo)
10. [Integración con Otros Módulos](#integración)

---

## 🎬 RESUMEN EJECUTIVO

La **Pestaña "Sesión de Estudio"** es un sistema completo de **aprendizaje adaptativo guiado** que estructura el tiempo de estudio del usuario en **fases especializadas**, basado en técnicas científicas de aprendizaje y la **técnica Pomodoro**.

### Características Principales:

- ✅ **Sesiones estructuradas por fases** (Calentamiento, Errores, Flashcards, Contenido, Cierre)
- ✅ **Modo Pomodoro integrado** (descansos automáticos basados en neurociencia)
- ✅ **Adaptación de prioridades** (errores, flashcards, contenido nuevo)
- ✅ **Modo Libre** (sin límite de tiempo, exploración flexible)
- ✅ **Persistencia automática** (guarda progreso en backend y localStorage)
- ✅ **Restauración de sesión** (continúa donde lo dejaste)
- ✅ **Estadísticas en tiempo real** (errores reforzados, flashcards repasadas, etc.)
- ✅ **Reflexión personal** (al finalizar, el usuario reflexiona sobre su aprendizaje)

---

## 🏗️ ARQUITECTURA GENERAL

### Componentes Principales:

```
┌─────────────────────────────────────────────────────────────┐
│                    PESTAÑA "SESIÓN"                         │
├─────────────────────────────────────────────────────────────┤
│  1. CONFIGURACIÓN DE SESIÓN (Modal)                         │
│     • Tiempo de sesión (15/30/45/60 min o Modo Libre)      │
│     • Prioridad (errores, flashcards, contenido)           │
│     • Carpeta de trabajo                                    │
│                                                              │
│  2. SISTEMA DE FASES (5 fases secuenciales)                 │
│     • Calentamiento (explorar carpetas, contexto)           │
│     • Refuerzo de Errores (corregir conceptos débiles)      │
│     • Flashcards (repaso espaciado con Anki-style)          │
│     • Contenido Nuevo (notas, documentos, flashcards)       │
│     • Cierre (resumen, estadísticas, reflexión)             │
│                                                              │
│  3. SISTEMA DE DESCANSOS (Pomodoro científico)              │
│     • Descansos cortos (cada 25 min)                        │
│     • Descansos largos (cada 90 min)                        │
│     • Recomendaciones neurocientíficas                      │
│                                                              │
│  4. PERSISTENCIA Y ESTADÍSTICAS                             │
│     • Guardado automático cada 30s                          │
│     • Sincronización backend                                │
│     • Estadísticas acumuladas                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ CICLO DE VIDA DE UNA SESIÓN

### 1. **INICIO DE SESIÓN**

```javascript
// Usuario hace clic en "Sesión de Estudio" en la barra lateral
// → Se abre modal de configuración

const abrirConfiguracionSesion = () => {
  setModalConfigSesion(true);
};
```

**Modal de Configuración muestra:**
- ⏱️ Selector de tiempo (15, 30, 45, 60 minutos o Modo Libre)
- 🎯 Prioridad de sesión:
  - `errores`: Enfocarse en corregir errores de exámenes
  - `flashcards`: Repaso de memoria espaciada
  - `contenido`: Aprender material nuevo
- 📂 Carpeta de trabajo (opcional, se puede seleccionar en Calentamiento)

### 2. **CÁLCULO DE FASES**

```javascript
const calcularFasesSesion = (minutos, prioridad) => {
  const segundos = minutos * 60;
  const fases = [];
  
  if (minutos <= 15) {
    // Sesión corta: Calentamiento + 1 fase prioritaria + Cierre
    fases.push(
      { tipo: 'calentamiento', duracion: Math.floor(segundos * 0.15), emoji: '🔥' },
      { tipo: prioridad, duracion: Math.floor(segundos * 0.70), emoji: '🎯' },
      { tipo: 'cierre', duracion: Math.floor(segundos * 0.15), emoji: '✅' }
    );
  } else if (minutos <= 30) {
    // Sesión media: Calentamiento + 2 fases (prioritaria 50%, secundaria 30%) + Cierre
    // ...
  } else {
    // Sesión larga: Calentamiento + 3 fases balanceadas + Cierre
    // ...
  }
  
  return fases;
};
```

**Ejemplo de distribución (30 minutos, prioridad "errores"):**
```
📊 Distribución de tiempo:
├── Calentamiento: 3 min (10%)
├── Errores: 15 min (50%) ← PRIORIDAD
├── Flashcards: 9 min (30%)
└── Cierre: 3 min (10%)
```

### 3. **MODO LIBRE (Infinito)**

Si el usuario activa **Modo Libre**:
```javascript
if (modoLibreActivo) {
  fases = [
    { tipo: 'calentamiento', duracion: Infinity, emoji: '🔥' },
    { tipo: 'errores', duracion: Infinity, emoji: '🎯' },
    { tipo: 'flashcards', duracion: Infinity, emoji: '🃏' },
    { tipo: 'contenido', duracion: Infinity, emoji: '📚' },
    { tipo: 'cierre', duracion: Infinity, emoji: '✅' }
  ];
}
```
- ✅ Todas las fases disponibles sin tiempo límite
- ✅ Usuario avanza manualmente entre fases
- ✅ Descanso sugerido cada 90 min (límite de atención)

---

## 🎯 SISTEMA DE FASES

### **FASE 1: CALENTAMIENTO** 🔥

**Objetivo:** Preparar al usuario, seleccionar carpeta de trabajo, contextualizar la sesión.

#### Funcionalidades:

1. **Estadísticas de la semana** (tiempo total, flashcards, errores, prácticas)
2. **Selector de carpeta** (navegador de carpetas estilo explorador)
3. **Contexto de la carpeta seleccionada** (errores pendientes, flashcards, documentos)

```jsx
{faseActual === 'calentamiento' && (
  <div className="fase-calentamiento">
    {/* Bloque destacado: Hoy trabajaremos en */}
    <div className="calentamiento-highlight">
      <h2>🎯 HOY TRABAJAREMOS EN</h2>
      <h3>{rutaCalentamientoActual || 'Selecciona tu carpeta'}</h3>
      
      {/* Contexto de la carpeta */}
      <ul className="contexto-lista">
        {erroresActuales.length > 0 && (
          <li>• {erroresActuales.length} errores pendientes</li>
        )}
        {flashcardsSesion.length > 0 && (
          <li>• {flashcardsSesion.length} flashcards listas</li>
        )}
      </ul>
    </div>
    
    {/* Navegador de carpetas */}
    <div className="explorador-carpetas-calentamiento">
      {/* Breadcrumb */}
      <div className="breadcrumb-explorador">
        <button onClick={() => cargarCarpetasCalentamiento('')}>
          🏠 Inicio
        </button>
        {/* Ruta actual */}
      </div>
      
      {/* Lista de carpetas */}
      <div className="carpetas-grid">
        {carpetasCalentamiento.map((carpeta) => (
          <button onClick={() => seleccionarCarpeta(carpeta)}>
            📁 {carpeta.nombre}
          </button>
        ))}
      </div>
    </div>
    
    {/* Botón para continuar */}
    <button onClick={() => avanzarFase()}>
      ✅ Listo, Continuar →
    </button>
  </div>
)}
```

#### Flujo:
```
Usuario entra a Calentamiento
  ↓
Ve estadísticas de la semana
  ↓
Navega carpetas (Mis Cursos)
  ↓
Selecciona carpeta de trabajo
  ↓
Sistema carga errores + flashcards de esa carpeta
  ↓
Usuario hace clic en "Listo, Continuar"
  ↓
Avanza a la siguiente fase
```

---

### **FASE 2: REFUERZO DE ERRORES** 🎯

**Objetivo:** Corregir errores de exámenes/prácticas anteriores mediante revisión interactiva.

#### Datos cargados:
```javascript
const cargarDatosSesion = async () => {
  // Cargar errores desde el backend
  const errores = await getDatos('errores');
  
  // Filtrar errores de la carpeta seleccionada
  const erroresCarpeta = errores.filter(err => 
    err.carpeta === rutaCalentamientoActual
  );
  
  setErroresActuales(erroresCarpeta);
};
```

#### Componentes visuales:

1. **Header con progreso**
```jsx
<div className="errores-header">
  <h2>🎯 Corrigiendo Errores Clave</h2>
  <div className="errores-progreso-numerico">
    {indiceErrorActual + 1} / {erroresActuales.length}
  </div>
</div>

{/* Barra de progreso */}
<div className="errores-progress-bar">
  <div style={{width: `${(indiceErrorActual / total) * 100}%`}} />
</div>
```

2. **Tarjeta de pregunta**
```jsx
<div className="error-wizard-card">
  {/* Tags */}
  <div className="error-tags">
    <span>📚 {error.carpeta}</span>
    <span>📊 {error.porcentaje_obtenido}%</span>
  </div>
  
  {/* Pregunta */}
  <h3>{error.pregunta}</h3>
  
  {/* Opciones (si es MCQ) */}
  {error.opciones && (
    <div className="error-opciones">
      {error.opciones.map((opcion, idx) => (
        <div 
          className={esCorrecta(opcion) ? 'correcta' : 'incorrecta'}
          onClick={() => seleccionarRespuestaError(opcion)}
        >
          {opcion}
        </div>
      ))}
    </div>
  )}
  
  {/* Respuesta textual (si es pregunta abierta) */}
  {!error.opciones && (
    <textarea 
      placeholder="Escribe tu respuesta..."
      value={respuestaTextual}
      onChange={(e) => setRespuestaTextual(e.target.value)}
    />
  )}
  
  {/* Comparación (después de responder) */}
  {errorYaRespondido && (
    <div className="error-comparison">
      <div>Tu respuesta: {respuestaSeleccionada}</div>
      <div>Correcta: {error.respuesta_correcta}</div>
    </div>
  )}
  
  {/* Explicación */}
  <div className="error-explanation">
    <h4>💡 Explicación</h4>
    <p>{error.feedback}</p>
  </div>
</div>
```

3. **Acciones del usuario**
```jsx
<div className="error-actions">
  <button onClick={saltarError}>
    ⏭️ Saltar
  </button>
  
  <button onClick={marcarComprendido}>
    ✅ Siguiente
  </button>
  
  <button onClick={necesitoPracticar}>
    🔄 Necesito Practicar Más
  </button>
</div>
```

#### Evaluación con IA (preguntas abiertas):

Si la pregunta NO tiene opciones (es respuesta corta o caso de estudio):

```javascript
const evaluarRespuestaTextual = async () => {
  setEvaluandoRespuesta(true);
  
  const response = await fetch(`${API_URL}/api/evaluar_respuesta_error`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      pregunta: erroresActuales[indiceErrorActual].pregunta,
      respuesta_usuario: respuestaTextual,
      respuesta_correcta: erroresActuales[indiceErrorActual].respuesta_correcta,
      contexto: erroresActuales[indiceErrorActual].contexto
    })
  });
  
  const resultado = await response.json();
  
  setFeedbackIA({
    puntaje: resultado.puntaje, // 0-100
    texto: resultado.feedback,
    esSuficiente: resultado.puntaje >= 70
  });
  
  // Guardar en historial de intentos
  setHistorialIntentos([...historialIntentos, {
    respuesta: respuestaTextual,
    puntaje: resultado.puntaje,
    feedback: resultado.feedback
  }]);
  
  setEvaluandoRespuesta(false);
};
```

#### Actualización en backend:

Cuando el usuario responde correctamente:
```javascript
const marcarErrorComprendido = async () => {
  const errorActual = erroresActuales[indiceErrorActual];
  
  // Actualizar error en backend con nueva respuesta
  await fetch(`${API_URL}/api/actualizar_error`, {
    method: 'POST',
    body: JSON.stringify({
      error_id: errorActual.id,
      nueva_respuesta: respuestaErrorSeleccionada,
      comprendido: true,
      proxima_revision: new Date(Date.now() + 24*60*60*1000) // Mañana
    })
  });
  
  // Actualizar estadísticas
  setEstadisticasSesion(prev => ({
    ...prev,
    erroresReforzados: prev.erroresReforzados + 1
  }));
  
  // Avanzar al siguiente error
  if (indiceErrorActual < erroresActuales.length - 1) {
    setIndiceErrorActual(indiceErrorActual + 1);
  } else {
    avanzarFase(); // Ir a Flashcards
  }
};
```

---

### **FASE 3: FLASHCARDS** 🃏

**Objetivo:** Repasar conceptos usando repetición espaciada (Spaced Repetition) con interfaz tipo Anki.

#### Sistema de carga:

```javascript
const cargarDatosSesion = async () => {
  // Cargar todas las flashcards
  const flashcards = await cargarTodasFlashcards();
  
  // Filtrar por carpeta seleccionada
  const flashcardsCarpeta = flashcards.filter(fc =>
    fc.carpeta === rutaCalentamientoActual
  );
  
  // Filtrar por fecha de revisión (vencidas o próximas a vencer)
  const hoy = new Date();
  const flashcardsRevision = flashcardsCarpeta.filter(fc => {
    const proximaRevision = new Date(fc.proxima_revision || hoy);
    return proximaRevision <= hoy;
  });
  
  setFlashcardsSesion(flashcardsRevision);
};
```

#### Interfaz de Flashcard (estilo Anki):

```jsx
{faseActual === 'flashcards' && (
  <div className="fase-flashcards">
    {/* Header con progreso */}
    <div className="flashcards-header">
      <h2>🃏 Repaso de Memoria</h2>
      <div>{indiceFlashcardActual + 1} / {flashcardsSesion.length}</div>
    </div>
    
    {/* Botones de Acceso Rápido */}
    <div className="accesos-rapidos-fase">
      <button onClick={() => irAMisCursos()}>
        📚 Ver en Mis Cursos
      </button>
      <button onClick={() => irANotas()}>
        📝 Ver Notas
      </button>
      <button onClick={() => irAFlashcards()}>
        🎴 Ver Flashcards
      </button>
    </div>
    
    {/* Tarjeta volteadora */}
    <div 
      className={`flashcard-anki ${volteada ? 'flipped' : ''}`}
      onClick={() => setFlashcardsVolteadas({
        ...flashcardsVolteadas,
        [indiceFlashcardActual]: true
      })}
    >
      {/* Cara frontal */}
      <div className="flashcard-front">
        <h3>{flashcardActual.pregunta}</h3>
        {!volteada && <span>👆 Click para ver respuesta</span>}
      </div>
      
      {/* Cara trasera */}
      <div className="flashcard-back">
        <div>{flashcardActual.respuesta}</div>
        {flashcardActual.explicacion && (
          <p>💡 {flashcardActual.explicacion}</p>
        )}
      </div>
    </div>
    
    {/* Botones de evaluación (solo cuando está volteada) */}
    {volteada && (
      <div className="flashcard-evaluation">
        <p>¿Qué tan bien recordaste esto?</p>
        
        <button onClick={() => evaluarFlashcard('dificil')}>
          😰 Lo Olvidé
          <span>Revisar pronto</span>
        </button>
        
        <button onClick={() => evaluarFlashcard('medio')}>
          🤔 Me Costó
          <span>Intervalo medio</span>
        </button>
        
        <button onClick={() => evaluarFlashcard('facil')}>
          😎 Lo Recordé Fácil
          <span>Intervalo largo</span>
        </button>
      </div>
    )}
    
    {/* Atajos de teclado */}
    <div className="flashcards-shortcuts">
      <span><kbd>Espacio</kbd> Voltear</span>
      <span><kbd>1</kbd> Olvidé</span>
      <span><kbd>2</kbd> Me costó</span>
      <span><kbd>3</kbd> Fácil</span>
    </div>
  </div>
)}
```

#### Algoritmo de Spaced Repetition (SM-2 simplificado):

```javascript
const evaluarFlashcard = async (dificultad) => {
  const flashcard = flashcardsSesion[indiceFlashcardActual];
  
  let nuevoIntervalo;
  let nuevoEaseFactor = flashcard.ease_factor || 2.5;
  
  switch (dificultad) {
    case 'dificil':
      nuevoIntervalo = 1; // Mañana
      nuevoEaseFactor = Math.max(1.3, nuevoEaseFactor - 0.2);
      break;
    case 'medio':
      nuevoIntervalo = flashcard.interval ? flashcard.interval * 1.2 : 3;
      break;
    case 'facil':
      nuevoIntervalo = flashcard.interval 
        ? flashcard.interval * nuevoEaseFactor 
        : 7;
      nuevoEaseFactor = Math.min(2.5, nuevoEaseFactor + 0.1);
      break;
  }
  
  // Calcular próxima revisión
  const proximaRevision = new Date();
  proximaRevision.setDate(proximaRevision.getDate() + nuevoIntervalo);
  
  // Actualizar flashcard en backend
  await fetch(`${API_URL}/api/actualizar_flashcard`, {
    method: 'POST',
    body: JSON.stringify({
      flashcard_id: flashcard.id,
      ease_factor: nuevoEaseFactor,
      interval: nuevoIntervalo,
      proxima_revision: proximaRevision.toISOString(),
      ultima_revision: new Date().toISOString()
    })
  });
  
  // Actualizar estadísticas
  setEstadisticasSesion(prev => ({
    ...prev,
    flashcardsRepasadas: prev.flashcardsRepasadas + 1
  }));
  
  // Siguiente flashcard
  if (indiceFlashcardActual < flashcardsSesion.length - 1) {
    setIndiceFlashcardActual(indiceFlashcardActual + 1);
    setFlashcardsVolteadas({...flashcardsVolteadas, [indiceFlashcardActual + 1]: false});
  } else {
    avanzarFase(); // Ir a Contenido Nuevo
  }
};
```

---

### **FASE 4: CONTENIDO NUEVO** 📚

**Objetivo:** Crear notas, estudiar documentos nuevos, generar flashcards desde el contenido.

#### Sistema de Tabs:

```jsx
{faseActual === 'contenido' && (
  <div className="fase-contenido">
    {/* Tabs */}
    <div className="tabs-header-contenido">
      <button onClick={() => setTabContenidoActivo(0)}>
        📝 Notas
      </button>
      <button onClick={() => setTabContenidoActivo(1)}>
        🎴 Flashcards
      </button>
    </div>
    
    {/* TAB 1: NOTAS */}
    {tabContenidoActivo === 0 && (
      <div className="tab-notas-contenido">
        {/* Editor estilo Notion con vista previa */}
        <NotionStyleEditor 
          titulo={editorNotaTitulo}
          contenido={editorNotaContenido}
          tags={editorNotaTags}
        />
      </div>
    )}
    
    {/* TAB 2: FLASHCARDS */}
    {tabContenidoActivo === 1 && (
      <div className="tab-flashcards-contenido">
        {/* Formulario de creación de flashcard */}
        <FlashcardCreator 
          carpeta={carpetaFlashcardActual}
        />
      </div>
    )}
  </div>
)}
```

#### Editor de Notas (Notion-style):

**Layout:**
```
┌──────────────────────────────────────────────────┐
│ Sidebar Izq │ Editor │ Vista Previa              │
│─────────────│────────│──────────────────────────│
│ 📁 Destino  │ Título │ HTML Renderizado         │
│ Biologia/   │ ✏️ ...  │                          │
│ Unidad1     │        │                          │
│             │ Editor │                          │
│ 📄 Notas    │ Texto  │                          │
│ • Nota 1    │ MD     │                          │
│ • Nota 2    │        │                          │
│             │        │                          │
│ [+ Nueva]   │ [/cmd] │                          │
│             │        │                          │
│ Acciones:   │        │                          │
│ [Guardar]   │        │                          │
│ [Generar]   │        │                          │
└─────────────┴────────┴──────────────────────────┘
```

**Menú de comandos (/):**
```javascript
const comandosDisponibles = [
  { id: 'h1', icono: '📌', nombre: 'Título Grande', plantilla: '# ' },
  { id: 'h2', icono: '📄', nombre: 'Título Mediano', plantilla: '## ' },
  { id: 'h3', icono: '📝', nombre: 'Título Pequeño', plantilla: '### ' },
  { id: 'lista', icono: '📋', nombre: 'Lista', plantilla: '• ' },
  { id: 'numero', icono: '🔢', nombre: 'Lista Numerada', plantilla: '1. ' },
  { id: 'checkbox', icono: '☑️', nombre: 'Checkbox', plantilla: '- [ ] ' },
  { id: 'cita', icono: '💬', nombre: 'Cita', plantilla: '> ' },
  { id: 'codigo', icono: '💻', nombre: 'Bloque de Código', plantilla: '```\n\n```' },
  { id: 'divisor', icono: '➖', nombre: 'Línea Divisora', plantilla: '\n---\n' }
];
```

**Renderizado Markdown → HTML:**
```javascript
const renderizarContenidoNotion = (markdown) => {
  let html = markdown
    // Títulos
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    
    // Negrita/Cursiva
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    
    // Código inline
    .replace(/`(.+?)`/g, '<code>$1</code>')
    
    // Listas
    .replace(/^• (.+)$/gm, '<li>$1</li>')
    .replace(/^- \[ \] (.+)$/gm, '<li class="checkbox">☐ $1</li>')
    .replace(/^- \[x\] (.+)$/gm, '<li class="checkbox checked">☑ $1</li>')
    
    // Bloques de código
    .replace(/```\n([\s\S]+?)\n```/g, '<pre><code>$1</code></pre>')
    
    // Citas
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    
    // Divisores
    .replace(/^---$/gm, '<hr />');
  
  return html;
};
```

#### Generación de Ejercicios desde Notas:

```javascript
const generarEjerciciosDesdeNota = async () => {
  // 1. Guardar contexto en archivo temporal
  const carpetaDestino = rutaNotasActual || 'contexto_ejercicios';
  
  await fetch(`${API_URL}/api/guardar_contexto_ejercicio`, {
    method: 'POST',
    body: JSON.stringify({
      contenido: editorNotaContenido,
      titulo: editorNotaTitulo,
      carpeta: carpetaDestino
    })
  });
  
  // 2. Abrir modal de configuración de práctica
  setCarpetaPractica(carpetaDestino);
  setTipoFuentePractica('carpeta');
  setModalPracticaAbierto(true);
};
```

---

### **FASE 5: CIERRE** ✅

**Objetivo:** Resumir sesión, reflexionar, guardar estadísticas.

#### Datos mostrados:

```jsx
{faseActual === 'cierre' && (
  <div className="fase-cierre">
    {/* Header celebración */}
    <div className="cierre-header-celebracion">
      <div className="celebration-icon">🎉</div>
      <h1>¡SESIÓN COMPLETADA!</h1>
      <p>Has dedicado {resumenSesion.tiempoEfectivo} minutos</p>
    </div>
    
    {/* Tiempo efectivo */}
    <div className="tiempo-efectivo-block">
      <span>⏱️ {resumenSesion.tiempoEfectivo} min</span>
      <div>({resumenSesion.tiempoTotal} min totales - {resumenSesion.tiempoPausa} min pausa)</div>
    </div>
    
    {/* Grid de resumen */}
    <div className="resumen-grid">
      <div className="stat-card-resumen">
        <div className="stat-icon-grande">❌</div>
        <div className="stat-numero-grande">{resumenSesion.erroresReforzados}</div>
        <div>Errores Reforzados</div>
      </div>
      
      <div className="stat-card-resumen">
        <div className="stat-icon-grande">🃏</div>
        <div className="stat-numero-grande">{resumenSesion.flashcardsRepasadas}</div>
        <div>Flashcards Repasadas</div>
      </div>
      
      <div className="stat-card-resumen">
        <div className="stat-icon-grande">📖</div>
        <div className="stat-numero-grande">{resumenSesion.documentosEstudiados}</div>
        <div>Documentos Nuevos</div>
      </div>
      
      <div className="stat-card-resumen">
        <div className="stat-icon-grande">📝</div>
        <div className="stat-numero-grande">{resumenSesion.notasCreadas}</div>
        <div>Notas Creadas</div>
      </div>
    </div>
    
    {/* Reflexión personal */}
    <div className="reflexion-section">
      <h3>💭 REFLEXIÓN PERSONAL</h3>
      
      <label>¿Qué fue lo más difícil hoy?</label>
      <textarea 
        value={reflexionDificil}
        onChange={(e) => setReflexionDificil(e.target.value)}
        maxLength={150}
      />
      
      <label>¿Qué deberías revisar mañana?</label>
      <textarea 
        value={reflexionManana}
        onChange={(e) => setReflexionManana(e.target.value)}
        maxLength={150}
      />
    </div>
    
    {/* Recomendaciones */}
    {recomendacionesSesion.length > 0 && (
      <div className="proxima-sesion-preview">
        <h3>🔮 PRÓXIMA SESIÓN RECOMENDADA</h3>
        <ul>
          {recomendacionesSesion.map((rec) => (
            <li>{rec.texto}</li>
          ))}
        </ul>
      </div>
    )}
    
    {/* Botón finalizar */}
    <button onClick={finalizarYGuardarSesion}>
      🎯 FINALIZAR SESIÓN Y GUARDAR
    </button>
  </div>
)}
```

#### Guardado final:

```javascript
const finalizarYGuardarSesion = async () => {
  setGuardandoSesion(true);
  
  const sesionCompleta = {
    fecha: new Date().toISOString(),
    carpeta_trabajo: rutaCalentamientoActual,
    tiempo_efectivo: tiempoTotalEfectivo,
    tiempo_total: tiempoSesion * 60,
    tiempo_pausa: tiempoTotalPausa,
    estadisticas: estadisticasSesion,
    reflexion: {
      dificil: reflexionDificil,
      manana: reflexionManana
    },
    fases_completadas: fasesSesion.map((f, idx) => ({
      nombre: f.nombre,
      completada: idx <= indiceFaseActual
    }))
  };
  
  // Guardar en backend
  await fetch(`${API_URL}/datos/sesiones/completadas`, {
    method: 'POST',
    body: JSON.stringify({ sesiones: [sesionCompleta] })
  });
  
  // Limpiar sesión activa
  await fetch(`${API_URL}/sesion`, { method: 'DELETE' });
  localStorage.removeItem('examinator_sesion_activa');
  
  // Resetear estado
  setSesionActiva(false);
  setSelectedMenu('inicio');
  
  setGuardandoSesion(false);
  setMensaje({
    tipo: 'success',
    texto: '✅ Sesión guardada exitosamente'
  });
};
```

---

## ⏸️ SISTEMA DE DESCANSOS (POMODORO)

### Cálculo de descansos científicos:

```javascript
const calcularTiempoDescanso = (tiempoTotalMinutos) => {
  if (tiempoTotalMinutos <= 25) {
    return tiempoTotalMinutos * 60; // Sin interrupciones
  } else if (tiempoTotalMinutos <= 50) {
    return 1500; // 25 min (Pomodoro estándar)
  } else if (tiempoTotalMinutos <= 90) {
    return 1800; // 30 min (Ultradian rhythm)
  } else if (tiempoTotalMinutos <= 120) {
    return 2400; // 40 min
  } else {
    return 3000; // 50 min (máximo)
  }
};
```

### Cronómetro de descanso:

```javascript
useEffect(() => {
  if (!sesionActiva || sesionPausada || enDescanso) return;
  
  const intervalo = setInterval(() => {
    // Decrementar tiempo restante de la fase
    setTiempoRestante(prev => {
      if (prev <= 0) {
        // Fase terminada, avanzar
        avanzarFase();
        return 0;
      }
      return prev - 1;
    });
    
    // Decrementar tiempo hasta descanso
    setTiempoHastaDescanso(prev => {
      if (prev <= 0) {
        // ¡Descanso!
        activarDescanso();
        return intervaloDescansoInicial;
      }
      return prev - 1;
    });
    
    // Acumular tiempo de estudio efectivo
    setTiempoTotalEfectivo(prev => prev + 1);
  }, 1000);
  
  return () => clearInterval(intervalo);
}, [sesionActiva, sesionPausada, enDescanso]);
```

### Activación de descanso:

```javascript
const activarDescanso = () => {
  setEnDescanso(true);
  
  // Determinar duración del descanso
  const tiempoDescanso = tiempoAcumuladoEstudio >= 7200 
    ? 900   // 15 min (descanso largo después de 2 horas)
    : 300;  // 5 min (descanso corto después de 25-50 min)
  
  setFaseActual('descanso');
  setTiempoRestante(tiempoDescanso);
  setTiempoFaseActual(tiempoDescanso);
};
```

### Fase de descanso:

```jsx
{faseActual === 'descanso' && (
  <div className="fase-descanso">
    <div className="descanso-icon-main">
      {tiempoRestante > 600 ? '🧘' : '☕'}
    </div>
    
    <h1>{tiempoRestante > 600 ? 'Descanso Largo' : 'Descanso Corto'}</h1>
    
    <div className="descanso-tiempo-grande">
      {Math.floor(tiempoRestante / 60)} minutos
    </div>
    
    <div className="descanso-recomendaciones">
      <h3>💡 Recomendaciones científicas:</h3>
      <ul>
        <li>🚶 Levántate y camina</li>
        <li>💧 Bebe agua</li>
        <li>👀 Regla 20-20-20 (mirar 20 metros por 20 seg)</li>
        <li>🧘 Respira profundo</li>
        {tiempoRestante > 600 && <li>🍎 Come algo ligero</li>}
      </ul>
    </div>
    
    <button onClick={saltarDescanso}>
      ⏭️ Saltar descanso
    </button>
  </div>
)}
```

---

## 💾 PERSISTENCIA DE SESIÓN

### Guardado automático (cada 30s):

```javascript
useEffect(() => {
  if (!sesionActiva) return;
  
  const intervaloGuardado = setInterval(() => {
    guardarEstadoSesion();
  }, 30000); // 30 segundos
  
  return () => clearInterval(intervaloGuardado);
}, [sesionActiva, faseActual, tiempoRestante, estadisticasSesion]);
```

### Función de guardado:

```javascript
const guardarEstadoSesion = async () => {
  const estadoCompleto = {
    timestamp: new Date().toISOString(),
    estado: {
      sesionActiva,
      sesionPausada,
      faseActual,
      indiceFaseActual,
      tiempoRestante,
      tiempoFaseActual,
      tiempoTotalEfectivo,
      tiempoHastaDescanso,
      enDescanso
    },
    datos: {
      errores: {
        lista: erroresActuales,
        indiceActual: indiceErrorActual,
        respuestas: historialRespuestasErrores
      },
      flashcards: {
        lista: flashcardsSesion,
        indiceActual: indiceFlashcardActual,
        volteadas: flashcardsVolteadas
      },
      notas: {
        titulo: editorNotaTitulo,
        contenido: editorNotaContenido,
        tags: editorNotaTags
      }
    },
    configuracion: {
      fasesSesion,
      rutaCalentamiento: rutaCalentamientoActual,
      prioridad: prioridadSesion,
      modoLibre: modoLibreActivo
    },
    estadisticas: estadisticasSesion,
    reflexion: {
      dificil: reflexionDificil,
      manana: reflexionManana
    }
  };
  
  // Guardar en backend
  try {
    await setSesionActiva(estadoCompleto);
    console.log('✅ Sesión guardada en backend');
  } catch (error) {
    console.error('❌ Error guardando sesión:', error);
  }
  
  // Guardar en localStorage (respaldo)
  localStorage.setItem('examinator_sesion_activa', JSON.stringify(estadoCompleto));
};
```

### Restauración de sesión:

```javascript
useEffect(() => {
  const restaurarSesionGuardada = async () => {
    // 1. Intentar cargar desde backend
    try {
      const sesionBackend = await getSesionActiva();
      if (sesionBackend && sesionBackend.timestamp) {
        aplicarEstadoSesion(sesionBackend);
        return;
      }
    } catch (error) {
      console.warn('No se pudo cargar sesión del backend');
    }
    
    // 2. Intentar cargar desde localStorage
    const sesionLocal = localStorage.getItem('examinator_sesion_activa');
    if (sesionLocal) {
      const estadoGuardado = JSON.parse(sesionLocal);
      aplicarEstadoSesion(estadoGuardado);
    }
  };
  
  restaurarSesionGuardada();
}, []);

const aplicarEstadoSesion = (estadoGuardado) => {
  // Restaurar estado
  setSesionActiva(estadoGuardado.estado.sesionActiva);
  setSesionPausada(estadoGuardado.estado.sesionPausada);
  setFaseActual(estadoGuardado.estado.faseActual);
  setIndiceFaseActual(estadoGuardado.estado.indiceFaseActual);
  setTiempoRestante(estadoGuardado.estado.tiempoRestante);
  setTiempoFaseActual(estadoGuardado.estado.tiempoFaseActual);
  setTiempoTotalEfectivo(estadoGuardado.estado.tiempoTotalEfectivo);
  setTiempoHastaDescanso(estadoGuardado.estado.tiempoHastaDescanso);
  setEnDescanso(estadoGuardado.estado.enDescanso);
  
  // Restaurar datos
  setErroresActuales(estadoGuardado.datos.errores.lista);
  setIndiceErrorActual(estadoGuardado.datos.errores.indiceActual);
  setFlashcardsSesion(estadoGuardado.datos.flashcards.lista);
  setIndiceFlashcardActual(estadoGuardado.datos.flashcards.indiceActual);
  setFlashcardsVolteadas(estadoGuardado.datos.flashcards.volteadas);
  setEditorNotaTitulo(estadoGuardado.datos.notas.titulo);
  setEditorNotaContenido(estadoGuardado.datos.notas.contenido);
  setEditorNotaTags(estadoGuardado.datos.notas.tags);
  
  // Restaurar configuración
  setFasesSesion(estadoGuardado.configuracion.fasesSesion);
  setRutaCalentamientoActual(estadoGuardado.configuracion.rutaCalentamiento);
  setPrioridadSesion(estadoGuardado.configuracion.prioridad);
  setModoLibreActivo(estadoGuardado.configuracion.modoLibre);
  
  // Restaurar estadísticas
  setEstadisticasSesion(estadoGuardado.estadisticas);
  
  // Restaurar reflexión
  setReflexionDificil(estadoGuardado.reflexion.dificil);
  setReflexionManana(estadoGuardado.reflexion.manana);
  
  // Cambiar a vista de sesión
  setSelectedMenu('sesion');
  
  console.log('✅ Sesión restaurada exitosamente');
};
```

---

## 📊 ESTADOS Y DATOS

### Estados principales (React):

```javascript
// 1. SESIÓN
const [sesionActiva, setSesionActiva] = useState(false);
const [sesionPausada, setSesionPausada] = useState(false);
const [tiempoSesion, setTiempoSesion] = useState(30); // minutos
const [prioridadSesion, setPrioridadSesion] = useState('errores');
const [modoLibreActivo, setModoLibreActivo] = useState(false);

// 2. FASES
const [fasesSesion, setFasesSesion] = useState([]);
const [faseActual, setFaseActual] = useState(null);
const [indiceFaseActual, setIndiceFaseActual] = useState(0);
const [tiempoRestante, setTiempoRestante] = useState(0); // segundos
const [tiempoFaseActual, setTiempoFaseActual] = useState(0);

// 3. TIEMPO
const [tiempoTotalEfectivo, setTiempoTotalEfectivo] = useState(0);
const [tiempoHastaDescanso, setTiempoHastaDescanso] = useState(1500);
const [intervaloDescansoInicial, setIntervaloDescansoInicial] = useState(1500);
const [enDescanso, setEnDescanso] = useState(false);
const [tiempoAcumuladoEstudio, setTiempoAcumuladoEstudio] = useState(0);

// 4. DATOS DE FASES
const [erroresActuales, setErroresActuales] = useState([]);
const [indiceErrorActual, setIndiceErrorActual] = useState(0);
const [flashcardsSesion, setFlashcardsSesion] = useState([]);
const [indiceFlashcardActual, setIndiceFlashcardActual] = useState(0);
const [flashcardsVolteadas, setFlashcardsVolteadas] = useState({});

// 5. EDITOR DE NOTAS
const [editorNotaTitulo, setEditorNotaTitulo] = useState('');
const [editorNotaContenido, setEditorNotaContenido] = useState('');
const [editorNotaTags, setEditorNotaTags] = useState('');
const [tabContenidoActivo, setTabContenidoActivo] = useState(0);

// 6. ESTADÍSTICAS
const [estadisticasSesion, setEstadisticasSesion] = useState({
  erroresReforzados: 0,
  flashcardsRepasadas: 0,
  practicasHechas: 0,
  notasTomadas: 0,
  documentosEstudiados: 0
});

// 7. CALENTAMIENTO
const [rutaCalentamientoActual, setRutaCalentamientoActual] = useState('');
const [carpetasCalentamiento, setCarpetasCalentamiento] = useState([]);

// 8. REFLEXIÓN (Cierre)
const [reflexionDificil, setReflexionDificil] = useState('');
const [reflexionManana, setReflexionManana] = useState('');
const [recomendacionesSesion, setRecomendacionesSesion] = useState([]);
const [guardandoSesion, setGuardandoSesion] = useState(false);
```

---

## 🔄 FLUJO COMPLETO

### Diagrama de flujo:

```
                    INICIO
                      ↓
          ┌───────────────────────┐
          │ Usuario hace clic en  │
          │ "Sesión de Estudio"   │
          └───────────────────────┘
                      ↓
          ┌───────────────────────┐
          │ Abrir Modal Config    │
          │ - Tiempo (15/30/45/60)│
          │ - Prioridad (errores) │
          │ - Modo Libre?         │
          └───────────────────────┘
                      ↓
          ┌───────────────────────┐
          │ Calcular Fases        │
          │ según tiempo/prioridad│
          └───────────────────────┘
                      ↓
          ┌───────────────────────┐
          │ FASE 1: CALENTAMIENTO │
          │ - Ver estadísticas    │
          │ - Seleccionar carpeta │
          │ - Cargar errores/fc   │
          └───────────────────────┘
                      ↓
          ┌───────────────────────┐
          │ FASE 2: ERRORES       │
          │ - Revisar 1 por 1     │
          │ - Responder/Evaluar   │
          │ - Marcar comprendido  │
          └───────────────────────┘
                      ↓
          ┌───────────────────────┐
          │ FASE 3: FLASHCARDS    │
          │ - Repaso tipo Anki    │
          │ - Evaluación SR       │
          │ - Actualizar intervalos│
          └───────────────────────┘
                      ↓
          ┌───────────────────────┐
          │ FASE 4: CONTENIDO     │
          │ - Crear notas         │
          │ - Crear flashcards    │
          │ - Generar ejercicios  │
          └───────────────────────┘
                      ↓
          ┌───────────────────────┐
          │ FASE 5: CIERRE        │
          │ - Ver resumen         │
          │ - Reflexionar         │
          │ - Guardar sesión      │
          └───────────────────────┘
                      ↓
                    FIN
```

### Funciones clave:

```javascript
// 1. Iniciar sesión
const iniciarSesionEstudio = async () => { ... };

// 2. Avanzar entre fases
const avanzarFase = () => {
  if (indiceFaseActual < fasesSesion.length - 1) {
    const siguienteFase = fasesSesion[indiceFaseActual + 1];
    setIndiceFaseActual(indiceFaseActual + 1);
    setFaseActual(siguienteFase.tipo);
    setTiempoRestante(siguienteFase.duracion);
    setTiempoFaseActual(siguienteFase.duracion);
  } else {
    // Sesión completa
    finalizarYGuardarSesion();
  }
};

// 3. Pausar/Reanudar
const pausarReanudarSesion = () => {
  if (sesionPausada) {
    // Reanudar
    setSesionPausada(false);
  } else {
    // Pausar
    setSesionPausada(true);
    setTimestampInicioPausa(Date.now());
  }
};

// 4. Salir de sesión
const salirSesion = async () => {
  if (confirm('¿Seguro que quieres salir? El progreso se guardará.')) {
    await guardarEstadoSesion();
    setSesionActiva(false);
    setSelectedMenu('inicio');
  }
};

// 5. Detener sesión (sin guardar)
const detenerSesion = async () => {
  setSesionActiva(false);
  await fetch(`${API_URL}/sesion`, { method: 'DELETE' });
  localStorage.removeItem('examinator_sesion_activa');
  // Resetear todos los estados
  // ...
};

// 6. Finalizar y guardar
const finalizarYGuardarSesion = async () => { ... };
```

---

## 🔗 INTEGRACIÓN CON OTROS MÓDULOS

### 1. **Integración con "Mis Cursos"**

```javascript
// Botón de acceso rápido desde fases
const irAMisCursos = () => {
  const carpetaActual = rutaCalentamientoActual || '';
  setRutaActual(carpetaActual);
  setSelectedMenu('cursos');
  cargarCarpeta(carpetaActual);
};
```

### 2. **Integración con "Notas"**

```javascript
// Guardar nota desde editor de sesión
const guardarNotaDesdeSesion = async () => {
  const nuevaNota = {
    id: `nota_${Date.now()}`,
    titulo: editorNotaTitulo,
    contenido: editorNotaContenido,
    tags: editorNotaTags.split(','),
    carpeta: rutaNotasActual || rutaCalentamientoActual || '',
    fecha_creacion: new Date().toISOString()
  };
  
  await guardarDatos('notas', [nuevaNota]);
  
  setMensaje({
    tipo: 'success',
    texto: '✅ Nota guardada'
  });
};
```

### 3. **Integración con "Flashcards"**

```javascript
// Guardar flashcard desde sesión
const guardarFlashcardDesdeSesion = async () => {
  const nuevaFlashcard = {
    id: `fc_${Date.now()}`,
    pregunta: formDataFlashcard.titulo,
    respuesta: formDataFlashcard.respuestaCorrecta,
    tipo: formDataFlashcard.tipo,
    carpeta: carpetaFlashcardActual?.ruta || '',
    fecha_creacion: new Date().toISOString(),
    proxima_revision: new Date(Date.now() + 24*60*60*1000).toISOString()
  };
  
  await guardarFlashcardEnCarpeta(nuevaFlashcard);
  
  setMensaje({
    tipo: 'success',
    texto: '✅ Flashcard guardada'
  });
};
```

### 4. **Integración con "Prácticas"**

```javascript
// Generar práctica desde contenido de sesión
const generarPracticaDesdeSesion = async () => {
  setCarpetaPractica(rutaCalentamientoActual || 'contexto_ejercicios');
  setPromptPractica(editorNotaContenido);
  setModalPracticaAbierto(true);
};
```

### 5. **Integración con "Errores"**

```javascript
// Cargar errores desde backend
const cargarErroresDeSesion = async () => {
  const todosErrores = await getDatos('errores');
  
  const erroresFiltrados = todosErrores.filter(err => 
    err.carpeta === rutaCalentamientoActual &&
    !err.comprendido
  );
  
  setErroresActuales(erroresFiltrados);
};
```

---

## 🎓 RESUMEN TÉCNICO

### Tecnologías utilizadas:
- **React** (hooks: useState, useEffect)
- **Backend API** (FastAPI)
- **LocalStorage** (persistencia local)
- **CSS Modules** (estilos especializados)

### Algoritmos clave:
- **Spaced Repetition** (SM-2 simplificado)
- **Pomodoro científico** (descansos adaptativos)
- **Cálculo de fases dinámico** (según tiempo/prioridad)

### Patrones de diseño:
- **Estado centralizado** (React hooks)
- **Persistencia dual** (backend + localStorage)
- **Componentes modulares** (fases independientes)
- **Progresión secuencial** (wizard de fases)

---

## 📝 CONCLUSIÓN

La **Pestaña "Sesión de Estudio"** es un **sistema completo de aprendizaje guiado** que combina:

✅ **Estructura científica** (Pomodoro, Spaced Repetition)  
✅ **Adaptación personalizada** (prioridades, tiempo, carpetas)  
✅ **Interactividad avanzada** (corrección de errores, flashcards tipo Anki)  
✅ **Persistencia robusta** (dual: backend + localStorage)  
✅ **Reflexión metacognitiva** (fase de cierre con reflexión personal)

Es el **núcleo del sistema de aprendizaje** de Examinator, integrando todos los módulos (cursos, notas, flashcards, prácticas, errores) en una **experiencia cohesiva y científicamente fundamentada**.

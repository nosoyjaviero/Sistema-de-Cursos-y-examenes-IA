# 🎯 Flujo Completo: Generación de Práctica

Este documento explica paso a paso cómo funciona el proceso de generación de prácticas desde que el usuario hace clic en el botón hasta que se guarda el archivo.

---

## 📍 Punto de Inicio

### 🔘 Botón en la UI
**Ubicación:** `examinator-web/src/App.jsx` línea ~13949

```jsx
<button onClick={(e) => {
  e.stopPropagation();
  setMenuAbierto(null);
  abrirModalPractica(doc.ruta, 'documento');
}}>
  🧑‍💻 Generar Práctica
</button>
```

**Contexto:** Este botón aparece en el menú de puntos (`btn-menu-dots`) de cada documento (`documento-item`) dentro de una carpeta.

---

## 📝 PASO 1: Abrir Modal de Configuración

### Función: `abrirModalPractica()`
**Ubicación:** `App.jsx` línea ~7933

```javascript
const abrirModalPractica = (ruta, tipo = 'carpeta') => {
  // Limpiar estado anterior
  setPreguntasExamen([]);
  setRespuestasUsuario({});
  setExamenCompletado(false);
  setResultadoExamen(null);
  setFlashcardsVolteadas({});
  
  // Configurar datos del modal
  setCarpetaPractica(ruta);              // Guarda la ruta del documento
  setTipoFuentePractica(tipo);           // Tipo: 'documento' o 'carpeta'
  setPromptPractica('');                 // Limpia prompt personalizado
  setModalPracticaAbierto(true);         // Abre el modal
};
```

**Acción:** Abre un modal donde el usuario puede:
- Seleccionar cantidad de preguntas por tipo (flashcards, MCQ, verdadero/falso, etc.)
- Escribir un prompt personalizado (opcional)
- Ver el subtipo de flashcard (respuesta corta vs. selección múltiple)

---

## ⚙️ PASO 2: Confirmar y Generar

### Función: `confirmarGenerarPractica()`
**Ubicación:** `App.jsx` línea ~7947

#### 2.1 Validación Inicial
```javascript
const totalPreguntas = numFlashcards + numMCQ + numVerdaderoFalso + 
                       numCloze + numRespuestaCorta + ... // más tipos

if (totalPreguntas === 0) {
  setMensaje({
    tipo: 'error',
    texto: '❌ Debes seleccionar al menos un tipo de pregunta'
  });
  return;
}
```

#### 2.2 Construcción del Prompt
```javascript
let promptCompleto = ``;

if (promptPractica.trim()) {
  promptCompleto += `INSTRUCCIONES PERSONALIZADAS:\n${promptPractica}\n\n`;
}

promptCompleto += `TIPOS DE PREGUNTAS A GENERAR:\n\n`;

// Añade especificaciones JSON para cada tipo de pregunta
if (numFlashcards > 0) {
  promptCompleto += `**${numFlashcards} Flashcards...`;
  // Incluye ejemplo de formato JSON esperado
}
```

**Nota:** El prompt se construye en el frontend pero el backend también puede ignorarlo si encuentra contenido en la ruta del documento.

#### 2.3 Llamada al Backend
```javascript
const response = await fetch(`${API_URL}/api/generar_practica`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    ruta: carpetaPractica,           // Ruta del documento
    prompt: promptCompleto,          // Prompt construido
    tipo_caso: tipoCasoEstudio,      // Tipo de caso de estudio
    tipo_flashcard: tipoFlashcard,   // 'respuesta_corta' o 'seleccion_confusa'
    
    // Contadores de cada tipo de pregunta
    num_flashcards: numFlashcards,
    num_mcq: numMCQ,
    num_verdadero_falso: numVerdaderoFalso,
    num_cloze: numCloze,
    num_respuesta_corta: numRespuestaCorta,
    // ... todos los demás tipos
  }),
});
```

---

## 🤖 PASO 3: Procesamiento en el Backend

### Endpoint: `/api/generar_practica`
**Ubicación:** `api_server.py` línea ~2622

#### 3.1 Extracción de Parámetros
```python
@app.post("/api/generar_practica")
async def generar_practica(datos: dict):
    # Extraer todos los parámetros
    ruta = datos.get("ruta")
    prompt = datos.get("prompt", "")
    tipo_flashcard = datos.get("tipo_flashcard", "respuesta_corta")
    
    # Contadores
    num_flashcards = datos.get("num_flashcards", 0)
    num_mcq = datos.get("num_mcq", 0)
    # ... etc
```

#### 3.2 Cargar Contenido del Documento
```python
contenido = ""
if ruta:
    try:
        ruta_path = Path(ruta)
        
        # Si la ruta no existe, intentar desde extracciones/
        if not ruta_path.exists():
            ruta_alternativa = Path("extracciones") / ruta
            if ruta_alternativa.exists():
                ruta_path = ruta_alternativa
        
        if ruta_path.exists():
            contenido = obtener_texto(str(ruta_path))  # Extrae texto del PDF/TXT
            print(f"✅ Contenido cargado: {len(contenido)} caracteres")
```

**Función `obtener_texto()`:** Usa PyMuPDF para extraer texto de PDFs o lee archivos de texto plano.

#### 3.3 Inicializar Generador de IA
```python
# Cargar configuración
config = cargar_config()
modelo_ollama = config.get("modelo_ollama_activo", "Meta-Llama-3.1-8B-Instruct-Q4-K-L")
usar_ollama = config.get("usar_ollama", True)

# Crear generador
if usar_ollama:
    generador_actual = GeneradorUnificado(
        usar_ollama=True,
        modelo_ollama=modelo_ollama,
        n_gpu_layers=gpu_layers
    )
```

**GeneradorUnificado:** Clase que maneja tanto modelos de Ollama (GPU) como llama-cpp-python (CPU/GPU).

#### 3.4 Mapeo de Tipos de Preguntas
```python
num_preguntas = {}

# Mapear tipos de práctica a tipos del generador
if num_flashcards > 0 or num_respuesta_corta > 0:
    num_preguntas['short_answer'] = num_flashcards + num_respuesta_corta

if num_mcq > 0:
    num_preguntas['mcq'] = num_mcq

if num_verdadero_falso > 0:
    num_preguntas['true_false'] = num_verdadero_falso

# ... mapeo de todos los tipos
```

**Nota:** Los tipos del frontend se mapean a los tipos internos del generador.

#### 3.5 Generación con IA
```python
contexto = contenido if contenido else prompt

preguntas = generador_actual.generar_examen(
    contexto,                    # Contenido del documento
    num_preguntas,               # Dict con cantidad por tipo
    ajustes_modelo=ajustes,      # Configuración (temperature, max_tokens, etc.)
    callback_progreso=callback_progreso,
    session_id=session_id,
    tipo_caso=tipo_caso
)
```

**Proceso Interno:**
1. El generador construye un prompt especializado por cada tipo de pregunta
2. Llama al modelo de IA (Ollama o llama-cpp)
3. Parsea la respuesta JSON del modelo
4. Crea objetos `Pregunta` con la estructura correcta

#### 3.6 Post-procesamiento
```python
# Convertir a JSON
preguntas_json = [p.to_dict() for p in preguntas]

# Aplanar metadata anidada (fix común)
for pregunta_json in preguntas_json:
    if pregunta_json.get('tipo') == 'cloze' and 'metadata' in pregunta_json:
        # Si metadata tiene metadata anidada, aplanar
        if isinstance(pregunta_json['metadata'], dict) and 'metadata' in pregunta_json['metadata']:
            metadata_interna = pregunta_json['metadata']['metadata']
            # Mover campos importantes al nivel superior
            pregunta_json['metadata']['text_with_gaps'] = metadata_interna.get('text_with_gaps')
            pregunta_json['metadata']['answers'] = metadata_interna.get('answers')
            del pregunta_json['metadata']['metadata']
```

**Problema Resuelto:** A veces el modelo genera `metadata.metadata` anidado, este código lo aplana.

#### 3.7 Respuesta al Frontend
```python
resultado = {
    "success": True,
    "session_id": session_id,
    "preguntas": preguntas_json,
    "total_preguntas": len(preguntas),
}

return resultado
```

---

## 💾 PASO 4: Guardar Práctica en el Frontend

### Procesamiento de la Respuesta
**Ubicación:** `App.jsx` línea ~8520

```javascript
if (response.ok) {
  const data = await response.json();
  
  // Limpiar archivo temporal de exámenes
  await limpiarExamenLocal();
  
  const practicaId = `practica_${Date.now()}`;
  
  // 1. Determinar carpeta destino
  let carpetaPracticaGuardar = '';
  if (tipoFuentePractica === 'carpeta') {
    carpetaPracticaGuardar = carpetaPractica;
  } else {
    // Es un documento, extraer carpeta padre
    const partes = carpetaPractica.split('\\');
    partes.pop(); // Quitar el nombre del archivo
    carpetaPracticaGuardar = partes.join('\\');
  }
  
  // 2. Normalizar carpeta (remover "extracciones\")
  if (carpetaPracticaGuardar.includes('extracciones\\')) {
    const partes = carpetaPracticaGuardar.split('extracciones\\');
    carpetaPracticaGuardar = partes[partes.length - 1] || '';
  }
  
  // 3. Crear objeto de práctica
  const nuevaPractica = {
    id: practicaId,
    ruta: carpetaPractica,
    carpeta: carpetaPracticaGuardar,
    tipo: tipoFuentePractica,
    prompt: promptPractica,
    preguntas: data.preguntas || [],
    respuestas: {},
    fecha: new Date().toISOString(),
    completada: false,
    stats: {
      flashcards: numFlashcards,
      mcq: numMCQ,
      // ... todos los contadores
    }
  };
  
  // 4. Guardar en backend
  await guardarPracticaEnCarpeta(nuevaPractica);
  
  // 5. Actualizar estado local
  const practicas = await getDatos('practicas');
  setPracticas([...practicas, nuevaPractica]);
  
  // 6. Abrir modal de práctica
  setEsPractica(true);
  setExamenActivo(true);
  setPreguntasExamen(data.preguntas || []);
  setModalExamenAbierto(true);
}
```

---

## 📂 PASO 5: Persistencia en Disco

### Función: `guardarPracticaEnCarpeta()`
**Ubicación:** `App.jsx` línea ~2951

```javascript
const guardarPracticaEnCarpeta = async (practica) => {
  const carpeta = practica.carpeta || '';
  
  // Endpoint para practicas.json
  const response = await fetch(`${API_URL}/datos/practicas/carpeta`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      practica: practica,
      carpeta: practica.carpeta
    })
  });

  if (!response.ok) throw new Error('Error al guardar práctica');
  
  return await response.json();
};
```

### Endpoint: `/datos/practicas/carpeta`
**Ubicación:** `api_server.py` línea ~4051

```python
@app.post("/datos/practicas/carpeta")
async def guardar_practica_carpeta(request: Request):
    data = await request.json()
    practica = data.get("practica")
    carpeta = data.get("carpeta", "")
    
    # 1. Determinar carpeta destino
    if carpeta:
        carpeta_destino = EXTRACCIONES_PATH / carpeta
    else:
        carpeta_destino = EXTRACCIONES_PATH / "practicas"
    
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    archivo = carpeta_destino / "practicas.json"
    
    # 2. Leer prácticas existentes
    practicas = []
    if archivo.exists():
        with open(archivo, "r", encoding="utf-8") as f:
            practicas = json.load(f)
    
    # 3. Actualizar o agregar
    practica_id = practica.get("id")
    encontrado = False
    for i, p in enumerate(practicas):
        if p.get("id") == practica_id:
            practicas[i] = practica
            encontrado = True
            break
    
    if not encontrado:
        practicas.append(practica)
    
    # 4. Guardar archivo
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(practicas, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Práctica guardada en: {archivo}")
    return JSONResponse(content={
        "success": True,
        "count": len(practicas),
        "carpeta": str(carpeta_destino.name)
    })
```

---

## 📁 Estructura de Archivos Resultante

Después de generar una práctica desde un documento en `extracciones/Platzi/documento.pdf`:

```
extracciones/
└── Platzi/
    ├── documento.pdf
    └── practicas.json  ← SE CREA/ACTUALIZA AQUÍ
```

**Contenido de `practicas.json`:**
```json
[
  {
    "id": "practica_1732654321000",
    "ruta": "C:\\...\\extracciones\\Platzi\\documento.pdf",
    "carpeta": "Platzi",
    "tipo": "documento",
    "prompt": "",
    "preguntas": [
      {
        "tipo": "flashcard",
        "pregunta": "¿Qué es Python?",
        "respuesta": "Un lenguaje de programación...",
        "puntos": 10,
        "metadata": { ... }
      }
    ],
    "respuestas": {},
    "fecha": "2024-11-26T10:30:00.000Z",
    "completada": false,
    "stats": {
      "flashcards": 5,
      "mcq": 3,
      ...
    }
  }
]
```

---

## 🔄 Flujo Resumido

```
1. Usuario → Clic en "🧑‍💻 Generar Práctica" (documento-item)
   ↓
2. Frontend → abrirModalPractica(doc.ruta, 'documento')
   ↓
3. Usuario → Configura tipos de preguntas en modal
   ↓
4. Usuario → Clic en "Generar"
   ↓
5. Frontend → confirmarGenerarPractica()
   │  • Construye prompt con especificaciones
   │  • Llama a POST /api/generar_practica
   ↓
6. Backend → Endpoint generar_practica()
   │  • Carga contenido del documento (PyMuPDF)
   │  • Inicializa GeneradorUnificado (IA)
   │  • Mapea tipos de preguntas
   │  • Genera con modelo de IA
   │  • Post-procesa respuesta
   │  • Retorna JSON con preguntas
   ↓
7. Frontend → Recibe respuesta
   │  • Crea objeto nuevaPractica
   │  • Normaliza carpeta
   │  • Llama a guardarPracticaEnCarpeta()
   ↓
8. Backend → Endpoint /datos/practicas/carpeta
   │  • Determina ruta: extracciones/Platzi/practicas.json
   │  • Lee archivo existente (si existe)
   │  • Agrega/actualiza práctica
   │  • Guarda JSON en disco
   ↓
9. Frontend → Actualiza estado
   │  • Añade a setPracticas()
   │  • Abre modal de examen
   │  • Usuario puede responder preguntas
```

---

## 🔍 Puntos Clave

### 1. **Ruta del Documento**
- Se pasa la ruta completa del documento (puede ser absoluta o relativa)
- El backend intenta cargarla directamente o desde `extracciones/`

### 2. **Normalización de Carpeta**
- Se remueve la parte `extracciones\` para obtener solo el nombre de la carpeta
- Ejemplo: `C:\...\extracciones\Platzi` → `Platzi`

### 3. **Tipos de Preguntas**
- Frontend: nombres descriptivos (`num_flashcards`, `num_mcq`)
- Backend: mapeo a tipos internos (`short_answer`, `mcq`, `true_false`)

### 4. **Generador de IA**
- Puede usar Ollama (GPU) o llama-cpp-python (CPU/GPU)
- Configurado en `config.json` → `usar_ollama: true/false`

### 5. **Archivo de Destino**
- Siempre se guarda en `practicas.json` dentro de la carpeta correspondiente
- No en `resultados_practicas/*.json` (ese se usa para resultados evaluados)

### 6. **Estado vs. Persistencia**
- Estado: `practicas` array en React (temporal, sesión actual)
- Persistencia: `practicas.json` en disco (permanente)

---

## 🐛 Problemas Comunes

### ❌ "No se pudo cargar contenido de ruta"
**Causa:** La ruta no existe o no es accesible
**Solución:** Verificar que el archivo existe y la ruta es correcta

### ❌ "Error al generar práctica: timeout"
**Causa:** El modelo de IA tarda mucho en responder
**Solución:** Reducir cantidad de preguntas o usar modelo más rápido

### ❌ "Metadata anidada incorrectamente"
**Causa:** El modelo genera `metadata.metadata`
**Solución:** El post-procesamiento aplana automáticamente

### ❌ "Práctica no aparece en la lista"
**Causa:** No se guardó correctamente o no se actualizó el estado
**Solución:** Verificar logs del backend y llamar a `getDatos('practicas')`

---

## 📊 Logs de Debugging

### Frontend (Consola del Navegador)
```javascript
console.log('🎯 Práctica generada - Total preguntas:', data.preguntas?.length);
console.log('📁 Carpeta práctica normalizada:', carpetaPracticaGuardar);
```

### Backend (Terminal)
```python
print(f"🔍 DEBUG - Ruta recibida: {ruta}")
print(f"✅ Contenido cargado: {len(contenido)} caracteres")
print(f"🤖 Generando flashcards con IA...")
print(f"✅ Práctica guardada en: {archivo}")
```

---

## 🎯 Conclusión

El flujo completo involucra:
1. **UI React** para configuración
2. **Fetch API** para comunicación
3. **FastAPI Backend** para procesamiento
4. **IA (Ollama/llama-cpp)** para generación
5. **Sistema de archivos** para persistencia

Todo el proceso está diseñado para ser robusto, con validaciones en cada paso y manejo de errores completo.

---

# 📚 ANEXO: Gestión Completa de Prácticas en App.jsx

Este anexo documenta todo el ciclo de vida de las prácticas en el frontend: carga, visualización, resolución, evaluación y repetición espaciada.

---

## 📥 CARGA INICIAL DE PRÁCTICAS

### Función: `getDatos()`
**Ubicación:** `App.jsx` línea ~44

Esta es la función genérica para obtener datos desde el backend:

```javascript
async function getDatos(tipo) {
  try {
    const response = await fetch(`http://${SERVER_IP}:8000/datos/${tipo}`);
    if (!response.ok) {
      console.error(`Error al obtener ${tipo}: ${response.status}`);
      return [];
    }
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error(`Error de red al obtener ${tipo}:`, error);
    return [];
  }
}
```

**Uso para prácticas:**
```javascript
const practicas = await getDatos('practicas');
```

**Backend Endpoint:** `GET /datos/practicas`
- Busca recursivamente todos los `practicas.json` en `extracciones/`
- También busca archivos individuales en `resultados_practicas/*.json`
- Retorna array unificado de todas las prácticas

### Estado de Prácticas
```javascript
const [practicas, setPracticas] = useState([]);
```

Se carga inicialmente y se actualiza cuando:
- Se genera una nueva práctica
- Se completa una práctica
- Se evalúa una práctica (repetición espaciada)

---

## 🗂️ PESTAÑA DE PRÁCTICAS EN EL CHATBOT

### Ubicación de la Tab
**Línea:** `App.jsx` ~16918

```jsx
<button
  className={`explorador-tab ${tipoExploradorChat === 'practicas' ? 'active' : ''}`}
  onClick={() => {
    setTipoExploradorChat('practicas')
    explorarCarpetaChat('practicas', '')
  }}
>
  ✅ Prácticas
</button>
```

### Función: `explorarCarpetaChat()`
**Ubicación:** `App.jsx` línea ~6017

```javascript
const explorarCarpetaChat = async (tipo, ruta = '') => {
  setCargandoArchivos(true)
  try {
    const response = await fetch(
      `${API_URL}/api/archivos/explorar?tipo=${tipo}&ruta=${encodeURIComponent(ruta)}`
    )
    const data = await response.json()
    
    // Actualizar carpetas y archivos
    setCarpetasExploradorChat(data.carpetas || [])
    setRutaExploradorChat(data.ruta_actual || '')
    setArchivosRecientes(data.archivos || [])
  } catch (error) {
    console.error('Error al explorar carpeta:', error)
    setMensaje({
      tipo: 'error',
      texto: '❌ Error al explorar carpeta'
    })
  } finally {
    setCargandoArchivos(false)
  }
}
```

**Backend Endpoint:** `GET /api/archivos/explorar?tipo=practicas&ruta=`

**Proceso:**
1. El backend busca en `extracciones/` según el tipo
2. Para prácticas, busca `practicas.json` en cada carpeta
3. Retorna lista de carpetas (con contador de prácticas) y archivos
4. El frontend muestra árbol de carpetas navegable

### Visualización de Archivos

```jsx
{archivosRecientes.map((archivo, idx) => {
  const yaAdjuntado = archivosContextoChat.some(
    a => a.ruta_completa === archivo.ruta_completa
  )
  
  return (
    <div key={idx} className={`archivo-item ${yaAdjuntado ? 'adjuntado' : ''}`}>
      <div className="archivo-info">
        <span className="archivo-icon">
          {archivo.tipo === 'Práctica' ? '✅' : '📝'}
        </span>
        <div className="archivo-detalles">
          <span className="archivo-nombre">{archivo.nombre}</span>
          <span className="archivo-meta">
            {archivo.tipo} • {archivo.carpeta} • 
            {(archivo.tamaño / 1024).toFixed(1)} KB • 
            {new Date(archivo.modificado * 1000).toLocaleDateString('es-ES')}
          </span>
        </div>
      </div>
      <button
        className={`btn-adjuntar ${yaAdjuntado ? 'adjuntado' : ''}`}
        onClick={() => yaAdjuntado 
          ? quitarArchivoContexto(archivo.ruta_completa) 
          : adjuntarArchivoContexto(archivo)
        }
      >
        {yaAdjuntado ? '✓ Adjuntado' : '+ Adjuntar'}
      </button>
    </div>
  )
})}
```

**Características:**
- Muestra icono según tipo (✅ para prácticas)
- Indica si ya está adjuntado al contexto del chat
- Muestra metadata (carpeta, tamaño, fecha)
- Permite adjuntar/quitar del contexto

---

## 📎 ADJUNTAR PRÁCTICAS AL CONTEXTO DEL CHAT

### Función: `adjuntarArchivoContexto()`
**Ubicación:** `App.jsx` línea ~6038

```javascript
const adjuntarArchivoContexto = async (archivo) => {
  try {
    console.log('📎 Adjuntando archivo:', archivo)
    
    // Leer contenido del archivo
    const response = await fetch(`${API_URL}/api/archivos/leer-contenido`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ruta: archivo.ruta_completa })
    })
    
    const data = await response.json()
    console.log('📥 Respuesta del servidor:', data)
    
    if (!data.contenido) {
      throw new Error('El servidor no devolvió contenido')
    }
    
    // Crear objeto con contenido
    const nuevoArchivo = {
      ...archivo,
      contenido: data.contenido,
      vista_previa: data.contenido.substring(0, 200) + 
                    (data.contenido.length > 200 ? '...' : '')
    }
    
    console.log('✅ Archivo adjuntado con contenido de', 
                data.contenido.length, 'caracteres')
    
    // Evitar duplicados
    const yaExiste = archivosContextoChat.some(
      a => a.ruta_completa === archivo.ruta_completa
    )
    
    if (!yaExiste) {
      setArchivosContextoChat(prev => [...prev, nuevoArchivo])
      setMensaje({
        tipo: 'success',
        texto: `📎 Archivo "${archivo.nombre}" adjuntado al contexto`
      })
    } else {
      setMensaje({
        tipo: 'info',
        texto: 'Este archivo ya está en el contexto'
      })
    }
  } catch (error) {
    setMensaje({
      tipo: 'error',
      texto: `❌ Error al leer archivo: ${error.message}`
    })
  }
}
```

**Backend Endpoint:** `POST /api/archivos/leer-contenido`

**Proceso:**
1. Frontend envía `ruta_completa` del archivo
2. Backend detecta si es práctica mediante ruta virtual o archivo JSON
3. Para prácticas:
   - Lee `practicas.json` de la carpeta
   - Busca la práctica por índice (si es ruta virtual)
   - Formatea contenido con preguntas y respuestas
   - Retorna texto formateado
4. Frontend almacena contenido en `archivosContextoChat`

**Formato del Contenido (para prácticas):**
```
# 📝 Práctica: [Título]

📅 Creada: [Fecha]
📁 Carpeta: [Nombre carpeta]
🎯 Tipo: documento/carpeta

## 📊 Estadísticas
- Flashcards: X
- MCQ: Y
- Verdadero/Falso: Z
...

## ❓ Preguntas

### Pregunta 1
**Tipo:** flashcard
**Pregunta:** ¿Qué es...?
**Respuesta:** Es...
**Puntos:** 10
```

---

## 📝 RESOLVER PRÁCTICA

### Modal de Práctica Activa

Cuando se genera o abre una práctica, se activa el modal de examen:

```javascript
// En confirmarGenerarPractica() después de recibir respuesta:

setEsPractica(true);           // Marca que es práctica (no examen)
setExamenActivo(true);         // Activa el modal
setPreguntasExamen(data.preguntas || []);  // Carga preguntas
setRespuestasUsuario({});      // Limpia respuestas
setExamenCompletado(false);    // Estado inicial
setModalExamenAbierto(true);   // Abre el modal
```

**Estados Relevantes:**
```javascript
const [esPractica, setEsPractica] = useState(false);
const [examenActivo, setExamenActivo] = useState(false);
const [preguntasExamen, setPreguntasExamen] = useState([]);
const [respuestasUsuario, setRespuestasUsuario] = useState({});
const [examenCompletado, setExamenCompletado] = useState(false);
```

### Renderizado de Preguntas

Las preguntas se renderizan según su tipo:

**Flashcard:**
```jsx
{pregunta.tipo === 'flashcard' && (
  <div className="flashcard-container">
    <div className="flashcard-pregunta">
      {pregunta.pregunta}
    </div>
    <input
      type="text"
      placeholder="Tu respuesta..."
      onChange={(e) => setRespuestasUsuario({
        ...respuestasUsuario,
        [idx]: e.target.value
      })}
    />
  </div>
)}
```

**MCQ (Opción Múltiple):**
```jsx
{pregunta.tipo === 'mcq' && (
  <div className="mcq-opciones">
    {pregunta.opciones.map((opcion, optIdx) => (
      <label key={optIdx}>
        <input
          type="checkbox"
          checked={respuestasUsuario[idx]?.includes(optIdx)}
          onChange={(e) => {
            const seleccionadas = respuestasUsuario[idx] || [];
            setRespuestasUsuario({
              ...respuestasUsuario,
              [idx]: e.target.checked
                ? [...seleccionadas, optIdx]
                : seleccionadas.filter(i => i !== optIdx)
            });
          }}
        />
        {opcion}
      </label>
    ))}
  </div>
)}
```

**Cloze (Relleno de Huecos):**
```jsx
{pregunta.tipo === 'cloze' && (
  <div className="cloze-container">
    {renderizarTextoCloze(
      pregunta.metadata?.text_with_gaps,
      pregunta.metadata?.answers,
      idx
    )}
  </div>
)}
```

### Envío de Respuestas

Al hacer clic en "Enviar Práctica":

```javascript
const enviarPractica = () => {
  // Marcar como completada
  setExamenCompletado(true);
  
  // Calcular resultados
  const totalPreguntas = preguntasExamen.length;
  let correctas = 0;
  
  preguntasExamen.forEach((pregunta, idx) => {
    const respuesta = respuestasUsuario[idx];
    // Evaluar según tipo de pregunta
    if (esRespuestaCorrecta(pregunta, respuesta)) {
      correctas++;
    }
  });
  
  const porcentaje = (correctas / totalPreguntas) * 100;
  
  setResultadoExamen({
    correctas,
    incorrectas: totalPreguntas - correctas,
    porcentaje,
    total: totalPreguntas
  });
  
  // Mostrar botones de evaluación para repetición espaciada
  // (Fácil, Medio, Difícil)
};
```

---

## 🔁 EVALUACIÓN Y REPETICIÓN ESPACIADA

### Función: `evaluarPractica()`
**Ubicación:** `App.jsx` línea ~9191

```javascript
const evaluarPractica = async (idPractica, dificultad) => {
  // Cargar práctica actual
  const practicasActuales = await getDatos('practicas');
  const practicaActualizada = practicasActuales.find(p => p.id === idPractica);
  
  if (practicaActualizada) {
    // Calcular próxima revisión usando algoritmo SM-2
    const practicaConNuevosDatos = calcularProximaRevision(
      practicaActualizada, 
      dificultad
    );
    
    // 🔥 GUARDAR EN CARPETA CORRESPONDIENTE
    await guardarPracticaEnCarpeta(practicaConNuevosDatos);
    
    // Actualizar estado local
    const practicasActualizadas = practicasActuales.map(p => 
      p.id === idPractica ? practicaConNuevosDatos : p
    );
    setPracticas(practicasActualizadas);
    
    console.log('🎯 Práctica evaluada:', {
      dificultad,
      practica: practicaConNuevosDatos
    });
    
    setMensaje({
      tipo: 'success',
      texto: `✅ Práctica evaluada: ${
        dificultad === 'facil' ? 'Excelente' : 
        dificultad === 'medio' ? 'Bien' : 
        'Necesita más práctica'
      }`
    });
  }
};
```

### Función: `calcularProximaRevision()`

Implementa el algoritmo **SM-2 (SuperMemo 2)** para repetición espaciada:

```javascript
const calcularProximaRevision = (item, evaluacion) => {
  const ahora = new Date();
  
  // Inicializar valores si es primera revisión
  let facilidad = item.facilidad || 2.5;
  let intervalo = item.intervalo || 0;
  let repeticiones = item.repeticiones || 0;
  
  // Ajustar facilidad según evaluación
  if (evaluacion === 'facil') {
    facilidad += 0.1;
    repeticiones++;
  } else if (evaluacion === 'medio') {
    // Mantener facilidad
    repeticiones++;
  } else { // dificil
    facilidad -= 0.2;
    repeticiones = 0;  // Reiniciar contador
    intervalo = 0;
  }
  
  // Limitar facilidad entre 1.3 y 2.5
  facilidad = Math.max(1.3, Math.min(2.5, facilidad));
  
  // Calcular nuevo intervalo
  if (repeticiones === 0) {
    intervalo = 0;  // Hoy mismo
  } else if (repeticiones === 1) {
    intervalo = 1;  // Mañana
  } else if (repeticiones === 2) {
    intervalo = 6;  // En 6 días
  } else {
    intervalo = Math.round(intervalo * facilidad);
  }
  
  // Calcular fecha de próxima revisión
  const proximaRevision = new Date(ahora);
  proximaRevision.setDate(proximaRevision.getDate() + intervalo);
  
  // Registrar en historial
  const historialRevisiones = item.historialRevisiones || [];
  historialRevisiones.push({
    fecha: ahora.toISOString(),
    evaluacion: evaluacion,
    intervaloSiguiente: intervalo
  });
  
  // Retornar item actualizado
  return {
    ...item,
    facilidad,
    intervalo,
    repeticiones,
    proximaRevision: proximaRevision.toISOString(),
    ultimaRevision: ahora.toISOString(),
    historialRevisiones
  };
};
```

**Valores de Evaluación:**
- `facil`: Respuesta correcta y fácil → Aumenta facilidad, incrementa intervalo
- `medio`: Respuesta correcta con esfuerzo → Mantiene facilidad
- `dificil`: Respuesta incorrecta → Reduce facilidad, reinicia contador

**Campos Agregados al Item:**
```javascript
{
  facilidad: 2.5,              // Factor de facilidad (1.3 - 2.5)
  intervalo: 6,                // Días hasta próxima revisión
  repeticiones: 3,             // Número de repeticiones exitosas
  proximaRevision: "2024-12-02T10:00:00.000Z",  // Fecha ISO
  ultimaRevision: "2024-11-26T10:00:00.000Z",   // Fecha ISO
  historialRevisiones: [
    {
      fecha: "2024-11-20T10:00:00.000Z",
      evaluacion: "facil",
      intervaloSiguiente: 1
    },
    {
      fecha: "2024-11-21T10:00:00.000Z",
      evaluacion: "medio",
      intervaloSiguiente: 6
    }
  ]
}
```

---

## 📅 VISTA DE REPETICIÓN ESPACIADA

En la pestaña "Repetición Espaciada" se muestran todas las prácticas agendadas:

### Agrupación por Fecha

```javascript
// Filtrar items con próxima revisión
const itemsConRevision = todosLosItems.filter(item => item.proximaRevision);

// Agrupar por fecha
const itemsPorFecha = itemsConRevision.reduce((acc, item) => {
  const fecha = new Date(item.proximaRevision);
  const fechaKey = fecha.toLocaleDateString('es-ES', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
  
  if (!acc[fechaKey]) {
    acc[fechaKey] = {
      fecha: fecha,
      fechaTexto: fechaKey,
      items: []
    };
  }
  
  acc[fechaKey].items.push(item);
  return acc;
}, {});

// Convertir a array y ordenar por fecha
const diasRepaso = Object.values(itemsPorFecha)
  .sort((a, b) => a.fecha - b.fecha);
```

### Renderizado de Items Agendados

```jsx
{diasRepaso.map((dia, idx) => {
  const esHoy = new Date().toDateString() === dia.fecha.toDateString();
  const diasHasta = Math.ceil((dia.fecha - new Date()) / (1000 * 60 * 60 * 24));
  
  return (
    <div key={idx} className={`dia-repaso ${esHoy ? 'dia-repaso-hoy' : ''}`}>
      <div className="dia-repaso-header">
        <h3>{esHoy ? '⏰ HOY' : dia.fechaTexto}</h3>
        {!esHoy && (
          <span className="dias-hasta">
            En {diasHasta} día{diasHasta !== 1 ? 's' : ''}
          </span>
        )}
        <span className="total-items">
          {dia.items.length} item{dia.items.length !== 1 ? 's' : ''}
        </span>
      </div>
      
      <div className="items-repaso-lista">
        {dia.items.map((item, itemIdx) => (
          <div 
            key={itemIdx} 
            className="item-repaso item-repaso-clickable"
            onClick={() => setItemMapaRepeticion(item)}
          >
            <span className="item-repaso-tipo">{item.tipo}</span>
            <span className="item-repaso-titulo">
              {item.titulo || 'Sin título'}
            </span>
            <div className="item-repaso-info">
              <span className="item-repaso-intervalo">
                🔁 {intervaloTexto}
              </span>
              <span className="item-repaso-estado">
                {item.repeticiones || 0}× visto
              </span>
              <span className="item-repaso-facilidad">
                ⚡ {(item.facilidad || 2.5).toFixed(1)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
})}
```

### Modal de Detalle del Item

Al hacer clic en un item se abre un modal con:

1. **Estadísticas:**
   - Repeticiones
   - Facilidad
   - Intervalo actual
   - Próxima revisión

2. **Preguntas a Repasar** (primeras 5):
```jsx
{item.preguntas && item.preguntas.length > 0 && (
  <div className="mapa-preguntas-repaso">
    <h4>📋 Preguntas a Repasar ({item.preguntas.length})</h4>
    <div className="preguntas-lista-preview">
      {item.preguntas.slice(0, 5).map((pregunta, idx) => (
        <div key={idx} className="pregunta-preview-item">
          <span className="pregunta-numero">#{idx + 1}</span>
          <div className="pregunta-info">
            <span className="pregunta-tipo">
              [{pregunta.tipo?.toUpperCase() || 'PREGUNTA'}]
            </span>
            <span className="pregunta-texto">
              {pregunta.pregunta?.substring(0, 80) || 'Sin texto'}
              {pregunta.pregunta?.length > 80 ? '...' : ''}
            </span>
            {pregunta.puntos && (
              <span className="pregunta-puntos">{pregunta.puntos} pts</span>
            )}
          </div>
        </div>
      ))}
      {item.preguntas.length > 5 && (
        <div className="preguntas-mas">
          + {item.preguntas.length - 5} pregunta(s) más
        </div>
      )}
    </div>
  </div>
)}
```

3. **Historial de Repasos** (timeline):
   - Fecha de creación
   - Cada revisión con evaluación
   - Próxima revisión programada

---

## 🔄 Ciclo Completo de Vida de una Práctica

```
1. GENERACIÓN
   ├─ Usuario hace clic en "🧑‍💻 Generar Práctica"
   ├─ Se abre modal de configuración
   ├─ Usuario selecciona tipos y cantidad
   ├─ Frontend → POST /api/generar_practica
   ├─ Backend genera con IA
   ├─ Frontend recibe preguntas
   └─ Se guarda en practicas.json

2. GUARDADO INICIAL
   ├─ Objeto práctica con:
   │  ├─ id, ruta, carpeta
   │  ├─ preguntas[]
   │  ├─ respuestas: {}
   │  ├─ completada: false
   │  └─ stats{}
   └─ Se escribe en extracciones/[carpeta]/practicas.json

3. VISUALIZACIÓN EN PESTAÑA
   ├─ Usuario abre pestaña "✅ Prácticas" en chatbot
   ├─ Frontend → GET /api/archivos/explorar?tipo=practicas
   ├─ Backend lista practicas.json de cada carpeta
   ├─ Frontend muestra árbol navegable
   └─ Usuario puede adjuntar al contexto del chat

4. RESOLUCIÓN
   ├─ Usuario abre práctica (desde lista o generación nueva)
   ├─ Se abre modal con preguntas
   ├─ Usuario responde cada pregunta
   ├─ Frontend almacena en respuestasUsuario{}
   └─ Usuario hace clic en "Enviar"

5. EVALUACIÓN AUTOMÁTICA
   ├─ Frontend compara respuestas con correctas
   ├─ Calcula porcentaje de acierto
   ├─ Muestra resultado
   └─ Presenta botones: Fácil / Medio / Difícil

6. REPETICIÓN ESPACIADA
   ├─ Usuario evalúa dificultad
   ├─ Frontend → evaluarPractica(id, dificultad)
   ├─ Se ejecuta algoritmo SM-2
   ├─ Se calculan:
   │  ├─ Nueva facilidad
   │  ├─ Nuevo intervalo
   │  ├─ Próxima revisión
   │  └─ Se registra en historial
   ├─ Frontend → POST /datos/practicas/carpeta
   └─ Backend actualiza practicas.json

7. SEGUIMIENTO
   ├─ Práctica aparece en "Repetición Espaciada"
   ├─ Agrupada por fecha de próxima revisión
   ├─ Usuario puede ver:
   │  ├─ Estadísticas (repeticiones, facilidad, intervalo)
   │  ├─ Preguntas a repasar
   │  └─ Historial de repasos
   └─ Al llegar la fecha, se repite desde paso 4
```

---

## 📊 Estructura de Datos Completa

### Práctica Recién Generada
```json
{
  "id": "practica_1732654321000",
  "ruta": "C:\\...\\extracciones\\Platzi\\documento.pdf",
  "carpeta": "Platzi",
  "tipo": "documento",
  "prompt": "",
  "preguntas": [
    {
      "tipo": "flashcard",
      "pregunta": "¿Qué es Python?",
      "respuesta": "Un lenguaje de programación de alto nivel",
      "puntos": 10,
      "dificultad": 1,
      "tags": ["python", "programación"],
      "metadata": {
        "hint": "Piensa en lenguajes interpretados"
      }
    },
    {
      "tipo": "mcq",
      "pregunta": "¿Cuáles son características de Python?",
      "opciones": [
        "Interpretado",
        "Compilado",
        "Tipado dinámico",
        "Tipado estático"
      ],
      "respuestas_correctas": [0, 2],
      "puntos": 15,
      "explicacion": "Python es interpretado y usa tipado dinámico"
    }
  ],
  "respuestas": {},
  "fecha": "2024-11-26T10:30:00.000Z",
  "completada": false,
  "stats": {
    "flashcards": 5,
    "mcq": 3,
    "verdadero_falso": 2
  }
}
```

### Práctica Después de Primera Evaluación
```json
{
  "id": "practica_1732654321000",
  "...": "...",
  "completada": true,
  "facilidad": 2.5,
  "intervalo": 1,
  "repeticiones": 1,
  "proximaRevision": "2024-11-27T10:30:00.000Z",
  "ultimaRevision": "2024-11-26T10:30:00.000Z",
  "estadoRevision": "en_progreso",
  "historialRevisiones": [
    {
      "fecha": "2024-11-26T10:30:00.000Z",
      "evaluacion": "facil",
      "intervaloSiguiente": 1
    }
  ]
}
```

### Práctica Después de Múltiples Repasos
```json
{
  "id": "practica_1732654321000",
  "...": "...",
  "facilidad": 2.6,
  "intervalo": 30,
  "repeticiones": 5,
  "proximaRevision": "2024-12-26T10:30:00.000Z",
  "ultimaRevision": "2024-11-26T10:30:00.000Z",
  "estadoRevision": "dominada",
  "historialRevisiones": [
    {
      "fecha": "2024-11-26T10:30:00.000Z",
      "evaluacion": "facil",
      "intervaloSiguiente": 1
    },
    {
      "fecha": "2024-11-27T10:30:00.000Z",
      "evaluacion": "medio",
      "intervaloSiguiente": 6
    },
    {
      "fecha": "2024-12-03T10:30:00.000Z",
      "evaluacion": "facil",
      "intervaloSiguiente": 15
    },
    {
      "fecha": "2024-12-18T10:30:00.000Z",
      "evaluacion": "facil",
      "intervaloSiguiente": 30
    }
  ]
}
```

---

## 🎨 Estilos y Temas

Las prácticas utilizan tema oscuro consistente con el resto de la aplicación:

```css
/* Modal de preguntas */
.mapa-preguntas-repaso {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
}

/* Timeline de historial */
.historial-timeline {
  position: relative;
  padding-left: 2rem;
}

.historial-timeline::before {
  content: '';
  position: absolute;
  left: 14px;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(to bottom, 
    rgba(59, 130, 246, 0.5) 0%,
    rgba(148, 163, 184, 0.3) 50%,
    rgba(59, 130, 246, 0.5) 100%
  );
}

/* Dots con animación pulse para próximas revisiones */
.historial-item.proxima .historial-dot {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.2);
  animation: pulse-dot 2s infinite;
}
```

---

## 🧩 Integración con Otros Componentes

### Relación con Flashcards
- Las flashcards individuales también usan repetición espaciada
- Comparten la misma función `calcularProximaRevision()`
- Se muestran en la misma vista de "Repetición Espaciada"

### Relación con Exámenes
- Exámenes y prácticas comparten el mismo modal de resolución
- Se diferencian por el flag `esPractica`
- Los exámenes no tienen repetición espaciada (son evaluaciones únicas)

### Relación con Notas
- Las prácticas pueden generarse desde documentos
- Las notas pueden convertirse en flashcards
- Ambas se organizan por carpetas en `extracciones/`

---

## 🔧 Funciones de Utilidad

### Normalización de Rutas
```javascript
// Remover "extracciones\" de la ruta
if (carpeta.includes('extracciones\\')) {
  const partes = carpeta.split('extracciones\\');
  carpeta = partes[partes.length - 1] || '';
} else if (carpeta.includes('extracciones/')) {
  const partes = carpeta.split('extracciones/');
  carpeta = partes[partes.length - 1] || '';
}
```

### Formateo de Intervalos
```javascript
const intervaloTexto = intervalo ? 
  (intervalo === 1 ? '1 día' :
   intervalo < 7 ? `${intervalo} días` :
   intervalo < 30 ? `${Math.round(intervalo / 7)} semanas` :
   `${Math.round(intervalo / 30)} meses`) : 
  'Primera vez';
```

### Cálculo de Días Hasta Revisión
```javascript
const diasHasta = Math.ceil(
  (new Date(item.proximaRevision) - new Date()) / (1000 * 60 * 60 * 24)
);
```

---

## 🎓 Resumen de Estados y Props Clave

### Estados de Práctica
```javascript
const [practicas, setPracticas] = useState([]);
const [esPractica, setEsPractica] = useState(false);
const [examenActivo, setExamenActivo] = useState(false);
const [preguntasExamen, setPreguntasExamen] = useState([]);
const [respuestasUsuario, setRespuestasUsuario] = useState({});
const [examenCompletado, setExamenCompletado] = useState(false);
const [resultadoExamen, setResultadoExamen] = useState(null);
```

### Estados del Explorador (Pestaña)
```javascript
const [tipoExploradorChat, setTipoExploradorChat] = useState('recientes');
const [carpetasExploradorChat, setCarpetasExploradorChat] = useState([]);
const [rutaExploradorChat, setRutaExploradorChat] = useState('');
const [archivosRecientes, setArchivosRecientes] = useState([]);
const [archivosContextoChat, setArchivosContextoChat] = useState([]);
const [cargandoArchivos, setCargandoArchivos] = useState(false);
```

### Estados del Modal de Repetición
```javascript
const [itemMapaRepeticion, setItemMapaRepeticion] = useState(null);
const [modalMapaAbierto, setModalMapaAbierto] = useState(false);
```

---

Esta documentación completa proporciona una visión exhaustiva de cómo funcionan las prácticas en todo el sistema, desde su generación hasta su seguimiento en el tiempo mediante repetición espaciada.

---

# 🔄 ACTUALIZACIÓN: Normalización Automática para Spaced Repetition

## 📅 Fecha: 26 de Noviembre de 2025

Se ha implementado un sistema de **normalización automática** que garantiza que **TODAS las preguntas** del sistema (prácticas, exámenes, flashcards) tengan los campos necesarios para funcionar con repetición espaciada, sin importar su origen o antigüedad.

### ✅ Campos Agregados Automáticamente

Cada pregunta ahora incluye estos campos (si no los tiene ya):

```json
{
  "id": "tipo_timestamp_hash",
  "ease_factor": 2.5,
  "interval": 0,
  "repetitions": 0,
  "last_review": null,
  "next_review": null,
  "state": "new"
}
```

### 🎯 Puntos de Aplicación

La normalización se aplica automáticamente en:

1. ✅ **POST /api/generar_practica** - Al generar nueva práctica
2. ✅ **POST /api/generar-examen** - Al generar nuevo examen
3. ✅ **POST /datos/practicas/carpeta** - Al guardar práctica (nueva + existentes)
4. ✅ **GET /datos/practicas** - Al cargar prácticas (migración en tiempo real)
5. ✅ **POST /datos/examenes/carpeta** - Al guardar examen (nuevo + existentes)
6. ✅ **GET /datos/examenes** - Al cargar exámenes (migración en tiempo real)

### 🛡️ Garantías

- ✅ **No sobrescribe** campos existentes
- ✅ **Preserva** toda la estructura original
- ✅ **Genera ID único** si falta
- ✅ **Compatible** con frontend
- ✅ **Sin migraciones manuales** requeridas

### 📚 Documentación Completa

Ver: [`NORMALIZACION_SPACED_REPETITION.md`](./NORMALIZACION_SPACED_REPETITION.md)

**Resultado:** Sistema unificado donde toda pregunta está lista para aprendizaje espaciado desde el momento de su creación o primera carga.

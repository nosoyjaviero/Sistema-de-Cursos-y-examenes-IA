# 📚 EXAMINATOR - Documentación Completa del Sistema

## 🎯 ¿Qué es Examinator?

**Examinator** es un **sistema completo de aprendizaje inteligente** que utiliza **Inteligencia Artificial local (Ollama + GPU)** para transformar documentos PDF en experiencias de aprendizaje interactivas. El sistema genera automáticamente exámenes, prácticas y flashcards basándose en el contenido que tú proporcionas.

### Propósito Principal
Ayudar a estudiantes y educadores a:
- Extraer conocimiento de documentos PDF/TXT
- Generar evaluaciones automáticas con IA
- Estudiar con flashcards interactivas
- Practicar con exámenes adaptativos
- Chatear con un asistente IA que conoce tus documentos
- Organizar contenido educativo en carpetas

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    EXAMINATOR SYSTEM                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   FRONTEND WEB   │  ←────→ │   BACKEND API    │         │
│  │   (React/Vite)   │  HTTP   │   (FastAPI)      │         │
│  │   Port: 5173     │         │   Port: 8000     │         │
│  └──────────────────┘         └──────────────────┘         │
│           │                            │                     │
│           │                            ↓                     │
│           │                   ┌────────────────┐            │
│           │                   │  OLLAMA SERVER │            │
│           │                   │  (IA Local)    │            │
│           │                   │  Port: 11434   │            │
│           │                   │  GPU: NVIDIA   │            │
│           │                   └────────────────┘            │
│           │                            │                     │
│           └────────────────────────────┘                     │
│                          ↓                                   │
│                 ┌──────────────────┐                        │
│                 │  FILE SYSTEM     │                        │
│                 │  extracciones/   │                        │
│                 │  chats_historial/│                        │
│                 │  examenes/       │                        │
│                 └──────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Stack Tecnológico

**Backend (Python):**
- `FastAPI` - API REST moderna y rápida
- `Ollama` - Motor de IA local con GPU (llama3.1, deepseek-r1, qwen)
- `llama-cpp-python` - Fallback para modelos GGUF
- `pypdf` - Extracción de texto de PDFs
- `requests` - Comunicación con Ollama

**Frontend (React):**
- `React 18` + `Vite` - Framework moderno
- `KaTeX` - Renderizado de matemáticas (LaTeX)
- `react-katex` - Componentes LaTeX para React
- CSS modular con diseño responsive

**IA/ML:**
- Modelos Ollama locales (GPU NVIDIA)
- Generación de preguntas inteligentes
- Evaluación automática de respuestas
- Búsqueda web contextual

---

## 📂 Estructura de Archivos

```
Examinator/
│
├── 🐍 BACKEND (Python)
│   ├── api_server.py                 # API FastAPI principal (3600+ líneas)
│   ├── examinator.py                 # Extractor de PDFs
│   ├── generador_unificado.py        # Generador IA unificado (Ollama + GGUF)
│   ├── generador_dos_pasos.py        # Generador avanzado 2 pasos
│   ├── generador_examenes.py         # Motor de exámenes
│   ├── cursos_db.py                  # Gestor de carpetas/documentos
│   ├── busqueda_web.py               # Búsqueda y resumen web
│   ├── config.json                   # Configuración del modelo IA
│   └── requirements.txt              # Dependencias Python
│
├── ⚛️ FRONTEND (React)
│   └── examinator-web/
│       ├── src/
│       │   ├── App.jsx               # Aplicación principal (19000+ líneas)
│       │   ├── App.css               # Estilos principales
│       │   ├── components/           # Componentes React
│       │   │   ├── MathEditor.jsx    # Editor de matemáticas
│       │   │   ├── ChemEditor.jsx    # Editor de química
│       │   │   ├── PhysicsEditor.jsx # Editor de física
│       │   │   └── ... (más editores)
│       │   └── utils/                # Utilidades
│       ├── package.json              # Dependencias Node.js
│       └── vite.config.js            # Configuración Vite
│
├── 📁 DATOS
│   ├── extracciones/                 # Carpetas y documentos .txt
│   │   ├── Platzi/                   # Ejemplo: curso de Platzi
│   │   ├── Biologia/                 # Ejemplo: materiales biología
│   │   └── [tus carpetas]/           # Estructura personalizada
│   │
│   ├── chats_historial/              # Conversaciones guardadas
│   │   ├── chat_1763291321.json      
│   │   ├── Biologia/                 # Chats por carpeta
│   │   └── Tonteras/                 
│   │
│   ├── examenes/                     # Exámenes generados y resultados
│   │   └── Platzi/                   
│   │       └── resultados_examenes/  # Calificaciones guardadas
│   │
│   └── logs_practicas_detallado/     # Logs de generación IA
│
└── 📜 SCRIPTS
    ├── iniciar_todo.ps1              # Inicia backend + frontend + Ollama
    ├── iniciar_ollama.ps1            # Solo Ollama
    └── descargar_modelo.py           # Descarga modelos Ollama

```

---

## 🔥 Funcionalidades Principales

### 1. 📄 Extracción de Documentos PDF

**Archivo:** `examinator.py`

**Flujo:**
1. Usuario sube un PDF desde la interfaz web
2. `api_server.py` recibe el archivo (endpoint `/api/extraer-pdf`)
3. Llama a `obtener_texto()` de `examinator.py`
4. Extrae texto página por página
5. Limpia y normaliza el texto
6. Guarda `.txt` en carpeta especificada

**Características:**
- ✅ Limpieza inteligente de texto (preserva formato)
- ✅ División automática en secciones/capítulos
- ✅ Soporte para PDFs largos con progreso
- ✅ Guardado organizado por carpetas

**Código clave:**
```python
def obtener_texto(path_pdf: str, limpiar: bool = True) -> str:
    """Extrae texto de PDF con limpieza opcional"""
    reader = PdfReader(path_pdf)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    
    if limpiar:
        texto = limpiar_texto(texto)
    
    return texto
```

---

### 2. 🤖 Chatbot Inteligente con Contexto

**Archivo:** `api_server.py` - Endpoint `/api/chat`

**Flujo:**
1. Usuario escribe pregunta en el chat
2. Frontend envía: `{mensaje, historial, archivo_contexto, busqueda_web}`
3. Backend carga contenido del documento (si hay contexto)
4. Construye prompt con:
   - Historial de conversación
   - Contenido del documento
   - Resultados de búsqueda web (opcional)
5. Envía a Ollama con streaming
6. Respuesta se envía en tiempo real al frontend

**Características:**
- ✅ Streaming de respuestas (respuesta en vivo)
- ✅ Contexto de documentos (el chatbot "lee" tus PDFs)
- ✅ Búsqueda web integrada (DuckDuckGo)
- ✅ Historial persistente (guarda conversaciones)
- ✅ Organización por carpetas de proyecto

**Código clave:**
```python
@app.post("/api/chat")
async def chat(data: dict):
    mensaje = data.get("mensaje")
    historial = data.get("historial", [])
    archivo_contexto = data.get("archivo_contexto")
    
    # Cargar contenido del documento
    if archivo_contexto:
        contenido = Path(archivo_contexto).read_text(encoding='utf-8')
        prompt = f"Documento: {contenido}\n\nPregunta: {mensaje}"
    else:
        prompt = mensaje
    
    # Streaming a Ollama
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": "llama31-local", "messages": [...], "stream": True}
    )
    
    for line in response.iter_lines():
        yield line
```

---

### 3. 📝 Generación de Exámenes/Prácticas

**Archivos:** 
- `generador_unificado.py` - Adaptador Ollama/GGUF
- `generador_dos_pasos.py` - Generador avanzado

**Tipos de Preguntas:**
1. **Opción Múltiple** - 4 opciones (A, B, C, D)
2. **Verdadero/Falso** - Con justificación
3. **Respuesta Corta** - 2-4 líneas
4. **Desarrollo** - Análisis profundo

**Flujo de Generación:**
1. Usuario selecciona documento
2. Configura cantidad de preguntas por tipo
3. Backend lee el documento completo
4. Divide texto en chunks (fragmentos)
5. Para cada tipo de pregunta:
   - Construye prompt especializado
   - Envía a Ollama (llama3.1/deepseek-r1)
   - Parsea respuesta JSON
   - Valida formato
6. Retorna examen completo

**Prompt Example (Opción Múltiple):**
```python
prompt = f"""Genera {num_preguntas} preguntas de opción múltiple basadas en este texto:

{fragmento_texto}

Formato JSON:
{{
  "preguntas": [
    {{
      "pregunta": "¿Cuál es...?",
      "opciones": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "respuesta_correcta": "A",
      "explicacion": "Porque..."
    }}
  ]
}}
"""
```

**Características:**
- ✅ Generación por bloques (memoria eficiente)
- ✅ Logs detallados (debugging)
- ✅ Sistema de 2 pasos (generación + validación)
- ✅ Puntuación configurable
- ✅ Guardado de exámenes para reutilizar

---

### 4. ✅ Evaluación Automática

**Archivo:** `generador_unificado.py` - Método `evaluar_respuesta()`

**Flujo:**
1. Usuario completa examen
2. Frontend envía respuestas: `/api/evaluar-examen`
3. Para cada pregunta:
   - Si es opción múltiple/V-F → Comparación directa
   - Si es desarrollo/corta → IA evalúa (prompt especializado)
4. IA genera:
   - Puntos obtenidos (0-10)
   - Feedback detallado
   - Correcciones
5. Backend calcula calificación final
6. Guarda resultado en JSON

**Prompt de Evaluación (Desarrollo):**
```python
prompt_eval = f"""Evalúa esta respuesta sobre una escala de 0 a {puntos_max}:

PREGUNTA: {pregunta.pregunta}
RESPUESTA CORRECTA: {pregunta.respuesta_correcta}
RESPUESTA DEL ESTUDIANTE: {respuesta_usuario}

Devuelve JSON:
{{
  "puntos_obtenidos": 7.5,
  "feedback": "La respuesta es correcta pero...",
  "aspectos_bien": ["Menciona X", "Explica Y"],
  "aspectos_mejorar": ["Falta profundizar Z"]
}}
"""
```

**Características:**
- ✅ Evaluación inteligente (no solo keyword matching)
- ✅ Feedback constructivo
- ✅ Puntuación granular
- ✅ Guardado de resultados con timestamp

---

### 5. 🃏 Sistema de Flashcards Avanzado

**Archivo:** `api_server.py` - Endpoints `/api/flashcards/*`

**Estructura de Flashcard:**
```javascript
{
  id: "uuid-único",
  tipo: "pregunta_respuesta", // o "terminologia", "formula", "codigo"
  frente: "¿Qué es un algoritmo?",
  reverso: "Secuencia finita de instrucciones...",
  latex: true,  // Renderiza con KaTeX
  archivos: [   // Imágenes/PDFs en base64
    {
      nombre: "diagrama.png",
      tipo: "image/png",
      url: "data:image/png;base64,iVBOR...",
      base64: "iVBOR..."
    }
  ],
  etiquetas: ["algoritmos", "programacion", "fundamentos"],
  dificultad: "media",
  fecha_creacion: "2025-11-22T10:30:00",
  fecha_ultima_revision: "2025-11-22T14:00:00"
}
```

**Funcionalidades:**
- ✅ Renderizado LaTeX (fórmulas matemáticas)
- ✅ Adjuntos multimedia (imágenes/PDF en base64)
- ✅ Sistema de etiquetas
- ✅ Filtrado por tipo/dificultad
- ✅ Exportación/importación JSON
- ✅ Asistente IA para generar flashcards automáticamente

**Asistente IA de Flashcards:**
```python
@app.post("/api/flashcards/asistente")
async def asistente_flashcards(data: dict):
    """Genera flashcards automáticamente desde texto"""
    texto = data.get("texto")
    tipo = data.get("tipo", "pregunta_respuesta")
    cantidad = data.get("cantidad", 5)
    
    prompt = f"""Genera {cantidad} flashcards de tipo {tipo} desde:
    {texto}
    
    Formato JSON con frente/reverso"""
    
    flashcards = generador_unificado.generar_flashcards(prompt)
    return {"flashcards": flashcards}
```

---

### 6. 📊 Sistema de Carpetas y Organización

**Archivo:** `cursos_db.py` - Clase `CursosDatabase`

**Estructura de Datos:**
```
extracciones/
├── Universidad/
│   ├── Semestre_1/
│   │   ├── Calculo/
│   │   │   ├── tema1_limites.txt
│   │   │   └── tema2_derivadas.txt
│   │   └── Fisica/
│   └── Semestre_2/
├── Platzi/
│   ├── Python_Basico/
│   └── JavaScript_Profesional/
└── Libros/
```

**Operaciones:**
- ✅ `listar_carpetas(ruta)` - Lista subcarpetas
- ✅ `listar_documentos(ruta)` - Lista .txt en carpeta
- ✅ `crear_carpeta(ruta, nombre)` - Crea nueva carpeta
- ✅ `renombrar_carpeta(ruta, nuevo_nombre)`
- ✅ `eliminar_carpeta(ruta)` - Solo si está vacía
- ✅ `mover_carpeta(origen, destino)`
- ✅ `buscar_documentos(query)` - Búsqueda global

**Ventajas:**
- Sin base de datos (solo filesystem)
- Estructura flexible
- Puedes editar directamente en Windows Explorer
- Backup fácil (copiar carpeta)

---

## 🔧 Configuración y Setup

### Requisitos del Sistema

**Hardware:**
- GPU NVIDIA (recomendado para mejor rendimiento)
- 8GB RAM mínimo (16GB recomendado)
- 10GB espacio disco (para modelos IA)

**Software:**
- Windows 10/11
- Python 3.10+
- Node.js 18+
- Ollama (motor IA local)

### Instalación

**1. Instalar Ollama:**
```powershell
# Descargar de https://ollama.ai
# Instalar y ejecutar
ollama serve

# Descargar modelos
ollama pull llama3.1:8b
ollama pull deepseek-r1:7b
ollama pull qwen2.5:7b
```

**2. Backend Python:**
```powershell
cd Examinator
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**3. Frontend React:**
```powershell
cd examinator-web
npm install
```

**4. Iniciar Sistema:**
```powershell
# Opción 1: Script automático
.\iniciar_todo.ps1

# Opción 2: Manual
# Terminal 1: Backend
python api_server.py

# Terminal 2: Frontend
cd examinator-web
npm run dev

# Terminal 3: Ollama
ollama serve
```

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Ollama: http://localhost:11434

---

## 🎮 Uso del Sistema

### Flujo Completo de Trabajo

**Paso 1: Subir Documento**
1. Ir a "Mis Carpetas"
2. Crear carpeta (ej: "Matematicas")
3. Subir PDF
4. Sistema extrae texto automáticamente

**Paso 2: Estudiar con Chat**
1. Ir a "Chatbot"
2. Seleccionar documento como contexto
3. Hacer preguntas sobre el contenido
4. IA responde basándose en el documento

**Paso 3: Practicar con Exámenes**
1. Ir a "Exámenes"
2. Seleccionar documento
3. Configurar tipos de preguntas:
   - 10 múltiples
   - 5 verdadero/falso
   - 3 desarrollo
4. Generar examen
5. Responder preguntas
6. Ver calificación y feedback

**Paso 4: Repasar con Flashcards**
1. Ir a "Flashcards"
2. Crear carpeta para tema
3. Generar flashcards automáticamente desde documento
4. Editar/refinar manualmente
5. Estudiar con sistema de volteo

---

## 📈 Casos de Uso

### 1. Estudiante Universitario

**Objetivo:** Preparar examen de Cálculo

**Workflow:**
```
1. Subir PDF del libro de Cálculo
2. Chatear para aclarar dudas:
   - "Explícame el teorema fundamental del cálculo"
3. Generar examen de práctica (20 preguntas)
4. Resolver y revisar feedback
5. Crear flashcards de fórmulas clave
6. Repasar antes del examen real
```

### 2. Profesor

**Objetivo:** Crear material educativo

**Workflow:**
```
1. Subir syllabus del curso
2. Generar 10 exámenes diferentes (banco de preguntas)
3. Crear flashcards de terminología
4. Exportar material para compartir con estudiantes
```

### 3. Autodidacta

**Objetivo:** Aprender nuevo tema

**Workflow:**
```
1. Descargar PDF de curso online
2. Subir a Examinator
3. Chatear para entender conceptos difíciles
4. Hacer exámenes para autoevaluarse
5. Crear flashcards de puntos clave
```

---

## 🧠 Sistema de IA

### Modelos Disponibles

**Ollama (GPU - Recomendado):**
- `llama31-local` - Llama 3.1 8B (general purpose)
- `deepseek-r1` - DeepSeek-R1 7B (razonamiento avanzado)
- `qwen2.5` - Qwen 2.5 7B (multilingüe)

**Fallback (CPU):**
- Modelos GGUF con `llama-cpp-python`

### Configuración IA

**Archivo:** `config.json`
```json
{
  "modelo_ollama_activo": "llama31-local",
  "usar_ollama": true,
  "modelo_path": "modelos/llama-3.1-8b.gguf",
  "ajustes_avanzados": {
    "n_ctx": 4096,
    "temperature": 0.7,
    "max_tokens": 512,
    "top_p": 0.9,
    "repeat_penalty": 1.15,
    "n_gpu_layers": 35
  }
}
```

### Prompts Sistema

**Generación de Preguntas:**
- Estructura JSON estricta
- Validación automática
- Retry con corrección

**Evaluación:**
- Rúbricas detalladas
- Feedback constructivo
- Puntuación justificada

---

## 📊 Gestión de Calificaciones

### Almacenamiento de Resultados

**Ubicación:** `examenes/{carpeta}/resultados_examenes/`

**Estructura de Resultado (REAL - Datos actuales del sistema):**
```json
{
  "id": "20251120_122000",
  "archivo": "examen_20251120_122000.json",
  "fecha_completado": "2025-11-20T12:20:00.121802",
  "carpeta_ruta": "Platzi",
  "carpeta_nombre": "Platzi",
  "puntos_obtenidos": 45.5,
  "puntos_totales": 100,
  "porcentaje": 45.5,
  "tipo": "completado",
  "resultados": [
    {
      "pregunta": "¿Qué es una derivada?",
      "tipo": "desarrollo",
      "opciones": [],
      "respuesta_usuario": "Es la tasa de cambio instantáneo...",
      "respuesta_correcta": "La derivada representa la tasa de cambio...",
      "puntos": 8.5,
      "puntos_maximos": 10,
      "feedback": "Muy bien, pero falta mencionar el límite matemático..."
    },
    {
      "pregunta": "¿Cuál es la capital de Francia?",
      "tipo": "multiple",
      "opciones": ["A) Londres", "B) París", "C) Berlín", "D) Madrid"],
      "respuesta_usuario": "B",
      "respuesta_correcta": "B",
      "puntos": 10,
      "puntos_maximos": 10,
      "feedback": "¡Correcto!"
    }
  ]
}
```

### Funcionalidades de Calificaciones

**Actualmente implementado:**
- ✅ Guardado automático de resultados en `examenes/{carpeta}/`
- ✅ Historial completo por carpeta (estructura paralela a `extracciones/`)
- ✅ Feedback detallado por pregunta (generado por IA)
- ✅ Cálculo de porcentajes y puntos
- ✅ Sistema de pausar/continuar exámenes (en `examenes_progreso/`)
- ✅ IDs únicos por examen (timestamp: `examen_YYYYMMDD_HHMMSS.json`)
- ✅ Listado de exámenes completados y en progreso
- ✅ Visualización de resultados en frontend con colores (verde >70%, amarillo >50%, rojo <50%)

**Por implementar (tu objetivo):**
- ⏳ **Dashboard de Rendimiento** - Vista unificada de todos los exámenes
- ⏳ **Análisis de Progreso** - Gráficos de evolución temporal
- ⏳ **Gráficos de Evolución** - Line charts, bar charts con calificaciones
- ⏳ **Recomendaciones de Estudio** - Basadas en puntos débiles detectados
- ⏳ **Comparación entre Exámenes** - Mismo documento en diferentes fechas
- ⏳ **Identificación de Puntos Débiles** - Tipos de preguntas con menor rendimiento
- ⏳ **Sistema de Metas** - Establecer y seguir objetivos de calificación
- ⏳ **Análisis por Carpeta** - Rendimiento global por tema/curso
- ⏳ **Predicción de Rendimiento** - Tendencias y proyecciones
- ⏳ **Exportación de Reportes** - PDF/Excel con estadísticas

---

## 🎯 Tu Próximo Objetivo: Optimizador de Rendimiento

### Contexto para ChatGPT

**Datos Disponibles en el Sistema (REAL):**
```javascript
// 1. EXÁMENES COMPLETADOS
// Ubicación: examenes/{carpeta}/examen_{timestamp}.json
// Ejemplo: examenes/Platzi/examen_20251120_122000.json

Estructura:
{
  id: "20251120_122000",
  archivo: "examen_20251120_122000.json",
  fecha_completado: "2025-11-20T12:20:00.121802", // ISO format
  carpeta_ruta: "Platzi",  // Ruta relativa desde extracciones/
  carpeta_nombre: "Platzi",
  puntos_obtenidos: 45.5,
  puntos_totales: 100,
  porcentaje: 45.5,
  tipo: "completado",
  resultados: [
    {
      pregunta: "...",
      tipo: "multiple" | "desarrollo" | "corta" | "flashcard" | "verdadero_falso",
      opciones: [...],  // Solo para tipo 'multiple'
      respuesta_usuario: "...",
      respuesta_correcta: "...",
      puntos: 8.5,
      puntos_maximos: 10,
      feedback: "Feedback generado por IA..."
    }
  ]
}

// 2. EXÁMENES EN PROGRESO (pausados)
// Ubicación: examenes/{carpeta}/examenes_progreso/examen_progreso_{timestamp}.json

Estructura:
{
  id: "20251120_143000",
  archivo: "examen_progreso_20251120_143000.json",
  carpeta_ruta: "Platzi/Diseño UX",
  carpeta_nombre: "Diseño UX",
  preguntas: [...],  // Array completo de preguntas
  respuestas: {      // Respuestas parciales del usuario
    "0": "Mi respuesta...",
    "1": "Otra respuesta...",
    "2": ""  // Sin responder aún
  },
  fecha_inicio: "2025-11-20T14:30:00",
  fecha_pausa: "2025-11-20T14:45:00",
  tipo: "en_progreso"
}

// 3. ESTRUCTURA DE CARPETAS (paralela)
extracciones/              examenes/
├── Platzi/        ➡️     ├── Platzi/
│   ├── doc1.txt           │   ├── examen_xxx.json
│   └── Diseño UX/         │   └── Diseño UX/
│       └── doc2.txt       │       ├── examen_yyy.json
│                          │       └── examenes_progreso/
│                          │           └── examen_progreso_zzz.json
```

**Tipos de Preguntas Existentes:**
- `"multiple"` - Opción múltiple (A, B, C, D)
- `"desarrollo"` - Respuesta larga evaluada por IA
- `"corta"` - Respuesta breve (2-4 líneas)
- `"verdadero_falso"` - V/F con justificación
- `"flashcard"` - Pregunta/respuesta de flashcard practicada

**Funcionalidades Deseadas para el Optimizador:**

1. **📊 Dashboard de Rendimiento General:**
   - **Calificación Promedio Global** - Media de todos los exámenes
   - **Gráfico de Evolución** - Line chart con porcentaje vs fecha
   - **Total de Exámenes Realizados** - Conteo completo
   - **Tiempo Total de Estudio** - Suma de duraciones estimadas
   - **Distribución de Calificaciones** - Histograma (0-50%, 50-70%, 70-100%)
   - **Mejor/Peor Resultado** - Destacar extremos
   - **Racha Actual** - Días consecutivos estudiando

2. **📈 Análisis por Tipo de Pregunta:**
   - **Rendimiento por Tipo:**
     * Opción Múltiple: X% promedio
     * Desarrollo: Y% promedio
     * Respuesta Corta: Z% promedio
     * Verdadero/Falso: W% promedio
   - **Visualización:** Gráfico de barras horizontal
   - **Recomendación:** "Deberías practicar más: [tipo con menor %]"

3. **🎯 Recomendaciones Inteligentes:**
   - **Temas a Repasar:** Detectar carpetas/documentos con <70%
   - **Mejor Momento:** Analizar hora del día con mejores resultados
   - **Frecuencia Óptima:** "Llevas X días sin practicar [tema]"
   - **Predicción:** "Con tu ritmo actual, alcanzarás 80% en [N] exámenes más"

4. **📚 Comparación entre Carpetas/Temas:**
   - **Tabla Comparativa:**
     | Carpeta | Promedio | Exámenes | Última Práctica |
     |---------|----------|----------|-----------------|
     | Platzi  | 75%      | 12       | Hace 2 días     |
     | Biología| 85%      | 8        | Hace 1 semana   |
   - **Gráfico de Radar** - Visualizar fortalezas/debilidades por tema
   - **Progreso Temporal** - Línea de tiempo por carpeta

5. **🎯 Sistema de Metas y Seguimiento:**
   - **Establecer Meta:** "Quiero alcanzar 85% promedio"
   - **Progreso Visual:** Barra de progreso (actual vs meta)
   - **Predicción Inteligente:** 
     * "Actual: 72%, Meta: 85%"
     * "Necesitas +13 puntos"
     * "Estimado: 5-6 exámenes más con >90%"
   - **Notificaciones:** "¡Estás a solo 2% de tu meta!"

6. **📉 Identificación de Puntos Débiles:**
   - **Análisis de Feedback:** Extraer palabras clave de feedbacks negativos
   - **Conceptos Problemáticos:** 
     * "Fallas frecuentemente en: [derivadas, límites, integrales]"
     * Basado en análisis de preguntas con <50%
   - **Sugerencias de Estudio:** "Genera flashcards sobre: [conceptos débiles]"

7. **📊 Métricas Avanzadas:**
   - **Tendencia de Mejora:** Pendiente de la curva de aprendizaje
   - **Consistencia:** Desviación estándar de calificaciones
   - **Velocidad de Respuesta:** Tiempo promedio por pregunta (si se implementa timer)
   - **Tasa de Abandono:** % de exámenes iniciados vs completados

8. **💾 Exportación y Reportes:**
   - **Reporte PDF:** Resumen mensual/semanal con gráficos
   - **Exportar CSV:** Datos tabulares para análisis externo
   - **Compartir Logros:** Capturas de progreso

9. **🔔 Sistema de Alertas:**
   - "Hace 7 días que no practicas [Cálculo]"
   - "Tu promedio bajó 5% esta semana"
   - "¡Nuevo récord personal en [Física]!"

10. **🧪 Comparación de Intentos:**
    - Para el mismo documento/carpeta:
      * "Primer intento: 65%"
      * "Segundo intento: 78% (+13% mejora)"
      * "Mejor intento: 85%"
    - Gráfico de evolución por documento específico

---

## 📁 Estructura de Datos Completa

### Base de Datos (Filesystem)

```
Examinator/
├── extracciones/                    # DOCUMENTOS
│   ├── {carpeta}/
│   │   ├── {documento}.txt
│   │   └── ...
│   
├── chats_historial/                 # CONVERSACIONES
│   ├── chat_{timestamp}.json
│   └── {carpeta}/
│       └── chat_{timestamp}.json
│
├── examenes/                        # EVALUACIONES
│   └── {carpeta}/
│       ├── examen_{timestamp}.json
│       └── resultados_examenes/
│           └── resultado_{timestamp}.json
│
└── logs_practicas_detallado/        # DEBUG/LOGS
    └── practica_{timestamp}/
        └── practica_{timestamp}.log
```

---

## 🔌 API Endpoints Principales

### Documentos
- `POST /api/extraer-pdf` - Sube y extrae PDF a texto
- `GET /api/documentos?ruta=` - Lista documentos .txt en carpeta
- `GET /api/carpetas?ruta=` - Lista subcarpetas
- `POST /api/carpetas` - Crea nueva carpeta
- `DELETE /api/carpetas?ruta=` - Elimina carpeta (solo si está vacía)
- `PUT /api/carpetas/renombrar` - Renombra carpeta
- `PUT /api/documentos/mover` - Mueve carpeta a otro destino
- `GET /api/buscar?q=` - Búsqueda global de documentos

### Chatbot
- `POST /api/chat` - Chat con streaming (SSE - Server-Sent Events)
- `GET /api/chats/historial` - Lista conversaciones guardadas
- `POST /api/chats/guardar` - Guarda chat (con carpeta opcional)
- `GET /api/chats/carpetas` - Lista carpetas de chats

### Exámenes/Prácticas
- `POST /api/generar-examen` - Genera examen completo (multi-tipo)
- `POST /api/generar_examen_bloque` - Genera por bloques (memoria eficiente)
- `POST /api/evaluar-examen` - Evalúa respuestas con IA
- `POST /api/examenes/pausar` - Guarda progreso de examen
- `POST /api/examenes/guardar-temporal` - Guarda examen temporal
- `GET /api/examenes/cargar-temporal?carpeta=` - Carga examen pausado
- `GET /api/examenes/listar` - Lista todos los exámenes (completados + progreso)
- `GET /api/examenes/carpetas` - Lista carpetas con exámenes disponibles
- `GET /api/progreso-examen/{session_id}` - Obtiene progreso de generación

### Flashcards
- `GET /api/flashcards?carpeta=` - Lista flashcards de carpeta
- `GET /api/flashcards/{id}` - Obtiene flashcard específica
- `POST /api/flashcards` - Crea nueva flashcard
- `PUT /api/flashcards/{id}` - Edita flashcard existente
- `DELETE /api/flashcards/{id}` - Elimina flashcard
- `POST /api/flashcards/asistente` - Genera flashcards con IA
- `POST /api/flashcards/evaluar` - Evalúa respuesta de flashcard
- `GET /api/flashcards/carpetas` - Lista carpetas de flashcards
- `POST /api/flashcards/carpetas` - Crea carpeta de flashcards
- `POST /api/flashcards/exportar` - Exporta flashcards a JSON
- `POST /api/flashcards/importar` - Importa flashcards desde JSON

### Configuración IA
- `GET /api/config` - Obtiene configuración actual
- `POST /api/config` - Actualiza configuración del modelo
- `GET /api/modelos` - Lista modelos Ollama disponibles
- `GET /api/modelos/disponibles` - Modelos disponibles para descargar
- `POST /api/descargar-modelo` - Descarga modelo Ollama
- `GET /api/diagnostico/ollama` - Diagnóstico de estado de Ollama
- `POST /api/diagnostico/reparar-ollama` - Intenta reparar Ollama

### Búsqueda Web
- `POST /api/buscar-web` - Búsqueda contextual en DuckDuckGo

---

## 🚀 Tecnologías y Librerías Clave

### Backend
```python
fastapi==0.104.1          # Framework API
uvicorn==0.24.0           # Servidor ASGI
ollama==0.1.0             # Cliente Ollama
llama-cpp-python==0.2.20  # Fallback CPU
pypdf==3.17.1             # Extracción PDF
requests==2.31.0          # HTTP client
```

### Frontend
```json
{
  "react": "^18.2.0",
  "vite": "^5.0.0",
  "katex": "^0.16.9",
  "react-katex": "^3.0.1"
}
```

---

## 🎓 Resumen Ejecutivo para ChatGPT

**Examinator es:**
- Sistema completo de aprendizaje con IA local
- Backend Python (FastAPI) + Frontend React
- Usa Ollama (GPU) para generación inteligente
- Extrae texto de PDFs
- Genera exámenes/flashcards automáticamente
- Evalúa respuestas con feedback detallado
- Chatbot contextual que "lee" tus documentos
- Sistema de carpetas flexible
- Guarda resultados en JSON

**Stack:**
- Python 3.10+ (FastAPI, Ollama, pypdf)
- React 18 + Vite
- Ollama (llama3.1, deepseek-r1, qwen)
- KaTeX (LaTeX rendering)

**Datos importantes:**
- Resultados en: `examenes/{carpeta}/resultados_examenes/`
- Estructura: JSON con calificaciones, feedback, timestamps
- Frontend: 19000+ líneas (App.jsx)
- Backend: 3600+ líneas (api_server.py)

**Próximo objetivo:**
Optimizador de rendimiento sobre calificaciones guardadas:
- Dashboard de evolución temporal con gráficos
- Análisis de puntos débiles por tipo de pregunta
- Recomendaciones inteligentes de estudio
- Comparación entre exámenes del mismo tema
- Sistema de metas con predicción de progreso
- Métricas avanzadas (tendencia, consistencia, velocidad)
- Exportación de reportes (PDF/CSV)
- Alertas de práctica y notificaciones
- Análisis de feedback automático (conceptos problemáticos)
- Comparación de intentos múltiples (mejora entre exámenes)

**Contexto técnico importante:**
- Resultados en: `examenes/{carpeta}/examen_{timestamp}.json`
- Estructura JSON con: `puntos_obtenidos`, `puntos_totales`, `porcentaje`, `fecha_completado`, `resultados[]`
- Cada pregunta tiene: `tipo`, `puntos`, `puntos_maximos`, `feedback`
- Sistema ya guarda automáticamente al completar examen
- Exámenes pausados en: `examenes/{carpeta}/examenes_progreso/`
- Estructura paralela a `extracciones/` (misma jerarquía de carpetas)
- Frontend tiene estados: `resultadoExamen`, `examenCompletado`
- Endpoints disponibles: `/api/examenes/listar`, `/api/examenes/carpetas`

---

## 📝 Notas Técnicas

### Generación de Exámenes

**Proceso:**
1. Documento dividido en chunks (1500 palabras)
2. Prompts especializados por tipo
3. Respuesta JSON validada
4. Sistema de retry si falla parsing
5. Logs detallados en `logs_practicas_detallado/`

**Ventajas:**
- Memoria eficiente (chunks)
- Calidad alta (prompts especializados)
- Debugging fácil (logs detallados)

### Evaluación

**Tipos:**
- Múltiple/V-F: Comparación exacta
- Corta/Desarrollo: IA evalúa con prompt

**Prompt de evaluación:**
```
Evalúa la respuesta del estudiante.
Pregunta: {pregunta}
Respuesta correcta: {correcta}
Respuesta estudiante: {usuario}

Retorna JSON:
{
  "puntos_obtenidos": 8.5,
  "feedback": "...",
  "aspectos_bien": [...],
  "aspectos_mejorar": [...]
}
```

---

## 🌟 Características Únicas

1. **IA 100% Local** - Sin enviar datos a internet
2. **GPU Acelerada** - Respuestas rápidas con NVIDIA
3. **Streaming Real** - Respuestas del chat en vivo
4. **LaTeX Nativo** - Fórmulas matemáticas perfectas
5. **Sistema Modular** - Fácil agregar nuevas funcionalidades
6. **Sin Base de Datos** - Solo archivos JSON/TXT
7. **Logs Detallados** - Debugging profesional
8. **Multiplataforma** - Windows/Linux/Mac

---

**Fecha de Documentación:** 22 de noviembre de 2025  
**Versión del Sistema:** 3.0  
**Autor:** Sistema Examinator  
**Propósito:** Documentación completa para ChatGPT y desarrollo futuro

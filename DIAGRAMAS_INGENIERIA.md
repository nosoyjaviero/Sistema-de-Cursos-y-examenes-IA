# 📐 Diagramas de Ingeniería - Sistema Examinator

> **Sistema de estudio inteligente con generación de exámenes, flashcards, corrección automática y repetición espaciada impulsado por IA**

---

## 📑 Índice de Diagramas

1. [Diagrama de Arquitectura del Sistema](#1-diagrama-de-arquitectura-del-sistema)
2. [Diagrama de Componentes](#2-diagrama-de-componentes)
3. [Diagrama de Secuencia - Generación de Examen](#3-diagrama-de-secuencia---generación-de-examen)
4. [Diagrama de Secuencia - Sesión de Estudio](#4-diagrama-de-secuencia---sesión-de-estudio)
5. [Diagrama de Flujo de Datos](#5-diagrama-de-flujo-de-datos)
6. [Diagrama Entidad-Relación](#6-diagrama-entidad-relación)
7. [Diagrama de Estados - Sesión de Estudio](#7-diagrama-de-estados---sesión-de-estudio)
8. [Diagrama de Casos de Uso](#8-diagrama-de-casos-de-uso)
9. [Diagrama de Despliegue](#9-diagrama-de-despliegue)
10. [Diagrama de Clases Backend](#10-diagrama-de-clases-backend)

---

## 1. Diagrama de Arquitectura del Sistema

```mermaid
graph TB
    subgraph "Cliente - Frontend React"
        UI[Interface de Usuario]
        STATE[React State Management]
        CACHE[LocalStorage Cache]
        VISUAL[Canvas Editors<br/>Math, Chemistry, Physics]
    end
    
    subgraph "Servidor - FastAPI Backend"
        API[API REST FastAPI]
        AUTH[CORS Middleware]
        
        subgraph "Servicios de IA"
            OLLAMA[Ollama Service<br/>GPU Acceleration]
            GENUNI[GeneradorUnificado]
            GENDOS[GeneradorDosPasos]
        end
        
        subgraph "Procesamiento"
            EXTRACT[Extractor de Texto<br/>PDF, DOCX, TXT]
            EVAL[Evaluador Semántico]
            SEARCH[Búsqueda Web<br/>DuckDuckGo]
        end
        
        subgraph "Gestión de Datos"
            DB[CursosDatabase]
            FILES[File System Manager]
            PERSIST[Datos Persistentes]
        end
    end
    
    subgraph "Almacenamiento"
        FS[(Sistema de Archivos)]
        subgraph "extracciones/"
            DOCS[Documentos Extraídos]
            NOTES[Notas TXT/MD]
        end
        subgraph "Datos JSON"
            EXAMS[Exámenes]
            FLASH[Flashcards]
            PRACT[Prácticas]
            SESS[Sesiones]
        end
    end
    
    subgraph "Servicios Externos"
        OLLAMASRV[Ollama Server<br/>:11434]
        WEB[Internet<br/>Búsqueda Web]
    end
    
    UI --> STATE
    STATE --> CACHE
    UI --> API
    
    API --> AUTH
    AUTH --> OLLAMA
    AUTH --> GENUNI
    AUTH --> GENDOS
    AUTH --> EXTRACT
    AUTH --> EVAL
    AUTH --> SEARCH
    AUTH --> DB
    AUTH --> FILES
    AUTH --> PERSIST
    
    OLLAMA --> OLLAMASRV
    GENUNI --> OLLAMA
    GENDOS --> OLLAMA
    EVAL --> OLLAMA
    SEARCH --> WEB
    
    DB --> FS
    FILES --> DOCS
    FILES --> NOTES
    PERSIST --> EXAMS
    PERSIST --> FLASH
    PERSIST --> PRACT
    PERSIST --> SESS
    
    VISUAL --> UI
    
    style UI fill:#4CAF50
    style API fill:#2196F3
    style OLLAMA fill:#FF9800
    style FS fill:#9C27B0
```

---

## 2. Diagrama de Componentes

```mermaid
graph LR
    subgraph "Frontend Components"
        APP[App.jsx<br/>Main Component]
        
        subgraph "UI Modules"
            STUDY[Modo Sesión<br/>Study Session]
            DOCS[Visor Documentos]
            EXAM[Generador Exámenes]
            FLASH[Flashcards Manager]
            CHAT[Chat IA]
            SEARCH[Buscador]
            HIST[Historial]
        end
        
        subgraph "Visual Editors"
            MATH[MathEditor]
            CHEM[ChemEditor]
            PHYS[PhysicsEditor]
            ENG[EngineeringCanvas]
            PROG[ProgrammingCanvas]
            MUSIC[MusicCanvas]
            GEO[GeometryCanvas]
            ART[ArtCanvas]
        end
        
        subgraph "Utilities"
            HELPERS[Data Helpers]
            SM2[SM-2 Algorithm]
            AUDIO[Audio Synthesis]
        end
    end
    
    subgraph "Backend Modules"
        SERVER[api_server.py]
        
        subgraph "Generators"
            GU[generador_unificado.py]
            GD[generador_dos_pasos.py]
            GE[generador_examenes.py]
        end
        
        subgraph "Data Management"
            CDB[cursos_db.py]
            EP[endpoints_datos_persistentes.py]
        end
        
        subgraph "Utilities Backend"
            EXAM_EXT[examinator.py<br/>Text Extraction]
            WEB_SEARCH[busqueda_web.py]
            ERR_DETECT[detector_errores.py]
        end
    end
    
    APP --> STUDY
    APP --> DOCS
    APP --> EXAM
    APP --> FLASH
    APP --> CHAT
    APP --> SEARCH
    APP --> HIST
    
    STUDY --> MATH
    STUDY --> CHEM
    STUDY --> PHYS
    STUDY --> ENG
    STUDY --> PROG
    
    EXAM --> GU
    CHAT --> SERVER
    DOCS --> EXAM_EXT
    
    SERVER --> GU
    SERVER --> GD
    SERVER --> GE
    SERVER --> CDB
    SERVER --> EP
    SERVER --> EXAM_EXT
    SERVER --> WEB_SEARCH
    
    HELPERS --> SM2
    STUDY --> SM2
    FLASH --> SM2
    
    style APP fill:#4CAF50
    style SERVER fill:#2196F3
    style GU fill:#FF9800
```

---

## 3. Diagrama de Secuencia - Generación de Examen

```mermaid
sequenceDiagram
    participant U as Usuario
    participant UI as Frontend React
    participant API as FastAPI Server
    participant GEN as GeneradorUnificado
    participant OLLAMA as Ollama Service
    participant FS as File System
    
    U->>UI: Selecciona documento
    U->>UI: Configura examen (tipo, cantidad)
    UI->>UI: Valida configuración
    
    UI->>API: POST /api/generar-examen
    Note over UI,API: {documento, tipo, cantidad,<br/>temperatura, contexto}
    
    API->>API: Genera session_id
    API->>GEN: Inicializar generador
    
    alt Ollama disponible
        GEN->>OLLAMA: Verificar conexión
        OLLAMA-->>GEN: OK (GPU activa)
    else Ollama no disponible
        GEN->>GEN: Usar modelo GGUF local
    end
    
    loop Por cada pregunta
        GEN->>OLLAMA: Generar pregunta<br/>(prompt + contexto)
        OLLAMA-->>GEN: Pregunta JSON
        GEN->>GEN: Validar formato
        GEN->>GEN: Generar distractores
        GEN->>API: Actualizar progreso
        API->>UI: SSE: {progreso: X%}
        UI->>U: Mostrar barra progreso
    end
    
    GEN-->>API: Examen completo
    API->>FS: Guardar JSON
    FS-->>API: Guardado exitoso
    
    API-->>UI: {examen_id, preguntas[]}
    UI->>U: Mostrar examen generado
    
    U->>UI: Iniciar examen
    UI->>UI: Cambiar a modo práctica
```

---

## 4. Diagrama de Secuencia - Sesión de Estudio

```mermaid
sequenceDiagram
    participant U as Usuario
    participant UI as Frontend
    participant TIMER as Timer/Scheduler
    participant SM2 as SM-2 Algorithm
    participant API as Backend API
    participant FS as File System
    
    U->>UI: Iniciar sesión de estudio
    UI->>UI: Configurar duración/prioridad
    
    UI->>API: GET /datos/practicas
    API->>FS: Leer archivos JSON
    FS-->>API: Prácticas con errores
    API-->>UI: Lista de errores
    
    UI->>SM2: Filtrar por fecha revisión
    SM2-->>UI: Errores para hoy
    
    UI->>UI: Activar sesión
    UI->>TIMER: Iniciar countdown
    
    loop Fase: Corrigiendo Errores
        UI->>U: Mostrar pregunta error
        U->>UI: Responder pregunta
        
        UI->>API: POST /api/evaluar-respuesta
        API->>API: Evaluar (similitud/exacta)
        API-->>UI: {correcta: bool, puntos}
        
        alt Respuesta correcta
            UI->>SM2: Calcular próxima revisión
            SM2-->>UI: {fecha, intervalo, facilidad}
            UI->>UI: Marcar corregido=true
            UI->>API: POST /datos/practicas/actualizar_archivo
            API->>FS: Actualizar JSON individual
            FS-->>API: OK
        else Respuesta incorrecta
            UI->>SM2: Programar para mañana
        end
        
        TIMER->>UI: Tick (cada segundo)
        UI->>U: Actualizar cronómetro
        
        alt Tiempo descanso alcanzado (25 min)
            TIMER->>UI: Activar descanso
            UI->>U: Pantalla de descanso (5 min)
        end
    end
    
    loop Fase: Flashcards
        UI->>U: Mostrar flashcard
        U->>UI: Voltear / Responder
        U->>UI: Calificar dificultad
        UI->>SM2: Actualizar espaciado
    end
    
    loop Fase: Lectura Profunda
        UI->>U: Mostrar documento
        U->>UI: Leer / Tomar notas
        UI->>API: POST /api/guardar-nota-txt
    end
    
    TIMER->>UI: Sesión finalizada
    UI->>U: Mostrar resumen
    U->>UI: Reflexión (qué fue difícil)
    
    UI->>API: POST /datos/sesiones/completadas
    API->>FS: Guardar sesión
    
    UI->>UI: Limpiar estado
    UI->>U: Volver a inicio
```

---

## 5. Diagrama de Flujo de Datos

```mermaid
graph TB
    subgraph "Entrada de Datos"
        PDF[Documento PDF/DOCX]
        WEB[Búsqueda Web]
        USER_INPUT[Input Usuario]
    end
    
    subgraph "Procesamiento"
        EXTRACT[Extracción Texto]
        CHUNK[Chunking Contexto]
        PROMPT[Construcción Prompt]
    end
    
    subgraph "Generación IA"
        OLLAMA[Modelo Ollama]
        VALIDATE[Validación JSON]
        DISTRACT[Gen. Distractores]
    end
    
    subgraph "Almacenamiento"
        EXAMEN_JSON[examen_XXXXXX.json]
        PRACTICA_JSON[practica_XXXXXX.json]
        FLASHCARD_JSON[flashcards.json]
        NOTAS_TXT[notas/XXXXXX.txt]
    end
    
    subgraph "Evaluación"
        RESPUESTA[Respuesta Usuario]
        EVAL_SEM[Evaluación Semántica]
        EVAL_EXACT[Evaluación Exacta]
        SM2_CALC[Cálculo SM-2]
    end
    
    subgraph "Actualización"
        UPDATE[Actualizar JSON]
        MARK_CORR[Marcar corregido]
        NEXT_REV[Próxima revisión]
    end
    
    PDF --> EXTRACT
    WEB --> EXTRACT
    USER_INPUT --> PROMPT
    
    EXTRACT --> CHUNK
    CHUNK --> PROMPT
    PROMPT --> OLLAMA
    
    OLLAMA --> VALIDATE
    VALIDATE --> DISTRACT
    DISTRACT --> EXAMEN_JSON
    
    EXAMEN_JSON --> RESPUESTA
    RESPUESTA --> EVAL_SEM
    RESPUESTA --> EVAL_EXACT
    
    EVAL_SEM --> SM2_CALC
    EVAL_EXACT --> SM2_CALC
    
    SM2_CALC --> UPDATE
    UPDATE --> MARK_CORR
    UPDATE --> NEXT_REV
    
    MARK_CORR --> PRACTICA_JSON
    NEXT_REV --> FLASHCARD_JSON
    
    USER_INPUT --> NOTAS_TXT
    
    style OLLAMA fill:#FF9800
    style SM2_CALC fill:#4CAF50
    style EXAMEN_JSON fill:#2196F3
```

---

## 6. Diagrama Entidad-Relación

```mermaid
erDiagram
    CARPETA ||--o{ DOCUMENTO : contiene
    CARPETA ||--o{ CARPETA : subcarpeta
    CARPETA ||--o{ EXAMEN : genera
    CARPETA ||--o{ PRACTICA : realiza
    CARPETA ||--o{ FLASHCARD : crea
    CARPETA ||--o{ NOTA : guarda
    
    EXAMEN ||--o{ PREGUNTA : incluye
    PRACTICA ||--o{ RESULTADO : tiene
    PREGUNTA ||--o{ RESULTADO : evalua
    
    FLASHCARD ||--|| SM2_DATA : aplica
    RESULTADO ||--|| SM2_DATA : aplica
    
    SESION ||--o{ FASE : contiene
    FASE ||--o{ RESULTADO : registra
    FASE ||--o{ FLASHCARD : repasa
    
    USUARIO ||--o{ SESION : realiza
    USUARIO ||--o{ NOTA : escribe
    
    CARPETA {
        string nombre
        string ruta
        datetime fecha_creacion
        int nivel
    }
    
    DOCUMENTO {
        string id
        string nombre
        string tipo
        string ruta_original
        string contenido_extraido
        datetime fecha_extraccion
    }
    
    EXAMEN {
        string id
        string carpeta_ruta
        string archivo
        datetime fecha_creacion
        int num_preguntas
        string tipo
        float temperatura
    }
    
    PREGUNTA {
        string pregunta
        string tipo
        array opciones
        string respuesta_correcta
        string explicacion
        int puntos_maximos
    }
    
    PRACTICA {
        string id
        string archivo
        string carpeta_ruta
        datetime fecha_completado
        float puntos_obtenidos
        float puntos_totales
        float porcentaje
        bool es_practica
    }
    
    RESULTADO {
        string pregunta
        string tipo
        string respuesta_usuario
        string respuesta_correcta
        float puntos
        float puntos_maximos
        string feedback
        bool corregido
        datetime fechaCorreccion
    }
    
    FLASHCARD {
        string id
        string pregunta
        string respuesta
        string carpeta
        datetime proximaRevision
        datetime ultimaRevision
        int intervalo
        int repeticiones
        float facilidad
        string estadoRevision
    }
    
    SM2_DATA {
        datetime proximaRevision
        datetime ultimaRevision
        int intervalo
        int repeticiones
        float facilidad
        string estadoRevision
    }
    
    NOTA {
        string id
        string titulo
        string contenido
        string carpeta
        array tags
        datetime fecha_creacion
        datetime fecha_modificacion
    }
    
    SESION {
        string sesion_id
        string usuario_id
        datetime fecha_inicio
        datetime fecha_fin
        int duracion_planificada
        string prioridad
        int total_minutos
        int pausa_minutos
        int efectivo_minutos
    }
    
    FASE {
        string tipo
        int duracion_minutos
        int errores_reforzados
        int flashcards_repasadas
        int documentos_estudiados
    }
    
    USUARIO {
        string id
        string nombre
        datetime registro
    }
```

---

## 7. Diagrama de Estados - Sesión de Estudio

```mermaid
stateDiagram-v2
    [*] --> Configurando
    
    Configurando --> Iniciada : Configurar duración/prioridad
    
    Iniciada --> CorrigiendoErrores : Cargar errores pendientes
    
    state CorrigiendoErrores {
        [*] --> MostrandoPregunta
        MostrandoPregunta --> EsperandoRespuesta
        EsperandoRespuesta --> Evaluando : Usuario responde
        Evaluando --> Correcta : Respuesta ≥60%
        Evaluando --> Incorrecta : Respuesta <60%
        Correcta --> ActualizandoJSON : Marcar corregido
        Incorrecta --> ProgramarRevision : SM-2 (difícil)
        ActualizandoJSON --> SiguientePregunta
        ProgramarRevision --> SiguientePregunta
        SiguientePregunta --> MostrandoPregunta : Hay más errores
        SiguientePregunta --> [*] : No hay más errores
    }
    
    CorrigiendoErrores --> Descanso : 25 min transcurridos
    Descanso --> RepasandoFlashcards : 5 min descanso
    
    state RepasandoFlashcards {
        [*] --> MostrandoFlashcard
        MostrandoFlashcard --> Volteada : Usuario voltea
        Volteada --> Calificando : Usuario califica
        Calificando --> ActualizandoSM2 : Guardar facilidad
        ActualizandoSM2 --> SiguienteFlashcard
        SiguienteFlashcard --> MostrandoFlashcard : Hay más
        SiguienteFlashcard --> [*] : No hay más
    }
    
    RepasandoFlashcards --> Descanso : 25 min transcurridos
    Descanso --> LecturaProfunda : 5 min descanso
    
    state LecturaProfunda {
        [*] --> MostrandoDocumento
        MostrandoDocumento --> Leyendo
        Leyendo --> TomandoNotas : Usuario escribe
        TomandoNotas --> GuardandoNota
        GuardandoNota --> Leyendo
        Leyendo --> [*] : Tiempo agotado
    }
    
    LecturaProfunda --> Pausada : Usuario pausa
    CorrigiendoErrores --> Pausada : Usuario pausa
    RepasandoFlashcards --> Pausada : Usuario pausa
    
    Pausada --> CorrigiendoErrores : Usuario reanuda
    Pausada --> RepasandoFlashcards : Usuario reanuda
    Pausada --> LecturaProfunda : Usuario reanuda
    Pausada --> Detenida : Usuario detiene
    
    LecturaProfunda --> Finalizada : Tiempo total agotado
    RepasandoFlashcards --> Finalizada : Tiempo total agotado
    CorrigiendoErrores --> Finalizada : Tiempo total agotado
    
    state Finalizada {
        [*] --> MostrandoResumen
        MostrandoResumen --> SolicitandoReflexion
        SolicitandoReflexion --> GuardandoSesion
        GuardandoSesion --> [*]
    }
    
    Finalizada --> [*]
    Detenida --> [*]
    
    note right of CorrigiendoErrores
        Fase obligatoria
        Errores con porcentaje <60%
    end note
    
    note right of RepasandoFlashcards
        Repetición espaciada SM-2
        Solo tarjetas programadas para hoy
    end note
    
    note right of Descanso
        Técnica Pomodoro
        25 min estudio / 5 min descanso
    end note
```

---

## 8. Diagrama de Casos de Uso

```mermaid
graph TB
    subgraph "Sistema Examinator"
        subgraph "Gestión Documentos"
            UC1[Subir documento PDF/DOCX]
            UC2[Organizar en carpetas]
            UC3[Buscar documento]
            UC4[Ver contenido extraído]
        end
        
        subgraph "Generación de Contenido"
            UC5[Generar examen]
            UC6[Configurar tipo preguntas]
            UC7[Ajustar dificultad]
            UC8[Crear flashcards automáticas]
        end
        
        subgraph "Práctica y Evaluación"
            UC9[Realizar práctica]
            UC10[Responder preguntas]
            UC11[Ver feedback IA]
            UC12[Revisar errores]
        end
        
        subgraph "Sesión de Estudio"
            UC13[Iniciar sesión]
            UC14[Corregir errores clave]
            UC15[Repasar flashcards]
            UC16[Lectura profunda]
            UC17[Tomar notas]
            UC18[Pausar/Reanudar]
            UC19[Finalizar sesión]
        end
        
        subgraph "Repetición Espaciada"
            UC20[Ver calendario revisiones]
            UC21[Revisar items programados]
            UC22[Actualizar espaciado SM-2]
        end
        
        subgraph "Chat IA"
            UC23[Hacer pregunta a IA]
            UC24[Buscar en web]
            UC25[Explicar concepto]
        end
        
        subgraph "Historial"
            UC26[Ver sesiones completadas]
            UC27[Ver estadísticas]
            UC28[Exportar datos]
        end
        
        subgraph "Configuración"
            UC29[Seleccionar modelo IA]
            UC30[Ajustar temperatura]
            UC31[Configurar GPU]
        end
    end
    
    ESTUDIANTE((Estudiante))
    ADMIN((Administrador))
    OLLAMA_SRV[Ollama Server]
    WEB_SRV[Servicio Web]
    
    ESTUDIANTE --> UC1
    ESTUDIANTE --> UC2
    ESTUDIANTE --> UC3
    ESTUDIANTE --> UC4
    ESTUDIANTE --> UC5
    ESTUDIANTE --> UC6
    ESTUDIANTE --> UC7
    ESTUDIANTE --> UC8
    ESTUDIANTE --> UC9
    ESTUDIANTE --> UC10
    ESTUDIANTE --> UC11
    ESTUDIANTE --> UC12
    ESTUDIANTE --> UC13
    ESTUDIANTE --> UC14
    ESTUDIANTE --> UC15
    ESTUDIANTE --> UC16
    ESTUDIANTE --> UC17
    ESTUDIANTE --> UC18
    ESTUDIANTE --> UC19
    ESTUDIANTE --> UC20
    ESTUDIANTE --> UC21
    ESTUDIANTE --> UC22
    ESTUDIANTE --> UC23
    ESTUDIANTE --> UC24
    ESTUDIANTE --> UC25
    ESTUDIANTE --> UC26
    ESTUDIANTE --> UC27
    ESTUDIANTE --> UC28
    
    ADMIN --> UC29
    ADMIN --> UC30
    ADMIN --> UC31
    
    UC5 --> OLLAMA_SRV
    UC8 --> OLLAMA_SRV
    UC11 --> OLLAMA_SRV
    UC23 --> OLLAMA_SRV
    UC25 --> OLLAMA_SRV
    
    UC24 --> WEB_SRV
    
    style ESTUDIANTE fill:#4CAF50
    style ADMIN fill:#FF9800
    style OLLAMA_SRV fill:#2196F3
```

---

## 9. Diagrama de Despliegue

```mermaid
graph TB
    subgraph "Máquina del Usuario"
        subgraph "Navegador Web"
            REACT[React App<br/>Puerto 5173<br/>Vite Dev Server]
        end
        
        subgraph "Python Backend"
            FASTAPI[FastAPI Server<br/>Puerto 8000<br/>Uvicorn ASGI]
        end
        
        subgraph "Servicio IA Local"
            OLLAMA_LOCAL[Ollama Service<br/>Puerto 11434<br/>GPU CUDA/ROCm]
        end
        
        subgraph "Sistema de Archivos"
            DOCS_FOLDER[extracciones/<br/>Documentos]
            DATA_FOLDER[datos_persistentes/<br/>JSON Files]
            NOTES_FOLDER[notas/<br/>TXT/MD Files]
            LOGS_FOLDER[logs/<br/>Generation Logs]
        end
    end
    
    subgraph "Red Local (LAN)"
        OTROS[Otros dispositivos<br/>Tablets, Móviles]
    end
    
    subgraph "Internet"
        DUCKGO[DuckDuckGo API<br/>Búsqueda Web]
        GITHUB[GitHub Repo<br/>Versionado]
    end
    
    REACT -->|HTTP/SSE| FASTAPI
    REACT -->|WebSocket| FASTAPI
    FASTAPI -->|HTTP| OLLAMA_LOCAL
    FASTAPI -->|Read/Write| DOCS_FOLDER
    FASTAPI -->|Read/Write| DATA_FOLDER
    FASTAPI -->|Read/Write| NOTES_FOLDER
    FASTAPI -->|Write| LOGS_FOLDER
    
    FASTAPI -->|HTTPS| DUCKGO
    
    OTROS -->|HTTP :5173| REACT
    OTROS -->|HTTP :8000| FASTAPI
    
    FASTAPI -.->|Push/Pull| GITHUB
    
    style REACT fill:#61DAFB
    style FASTAPI fill:#009688
    style OLLAMA_LOCAL fill:#FF9800
    style DOCS_FOLDER fill:#9C27B0
    style DATA_FOLDER fill:#9C27B0
```

**Puertos utilizados:**
- **5173**: Frontend React (Vite)
- **8000**: Backend FastAPI
- **11434**: Ollama Service

**Protocolos:**
- HTTP REST para API calls
- Server-Sent Events (SSE) para progreso en tiempo real
- WebSocket para chat en tiempo real

---

## 10. Diagrama de Clases Backend

```mermaid
classDiagram
    class FastAPIApp {
        +CORSMiddleware middleware
        +startup_event()
        +listar_modelos()
        +generar_examen()
        +evaluar_respuesta()
        +guardar_nota()
    }
    
    class GeneradorUnificado {
        -usar_ollama: bool
        -modelo_ollama: str
        -modelo_gguf: LlamaCpp
        -temperatura: float
        +generar_pregunta(contexto, tipo)
        +generar_flashcard(error)
        +validar_json(respuesta)
    }
    
    class GeneradorDosPasos {
        -llm: LlamaCpp
        -temperatura: float
        +generar_pregunta_paso1(texto)
        +refinar_paso2(pregunta)
        +generar_distractores(pregunta)
    }
    
    class CursosDatabase {
        -base_path: Path
        +crear_carpeta(nombre, ruta)
        +listar_carpetas(ruta)
        +mover_carpeta(origen, destino)
        +buscar_documentos(query)
    }
    
    class ExaminadorTexto {
        +obtener_texto(archivo)
        +extraer_pdf(ruta)
        +extraer_docx(ruta)
        +extraer_txt(ruta)
    }
    
    class DetectorErrores {
        -errores: List
        +analizar_examen(resultados)
        +identificar_patrones()
        +generar_reporte()
    }
    
    class BusquedaWeb {
        +buscar_duckduckgo(query)
        +resumir_resultados(resultados)
        +extraer_snippets()
    }
    
    class EvaluadorSemantico {
        -llm: LlamaCpp
        +calcular_similitud(texto1, texto2)
        +evaluar_respuesta(usuario, correcta)
        +generar_feedback(comparacion)
    }
    
    class SM2Algorithm {
        +calcular_facilidad(calidad)
        +calcular_intervalo(facilidad, repeticiones)
        +proxima_revision(fecha_actual, intervalo)
    }
    
    class PreguntaExamen {
        +pregunta: str
        +tipo: str
        +opciones: List[str]
        +respuesta_correcta: str
        +explicacion: str
        +puntos_maximos: int
    }
    
    class Examen {
        +id: str
        +carpeta_ruta: str
        +fecha_creacion: datetime
        +preguntas: List[PreguntaExamen]
        +tipo: str
    }
    
    class Practica {
        +id: str
        +archivo: str
        +carpeta_ruta: str
        +fecha_completado: datetime
        +puntos_obtenidos: float
        +puntos_totales: float
        +porcentaje: float
        +resultados: List[Resultado]
        +es_practica: bool
    }
    
    class Resultado {
        +pregunta: str
        +tipo: str
        +respuesta_usuario: str
        +respuesta_correcta: str
        +puntos: float
        +puntos_maximos: float
        +feedback: str
        +corregido: bool
        +fechaCorreccion: datetime
    }
    
    class Flashcard {
        +id: str
        +pregunta: str
        +respuesta: str
        +carpeta: str
        +proximaRevision: datetime
        +ultimaRevision: datetime
        +intervalo: int
        +repeticiones: int
        +facilidad: float
        +estadoRevision: str
    }
    
    class Sesion {
        +sesion_id: str
        +usuario_id: str
        +fecha_inicio: datetime
        +fecha_fin: datetime
        +duracion_planificada: int
        +total_minutos: int
        +errores_reforzados: int
        +flashcards_repasadas: int
    }
    
    FastAPIApp --> GeneradorUnificado
    FastAPIApp --> GeneradorDosPasos
    FastAPIApp --> CursosDatabase
    FastAPIApp --> ExaminadorTexto
    FastAPIApp --> DetectorErrores
    FastAPIApp --> BusquedaWeb
    FastAPIApp --> EvaluadorSemantico
    
    GeneradorUnificado --> PreguntaExamen
    GeneradorDosPasos --> PreguntaExamen
    
    Examen *-- PreguntaExamen
    Practica *-- Resultado
    
    EvaluadorSemantico --> Resultado
    SM2Algorithm --> Flashcard
    SM2Algorithm --> Resultado
    
    CursosDatabase --> Examen
    CursosDatabase --> Practica
    CursosDatabase --> Flashcard
    CursosDatabase --> Sesion
```

---

## 📊 Métricas del Sistema

### Performance
- **Tiempo generación examen (10 preguntas)**: ~2-5 minutos
- **Evaluación semántica**: ~500ms por pregunta
- **Carga inicial**: ~1-2 segundos
- **Uso GPU**: 70-90% durante generación

### Capacidad
- **Archivos concurrentes**: Ilimitados
- **Tamaño máximo PDF**: 50MB
- **Sesiones simultáneas**: 1 por usuario
- **Flashcards por carpeta**: Ilimitadas

### Almacenamiento
```
extracciones/
├── Carpeta1/
│   ├── documentos/           # PDFs extraídos
│   ├── resultados_examenes/  # Exámenes individuales
│   ├── resultados_practicas/ # Prácticas individuales
│   └── notas/               # Notas TXT/MD
└── datos_persistentes/
    ├── flashcards.json      # Todas las flashcards
    ├── sesiones.json        # Sesiones completadas
    └── sesion_activa.json   # Sesión en curso
```

---

## 🔐 Seguridad

- **CORS**: Configurado para red local (*)
- **Validación**: JSON Schema en todas las requests
- **Sanitización**: Escape de HTML en respuestas
- **Rate Limiting**: No implementado (uso local)
- **Autenticación**: No requerida (uso local)

---

## 🚀 Tecnologías Clave

### Frontend
- **React 19.2.0** - UI Framework
- **Vite 7.2.2** - Build tool
- **KaTeX 0.16.25** - Math rendering
- **Mermaid 11.12.1** - Diagramas
- **MathLive 0.108.2** - Editor matemático

### Backend
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Ollama** - LLM inference
- **PyPDF2** - PDF extraction
- **python-docx** - DOCX extraction

### IA
- **Llama 3.1 8B** - Modelo principal
- **Qwen 2.5** - Modelo alternativo
- **DeepSeek R1** - Razonamiento
- **CUDA/ROCm** - Aceleración GPU

---

## 📝 Notas de Implementación

### Patrón de Arquitectura
- **Frontend**: Component-based (React)
- **Backend**: Microservicios (FastAPI)
- **Datos**: File-based JSON (sin BD tradicional)
- **IA**: Local inference (sin cloud)

### Decisiones de Diseño

1. **¿Por qué archivos JSON individuales?**
   - Evita conflictos de escritura
   - Fácil versionado con Git
   - Sin necesidad de ORM
   - Portable y legible

2. **¿Por qué Ollama local?**
   - Privacidad total (sin cloud)
   - Sin costos de API
   - Baja latencia
   - Control total del modelo

3. **¿Por qué SM-2 para repetición espaciada?**
   - Algoritmo probado (Anki lo usa)
   - Simple pero efectivo
   - Fácil de implementar
   - Adaptable

4. **¿Por qué FastAPI?**
   - Async nativo
   - Validación automática (Pydantic)
   - Documentación auto-generada
   - Alto rendimiento

---

## 🔄 Flujos Críticos

### 1. Flujo de Corrección de Errores
```
Error guardado (corregido=false)
    ↓
Extracción en sesión (porcentaje <60%)
    ↓
Mostrar al usuario
    ↓
Usuario responde
    ↓
Evaluación semántica
    ↓
Si correcta:
    - Marcar corregido=true
    - Calcular próxima revisión (SM-2)
    - Actualizar JSON individual
    - Recargar desde backend
    - Verificar que no está en lista
    ↓
Continuar con siguiente
```

### 2. Flujo de Guardado Distribuido
```
Usuario completa práctica
    ↓
Frontend detecta archivo individual
    (tiene carpeta_ruta + archivo)
    ↓
POST /datos/practicas/actualizar_archivo
    ↓
Backend busca:
    extracciones/{carpeta_ruta}/resultados_practicas/{archivo}.json
    ↓
Actualiza JSON con:
    - Nuevos resultados
    - Recalcula porcentaje
    - Actualiza fecha
    ↓
Guarda en mismo archivo
```

---

**Última actualización**: 26 de noviembre de 2025  
**Versión del sistema**: 3.0 (Corrección de errores v3)  
**Autor**: Sistema Examinator Team

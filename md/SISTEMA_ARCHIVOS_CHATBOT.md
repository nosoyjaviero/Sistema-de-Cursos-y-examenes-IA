# 📎 Sistema de Archivos para Chatbot - Guía Completa

## ✨ Características Implementadas

### 1. **📁 Explorador de Archivos Integrado**
Un panel completo para navegar y seleccionar archivos desde el chat:

- **🕒 Archivos Recientes**: Los últimos 30 archivos modificados de todas las categorías
- **📝 Notas**: Explora tus notas HTML, TXT y MD
- **📋 Exámenes**: Accede a exámenes generados (JSON)
- **✍️ Prácticas**: Revisa prácticas completadas (JSON)
- **📚 Cursos**: Navega material de cursos (TXT, PDF, DOCX)

### 2. **📎 Contexto Múltiple**
- Adjunta **múltiples archivos** al contexto del chat
- El chatbot usará **todos los archivos adjuntos** para responder
- Vista previa de archivos adjuntos con chips visuales
- Fácil eliminación individual o total

### 3. **🔍 Navegación por Carpetas**
- Explora la estructura completa de carpetas
- Botón "Volver" para navegar hacia atrás
- Contador de archivos en cada carpeta
- Breadcrumb mostrando la ruta actual

## 🎯 Cómo Usar

### Adjuntar Archivos al Chat

1. **Abrir el explorador**:
   - Ve al menú **Chat**
   - Haz clic en el botón **"📎 Archivos"** en la barra superior

2. **Seleccionar tipo de archivo**:
   - 🕒 **Recientes**: Ve los últimos archivos modificados
   - 📝 **Notas**: Busca en tus notas
   - 📋 **Exámenes**: Encuentra exámenes generados
   - ✍️ **Prácticas**: Revisa prácticas
   - 📚 **Cursos**: Explora material de estudio

3. **Navegar carpetas** (opcional):
   - Haz clic en una carpeta para entrar
   - Usa el botón **"⬅️ Volver"** para regresar

4. **Adjuntar archivo**:
   - Haz clic en **"+ Adjuntar"** junto al archivo deseado
   - El archivo se marcará como **"✓ Adjuntado"**
   - Aparecerá un chip verde debajo del explorador

5. **Usar el contexto**:
   - Haz tu pregunta normalmente en el chat
   - El chatbot usará **automáticamente** todos los archivos adjuntos
   - Ejemplo: *"Resume los puntos principales"*

6. **Gestionar contexto**:
   - Haz clic en **✕** en un chip para quitar ese archivo
   - Usa **"🗑️ Limpiar todo"** para remover todos los archivos

### Ejemplos de Uso

**Ejemplo 1: Analizar múltiples notas**
```
1. Adjuntar: "Nota sobre JavaScript.html"
2. Adjuntar: "Nota sobre React.html"
3. Preguntar: "¿Cuáles son las diferencias entre ambos?"
```

**Ejemplo 2: Revisar un examen con su material**
```
1. Adjuntar: "Curso Python Básico.txt"
2. Adjuntar: "Examen Python 01.json"
3. Preguntar: "¿Qué preguntas del examen no están cubiertas en el curso?"
```

**Ejemplo 3: Comparar prácticas**
```
1. Adjuntar: "Practica_Flashcards_01.json"
2. Adjuntar: "Practica_Flashcards_02.json"
3. Preguntar: "¿En qué práctica tuve mejor rendimiento?"
```

## 🔧 Funcionalidades Técnicas

### Backend (api_server.py)

**Nuevos Endpoints:**

1. **GET `/api/archivos/recientes`**
   - Parámetros: `limite` (default: 20)
   - Retorna: Archivos más recientes de todas las categorías
   - Ordenados por fecha de modificación

2. **GET `/api/archivos/explorar`**
   - Parámetros: `tipo` (notas/examenes/practicas/cursos), `ruta` (opcional)
   - Retorna: Carpetas y archivos en la ruta especificada
   - Incluye metadata (tamaño, fecha modificación)

3. **POST `/api/archivos/leer-contenido`**
   - Body: `{ ruta: "path/to/file" }`
   - Retorna: Contenido del archivo procesado
   - Soporta: TXT, MD, HTML, JSON, PDF

**Procesamiento de Archivos:**
- **.txt, .md**: Lectura directa
- **.html**: Extracción de texto con BeautifulSoup
- **.json**: Formateo pretty-print
- **.pdf**: Extracción con `obtener_texto()`
- Límite: 50KB de contenido (con truncado automático)

### Frontend (App.jsx)

**Nuevos Estados:**
```javascript
const [mostrarExploradorChat, setMostrarExploradorChat] = useState(false)
const [archivosRecientes, setArchivosRecientes] = useState([])
const [archivosContextoChat, setArchivosContextoChat] = useState([])
const [rutaExploradorChat, setRutaExploradorChat] = useState('')
const [carpetasExploradorChat, setCarpetasExploradorChat] = useState([])
const [tipoExploradorChat, setTipoExploradorChat] = useState('notas')
const [cargandoArchivos, setCargandoArchivos] = useState(false)
```

**Nuevas Funciones:**
- `cargarArchivosRecientes()` - Obtiene archivos recientes
- `explorarCarpetaChat(tipo, ruta)` - Navega por carpetas
- `adjuntarArchivoContexto(archivo)` - Adjunta archivo al contexto
- `quitarArchivoContexto(ruta)` - Remueve archivo del contexto
- `limpiarContextoArchivos()` - Limpia todo el contexto

**Integración con Chat:**
- El contexto se combina en `enviarMensajeChat()`
- Formato: `[Archivo: nombre]\ncontenido\n[Fin de nombre]`
- Se concatena con contexto existente (búsqueda web, archivo único)

## 🎨 Interfaz Visual

### Colores y Diseño

- **Panel Explorador**: Fondo oscuro semi-transparente
- **Tabs Activos**: Gradiente azul (#646cff)
- **Carpetas**: Naranja (#ff9800) con hover effect
- **Archivos Adjuntos**: Verde (#4caf50)
- **Iconos**: Emojis contextuales por tipo de archivo

### Componentes

1. **Explorador Header**: Título + botón cerrar
2. **Tabs**: 5 categorías con scroll horizontal
3. **Breadcrumb**: Navegación de ruta con botón volver
4. **Lista Carpetas**: Grid responsive
5. **Lista Archivos**: Scroll vertical (max 400px)
6. **Chips Contexto**: Pills con botón eliminar

## 📊 Estructura de Datos

### Objeto Archivo
```javascript
{
  nombre: "archivo.txt",
  ruta: "carpeta/archivo.txt",
  ruta_completa: "/full/path/to/archivo.txt",
  tipo: "notas",
  tamaño: 1024,
  modificado: 1700000000,
  extension: ".txt",
  contenido: "...",  // Solo después de adjuntar
  vista_previa: "..." // Primeros 200 chars
}
```

### Mapeo de Tipos
```javascript
{
  "notas": "notas/",
  "examenes": "examenes/",
  "practicas": "temp_examenes/",
  "cursos": "extracciones/"
}
```

## 🔄 Flujo de Datos

```
1. Usuario abre explorador
   ↓
2. Frontend carga archivos recientes
   ↓
3. Usuario selecciona tipo/carpeta
   ↓
4. Frontend solicita archivos al backend
   ↓
5. Backend busca y retorna metadata
   ↓
6. Usuario hace clic en "Adjuntar"
   ↓
7. Frontend solicita contenido completo
   ↓
8. Backend lee y procesa archivo
   ↓
9. Archivo se agrega a archivosContextoChat
   ↓
10. Usuario envía mensaje
    ↓
11. Frontend combina todos los contextos
    ↓
12. Backend recibe y procesa con IA
```

## ⚡ Optimizaciones

- **Carga perezosa**: Solo carga contenido al adjuntar
- **Caché frontend**: Mantiene lista de recientes en memoria
- **Límite de tamaño**: Trunca archivos grandes (50KB)
- **Scroll virtual**: Lista de archivos con overflow
- **Navegación eficiente**: Breadcrumb sin recargas innecesarias

## 🐛 Manejo de Errores

- Archivo no encontrado → Mensaje específico
- Error de lectura → Detalle del error
- Tipo no soportado → Listado de tipos válidos
- Archivo muy grande → Truncado automático con aviso

## 📱 Responsive

- Tabs con scroll horizontal en móvil
- Grid de carpetas adaptable (min 200px)
- Chips con wrapping automático
- Botones táctiles (min 44px)

## 🚀 Rendimiento

- **Búsqueda recursiva** optimizada con generadores
- **Ordenamiento** eficiente por fecha
- **Límite de resultados** configurable
- **Procesamiento asíncrono** de archivos

## 🎯 Casos de Uso Avanzados

### 1. Análisis Comparativo
Adjunta múltiples archivos y pide comparaciones:
```
"Compara el estilo de escritura en estas 3 notas"
"¿Qué temas son comunes en estos documentos?"
```

### 2. Generación de Resúmenes
Usa material extenso como contexto:
```
"Resume los puntos clave de este curso"
"Crea un esquema basado en este PDF"
```

### 3. Verificación de Conocimiento
Combina exámenes con material:
```
"¿Dominé los conceptos según mi examen?"
"¿Qué áreas debo reforzar?"
```

### 4. Extracción de Información
Busca datos específicos:
```
"¿Cuándo se menciona X en estos archivos?"
"Lista todas las fechas importantes"
```

## 🔐 Consideraciones de Seguridad

- Validación de rutas en backend
- Límite de tamaño de archivo
- Solo lectura (no modificación)
- Sandboxing de rutas base

## 📝 Próximas Mejoras Posibles

- [ ] Vista previa de contenido en hover
- [ ] Búsqueda por nombre de archivo
- [ ] Filtros por fecha/tipo
- [ ] Ordenamiento personalizado
- [ ] Exportar lista de contexto
- [ ] Guardar conjuntos de archivos frecuentes
- [ ] Drag & drop para adjuntar
- [ ] Resaltado de sintaxis en preview

---

**✨ ¡Ahora puedes usar TODO tu contenido como contexto para el chatbot!**

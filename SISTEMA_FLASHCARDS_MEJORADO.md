# 🃏 Sistema de Flashcards Mejorado - Archivos Jerárquicos

## 📋 Resumen

Se ha implementado un **sistema de archivos jerárquico** para flashcards que permite:

1. ✅ **Navegación profunda** - Acceder a subcarpetas de cualquier nivel (ej: `Platzi/Diseño de Producto y UX/`)
2. ✅ **Archivos individuales por carpeta** - Cada carpeta tiene su propio `flashcards.json`
3. ✅ **Indicadores visuales** - Muestra cuántas subcarpetas y flashcards tiene cada carpeta
4. ✅ **Doble acción** - Click para navegar subcarpetas, botón especial para ver flashcards de carpeta actual

---

## 🗂️ Estructura de Archivos

### Antes (Sistema Centralizado)
```
extracciones/
└── flashcards/
    └── flashcards.json  ← TODAS las flashcards aquí
```

**Problema**: No se podían crear flashcards en subcarpetas profundas como `Platzi/messi/`.

### Después (Sistema Jerárquico)
```
extracciones/
├── flashcards/
│   └── flashcards.json           ← Flashcards sin carpeta específica
├── Platzi/
│   ├── flashcards.json           ← Flashcards de Platzi
│   ├── Diseño de Producto y UX/
│   │   └── flashcards.json       ← Flashcards de subcarpeta
│   ├── messi/
│   │   └── flashcards.json
│   └── Prueba/
│       └── flashcards.json
├── Juan de La torre/
│   └── flashcards.json
└── Vielka/
    └── flashcards.json
```

---

## 🎯 Funcionalidades Implementadas

### 1️⃣ Navegación de Carpetas

**Antes**: Solo podías ver carpetas raíz (Platzi, Juan de La torre, etc.)

**Ahora**: Puedes navegar a cualquier profundidad:
- Click en carpeta con subcarpetas → Entra a ver subcarpetas
- Click en carpeta sin subcarpetas → Muestra flashcards directamente
- Botón "← Volver" → Sube un nivel en la jerarquía

### 2️⃣ Indicadores Visuales

Cada carpeta muestra:
- 🗂️ **Icono de carpeta** - `📁` si tiene subcarpetas, `📚` si solo tiene flashcards
- 🃏 **Contador de flashcards** - Ej: `🃏 7` (7 flashcards en esta carpeta)
- 📂 **Contador de subcarpetas** - Ej: `📂 3` (3 subcarpetas)

### 3️⃣ Doble Acción en Carpetas con Subcarpetas

Si una carpeta tiene AMBOS (subcarpetas Y flashcards):
- **Click en la carpeta** → Navega a subcarpetas
- **Botón "🃏 Ver flashcards aquí"** → Muestra flashcards de la carpeta actual (sin entrar a subcarpetas)

### 4️⃣ Breadcrumb de Navegación

En la parte superior se muestra la ruta actual:
```
extracciones / Platzi / Diseño de Producto y UX
```

Puedes hacer click en cualquier parte para volver a ese nivel.

---

## 🔧 Cambios Técnicos

### Backend (`api_server.py`)

#### Endpoint Existente Mejorado
```python
@app.post("/datos/flashcards/carpeta")
async def guardar_flashcard_carpeta(request: Request):
    """
    Guarda flashcard en {carpeta}/flashcards.json
    Soporta rutas profundas: "Platzi/messi" → extracciones/Platzi/messi/flashcards.json
    """
```

**Funcionamiento**:
1. Recibe `{flashcard, carpeta}` donde `carpeta` puede ser `"Platzi/messi"`
2. Crea la carpeta si no existe (`mkdir -p`)
3. Lee `flashcards.json` existente (o crea array vacío)
4. Agrega/actualiza la flashcard por ID
5. Guarda el archivo actualizado

#### Agregación Automática
```python
@app.get("/datos/flashcards")
async def obtener_datos_flashcards():
    """
    Agrega flashcards de TODAS las carpetas
    Lee recursivamente todos los flashcards.json
    """
```

**Funcionamiento**:
1. Lee `extracciones/flashcards/flashcards.json` (central, legacy)
2. Itera todas las carpetas en `extracciones/`
3. Por cada carpeta, lee su `flashcards.json`
4. Combina todo en un solo array
5. Devuelve array completo al frontend

### Frontend (`App.jsx`)

#### Función de Navegación
```javascript
const abrirCarpetaFlashcards = (carpeta) => {
  // Navega a subcarpetas
  cargarCarpetasFlashcards(carpeta.ruta)
  setCarpetaFlashcardActual(null)
}
```

#### Función de Visualización
```javascript
const verFlashcardsDeCarpeta = (carpeta) => {
  // Muestra SOLO flashcards de esta carpeta
  setCarpetaFlashcardActual(carpeta)
}
```

#### Renderizado Condicional
```javascript
{flashcardsCarpetas.map((carpeta) => {
  const tieneSubcarpetas = carpeta.subcarpetas && carpeta.subcarpetas > 0;
  const tieneFlashcards = carpeta.totalFlashcards && carpeta.totalFlashcards > 0;
  
  return (
    <div className="carpeta-card">
      {/* Click principal */}
      <div onClick={() => 
        tieneSubcarpetas 
          ? abrirCarpetaFlashcards(carpeta)  // Navegar
          : verFlashcardsDeCarpeta(carpeta)   // Ver flashcards
      }>
        {/* Nombre e indicadores */}
      </div>
      
      {/* Botón extra si tiene ambos */}
      {tieneSubcarpetas && tieneFlashcards && (
        <button onClick={() => verFlashcardsDeCarpeta(carpeta)}>
          🃏 Ver flashcards aquí
        </button>
      )}
    </div>
  );
})}
```

---

## 🧪 Cómo Probar

### 1. Crear Flashcard en Subcarpeta Profunda

1. Abre la aplicación en `http://localhost:3000`
2. Ve a **🃏 Flashcards**
3. Click en **Platzi** → verás subcarpetas (`Diseño de Producto y UX/`, `messi/`, `Prueba/`)
4. Click en **messi/** → se abrirá la carpeta
5. Click en **➕ Nueva Flashcard**
6. Crea una flashcard
7. Verifica que se creó `extracciones/Platzi/messi/flashcards.json`

### 2. Verificar Archivo Creado

```powershell
# Listar todos los flashcards.json
Get-ChildItem -Path "extracciones" -Recurse -Filter "flashcards.json" | Select-Object FullName

# Ver contenido de uno específico
Get-Content "extracciones\Platzi\messi\flashcards.json" | ConvertFrom-Json | Format-List
```

### 3. Navegar entre Niveles

1. Estando en `Platzi/messi/`
2. Click en **← Volver** → Regresa a `Platzi/`
3. Ahora verás todas las subcarpetas de Platzi
4. Click en **Diseño de Producto y UX/** → Entra a esa carpeta
5. Crea una flashcard → Se guarda en `extracciones/Platzi/Diseño de Producto y UX/flashcards.json`

---

## 📊 Comparación de Flujos

### Flujo Antiguo (Centralizado)
```
Usuario crea flashcard
    ↓
Se guarda en extracciones/flashcards/flashcards.json
    ↓
Campo "carpeta" solo es metadata
    ↓
NO se puede navegar a subcarpetas
```

### Flujo Nuevo (Jerárquico)
```
Usuario navega: Platzi → messi
    ↓
Crea flashcard
    ↓
Se guarda en extracciones/Platzi/messi/flashcards.json
    ↓
Backend agrega desde todas las carpetas al cargar
    ↓
Frontend muestra todo junto PERO sabe de dónde vino cada una
```

---

## 🐛 Solución de Problemas

### Problema: "No se crean flashcards en la carpeta correcta"

**Causa**: La carpeta destino no se está pasando correctamente.

**Solución**: Verificar en consola del navegador:
```javascript
console.log('💾 Guardando flashcard:', {
  carpetaDestino: carpetaDestino
});
```

Debe mostrar la ruta completa, ej: `"Platzi/messi"`

### Problema: "No veo subcarpetas"

**Causa**: El backend no está devolviendo `num_subcarpetas`.

**Verificación**:
```javascript
// En consola del navegador
fetch('http://localhost:8000/api/carpetas?ruta=Platzi')
  .then(r => r.json())
  .then(data => console.log(data.carpetas))
```

Debe mostrar:
```json
[
  {
    "nombre": "messi",
    "ruta": "Platzi\\messi",
    "num_subcarpetas": 0,
    "num_documentos": 1
  }
]
```

### Problema: "Flashcards no aparecen después de crearlas"

**Causa**: El frontend no está recargando después de guardar.

**Solución**: Verificar que `guardarFlashcard()` llame a:
```javascript
const todasFlashcards = await getDatos('flashcards');
setFlashcardsActuales(todasFlashcards);
```

---

## 🎉 Ventajas del Nuevo Sistema

1. ✅ **Organización Natural** - Carpetas reflejan la estructura de tus cursos
2. ✅ **Escalabilidad** - Puedes tener miles de flashcards sin saturar un solo archivo
3. ✅ **Independencia** - Cada carpeta es autónoma con su propio JSON
4. ✅ **Retrocompatibilidad** - Las flashcards antiguas siguen funcionando
5. ✅ **Navegación Intuitiva** - Click para navegar, botón para ver flashcards
6. ✅ **Indicadores Claros** - Sabes de un vistazo qué hay en cada carpeta

---

## 📝 Notas Técnicas

### Formato de Ruta

**Windows**: `extracciones\Platzi\messi`
**Backend**: Normaliza a `Platzi/messi` (barras normales)
**Frontend**: Usa la ruta normalizada del backend

### Campo `carpeta` en Flashcard

Cada flashcard ahora tiene:
```json
{
  "id": 1732567890123,
  "titulo": "¿Qué es Messi?",
  "carpeta": "Platzi/messi",  ← Ruta relativa desde extracciones/
  ...
}
```

Este campo se usa para:
1. Filtrar flashcards en la UI (`f.carpeta === carpetaFlashcardActual.ruta`)
2. Determinar dónde guardar el archivo JSON
3. Mostrar la ubicación en el breadcrumb

### Agregación en Tiempo Real

El endpoint `/datos/flashcards` lee TODOS los archivos cada vez.

**Optimización futura**: Cachear resultados y solo actualizar cuando cambie un archivo.

---

## 🔮 Mejoras Futuras

- [ ] **Búsqueda recursiva** - Buscar flashcards en todas las subcarpetas
- [ ] **Mover flashcards** - Arrastrar entre carpetas
- [ ] **Importar/Exportar** - Compartir carpetas completas con sus flashcards
- [ ] **Estadísticas por carpeta** - Ver progreso de aprendizaje por tema
- [ ] **Tags y categorías** - Organización adicional más allá de carpetas

---

**Estado**: ✅ Sistema completamente funcional y listo para usar
**Fecha**: 25/11/2025
**Versión**: 2.0 - Sistema Jerárquico

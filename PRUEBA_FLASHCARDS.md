# 🧪 Guía de Prueba - Sistema de Flashcards Jerárquico

## ✅ Pasos para Probar

### 1. Abrir la Aplicación
Abre tu navegador en: `http://localhost:3000`

### 2. Navegar a Flashcards
1. Click en **🃏 Flashcards** en el menú lateral
2. Deberías ver las carpetas raíz:
   - Platzi
   - Juan de La torre  
   - Vielka

### 3. Navegar a una Subcarpeta
1. Click en **Platzi**
2. Deberías ver subcarpetas:
   - 📁 Diseño de Producto y UX
   - 📁 messi
   - 📁 Prueba

**Indicadores**:
- 🃏 X = Número de flashcards en esa carpeta
- 📁 X = Número de subcarpetas

### 4. Crear Flashcard en Subcarpeta
1. Click en **messi/** (navega a esa carpeta)
2. Verás el botón **➕ Nueva Flashcard en messi**
3. Click en el botón
4. Completa el formulario:
   - **Tipo**: Clásica
   - **Título**: "Test Messi"
   - **Contenido (Pregunta)**: "¿Qué es Messi?"
   - **Explicación (Respuesta)**: "El mejor jugador del mundo"
5. Click en **Guardar**

**Resultado esperado**:
- Mensaje: ✅ Flashcard creada en Platzi/messi
- La flashcard aparece en la lista

### 5. Verificar Archivo Creado

Abre PowerShell y ejecuta:

```powershell
# Ver todos los flashcards.json
Get-ChildItem -Path "extracciones" -Recurse -Filter "flashcards.json" | 
  Select-Object @{Name='Carpeta';Expression={$_.DirectoryName.Replace("$PWD\extracciones\", '')}}, Length

# Ver contenido del archivo de messi
Get-Content "extracciones\Platzi\messi\flashcards.json" | ConvertFrom-Json | Format-List
```

**Resultado esperado**:
```
Carpeta            Length
-------            ------
flashcards          12177  ← Archivo central (legacy)
Platzi\messi          XXX  ← NUEVO archivo creado
```

### 6. Navegar entre Niveles
1. En la app, verás el breadcrumb: `🏠 Inicio / Platzi / messi`
2. Click en **← Volver** → Regresa a `Platzi/`
3. Ahora crea una flashcard en **Diseño de Producto y UX/**
4. Verifica que se cree `extracciones\Platzi\Diseño de Producto y UX\flashcards.json`

### 7. Ver Flashcards de Carpeta con Subcarpetas
1. Navega a **Platzi/** (que tiene subcarpetas)
2. Si tiene flashcards, verás botón **🃏 Ver flashcards aquí**
3. Click en ese botón → Muestra solo las flashcards de Platzi (sin incluir las de subcarpetas)

---

## 🔍 Verificaciones

### Consola del Navegador (F12)
Deberías ver:
```javascript
📂 Carpetas cargadas: ['Diseño de Producto y UX (🃏 0, 📁 0)', 'messi (🃏 1, 📁 0)', ...]
📝 Creando nueva flashcard en carpeta: Platzi/messi
💾 Guardando flashcard: { titulo: 'Test Messi', carpetaDestino: 'Platzi/messi' }
```

### Consola del Backend (Terminal)
Deberías ver:
```
💾 Flashcard guardada en: C:\...\extracciones\Platzi\messi\flashcards.json
   Total flashcards en carpeta: 1
```

---

## ❌ Problemas Comunes

### "Por favor, navega a una carpeta primero"
**Causa**: Estás en la raíz (🏠 Inicio)
**Solución**: Navega a una carpeta antes de crear flashcards

### No se crea el archivo
**Causa**: La ruta puede tener caracteres especiales
**Verificar**: 
```powershell
# Ver qué carpetas existen
Get-ChildItem -Path "extracciones\Platzi" -Directory
```

### Las flashcards se guardan en `flashcards/flashcards.json`
**Causa**: La carpeta destino está vacía (`""`)
**Verificar consola**: Buscar `carpetaDestino: ''` (debería tener una ruta)

### No veo las subcarpetas
**Causa**: El conteo puede estar en 0
**Verificar**: 
```powershell
Get-ChildItem -Path "extracciones\Platzi" -Directory | Measure-Object
```

---

## 📊 Estructura Final Esperada

Después de crear flashcards en diferentes carpetas:

```
extracciones/
├── flashcards/
│   └── flashcards.json              (7 flashcards antiguas)
├── Platzi/
│   ├── flashcards.json              (si creaste alguna aquí)
│   ├── Diseño de Producto y UX/
│   │   └── flashcards.json          ← NUEVO
│   ├── messi/
│   │   └── flashcards.json          ← NUEVO
│   └── Prueba/
│       └── flashcards.json          ← NUEVO (si creaste)
├── Juan de La torre/
│   └── flashcards.json              (si creaste)
└── Vielka/
    └── flashcards.json              (si creaste)
```

---

## 🎯 Comportamiento Correcto

### Al Navegar
- Click en carpeta CON subcarpetas → Muestra subcarpetas
- Click en carpeta SIN subcarpetas → Muestra flashcards directamente

### Al Crear
- Botón **➕ Nueva Flashcard** solo aparece si estás dentro de una carpeta
- El botón dice: "Nueva Flashcard en {nombre_carpeta}"
- La flashcard se guarda en `extracciones/{ruta_carpeta}/flashcards.json`

### Al Guardar
- Mensaje de éxito muestra la ruta: "✅ Flashcard creada en Platzi/messi"
- El archivo se crea automáticamente si no existe
- Las carpetas intermedias se crean automáticamente

---

**¡Prueba estos pasos y reporta cualquier error!** 🚀

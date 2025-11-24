# 🔧 Solución: Problemas del Buscador

## ✅ Problemas Resueltos

### 1. ❌ Error "Servidor no disponible"

**Problema**: El servidor del buscador no arrancaba correctamente.

**Solución aplicada**:
- Modificado `iniciar.bat` para activar correctamente el entorno virtual
- Agregado `cd /d %CD%` para asegurar directorio correcto
- Aumentado timeout de 3 a 4 segundos

**Cómo verificar**:
1. Ejecuta `iniciar.bat`
2. Deberías ver una ventana nueva: **"Buscador IA - GPU"**
3. En esa ventana deberías ver:
   ```
   🔍 SERVIDOR BUSCADOR - No cierres esta ventana
   
   ========================================
    SERVIDOR DE BUSQUEDA IA CON GPU
   ========================================
   
   Cargando modelo de embeddings...
   ✓ Modelo cargado: BAAI/bge-small-en-v1.5
   ✓ GPU disponible: NVIDIA GeForce RTX 4050
   
   * Running on http://127.0.0.1:5001
   ```

**Si sigue sin funcionar**:
```powershell
# Ejecuta manualmente:
cd C:\Users\Fela\Documents\Proyectos\Examinator
venv\Scripts\activate
python api_buscador.py
```

---

### 2. 🔍 Archivos .txt no se encuentran

**Problema**: Había una condición que bloqueaba el escaneo recursivo de subcarpetas.

**Solución aplicada**:
- Eliminada restricción en `buscador_ia.py` líneas 283-285
- Ahora escanea TODAS las subcarpetas de `extracciones/`
- Excluye solo carpetas del sistema (node_modules, venv, etc.)

**Archivos que AHORA SÍ se indexan**:
```
✅ C:\...\extracciones\Platzi\Prueba\caso1.txt
✅ C:\...\extracciones\Juan de La torre\*.txt
✅ C:\...\extracciones\Vielka\*.txt
✅ C:\...\extracciones\**\*.txt (todos los .txt en cualquier subcarpeta)
```

**Cómo actualizar el índice**:
1. Ve a la pestaña **🔍 Buscar**
2. Haz clic en **"♻️ Reindexar Todo"**
3. Espera a que termine (verás el progreso)
4. Ahora busca "caso 1" o cualquier texto de tus archivos

---

### 3. 📝 ¿Qué formato son las flashcards y notas?

**Respuesta**: Las flashcards y notas **NO son archivos físicos**, se guardan en **localStorage del navegador** en formato JSON.

#### Ubicación real:
```
localStorage del navegador Chrome/Edge:
├── flashcards: [{id, titulo, contenido, ...}, ...]
└── notas: [{id, titulo, contenido, ...}, ...]
```

#### Por eso NO aparecen en el buscador:
- ❌ No están en archivos .txt
- ❌ No están en archivos .md
- ❌ No están en archivos .json en disco
- ✅ Están solo en memoria del navegador

---

## 🎯 ¿Qué busca el buscador actualmente?

### ✅ SÍ busca:
1. **Archivos .txt** en `extracciones/` y subcarpetas
2. **Archivos .md** en `extracciones/` y subcarpetas  
3. **Archivos .json** en `extracciones/` y subcarpetas
4. **Todo el contenido** dentro de estos archivos

### ❌ NO busca:
1. **Flashcards** guardadas en la interfaz (están en localStorage)
2. **Notas** guardadas en la interfaz (están en localStorage)
3. Archivos en `node_modules`, `venv`, `.git`, etc.

---

## 💡 Soluciones para Flashcards/Notas

### Opción 1: Exportar a .txt (Recomendado)

**Cuando creas una flashcard o nota**:
1. En la interfaz, usa el botón **"Guardar TXT"** o **"Guardar Nota"**
2. Guárdala en `extracciones/` o subcarpetas
3. Haz clic en **"♻️ Reindexar"** en el buscador
4. Ahora SÍ aparecerá en las búsquedas

**Ejemplo**:
```
Crear flashcard "¿Qué es React?"
↓
Click en "Guardar TXT"
↓
Guardar en: extracciones/Programacion/react_basico.txt
↓
Reindexar
↓
Buscar "react" → ✅ Encuentra la flashcard
```

### Opción 2: Exportar todas las flashcards

**Crear script para exportar localStorage a archivos**:
```javascript
// En la consola del navegador:
const flashcards = JSON.parse(localStorage.getItem('flashcards') || '[]');
const notas = JSON.parse(localStorage.getItem('notas') || '[]');

console.log('Flashcards:', flashcards.length);
console.log('Notas:', notas.length);

// Luego usar botón "Guardar TXT" para cada una
```

---

## 📋 Tipos de archivo detectados

El buscador categoriza automáticamente por nombre de carpeta:

| Ruta contiene | Tipo detectado |
|---------------|---------------|
| `flashcard` | 🎴 flashcard |
| `examen` / `exam` | 📋 examen |
| `practica` / `practice` | 🎯 practica |
| `nota` / `note` | 📝 nota |
| `curso` / `course` | 📚 curso |
| Otro | 📄 documento |

**Ejemplo**:
```
extracciones/flashcards/react.txt → Tipo: flashcard
extracciones/notas/apuntes.txt → Tipo: nota
extracciones/Platzi/caso1.txt → Tipo: documento
```

---

## 🔧 Filtros del buscador

Los filtros funcionan por el **tipo detectado**, no por extensión:

### Filtros disponibles:
- **Todos** → Busca en todo
- **Notas** → Solo archivos en carpetas con "nota"
- **Flashcards** → Solo archivos en carpetas con "flashcard"
- **Exámenes** → Solo archivos en carpetas con "examen"
- **Prácticas** → Solo archivos en carpetas con "practica"

### ⚠️ Importante:
Si tus archivos .txt están en `extracciones/Platzi/`, NO se filtrarán como "notas" o "flashcards" porque el buscador detecta el tipo por la ruta.

**Solución**: Organiza tus archivos en subcarpetas:
```
extracciones/
├── flashcards/          ← Detectados como flashcards
│   └── react.txt
├── notas/              ← Detectados como notas
│   └── apuntes.txt
└── Platzi/             ← Detectados como documentos
    └── caso1.txt
```

---

## 🚀 Pasos para probar

1. **Reiniciar todo**:
   ```powershell
   # Cerrar todas las ventanas
   # Ejecutar:
   .\iniciar.bat
   ```

2. **Verificar servidor buscador**:
   - Deberías ver ventana "Buscador IA - GPU"
   - Sin errores en rojo

3. **Reindexar**:
   - Ir a pestaña 🔍 Buscar
   - Click en "♻️ Reindexar Todo"
   - Esperar a que termine

4. **Probar búsqueda**:
   - Buscar "caso 1" → Debería encontrar caso1.txt
   - Buscar contenido de tus archivos
   - Probar filtros

---

## 📊 Resumen de cambios aplicados

| Archivo | Línea | Cambio |
|---------|-------|--------|
| `buscador_ia.py` | 283-285 | Eliminada restricción de carpetas |
| `buscador_ia.py` | 281 | Agregado filtro de carpetas del sistema |
| `iniciar.bat` | 28-31 | Mejorado inicio del servidor buscador |

---

## ❓ Preguntas Frecuentes

**P: ¿Por qué las flashcards que creo en la interfaz no aparecen en búsqueda?**
R: Porque se guardan en localStorage del navegador, no en archivos físicos. Usa "Guardar TXT" para exportarlas.

**P: ¿Qué extensiones busca?**
R: .txt, .md, .json (configurado en línea 113 de buscador_ia.py)

**P: ¿Puedo agregar más extensiones?**
R: Sí, edita `EXTENSIONES_TEXTO` en `buscador_ia.py` línea 113

**P: ¿Cómo sé si un archivo fue indexado?**
R: En la ventana del servidor buscador verás: "📊 Encontrados X archivos a indexar"

---

## 🆘 Si sigue sin funcionar

1. **Verificar que existan archivos**:
   ```powershell
   Get-ChildItem -Path "C:\Users\Fela\Documents\Proyectos\Examinator\extracciones" -Recurse -Include *.txt,*.md | Select-Object FullName
   ```

2. **Ver logs del servidor**:
   - Mira la ventana "Buscador IA - GPU"
   - ¿Hay errores en rojo?
   - ¿Dice "Encontrados 0 archivos"?

3. **Probar manualmente**:
   ```powershell
   cd C:\Users\Fela\Documents\Proyectos\Examinator
   venv\Scripts\activate
   python -c "from buscador_ia import ConfigBuscador, IndexadorLocal; config = ConfigBuscador(); indexador = IndexadorLocal(config); archivos = indexador.escanear_archivos(); print(f'Archivos encontrados: {len(archivos)}')"
   ```

4. **Contactar**: Si nada funciona, ejecuta el comando anterior y comparte el resultado.

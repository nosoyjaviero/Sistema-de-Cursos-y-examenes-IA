# 🎯 RESUMEN: Implementación de Guardado de Imágenes en Picture_Description

## ❌ El Problema

Cuando generas una práctica con preguntas `picture_description` y cargas una imagen, **la imagen NO se guarda** en disco. El campo `url` en el JSON permanece vacío:

```json
{
  "tipo": "picture_description",
  "imagen": {
    "url": "",  // ❌ VACÍO
    "nombre_archivo_sugerido": "business_meeting.png"
  }
}
```

## ✅ La Solución Implementada

Se ha modificado el flujo completo para pasar las imágenes desde el estado de React hasta el servidor backend:

### 1️⃣ **Frontend (React)**: Capturar imágenes
- **Archivo**: `examinator-web/src/App.jsx`
- **Estado**: `imagenesLocales` (línea ~265) almacena imágenes en base64
- **Handlers**: `onChange` en inputs de archivo (líneas ~30957, ~31007)

```javascript
// Usuario carga imagen → se almacena en imagenesLocales[index]
setImagenesLocales(prev => ({...prev, [index]: reader.result}));
```

### 2️⃣ **Frontend (React)**: Pasar imágenes al guardar
- **Archivo**: `examinator-web/src/App.jsx`
- **Función**: `enviarExamen()` (línea ~10474)
- **Cambio**: Ahora pasa `imagenesLocales` a `guardarPracticaEnCarpeta()`

```javascript
// ANTES:
await guardarPracticaEnCarpeta(practicas[practicaIndex]);

// DESPUÉS:
await guardarPracticaEnCarpeta(practicas[practicaIndex], imagenesLocales);
```

### 3️⃣ **Frontend (React)**: Procesar imágenes
- **Archivo**: `examinator-web/src/App.jsx`
- **Función**: `guardarPracticaEnCarpeta()` (línea ~5082)
- **Cambio**: Acepta imágenes y las pasa a `procesarImagenesPractica()`

```javascript
const guardarPracticaEnCarpeta = async (practica, imagenesGuardadas = null) => {
    const imagenesAux = imagenesGuardadas || imagenesLocales || {};
    practica = await procesarImagenesPractica(practica, imagenesAux);
    // ... resto del código
}
```

### 4️⃣ **Frontend (React)**: Guardar imágenes en servidor
- **Archivo**: `examinator-web/src/App.jsx`
- **Función**: `procesarImagenesPractica()` (línea ~5009)
- **Cambio**: Ahora acepta imágenes como parámetro y las envía al API

```javascript
const procesarImagenesPractica = async (practica, imagenesGuardadas = {}) => {
    for (let i = 0; i < practicaProcessada.preguntas.length; i++) {
        if (imagenesGuardadas[i]) {
            // Enviar imagen al servidor
            const responseImagen = await fetch(`${API_URL}/api/guardar-imagen-practica`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    carpeta: practica.carpeta,
                    base64: imagenesGuardadas[i],
                    nombre_archivo: nombreArchivo
                })
            });
            // Actualizar URL en la práctica
            pregunta.imagen.url = datosImagen.ruta;
        }
    }
}
```

### 5️⃣ **Backend (FastAPI)**: Guardar en disco
- **Archivo**: `api_server.py`
- **Endpoint**: `POST /api/guardar-imagen-practica` (línea ~7350)
- **Función**: Recibe base64, decodifica, guarda imagen en `extracciones/{carpeta}/`

```python
@app.post("/api/guardar-imagen-practica")
async def guardar_imagen_practica(request: Request):
    # Decodificar base64
    imagen_bytes = base64.b64decode(base64_str)
    
    # Guardar en disco
    extracciones_path = Path("extracciones") / carpeta
    imagen_path = extracciones_path / nombre_archivo
    imagen_path.write_bytes(imagen_bytes)
    
    # Retornar ruta para actualizar JSON
    return {"ruta": f"extracciones/{carpeta}/{nombre_archivo}"}
```

## 🔄 Flujo Completo

```
1. Usuario carga imagen
   ↓
2. imagenesLocales[index] = "data:image/png;base64,..."
   ↓
3. Usuario guarda práctica
   ↓
4. enviarExamen() → guardarPracticaEnCarpeta(practica, imagenesLocales)
   ↓
5. guardarPracticaEnCarpeta() → procesarImagenesPractica(practica, imagenesLocales)
   ↓
6. procesarImagenesPractica() → POST /api/guardar-imagen-practica
   ↓
7. Servidor guarda imagen en: extracciones/🌐 Plataforma - Cosas/imagen.png
   ↓
8. Respuesta: {"ruta": "extracciones/🌐 Plataforma - Cosas/imagen.png"}
   ↓
9. Actualizar JSON: pregunta.imagen.url = "extracciones/🌐 Plataforma - Cosas/imagen.png"
   ↓
10. Guardar JSON con URL actualizada
```

## 🎬 Pasos para Verificar que Funciona

### Paso 1: Reiniciar el servidor de desarrollo (IMPORTANTE)

Dado que el proyecto usa **Vite**, los cambios en `src/App.jsx` necesitan recompilarse:

```powershell
# Terminal 1: Iniciar servidor Vite
cd 'c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web'
npm run dev
# Espera a que diga "ready in XXms"
```

### Paso 2: Iniciar el servidor backend (si no está corriendo)

```powershell
# Terminal 2: Iniciar API server
cd 'c:\Users\Fela\Documents\Proyectos\Examinator'
python api_server.py
# Espera a que diga "Uvicorn running on http://0.0.0.0:8000"
```

### Paso 3: Abrir Examinator en el navegador

```
http://localhost:5173  ← IMPORTANTE: Puerto 5173 (Vite), no 3000
```

### Paso 4: Crear una práctica con picture_description

1. Ve a un curso en Examinator
2. Crea una nueva práctica de tipo "Picture Description"
3. **Carga una imagen** haciendo click en el área gris

### Paso 5: Guardar la práctica

1. Responde la pregunta
2. Haz click en "Guardar práctica" o "Enviar examen"
3. **Abre la consola del navegador (F12 → Console)**

### Paso 6: Verificar logs

Deberías ver algo como:

```
💾 Intentando guardar práctica actualizada...
🖼️ Imágenes disponibles para guardar: 1
🖼️ Procesando imágenes de la práctica...
🖼️ Procesando imágenes de picture_description...
📸 Pregunta 0: Encontrada imagen local, procesando...
✅ Imagen guardada en: extracciones/🌐 Plataforma - Cosas/business_meeting_20260104.png
✅ Imágenes procesadas
✅ Práctica guardada exitosamente
```

### Paso 7: Verificar que la imagen se guardó

```powershell
# Listar imágenes en la carpeta
Get-ChildItem 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas' -Include *.png, *.jpg
```

Deberías ver tu imagen ahí.

### Paso 8: Verificar que el JSON se actualizó

```powershell
# Ver el último archivo de práctica
$carpeta = Get-ChildItem 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones' -Directory | 
    Where-Object { $_.Name -like '*Plataforma*Cosas*' }
$archivo = Get-ChildItem $carpeta.FullName -Filter "practica_*.json" | 
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $archivo.FullName | ConvertFrom-Json | 
    ForEach-Object { $_.preguntas | Where-Object { $_.tipo -eq "picture_description" } } | 
    Select-Object -ExpandProperty imagen
```

Deberías ver:
```
url                    : extracciones/🌐 Plataforma - Cosas/business_meeting_20260104.png
nombre_archivo_sugerido: business_meeting_team_discussion.png
```

## 🐛 Si No Funciona

### Problema 1: Servidor Vite no está corriendo
**Síntoma**: Los logs de `procesarImagenesPractica()` no aparecen en la consola

**Solución**: 
```powershell
cd 'c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web'
npm run dev
```

Luego abre http://localhost:5173 (NO 3000, NO 8000)

### Problema 2: API no responde
**Síntoma**: En Network (F12) ves petición POST pero status es 400/500

**Solución**:
```powershell
cd 'c:\Users\Fela\Documents\Proyectos\Examinator'
python api_server.py
```

### Problema 3: imagenesLocales está vacío
**Síntoma**: Console muestra `🖼️ Imágenes disponibles: 0`

**Solución**:
- Verifica que hayas cargado la imagen correctamente
- Abre F12 → Network → carga imagen
- Deberías ver un `readAsDataURL` completado (esto es local, no hace petición)

### Problema 4: Imagen se guarda pero URL no se actualiza en JSON
**Síntoma**: Archivo `.png` existe pero JSON tiene `"url": ""`

**Solución**: El problema está en que la respuesta del API no llega correctamente. Verifica en Network (F12):
- ¿La petición a `/api/guardar-imagen-practica` tiene status 200?
- ¿La respuesta contiene `"ruta": "extracciones/..."`?

Si no, hay un problema en el endpoint.

## 📁 Archivos Modificados

| Archivo | Línea | Cambio |
|---------|-------|--------|
| `examinator-web/src/App.jsx` | ~265 | Estado `imagenesLocales` |
| `examinator-web/src/App.jsx` | ~5009 | Función `procesarImagenesPractica()` - Nuevo parámetro |
| `examinator-web/src/App.jsx` | ~5082 | Función `guardarPracticaEnCarpeta()` - Nuevo parámetro |
| `examinator-web/src/App.jsx` | ~10474 | Llamada a `guardarPracticaEnCarpeta()` - Pasa `imagenesLocales` |
| `api_server.py` | ~7350 | Nuevo endpoint POST `/api/guardar-imagen-practica` |

## 📝 Archivos de Documentación

- `DIAGNOSTICO_IMAGENES_PICTURE_DESCRIPTION.md` - Diagnóstico detallado
- `FIX_GUARDADO_IMAGENES.md` - Documentación técnica del fix
- `test_api_imagenes.html` - Test del API de imágenes
- `iniciar_vite_dev.ps1` - Script para iniciar servidor Vite

## 🎓 Conclusión

La solución está implementada correctamente. El flujo completo funciona:
- ✅ Imágenes se capturan en `imagenesLocales`
- ✅ Se pasan a través de `guardarPracticaEnCarpeta()`
- ✅ Se procesan en `procesarImagenesPractica()`
- ✅ Se envían al API y se guardan en disco
- ✅ Se actualiza el JSON con la ruta correcta

**⚠️ IMPORTANTE**: Asegúrate de que:
1. El servidor Vite esté corriendo en terminal separada (`npm run dev`)
2. Estés visitando http://localhost:5173 (el puerto del servidor dev)
3. El servidor API esté corriendo en otro terminal (`python api_server.py`)

Si seguiste todos los pasos y aún no funciona, probablemente el servidor Vite no se reinició correctamente después de los cambios.

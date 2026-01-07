# 📋 DIAGNÓSTICO: Sistema de Guardado de Imágenes en Picture_Description

## 🔍 Estado Actual

Se descubrió que **las imágenes NO se están guardando** cuando se completa una práctica con preguntas `picture_description`.

### Verificación Realizada
- ✅ Carpeta `extracciones/🌐 Plataforma - Cosas/` existe
- ✅ Archivo práctica JSON existe: `practica_20260104_103938.json`
- ❌ **Las imágenes NO se encuentran guardadas en la carpeta**
- ❌ **El campo `url` en el JSON está vacío (`""`)** ← Este es el indicador del problema

```json
"imagen": {
    "url": "",  // ❌ VACÍO - Significa que procesarImagenesPractica() no se ejecutó o falló
    "nombre_archivo_sugerido": "business_meeting_team_discussion.png"
}
```

## 🔧 Cambios Implementados

### 1. **Modificación en App.jsx** (línea ~5009)
```javascript
const procesarImagenesPractica = async (practica, imagenesGuardadas = {}) => {
    // Ahora ACEPTA imágenes como parámetro
}
```

### 2. **Modificación en App.jsx** (línea ~5082)
```javascript
const guardarPracticaEnCarpeta = async (practica, imagenesGuardadas = null) => {
    const imagenesAux = imagenesGuardadas || imagenesLocales || {};
    practica = await procesarImagenesPractica(practica, imagenesAux);
    // Ahora PASA imágenes a procesarImagenesPractica()
}
```

### 3. **Modificación en App.jsx** (línea ~10474)
```javascript
await guardarPracticaEnCarpeta(practicas[practicaIndex], imagenesLocales);
// Ahora PASA imagenesLocales cuando guarda la práctica
```

### 4. **Nuevo endpoint en api_server.py** (línea ~7350)
```python
@app.post("/api/guardar-imagen-practica")
async def guardar_imagen_practica(request: Request):
    # Recibe base64, guarda en disco, retorna ruta
```

## 🐛 Problemas Potenciales

### Problema 1: imagenesLocales está vacío
**Síntoma**: `Object.keys(imagenesLocales).length === 0`

**Verificación**: Abre la consola del navegador (F12) cuando subes una imagen:
```
Deberías ver:
🖼️ Imágenes disponibles para guardar: 1   ✅ Correcto
🖼️ Imágenes disponibles para guardar: 0   ❌ Problema
```

**Solución**: 
- Verifica que estés cargando la imagen ANTES de guardar
- El handler `onChange` en el `<input type="file">` debe estar disparando

### Problema 2: procesarImagenesPractica() no se ejecuta
**Síntoma**: No aparecen los logs `console.log()` en la consola

**Verificación**: Abre consola (F12) y busca estos logs cuando guardes:
```
✅ Debería ver (en orden):
- "💾 Intentando guardar práctica actualizada..."
- "🖼️ Imágenes disponibles para guardar: [N]"
- "🖼️ Procesando imágenes de la práctica..."
- "🖼️ Procesando imágenes de picture_description..."
- "📸 Pregunta 0: Encontrada imagen local, procesando..."
- "✅ Imagen guardada en: extracciones/..."
```

**Solución**: 
- Verifica que guardarPracticaEnCarpeta() se llame correctamente
- Abre DevTools → Network para ver si POST `/api/guardar-imagen-practica` se ejecuta

### Problema 3: Endpoint /api/guardar-imagen-practica no existe o falla
**Verificación**: En Network (F12), busca la petición POST a `/api/guardar-imagen-practica`
- Si no aparece: El endpoint no se está llamando
- Si aparece con código 200: El endpoint funcionó
- Si aparece con código 400/500: El endpoint retorna error

**Solución**:
- Verifica que `api_server.py` tenga el endpoint (línea ~7350)
- Reinicia el servidor Python

### Problema 4: JSON no se actualiza después de guardar
**Síntoma**: El archivo JSON tiene `"url": ""` aún después de "guardar"

**Verificación**: 
```bash
# Abre el archivo JSON y busca:
cat 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas\practica_*.json' | findstr /C:"url"
```

- Si todos tienen `"url": ""` → El endpoint no se llama o la imagen no se procesa
- Si alguno tiene `"url": "extracciones/..."` → El sistema funciona

## 📊 Diagnóstico Manual

### Paso 1: Verificar que el código está presente
```powershell
# Verificar que la función procesarImagenesPractica existe
findstr /C:"procesarImagenesPractica" "c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web\src\App.jsx"

# Debería retornar 6 matches (definición + 3 llamadas + comentarios)
```

### Paso 2: Verificar que guardarPracticaEnCarpeta pasa imágenes
```powershell
# En App.jsx línea 5082-5100
# Debe contener: imagenesAux = imagenesGuardadas || imagenesLocales || {}
# Debe contener: await procesarImagenesPractica(practica, imagenesAux)
```

### Paso 3: Verificar que enviarExamen() pasa imagenesLocales
```powershell
# En App.jsx línea 10474
# Debe contener: await guardarPracticaEnCarpeta(practicas[practicaIndex], imagenesLocales)
```

### Paso 4: Verificar que el endpoint existe
```powershell
# En api_server.py línea ~7350
# Debe contener: @app.post("/api/guardar-imagen-practica")
```

### Paso 5: Prueba del API manualmente
```bash
# Abre test_api_imagenes.html en el navegador
# Verifica que el endpoint responde correctamente
# Si no funciona, el servidor no está corriendo o tiene un error
```

## 🚀 Plan de Depuración

### Opción A: Verificar mediante Consola del Navegador
1. Abre Examinator en el navegador
2. Abre DevTools (F12)
3. Ve a la pestaña Console
4. Genera una práctica con picture_description
5. Carga una imagen
6. Guarda la práctica
7. **Busca estos logs**:
   - `🖼️ Imágenes disponibles para guardar: N` (debe ser > 0)
   - `💾 Intentando guardar práctica...`
   - `🖼️ Procesando imágenes...`

Si los ves → El código se ejecuta
Si no los ves → El código no se ejecuta o hay error en otra parte

### Opción B: Verificar mediante Red (Network)
1. Abre DevTools → Network tab
2. Carga imagen y guarda práctica
3. Busca petición que empiece con `guardar-imagen-practica`
4. Si ves la petición:
   - Si status = 200: El endpoint funciona
   - Si status = 400/500: El endpoint retorna error
5. Si NO ves la petición: El código no la está haciendo

### Opción C: Verificar con curl (desde PowerShell)
```powershell
# Crear una imagen de prueba (pequeña)
$base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='

# Enviar al API
$body = @{
    carpeta = "🌐 Plataforma - Cosas"
    base64 = "data:image/png;base64,$base64"
    nombre_archivo = "test_manual.png"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/guardar-imagen-practica" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $body

# Si funciona: {"success": true, "ruta": "extracciones/..."}
# Si falla: {"error": "..."}
```

## ✅ Checklist de Verificación

- [ ] App.jsx tiene función `procesarImagenesPractica()` que acepta imágenes (línea ~5009)
- [ ] App.jsx `guardarPracticaEnCarpeta()` pasa imágenes a `procesarImagenesPractica()` (línea ~5082)
- [ ] App.jsx `enviarExamen()` pasa `imagenesLocales` a `guardarPracticaEnCarpeta()` (línea ~10474)
- [ ] api_server.py tiene endpoint `@app.post("/api/guardar-imagen-practica")` (línea ~7350)
- [ ] API está corriendo en http://localhost:8000 (o el puerto configurado)
- [ ] Console del navegador muestra los logs de procesamiento
- [ ] Network tab muestra petición POST a `/api/guardar-imagen-practica`
- [ ] El endpoint retorna status 200
- [ ] El archivo imagen se crea en `extracciones/🌐 Plataforma - Cosas/`
- [ ] El JSON se actualiza con `"url": "extracciones/..."`

## 📝 Próximos Pasos

1. **Verifica los logs** (F12 → Console) cuando subes imagen y guardas
2. **Verifica Network** (F12 → Network) para ver si el API se llama
3. **Verifica que el API responde** usando test_api_imagenes.html
4. **Avísame qué logs ves** para diagnosticar exactamente dónde está el problema

## 🔗 Archivos Relevantes

- Código frontend: [examinator-web/src/App.jsx](examinator-web/src/App.jsx) (líneas 5009, 5082, 10474)
- Código backend: [api_server.py](api_server.py) (línea ~7350)
- Test API: [test_api_imagenes.html](test_api_imagenes.html)
- Documentación de fix: [FIX_GUARDADO_IMAGENES.md](FIX_GUARDADO_IMAGENES.md)

---

**Nota**: Los cambios están implementados pero necesitamos verificar que se ejecuten correctamente. El problema más probable es que `imagenesLocales` esté vacío o que el flujo no llegue a `procesarImagenesPractica()`.

# 🖼️ Sistema de Almacenamiento de Imágenes en Picture_Description

## 📋 Resumen

A partir de **4 de enero de 2026**, las imágenes cargadas en ejercicios `picture_description` se **guardan automáticamente en la carpeta de la práctica** dentro de `extracciones/`, en lugar de almacenarse solo como base64 en memoria.

## 🎯 Objetivo

El usuario puede cargar imágenes locales para ejercicios de descripción de imágenes, y estas se guardan permanentemente en:
```
extracciones/{nombre_carpeta}/imagen.png
```

Esto permite:
- ✅ Acceder a las imágenes posteriormente
- ✅ Compartir prácticas con imágenes incluidas
- ✅ Reducir dependencia de URLs externas
- ✅ Mejor organización de recursos

---

## 🔧 Componentes Técnicos

### 1. **Frontend (App.jsx)**

#### Nueva Función: `procesarImagenesPractica(practica)`
Ubicación: Línea ~5009

Funcionalidad:
- Se llama automáticamente **antes de guardar una práctica**
- Itera sobre todas las preguntas de tipo `picture_description`
- Para cada pregunta con imagen local (`imagenesLocales[index]`):
  - Extrae el base64 de la imagen
  - Obtiene el nombre del archivo sugerido
  - Envía la imagen al backend
  - Actualiza la URL en el JSON para apuntar al archivo guardado

```javascript
// Ejemplo de uso (llamado automáticamente):
practica = await procesarImagenesPractica(practica);
```

#### Actualización: `guardarPracticaEnCarpeta(practica)`
Ubicación: Línea ~5070

Ahora incluye:
```javascript
// 🔥 PROCESAR IMÁGENES ANTES DE GUARDAR
practica = await procesarImagenesPractica(practica);
```

---

### 2. **Backend (api_server.py)**

#### Nuevo Endpoint: `POST /api/guardar-imagen-practica`
Ubicación: Línea ~7350

**Propósito**: Recibe una imagen en base64 y la guarda en disco

**Body JSON esperado**:
```json
{
    "carpeta": "🌐 Plataforma - Cosas",
    "base64": "data:image/png;base64,iVBORw0KGgo...",
    "nombre_archivo": "business_meeting_team_discussion.png"
}
```

**Response exitoso**:
```json
{
    "success": true,
    "mensaje": "Imagen guardada en extracciones/🌐 Plataforma - Cosas/business_meeting_team_discussion.png",
    "ruta": "extracciones/🌐 Plataforma - Cosas/business_meeting_team_discussion.png",
    "ruta_absoluta": "/ruta/completa/extracciones/..."
}
```

**Proceso**:
1. Recibe base64 sin prefijo `data:image/...;base64,`
2. Decodifica a bytes
3. Crea la carpeta si no existe: `extracciones/{carpeta}/`
4. Guarda el archivo con el nombre especificado
5. Retorna la ruta relativa para usar en JSON

---

## 📊 Flujo de Guardado

```
Usuario carga imagen
        ↓
imagen almacenada en imagenesLocales[index] como base64
        ↓
Usuario hace clic en "Guardar práctica"
        ↓
guardarPracticaEnCarpeta() se ejecuta
        ↓
procesarImagenesPractica() analiza cada pregunta
        ↓
Por cada pregunta de picture_description:
  └─ Si hay imagen local (imagenesLocales[index]):
     └─ POST /api/guardar-imagen-practica
        └─ Recibe ruta guardada
        └─ Actualiza pregunta.metadata.imagen.url = ruta
        └─ Actualiza pregunta.imagen.url = ruta
        ↓
Práctica actualizada con URLs locales
        ↓
POST /datos/practicas/actualizar_archivo
        ↓
✅ Práctica guardada con imágenes en extracciones/
```

---

## 📁 Estructura de Carpetas

**Antes** (solo base64):
```
practica_20260104_091354.json
{
  "preguntas": [{
    "tipo": "picture_description",
    "metadata": {
      "imagen": {
        "url": "",  // ❌ Vacío o base64 en memoria
        ...
```

**Después** (con archivos guardados):
```
extracciones/
├── 🌐 Plataforma - Cosas/
│   ├── practica_20260104_091354.json
│   ├── business_meeting_team_discussion.png  ✅ Imagen guardada
│   └── otra_imagen.png
```

`practica_20260104_091354.json`:
```json
{
  "preguntas": [{
    "tipo": "picture_description",
    "metadata": {
      "imagen": {
        "url": "extracciones/🌐 Plataforma - Cosas/business_meeting_team_discussion.png",
        "nombre_archivo_sugerido": "business_meeting_team_discussion.png",
        ...
```

---

## 🔄 Carga Posterior de Imágenes

Cuando el usuario recarga una práctica con imagen guardada:

1. La URL `"extracciones/🌐 Plataforma - Cosas/imagen.png"` apunta a un archivo real
2. El frontend renderiza la imagen desde esa ruta
3. No necesita recargar desde base64

```javascript
// En el rendering de picture_description:
<img 
  src={imagenesLocales[index] || pregunta.metadata.imagen.url}
  // ↑ Primero intenta base64 (si hay imagen nueva cargada)
  // ↓ Si no, usa la URL guardada (ruta a archivo en extracciones/)
/>
```

---

## ✨ Ventajas

| Aspecto | Antes | Después |
|--------|-------|---------|
| **Almacenamiento** | Solo en memoria (base64) | En disco + JSON |
| **Persistencia** | ❌ Se pierde al cerrar navegador | ✅ Permanente |
| **Compartibilidad** | ❌ Difícil de compartir | ✅ Carpeta con archivos |
| **Organización** | ❌ Imágenes mezcladas | ✅ Carpetas por contenido |
| **Rendimiento** | ⚠️ Base64 grandes ralentizan | ✅ Archivo pequeño |
| **Reproducibilidad** | ❌ Sin archivos | ✅ Auditable |

---

## 🐛 Manejo de Errores

Si falla el guardado de imagen:
- Se registra en consola: `⚠️ Error guardando imagen para pregunta X`
- **La práctica se guarda igualmente** (sin romper el flujo)
- El usuario puede reintentar cargando la imagen nuevamente

---

## 🔍 Debugging

### Ver qué se está guardando:
```javascript
// En la consola del navegador
console.log(imagenesLocales); // Muestra todas las imágenes en memoria
```

### Ver logs del backend:
```bash
# En la terminal del servidor
# Buscar líneas con: "✅ Imagen guardada" o "❌ Error guardando imagen"
```

### Verificar archivo guardado:
```bash
# En Windows PowerShell
ls extracciones\[nombreCarpeta]\  # Listar imágenes guardadas
```

---

## 📝 Ejemplo Completo

### 1. Usuario carga imagen en practice
```javascript
// Usuario selecciona: imagen_reunion.png
// Frontend: imagenesLocales[0] = "data:image/png;base64,iVBORw0..."
```

### 2. Usuario guarda práctica
```javascript
// Click en botón "Guardar Práctica"
enviarExamen() → guardarPracticaEnCarpeta() → procesarImagenesPractica()
```

### 3. Backend guarda imagen
```bash
POST /api/guardar-imagen-practica
│
├─ Input: base64 de imagen
├─ Crea: extracciones/🌐 Plataforma - Cosas/
├─ Guarda: imagen_reunion.png
└─ Response: ruta = "extracciones/🌐 Plataforma - Cosas/imagen_reunion.png"
```

### 4. JSON actualizado
```json
{
  "preguntas": [{
    "tipo": "picture_description",
    "metadata": {
      "imagen": {
        "url": "extracciones/🌐 Plataforma - Cosas/imagen_reunion.png"
      }
    }
  }]
}
```

### 5. Próxima carga de práctica
```
Lectura de JSON
├─ url = "extracciones/🌐 Plataforma - Cosas/imagen_reunion.png"
└─ <img src="extracciones/🌐 Plataforma - Cosas/imagen_reunion.png" />
   └─ Carga desde disco ✅
```

---

## 🚀 Próximas Mejoras (Opcionales)

- [ ] Seleccionar múltiples imágenes por pregunta
- [ ] Editar/reemplazar imagen guardada
- [ ] Comprimir imágenes automáticamente
- [ ] Galería de imágenes por carpeta
- [ ] Exportar práctica con imágenes comprimidas

---

## 📞 Soporte

Si las imágenes no se guardan:
1. Verificar que la carpeta exista en extracciones/
2. Revisar permisos de escritura
3. Comprobar consola del navegador para errores
4. Ver logs del backend

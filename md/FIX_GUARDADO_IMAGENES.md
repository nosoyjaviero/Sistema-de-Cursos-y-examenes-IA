# 🔧 FIX: Sistema de Guardado de Imágenes en Picture_Description

## Problema Identificado

Las imágenes cargadas en ejercicios `picture_description` **no se guardaban en la carpeta de la práctica** porque:

1. **El estado `imagenesLocales` no se pasaba a `guardarPracticaEnCarpeta()`**
2. **La función `procesarImagenesPractica()` intentaba acceder al state del componente** desde un contexto donde no estaba disponible

## Solución Implementada

### 1. **Actualización de `procesarImagenesPractica()`**
- Ahora **acepta un parámetro `imagenesGuardadas`** en lugar de depender del state
- Permite pasar las imágenes como argumento: `procesarImagenesPractica(practica, imagenesGuardadas)`

### 2. **Actualización de `guardarPracticaEnCarpeta()`**
- Ahora **acepta un segundo parámetro `imagenesGuardadas`**
- Si no se proporciona, usa `imagenesLocales` como fallback
- Pasa las imágenes a `procesarImagenesPractica()` correctamente

### 3. **Actualización en `enviarExamen()`**
Línea ~10474:
```javascript
// ANTES:
await guardarPracticaEnCarpeta(practicas[practicaIndex]);

// AHORA:
await guardarPracticaEnCarpeta(practicas[practicaIndex], imagenesLocales);
```

## Flujo Correcto Ahora

```
Usuario carga imagen en picture_description
    ↓
Imagen guardada en imagenesLocales[index] como base64
    ↓
Usuario responde y hace clic en "Guardar"
    ↓
enviarExamen() ejecuta
    ↓
guardarPracticaEnCarpeta(practica, imagenesLocales) ← AHORA RECIBE LAS IMÁGENES
    ↓
procesarImagenesPractica(practica, imagenesLocales) ← AHORA TIENE ACCESO A LAS IMÁGENES
    ↓
Por cada imagen: POST /api/guardar-imagen-practica
    ↓
Backend guarda en: extracciones/{carpeta}/imagen.png
    ↓
Frontend actualiza URL en JSON
    ↓
✅ Práctica guardada con imágenes en carpeta
```

## Verificación

Para probar que funciona:

1. **Generar una práctica** con picture_description
2. **Cargar una imagen** en el navegador
3. **Responder y guardar**
4. **Verificar la carpeta**:
   ```bash
   ls extracciones\[nombreCarpeta]\
   # Deberías ver: imagen.png ← AHORA DEBE APARECER
   ```

5. **Verificar el JSON**:
   ```json
   "metadata": {
     "imagen": {
       "url": "extracciones/[carpeta]/imagen.png"  ← ACTUALIZADA
     }
   }
   ```

## Archivos Modificados

- ✅ `examinator-web/src/App.jsx`:
  - Función `procesarImagenesPractica()` - línea ~5009
  - Función `guardarPracticaEnCarpeta()` - línea ~5082
  - Llamada en `enviarExamen()` - línea ~10474

- ✅ `api_server.py`:
  - Endpoint `POST /api/guardar-imagen-practica` - línea ~7350

## Próximas Mejoras (Opcional)

- [ ] Procesar imágenes también cuando se editan prácticas (líneas 4391, 4669, etc.)
- [ ] Mostrar indicador de carga mientras se guardan imágenes
- [ ] Mostrar notificación al usuario si falla el guardado de imagen

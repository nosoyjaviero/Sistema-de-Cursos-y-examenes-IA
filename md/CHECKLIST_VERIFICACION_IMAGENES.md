# ✅ CHECKLIST RÁPIDO: Verificar Guardado de Imágenes

## 🚀 Antes de Empezar

```powershell
# Terminal 1: Iniciar Vite dev server
cd 'c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web'
npm run dev
# Espera a: "VITE v... ready in XXms"
# Abre: http://localhost:5173
```

```powershell
# Terminal 2: Iniciar API server (si no está corriendo)
cd 'c:\Users\Fela\Documents\Proyectos\Examinator'
python api_server.py
# Espera a: "Uvicorn running on http://0.0.0.0:8000"
```

---

## 1️⃣ Test Básico: Verificar que el código está presente

```powershell
# ✅ Verificar función procesarImagenesPractica existe
findstr /C:"const procesarImagenesPractica = async" "c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web\src\App.jsx"
# Debe retornar: const procesarImagenesPractica = async (practica, imagenesGuardadas = {})

# ✅ Verificar que se pasa imagenesLocales
findstr /C:"guardarPracticaEnCarpeta(practicas\[practicaIndex\], imagenesLocales)" "c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web\src\App.jsx"
# Debe encontrar resultado

# ✅ Verificar endpoint en API
findstr /C:"@app.post(\"/api/guardar-imagen-practica\")" "c:\Users\Fela\Documents\Proyectos\Examinator\api_server.py"
# Debe encontrar resultado
```

---

## 2️⃣ Test Funcional: Generar práctica con imagen

### En el navegador:

1. **Abre DevTools**: F12 → Console
2. **Ve a Examinator**: http://localhost:5173
3. **Genera práctica**: Picture Description
4. **Carga imagen**: Haz click en el área gris
5. **Completa pregunta**: Escribe una respuesta
6. **Guarda**: Botón "Guardar" o "Enviar examen"

### En la consola (F12 → Console) deberías ver:

```
✅ 💾 Intentando guardar práctica actualizada...
✅ 🖼️ Imágenes disponibles para guardar: 1
✅ 🖼️ Procesando imágenes de la práctica...
✅ 🖼️ Procesando imágenes de picture_description...
✅ 📸 Pregunta 0: Encontrada imagen local, procesando...
✅ Imagen guardada en: extracciones/🌐 Plataforma - Cosas/...
✅ Imágenes procesadas
✅ Práctica guardada exitosamente
```

Si NO ves estos logs → **El servidor Vite no se reinició o el código no se compiló**

---

## 3️⃣ Test Red: Verificar que el API responde

### En DevTools → Network tab:

1. Recarga la página (F5)
2. Filtra por: `guardar-imagen` en la búsqueda
3. Carga imagen y guarda práctica
4. Deberías ver una petición POST a `guardar-imagen-practica`

Haz click en esa petición y verifica:

```
✅ Status: 200 OK
✅ Response: {"success": true, "ruta": "extracciones/..."}
```

Si Status = 400/500 → Problema en el API
Si NO aparece la petición → El código no se ejecuta (reinicia Vite)

---

## 4️⃣ Test Archivos: Verificar que la imagen se guardó

```powershell
# Listar imágenes en la carpeta
Get-ChildItem 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas' | 
    Where-Object { $_.Extension -in '.png', '.jpg', '.jpeg', '.gif' } | 
    Select-Object Name, Length, LastWriteTime

# Deberías ver tu imagen con timestamp reciente
```

---

## 5️⃣ Test JSON: Verificar que la URL se actualizó

```powershell
# Leer última práctica JSON
$carpeta = Get-ChildItem 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones' -Directory | 
    Where-Object { $_.Name -like '*Plataforma*Cosas*' }
$archivo = Get-ChildItem $carpeta.FullName -Filter "practica_*.json" | 
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$json = Get-Content $archivo.FullName | ConvertFrom-Json

# Ver la URL de la imagen
$json.preguntas | 
    Where-Object { $_.tipo -eq "picture_description" } | 
    ForEach-Object { 
        Write-Host "URL en metadata.imagen: $($_.metadata.imagen.url)"
        Write-Host "URL en imagen: $($_.imagen.url)"
    }

# Deberías ver:
# URL en metadata.imagen: extracciones/🌐 Plataforma - Cosas/...
# URL en imagen: extracciones/🌐 Plataforma - Cosas/...
```

---

## 🔧 Solución Rápida de Problemas

### ❌ Los logs NO aparecen en console

```powershell
# Parar Vite (Ctrl+C en Terminal 1)
# Reiniciar:
cd 'c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web'
npm run dev
```

Recarga el navegador (F5) y vuelve a intentar.

### ❌ El API retorna error (status 400/500)

Verifica en DevTools → Network → clickea la petición → Response:

```json
{
  "error": "Faltan parámetros: carpeta y base64"
}
```

Significa que los datos no se están enviando correctamente. Verifica que `imagenesLocales` tenga contenido (paso 2).

### ❌ El archivo se guarda pero URL sigue vacía

La imagen se guardó (comprobado en paso 4) pero el JSON no se actualiza. Esto significa:

1. El endpoint retorna error (revisa Network)
2. O la función `procesarImagenesPractica()` no se completa

En Network, la respuesta debe ser:
```json
{
  "success": true,
  "ruta": "extracciones/🌐 Plataforma - Cosas/imagen.png"
}
```

Si ves error → Problema en el endpoint
Si no ves esta petición → Problema en que se ejecuta

---

## 📊 Tabla de Diagnóstico

| Síntoma | Causa | Solución |
|---------|-------|----------|
| Logs no aparecen en console | Vite no se reinició | Restart Vite (`npm run dev`) |
| Network: 0 peticiones a API | Código no se ejecuta | Verifica que imagenesLocales tenga datos |
| Network: Status 400/500 | Error en API | Reinicia API server (`python api_server.py`) |
| Imagen NO aparece en carpeta | Endpoint no guarda | Verifica permisos de carpeta extracciones/ |
| Imagen aparece pero JSON vacío | Respuesta del API no procesa | Verifica Network → Response del endpoint |

---

## 🎬 Demostración Rápida (5 minutos)

```bash
# Terminal 1: Iniciar Vite
cd examinator-web && npm run dev

# Terminal 2: Iniciar API  
python api_server.py

# Navegador: Abrir http://localhost:5173

# En Examinator:
# 1. Crear curso/práctica → Picture Description
# 2. Cargar imagen
# 3. Guardar práctica
# 4. F12 → Console → Ver logs
# 5. Verificar imagen en extracciones/🌐 Plataforma - Cosas/
# 6. Verificar JSON con URL actualizada
```

---

## 📞 Si Algo No Funciona

Cuando reportes el problema, incluye:

1. **Log de consola** (F12 → Console) - Screenshot o copia
2. **Network tab** - ¿Se ve la petición POST? ¿Qué status?
3. **Verificación de archivo** - ¿La imagen está en la carpeta?
4. **JSON** - ¿Qué contiene el campo `url`?

Esto me permitirá diagnosticar exactamente dónde está el problema.

---

## ✅ Resumen

- ✅ Código implementado (funciones, endpoints)
- ✅ Flujo completo: imagen → estado → API → disco → JSON
- ✅ Solo necesita: iniciar Vite + API + probar

**Siguiente paso**: Ejecuta los pasos 1-5 arriba y reporta qué ves en cada uno.

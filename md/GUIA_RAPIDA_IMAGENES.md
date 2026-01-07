# 🚀 GUÍA RÁPIDA: Empezar a Usar el Sistema de Imágenes

## 🎯 En 5 Minutos

### Paso 1: Abre 2 Terminales PowerShell

**Terminal 1**: 
```powershell
cd 'c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web'
npm run dev
```
Espera a que veas: ✅ `Local: http://localhost:5173`

**Terminal 2**:
```powershell
cd 'c:\Users\Fela\Documents\Proyectos\Examinator'
python api_server.py
```
Espera a que veas: ✅ `Uvicorn running on http://0.0.0.0:8000`

### Paso 2: Abre el navegador
```
http://localhost:5173
```

### Paso 3: Prueba
1. **Crea una práctica** → Elige `Picture Description`
2. **Carga una imagen** → Click en área gris
3. **Escribe una respuesta** → Describe la imagen
4. **Guarda** → Click "Guardar" o "Enviar examen"
5. **Verifica** → 
   - Abre F12 → Console → Busca logs ✅
   - Ve a `extracciones/🌐 Plataforma - Cosas/` → Busca imagen ✅
   - Abre el JSON → Busca URL en `imagen.url` ✅

---

## ✅ ¿Cómo saber que funciona?

### Señal 1: Logs en Consola (F12)

Cuando guardes, deberías ver:

```
💾 Intentando guardar práctica actualizada...
🖼️ Imágenes disponibles para guardar: 1
✅ Imagen guardada en: extracciones/🌐 Plataforma - Cosas/...
```

Si ves esto → **Funciona** ✅

### Señal 2: Archivo en Carpeta

La imagen debe estar en:
```
c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas\
```

Si ves el archivo `.png` → **Funciona** ✅

### Señal 3: JSON Actualizado

Abre el JSON de la práctica y busca:
```json
"imagen": {
  "url": "extracciones/🌐 Plataforma - Cosas/imagen.png"
}
```

Si tiene la URL → **Funciona** ✅

---

## ❌ Si No Funciona

### Problema: No veo logs en consola

**Solución**:
```powershell
# Terminal 1: Parar Vite (Ctrl+C)
# Luego:
cd 'c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web'
npm run dev
# Recarga el navegador (F5)
```

### Problema: No aparece la imagen en la carpeta

**Solución**:
1. Verifica que hayas cargado la imagen correctamente
2. Verifica que la carpeta exista:
   ```powershell
   Test-Path 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas'
   ```
3. Verifica que el API esté corriendo (Terminal 2)

### Problema: El JSON sigue teniendo `"url": ""`

**Solución**:
1. Verifica que el API retorne error en Network (F12)
2. Si hay error, reinicia el API:
   ```powershell
   # Terminal 2: Parar (Ctrl+C)
   # Luego:
   python api_server.py
   ```

---

## 📱 Cheat Sheet

### Iniciar desde cero
```powershell
# Terminal 1
cd 'c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web'
npm run dev

# Terminal 2
cd 'c:\Users\Fela\Documents\Proyectos\Examinator'
python api_server.py

# Navegador
http://localhost:5173
```

### Verificar que funciona
```powershell
# ¿Servidor Vite activo?
http://localhost:5173

# ¿API activo?
http://localhost:8000

# ¿Imagen guardada?
Get-ChildItem 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas' -Include *.png, *.jpg

# ¿JSON actualizado?
Get-Content 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas\practica_*.json' | ConvertFrom-Json | Select-Object -ExpandProperty preguntas | Where-Object tipo -eq picture_description | Select-Object -ExpandProperty imagen
```

### Reiniciar todo
```powershell
# Terminal 1: Ctrl+C, luego:
npm run dev

# Terminal 2: Ctrl+C, luego:
python api_server.py

# Navegador: F5
```

---

## 🎬 Demostración Paso a Paso

### 1. Iniciar servidores

```powershell
# Terminal 1
C:\Users\Fela\Documents\Proyectos\Examinator\examinator-web> npm run dev

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

```powershell
# Terminal 2
C:\Users\Fela\Documents\Proyectos\Examinator> python api_server.py

INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Abrir navegador

```
http://localhost:5173
```

### 3. En Examinator

1. Ve a un curso (ej: "🌐 Plataforma - Cosas")
2. Click en "Crear nueva práctica"
3. Elige "Picture Description"
4. Aparece ejercicio con área gris
5. Click en "Seleccionar imagen" o arrastra imagen
6. Responde con descripción
7. Click "Guardar" o "Enviar examen"

### 4. Verificar en Consola

```
F12 → Console → Busca logs:
✅ 💾 Intentando guardar práctica actualizada...
✅ 🖼️ Imágenes disponibles para guardar: 1
✅ ✅ Imagen guardada en: extracciones/...
```

### 5. Verificar en Carpeta

```powershell
Get-ChildItem 'c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas' | Format-Table Name, Length

Name                              Length
----                              ------
practica_20260104_103938.json     7395
business_meeting_team.png         45623    ✅ NUEVA
```

### 6. Verificar en JSON

```powershell
$json = Get-Content practica_20260104_103938.json | ConvertFrom-Json
$json.preguntas[0].imagen.url

# Deberías ver:
extracciones/🌐 Plataforma - Cosas/business_meeting_team.png
```

---

## 📞 Soporte Rápido

| Problema | Solución | Comando |
|----------|----------|---------|
| Vite no inicia | npm no instalado | `npm install` |
| API no inicia | Python no en PATH | `python --version` |
| Imagen no guarda | Servidores no corren | Ver paso 1 |
| URL vacía en JSON | API error | F12 → Network |
| Logs no aparecen | Caché navegador | F5 para recargar |

---

## 🎯 Resumen

✅ **El sistema está listo**  
✅ **Solo necesitas iniciar 2 servidores**  
✅ **Luego prueba en Examinator**  
✅ **Verifica en 3 lugares: Consola, Carpeta, JSON**

Si ves las 3 señales (logs + archivo + URL) → **¡Funciona!**

---

## 📚 Más Información

Para detalles técnicos, lee:
- `RESUMEN_GUARDADO_IMAGENES.md` - Resumen general
- `CHECKLIST_VERIFICACION_IMAGENES.md` - Checklist detallado
- `IMPLEMENTACION_GUARDADO_IMAGENES_COMPLETA.md` - Documentación completa

---

**¡A por ello! 🚀**

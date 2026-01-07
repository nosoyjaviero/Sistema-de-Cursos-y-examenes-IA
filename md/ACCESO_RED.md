# 🌐 Acceso en Red Local - Instrucciones

## 🚀 Inicio Rápido

### **Opción 1: Archivo .BAT (Windows tradicional)**
1. Haz **doble clic** en `iniciar_red.bat`
2. Sigue las instrucciones en pantalla
3. Usa la URL mostrada en tu móvil

### **Opción 2: Script PowerShell (Recomendado)**
1. **Click derecho** en `iniciar_red.ps1`
2. Selecciona **"Ejecutar con PowerShell"**
3. Usa la URL mostrada en tu móvil

### **Para Configurar Firewall Automáticamente:**
1. **Click derecho** en `iniciar_red.ps1` (o `iniciar_red.bat`)
2. Selecciona **"Ejecutar como Administrador"**

---

## 📱 Conectar desde tu Móvil/Tablet

### **Paso 1:** Verificar que estás en la misma WiFi
- Tu PC y tu móvil deben estar en la **misma red WiFi**

### **Paso 2:** Ejecutar el script
- Ejecuta `iniciar_red.bat` o `iniciar_red.ps1`
- Aparecerá una URL como: `http://192.168.1.100:5173`

### **Paso 3:** Abrir en el móvil
- Abre el navegador en tu móvil
- Escribe la URL que te dio el script
- ¡Listo! 🎉

---

## 🔧 Qué Hace el Script

✅ Detecta tu IP local automáticamente  
✅ Libera los puertos si están ocupados  
✅ Configura el firewall (si se ejecuta como Admin)  
✅ Modifica Vite para aceptar conexiones de red  
✅ Inicia el backend (API en puerto 8000)  
✅ Inicia el frontend (Web en puerto 5173/5174)  
✅ Te muestra la URL exacta para tu móvil  
✅ Guarda tu IP en `.ip_local.txt` para referencia  
✅ Abre el navegador local automáticamente  

---

## ⚠️ Solución de Problemas

### **"No puedo conectarme desde el móvil"**

**Causa más común: Firewall de Windows**

**Solución 1 (Automática):**
- Ejecuta el script como **Administrador** (click derecho → Ejecutar como Administrador)

**Solución 2 (Manual):**
1. Busca "Firewall de Windows Defender" en Windows
2. Click en "Configuración avanzada"
3. "Reglas de entrada" → "Nueva regla"
4. Tipo: Puerto
5. Puerto: 5173 y 8000
6. Acción: Permitir conexión
7. Dar un nombre: "Examinator"

### **"La IP mostrada es 169.254.x.x"**
- Esa es una IP de autoconfiguración (no válida)
- Revisa que tu WiFi esté conectada correctamente
- Ejecuta `ipconfig` en PowerShell y busca la IP que empieza con `192.168.x.x` o `10.x.x.x`

### **"El puerto está ocupado"**
- El script intenta liberarlo automáticamente
- Si persiste, reinicia tu PC

### **"Vite no inicia con --host"**
- El script modifica `package.json` automáticamente
- Si falla, abre `examinator-web/package.json` y cambia:
  ```json
  "dev": "vite"
  ```
  por:
  ```json
  "dev": "vite --host"
  ```

---

## 📖 URLs de Acceso

### **Desde esta PC:**
- Frontend: `http://localhost:5173` o `http://localhost:5174`
- Backend API: `http://localhost:8000`
- Docs API: `http://localhost:8000/docs`

### **Desde otros dispositivos:**
- Frontend: `http://TU_IP:5173` o `http://TU_IP:5174`
- Backend API: `http://TU_IP:8000`

*(Tu IP se muestra al ejecutar el script y se guarda en `.ip_local.txt`)*

---

## 🛑 Detener los Servidores

Los scripts abren **2 ventanas separadas**:
1. **Backend API** (ventana negra con "Backend API corriendo...")
2. **Frontend Web** (ventana con "Frontend corriendo...")

**Para detener:**
- Simplemente **cierra ambas ventanas**
- O presiona `Ctrl+C` en cada ventana

---

## 🔒 Seguridad

⚠️ **IMPORTANTE:**
- Estos scripts permiten acceso desde tu red local (WiFi de casa)
- **NO** expongas tu PC a Internet sin protección
- Si necesitas acceso desde fuera de tu red, considera:
  - VPN (más seguro)
  - Túneles SSH
  - Servicios como ngrok (solo para desarrollo/testing)

---

## 💡 Consejos

1. **Ejecuta como Administrador la primera vez** para configurar el firewall
2. **Guarda la URL en el móvil** para acceso rápido
3. **Usa la IP en lugar de localhost** desde otros dispositivos
4. **Verifica que ambos dispositivos estén en la misma WiFi**
5. **Si cambias de red WiFi**, tu IP puede cambiar (vuelve a ejecutar el script)

---

## ✅ Checklist de Verificación

Antes de intentar conectar desde el móvil:

- [ ] ¿Mi PC y móvil están en la **misma red WiFi**?
- [ ] ¿Ejecuté `iniciar_red.bat` o `iniciar_red.ps1`?
- [ ] ¿Veo las ventanas del Backend y Frontend abiertas?
- [ ] ¿Copié correctamente la URL mostrada?
- [ ] ¿El firewall está configurado? (ejecutar como Admin)
- [ ] ¿La URL incluye mi IP real (no 169.254.x.x)?

---

## 📞 Referencia Rápida

| Archivo | Descripción |
|---------|-------------|
| `iniciar_red.bat` | Script Windows tradicional |
| `iniciar_red.ps1` | Script PowerShell (recomendado) |
| `.ip_local.txt` | Tu IP guardada automáticamente |
| `iniciar.bat` | Script original (solo local) |

---

**Fecha:** 17 de noviembre de 2025  
**Versión:** 1.0

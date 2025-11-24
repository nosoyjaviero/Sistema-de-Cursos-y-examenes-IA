# 🔧 Soluciones a Problemas Comunes

> Basado en problemas reales encontrados durante el desarrollo

---

## 🚨 Problemas de GPU/CUDA

### ❌ Error: "CUDA not available" o torch.cuda.is_available() = False

**Síntomas:**
```python
>>> import torch
>>> torch.cuda.is_available()
False
```

**Causas comunes:**

1. **PyTorch instalado sin CUDA**
   ```powershell
   # Verificar versión
   pip show torch
   # Si dice "cpu" en lugar de "cu118", está mal
   ```

2. **Drivers NVIDIA desactualizados**

**Soluciones:**

```powershell
# 1. Desinstalar PyTorch actual
pip uninstall torch torchvision torchaudio

# 2. Instalar versión con CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Verificar
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Salida esperada:**
```
CUDA: True
GPU: NVIDIA GeForce RTX 4050 Laptop GPU
```

### ⚠️ GPU detectada pero no se usa

**Verificar en logs del servidor:**
```
Modelo cargado en: cpu
```

**Solución:**
En `buscador_ia.py`, asegurar:
```python
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer(config.modelo_embeddings, device=device)
```

---

## 🌐 Problemas de Servidor

### ❌ Error: "Servidor se cierra inmediatamente"

**Síntomas:**
```powershell
python api_buscador.py
# Ventana se cierra sin mensaje
```

**Causas:**
1. Error en importación
2. Puerto ocupado
3. Archivo corrupto

**Solución 1: Usar batch file (RECOMENDADO)**
```powershell
.\INICIAR_BUSCADOR_GPU.bat
```

El `.bat` mantiene la ventana abierta mostrando errores.

**Solución 2: PowerShell con output**
```powershell
& .\venv\Scripts\python.exe api_buscador.py 2>&1 | Tee-Object -FilePath error.log
```

### ❌ Error: "Address already in use" / Puerto ocupado

**Síntomas:**
```
OSError: [WinError 10048] Only one usage of each socket address
```

**Verificar puerto:**
```powershell
netstat -ano | Select-String ":5001"
```

**Solución:**
```powershell
# Opción 1: Matar proceso
$pid = (netstat -ano | Select-String ":5001" | ForEach-Object {$_.ToString().Split()[-1]})[0]
Stop-Process -Id $pid -Force

# Opción 2: Cambiar puerto en api_buscador.py
# Línea ~400: serve(app, host='0.0.0.0', port=5002)
```

### ❌ Servidor inicia pero no responde

**Verificar estado:**
```powershell
curl http://localhost:5001/api/estado
# o
Invoke-WebRequest -Uri http://localhost:5001/api/estado
```

**Salida esperada:**
```json
{
  "gpu_disponible": true,
  "total_chunks": 27,
  "archivos_indexados": 3
}
```

**Si falla:**
1. Verificar firewall de Windows
2. Verificar que el servidor muestra: "Running on http://0.0.0.0:5001"
3. Revisar logs en la terminal del servidor

---

## 📦 Problemas de Instalación

### ❌ Error: "pip install torch" muy lento o falla

**Causas:**
- Conexión lenta
- Timeout de pip

**Solución:**
```powershell
# Aumentar timeout
pip install --timeout=1000 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# O descargar manual desde:
# https://download.pytorch.org/whl/cu118/torch-2.7.1%2Bcu118-cp311-cp311-win_amd64.whl
pip install torch-2.7.1+cu118-cp311-cp311-win_amd64.whl
```

### ❌ Error: "faiss-gpu not available on Windows"

**Mensaje:**
```
ERROR: Could not find a version that satisfies the requirement faiss-gpu
```

**Solución:**
```powershell
# Usar faiss-cpu (funciona bien, GPU solo para embeddings)
pip install faiss-cpu
```

**Nota:** La GPU se usa para embeddings (sentence-transformers), no para FAISS en este proyecto.

### ❌ Error: ModuleNotFoundError al ejecutar scripts

**Síntomas:**
```
ModuleNotFoundError: No module named 'sentence_transformers'
```

**Causa:** Entorno virtual no activado

**Solución:**
```powershell
# Activar entorno
.\venv\Scripts\Activate.ps1

# Verificar Python correcto
which python  # Debe mostrar ruta con "venv"

# Instalar paquete faltante
pip install sentence-transformers
```

---

## 🎨 Problemas de Frontend

### ❌ Frontend no se conecta a backend

**Síntomas:**
- Búsqueda no funciona
- Consola muestra: `Failed to fetch`

**Verificar:**
```javascript
// En App.jsx debe decir:
const BACKEND_URL = 'http://localhost:5001';
```

**Solución:**
1. Verificar servidor corriendo: http://localhost:5001/api/estado
2. Verificar CORS en `api_buscador.py`:
   ```python
   CORS(app, origins=["http://localhost:5174"])
   ```

### ❌ npm run dev falla

**Error común:**
```
Error: Cannot find module 'vite'
```

**Solución:**
```powershell
cd examinator-web
rm -r node_modules
rm package-lock.json
npm install
npm run dev
```

### ❌ Cambios en código no se reflejan

**Solución:**
```powershell
# Frontend React
# Vite tiene HMR, pero a veces falla
Ctrl+C  # Detener
npm run dev  # Reiniciar

# Backend Python
# Waitress no tiene hot-reload
Ctrl+C en ventana del servidor
.\INICIAR_BUSCADOR_GPU.bat
```

---

## 🔍 Problemas de Búsqueda

### ❌ Búsqueda no encuentra nada

**Causas:**
1. Índice no creado
2. Archivos no en carpetas correctas
3. Índice desactualizado

**Verificar índice:**
```powershell
# Debe existir:
ls indices_busqueda/
# faiss_index.bin
# bm25_index.pkl
# chunks.json
```

**Solución:**
```powershell
# Recrear índice
python crear_indice_inicial.py

# O desde UI: Pestaña Buscar → ♻️ Reindexar Todo
```

### ⚠️ Búsqueda muy lenta (>5 segundos)

**Causa:** GPU no detectada, corriendo en CPU

**Verificar:**
```python
# En logs del servidor debe decir:
Modelo cargado en: cuda
GPU disponible: NVIDIA GeForce RTX 4050
```

**Si dice "cpu":**
```powershell
# Reinstalar PyTorch con CUDA
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### ❌ Resultados irrelevantes

**Ajustar pesos del híbrido:**

En `api_buscador.py`:
```python
# Línea ~200
self.peso_semantico = 0.7  # Más semántica
self.peso_keywords = 0.3   # Menos keywords

# Experimenta: 0.8/0.2 o 0.6/0.4
```

---

## 🖥️ Problemas de Sistema

### ❌ "Script execution disabled" en PowerShell

**Error:**
```
cannot be loaded because running scripts is disabled
```

**Solución (como administrador):**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ Firewall bloquea servidor

**Solución:**
```powershell
# Ejecutar como administrador
.\configurar_firewall.ps1

# O manual:
New-NetFirewallRule -DisplayName "Examinator API" -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow
```

### ❌ Disco lleno / Sin espacio

**PyTorch ocupa ~2GB, modelos de embeddings ~400MB**

**Verificar espacio:**
```powershell
Get-PSDrive C | Select-Object Used,Free
```

**Limpiar:**
```powershell
# Cache pip
pip cache purge

# Modelos descargados
rm -r $env:USERPROFILE\.cache\huggingface\
```

---

## 📊 Problemas de Rendimiento

### 🐌 Primera búsqueda muy lenta (~30s)

**Normal:** Carga de modelo en memoria

**Optimizar:**
```python
# En buscador_ia.py, precargar al inicio:
def inicializar_sistema():
    buscador = BuscadorHibrido()
    buscador.cargar_indices()  # Precarga
    return buscador
```

### 💾 Uso alto de RAM (>4GB)

**Causas:**
- Modelo de embeddings en memoria
- Índice FAISS grande

**Reducir uso:**
```python
# En buscador_ia.py, usar modelo más pequeño:
modelo_embeddings = 'sentence-transformers/all-MiniLM-L6-v2'  # ~80MB
# En vez de:
# 'BAAI/bge-small-en-v1.5'  # ~130MB
```

---

## 🆘 Comandos de Diagnóstico Rápido

```powershell
# Estado completo del sistema
.\VERIFICAR_ENTORNO.ps1

# Verificar GPU
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

# Verificar dependencias
pip list | Select-String -Pattern "torch|sentence|faiss|flask|waitress"

# Verificar puertos
netstat -ano | Select-String ":5001|:5174|:8000"

# Ver procesos Python
Get-Process python | Select-Object Id, ProcessName, Path

# Logs del servidor
# (ver ventana donde corre INICIAR_BUSCADOR_GPU.bat)

# Test API directamente
Invoke-WebRequest -Method POST -Uri "http://localhost:5001/api/buscar" -ContentType "application/json" -Body '{"query":"test","max_resultados":5}' | Select-Object -ExpandProperty Content
```

---

## 📞 Obtener Ayuda

Si el problema persiste:

1. **Revisar logs:**
   - Terminal del servidor de búsqueda
   - Consola del navegador (F12)
   - `error.log` si usaste `Tee-Object`

2. **Generar reporte:**
   ```powershell
   .\VERIFICAR_ENTORNO.ps1 > reporte.txt
   python -c "import torch; print(torch.__version__, torch.cuda.is_available())" >> reporte.txt
   pip list >> reporte.txt
   ```

3. **Información útil para reportar:**
   - Versión de Python
   - Versión de Node.js
   - GPU (si tienes)
   - Windows version
   - Mensaje de error completo
   - Pasos para reproducir

# 📚 Guía Completa de Instalación - Examinator con Búsqueda IA

> **Última actualización:** 23 de noviembre de 2025  
> **Versión:** 2.0 (con búsqueda IA y GPU)

## 🎯 Requisitos del Sistema

### Software Necesario

1. **Python 3.8 o superior**
   - Descargar: https://www.python.org/downloads/
   - ✅ Marcar "Add Python to PATH" durante instalación

2. **Node.js 16 o superior**
   - Descargar: https://nodejs.org/
   - Incluye npm automáticamente

3. **Git** (opcional, para clonar repositorio)
   - Descargar: https://git-scm.com/

### Hardware Recomendado

- **Para modo CPU:** 8GB RAM mínimo
- **Para modo GPU:** NVIDIA GPU con CUDA support (ej: RTX 4050, RTX 3060, etc.)
  - 16GB RAM recomendado
  - GPU con 4GB+ VRAM

---

## ⚡ Instalación Rápida (Recomendada)

### Opción 1: Script Automático

```powershell
# Ejecutar como administrador (recomendado)
.\INSTALACION_COMPLETA.ps1
```

Este script:
- ✅ Verifica Python y Node.js
- ✅ Crea entorno virtual Python
- ✅ Instala PyTorch con CUDA (GPU)
- ✅ Instala todas las dependencias
- ✅ Crea índice de búsqueda inicial

**Tiempo estimado:** 10-15 minutos (depende de conexión)

---

## 🔧 Instalación Manual

### Paso 1: Clonar/Descargar Proyecto

```powershell
git clone https://github.com/tu-usuario/examinator.git
cd examinator
```

### Paso 2: Configurar Python

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Actualizar pip
python -m pip install --upgrade pip
```

### Paso 3: Instalar PyTorch con CUDA

```powershell
# Para GPU NVIDIA (RTX 4050, 3060, etc.)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verificar instalación
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

**Salida esperada:** `CUDA: True`

### Paso 4: Instalar Dependencias Python

```powershell
pip install sentence-transformers
pip install faiss-cpu
pip install rank-bm25
pip install flask flask-cors
pip install waitress
pip install requests
pip install PyPDF2 python-docx
pip install numpy tqdm
```

### Paso 5: Instalar Dependencias Node.js

```powershell
cd examinator-web
npm install
cd ..
```

### Paso 6: Crear Índice Inicial

```powershell
python crear_indice_inicial.py
```

---

## 🚀 Iniciar el Sistema

### Opción 1: Script Automático (Recomendada)

```powershell
.\INICIAR_BUSCADOR_TODO.ps1
```

### Opción 2: Manual (2 terminales)

**Terminal 1 - Servidor de Búsqueda:**
```powershell
.\INICIAR_BUSCADOR_GPU.bat
```

**Terminal 2 - Frontend:**
```powershell
cd examinator-web
npm run dev
```

### Acceder a la Aplicación

- **Frontend:** http://localhost:5174
- **API Búsqueda:** http://localhost:5001
- **API Principal:** http://localhost:8000 (si usas Ollama)

---

## ✅ Verificación de Instalación

### Script de Verificación

```powershell
.\VERIFICAR_ENTORNO.ps1
```

### Verificación Manual

```powershell
# 1. Python
python --version
# Esperado: Python 3.8+

# 2. Node.js
node --version
# Esperado: v16+

# 3. GPU/CUDA
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
# Esperado: GPU: NVIDIA GeForce RTX 4050 (o tu GPU)

# 4. Dependencias Python
pip list | Select-String -Pattern "torch|sentence|faiss|flask"
# Debe mostrar: torch, sentence-transformers, faiss-cpu, flask

# 5. Puerto 5001 disponible
netstat -ano | Select-String ":5001"
# No debe mostrar nada (puerto libre)

# 6. Puerto 5174 disponible
netstat -ano | Select-String ":5174"
# No debe mostrar nada (puerto libre)
```

---

## 📦 Estructura del Proyecto

```
Examinator/
├── 📁 venv/                      # Entorno virtual Python
├── 📁 examinator-web/            # Frontend React
│   ├── src/
│   │   ├── App.jsx              # Componente principal
│   │   └── App.css              # Estilos
│   └── package.json
├── 📁 indices_busqueda/          # Índices FAISS y BM25
├── 📄 buscador_ia.py            # Motor de búsqueda
├── 📄 api_buscador.py           # API REST búsqueda
├── 📄 crear_indice_inicial.py   # Creador de índices
├── 📄 INICIAR_BUSCADOR_GPU.bat  # Iniciar servidor
├── 📄 INSTALACION_COMPLETA.ps1  # Script instalación
└── 📄 GUIA_INSTALACION.md       # Este archivo
```

---

## 🎓 Siguientes Pasos

1. **Leer documentación de uso:**
   - `SOLUCIONES_PROBLEMAS.md` - Errores comunes
   - `ARQUITECTURA_BUSQUEDA.md` - Cómo funciona

2. **Configurar carpetas de contenido:**
   - `cursos/` - Tus cursos
   - `notas/` - Tus notas
   - `flashcards/` - Tus tarjetas

3. **Actualizar índice:**
   - Pestaña "Buscar" → "🔄 Actualizar Índice"

4. **Probar búsqueda:**
   - Busca: "integral", "loop", "componente", etc.

---

## 💡 Consejos

- 🔋 **GPU:** Asegura drivers NVIDIA actualizados
- ⚡ **Primera ejecución:** El primer índice tarda ~30 segundos
- 🔍 **Búsqueda híbrida:** Combina semántica (70%) + palabras clave (30%)
- 📊 **Rendimiento:** GPU es 5-10x más rápida que CPU
- 🔄 **Actualizar:** Ejecuta actualización de índice cuando agregues archivos

---

## 🆘 Problemas Comunes

Ver `SOLUCIONES_PROBLEMAS.md` para:
- ❌ Error de GPU no detectada
- ❌ Puerto ocupado
- ❌ Servidor se cierra inmediatamente
- ❌ Error de importación torch/CUDA
- ❌ Frontend no se conecta al backend

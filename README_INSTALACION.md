# 📋 README - Instalación y Configuración del Proyecto

> **Examinator con Sistema de Búsqueda IA**  
> Sistema completo de gestión de cursos, notas, flashcards y exámenes con búsqueda semántica acelerada por GPU

---

## 🚀 Inicio Rápido (3 pasos)

### 1. Instalar Dependencias

```powershell
# Ejecutar como administrador (recomendado)
.\INSTALACION_COMPLETA.ps1
```

Este script instala automáticamente:
- ✅ Entorno virtual Python
- ✅ PyTorch con CUDA (GPU)
- ✅ Sentence Transformers + FAISS
- ✅ Flask + Waitress
- ✅ Dependencias Node.js

**Tiempo:** 10-15 minutos

### 2. Verificar Instalación

```powershell
.\VERIFICAR_ENTORNO.ps1
```

Debe mostrar:
- ✅ Python 3.8+
- ✅ Node.js
- ✅ PyTorch con CUDA
- ✅ GPU detectada (si tienes NVIDIA)
- ✅ Dependencias instaladas

### 3. Iniciar Sistema

```powershell
.\INICIAR_BUSCADOR_TODO.ps1
```

Abre automáticamente:
- 🌐 Frontend: http://localhost:5174
- 🔍 API Búsqueda: http://localhost:5001

---

## 📦 Requisitos

### Software

| Componente | Versión Mínima | Descargar |
|------------|----------------|-----------|
| Python | 3.8+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 16+ | [nodejs.org](https://nodejs.org/) |
| Git | Cualquiera | [git-scm.com](https://git-scm.com/) |

### Hardware

**Mínimo (Modo CPU):**
- 8GB RAM
- 10GB espacio en disco

**Recomendado (Modo GPU):**
- NVIDIA GPU con CUDA support (RTX 4050, RTX 3060, etc.)
- 16GB RAM
- 15GB espacio en disco

---

## 📁 Estructura del Proyecto

```
Examinator/
│
├── 📄 Scripts de Inicio
│   ├── INSTALACION_COMPLETA.ps1      ← Instalar todo automáticamente
│   ├── VERIFICAR_ENTORNO.ps1         ← Verificar configuración
│   ├── INICIAR_BUSCADOR_TODO.ps1     ← Iniciar sistema completo
│   ├── INICIAR_BUSCADOR_GPU.bat      ← Solo servidor de búsqueda
│   └── DETENER_BUSCADOR.ps1          ← Detener servicios
│
├── 📚 Documentación
│   ├── GUIA_INSTALACION.md           ← Guía paso a paso
│   ├── SOLUCIONES_PROBLEMAS.md       ← Errores comunes y soluciones
│   ├── ARQUITECTURA_BUSQUEDA.md      ← Cómo funciona el sistema
│   └── README_INSTALACION.md         ← Este archivo
│
├── 🔍 Backend Búsqueda IA
│   ├── buscador_ia.py                ← Motor de búsqueda híbrido
│   ├── api_buscador.py               ← API REST (Flask)
│   ├── crear_indice_inicial.py       ← Crea índices FAISS/BM25
│   └── indices_busqueda/             ← Índices generados
│
├── 🎨 Frontend
│   └── examinator-web/
│       ├── src/
│       │   ├── App.jsx               ← Componente principal
│       │   └── App.css               ← Estilos
│       └── package.json
│
├── 📂 Contenido del Usuario
│   ├── cursos/                       ← Tus cursos
│   ├── notas/                        ← Tus notas
│   ├── flashcards/                   ← Tus flashcards
│   └── examenes/                     ← Tus exámenes
│
└── 🐍 Python
    ├── venv/                         ← Entorno virtual
    └── requirements.txt              ← Dependencias Python
```

---

## 🎯 Características Principales

### ✨ Sistema de Búsqueda IA

- 🧠 **Búsqueda semántica:** Entiende el significado, no solo palabras exactas
- 🔤 **Búsqueda por palabras clave:** BM25 para matches exactos
- 🔀 **Híbrida:** Combina ambas (70% semántica + 30% keywords)
- ⚡ **GPU acelerada:** 5-10x más rápida que CPU
- 📊 **Resultados con metadata:** Muestra títulos, preguntas, contexto

### 📚 Gestión de Contenido

- 📝 Notas organizadas por carpetas
- 🎴 Flashcards con sistema de repetición espaciada
- 📋 Generación de exámenes
- 📊 Estadísticas de progreso
- 🔄 Sincronización automática de índices

---

## 🛠️ Comandos Útiles

### Instalación y Configuración

```powershell
# Instalación completa
.\INSTALACION_COMPLETA.ps1

# Verificar entorno
.\VERIFICAR_ENTORNO.ps1

# Actualizar solo dependencias Python
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Actualizar solo dependencias Node.js
cd examinator-web
npm install
```

### Iniciar/Detener Sistema

```powershell
# Iniciar todo (recomendado)
.\INICIAR_BUSCADOR_TODO.ps1

# Solo servidor de búsqueda
.\INICIAR_BUSCADOR_GPU.bat

# Solo frontend
cd examinator-web
npm run dev

# Detener todo
.\DETENER_BUSCADOR.ps1
```

### Diagnóstico

```powershell
# Verificar GPU
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

# Ver puertos ocupados
netstat -ano | Select-String ":5001|:5174"

# Listar dependencias instaladas
pip list

# Test API
Invoke-WebRequest -Uri "http://localhost:5001/api/estado"
```

### Mantenimiento

```powershell
# Recrear índice de búsqueda
python crear_indice_inicial.py

# Limpiar cache pip
pip cache purge

# Reinstalar PyTorch con CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 🆘 Solución de Problemas

### ❌ "CUDA not available"

```powershell
# Reinstalar PyTorch con CUDA
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### ❌ "Puerto ocupado"

```powershell
# Liberar puerto 5001
$pid = (netstat -ano | Select-String ":5001").ToString().Split()[-1]
Stop-Process -Id $pid -Force
```

### ❌ "Servidor se cierra"

```powershell
# Usar batch file en vez de PowerShell
.\INICIAR_BUSCADOR_GPU.bat
```

### ❌ "Frontend no se conecta"

1. Verificar servidor corriendo: http://localhost:5001/api/estado
2. Verificar CORS en `api_buscador.py`
3. Revisar consola del navegador (F12)

**Más soluciones:** Ver `SOLUCIONES_PROBLEMAS.md`

---

## 📖 Documentación Completa

| Documento | Contenido |
|-----------|-----------|
| [GUIA_INSTALACION.md](GUIA_INSTALACION.md) | Instalación paso a paso detallada |
| [SOLUCIONES_PROBLEMAS.md](SOLUCIONES_PROBLEMAS.md) | Errores comunes y soluciones |
| [ARQUITECTURA_BUSQUEDA.md](ARQUITECTURA_BUSQUEDA.md) | Cómo funciona el sistema técnicamente |
| [requirements.txt](requirements.txt) | Lista de dependencias Python |

---

## 🔧 Tecnologías Utilizadas

### Backend

- **Python 3.11**
- **PyTorch 2.7.1** (CUDA 11.8)
- **Sentence Transformers** - Embeddings semánticos
- **FAISS** - Vector similarity search
- **BM25** - Búsqueda por palabras clave
- **Flask + Waitress** - API REST

### Frontend

- **React 18**
- **Vite** - Build tool + dev server
- **JavaScript ES6+**

### Modelos IA

- **BAAI/bge-small-en-v1.5** - Embeddings (384 dimensiones, ~130MB)
- **FAISS IndexFlatIP** - Índice vectorial
- **BM25 Okapi** - Ranking de keywords

---

## 📊 Rendimiento

**Con GPU (RTX 4050):**
- Indexación: ~30 segundos para 100 archivos
- Primera búsqueda: ~5 segundos (carga modelo)
- Búsquedas siguientes: ~0.5 segundos

**Sin GPU (CPU):**
- Indexación: ~2 minutos para 100 archivos
- Búsquedas: ~3-5 segundos

---

## 🤝 Contribuir

Para reportar problemas o sugerir mejoras:

1. Genera reporte de diagnóstico:
   ```powershell
   .\VERIFICAR_ENTORNO.ps1 > diagnostico.txt
   ```

2. Incluye:
   - Versión de Python
   - Versión de Node.js
   - GPU (si tienes)
   - Mensaje de error completo
   - Pasos para reproducir

---

## 📜 Licencia

Este proyecto es de uso educativo.

---

## 🎓 Próximos Pasos

1. **Primera vez:**
   - Ejecuta `.\INSTALACION_COMPLETA.ps1`
   - Espera a que termine (~15 min)
   - Ejecuta `.\VERIFICAR_ENTORNO.ps1`
   - Si todo OK, ejecuta `.\INICIAR_BUSCADOR_TODO.ps1`

2. **Después de instalación:**
   - Agrega tus archivos en `cursos/`, `notas/`, `flashcards/`
   - En la interfaz, ve a pestaña "Buscar"
   - Haz clic en "🔄 Actualizar Índice"
   - Prueba buscar: "integral", "componente", etc.

3. **Explorar funcionalidades:**
   - Gestión de cursos
   - Crear flashcards
   - Generar exámenes
   - Sistema de repetición espaciada
   - Estadísticas de progreso

---

**¿Problemas?** → Ver `SOLUCIONES_PROBLEMAS.md`  
**¿Cómo funciona?** → Ver `ARQUITECTURA_BUSQUEDA.md`  
**¿Instalar desde cero?** → Ver `GUIA_INSTALACION.md`

---

*Última actualización: 23 de noviembre de 2025*

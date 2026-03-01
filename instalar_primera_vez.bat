@echo off
chcp 65001 > nul
title 📦 Examinator - Instalación Primera Vez

echo.
echo ══════════════════════════════════════════════════════════════════════
echo    📦 EXAMINATOR - INSTALACIÓN AUTOMÁTICA
echo ══════════════════════════════════════════════════════════════════════
echo.
echo    Este script instalará todo lo necesario para ejecutar Examinator
echo    en tu computadora. Esto solo se ejecuta la primera vez.
echo.
echo    ⏱️ Tiempo estimado: 5-15 minutos (según tu conexión)
echo.
echo    ⚠️ NO CIERRES ESTA VENTANA - La instalación está en progreso
echo.
echo ══════════════════════════════════════════════════════════════════════
echo.

:: ============================================================================
:: BARRA DE PROGRESO VISUAL
:: ============================================================================

echo.
echo    PROGRESO DE INSTALACIÓN:
echo    ┌──────────────────────────────────────────────────────────────┐
echo    │                                                              │
echo    └──────────────────────────────────────────────────────────────┘
echo.

:: ============================================================================
:: VERIFICACIÓN DE REQUISITOS BASE
:: ============================================================================

echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [1/10] ▶ Verificando Python...                                    │
echo └─────────────────────────────────────────────────────────────────────┘
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado.
    echo.
    echo    Descarga Python desde: https://www.python.org/downloads/
    echo    ⚠️ IMPORTANTE: Marca "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo ✅ Python encontrado: %PYTHON_VER%

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [2/10] ▶ Verificando Node.js...                                   │
echo └─────────────────────────────────────────────────────────────────────┘
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js no está instalado.
    echo.
    echo    Descarga Node.js desde: https://nodejs.org/
    echo    Instala la versión LTS (recomendada)
    echo.
    pause
    exit /b 1
)
for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
echo ✅ Node.js encontrado: %NODE_VER%

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [3/10] ▶ Verificando npm...                                       │
echo └─────────────────────────────────────────────────────────────────────┘
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm no está instalado (debería venir con Node.js)
    pause
    exit /b 1
)
for /f "tokens=1" %%i in ('npm --version 2^>^&1') do set NPM_VER=%%i
echo ✅ npm encontrado: v%NPM_VER%

:: ============================================================================
:: DETECCIÓN DE GPU NVIDIA
:: ============================================================================

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [4/10] ▶ Detectando GPU...                                        │
echo └─────────────────────────────────────────────────────────────────────┘
set GPU_DISPONIBLE=0
set GPU_NOMBRE=CPU

nvidia-smi --query-gpu=name --format=csv,noheader 2>nul > temp_gpu.txt
if %errorlevel% equ 0 (
    set /p GPU_NOMBRE=<temp_gpu.txt
    set GPU_DISPONIBLE=1
    echo ✅ GPU NVIDIA detectada: %GPU_NOMBRE%
    echo    Se instalará soporte CUDA para mejor rendimiento
) else (
    echo ⚠️ No se detectó GPU NVIDIA
    echo    Se usará modo CPU (más lento pero funcional)
)
del temp_gpu.txt 2>nul

:: ============================================================================
:: VERIFICAR OLLAMA
:: ============================================================================

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [5/10] ▶ Verificando Ollama...                                    │
echo └─────────────────────────────────────────────────────────────────────┘
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Ollama no está instalado.
    echo.
    echo    Ollama es necesario para la generación de exámenes con IA.
    echo    Descarga desde: https://ollama.com/download
    echo.
    echo    Después de instalar Ollama, ejecuta:
    echo    ollama pull llama3.2:3b
    echo.
    set OLLAMA_INSTALADO=0
) else (
    echo ✅ Ollama encontrado
    set OLLAMA_INSTALADO=1
    
    :: Verificar si hay modelos
    ollama list 2>nul | findstr /i "llama" >nul
    if %errorlevel% equ 0 (
        echo    Modelos disponibles detectados
    ) else (
        echo    ⚠️ No hay modelos descargados. Ejecuta: ollama pull llama3.2:3b
    )
)

:: ============================================================================
:: CREAR CARPETAS NECESARIAS
:: ============================================================================

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [6/10] ▶ Creando estructura de carpetas...                        │
echo └─────────────────────────────────────────────────────────────────────┘

if not exist "extracciones" mkdir extracciones
echo    ✓ extracciones/

if not exist "chats" mkdir chats
echo    ✓ chats/

if not exist "chats_historial" mkdir chats_historial
echo    ✓ chats_historial/

if not exist "datos_persistentes" mkdir datos_persistentes
echo    ✓ datos_persistentes/

if not exist "examenes_de_archivos" mkdir examenes_de_archivos
echo    ✓ examenes_de_archivos/

if not exist "indice_busqueda" mkdir indice_busqueda
echo    ✓ indice_busqueda/

if not exist "logs_practicas_detallado" mkdir logs_practicas_detallado
echo    ✓ logs_practicas_detallado/

if not exist "temp" mkdir temp
echo    ✓ temp/

if not exist "temp_examenes" mkdir temp_examenes
echo    ✓ temp_examenes/

if not exist "modelos" mkdir modelos
echo    ✓ modelos/

if not exist "md" mkdir md
echo    ✓ md/

echo ✅ Carpetas creadas

:: ============================================================================
:: CREAR ENTORNO VIRTUAL PYTHON
:: ============================================================================

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [7/10] ▶ Configurando entorno virtual Python...                   │
echo └─────────────────────────────────────────────────────────────────────┘

if exist "venv" (
    echo    Entorno virtual ya existe
) else (
    echo    Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
)
echo ✅ Entorno virtual configurado

:: Activar entorno
call venv\Scripts\activate.bat

:: Actualizar pip
echo    Actualizando pip...
python -m pip install --upgrade pip -q

:: ============================================================================
:: INSTALAR DEPENDENCIAS PYTHON
:: ============================================================================

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [8/10] ▶ Instalando dependencias Python...                        │
echo │         ⚠️  ESTO PUEDE TARDAR 5-10 MINUTOS - NO CERRAR            │
echo └─────────────────────────────────────────────────────────────────────┘
echo.

:: Instalar PyTorch (con o sin CUDA según GPU)
if %GPU_DISPONIBLE% equ 1 (
    echo    📦 [1/5] Instalando PyTorch con soporte CUDA...
    echo        Descargando ~2GB - por favor espera...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q
    echo        ✅ PyTorch CUDA instalado
) else (
    echo    📦 [1/5] Instalando PyTorch (modo CPU)...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu -q
    echo        ✅ PyTorch CPU instalado
)

:: Dependencias del servidor FastAPI
echo    📦 [2/5] Instalando FastAPI y servidor...
pip install fastapi uvicorn python-multipart requests beautifulsoup4 -q
echo        ✅ FastAPI instalado

:: Dependencias del buscador IA
echo    📦 [3/5] Instalando buscador IA (puede tardar)...
pip install sentence-transformers faiss-cpu rank-bm25 -q
echo        ✅ Buscador IA instalado

:: Servidor Flask para buscador
echo    📦 [4/5] Instalando Flask...
pip install Flask Flask-Cors waitress -q
echo        ✅ Flask instalado

:: Utilidades
echo    📦 [5/5] Instalando utilidades...
pip install pypdf PyPDF2 python-docx numpy tqdm ddgs -q
echo        ✅ Utilidades instaladas

echo.
echo ✅ Todas las dependencias Python instaladas

:: Verificar CUDA si hay GPU
if %GPU_DISPONIBLE% equ 1 (
    echo.
    echo    Verificando CUDA...
    python -c "import torch; print('    CUDA:', 'Activo ✅' if torch.cuda.is_available() else 'No disponible ⚠️')"
)

:: ============================================================================
:: INSTALAR DEPENDENCIAS NODE.JS (REACT/VITE)
:: ============================================================================

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [9/10] ▶ Instalando dependencias del frontend (React/Vite)...     │
echo └─────────────────────────────────────────────────────────────────────┘

if exist "examinator-web\package.json" (
    cd examinator-web
    
    if not exist "node_modules" (
        echo    Ejecutando npm install...
        call npm install
        if %errorlevel% neq 0 (
            echo ⚠️ Error en npm install, intentando de nuevo...
            call npm install --legacy-peer-deps
        )
    ) else (
        echo    node_modules ya existe, verificando...
        call npm install
    )
    
    cd ..
    echo ✅ Dependencias frontend instaladas
) else (
    echo ⚠️ No se encontró examinator-web/package.json
)

:: ============================================================================
:: CREAR ARCHIVO DE CONFIGURACIÓN
:: ============================================================================

echo.
echo ┌─────────────────────────────────────────────────────────────────────┐
echo │  [10/10] ▶ Creando configuración inicial...                        │
echo └─────────────────────────────────────────────────────────────────────┘

if not exist "config.json" (
    echo {> config.json
    echo   "modelo_chat": "llama3.2:3b",>> config.json
    echo   "modelo_examenes": "llama3.2:3b",>> config.json
    echo   "carpeta_cursos": "./md",>> config.json
    echo   "carpeta_extracciones": "./extracciones",>> config.json
    echo   "puerto_api": 8000,>> config.json
    echo   "puerto_buscador": 5001,>> config.json
    echo   "puerto_frontend": 5173,>> config.json
    echo   "gpu_activa": %GPU_DISPONIBLE%>> config.json
    echo }>> config.json
    echo    ✓ config.json creado
) else (
    echo    config.json ya existe
)

:: Crear marcador de instalación completa
echo %date% %time% > .instalacion_completa
echo ✅ Configuración completada

:: ============================================================================
:: RESUMEN FINAL
:: ============================================================================

echo.
echo ══════════════════════════════════════════════════════════════════════
echo    ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE
echo ══════════════════════════════════════════════════════════════════════
echo.
echo    📋 RESUMEN:
echo    ────────────────────────────────────────────────────────────────────
echo    ✓ Python %PYTHON_VER% configurado
echo    ✓ Node.js %NODE_VER% configurado
echo    ✓ Entorno virtual Python creado
if %GPU_DISPONIBLE% equ 1 (
echo    ✓ PyTorch con CUDA instalado (GPU: %GPU_NOMBRE%)
) else (
echo    ✓ PyTorch instalado (modo CPU)
)
echo    ✓ FastAPI y dependencias del servidor instaladas
echo    ✓ Buscador IA instalado (sentence-transformers + FAISS)
echo    ✓ Frontend React/Vite instalado
echo    ✓ Carpetas del proyecto creadas
echo.

if %OLLAMA_INSTALADO% equ 0 (
echo    ⚠️ PENDIENTE: Instalar Ollama desde https://ollama.com/download
echo       Luego ejecutar: ollama pull llama3.2:3b
echo.
)

echo    🚀 PARA INICIAR EL SISTEMA:
echo    ────────────────────────────────────────────────────────────────────
echo    Ejecuta: iniciar_simple.bat
echo.
echo    Esto iniciará:
echo    - Backend API (puerto 8000)
echo    - Frontend Web (puerto 5173)
echo    - El buscador se inicia bajo demanda en la app
echo.
echo ══════════════════════════════════════════════════════════════════════
echo.
pause

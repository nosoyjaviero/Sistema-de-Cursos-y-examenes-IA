@echo off
setlocal EnableExtensions
cd /d "%~dp0"
setlocal EnableDelayedExpansion
set "PIP_RETRIES=10"
set "PIP_TIMEOUT=60"
title Examinator - Instalacion Primera Vez

echo.
echo ======================================================================
echo    [INFO] EXAMINATOR - INSTALACION AUTOMATICA
echo ======================================================================
echo.
echo    Este script instalara todo lo necesario para ejecutar Examinator
echo    en tu computadora. Esto solo se ejecuta la primera vez.
echo.
echo    Tiempo estimado: 5-15 minutos, segun tu conexion
echo.
echo    ADVERTENCIA: NO CIERRES ESTA VENTANA - La instalacion esta en progreso
echo.
echo ======================================================================
echo.

:: ============================================================================
:: BARRA DE PROGRESO VISUAL
:: ============================================================================

echo.
echo    PROGRESO DE INSTALACION:
echo    [--------------------------------------------------------------]
echo    [                                                              ]
echo    [--------------------------------------------------------------]
echo.

:: ============================================================================
:: VERIFICACION DE REQUISITOS BASE
:: ============================================================================

echo [1/10] Verificando Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado.
    echo.
    echo    Descarga Python desde: https://www.python.org/downloads/
    echo    IMPORTANTE: Marca "Add Python to PATH" durante la instalacion
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo [OK] Python encontrado: %PYTHON_VER%

echo.
echo [2/10] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado.
    echo.
    echo    Descarga Node.js desde: https://nodejs.org/
    echo    Instala la version LTS recomendada.
    echo    Si ya lo instalaste, cierra esta ventana y abre CMD de nuevo.
    echo.
    pause
    exit /b 1
)
for /f "tokens=1" %%i in ('node --version 2^>nul') do set NODE_VER=%%i
echo [OK] Node.js encontrado: %NODE_VER%

echo.
echo [3/10] Verificando npm...
call npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm no esta instalado. Deberia venir con Node.js.
    echo    Repara o reinstala Node.js LTS desde https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=1" %%i in ('call npm --version 2^>nul') do set NPM_VER=%%i
echo [OK] npm encontrado: v%NPM_VER%

:: ============================================================================
:: DETECCION DE GPU NVIDIA
:: ============================================================================

echo.
echo [4/10] Detectando GPU...
set GPU_DISPONIBLE=0
set GPU_NOMBRE=CPU

nvidia-smi --query-gpu=name --format=csv,noheader 2>nul > temp_gpu.txt
if %errorlevel% equ 0 (
    set /p GPU_NOMBRE=<temp_gpu.txt
    set GPU_DISPONIBLE=1
    echo [OK] GPU NVIDIA detectada: !GPU_NOMBRE!
    echo    Se instalara soporte CUDA para mejor rendimiento
) else (
    echo ADVERTENCIA: No se detecto GPU NVIDIA
    echo    Se usara modo CPU, mas lento pero funcional
)
del temp_gpu.txt 2>nul

:: ============================================================================
:: VERIFICAR OLLAMA
:: ============================================================================

echo.
echo [5/10] Verificando Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Ollama no esta instalado.
    echo.
    echo    Ollama es necesario para la generacion de examenes con IA.
    echo    Descarga desde: https://ollama.com/download
    echo.
    echo    Despues de instalar Ollama, ejecuta:
    echo    ollama pull llama3.2:3b
    echo.
    set OLLAMA_INSTALADO=0
) else (
    echo [OK] Ollama encontrado
    set OLLAMA_INSTALADO=1
    
    :: Verificar si hay modelos
    ollama list 2>nul | findstr /i "llama" >nul
    if errorlevel 1 (
        echo    ADVERTENCIA: No hay modelos descargados. Ejecuta: ollama pull llama3.2:3b
    ) else (
        echo    Modelos disponibles detectados
    )
)

:: ============================================================================
:: CREAR CARPETAS NECESARIAS
:: ============================================================================

echo.
echo [6/10] Creando estructura de carpetas...

if not exist "extracciones" mkdir extracciones
echo    [OK] extracciones/

if not exist "chats" mkdir chats
echo    [OK] chats/

if not exist "chats_historial" mkdir chats_historial
echo    [OK] chats_historial/

if not exist "datos_persistentes" mkdir datos_persistentes
echo    [OK] datos_persistentes/

if not exist "examenes_de_archivos" mkdir examenes_de_archivos
echo    [OK] examenes_de_archivos/

if not exist "indice_busqueda" mkdir indice_busqueda
echo    [OK] indice_busqueda/

if not exist "logs_practicas_detallado" mkdir logs_practicas_detallado
echo    [OK] logs_practicas_detallado/

if not exist "temp" mkdir temp
echo    [OK] temp/

if not exist "temp_examenes" mkdir temp_examenes
echo    [OK] temp_examenes/

if not exist "modelos" mkdir modelos
echo    [OK] modelos/

if not exist "md" mkdir md
echo    [OK] md/

echo [OK] Carpetas creadas

:: ============================================================================
:: CREAR ENTORNO VIRTUAL PYTHON
:: ============================================================================

echo.
echo [7/10] Configurando entorno virtual Python...

if exist "venv" (
    echo    Entorno virtual ya existe
) else (
    echo    Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Error creando entorno virtual
        pause
        exit /b 1
    )
)
echo [OK] Entorno virtual configurado

:: Activar entorno
call venv\Scripts\activate.bat

:: Actualizar pip
echo    Actualizando pip...
python -m pip install --upgrade pip --progress-bar on
if errorlevel 1 goto :pip_install_failed

:: ============================================================================
:: INSTALAR DEPENDENCIAS PYTHON
:: ============================================================================

echo.
echo [8/10] Instalando dependencias Python
echo ADVERTENCIA: Esto puede tardar 5-10 minutos. No cierres la ventana.
echo.

:: Instalar PyTorch (con o sin CUDA segun GPU)
if %GPU_DISPONIBLE% equ 1 (
    echo    [INFO] [1/5] Instalando PyTorch con soporte CUDA...
    echo        pip mostrara el progreso de descarga de cada paquete...
    pip install --progress-bar on torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    if errorlevel 1 goto :pip_install_failed
    echo        [OK] PyTorch CUDA instalado
) else (
    echo    [INFO] [1/5] Instalando PyTorch en modo CPU...
    pip install --progress-bar on torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    if errorlevel 1 goto :pip_install_failed
    echo        [OK] PyTorch CPU instalado
)

:: Dependencias del servidor FastAPI
echo    [INFO] [2/5] Instalando FastAPI y servidor...
pip install --progress-bar on fastapi uvicorn python-multipart requests beautifulsoup4
if errorlevel 1 goto :pip_install_failed
echo        [OK] FastAPI instalado

:: Dependencias del buscador IA
echo    [INFO] [3/5] Instalando buscador IA (puede tardar)...
pip install --progress-bar on sentence-transformers faiss-cpu rank-bm25
if errorlevel 1 goto :pip_install_failed
echo        [OK] Buscador IA instalado

:: Servidor Flask para buscador
echo    [INFO] [4/5] Instalando Flask...
pip install --progress-bar on Flask Flask-Cors waitress
if errorlevel 1 goto :pip_install_failed
echo        [OK] Flask instalado

:: Utilidades
echo    [INFO] [5/5] Instalando utilidades...
pip install --progress-bar on pypdf PyPDF2 python-docx numpy tqdm ddgs
if errorlevel 1 goto :pip_install_failed
echo        [OK] Utilidades instaladas

echo.
echo [OK] Todas las dependencias Python instaladas

:: Verificar CUDA si hay GPU
if %GPU_DISPONIBLE% equ 1 (
    echo.
    echo    Verificando CUDA...
    python -c "import torch; print('    CUDA:', 'Activo [OK]' if torch.cuda.is_available() else 'No disponible')"
)

:: ============================================================================
:: INSTALAR DEPENDENCIAS NODE.JS (REACT/VITE)
:: ============================================================================

echo.
echo [9/10] Instalando dependencias del frontend React/Vite...

if exist "examinator-web\package.json" (
    cd examinator-web
    
    if not exist "node_modules" (
        echo    Ejecutando npm install...
        call npm install
        if errorlevel 1 (
            echo ADVERTENCIA: Error en npm install, intentando de nuevo...
            call npm install --legacy-peer-deps
        )
    ) else (
        echo    node_modules ya existe, verificando...
        call npm install
    )
    
    cd ..
    echo [OK] Dependencias frontend instaladas
) else (
    echo ADVERTENCIA: No se encontro examinator-web/package.json
)

:: ============================================================================
:: CREAR ARCHIVO DE CONFIGURACION
:: ============================================================================

echo.
echo [10/10] Creando configuracion inicial...

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
    echo    [OK] config.json creado
) else (
    echo    config.json ya existe
)

:: Crear marcador de instalacion completa
echo %date% %time% > .instalacion_completa
echo [OK] Configuracion completada

:: ============================================================================
:: RESUMEN FINAL
:: ============================================================================

echo.
echo ======================================================================
echo    [OK] INSTALACION COMPLETADA EXITOSAMENTE
echo ======================================================================
echo.
echo     RESUMEN:
echo    --------------------------------------------------------------------
echo    [OK] Python %PYTHON_VER% configurado
echo    [OK] Node.js %NODE_VER% configurado
echo    [OK] Entorno virtual Python creado
if %GPU_DISPONIBLE% equ 1 (
echo    [OK] PyTorch con CUDA instalado. GPU: !GPU_NOMBRE!
) else (
echo    [OK] PyTorch instalado en modo CPU
)
echo    [OK] FastAPI y dependencias del servidor instaladas
echo    [OK] Buscador IA instalado: sentence-transformers + FAISS
echo    [OK] Frontend React/Vite instalado
echo    [OK] Carpetas del proyecto creadas
echo.

if %OLLAMA_INSTALADO% equ 0 (
echo    ADVERTENCIA: PENDIENTE: Instalar Ollama desde https://ollama.com/download
echo       Luego ejecutar: ollama pull llama3.2:3b
echo.
)

echo     PARA INICIAR EL SISTEMA:
echo    --------------------------------------------------------------------
echo    Ejecuta: iniciar_simple.bat
echo.
echo    Esto iniciara:
echo    - Backend API (puerto 8000)
echo    - Frontend Web (puerto 5173)
echo    - El buscador se inicia bajo demanda en la app
echo.
echo ======================================================================
echo.
pause
exit /b 0

:pip_install_failed
echo.
echo ERROR: No se pudieron descargar o instalar las dependencias Python.
echo pip reintentara cada descarga hasta 10 veces y esperara hasta 60 segundos.
echo Verifica la conexion a internet y vuelve a ejecutar este instalador.
echo Las dependencias instaladas anteriormente se conservaran.
echo.
pause
exit /b 1

@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title 📚 Examinator - Inicio Local
cd /d "%~dp0"

echo.
echo ════════════════════════════════════════════════════════════════
echo    📚 EXAMINATOR - INICIO LOCAL
echo ════════════════════════════════════════════════════════════════
echo.

:: ============================================================================
:: ACTUALIZACIÓN AUTOMÁTICA DESDE GITHUB
:: ============================================================================

echo 🔄 Verificando actualizaciones en GitHub...

:: Verificar si git está instalado
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Git no está instalado. Saltando actualización.
    goto :skip_update
)

:: Verificar conexión a GitHub
ping -n 1 github.com >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Sin conexión a internet. Saltando actualización.
    goto :skip_update
)

:: Obtener cambios remotos
git fetch origin Flashcards >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Error al conectar con GitHub. Saltando actualización.
    goto :skip_update
)

:: Verificar si hay cambios
for /f %%i in ('git rev-list HEAD...origin/Flashcards --count 2^>nul') do set COMMITS_BEHIND=%%i

if "%COMMITS_BEHIND%"=="" set COMMITS_BEHIND=0
if "%COMMITS_BEHIND%"=="0" (
    echo ✅ Ya tienes la última versión.
) else (
    echo 📥 Hay %COMMITS_BEHIND% actualizaciones disponibles. Descargando...
    git pull origin Flashcards
    if !errorlevel! equ 0 (
        echo ✅ Actualización completada!
    ) else (
        echo ⚠️ Error al actualizar. Puede haber conflictos locales.
    )
)

:skip_update
echo.

:: ============================================================================
:: VERIFICACIÓN DE PRIMERA EJECUCIÓN / VENV CORRUPTO
:: ============================================================================

set NECESITA_INSTALACION=0

:: Caso 1: No existe el venv
if not exist "venv\Scripts\activate.bat" (
    echo ⚠️ Entorno virtual no encontrado
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

:: Caso 2: El venv es de otra PC
echo 🔍 Verificando entorno virtual...
findstr /C:"%USERNAME%" "venv\pyvenv.cfg" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ════════════════════════════════════════════════════════════════
    echo    ⚠️  ENTORNO VIRTUAL DE OTRA PC DETECTADO
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo    El entorno virtual fue creado en otra computadora.
    echo    Eliminando y recreando...
    echo.
    rmdir /s /q venv 2>nul
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

:: Caso 3: El venv existe pero las dependencias no están instaladas
echo 🔍 Verificando dependencias instaladas...
call "venv\Scripts\python.exe" -c "import fastapi" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ════════════════════════════════════════════════════════════════
    echo    ⚠️  DEPENDENCIAS NO INSTALADAS
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo    El entorno virtual existe pero faltan las dependencias.
    echo    Instalando dependencias...
    echo.
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

echo ✓ Entorno virtual y dependencias válidos

:check_instalacion
if !NECESITA_INSTALACION!==0 goto :venv_ok

:: ============================================================================
:: INSTALACIÓN AUTOMÁTICA (independiente de instalar_primera_vez.bat)
:: ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════
echo    📦 INSTALACIÓN AUTOMÁTICA - Primera ejecución en esta PC
echo ════════════════════════════════════════════════════════════════
echo.
echo    ⏱️ Esto puede tardar 5-15 minutos. NO CIERRES ESTA VENTANA.
echo.

:: Verificar Python
echo [1/6] 🐍 Verificando Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Python no está instalado o no está en PATH
    echo.
    echo    Descarga Python desde: https://www.python.org/downloads/
    echo    ⚠️ IMPORTANTE: Marca "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)
python --version
echo    ✓ Python encontrado

:: Verificar Node.js
echo.
echo [2/6] 📦 Verificando Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Node.js no está instalado
    echo.
    echo    Descarga Node.js desde: https://nodejs.org/
    echo    Instala la versión LTS (recomendada)
    echo.
    pause
    exit /b 1
)
node --version
echo    ✓ Node.js encontrado

:: Crear entorno virtual (solo si no existe)
echo.
echo [3/6] 🔧 Verificando entorno virtual Python...
if exist "venv\Scripts\python.exe" (
    echo    ✓ Entorno virtual ya existe - solo faltan dependencias
) else (
    echo    Creando entorno virtual...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo    ✓ Entorno virtual creado
)

:: Activar e instalar dependencias
echo.
echo [4/6] 📥 Instalando dependencias Python (esto tarda varios minutos)...
echo       Por favor espera, no cierres la ventana...
echo.

call venv\Scripts\activate.bat

echo    [4.1] Instalando servidor FastAPI...
pip install fastapi uvicorn python-multipart requests beautifulsoup4 --quiet
echo       ✓ FastAPI instalado

echo    [4.2] Instalando Flask...
pip install Flask Flask-Cors waitress --quiet
echo       ✓ Flask instalado

echo    [4.3] Instalando utilidades PDF/DOC...
pip install pypdf PyPDF2 python-docx numpy tqdm --quiet
echo       ✓ Utilidades instaladas

echo    [4.4] Instalando buscador IA (puede tardar)...
pip install sentence-transformers faiss-cpu rank-bm25 --quiet
echo       ✓ Buscador IA instalado

echo    [4.5] Instalando PyTorch CPU...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
echo       ✓ PyTorch instalado

echo    [4.6] Instalando llama-cpp (para modelos locales)...
pip install llama-cpp-python --quiet
echo       ✓ llama-cpp instalado

echo    [4.7] Instalando búsqueda web...
pip install ddgs --quiet
echo       ✓ Búsqueda web instalada

echo.
echo    ✅ Todas las dependencias Python instaladas

:: Verificar/instalar dependencias Node
echo.
echo [5/6] ⚛️ Verificando dependencias del frontend...
if not exist "examinator-web\node_modules" (
    echo    Instalando dependencias de React/Vite...
    cd examinator-web
    call npm install
    cd ..
)
echo    ✓ Frontend listo

:: Crear carpetas necesarias
echo.
echo [6/6] 📁 Creando carpetas del proyecto...
if not exist "extracciones" mkdir extracciones
if not exist "datos_persistentes" mkdir datos_persistentes
if not exist "chats" mkdir chats
if not exist "chats_historial" mkdir chats_historial
if not exist "indice_busqueda" mkdir indice_busqueda
if not exist "examenes_de_archivos" mkdir examenes_de_archivos
if not exist "logs_practicas_detallado" mkdir logs_practicas_detallado
if not exist "temp" mkdir temp
if not exist "modelos" mkdir modelos
if not exist "md" mkdir md
echo    ✓ Carpetas creadas

echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ INSTALACIÓN COMPLETADA - Continuando con el inicio...
echo ════════════════════════════════════════════════════════════════
echo.

:venv_ok

:: Verificar si las dependencias de Node están instaladas
if not exist "examinator-web\node_modules" (
    echo ⚠️ Dependencias de frontend no encontradas - Instalando...
    cd examinator-web
    call npm install
    cd ..
    echo.
)

:: ============================================================================
:: CREAR CARPETAS SI NO EXISTEN
:: ============================================================================

if not exist "extracciones" mkdir extracciones
if not exist "datos_persistentes" mkdir datos_persistentes
if not exist "chats" mkdir chats
if not exist "indice_busqueda" mkdir indice_busqueda

:: ============================================================================
:: INICIAR SERVIDORES
:: ============================================================================

echo 🔄 Liberando puertos 8000 y 5173...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
timeout /t 1 /nobreak >nul
echo ✓ Puertos liberados
echo.

:: NOTA: El buscador IA ya NO se inicia automáticamente
:: Se iniciará bajo demanda cuando abras la pestaña de búsqueda en la app
:: Esto ahorra recursos del sistema al inicio

:: Guardar rutas absolutas con comillas para manejar espacios
set "PYTHON_VENV=%CD%\venv\Scripts\python.exe"
set "API_SERVER=%CD%\api_server.py"
set "FRONTEND_DIR=%CD%\examinator-web"

:: Iniciar Backend
echo 🔥 Iniciando Backend API (puerto 8000)...
start /min "Backend API" cmd /c ""%PYTHON_VENV%" "%API_SERVER%""
timeout /t 2 >nul

:: Iniciar Frontend
echo 🎨 Iniciando Frontend Web (puerto 5173)...
start /min "Frontend" cmd /c "cd /d "%FRONTEND_DIR%" && npm run dev"
timeout /t 3 >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ SERVIDORES INICIADOS
echo ════════════════════════════════════════════════════════════════
echo.
echo 🌐 Abre: http://localhost:5173
echo.
echo ════════════════════════════════════════════════════════════════
echo.

:: Abrir navegador
timeout /t 2 >nul
start http://localhost:5173

echo ✅ Listo! Los servidores corren en segundo plano (minimizados).
echo    Para cerrarlos: usa el Administrador de tareas o DETENER_BUSCADOR.ps1
echo.
pause >nul

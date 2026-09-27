@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
title  Examinator - Inicio Local
cd /d "%~dp0"

echo.
echo ================================================================
echo     EXAMINATOR - INICIO LOCAL
echo ================================================================
echo.

:: ============================================================================
:: ACTUALIZACION AUTOMATICA DESDE GITHUB
:: ============================================================================

echo  Verificando actualizaciones en GitHub...

:: Verificar si git esta instalado
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Git no esta instalado. Saltando actualizacion.
    goto :skip_update
)

:: Verificar conexion a GitHub
ping -n 1 github.com >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Sin conexion a internet. Saltando actualizacion.
    goto :skip_update
)

:: Obtener cambios remotos
git fetch origin Flashcards >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Error al conectar con GitHub. Saltando actualizacion.
    goto :skip_update
)

:: Verificar si hay cambios
for /f %%i in ('git rev-list HEAD...origin/Flashcards --count 2^>nul') do set COMMITS_BEHIND=%%i

if "%COMMITS_BEHIND%"=="" set COMMITS_BEHIND=0
if "%COMMITS_BEHIND%"=="0" (
    echo [OK] Ya tienes la ultima version.
) else (
    echo  Hay %COMMITS_BEHIND% actualizaciones disponibles. Descargando...
    git pull origin Flashcards
    if !errorlevel! equ 0 (
        echo [OK] Actualizacion completada!
    ) else (
        echo ADVERTENCIA: Error al actualizar. Puede haber conflictos locales.
    )
)

:skip_update
echo.

:: ============================================================================
:: VERIFICACION DE PRIMERA EJECUCION / VENV CORRUPTO
:: ============================================================================

set NECESITA_INSTALACION=0

:: Caso 1: No existe el venv
if not exist "venv\Scripts\activate.bat" (
    echo ADVERTENCIA: Entorno virtual no encontrado
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

:: Caso 2: El venv es de otra PC
echo  Verificando entorno virtual...
findstr /C:"%USERNAME%" "venv\pyvenv.cfg" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ================================================================
    echo    ADVERTENCIA:  ENTORNO VIRTUAL DE OTRA PC DETECTADO
    echo ================================================================
    echo.
    echo    El entorno virtual fue creado en otra computadora.
    echo    Eliminando y recreando...
    echo.
    rmdir /s /q venv 2>nul
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

:: Caso 3: El venv existe pero las dependencias no estan instaladas
echo  Verificando dependencias instaladas...
call "venv\Scripts\python.exe" -c "import fastapi" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ================================================================
    echo    ADVERTENCIA:  DEPENDENCIAS NO INSTALADAS
    echo ================================================================
    echo.
    echo    El entorno virtual existe pero faltan las dependencias.
    echo    Instalando dependencias...
    echo.
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

echo [OK] Entorno virtual y dependencias validos

:check_instalacion
if !NECESITA_INSTALACION!==0 goto :venv_ok

:: ============================================================================
:: INSTALACION AUTOMATICA (independiente de instalar_primera_vez.bat)
:: ============================================================================

echo.
echo ================================================================
echo     INSTALACION AUTOMATICA - Primera ejecucion en esta PC
echo ================================================================
echo.
echo     Esto puede tardar 5-15 minutos. NO CIERRES ESTA VENTANA.
echo.

:: Verificar Python
echo [1/6]  Verificando Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: ERROR: Python no esta instalado o no esta en PATH
    echo.
    echo    Descarga Python desde: https://www.python.org/downloads/
    echo    ADVERTENCIA: IMPORTANTE: Marca "Add Python to PATH" durante la instalacion
    echo.
    pause
    exit /b 1
)
python --version
echo    [OK] Python encontrado

:: Verificar Node.js
echo.
echo [2/6]  Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: ERROR: Node.js no esta instalado
    echo.
    echo    Descarga Node.js desde: https://nodejs.org/
    echo    Instala la version LTS recomendada.
    echo.
    pause
    exit /b 1
)
node --version
echo    [OK] Node.js encontrado

:: Crear entorno virtual (solo si no existe)
echo.
echo [3/6]  Verificando entorno virtual Python...
if exist "venv\Scripts\python.exe" (
    echo    [OK] Entorno virtual ya existe - solo faltan dependencias
) else (
    echo    Creando entorno virtual...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ERROR: Error creando entorno virtual
        pause
        exit /b 1
    )
    echo    [OK] Entorno virtual creado
)

:: Activar e instalar dependencias
echo.
echo [4/6] Instalando dependencias Python. Esto tarda varios minutos.
echo       Por favor espera, no cierres la ventana...
echo.

call venv\Scripts\activate.bat

echo    [4.1] Instalando servidor FastAPI...
pip install fastapi uvicorn python-multipart requests beautifulsoup4 --quiet
echo       [OK] FastAPI instalado

echo    [4.2] Instalando Flask...
pip install Flask Flask-Cors waitress --quiet
echo       [OK] Flask instalado

echo    [4.3] Instalando utilidades PDF/DOC...
pip install pypdf PyPDF2 python-docx numpy tqdm --quiet
echo       [OK] Utilidades instaladas

echo    [4.4] Instalando buscador IA (puede tardar)...
pip install sentence-transformers faiss-cpu rank-bm25 --quiet
echo       [OK] Buscador IA instalado

echo    [4.5] Instalando PyTorch CPU...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
echo       [OK] PyTorch instalado

echo    [4.6] Instalando llama-cpp (para modelos locales)...
pip install llama-cpp-python --quiet
echo       [OK] llama-cpp instalado

echo    [4.7] Instalando busqueda web...
pip install ddgs --quiet
echo       [OK] Busqueda web instalada

echo.
echo    [OK] Todas las dependencias Python instaladas

:: Verificar/instalar dependencias Node
echo.
echo [5/6]  Verificando dependencias del frontend...
if not exist "examinator-web\node_modules" (
    echo    Instalando dependencias de React/Vite...
    cd examinator-web
    call npm install
    cd ..
)
echo    [OK] Frontend listo

:: Crear carpetas necesarias
echo.
echo [6/6]  Creando carpetas del proyecto...
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
echo    [OK] Carpetas creadas

echo.
echo ================================================================
echo    [OK] INSTALACION COMPLETADA - Continuando con el inicio...
echo ================================================================
echo.

:venv_ok

:: Verificar si las dependencias de Node estan instaladas
set "TIENE_NODE=0"
node --version >nul 2>&1
if not errorlevel 1 set "TIENE_NODE=1"

if "!TIENE_NODE!"=="1" (
    if not exist "examinator-web\package.json" (
        echo ERROR: No se encontro examinator-web\package.json.
        exit /b 1
    )
    if not exist "examinator-web\node_modules\.bin\vite.cmd" (
        echo Dependencias del frontend no encontradas. Instalando...
        call npm --prefix "%CD%\examinator-web" install
        if errorlevel 1 (
            echo ERROR: No se pudieron instalar las dependencias del frontend.
            pause
            exit /b 1
        )
        if not exist "examinator-web\node_modules\.bin\vite.cmd" (
            echo ERROR: npm termino, pero no se encontro Vite en node_modules.
            pause
            exit /b 1
        )
    )
) else (
    echo ADVERTENCIA: Node.js no esta disponible; se iniciara solo el backend.
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

echo  Liberando puertos 8000 y 5173...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
timeout /t 1 /nobreak >nul
echo [OK] Puertos liberados
echo.

:: NOTA: El buscador IA ya NO se inicia automaticamente
:: Se iniciara bajo demanda cuando abras la pestana de busqueda en la app
:: Esto ahorra recursos del sistema al inicio

:: Guardar rutas absolutas con comillas para manejar espacios
set "PYTHON_VENV=%CD%\venv\Scripts\python.exe"
set "API_SERVER=%CD%\api_server.py"
set "FRONTEND_DIR=%CD%\examinator-web"

if not exist "%PYTHON_VENV%" (
    echo ERROR: No se encontro el Python del entorno virtual: "%PYTHON_VENV%"
    pause
    exit /b 1
)
if not exist "%API_SERVER%" (
    echo ERROR: No se encontro el servidor API: "%API_SERVER%"
    pause
    exit /b 1
)
"%PYTHON_VENV%" -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Faltan dependencias del backend. Vuelve a ejecutar instalar_primera_vez.bat.
    pause
    exit /b 1
)

:: Iniciar Backend
echo  Iniciando Backend API (puerto 8000)...
start "Backend API" /D "%CD%" cmd /k ""%PYTHON_VENV%" "%API_SERVER%""
timeout /t 2 >nul

:: Iniciar Frontend
if "!TIENE_NODE!"=="1" (
    echo Iniciando Frontend Web (puerto 5173)...
    start "Frontend" /D "%FRONTEND_DIR%" cmd /k npm run dev
    timeout /t 3 >nul
)

echo.
echo ================================================================
echo    [OK] SERVIDORES INICIADOS
echo ================================================================
echo.
if "!TIENE_NODE!"=="1" (
    echo Abre: http://localhost:5173
) else (
    echo Backend: http://localhost:8000
)
echo.
echo ================================================================
echo.

:: Abrir el frontend solamente cuando Node.js esta disponible
if "!TIENE_NODE!"=="1" (
    timeout /t 2 >nul
    start http://localhost:5173
)

echo Listo. Las ventanas de los servidores permanecen abiertas para mostrar errores.
echo Para detenerlos, usa Ctrl+C en cada ventana.
echo.
pause >nul

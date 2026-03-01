@echo off
chcp 65001 > nul
color 0A
cls

echo ================================================================================
echo                         🚀 EXAMINATOR - INICIADOR
echo ================================================================================
echo.

REM Verificar que estamos en el directorio correcto
cd /d "%~dp0"

echo [1/7] 📍 Verificando directorio...
echo Ubicación: %CD%
echo.

REM ============================================================================
REM ACTUALIZACIÓN AUTOMÁTICA DESDE GITHUB
REM ============================================================================

echo [2/7] 🔄 Verificando actualizaciones en GitHub...

REM Verificar si git está instalado
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️ Git no está instalado. Saltando actualización.
    goto :skip_update
)

REM Verificar conexión a GitHub
ping -n 1 github.com >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️ Sin conexión a internet. Saltando actualización.
    goto :skip_update
)

REM Obtener cambios remotos
git fetch origin Flashcards >nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️ Error al conectar con GitHub. Saltando actualización.
    goto :skip_update
)

REM Verificar si hay cambios
for /f %%i in ('git rev-list HEAD...origin/Flashcards --count 2^>nul') do set COMMITS_BEHIND=%%i

if "%COMMITS_BEHIND%"=="" set COMMITS_BEHIND=0
if "%COMMITS_BEHIND%"=="0" (
    echo    ✅ Ya tienes la última versión.
) else (
    echo    📥 Hay %COMMITS_BEHIND% actualizaciones disponibles. Descargando...
    git pull origin Flashcards
    if %errorlevel% equ 0 (
        echo    ✅ Actualización completada!
    ) else (
        echo    ⚠️ Error al actualizar. Puede haber conflictos locales.
    )
)

:skip_update
echo.

REM ============================================================================
REM VERIFICACIÓN DE PRIMERA EJECUCIÓN / VENV CORRUPTO
REM ============================================================================

set NECESITA_INSTALACION=0

REM Caso 1: No existe el venv
if not exist "venv\Scripts\activate.bat" (
    echo ⚠️ Entorno virtual no encontrado
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

REM Caso 2: El venv es de otra PC (verificar que contiene el usuario actual)
echo [2.5/7] 🔍 Verificando entorno virtual...
findstr /C:"%USERNAME%" "venv\pyvenv.cfg" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo    ⚠️  ENTORNO VIRTUAL DE OTRA PC DETECTADO
    echo ================================================================================
    echo.
    echo    El entorno virtual fue creado en otra computadora.
    echo    Los entornos virtuales de Python NO son portables entre máquinas.
    echo.
    echo    Eliminando venv antiguo...
    rmdir /s /q venv 2>nul
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

REM Caso 3: El venv existe pero las dependencias no están instaladas
echo [2.6/7] 🔍 Verificando dependencias instaladas...
"venv\Scripts\python.exe" -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo    ⚠️  DEPENDENCIAS NO INSTALADAS
    echo ================================================================================
    echo.
    echo    El entorno virtual existe pero faltan las dependencias.
    echo    Instalando dependencias...
    echo.
    set NECESITA_INSTALACION=1
    goto :check_instalacion
) else (
    echo    ✓ Dependencias instaladas
)

echo    ✓ Entorno virtual válido

:check_instalacion
if %NECESITA_INSTALACION%==0 goto :venv_ok

REM ============================================================================
REM INSTALACIÓN AUTOMÁTICA DEL ENTORNO (independiente de instalar_primera_vez.bat)
REM ============================================================================

echo.
echo ================================================================================
echo    📦 INSTALACIÓN AUTOMÁTICA - Primera ejecución en esta PC
echo ================================================================================
echo.
echo    ⏱️ Esto puede tardar 5-15 minutos. NO CIERRES ESTA VENTANA.
echo.

REM Verificar Python
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

REM Verificar Node.js
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

REM Crear entorno virtual (solo si no existe)
echo.
echo [3/6] 🔧 Verificando entorno virtual Python...
if exist "venv\Scripts\python.exe" (
    echo    ✓ Entorno virtual ya existe - solo faltan dependencias
) else (
    echo    Creando entorno virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo    ✓ Entorno virtual creado
)

REM Activar e instalar dependencias
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

REM Verificar/instalar dependencias Node
echo.
echo [5/6] ⚛️ Verificando dependencias del frontend...
if not exist "examinator-web\node_modules" (
    echo    Instalando dependencias de React/Vite...
    cd examinator-web
    call npm install
    cd ..
)
echo    ✓ Frontend listo

REM Crear carpetas necesarias
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
echo ================================================================================
echo    ✅ INSTALACIÓN COMPLETADA - Continuando con el inicio...
echo ================================================================================
echo.

:venv_ok

if not exist "examinator-web\node_modules" (
    echo ⚠️ Dependencias frontend no encontradas - Instalando...
    cd examinator-web
    call npm install
    cd ..
    echo.
)

REM Crear carpetas si no existen (por si acaso)
if not exist "extracciones" mkdir extracciones
if not exist "datos_persistentes" mkdir datos_persistentes
if not exist "chats" mkdir chats
if not exist "indice_busqueda" mkdir indice_busqueda

REM Matar procesos en puertos si existen
echo [3/7] 🔄 Liberando puertos 8000 y 5173...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
timeout /t 1 /nobreak > nul
echo    ✓ Puertos liberados
echo.

REM NOTA: El buscador IA ya NO se inicia automáticamente
REM Se iniciará bajo demanda cuando abras la pestaña de búsqueda en la app
REM Esto ahorra recursos del sistema al inicio

REM Guardar rutas absolutas con comillas para manejar espacios
set "PYTHON_VENV=%CD%\venv\Scripts\python.exe"
set "API_SERVER=%CD%\api_server.py"
set "FRONTEND_DIR=%CD%\examinator-web"

REM Iniciar servidor backend
echo [4/7] 🐍 Iniciando servidor Backend (Python/FastAPI)...
start "Examinator Backend" cmd /k "echo 🚀 SERVIDOR BACKEND - No cierres esta ventana && echo. && "%PYTHON_VENV%" "%API_SERVER%""
timeout /t 3 /nobreak > nul
echo    ✓ Backend iniciado en http://localhost:8000
echo.

REM Iniciar servidor frontend
echo [5/7] ⚛️ Iniciando servidor Frontend (React/Vite)...
start "Examinator Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && echo 🎨 SERVIDOR FRONTEND - No cierres esta ventana && echo. && npm run dev"
timeout /t 3 /nobreak > nul
echo    ✓ Frontend iniciando en http://localhost:5173
echo.

echo ================================================================================
echo                          ✅ EXAMINATOR INICIADO
echo ================================================================================
echo.
echo 📍 URLs disponibles:
echo    • Frontend: http://localhost:5173
echo    • Backend:  http://localhost:8000
echo    • API Docs: http://localhost:8000/docs
echo.
echo 💡 Notas:
echo    - El buscador IA se inicia automáticamente al abrir la pestaña de búsqueda
echo    - No cierres las ventanas que se abrieron
echo.
echo Esperando 5 segundos para abrir el navegador...
timeout /t 5 /nobreak > nul

REM Abrir navegador
start http://localhost:5173

echo.
echo ✓ Navegador abierto
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
echo (Los servidores seguirán corriendo en sus propias ventanas)
pause > nul

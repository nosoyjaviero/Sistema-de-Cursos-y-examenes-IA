@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
color 0A
cls

echo ================================================================================
echo                          EXAMINATOR - INICIADOR
echo ================================================================================
echo.

REM Verificar que estamos en el directorio correcto
cd /d "%~dp0"

echo [1/7]  Verificando directorio...
echo Ubicacion: %CD%
echo.

REM ============================================================================
REM ACTUALIZACION AUTOMATICA DESDE GITHUB
REM ============================================================================

echo [2/7]  Verificando actualizaciones en GitHub...

REM Verificar si git esta instalado
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo    ADVERTENCIA: Git no esta instalado. Saltando actualizacion.
    goto :skip_update
)

REM Verificar conexion a GitHub
ping -n 1 github.com >nul 2>&1
if %errorlevel% neq 0 (
    echo    ADVERTENCIA: Sin conexion a internet. Saltando actualizacion.
    goto :skip_update
)

REM Obtener cambios remotos
git fetch origin Flashcards >nul 2>&1
if %errorlevel% neq 0 (
    echo    ADVERTENCIA: Error al conectar con GitHub. Saltando actualizacion.
    goto :skip_update
)

REM Verificar si hay cambios
for /f %%i in ('git rev-list HEAD...origin/Flashcards --count 2^>nul') do set COMMITS_BEHIND=%%i

if "%COMMITS_BEHIND%"=="" set COMMITS_BEHIND=0
if "%COMMITS_BEHIND%"=="0" (
    echo    [OK] Ya tienes la ultima version.
) else (
    echo     Hay %COMMITS_BEHIND% actualizaciones disponibles. Descargando...
    git pull origin Flashcards
    if !errorlevel! equ 0 (
        echo    [OK] Actualizacion completada!
    ) else (
        echo    ADVERTENCIA: Error al actualizar. Puede haber conflictos locales.
    )
)

:skip_update
echo.

REM ============================================================================
REM VERIFICACION DE PRIMERA EJECUCION / VENV CORRUPTO
REM ============================================================================

set NECESITA_INSTALACION=0
set NECESITA_LLAMA=0

REM Caso 1: No existe el venv
if not exist "venv\Scripts\activate.bat" (
    echo ADVERTENCIA: Entorno virtual no encontrado
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

REM Caso 2: El venv es de otra PC (verificar que contiene el usuario actual)
echo [2.5/7]  Verificando entorno virtual...
findstr /C:"%USERNAME%" "venv\pyvenv.cfg" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ================================================================================
    echo    ADVERTENCIA:  ENTORNO VIRTUAL DE OTRA PC DETECTADO
    echo ================================================================================
    echo.
    echo    El entorno virtual fue creado en otra computadora.
    echo    Los entornos virtuales de Python NO son portables entre maquinas.
    echo.
    echo    Eliminando venv antiguo...
    rmdir /s /q venv 2>nul
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

REM Caso 3: El venv existe pero las dependencias no estan instaladas
echo [2.6/7]  Verificando dependencias instaladas...
call "venv\Scripts\python.exe" -c "import fastapi" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ================================================================================
    echo    ADVERTENCIA:  DEPENDENCIAS NO INSTALADAS
    echo ================================================================================
    echo.
    echo    El entorno virtual existe pero faltan las dependencias.
    echo    Instalando dependencias...
    echo.
    set NECESITA_INSTALACION=1
    goto :check_instalacion
)

echo    [OK] Dependencias instaladas
echo    [OK] Entorno virtual valido
call "venv\Scripts\python.exe" -c "import llama_cpp" >nul 2>&1
if !errorlevel! neq 0 (
    echo    [AVISO] Falta llama-cpp-python; se instalara antes de iniciar.
    set NECESITA_LLAMA=1
)

:check_instalacion
if !NECESITA_INSTALACION!==0 goto :venv_ok

REM ============================================================================
REM INSTALACION AUTOMATICA DEL ENTORNO (independiente de instalar_primera_vez.bat)
REM ============================================================================

echo.
echo ================================================================================
echo     INSTALACION AUTOMATICA - Primera ejecucion en esta PC
echo ================================================================================
echo.
echo     Esto puede tardar 5-15 minutos. NO CIERRES ESTA VENTANA.
echo.

REM Verificar Python
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

REM Verificar Node.js (opcional - el backend funciona sin el)
echo.
echo [2/6]  Verificando Node.js...
set TIENE_NODE=0
node --version >nul 2>&1
if not errorlevel 1 set TIENE_NODE=1

if "!TIENE_NODE!"=="0" (
    echo.
    echo    ADVERTENCIA: Node.js no esta instalado
    echo    El BACKEND funcionara, pero el FRONTEND web no estara disponible.
    echo    Para instalar Node.js despues: https://nodejs.org/
    echo.
) else (
    node --version
    echo    [OK] Node.js encontrado
)

REM Crear entorno virtual (solo si no existe y esta completo)
echo.
echo [3/6]  Verificando entorno virtual Python...

REM Verificar que el venv este completo (debe tener pyvenv.cfg)
set VENV_OK=0
if exist "venv\Scripts\python.exe" (
    if exist "venv\pyvenv.cfg" (
        set VENV_OK=1
    )
)

if !VENV_OK!==1 (
    echo    [OK] Entorno virtual ya existe - solo faltan dependencias
) else (
    if exist "venv" (
        echo    ADVERTENCIA: Entorno virtual incompleto - recreando...
        rmdir /s /q venv 2>nul
    )
    echo    Creando entorno virtual...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ERROR: Error creando entorno virtual
        pause
        exit /b 1
    )
    echo    [OK] Entorno virtual creado
)

REM Activar e instalar dependencias
echo.
echo [4/6]  Instalando dependencias Python (esto tarda varios minutos)...
echo       Por favor espera, no cierres la ventana...
echo.

REM Usar ruta absoluta para pip (mas robusto que activate con espacios en ruta)
set "VENV_PIP=%CD%\venv\Scripts\pip.exe"
set "VENV_PYTHON=%CD%\venv\Scripts\python.exe"

echo    [4.0] Actualizando pip...
"%VENV_PYTHON%" -m pip install --upgrade pip --quiet
echo       [OK] pip actualizado

echo    [4.1] Instalando dependencias base...
"%VENV_PIP%" install wheel setuptools filelock fsspec huggingface-hub
echo       [OK] Dependencias base instaladas

echo    [4.2] Instalando servidor FastAPI...
"%VENV_PIP%" install fastapi uvicorn python-multipart requests beautifulsoup4
if !errorlevel! neq 0 (
    echo       ADVERTENCIA: Reintentando FastAPI...
    "%VENV_PIP%" install fastapi uvicorn python-multipart requests beautifulsoup4 --force-reinstall
)
REM Verificar que FastAPI se instalo
"%VENV_PYTHON%" -c "import fastapi" >nul 2>&1
if !errorlevel! neq 0 (
    echo       ERROR: ERROR: FastAPI no se instalo correctamente
    echo       Intentando instalacion forzada...
    "%VENV_PIP%" install fastapi --force-reinstall --no-cache-dir
)
echo       [OK] FastAPI instalado

echo    [4.3] Instalando Flask...
"%VENV_PIP%" install Flask Flask-Cors waitress
echo       [OK] Flask instalado

echo    [4.4] Instalando utilidades PDF/DOC...
"%VENV_PIP%" install pypdf PyPDF2 python-docx numpy tqdm
echo       [OK] Utilidades instaladas

echo    [4.5] Instalando buscador IA (puede tardar)...
"%VENV_PIP%" install sentence-transformers faiss-cpu rank-bm25
echo       [OK] Buscador IA instalado

echo    [4.6] Instalando PyTorch CPU...
"%VENV_PIP%" install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
echo       [OK] PyTorch instalado

echo    [4.7] Instalando llama-cpp (para modelos locales)...
"%VENV_PYTHON%" -m pip install --retries 10 --timeout 60 --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu llama-cpp-python
if !errorlevel! neq 0 (
    echo       ERROR: No se pudo instalar llama-cpp-python.
    echo       Comprueba la conexion y vuelve a ejecutar iniciar.bat.
    pause
    exit /b 1
)
"%VENV_PYTHON%" -c "import llama_cpp" >nul 2>&1
if !errorlevel! neq 0 (
    echo       ERROR: llama_cpp no se puede importar despues de instalarlo.
    echo       Comprueba la instalacion y vuelve a ejecutar iniciar.bat.
    pause
    exit /b 1
)
echo       [OK] llama-cpp instalado y verificado

echo    [4.8] Instalando busqueda web...
"%VENV_PIP%" install ddgs
echo       [OK] Busqueda web instalada

echo.
echo    [4.9] Verificando instalacion...
"%VENV_PYTHON%" -c "import fastapi; import torch; print('OK')" >nul 2>&1
if !errorlevel! neq 0 (
    echo       ADVERTENCIA: Reparando dependencias faltantes...
    "%VENV_PIP%" install --upgrade fastapi uvicorn torch --no-cache-dir
)
echo       [OK] Verificacion completada

echo.
echo    [OK] Todas las dependencias Python instaladas

REM Verificar/instalar dependencias Node (solo si Node.js esta instalado)
echo.
echo [5/6]  Verificando dependencias del frontend...
if "!TIENE_NODE!"=="0" (
    echo     Saltando frontend - Node.js no instalado
) else (
    REM Verificar si vite esta instalado (indicador de npm install completo)
    if not exist "examinator-web\node_modules\.bin\vite.cmd" (
        echo    Instalando dependencias de React/Vite...
        echo    Esto puede tardar unos minutos.
        set "FRONTEND_PATH=%CD%\examinator-web"
        cmd /c "cd /d "!FRONTEND_PATH!" && npm install"
        if not exist "examinator-web\node_modules\.bin\vite.cmd" (
            echo    ADVERTENCIA: Error instalando frontend - reintentando...
            cmd /c "cd /d "!FRONTEND_PATH!" && npm install --force"
        )
    )
    if exist "examinator-web\node_modules\.bin\vite.cmd" (
        echo    [OK] Frontend listo
    ) else (
        echo    ADVERTENCIA: Frontend no se pudo instalar completamente
        echo    Ejecuta manualmente: cd examinator-web ^&^& npm install
    )
)

REM Crear carpetas necesarias
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
echo ================================================================================
echo    [OK] INSTALACION COMPLETADA - Continuando con el inicio...
echo ================================================================================
echo.

:venv_ok

if "!NECESITA_LLAMA!"=="1" (
    echo.
    echo Instalando llama-cpp-python para habilitar modelos GGUF...
    "venv\Scripts\python.exe" -m pip install --retries 10 --timeout 60 --prefer-binary --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu llama-cpp-python
    if !errorlevel! neq 0 (
        echo ERROR: No se pudo instalar llama-cpp-python.
        echo Revisa tu conexion e intenta de nuevo.
        pause
        exit /b 1
    )
    "venv\Scripts\python.exe" -c "import llama_cpp" >nul 2>&1
    if !errorlevel! neq 0 (
        echo ERROR: La instalacion termino, pero llama_cpp no se puede importar.
        echo Ejecuta: venv\Scripts\python.exe -m pip install llama-cpp-python
        pause
        exit /b 1
    )
    echo [OK] llama-cpp-python instalado y verificado.
)

REM Verificar Node.js ejecutandolo directamente
set TIENE_NODE=0
node --version >nul 2>&1
if not errorlevel 1 set TIENE_NODE=1

if "!TIENE_NODE!"=="1" (
    if not exist "examinator-web\node_modules\.bin\vite.cmd" (
        echo ADVERTENCIA: Dependencias frontend no encontradas - Instalando...
        call npm --prefix "%CD%\examinator-web" install
        if errorlevel 1 (
            echo ADVERTENCIA: npm install fallo. Reintentando...
            call npm --prefix "%CD%\examinator-web" install --force
        )
        if errorlevel 1 (
            echo ADVERTENCIA: No se pudieron instalar las dependencias frontend.
            set TIENE_NODE=0
        )
    )
)

REM Crear carpetas si no existen (por si acaso)
if not exist "extracciones" mkdir extracciones
if not exist "datos_persistentes" mkdir datos_persistentes
if not exist "chats" mkdir chats
if not exist "indice_busqueda" mkdir indice_busqueda

REM Matar procesos en puertos si existen
echo [3/7]  Liberando puertos 8000 y 5173...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
timeout /t 1 /nobreak > nul
echo    [OK] Puertos liberados
echo.

REM NOTA: El buscador IA ya NO se inicia automaticamente
REM Se iniciara bajo demanda cuando abras la pestana de busqueda en la app
REM Esto ahorra recursos del sistema al inicio

REM Guardar rutas absolutas con comillas para manejar espacios
set "PYTHON_VENV=%CD%\venv\Scripts\python.exe"
set "API_SERVER=%CD%\api_server.py"
set "FRONTEND_DIR=%CD%\examinator-web"

REM Iniciar servidor backend
echo [4/7]  Iniciando servidor Backend (Python/FastAPI)...
start "Examinator Backend" /D "%CD%" cmd /k ""%PYTHON_VENV%" "%API_SERVER%""
timeout /t 3 /nobreak > nul
echo    [OK] Backend iniciado en http://localhost:8000
echo.

REM Iniciar servidor frontend (solo si Node.js esta disponible y archivos existen)
REM Verificar Node.js de nuevo aqui para estar seguros
set TIENE_NODE=0
node --version >nul 2>&1
if not errorlevel 1 set TIENE_NODE=1

if "!TIENE_NODE!"=="1" (
    if exist "examinator-web\node_modules\.bin\vite.cmd" (
        echo [5/7]  Iniciando servidor Frontend (React/Vite^)...
        start "Examinator Frontend" /D "%FRONTEND_DIR%" cmd /k npm run dev
        timeout /t 3 /nobreak > nul
        echo    [OK] Frontend iniciando en http://localhost:5173
    ) else (
        echo [5/7]  Frontend no disponible
        echo    ADVERTENCIA: Faltan las dependencias de Vite. Ejecuta npm install en examinator-web.
        set TIENE_NODE=0
    )
) else (
    echo [5/7]  Frontend no disponible - Node.js no detectado
)
echo.

echo ================================================================================
echo                          [OK] EXAMINATOR INICIADO
echo ================================================================================
echo.
if "!TIENE_NODE!"=="1" (
    echo  URLs disponibles:
    echo    - Frontend: http://localhost:5173
    echo    - Backend:  http://localhost:8000
) else (
    echo  URL disponible:
    echo    - Backend:  http://localhost:8000
    echo.
    echo ADVERTENCIA: Frontend no disponible - Instala Node.js para la interfaz web
)
echo.
echo  No cierres las ventanas que se abrieron
echo.
echo Esperando 5 segundos para abrir el navegador...
timeout /t 5 /nobreak > nul

REM Verificar Node.js de nuevo antes de abrir navegador
set TIENE_NODE_FINAL=0
node --version >nul 2>&1
if not errorlevel 1 set TIENE_NODE_FINAL=1

REM Abrir navegador - solo frontend si Node.js existe
if "!TIENE_NODE_FINAL!"=="1" (
    start http://localhost:5173
    echo.
    echo [OK] Navegador abierto en Frontend
) else (
    echo.
    echo ADVERTENCIA: No se puede abrir el frontend - Node.js no detectado
    echo    Backend disponible en: http://localhost:8000
)
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
echo (Los servidores seguiran corriendo en sus propias ventanas)
pause > nul

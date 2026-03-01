@echo off
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
    if %errorlevel% equ 0 (
        echo ✅ Actualización completada!
    ) else (
        echo ⚠️ Error al actualizar. Puede haber conflictos locales.
    )
)

:skip_update
echo.

:: ============================================================================
:: VERIFICACIÓN DE PRIMERA EJECUCIÓN
:: ============================================================================

:: Verificar si el entorno virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo ⚠️ Primera ejecución detectada - Iniciando instalación...
    echo.
    call instalar_primera_vez.bat
    if %errorlevel% neq 0 (
        echo ❌ Error en la instalación. Revisa los mensajes anteriores.
        pause
        exit /b 1
    )
    echo.
    echo 🔄 Continuando con el inicio del sistema...
    echo.
)

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

:: Iniciar Backend
echo 🔥 Iniciando Backend API (puerto 8000)...
start /min "Backend API" cmd /c "cd /d %~dp0 && venv\Scripts\activate.bat && python api_server.py"
timeout /t 2 >nul

:: Iniciar Frontend
echo 🎨 Iniciando Frontend Web (puerto 5173)...
start /min "Frontend" cmd /c "cd /d %~dp0\examinator-web && npm run dev"
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

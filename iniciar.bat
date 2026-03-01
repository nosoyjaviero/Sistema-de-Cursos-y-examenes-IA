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

echo [1/6] 📍 Verificando directorio...
echo Ubicación: %CD%
echo.

REM ============================================================================
REM VERIFICACIÓN DE PRIMERA EJECUCIÓN
REM ============================================================================

if not exist "venv\Scripts\activate.bat" (
    echo ⚠️ Primera ejecución detectada - Iniciando instalación automática...
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

if not exist "examinator-web\node_modules" (
    echo ⚠️ Dependencias frontend no encontradas - Instalando...
    cd examinator-web
    call npm install
    cd ..
    echo.
)

REM Crear carpetas si no existen
if not exist "extracciones" mkdir extracciones
if not exist "datos_persistentes" mkdir datos_persistentes
if not exist "chats" mkdir chats
if not exist "indice_busqueda" mkdir indice_busqueda

REM Matar procesos en puertos si existen
echo [2/6] 🔄 Liberando puertos 8000 y 5173...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
timeout /t 1 /nobreak > nul
echo    ✓ Puertos liberados
echo.

REM NOTA: El buscador IA ya NO se inicia automáticamente
REM Se iniciará bajo demanda cuando abras la pestaña de búsqueda en la app
REM Esto ahorra recursos del sistema al inicio

REM Iniciar servidor backend
echo [3/6] 🐍 Iniciando servidor Backend (Python/FastAPI)...
start "Examinator Backend" cmd /k "echo 🚀 SERVIDOR BACKEND - No cierres esta ventana && echo. && venv\Scripts\python.exe api_server.py"
timeout /t 3 /nobreak > nul
echo    ✓ Backend iniciado en http://localhost:8000
echo.

REM Iniciar servidor frontend
echo [4/6] ⚛️ Iniciando servidor Frontend (React/Vite)...
cd examinator-web
start "Examinator Frontend" cmd /k "echo 🎨 SERVIDOR FRONTEND - No cierres esta ventana && echo. && npm run dev"
cd ..
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

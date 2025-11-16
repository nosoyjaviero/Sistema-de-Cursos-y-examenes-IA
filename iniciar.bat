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

echo [1/4] 📍 Verificando directorio...
echo Ubicación: %CD%
echo.

REM Matar procesos en puertos si existen
echo [2/4] 🔄 Liberando puertos 8000 y 5173...
powershell -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }" 2>nul
powershell -Command "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }" 2>nul
timeout /t 2 /nobreak > nul
echo    ✓ Puertos liberados
echo.

REM Iniciar servidor backend
echo [3/4] 🐍 Iniciando servidor Backend (Python/FastAPI)...
start "Examinator Backend" cmd /k "echo 🚀 SERVIDOR BACKEND - No cierres esta ventana && echo. && venv\Scripts\python.exe api_server.py"
timeout /t 3 /nobreak > nul
echo    ✓ Backend iniciado en http://localhost:8000
echo.

REM Iniciar servidor frontend
echo [4/4] ⚛️ Iniciando servidor Frontend (React/Vite)...
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
echo 💡 Tip: No cierres las ventanas que se abrieron
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

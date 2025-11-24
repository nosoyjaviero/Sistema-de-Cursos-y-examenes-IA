@echo off
chcp 65001 > nul
title 📱 Examinator - Iniciar en Red

echo.
echo ════════════════════════════════════════════════════════════════
echo    📱 EXAMINATOR - INICIO RÁPIDO PARA RED LOCAL
echo ════════════════════════════════════════════════════════════════
echo.

:: Obtener IP local
echo 🔍 Detectando tu IP...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :ip_found
)

:ip_found
set IP=%IP: =%
echo ✅ Tu IP es: %IP%
echo.

:: Guardar IP
echo %IP% > .ip_local.txt

echo ════════════════════════════════════════════════════════════════
echo    🚀 INICIANDO SERVIDORES
echo ════════════════════════════════════════════════════════════════
echo.

echo 🔄 Liberando puertos 5001, 8000 y 5173...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5001.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
timeout /t 1 /nobreak >nul
echo ✓ Puertos liberados
echo.

:: Iniciar Buscador IA
echo 🔍 Iniciando Buscador IA con GPU (puerto 5001)...
start "Buscador IA - GPU" cmd /k "title Buscador IA GPU && cd /d %~dp0 && echo 🔍 Servidor Buscador corriendo en puerto 5001... && venv\Scripts\activate.bat && python api_buscador.py"
timeout /t 3 >nul

:: Iniciar Backend
echo 🔥 Iniciando Backend API (puerto 8000)...
start "Examinator Backend" cmd /k "title Backend API && echo Backend corriendo en puerto 8000... && python api_server.py"
timeout /t 3 >nul

:: Iniciar Frontend
echo 🎨 Iniciando Frontend Web (puerto 5173)...
start "Examinator Frontend" cmd /k "title Frontend Web && echo Frontend corriendo... && cd examinator-web && npm run dev -- --host"
timeout /t 5 >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ SERVIDORES INICIADOS
echo ════════════════════════════════════════════════════════════════
echo.
echo 📱 DESDE TU MÓVIL/TABLET:
echo    Abre el navegador y ve a:
echo.
echo    🌐 http://%IP%:5173
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo 💻 DESDE ESTA PC:
echo    🌐 http://localhost:5173
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo ⚠️  IMPORTANTE:
echo    Si no puedes conectarte desde el móvil, ejecuta:
echo    configurar_firewall.bat (como Administrador)
echo.
echo ════════════════════════════════════════════════════════════════
echo.

:: Abrir navegador local
timeout /t 2 >nul
start http://localhost:5173

echo ✅ Todo listo! Presiona cualquier tecla para cerrar.
echo    (Los servidores seguirán corriendo en las otras ventanas)
echo.
pause >nul

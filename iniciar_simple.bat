@echo off
chcp 65001 > nul
title 📚 Examinator - Inicio Local

echo.
echo ════════════════════════════════════════════════════════════════
echo    📚 EXAMINATOR - INICIO LOCAL
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
echo 🔍 Iniciando Buscador IA (puerto 5001)...
start /min "Buscador IA" cmd /c "cd /d %~dp0 && venv\Scripts\activate.bat && python api_buscador.py"
timeout /t 2 >nul

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

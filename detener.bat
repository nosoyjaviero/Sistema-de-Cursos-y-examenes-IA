@echo off
chcp 65001 > nul
color 0C
cls

echo ================================================================================
echo                      🛑 EXAMINATOR - DETENER SERVIDORES
echo ================================================================================
echo.

echo [1/3] Deteniendo servidor Buscador IA (Puerto 5001)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5001.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
echo    ✓ Buscador detenido
echo.

echo [2/3] Deteniendo servidor Backend (Puerto 8000)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
echo    ✓ Backend detenido
echo.

echo [3/3] Deteniendo servidor Frontend (Puertos 5173/5174)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5174.*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
echo    ✓ Frontend detenido
echo.

echo ================================================================================
echo                          ✅ SERVIDORES DETENIDOS
echo ================================================================================
echo.
echo Presiona cualquier tecla para salir...
pause > nul

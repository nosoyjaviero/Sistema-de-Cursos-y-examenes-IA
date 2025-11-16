@echo off
chcp 65001 > nul
color 0C
cls

echo ================================================================================
echo                      🛑 EXAMINATOR - DETENER SERVIDORES
echo ================================================================================
echo.

echo [1/2] Deteniendo servidor Backend (Puerto 8000)...
powershell -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"
echo    ✓ Backend detenido
echo.

echo [2/2] Deteniendo servidor Frontend (Puerto 5173)...
powershell -Command "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"
echo    ✓ Frontend detenido
echo.

echo ================================================================================
echo                          ✅ SERVIDORES DETENIDOS
echo ================================================================================
echo.
echo Presiona cualquier tecla para salir...
pause > nul

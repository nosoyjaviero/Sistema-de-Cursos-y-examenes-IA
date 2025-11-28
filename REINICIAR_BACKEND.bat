@echo off
echo ============================================
echo    REINICIAR BACKEND CON NUEVOS CAMBIOS
echo ============================================
echo.
echo 1. Presiona Ctrl+C en la terminal del backend
echo 2. Ejecuta de nuevo: python api_server.py
echo.
echo ============================================
echo.
echo O ejecuta este comando en PowerShell:
echo.
echo Get-Process python ^| Where-Object {$_.CommandLine -like "*api_server*"} ^| Stop-Process -Force; Start-Sleep 2; python api_server.py
echo.
pause

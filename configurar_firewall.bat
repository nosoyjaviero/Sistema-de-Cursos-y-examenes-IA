@echo off
echo.
echo ==========================================
echo   CONFIGURAR FIREWALL PARA EXAMINATOR
echo ==========================================
echo.
echo Este script configurara el firewall de Windows
echo para permitir conexiones desde tu movil/tablet
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

echo.
echo Configurando firewall...
echo.

netsh advfirewall firewall add rule name="Examinator Backend" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="Examinator Frontend" dir=in action=allow protocol=TCP localport=5173
netsh advfirewall firewall add rule name="Examinator Frontend Alt" dir=in action=allow protocol=TCP localport=5174

echo.
echo ==========================================
echo   FIREWALL CONFIGURADO CORRECTAMENTE
echo ==========================================
echo.
echo Ahora puedes acceder desde tu movil a:
echo   http://192.168.0.3:5173
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul

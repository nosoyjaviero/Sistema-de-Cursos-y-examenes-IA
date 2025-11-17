@echo off
chcp 65001 > nul
color 0A
title 📱 Examinator - Acceso en Red Local

echo.
echo ════════════════════════════════════════════════════════════════
echo    📱 EXAMINATOR - CONFIGURACIÓN DE RED LOCAL
echo ════════════════════════════════════════════════════════════════
echo.

:: Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  NOTA: No se detectaron privilegios de administrador
    echo    Si hay problemas de firewall, ejecuta como Administrador
    echo.
    timeout /t 3 >nul
)

:: Obtener IP local
echo 🔍 Detectando dirección IP local...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :ip_found
)

:ip_found
set IP=%IP: =%
echo ✅ IP detectada: %IP%
echo.

:: Verificar puertos disponibles
echo 🔍 Verificando puertos...
netstat -an | findstr ":8000" >nul
if %errorLevel% equ 0 (
    echo ⚠️  Puerto 8000 en uso, liberando...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

netstat -an | findstr ":5173" >nul
if %errorLevel% equ 0 (
    echo ⚠️  Puerto 5173 en uso, liberando...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

netstat -an | findstr ":5174" >nul
if %errorLevel% equ 0 (
    echo ⚠️  Puerto 5174 en uso, liberando...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5174"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 >nul
)

echo ✅ Puertos disponibles
echo.

:: Configurar firewall (solo si es admin)
net session >nul 2>&1
if %errorLevel% equ 0 (
    echo 🔥 Configurando firewall...
    
    netsh advfirewall firewall show rule name="Examinator Backend" >nul 2>&1
    if %errorLevel% neq 0 (
        netsh advfirewall firewall add rule name="Examinator Backend" dir=in action=allow protocol=TCP localport=8000 >nul
        echo ✅ Regla de firewall creada para puerto 8000
    ) else (
        echo ✅ Regla de firewall ya existe para puerto 8000
    )
    
    netsh advfirewall firewall show rule name="Examinator Frontend" >nul 2>&1
    if %errorLevel% neq 0 (
        netsh advfirewall firewall add rule name="Examinator Frontend" dir=in action=allow protocol=TCP localport=5173 >nul
        netsh advfirewall firewall add rule name="Examinator Frontend Alt" dir=in action=allow protocol=TCP localport=5174 >nul
        echo ✅ Reglas de firewall creadas para puertos 5173/5174
    ) else (
        echo ✅ Reglas de firewall ya existen para frontend
    )
    echo.
) else (
    echo ℹ️  Firewall no configurado (requiere permisos de admin)
    echo    Si no puedes conectarte desde el móvil, ejecuta este .bat
    echo    como Administrador (click derecho → Ejecutar como administrador)
    echo.
)

:: Crear script temporal para iniciar frontend con host
echo 🔧 Preparando configuración...

:: Verificar que estamos en el directorio correcto
if not exist "examinator-web" (
    echo ❌ Error: No se encontró la carpeta examinator-web
    echo    Asegúrate de ejecutar este script desde la carpeta raíz del proyecto
    pause
    exit /b 1
)

cd examinator-web
if not exist package.json (
    echo ❌ Error: No se encontró package.json en examinator-web
    cd ..
    pause
    exit /b 1
)

:: Modificar package.json para agregar --host si no existe
findstr /C:"--host" package.json >nul
if %errorLevel% neq 0 (
    echo ✏️  Actualizando configuración de Vite...
    powershell -Command "(Get-Content package.json) -replace '\"dev\": \"vite\"', '\"dev\": \"vite --host\"' | Set-Content package.json"
)

cd ..

echo.
echo ════════════════════════════════════════════════════════════════
echo    🚀 INICIANDO SERVIDORES
echo ════════════════════════════════════════════════════════════════
echo.
echo ⏳ Iniciando Backend API (puerto 8000)...
start "Examinator Backend" cmd /k "echo 🔥 Backend API corriendo... && python api_server.py"
timeout /t 3 >nul

echo ⏳ Iniciando Frontend Web (puerto 5173/5174)...
cd examinator-web
start "Examinator Frontend" cmd /k "echo 🎨 Frontend corriendo... && npm run dev"
cd ..
timeout /t 5 >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ SERVIDORES INICIADOS
echo ════════════════════════════════════════════════════════════════
echo.
echo 📱 PARA ACCEDER DESDE TU MÓVIL/TABLET:
echo.
echo    1. Asegúrate de estar en la MISMA RED WIFI que tu PC
echo.
echo    2. Abre el navegador en tu dispositivo móvil
echo.
echo    3. Ve a una de estas direcciones:
echo.
echo       🌐 http://%IP%:5173
echo       🌐 http://%IP%:5174  (si el 5173 está ocupado)
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo 💻 En esta PC puedes acceder en:
echo    🌐 http://localhost:5173
echo    🌐 http://localhost:5174
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo 📝 NOTA: Los servidores seguirán corriendo en ventanas separadas.
echo         Cierra esas ventanas para detener los servidores.
echo.
echo ════════════════════════════════════════════════════════════════
echo.

:: Crear archivo con la IP para fácil acceso
echo %IP% > .ip_local.txt
echo 📄 IP guardada en: .ip_local.txt
echo.

:: Intentar abrir el navegador local
timeout /t 2 >nul
echo 🌐 Abriendo navegador local...
start http://localhost:5173
timeout /t 1 >nul
if %errorLevel% neq 0 (
    start http://localhost:5174
)

echo.
echo ✅ ¡Todo listo! Presiona cualquier tecla para cerrar esta ventana.
echo    (Los servidores seguirán corriendo en las otras ventanas)
echo.
pause >nul

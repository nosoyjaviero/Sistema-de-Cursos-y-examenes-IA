@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
title 🚀 Examinator - Backend Server

:: Ir al directorio del script
cd /d "%~dp0"

echo.
echo ════════════════════════════════════════════════════════════════
echo    🚀 SERVIDOR BACKEND - No cierres esta ventana
echo ════════════════════════════════════════════════════════════════
echo.

:: ============================================================================
:: BUSCAR PYTHON AUTOMÁTICAMENTE
:: ============================================================================

echo [1/3] 🔍 Buscando Python...

:: Opción 1: Usar el venv local si existe
if exist "venv\Scripts\python.exe" (
    set PYTHON_EXE=venv\Scripts\python.exe
    echo       ✅ Usando entorno virtual local
    goto :python_found
)

:: Opción 2: Buscar python en PATH
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('where python') do (
        set PYTHON_EXE=%%i
        echo       ✅ Usando Python del sistema: %%i
        goto :python_found
    )
)

:: Opción 3: Buscar en ubicaciones comunes
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%p (
        set PYTHON_EXE=%%~p
        echo       ✅ Python encontrado en: %%~p
        goto :python_found
    )
)

:: No se encontró Python
echo.
echo ════════════════════════════════════════════════════════════════
echo    ❌ ERROR: Python no encontrado
echo ════════════════════════════════════════════════════════════════
echo.
echo    Por favor instala Python desde: https://www.python.org/downloads/
echo    ⚠️ IMPORTANTE: Marca "Add Python to PATH" durante la instalación
echo.
pause
exit /b 1

:python_found

:: ============================================================================
:: VERIFICAR ENTORNO VIRTUAL
:: ============================================================================

echo [2/3] 📦 Verificando entorno virtual...

if not exist "venv\Scripts\activate.bat" (
    echo       ⚠️ Entorno virtual no encontrado. Creando...
    echo.
    python -m venv venv
    if %errorlevel% neq 0 (
        echo       ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
    echo       ✅ Entorno virtual creado
    
    :: Instalar dependencias básicas
    echo       📥 Instalando dependencias básicas...
    call venv\Scripts\activate.bat
    pip install fastapi uvicorn python-multipart -q
)

:: Usar el python del venv
set PYTHON_EXE=venv\Scripts\python.exe
echo       ✅ Entorno virtual listo

:: ============================================================================
:: INICIAR SERVIDOR
:: ============================================================================

echo [3/3] 🚀 Iniciando servidor en http://127.0.0.1:8000 ...
echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ SERVIDOR ACTIVO - Presiona Ctrl+C para detener
echo ════════════════════════════════════════════════════════════════
echo.

"%PYTHON_EXE%" -m uvicorn api_server:app --host 127.0.0.1 --port 8000 --log-level info

pause

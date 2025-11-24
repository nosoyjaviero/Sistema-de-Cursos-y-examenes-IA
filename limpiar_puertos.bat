@echo off
chcp 65001 > nul
title 🧹 Limpieza de Puertos - Examinator

echo.
echo ════════════════════════════════════════════════════════════════
echo    🧹 LIMPIADOR DE PUERTOS - EXAMINATOR
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script liberará todos los puertos utilizados por Examinator
echo.
echo Puertos que se liberarán:
echo   • 5001 - Buscador IA
echo   • 8000 - Backend API
echo   • 5173 - Frontend React (Vite)
echo   • 5174 - Frontend alternativo
echo.
pause

echo.
echo 🔍 Detectando procesos en puertos...
echo.

:: Puerto 5001 (Buscador)
echo [1/4] Limpiando puerto 5001 (Buscador IA)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5001.*LISTENING"') do (
    echo    ✓ Deteniendo proceso PID %%p
    taskkill /F /PID %%p >nul 2>&1
)

:: Puerto 8000 (Backend)
echo [2/4] Limpiando puerto 8000 (Backend)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo    ✓ Deteniendo proceso PID %%p
    taskkill /F /PID %%p >nul 2>&1
)

:: Puerto 5173 (Frontend)
echo [3/4] Limpiando puerto 5173 (Frontend)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5173.*LISTENING"') do (
    echo    ✓ Deteniendo proceso PID %%p
    taskkill /F /PID %%p >nul 2>&1
)

:: Puerto 5174 (Frontend alternativo)
echo [4/4] Limpiando puerto 5174 (Frontend alt)...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5174.*LISTENING"') do (
    echo    ✓ Deteniendo proceso PID %%p
    taskkill /F /PID %%p >nul 2>&1
)

timeout /t 1 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ PUERTOS LIBERADOS
echo ════════════════════════════════════════════════════════════════
echo.
echo Verificación final:
netstat -ano | findstr ":5001 :8000 :5173 :5174" | findstr "LISTENING"
if %errorLevel% equ 0 (
    echo ⚠️  Algunos puertos aún están en uso
) else (
    echo ✅ Todos los puertos están libres
)
echo.
pause

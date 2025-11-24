@echo off
chcp 65001 > nul
title 🔄 Reindexar Buscador IA

echo.
echo ════════════════════════════════════════════════════════════════
echo    🔄 REINDEXACIÓN COMPLETA DEL BUSCADOR IA
echo ════════════════════════════════════════════════════════════════
echo.
echo Este script eliminará los índices actuales y creará nuevos
echo indexando SOLO la carpeta: extracciones\
echo.

cd /d "%~dp0"

echo 🗑️  Eliminando índices antiguos...
if exist "indice_busqueda" (
    rmdir /s /q "indice_busqueda"
    echo    ✓ Índices eliminados
) else (
    echo    ℹ️  No había índices previos
)
echo.

echo 🔍 Iniciando servidor del buscador...
echo.
echo ⚠️  IMPORTANTE: Cuando veas "Servidor corriendo en http://localhost:5001"
echo    ve al frontend y haz clic en "♻️ Reindexar Todo"
echo.
echo Presiona CTRL+C para detener el servidor cuando termine la indexación
echo.
pause

venv\Scripts\activate.bat && python api_buscador.py

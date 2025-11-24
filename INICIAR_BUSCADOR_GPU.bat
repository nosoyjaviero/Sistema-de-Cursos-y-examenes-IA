@echo off
title Servidor Buscador IA - GPU
color 0A

echo ========================================
echo  SERVIDOR DE BUSQUEDA IA CON GPU
echo ========================================
echo.

cd /d "C:\Users\Fela\Documents\Proyectos\Examinator"
call venv\Scripts\activate.bat

echo Iniciando servidor...
echo Mantén esta ventana abierta
echo Presiona CTRL+C para detener
echo.

python api_buscador.py

pause

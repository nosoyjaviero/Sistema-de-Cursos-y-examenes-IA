@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
echo.
echo ===============================================
echo  Iniciando Examinator API Server
echo  (4 workers para mejor estabilidad)
echo ===============================================
echo.

cd /d "C:\Users\Fela\Documents\Proyectos\Examinator"
"C:\Users\Fela\Documents\Proyectos\Examinator\venv\Scripts\python.exe" -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4

pause

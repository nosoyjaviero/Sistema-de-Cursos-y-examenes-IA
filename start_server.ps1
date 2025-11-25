# Script para iniciar el servidor FastAPI de forma permanente
$env:PYTHONIOENCODING='utf-8'

Write-Host "=== Iniciando Examinator API Server ===" -ForegroundColor Green
Write-Host "Puerto: 8000"
Write-Host "Codificación: UTF-8"
Write-Host ""

# Iniciar el servidor
& "C:\Users\Fela\Documents\Proyectos\Examinator\venv\Scripts\python.exe" -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --log-level info

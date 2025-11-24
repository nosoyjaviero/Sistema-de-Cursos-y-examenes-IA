# Script para mantener el servidor corriendo
$env:FLASK_ENV = "development"

Write-Host "🚀 Iniciando servidor de búsqueda IA con GPU..." -ForegroundColor Green
Write-Host "Presiona CTRL+C para detener`n" -ForegroundColor Yellow

& "C:\Users\Fela\Documents\Proyectos\Examinator\venv\Scripts\python.exe" api_buscador.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ El servidor se cerró con error código: $LASTEXITCODE" -ForegroundColor Red
    Pause
}

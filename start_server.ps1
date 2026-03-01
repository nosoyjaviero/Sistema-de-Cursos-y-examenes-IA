# Script para iniciar el servidor FastAPI de forma permanente
$env:PYTHONIOENCODING='utf-8'

# Obtener el directorio del script
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
Set-Location $scriptDir

Write-Host "=== Iniciando Examinator API Server ===" -ForegroundColor Green
Write-Host "Puerto: 8000"
Write-Host "Codificación: UTF-8"
Write-Host "Directorio: $scriptDir"
Write-Host ""

# Buscar Python dinámicamente
$pythonExe = "$scriptDir\venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    # Intentar con python del sistema
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonExe) {
        Write-Host "❌ Python no encontrado. Instala Python o crea el entorno virtual." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Usando Python: $pythonExe" -ForegroundColor Cyan

# Iniciar el servidor
& $pythonExe -m uvicorn api_server:app --host 127.0.0.1 --port 8000 --log-level info

# Script para mantener el servidor corriendo
$env:FLASK_ENV = "development"

# Obtener el directorio del script
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
Set-Location $scriptDir

Write-Host "🚀 Iniciando servidor de búsqueda IA con GPU..." -ForegroundColor Green
Write-Host "Directorio: $scriptDir" -ForegroundColor Cyan
Write-Host "Presiona CTRL+C para detener`n" -ForegroundColor Yellow

# Buscar Python dinámicamente
$pythonExe = "$scriptDir\venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pythonExe) {
        Write-Host "❌ Python no encontrado." -ForegroundColor Red
        exit 1
    }
}

& $pythonExe api_buscador.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ El servidor se cerró con error código: $LASTEXITCODE" -ForegroundColor Red
    Pause
}

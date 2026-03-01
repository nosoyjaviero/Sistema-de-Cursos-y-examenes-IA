#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando servidor Vite de desarrollo..." -ForegroundColor Cyan
Write-Host "Este es NECESARIO para que los cambios en src/App.jsx se actualicen en el navegador" -ForegroundColor Yellow

# Obtener el directorio del script y navegar al frontend
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
$frontendDir = Join-Path $scriptDir "examinator-web"

Set-Location $frontendDir
Write-Host "Directorio: $frontendDir" -ForegroundColor Gray

# Verificar si node_modules existe
if (!(Test-Path 'node_modules')) {
    Write-Host "📦 node_modules no existe, instalando dependencias..." -ForegroundColor Yellow
    npm install
}

# Iniciar servidor dev
Write-Host "`n✅ Ejecutando: npm run dev" -ForegroundColor Green
Write-Host "El servidor estará disponible en: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener el servidor`n" -ForegroundColor Yellow

npm run dev

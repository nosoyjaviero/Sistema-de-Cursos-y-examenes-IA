# Script para iniciar Examinator (Backend + Frontend)

Write-Host "🚀 Iniciando Examinator..." -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual de Python
Write-Host "📦 Activando entorno virtual de Python..." -ForegroundColor Yellow
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

# Iniciar servidor API en segundo plano
Write-Host "🔧 Iniciando servidor API (Backend)..." -ForegroundColor Yellow
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    & "$using:PSScriptRoot\venv\Scripts\python.exe" api_server.py
}

Start-Sleep -Seconds 2

# Iniciar servidor React
Write-Host "⚛️  Iniciando servidor React (Frontend)..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\examinator-web"
$reactJob = Start-Job -ScriptBlock {
    Set-Location "$using:PSScriptRoot\examinator-web"
    npm run dev
}

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ Servidores iniciados:" -ForegroundColor Green
Write-Host "   • API Backend: http://localhost:8000" -ForegroundColor White
Write-Host "   • Frontend: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "📝 Presiona Ctrl+C para detener ambos servidores" -ForegroundColor Yellow
Write-Host ""

# Mantener el script corriendo y mostrar logs
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "🛑 Deteniendo servidores..." -ForegroundColor Red
    Stop-Job -Job $apiJob
    Stop-Job -Job $reactJob
    Remove-Job -Job $apiJob
    Remove-Job -Job $reactJob
}

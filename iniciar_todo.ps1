#!/usr/bin/env pwsh
# Script para iniciar Ollama y el servidor API juntos

Write-Host "`n🚀 Iniciando Examinator completo..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# 1. Verificar si Ollama está corriendo
Write-Host "`n1️⃣ Verificando Ollama..." -ForegroundColor Yellow
try {
    $ollamaStatus = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ Ollama ya está corriendo" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Ollama no está corriendo. Iniciándolo..." -ForegroundColor Yellow
    
    # Intentar iniciar Ollama
    try {
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Write-Host "   ⏳ Esperando a que Ollama inicie..." -ForegroundColor Cyan
        Start-Sleep -Seconds 5
        
        # Verificar que inició correctamente
        $ollamaStatus = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host "   ✅ Ollama iniciado correctamente" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Error al iniciar Ollama" -ForegroundColor Red
        Write-Host "   💡 Solución: Abre una terminal y ejecuta: ollama serve" -ForegroundColor Yellow
        Write-Host "`n   Presiona cualquier tecla para continuar de todos modos..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# 2. Detener servidor API anterior si existe
Write-Host "`n2️⃣ Verificando servidor API..." -ForegroundColor Yellow
$processId = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess | Select-Object -First 1
if ($processId) {
    Write-Host "   ⏹️ Deteniendo servidor anterior (PID: $processId)..." -ForegroundColor Red
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Servidor anterior detenido" -ForegroundColor Green
} else {
    Write-Host "   ✅ Puerto 8000 disponible" -ForegroundColor Green
}

# 3. Iniciar servidor API
Write-Host "`n3️⃣ Iniciando servidor API..." -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "`n📍 URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`n💡 Presiona Ctrl+C para detener ambos servicios`n" -ForegroundColor Yellow

# Ejecutar el servidor
python api_server.py

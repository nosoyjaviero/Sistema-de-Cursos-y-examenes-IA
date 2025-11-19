#!/usr/bin/env pwsh
# Script para reiniciar el servidor API de Examinator

Write-Host "`n🔄 Reiniciando servidor API de Examinator..." -ForegroundColor Cyan

# Función para encontrar el PID que usa el puerto 8000
function Get-PortProcess {
    param([int]$Port = 8000)
    
    $netstatOutput = netstat -ano | Select-String ":$Port\s" | Select-String "LISTENING"
    if ($netstatOutput) {
        foreach ($line in $netstatOutput) {
            if ($line -match '\s+(\d+)$') {
                return [int]$matches[1]
            }
        }
    }
    return $null
}

# Buscar proceso usando el puerto 8000
Write-Host "🔍 Verificando puerto 8000..." -ForegroundColor Yellow
$processId = Get-PortProcess -Port 8000

if ($processId) {
    Write-Host "⏹️  Encontrado proceso en puerto 8000 (PID: $processId)" -ForegroundColor Red
    Write-Host "   Deteniendo proceso..." -ForegroundColor Yellow
    
    try {
        Stop-Process -Id $processId -Force -ErrorAction Stop
        Write-Host "✅ Proceso detenido exitosamente" -ForegroundColor Green
        Start-Sleep -Seconds 3
    } catch {
        Write-Host "❌ Error deteniendo proceso: $_" -ForegroundColor Red
        Write-Host "💡 Intenta cerrar manualmente la terminal del servidor" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ Puerto 8000 disponible" -ForegroundColor Green
}

# Verificar nuevamente que el puerto esté libre
Start-Sleep -Seconds 1
$pidCheck = Get-PortProcess -Port 8000
if ($pidCheck) {
    Write-Host "⚠️  El puerto 8000 todavía está en uso" -ForegroundColor Red
    Write-Host "   Espera unos segundos e intenta de nuevo" -ForegroundColor Yellow
    exit 1
}

# Iniciar el servidor
Write-Host "`n🚀 Iniciando servidor API..." -ForegroundColor Green
Write-Host "📍 URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`n💡 Presiona Ctrl+C para detener el servidor`n" -ForegroundColor Yellow

# Ejecutar el servidor
python api_server.py

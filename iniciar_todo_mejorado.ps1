# Script mejorado para iniciar todo el sistema Examinator automáticamente
Write-Host "🚀 INICIANDO SISTEMA EXAMINATOR" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar si Ollama está corriendo
Write-Host "🔍 Verificando Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "✅ Ollama ya está corriendo" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Ollama no está corriendo, iniciando..." -ForegroundColor Yellow
    
    # Iniciar Ollama en segundo plano
    try {
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Write-Host "🔄 Esperando a que Ollama inicie..." -ForegroundColor Cyan
        
        # Esperar hasta 15 segundos
        $intentos = 0
        $max_intentos = 15
        $ollama_ok = $false
        
        while ($intentos -lt $max_intentos -and -not $ollama_ok) {
            Start-Sleep -Seconds 1
            $intentos++
            try {
                $test = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
                $ollama_ok = $true
                Write-Host "✅ Ollama iniciado correctamente en $intentos segundos" -ForegroundColor Green
            } catch {
                Write-Host "." -NoNewline -ForegroundColor Gray
            }
        }
        
        if (-not $ollama_ok) {
            Write-Host ""
            Write-Host "⚠️ Ollama no pudo iniciarse automáticamente" -ForegroundColor Yellow
            Write-Host "💡 El sistema usará modelos GGUF locales si están disponibles" -ForegroundColor Cyan
            Write-Host "💡 Para usar Ollama, ejecútalo manualmente: ollama serve" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "❌ Error al iniciar Ollama: $_" -ForegroundColor Red
        Write-Host "💡 Asegúrate de que Ollama esté instalado desde https://ollama.ai" -ForegroundColor Cyan
    }
}

Write-Host ""

# 2. Detener servidor API anterior si existe
Write-Host "🔍 Verificando servidor API..." -ForegroundColor Yellow
$apiProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | Where-Object { $_ -ne 0 }
if ($apiProcess) {
    try {
        Stop-Process -Id $apiProcess -Force -ErrorAction Stop
        Write-Host "✅ Servidor API anterior detenido" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } catch {
        Write-Host "⚠️ No se pudo detener servidor anterior" -ForegroundColor Yellow
    }
} else {
    Write-Host "ℹ️ No hay servidor API anterior corriendo" -ForegroundColor Gray
}

Write-Host ""

# 3. Iniciar servidor API
Write-Host "🚀 Iniciando servidor API..." -ForegroundColor Cyan
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✨ Sistema listo!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 Servidor API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🤖 Ollama: http://localhost:11434" -ForegroundColor Cyan
Write-Host "📱 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 El servidor iniciará en unos segundos..." -ForegroundColor Yellow
Write-Host "💡 Presiona Ctrl+C en esta terminal para detener todo" -ForegroundColor Yellow
Write-Host ""

# Ejecutar servidor API
python api_server.py

# Script para iniciar el generador de exámenes con Ollama
Write-Host "🚀 Iniciando sistema con Ollama (GPU automática)" -ForegroundColor Green
Write-Host ""

# Verificar que Ollama esté instalado
$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
if (-not (Test-Path $ollamaPath)) {
    Write-Host "❌ Ollama no está instalado" -ForegroundColor Red
    Write-Host "📥 Descargar desde: https://ollama.com/download" -ForegroundColor Yellow
    exit 1
}

# Verificar que el modelo esté descargado
Write-Host "🔍 Verificando modelo..." -ForegroundColor Cyan
$modelos = & $ollamaPath list 2>&1
if ($modelos -match "llama3.2:3b") {
    Write-Host "✅ Modelo llama3.2:3b encontrado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Modelo llama3.2:3b no encontrado" -ForegroundColor Yellow
    Write-Host "📥 Descargando modelo..." -ForegroundColor Cyan
    & $ollamaPath pull llama3.2:3b
}

Write-Host ""
Write-Host "🎯 Opciones:" -ForegroundColor Cyan
Write-Host "  1. Usar generador_examenes_ollama.py" -ForegroundColor White
Write-Host "  2. Iniciar servidor web (api_server.py)" -ForegroundColor White
Write-Host ""

$opcion = Read-Host "Selecciona una opción (1-2)"

switch ($opcion) {
    "1" {
        Write-Host "🧪 Ejecutando test..." -ForegroundColor Green
        python generador_examenes_ollama.py
    }
    "2" {
        Write-Host "🌐 Iniciando servidor web..." -ForegroundColor Green
        Write-Host "💡 Nota: Necesitas modificar api_server.py para usar Ollama" -ForegroundColor Yellow
        python api_server.py
    }
    default {
        Write-Host "❌ Opción inválida" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✨ Proceso finalizado" -ForegroundColor Green

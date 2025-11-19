# Script para descargar modelo GGUF pequeño y rápido para chat
Write-Host "🤖 Descargando modelo Qwen2.5-3B (Q4_K_M - 2.4 GB)" -ForegroundColor Cyan
Write-Host "Este modelo es pequeño, rápido y funciona bien para chat" -ForegroundColor Yellow

$url = "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
$destino = ".\modelos\qwen2.5-3b-instruct-q4_k_m.gguf"

# Crear carpeta si no existe
if (-not (Test-Path ".\modelos")) {
    New-Item -ItemType Directory -Path ".\modelos" | Out-Null
}

Write-Host "📥 Descargando de HuggingFace..." -ForegroundColor Green
Write-Host "Destino: $destino" -ForegroundColor Gray

try {
    # Usar Invoke-WebRequest con barra de progreso
    $ProgressPreference = 'Continue'
    Invoke-WebRequest -Uri $url -OutFile $destino -UseBasicParsing
    
    Write-Host "`n✅ Modelo descargado exitosamente!" -ForegroundColor Green
    Write-Host "📁 Ubicación: $destino" -ForegroundColor Cyan
    Write-Host "`n🎯 Ahora ve a Configuración en la app y selecciona este modelo" -ForegroundColor Yellow
    
} catch {
    Write-Host "`n❌ Error descargando: $_" -ForegroundColor Red
    Write-Host "💡 Intenta descargarlo manualmente desde:" -ForegroundColor Yellow
    Write-Host $url -ForegroundColor Cyan
}

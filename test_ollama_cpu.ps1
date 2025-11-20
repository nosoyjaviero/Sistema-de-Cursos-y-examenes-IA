# Script para verificar y testear Ollama CPU
Write-Host "`n===========================================`n" -ForegroundColor Cyan
Write-Host "🔍 VERIFICACIÓN DE OLLAMA CPU" -ForegroundColor Yellow
Write-Host "`n===========================================`n" -ForegroundColor Cyan

# 1. Verificar modelos Ollama disponibles
Write-Host "`n📦 Modelos Ollama disponibles:" -ForegroundColor Green
ollama list

# 2. Verificar config.json
Write-Host "`n📄 Configuración actual (config.json):" -ForegroundColor Green
Get-Content config.json | ConvertFrom-Json | Select-Object usar_ollama, modelo_ollama_activo, @{N='n_gpu_layers';E={$_.ajustes_avanzados.n_gpu_layers}} | Format-List

# 3. Instrucciones
Write-Host "`n===========================================`n" -ForegroundColor Cyan
Write-Host "✅ PARA PROBAR:" -ForegroundColor Yellow
Write-Host "   1. Reinicia el servidor backend" -ForegroundColor White
Write-Host "   2. Abre la app web" -ForegroundColor White
Write-Host "   3. Abre la consola (F12)" -ForegroundColor White
Write-Host "   4. Ve a Configuración" -ForegroundColor White
Write-Host "   5. Haz clic en '🔷 Ollama CPU'" -ForegroundColor White
Write-Host "`n📊 LOGS ESPERADOS EN CONSOLA:" -ForegroundColor Yellow
Write-Host "   ✓ usar_ollama: true" -ForegroundColor White
Write-Host "   ✓ gpu_activa: false" -ForegroundColor White
Write-Host "   ✓ Evaluación Ollama CPU: true" -ForegroundColor White
Write-Host "`n===========================================`n" -ForegroundColor Cyan

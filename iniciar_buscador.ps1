# Script de inicio rápido del Buscador IA

Write-Host "🔍 BUSCADOR IA - INICIO RÁPIDO" -ForegroundColor Cyan
Write-Host "=" * 60

# Verificar si existe el índice
$rutaIndice = "C:\Users\Fela\Documents\Proyectos\Examinator\indice_busqueda\vectores.index"

if (-not (Test-Path $rutaIndice)) {
    Write-Host "⚠️  No se encontró índice existente" -ForegroundColor Yellow
    Write-Host "📦 Debes crear el índice primero:" -ForegroundColor Yellow
    Write-Host "   python crear_indice_inicial.py" -ForegroundColor White
    Write-Host ""
    
    $crear = Read-Host "¿Crear índice ahora? (s/n)"
    if ($crear -eq 's' -or $crear -eq 'S') {
        Write-Host "🚀 Creando índice..." -ForegroundColor Green
        python crear_indice_inicial.py
    } else {
        Write-Host "❌ Cancelado" -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "✅ Índice encontrado" -ForegroundColor Green
Write-Host "🚀 Iniciando servidor de búsqueda..." -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 El servidor estará en: http://localhost:5001" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏹️  Para detener: CTRL+C" -ForegroundColor Gray
Write-Host ""

# Iniciar servidor
python api_buscador.py

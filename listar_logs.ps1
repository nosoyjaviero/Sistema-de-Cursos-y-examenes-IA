# Script para listar todos los logs de prácticas

param(
    [int]$Ultimos = 10
)

Write-Host "📋 LOGS DE PRÁCTICAS GENERADAS" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Gray
Write-Host ""

$logDir = "logs_practicas_detallado"

if (!(Test-Path $logDir)) {
    Write-Host "❌ No existe el directorio de logs: $logDir" -ForegroundColor Red
    exit
}

$logs = Get-ChildItem "$logDir\*.log" | Sort-Object LastWriteTime -Descending

if ($logs.Count -eq 0) {
    Write-Host "❌ No hay logs disponibles" -ForegroundColor Red
    Write-Host "💡 Genera una práctica primero" -ForegroundColor Yellow
    exit
}

Write-Host "Total de logs: $($logs.Count)" -ForegroundColor Yellow
Write-Host "Mostrando últimos: $Ultimos" -ForegroundColor Gray
Write-Host ""

$logs | Select-Object -First $Ultimos | ForEach-Object {
    $nombre = $_.Name
    $fecha = $_.LastWriteTime
    $tamanio = [math]::Round($_.Length / 1KB, 2)
    
    # Leer primera línea de errores si existe
    $contenido = Get-Content $_.FullName -Raw -Encoding UTF8
    $tieneErrores = $contenido -match "8\. ERRORES ENCONTRADOS"
    $emoji = if ($tieneErrores) { "❌" } else { "✅" }
    
    # Contar preguntas en resultado final
    $numPreguntas = 0
    if ($contenido -match "Total preguntas: (\d+)") {
        $numPreguntas = [int]$Matches[1]
    }
    
    Write-Host "$emoji $nombre" -ForegroundColor $(if ($tieneErrores) { "Red" } else { "Green" })
    Write-Host "   📅 $fecha | 📦 $tamanio KB | 📝 $numPreguntas preguntas" -ForegroundColor Gray
    
    if ($tieneErrores) {
        # Extraer errores
        if ($contenido -match "8\. ERRORES ENCONTRADOS\r?\n-+\r?\n(.+?)\r?\n\r?\n=+") {
            $errores = $Matches[1] -split "\r?\n" | Where-Object { $_ -match "^•" }
            foreach ($error in $errores | Select-Object -First 2) {
                Write-Host "      $error" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
}

Write-Host "="*80 -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Para ver un log específico: Get-Content logs_practicas_detallado\<nombre>.log" -ForegroundColor Cyan
Write-Host "💡 Para ver el último log: .\ver_ultimo_log.ps1" -ForegroundColor Cyan
Write-Host "💡 Para cambiar cantidad mostrada: .\listar_logs.ps1 -Ultimos 20" -ForegroundColor Cyan

# Script rápido para verificar si la última práctica funcionó o falló

$logDir = "logs_practicas_detallado"

if (!(Test-Path $logDir)) {
    Write-Host "❌ No hay logs" -ForegroundColor Red
    exit
}

$ultimoLog = Get-ChildItem "$logDir\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (!$ultimoLog) {
    Write-Host "❌ No hay logs disponibles" -ForegroundColor Red
    exit
}

$contenido = Get-Content $ultimoLog.FullName -Raw -Encoding UTF8

Write-Host ""
Write-Host "📄 $($ultimoLog.Name)" -ForegroundColor Cyan
Write-Host "🕐 $($ultimoLog.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
Write-Host ""

# Extraer estado
if ($contenido -match "Estado: (.*?)\r?\n") {
    $estado = $Matches[1].Trim()
    
    if ($estado -match "✅") {
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
        Write-Host "  $estado  " -ForegroundColor Green
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    } else {
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
        Write-Host "  $estado  " -ForegroundColor Red
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
    }
}

# Extraer resumen
if ($contenido -match "Preguntas solicitadas: (\d+)") {
    $solicitadas = $Matches[1]
    Write-Host "📝 Solicitadas: $solicitadas" -ForegroundColor Cyan
}

if ($contenido -match "Preguntas generadas: (\d+)") {
    $generadas = $Matches[1]
    
    if ($generadas -eq $solicitadas) {
        Write-Host "✅ Generadas: $generadas" -ForegroundColor Green
    } elseif ($generadas -gt 0) {
        Write-Host "⚠️  Generadas: $generadas (menos de las solicitadas)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Generadas: $generadas" -ForegroundColor Red
    }
}

# Mostrar errores si existen
if ($contenido -match "⚠️ ERRORES ENCONTRADOS \((\d+)\)") {
    $numErrores = $Matches[1]
    Write-Host ""
    Write-Host "❌ Errores: $numErrores" -ForegroundColor Red
    
    # Extraer primeros 3 errores
    if ($contenido -match "⚠️ ERRORES ENCONTRADOS.*?\r?\n(.+?)\r?\n\r?\n") {
        $erroresTexto = $Matches[1]
        $lineasError = $erroresTexto -split "\r?\n" | Select-Object -First 3
        foreach ($error in $lineasError) {
            if ($error.Trim()) {
                Write-Host "   $error" -ForegroundColor Yellow
            }
        }
    }
}

# Mostrar info de filtrado
if ($contenido -match "Por tipo: (\{.*?\})") {
    Write-Host ""
    Write-Host "🔍 Filtrado por tipo:" -ForegroundColor Cyan
    Write-Host "   $($Matches[1])" -ForegroundColor Gray
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Ver detalles: .\ver_ultimo_log.ps1" -ForegroundColor Cyan
Write-Host "💡 Ver completo: .\ver_ultimo_log.ps1 -Completo" -ForegroundColor Cyan
Write-Host ""

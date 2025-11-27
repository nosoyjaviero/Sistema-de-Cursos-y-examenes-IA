# 🔍 Diagnóstico de Flashcards Activas
# Este script muestra qué flashcards deberían aparecer HOY para repaso

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "🔍 DIAGNÓSTICO DE FLASHCARDS ACTIVAS" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Cargar flashcards
$rutaFlashcards = "C:\Users\Fela\Documents\Proyectos\Examinator\extracciones\Platzi\flashcards.json"

if (-not (Test-Path $rutaFlashcards)) {
    Write-Host "❌ No se encontró el archivo: $rutaFlashcards" -ForegroundColor Red
    exit 1
}

$flashcards = Get-Content $rutaFlashcards | ConvertFrom-Json

# Fecha actual (inicio del día)
$ahora = Get-Date
$hoyInicio = Get-Date -Year $ahora.Year -Month $ahora.Month -Day $ahora.Day -Hour 0 -Minute 0 -Second 0

Write-Host "📅 Fecha actual: $($ahora.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Yellow
Write-Host "🕐 Inicio del día: $($hoyInicio.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Yellow
Write-Host ""

Write-Host "📊 TOTAL DE FLASHCARDS: $($flashcards.Count)" -ForegroundColor Green
Write-Host ""

# Filtrar flashcards que deberían aparecer HOY
$flashcardsParaHoy = @()

foreach ($flashcard in $flashcards) {
    $titulo = $flashcard.titulo
    $revisionesHoy = if ($flashcard.revisionesHoy) { $flashcard.revisionesHoy } else { 0 }
    $proximaRevision = $flashcard.proximaRevision
    $ultimaRevision = if ($flashcard.ultima_revision) { $flashcard.ultima_revision } else { $null }
    
    # Regla 1: Bloquear si tiene 2+ revisiones hoy
    if ($revisionesHoy -ge 2) {
        Write-Host "🚫 BLOQUEADA (límite diario): $titulo" -ForegroundColor Red
        Write-Host "   revisionesHoy: $revisionesHoy" -ForegroundColor DarkGray
        continue
    }
    
    # Regla 2: Verificar si fue revisada HOY
    if ($ultimaRevision) {
        $fechaUltima = [datetime]::Parse($ultimaRevision)
        $diaUltima = Get-Date -Year $fechaUltima.Year -Month $fechaUltima.Month -Day $fechaUltima.Day -Hour 0 -Minute 0 -Second 0
        
        if ($diaUltima.Ticks -eq $hoyInicio.Ticks) {
            if ($revisionesHoy -ge 2) {
                Write-Host "🚫 BLOQUEADA (revisada hoy 2+ veces): $titulo" -ForegroundColor Red
                Write-Host "   última revisión: $($fechaUltima.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray
                Write-Host "   revisionesHoy: $revisionesHoy" -ForegroundColor DarkGray
                continue
            } elseif ($revisionesHoy -eq 1) {
                Write-Host "⚠️  ÚLTIMA OPORTUNIDAD (1/2): $titulo" -ForegroundColor Yellow
                Write-Host "   última revisión: $($fechaUltima.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray
            }
        }
    }
    
    # Regla 3: Si no tiene proximaRevision, es nuevo
    if (-not $proximaRevision) {
        if (-not $ultimaRevision) {
            Write-Host "✅ ACTIVA (nueva, nunca revisada): $titulo" -ForegroundColor Green
            $flashcardsParaHoy += $flashcard
        } elseif ($fechaUltima -lt $hoyInicio) {
            Write-Host "✅ ACTIVA (revisada antes, no hoy): $titulo" -ForegroundColor Green
            $flashcardsParaHoy += $flashcard
        }
        continue
    }
    
    # Regla 4: Verificar si la fecha de revisión llegó
    $fechaRevision = [datetime]::Parse($proximaRevision)
    $diaRevision = Get-Date -Year $fechaRevision.Year -Month $fechaRevision.Month -Day $fechaRevision.Day -Hour 0 -Minute 0 -Second 0
    
    if ($diaRevision.Ticks -le $hoyInicio.Ticks) {
        # Fecha llegó o pasó
        if ($revisionesHoy -lt 2) {
            Write-Host "✅ ACTIVA (fecha llegada, $revisionesHoy/2): $titulo" -ForegroundColor Green
            Write-Host "   próxima revisión: $($fechaRevision.ToString('yyyy-MM-dd'))" -ForegroundColor DarkGray
            Write-Host "   revisionesHoy: $revisionesHoy" -ForegroundColor DarkGray
            $flashcardsParaHoy += $flashcard
        } else {
            Write-Host "🚫 BLOQUEADA (límite alcanzado): $titulo" -ForegroundColor Red
            Write-Host "   próxima revisión: $($fechaRevision.ToString('yyyy-MM-dd'))" -ForegroundColor DarkGray
            Write-Host "   revisionesHoy: $revisionesHoy" -ForegroundColor DarkGray
        }
    } else {
        # Fecha no llegó
        $diasFaltantes = [math]::Round(($diaRevision.Ticks - $hoyInicio.Ticks) / [timespan]::TicksPerDay)
        Write-Host "⏭️  PENDIENTE (faltan $diasFaltantes días): $titulo" -ForegroundColor DarkGray
        Write-Host "   próxima revisión: $($fechaRevision.ToString('yyyy-MM-dd'))" -ForegroundColor DarkGray
        Write-Host "   hoy: $($hoyInicio.ToString('yyyy-MM-dd'))" -ForegroundColor DarkGray
    }
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "📊 RESUMEN" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Total flashcards: $($flashcards.Count)" -ForegroundColor White
Write-Host "✅ Activas para HOY: $($flashcardsParaHoy.Count)" -ForegroundColor Green
Write-Host ""

if ($flashcardsParaHoy.Count -eq 0) {
    Write-Host "🎉 ¡No hay flashcards pendientes para hoy!" -ForegroundColor Green
    Write-Host "   Todas están programadas para fechas futuras o bloqueadas por límite diario." -ForegroundColor Gray
} else {
    Write-Host "📋 Flashcards que deberían aparecer:" -ForegroundColor Yellow
    foreach ($fc in $flashcardsParaHoy) {
        Write-Host "   - $($fc.titulo)" -ForegroundColor White
    }
}

Write-Host ""

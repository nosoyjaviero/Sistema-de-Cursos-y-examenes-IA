# Script para ver el último log generado

param(
    [switch]$Completo,
    [switch]$SoloResumen
)

Write-Host "📋 ÚLTIMO LOG DE PRÁCTICA GENERADA" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Gray

$logDir = "logs_practicas_detallado"

if (!(Test-Path $logDir)) {
    Write-Host "❌ No existe el directorio de logs: $logDir" -ForegroundColor Red
    exit
}

$ultimoLog = Get-ChildItem "$logDir\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (!$ultimoLog) {
    Write-Host "❌ No hay logs disponibles" -ForegroundColor Red
    Write-Host "💡 Genera una práctica primero" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "📄 Archivo: $($ultimoLog.Name)" -ForegroundColor Green
Write-Host "🕐 Fecha: $($ultimoLog.LastWriteTime)" -ForegroundColor Gray
Write-Host ""

$contenido = Get-Content $ultimoLog.FullName -Raw -Encoding UTF8

# Extraer resumen ejecutivo
if ($contenido -match "🎯 RESUMEN EJECUTIVO\r?\n-+(.+?)\r?\n=+") {
    $resumen = $Matches[1].Trim()
    
    Write-Host "="*70 -ForegroundColor Gray
    Write-Host "🎯 RESUMEN EJECUTIVO" -ForegroundColor Cyan
    Write-Host "-"*70 -ForegroundColor Gray
    
    # Colorear según estado
    $lineas = $resumen -split "\r?\n"
    foreach ($linea in $lineas) {
        if ($linea -match "Estado: ✅") {
            Write-Host $linea -ForegroundColor Green
        } elseif ($linea -match "Estado: ❌") {
            Write-Host $linea -ForegroundColor Red
        } elseif ($linea -match "⚠️|ERRORES") {
            Write-Host $linea -ForegroundColor Yellow
        } elseif ($linea -match "✅") {
            Write-Host $linea -ForegroundColor Green
        } else {
            Write-Host $linea
        }
    }
    Write-Host "="*70 -ForegroundColor Gray
}

# Mostrar log completo si se pide
if ($Completo -or !$SoloResumen) {
    if (!$SoloResumen) {
        Write-Host ""
        Write-Host "💡 Mostrando solo resumen. Para ver log completo: .\ver_ultimo_log.ps1 -Completo" -ForegroundColor Cyan
        Write-Host ""
    }
}

if ($Completo) {
    Write-Host ""
    Write-Host "="*70 -ForegroundColor Gray
    Write-Host "📄 LOG COMPLETO" -ForegroundColor Yellow
    Write-Host "="*70 -ForegroundColor Gray
    Write-Host ""
    
    # Mostrar contenido completo
    Get-Content $ultimoLog.FullName -Encoding UTF8
    
    Write-Host ""
    Write-Host "="*70 -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 Opciones:" -ForegroundColor Cyan
Write-Host "   .\ver_ultimo_log.ps1              → Solo resumen" -ForegroundColor Gray
Write-Host "   .\ver_ultimo_log.ps1 -Completo    → Log completo" -ForegroundColor Gray
Write-Host "   .\ver_ultimo_log.ps1 -SoloResumen → Solo resumen (explícito)" -ForegroundColor Gray
Write-Host ""
Write-Host "📁 Archivo JSON: $($ultimoLog.BaseName).json" -ForegroundColor Cyan

# ============================================================================
# SCRIPT PARA DETENER TODOS LOS SERVICIOS
# ============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DETENIENDO SERVICIOS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "SilentlyContinue"

# ----------------------------------------------------------------------------
# DETENER SERVIDOR DE BÚSQUEDA (Puerto 5001)
# ----------------------------------------------------------------------------
Write-Host "[1/2] Deteniendo servidor de búsqueda..." -ForegroundColor Yellow

$puerto5001 = netstat -ano | Select-String ":5001.*LISTENING"
if ($puerto5001) {
    $pid = ($puerto5001.ToString() -split '\s+')[-1]
    Stop-Process -Id $pid -Force
    Write-Host "   ✓ Servidor detenido (PID: $pid)" -ForegroundColor Green
} else {
    Write-Host "   - Servidor no estaba corriendo" -ForegroundColor Gray
}

# ----------------------------------------------------------------------------
# DETENER FRONTEND (Puerto 5174)
# ----------------------------------------------------------------------------
Write-Host "`n[2/2] Deteniendo frontend..." -ForegroundColor Yellow

$puerto5174 = netstat -ano | Select-String ":5174.*LISTENING"
if ($puerto5174) {
    $pid = ($puerto5174.ToString() -split '\s+')[-1]
    Stop-Process -Id $pid -Force
    Write-Host "   ✓ Frontend detenido (PID: $pid)" -ForegroundColor Green
} else {
    Write-Host "   - Frontend no estaba corriendo" -ForegroundColor Gray
}

# ----------------------------------------------------------------------------
# LIMPIEZA ADICIONAL
# ----------------------------------------------------------------------------
Write-Host "`n[Extra] Limpiando procesos Python/Node relacionados..." -ForegroundColor Yellow

# Procesos Python del proyecto
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*Examinator*"
} | ForEach-Object {
    Stop-Process -Id $_.Id -Force
    Write-Host "   ✓ Python detenido (PID: $($_.Id))" -ForegroundColor Green
}

# Procesos Node del proyecto
Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*examinator-web*"
} | ForEach-Object {
    Stop-Process -Id $_.Id -Force
    Write-Host "   ✓ Node detenido (PID: $($_.Id))" -ForegroundColor Green
}

# ----------------------------------------------------------------------------
# RESUMEN
# ----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✓ SERVICIOS DETENIDOS" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "🔄 Para reiniciar:" -ForegroundColor White
Write-Host "   .\INICIAR_BUSCADOR_TODO.ps1`n" -ForegroundColor Cyan

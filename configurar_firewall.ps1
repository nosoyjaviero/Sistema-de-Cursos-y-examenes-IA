# Script para agregar reglas de firewall para Examinator
# EJECUTAR COMO ADMINISTRADOR

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURANDO FIREWALL PARA EXAMINATOR" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si es admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ ERROR: Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host ""
    Write-Host "Click derecho en el script → Ejecutar como Administrador" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit
}

Write-Host "✅ Ejecutando como Administrador" -ForegroundColor Green
Write-Host ""

# Eliminar reglas existentes si existen
Write-Host "🔍 Verificando reglas existentes..." -ForegroundColor Cyan
$rules = Get-NetFirewallRule -DisplayName "Examinator*" -ErrorAction SilentlyContinue
if ($rules) {
    Write-Host "   Eliminando reglas antiguas..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName "Examinator*" -ErrorAction SilentlyContinue
}

# Crear nuevas reglas
Write-Host ""
Write-Host "🔥 Creando reglas de firewall..." -ForegroundColor Cyan

# Backend (puerto 8000)
Write-Host "   → Puerto 8000 (Backend API)..." -ForegroundColor White
New-NetFirewallRule -DisplayName "Examinator Backend" `
    -Direction Inbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any | Out-Null

# Frontend (puerto 5173)
Write-Host "   → Puerto 5173 (Frontend Web)..." -ForegroundColor White
New-NetFirewallRule -DisplayName "Examinator Frontend 5173" `
    -Direction Inbound `
    -LocalPort 5173 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any | Out-Null

# Frontend alternativo (puerto 5174)
Write-Host "   → Puerto 5174 (Frontend Web Alt)..." -ForegroundColor White
New-NetFirewallRule -DisplayName "Examinator Frontend 5174" `
    -Direction Inbound `
    -LocalPort 5174 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ FIREWALL CONFIGURADO CORRECTAMENTE" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Mostrar reglas creadas
Write-Host "📋 Reglas creadas:" -ForegroundColor Cyan
Get-NetFirewallRule -DisplayName "Examinator*" | Format-Table DisplayName, Enabled, Direction, Action -AutoSize

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ahora deberías poder acceder desde tu móvil/tablet" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# ============================================================================
# SCRIPT DE INICIO COMPLETO - BÚSQUEDA IA
# ============================================================================
# Verifica entorno, inicia servidor de búsqueda y frontend
# ============================================================================

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO EXAMINATOR + IA SEARCH" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ----------------------------------------------------------------------------
# VERIFICACIÓN RÁPIDA
# ----------------------------------------------------------------------------
Write-Host "[1/4] Verificación rápida..." -ForegroundColor Yellow

# Python
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "✗ Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "Ejecuta: .\INSTALACION_COMPLETA.ps1" -ForegroundColor Yellow
    exit 1
}
Write-Host "   ✓ Python" -ForegroundColor Green

# Node.js
try {
    $null = & node --version 2>&1
    Write-Host "   ✓ Node.js" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Node.js no encontrado" -ForegroundColor Red
    exit 1
}

# Archivos clave
if (-not (Test-Path "api_buscador.py")) {
    Write-Host "   ✗ api_buscador.py no encontrado" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "INICIAR_BUSCADOR_GPU.bat")) {
    Write-Host "   ✗ INICIAR_BUSCADOR_GPU.bat no encontrado" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ Archivos del sistema" -ForegroundColor Green

# GPU (opcional pero recomendado)
$gpuInfo = & .\venv\Scripts\python.exe -c "import torch; print('GPU' if torch.cuda.is_available() else 'CPU')" 2>&1
if ($gpuInfo -match "GPU") {
    $gpuNombre = & .\venv\Scripts\python.exe -c "import torch; print(torch.cuda.get_device_name(0))" 2>&1
    Write-Host "   ✓ GPU: $gpuNombre" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Modo CPU (más lento)" -ForegroundColor Yellow
}

# ----------------------------------------------------------------------------
# LIBERAR PUERTOS
# ----------------------------------------------------------------------------
Write-Host "`n[2/4] Verificando puertos..." -ForegroundColor Yellow

# Puerto 5001
$puerto5001 = netstat -ano | Select-String ":5001.*LISTENING"
if ($puerto5001) {
    Write-Host "   ⚠ Puerto 5001 ocupado. Liberando..." -ForegroundColor Yellow
    $pid = ($puerto5001.ToString() -split '\s+')[-1]
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}
Write-Host "   ✓ Puerto 5001 disponible" -ForegroundColor Green

# Puerto 5174
$puerto5174 = netstat -ano | Select-String ":5174.*LISTENING"
if ($puerto5174) {
    Write-Host "   ⚠ Puerto 5174 ocupado. Liberando..." -ForegroundColor Yellow
    $pid = ($puerto5174.ToString() -split '\s+')[-1]
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}
Write-Host "   ✓ Puerto 5174 disponible" -ForegroundColor Green

# ----------------------------------------------------------------------------
# INICIAR SERVIDOR DE BÚSQUEDA
# ----------------------------------------------------------------------------
Write-Host "`n[3/4] Iniciando servidor de búsqueda IA..." -ForegroundColor Yellow

Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "INICIAR_BUSCADOR_GPU.bat" -WindowStyle Normal
Write-Host "   ✓ Servidor iniciado en nueva ventana" -ForegroundColor Green
Write-Host "   URL: http://localhost:5001" -ForegroundColor Cyan

# Esperar a que el servidor esté listo
Write-Host "`n   Esperando servidor..." -ForegroundColor Cyan
$maxIntentos = 30
$intentos = 0
$servidorListo = $false

while ($intentos -lt $maxIntentos -and -not $servidorListo) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5001/api/estado" -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $servidorListo = $true
            Write-Host "`n   ✓ Servidor listo!" -ForegroundColor Green
            
            # Mostrar info del servidor
            $estado = $response.Content | ConvertFrom-Json
            Write-Host "      GPU: $($estado.gpu_disponible)" -ForegroundColor Cyan
            Write-Host "      Chunks: $($estado.total_chunks)" -ForegroundColor Cyan
        }
    } catch {
        Start-Sleep -Seconds 1
        $intentos++
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
}

if (-not $servidorListo) {
    Write-Host "`n   ⚠ Servidor tardando (continuando...)" -ForegroundColor Yellow
}

# ----------------------------------------------------------------------------
# INICIAR FRONTEND
# ----------------------------------------------------------------------------
Write-Host "`n[4/4] Iniciando frontend React..." -ForegroundColor Yellow

if (Test-Path "examinator-web") {
    Set-Location examinator-web
    
    # Verificar node_modules
    if (-not (Test-Path "node_modules")) {
        Write-Host "   ⚠ Instalando dependencias npm..." -ForegroundColor Yellow
        & npm install
    }
    
    # Iniciar en nueva ventana
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev"
    
    Set-Location ..
    Write-Host "   ✓ Frontend iniciado en nueva ventana" -ForegroundColor Green
    Write-Host "   URL: http://localhost:5174" -ForegroundColor Cyan
} else {
    Write-Host "   ✗ Carpeta examinator-web no encontrada" -ForegroundColor Red
}

# ----------------------------------------------------------------------------
# RESUMEN FINAL
# ----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✓ SISTEMA INICIADO" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "🌐 URLS DE ACCESO:" -ForegroundColor White
Write-Host "   Frontend:  http://localhost:5174" -ForegroundColor Cyan -NoNewline
Write-Host "  (Interfaz principal)" -ForegroundColor Gray
Write-Host "   API:       http://localhost:5001" -ForegroundColor Cyan -NoNewline
Write-Host "  (Búsqueda IA)" -ForegroundColor Gray

Write-Host "`n📊 SERVICIOS ACTIVOS:" -ForegroundColor White
Write-Host "   ✓ Servidor de búsqueda IA" -ForegroundColor Green
if ($gpuInfo -match "GPU") {
    Write-Host "   ✓ Aceleración GPU habilitada" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Modo CPU (considera instalar CUDA)" -ForegroundColor Yellow
}
Write-Host "   ✓ Frontend React + Vite" -ForegroundColor Green

Write-Host "`n💡 CONSEJOS:" -ForegroundColor Cyan
Write-Host "   - Espera 5-10 segundos para carga completa" -ForegroundColor White
Write-Host "   - Primera búsqueda puede tardar ~5 segundos (carga modelo)" -ForegroundColor White
Write-Host "   - Usa pestaña 'Buscar' en la interfaz" -ForegroundColor White
Write-Host "   - Actualiza índice si agregaste archivos nuevos" -ForegroundColor White

Write-Host "`n⚙️ PARA DETENER:" -ForegroundColor White
Write-Host "   Cierra las 2 ventanas de terminal que se abrieron" -ForegroundColor Yellow
Write-Host "   O ejecuta: .\DETENER_BUSCADOR.ps1" -ForegroundColor Yellow

Write-Host "`n📚 DOCUMENTACIÓN:" -ForegroundColor White
Write-Host "   - GUIA_INSTALACION.md" -ForegroundColor Yellow
Write-Host "   - SOLUCIONES_PROBLEMAS.md" -ForegroundColor Yellow
Write-Host "   - ARQUITECTURA_BUSQUEDA.md" -ForegroundColor Yellow

Write-Host "`n🎯 Abriendo navegador en 3 segundos...`n" -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://localhost:5174"

Write-Host "Presiona cualquier tecla para salir de este script..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

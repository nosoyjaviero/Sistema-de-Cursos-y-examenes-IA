# ============================================================================
# SCRIPT DE INSTALACIÓN COMPLETA - EXAMINATOR CON BÚSQUEDA IA
# ============================================================================
# Este script instala TODAS las dependencias necesarias para el proyecto
# incluyendo PyTorch con CUDA para aceleración GPU
# ============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  INSTALACIÓN EXAMINATOR + IA SEARCH" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"

# ----------------------------------------------------------------------------
# 1. VERIFICAR PYTHON
# ----------------------------------------------------------------------------
Write-Host "[1/8] Verificando Python..." -ForegroundColor Yellow

try {
    $pythonVersion = & python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
    
    # Verificar que sea Python 3.8+
    if ($pythonVersion -notmatch "Python 3\.(8|9|10|11|12)") {
        Write-Host "⚠ Se requiere Python 3.8 o superior" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Python no encontrado. Instala Python 3.8+ desde python.org" -ForegroundColor Red
    exit 1
}

# ----------------------------------------------------------------------------
# 2. VERIFICAR NODE.JS
# ----------------------------------------------------------------------------
Write-Host "`n[2/8] Verificando Node.js..." -ForegroundColor Yellow

try {
    $nodeVersion = & node --version 2>&1
    Write-Host "✓ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js no encontrado. Instala Node.js desde nodejs.org" -ForegroundColor Red
    exit 1
}

# ----------------------------------------------------------------------------
# 3. VERIFICAR/CREAR ENTORNO VIRTUAL
# ----------------------------------------------------------------------------
Write-Host "`n[3/8] Configurando entorno virtual Python..." -ForegroundColor Yellow

if (Test-Path "venv") {
    Write-Host "✓ Entorno virtual existente encontrado" -ForegroundColor Green
    $recrear = Read-Host "¿Recrear entorno virtual? (s/N)"
    if ($recrear -eq 's' -or $recrear -eq 'S') {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "✓ Entorno virtual recreado" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Entorno virtual activado" -ForegroundColor Green

# ----------------------------------------------------------------------------
# 4. ACTUALIZAR PIP
# ----------------------------------------------------------------------------
Write-Host "`n[4/8] Actualizando pip..." -ForegroundColor Yellow
& python -m pip install --upgrade pip
Write-Host "✓ pip actualizado" -ForegroundColor Green

# ----------------------------------------------------------------------------
# 5. INSTALAR PYTORCH CON CUDA
# ----------------------------------------------------------------------------
Write-Host "`n[5/8] Instalando PyTorch con soporte CUDA..." -ForegroundColor Yellow
Write-Host "   Esto puede tardar varios minutos..." -ForegroundColor Cyan

# Instalar PyTorch con CUDA 11.8 (compatible con RTX 4050)
& pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

Write-Host "✓ PyTorch con CUDA instalado" -ForegroundColor Green

# Verificar CUDA
Write-Host "`n   Verificando GPU..." -ForegroundColor Cyan
$gpuCheck = & python -c "import torch; print('CUDA disponible:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU mode')"
Write-Host "   $gpuCheck" -ForegroundColor $(if ($gpuCheck -match "True") { "Green" } else { "Yellow" })

# ----------------------------------------------------------------------------
# 6. INSTALAR DEPENDENCIAS PYTHON
# ----------------------------------------------------------------------------
Write-Host "`n[6/8] Instalando dependencias Python..." -ForegroundColor Yellow

$paquetes = @(
    "sentence-transformers",
    "faiss-cpu",
    "rank-bm25",
    "flask",
    "flask-cors",
    "waitress",
    "requests",
    "PyPDF2",
    "python-docx",
    "numpy",
    "tqdm"
)

foreach ($paquete in $paquetes) {
    Write-Host "   Instalando $paquete..." -ForegroundColor Cyan
    & pip install $paquete
}

Write-Host "✓ Dependencias Python instaladas" -ForegroundColor Green

# ----------------------------------------------------------------------------
# 7. INSTALAR DEPENDENCIAS NODE.JS
# ----------------------------------------------------------------------------
Write-Host "`n[7/8] Instalando dependencias Node.js..." -ForegroundColor Yellow

if (Test-Path "examinator-web") {
    Set-Location examinator-web
    
    if (Test-Path "package.json") {
        Write-Host "   Ejecutando npm install..." -ForegroundColor Cyan
        & npm install
        Write-Host "✓ Dependencias Node.js instaladas" -ForegroundColor Green
    } else {
        Write-Host "⚠ No se encontró package.json" -ForegroundColor Yellow
    }
    
    Set-Location ..
} else {
    Write-Host "⚠ Carpeta examinator-web no encontrada" -ForegroundColor Yellow
}

# ----------------------------------------------------------------------------
# 8. CREAR ÍNDICE INICIAL
# ----------------------------------------------------------------------------
Write-Host "`n[8/8] Creando índice de búsqueda inicial..." -ForegroundColor Yellow

if (Test-Path "crear_indice_inicial.py") {
    Write-Host "   Indexando archivos..." -ForegroundColor Cyan
    & python crear_indice_inicial.py
    Write-Host "✓ Índice creado" -ForegroundColor Green
} else {
    Write-Host "⚠ Script crear_indice_inicial.py no encontrado (se creará al iniciar)" -ForegroundColor Yellow
}

# ----------------------------------------------------------------------------
# RESUMEN FINAL
# ----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ✓ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "📋 RESUMEN:" -ForegroundColor White
Write-Host "   ✓ Python y entorno virtual configurados" -ForegroundColor Green
Write-Host "   ✓ PyTorch con CUDA instalado" -ForegroundColor Green
Write-Host "   ✓ Dependencias Python instaladas" -ForegroundColor Green
Write-Host "   ✓ Dependencias Node.js instaladas" -ForegroundColor Green
Write-Host "   ✓ Índice de búsqueda inicializado" -ForegroundColor Green

Write-Host "`n🚀 PARA INICIAR EL SISTEMA:" -ForegroundColor Cyan
Write-Host "   Opción 1 (Recomendada):" -ForegroundColor White
Write-Host "   .\INICIAR_TODO.ps1" -ForegroundColor Yellow
Write-Host "`n   Opción 2 (Manual):" -ForegroundColor White
Write-Host "   Terminal 1: .\INICIAR_BUSCADOR_GPU.bat" -ForegroundColor Yellow
Write-Host "   Terminal 2: cd examinator-web; npm run dev" -ForegroundColor Yellow

Write-Host "`n📚 DOCUMENTACIÓN:" -ForegroundColor Cyan
Write-Host "   - GUIA_INSTALACION.md: Guía completa de instalación" -ForegroundColor White
Write-Host "   - SOLUCIONES_PROBLEMAS.md: Soluciones a errores comunes" -ForegroundColor White
Write-Host "   - ARQUITECTURA_BUSQUEDA.md: Cómo funciona el sistema" -ForegroundColor White

Write-Host "`n"

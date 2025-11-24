# ============================================================================
# SCRIPT DE VERIFICACIÓN DE ENTORNO
# ============================================================================
# Verifica que todo esté instalado correctamente antes de iniciar
# ============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  VERIFICACIÓN DE ENTORNO" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$todoOK = $true

# ----------------------------------------------------------------------------
# 1. PYTHON
# ----------------------------------------------------------------------------
Write-Host "[1/10] Python..." -ForegroundColor Yellow

try {
    $pythonVersion = & python --version 2>&1
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$Matches[1]
        if ($minorVersion -ge 8) {
            Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "   ✗ Python 3.8+ requerido (tienes $pythonVersion)" -ForegroundColor Red
            $todoOK = $false
        }
    }
} catch {
    Write-Host "   ✗ Python no encontrado" -ForegroundColor Red
    Write-Host "      Instala desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    $todoOK = $false
}

# ----------------------------------------------------------------------------
# 2. NODE.JS
# ----------------------------------------------------------------------------
Write-Host "`n[2/10] Node.js..." -ForegroundColor Yellow

try {
    $nodeVersion = & node --version 2>&1
    Write-Host "   ✓ $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Node.js no encontrado" -ForegroundColor Red
    Write-Host "      Instala desde: https://nodejs.org/" -ForegroundColor Yellow
    $todoOK = $false
}

# ----------------------------------------------------------------------------
# 3. NPM
# ----------------------------------------------------------------------------
Write-Host "`n[3/10] npm..." -ForegroundColor Yellow

try {
    $npmVersion = & npm --version 2>&1
    Write-Host "   ✓ npm $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ npm no encontrado" -ForegroundColor Red
    $todoOK = $false
}

# ----------------------------------------------------------------------------
# 4. ENTORNO VIRTUAL
# ----------------------------------------------------------------------------
Write-Host "`n[4/10] Entorno virtual Python..." -ForegroundColor Yellow

if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "   ✓ Entorno virtual existe" -ForegroundColor Green
    
    # Verificar versión en venv
    $venvPython = & .\venv\Scripts\python.exe --version 2>&1
    Write-Host "      $venvPython" -ForegroundColor Cyan
} else {
    Write-Host "   ✗ Entorno virtual no encontrado" -ForegroundColor Red
    Write-Host "      Ejecuta: .\INSTALACION_COMPLETA.ps1" -ForegroundColor Yellow
    $todoOK = $false
}

# ----------------------------------------------------------------------------
# 5. PYTORCH
# ----------------------------------------------------------------------------
Write-Host "`n[5/10] PyTorch..." -ForegroundColor Yellow

if (Test-Path "venv\Scripts\python.exe") {
    try {
        $torchInfo = & .\venv\Scripts\python.exe -c "import torch; print(f'PyTorch {torch.__version__}')" 2>&1
        
        if ($torchInfo -match "PyTorch") {
            Write-Host "   ✓ $torchInfo" -ForegroundColor Green
            
            # Verificar CUDA
            $cudaAvail = & .\venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available())" 2>&1
            if ($cudaAvail -match "True") {
                $gpuName = & .\venv\Scripts\python.exe -c "import torch; print(torch.cuda.get_device_name(0))" 2>&1
                Write-Host "      ✓ CUDA disponible" -ForegroundColor Green
                Write-Host "      GPU: $gpuName" -ForegroundColor Cyan
            } else {
                Write-Host "      ⚠ CUDA no disponible (modo CPU)" -ForegroundColor Yellow
                Write-Host "      Para GPU: pip install torch --index-url https://download.pytorch.org/whl/cu118" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   ✗ PyTorch no instalado" -ForegroundColor Red
            $todoOK = $false
        }
    } catch {
        Write-Host "   ✗ Error verificando PyTorch" -ForegroundColor Red
        $todoOK = $false
    }
}

# ----------------------------------------------------------------------------
# 6. DEPENDENCIAS PYTHON CRÍTICAS
# ----------------------------------------------------------------------------
Write-Host "`n[6/10] Dependencias Python..." -ForegroundColor Yellow

if (Test-Path "venv\Scripts\python.exe") {
    $paquetesRequeridos = @(
        "sentence-transformers",
        "faiss-cpu",
        "rank-bm25",
        "flask",
        "flask-cors",
        "waitress"
    )
    
    $faltantes = @()
    
    foreach ($paquete in $paquetesRequeridos) {
        $instalado = & .\venv\Scripts\pip.exe list | Select-String -Pattern $paquete -Quiet
        if ($instalado) {
            Write-Host "   ✓ $paquete" -ForegroundColor Green
        } else {
            Write-Host "   ✗ $paquete (faltante)" -ForegroundColor Red
            $faltantes += $paquete
            $todoOK = $false
        }
    }
    
    if ($faltantes.Count -gt 0) {
        Write-Host "`n      Instalar faltantes con:" -ForegroundColor Yellow
        Write-Host "      pip install $($faltantes -join ' ')" -ForegroundColor Cyan
    }
}

# ----------------------------------------------------------------------------
# 7. NODE_MODULES
# ----------------------------------------------------------------------------
Write-Host "`n[7/10] Dependencias Node.js..." -ForegroundColor Yellow

if (Test-Path "examinator-web\node_modules") {
    $packageCount = (Get-ChildItem "examinator-web\node_modules" -Directory).Count
    Write-Host "   ✓ node_modules existe ($packageCount paquetes)" -ForegroundColor Green
} else {
    Write-Host "   ✗ node_modules no encontrado" -ForegroundColor Red
    Write-Host "      Ejecuta: cd examinator-web; npm install" -ForegroundColor Yellow
    $todoOK = $false
}

# ----------------------------------------------------------------------------
# 8. ÍNDICES DE BÚSQUEDA
# ----------------------------------------------------------------------------
Write-Host "`n[8/10] Índices de búsqueda..." -ForegroundColor Yellow

if (Test-Path "indices_busqueda") {
    $archivos = @(
        "faiss_index.bin",
        "bm25_index.pkl",
        "chunks.json"
    )
    
    $todosExisten = $true
    foreach ($archivo in $archivos) {
        if (Test-Path "indices_busqueda\$archivo") {
            Write-Host "   ✓ $archivo" -ForegroundColor Green
        } else {
            Write-Host "   ✗ $archivo (faltante)" -ForegroundColor Yellow
            $todosExisten = $false
        }
    }
    
    if (-not $todosExisten) {
        Write-Host "      Crear índices con: python crear_indice_inicial.py" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠ Carpeta indices_busqueda no existe" -ForegroundColor Yellow
    Write-Host "      Se creará al ejecutar: python crear_indice_inicial.py" -ForegroundColor Cyan
}

# ----------------------------------------------------------------------------
# 9. PUERTOS DISPONIBLES
# ----------------------------------------------------------------------------
Write-Host "`n[9/10] Puertos..." -ForegroundColor Yellow

# Puerto 5001 (API Búsqueda)
$puerto5001 = netstat -ano | Select-String ":5001.*LISTENING"
if ($puerto5001) {
    $pid = ($puerto5001.ToString() -split '\s+')[-1]
    Write-Host "   ⚠ Puerto 5001 ocupado (PID: $pid)" -ForegroundColor Yellow
    Write-Host "      Liberar con: Stop-Process -Id $pid -Force" -ForegroundColor Cyan
} else {
    Write-Host "   ✓ Puerto 5001 disponible" -ForegroundColor Green
}

# Puerto 5174 (Frontend)
$puerto5174 = netstat -ano | Select-String ":5174.*LISTENING"
if ($puerto5174) {
    $pid = ($puerto5174.ToString() -split '\s+')[-1]
    Write-Host "   ⚠ Puerto 5174 ocupado (PID: $pid)" -ForegroundColor Yellow
    Write-Host "      Liberar con: Stop-Process -Id $pid -Force" -ForegroundColor Cyan
} else {
    Write-Host "   ✓ Puerto 5174 disponible" -ForegroundColor Green
}

# ----------------------------------------------------------------------------
# 10. ARCHIVOS CLAVE
# ----------------------------------------------------------------------------
Write-Host "`n[10/10] Archivos del sistema..." -ForegroundColor Yellow

$archivosClave = @(
    "buscador_ia.py",
    "api_buscador.py",
    "crear_indice_inicial.py",
    "INICIAR_BUSCADOR_GPU.bat",
    "examinator-web\src\App.jsx"
)

foreach ($archivo in $archivosClave) {
    if (Test-Path $archivo) {
        Write-Host "   ✓ $archivo" -ForegroundColor Green
    } else {
        Write-Host "   ✗ $archivo (faltante)" -ForegroundColor Red
        $todoOK = $false
    }
}

# ----------------------------------------------------------------------------
# RESUMEN
# ----------------------------------------------------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan

if ($todoOK) {
    Write-Host "  ✓ SISTEMA LISTO" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "🚀 Para iniciar el sistema:" -ForegroundColor White
    Write-Host "   .\INICIAR_BUSCADOR_TODO.ps1" -ForegroundColor Cyan
    Write-Host "`n   O manualmente:" -ForegroundColor White
    Write-Host "   Terminal 1: .\INICIAR_BUSCADOR_GPU.bat" -ForegroundColor Yellow
    Write-Host "   Terminal 2: cd examinator-web; npm run dev" -ForegroundColor Yellow
    
} else {
    Write-Host "  ⚠ CONFIGURACIÓN INCOMPLETA" -ForegroundColor Yellow
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "📋 Para completar instalación:" -ForegroundColor White
    Write-Host "   .\INSTALACION_COMPLETA.ps1" -ForegroundColor Cyan
    
    Write-Host "`n📚 Más información:" -ForegroundColor White
    Write-Host "   - GUIA_INSTALACION.md" -ForegroundColor Yellow
    Write-Host "   - SOLUCIONES_PROBLEMAS.md" -ForegroundColor Yellow
}

Write-Host "`n"

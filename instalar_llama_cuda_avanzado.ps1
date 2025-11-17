# Script avanzado para compilar llama-cpp-python con CUDA
# Configura el entorno manualmente para evitar problemas de integración

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔧 INSTALACIÓN AVANZADA DE LLAMA-CPP-PYTHON CON CUDA" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar CUDA
$cudaVersion = "12.2"
$cudaPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v$cudaVersion"

Write-Host "📝 Verificando CUDA $cudaVersion..." -ForegroundColor Yellow
if (Test-Path $cudaPath) {
    Write-Host "   ✅ CUDA $cudaVersion encontrado: $cudaPath" -ForegroundColor Green
} else {
    Write-Host "   ❌ CUDA $cudaVersion no encontrado" -ForegroundColor Red
    Write-Host "   Buscando otras versiones..." -ForegroundColor Yellow
    
    $cudaVersions = Get-ChildItem "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\" -Directory | Select-Object -ExpandProperty Name
    Write-Host "   Versiones disponibles: $($cudaVersions -join ', ')" -ForegroundColor Cyan
    
    # Usar la versión más reciente
    $latestVersion = $cudaVersions | Sort-Object -Descending | Select-Object -First 1
    $cudaPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\$latestVersion"
    Write-Host "   ✅ Usando: $cudaPath" -ForegroundColor Green
}

# 2. Configurar variables de entorno CUDA
Write-Host ""
Write-Host "⚙️  Configurando variables de entorno..." -ForegroundColor Yellow

$env:CUDA_PATH = $cudaPath
$env:CUDA_HOME = $cudaPath
$env:CUDA_TOOLKIT_ROOT_DIR = $cudaPath

# Agregar binarios CUDA al PATH
$cudaBin = "$cudaPath\bin"
$cudaLib = "$cudaPath\lib\x64"

if (-not ($env:PATH -like "*$cudaBin*")) {
    $env:PATH = "$cudaBin;$env:PATH"
}
if (-not ($env:PATH -like "*$cudaLib*")) {
    $env:PATH = "$cudaLib;$env:PATH"
}

Write-Host "   ✅ CUDA_PATH: $env:CUDA_PATH" -ForegroundColor Green
Write-Host "   ✅ CUDA_HOME: $env:CUDA_HOME" -ForegroundColor Green

# 3. Verificar nvcc
Write-Host ""
Write-Host "🔍 Verificando compilador CUDA (nvcc)..." -ForegroundColor Yellow
try {
    $nvccVersion = & "$cudaBin\nvcc.exe" --version 2>&1 | Select-String "release" | Select-Object -First 1
    Write-Host "   ✅ nvcc encontrado: $nvccVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ nvcc no encontrado o no funciona" -ForegroundColor Red
    exit 1
}

# 4. Encontrar Visual Studio
Write-Host ""
Write-Host "🔍 Buscando Visual Studio..." -ForegroundColor Yellow

$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vsWhere) {
    $vsPath = & $vsWhere -latest -property installationPath
    $vsMajorVersion = & $vsWhere -latest -property installationVersion | ForEach-Object { $_.Split('.')[0] }
    
    Write-Host "   ✅ Visual Studio encontrado: $vsPath" -ForegroundColor Green
    Write-Host "   📦 Versión: $vsMajorVersion" -ForegroundColor Cyan
    
    # Buscar vcvarsall.bat
    $vcvarsPath = "$vsPath\VC\Auxiliary\Build\vcvarsall.bat"
    if (Test-Path $vcvarsPath) {
        Write-Host "   ✅ vcvarsall.bat encontrado" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  Visual Studio no detectado automáticamente" -ForegroundColor Yellow
}

# 5. Configurar CMAKE específicamente para CUDA
Write-Host ""
Write-Host "⚙️  Configurando CMAKE..." -ForegroundColor Yellow

# Usar método más directo: especificar el compilador CUDA
$env:CMAKE_ARGS = @"
-DGGML_CUDA=on `
-DCMAKE_CUDA_COMPILER="$cudaBin\nvcc.exe" `
-DCUDA_TOOLKIT_ROOT_DIR="$cudaPath" `
-DCMAKE_CUDA_ARCHITECTURES=native
"@ -replace "`n", " " -replace "`r", ""

Write-Host "   ✅ CMAKE_ARGS configurado" -ForegroundColor Green
Write-Host "      $env:CMAKE_ARGS" -ForegroundColor Gray

# 6. Desinstalar versión actual
Write-Host ""
Write-Host "🗑️  Desinstalando llama-cpp-python actual..." -ForegroundColor Yellow
$uninstallOutput = pip uninstall llama-cpp-python -y 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Desinstalado correctamente" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No había versión instalada" -ForegroundColor Cyan
}

# 7. Intentar compilación con configuración manual
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔨 INICIANDO COMPILACIÓN" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   ⏰ Esto tardará 10-20 minutos..." -ForegroundColor Yellow
Write-Host "   📊 Verás mucha salida de compilación (es normal)" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# Usar pip con variables de entorno configuradas
pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose 2>&1 | Tee-Object -Variable buildOutput

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ INSTALACIÓN EXITOSA" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "   ⏱️  Tiempo: $($duration.Minutes) min $($duration.Seconds) seg" -ForegroundColor Green
    Write-Host ""
    
    # Probar importación
    Write-Host "🧪 Probando importación..." -ForegroundColor Yellow
    python -c "from llama_cpp import Llama; print('✅ Importación exitosa')" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 TODO LISTO" -ForegroundColor Green
        Write-Host ""
        Write-Host "📝 Siguiente paso:" -ForegroundColor Cyan
        Write-Host "   python verificar_gpu.py" -ForegroundColor White
        Write-Host ""
    }
    
} else {
    Write-Host "❌ ERROR EN LA COMPILACIÓN" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    
    # Analizar el error
    $errorLines = $buildOutput | Select-String -Pattern "error|failed|ERROR|FAILED" | Select-Object -Last 10
    
    if ($errorLines -match "No CUDA toolset found") {
        Write-Host "⚠️  PROBLEMA DETECTADO: Visual Studio no encuentra CUDA" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "SOLUCIÓN 1: Integrar CUDA con Visual Studio" -ForegroundColor Cyan
        Write-Host "   1. Abre 'Visual Studio Installer'" -ForegroundColor White
        Write-Host "   2. Clic en 'Modificar' en Build Tools 2022" -ForegroundColor White
        Write-Host "   3. Marca 'Desarrollo para el escritorio con C++'" -ForegroundColor White
        Write-Host "   4. En la derecha, marca 'CUDA Toolkit'" -ForegroundColor White
        Write-Host "   5. Instalar y reiniciar" -ForegroundColor White
        Write-Host ""
        Write-Host "SOLUCIÓN 2: Reinstalar CUDA con integración VS" -ForegroundColor Cyan
        Write-Host "   1. Descargar CUDA 12.2:" -ForegroundColor White
        Write-Host "      https://developer.nvidia.com/cuda-12-2-0-download-archive" -ForegroundColor Gray
        Write-Host "   2. Durante instalación, seleccionar 'Visual Studio Integration'" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "SOLUCIÓN 3: Usar alternativas más simples" -ForegroundColor Cyan
    Write-Host "   Ollama (5 min): https://ollama.ai/" -ForegroundColor White
    Write-Host "   LM Studio (GUI): https://lmstudio.ai/" -ForegroundColor White
    Write-Host ""
}

Write-Host "============================================================" -ForegroundColor Cyan

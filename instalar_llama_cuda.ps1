# Script para instalar llama-cpp-python con soporte CUDA
# Ejecutar con: .\instalar_llama_cuda.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🎮 INSTALACIÓN DE LLAMA-CPP-PYTHON CON CUDA" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Configurar CUDA 12.2
Write-Host "📝 Configurando variables de entorno CUDA..." -ForegroundColor Yellow
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2"
$env:CUDA_HOME = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2"
$cudaBinPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2\bin"

# Agregar al PATH actual
$env:PATH = "$cudaBinPath;$env:PATH"

Write-Host "   ✅ CUDA_PATH: $env:CUDA_PATH" -ForegroundColor Green
Write-Host "   ✅ CUDA_HOME: $env:CUDA_HOME" -ForegroundColor Green

# 2. Verificar nvcc
Write-Host ""
Write-Host "🔍 Verificando nvcc..." -ForegroundColor Yellow
$nvccPath = "$cudaBinPath\nvcc.exe"
if (Test-Path $nvccPath) {
    Write-Host "   ✅ nvcc encontrado: $nvccPath" -ForegroundColor Green
    & $nvccPath --version | Select-Object -Last 1
} else {
    Write-Host "   ❌ ERROR: nvcc no encontrado en $nvccPath" -ForegroundColor Red
    Write-Host "   Por favor, instala CUDA Toolkit 12.2 desde:" -ForegroundColor Red
    Write-Host "   https://developer.nvidia.com/cuda-12-2-0-download-archive" -ForegroundColor Red
    exit 1
}

# 3. Verificar Visual Studio
Write-Host ""
Write-Host "🔍 Verificando Visual Studio Build Tools..." -ForegroundColor Yellow
$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vsWhere) {
    $vsPath = & $vsWhere -latest -property installationPath
    Write-Host "   ✅ Visual Studio encontrado: $vsPath" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Visual Studio Build Tools no detectado" -ForegroundColor Yellow
    Write-Host "   Si la compilación falla, instala desde:" -ForegroundColor Yellow
    Write-Host "   https://visualstudio.microsoft.com/es/downloads/#build-tools-for-visual-studio-2022" -ForegroundColor Yellow
}

# 4. Desinstalar versión actual
Write-Host ""
Write-Host "🗑️  Desinstalando llama-cpp-python actual..." -ForegroundColor Yellow
pip uninstall llama-cpp-python -y 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Desinstalado correctamente" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  No había versión instalada" -ForegroundColor Cyan
}

# 5. Configurar CMAKE para compilar con CUDA
Write-Host ""
Write-Host "⚙️  Configurando CMAKE para CUDA..." -ForegroundColor Yellow
$env:CMAKE_ARGS = "-DGGML_CUDA=on"
Write-Host "   ✅ CMAKE_ARGS: $env:CMAKE_ARGS" -ForegroundColor Green

# 6. Instalar llama-cpp-python compilando desde código
Write-Host ""
Write-Host "🔨 Compilando llama-cpp-python con CUDA..." -ForegroundColor Yellow
Write-Host "   ⏰ Esto puede tardar 5-15 minutos..." -ForegroundColor Cyan
Write-Host "   (verás mucha salida de compilación, es normal)" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "✅ INSTALACIÓN EXITOSA" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "   Tiempo: $($duration.Minutes) min $($duration.Seconds) seg" -ForegroundColor Green
    Write-Host ""
    Write-Host "🧪 Probando GPU..." -ForegroundColor Yellow
    
    # Probar GPU
    python -c "from llama_cpp import Llama; print('✅ Import exitoso')"
    
    Write-Host ""
    Write-Host "📝 Siguiente paso:" -ForegroundColor Cyan
    Write-Host "   1. Reinicia el servidor: python api_server.py" -ForegroundColor White
    Write-Host "   2. Verifica en la consola que diga 'assigned to device GPU'" -ForegroundColor White
    Write-Host "   3. Genera un examen y observa el uso de GPU en nvidia-smi" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "❌ ERROR EN LA INSTALACIÓN" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Posibles soluciones:" -ForegroundColor Yellow
    Write-Host "1. Instala Visual Studio 2022 Build Tools:" -ForegroundColor White
    Write-Host "   https://visualstudio.microsoft.com/es/downloads/#build-tools-for-visual-studio-2022" -ForegroundColor Cyan
    Write-Host "   - Selecciona 'Desarrollo para el escritorio con C++'" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Verifica que CUDA 12.2 esté completo:" -ForegroundColor White
    Write-Host "   https://developer.nvidia.com/cuda-12-2-0-download-archive" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Usa alternativas más simples:" -ForegroundColor White
    Write-Host "   - Ollama: https://ollama.ai/" -ForegroundColor Cyan
    Write-Host "   - LM Studio: https://lmstudio.ai/" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "================================================" -ForegroundColor Cyan

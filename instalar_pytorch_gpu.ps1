# Script para instalar PyTorch con CUDA para RTX 4050
Write-Host "🔧 Instalando PyTorch con soporte CUDA..." -ForegroundColor Green

# Detener todos los procesos Python del proyecto
Write-Host "`n🛑 Deteniendo procesos Python..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*Examinator*"} | Stop-Process -Force
Start-Sleep -Seconds 2

# Activar entorno virtual
Write-Host "`n📦 Activando entorno virtual..." -ForegroundColor Yellow
& "C:\Users\Fela\Documents\Proyectos\Examinator\venv\Scripts\Activate.ps1"

# Desinstalar versión CPU
Write-Host "`n❌ Desinstalando PyTorch CPU..." -ForegroundColor Yellow
python -m pip uninstall torch torchvision torchaudio -y

# Instalar versión CUDA (CUDA 11.8 es compatible con RTX 4050)
Write-Host "`n⚡ Instalando PyTorch con CUDA 11.8..." -ForegroundColor Green
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verificar instalación
Write-Host "`n✅ Verificando instalación..." -ForegroundColor Green
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA disponible: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

Write-Host "`n🎉 ¡Instalación completa!" -ForegroundColor Green
Write-Host "Ahora ejecuta: python api_buscador.py" -ForegroundColor Cyan

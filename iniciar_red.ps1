# Examinator - Iniciar con acceso en red local
# Ejecutar como Administrador para configurar firewall automáticamente

$Host.UI.RawUI.WindowTitle = "📱 Examinator - Red Local"
Clear-Host

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   📱 EXAMINATOR - CONFIGURACIÓN DE RED LOCAL" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar privilegios de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  ADVERTENCIA: No ejecutado como Administrador" -ForegroundColor Yellow
    Write-Host "   El firewall no será configurado automáticamente." -ForegroundColor Yellow
    Write-Host "   Si no puedes conectarte, ejecuta este script como Admin." -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 2
}

# Obtener IP local
Write-Host "🔍 Detectando dirección IP local..." -ForegroundColor Cyan
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "Loopback" -and $_.IPAddress -notmatch "^169\.254" } | Select-Object -First 1).IPAddress

if ($ipAddress) {
    Write-Host "✅ IP detectada: $ipAddress" -ForegroundColor Green
} else {
    Write-Host "❌ No se pudo detectar la IP. Usando localhost." -ForegroundColor Red
    $ipAddress = "localhost"
}
Write-Host ""

# Liberar puertos si están ocupados
Write-Host "🔍 Verificando y liberando puertos..." -ForegroundColor Cyan

$ports = @(8000, 5173, 5174)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connections) {
        Write-Host "   Liberando puerto $port..." -ForegroundColor Yellow
        foreach ($conn in $connections) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Milliseconds 500
    }
}
Write-Host "✅ Puertos verificados" -ForegroundColor Green
Write-Host ""

# Configurar firewall (solo si es admin)
if ($isAdmin) {
    Write-Host "🔥 Configurando firewall de Windows..." -ForegroundColor Cyan
    
    # Backend (puerto 8000)
    $backendRule = Get-NetFirewallRule -DisplayName "Examinator Backend" -ErrorAction SilentlyContinue
    if (-not $backendRule) {
        New-NetFirewallRule -DisplayName "Examinator Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow | Out-Null
        Write-Host "   ✅ Regla creada para Backend (8000)" -ForegroundColor Green
    } else {
        Write-Host "   ✅ Regla existente para Backend (8000)" -ForegroundColor Green
    }
    
    # Frontend (puertos 5173 y 5174)
    $frontendRule = Get-NetFirewallRule -DisplayName "Examinator Frontend" -ErrorAction SilentlyContinue
    if (-not $frontendRule) {
        New-NetFirewallRule -DisplayName "Examinator Frontend" -Direction Inbound -LocalPort 5173,5174 -Protocol TCP -Action Allow | Out-Null
        Write-Host "   ✅ Reglas creadas para Frontend (5173, 5174)" -ForegroundColor Green
    } else {
        Write-Host "   ✅ Reglas existentes para Frontend (5173, 5174)" -ForegroundColor Green
    }
    Write-Host ""
}

# Modificar package.json para incluir --host
Write-Host "🔧 Configurando Vite para acceso en red..." -ForegroundColor Cyan
$packageJsonPath = "examinator-web\package.json"
if (Test-Path $packageJsonPath) {
    $packageJson = Get-Content $packageJsonPath -Raw
    if ($packageJson -notmatch '--host') {
        $packageJson = $packageJson -replace '"vite"', '"vite --host"'
        Set-Content -Path $packageJsonPath -Value $packageJson -Encoding UTF8
        Write-Host "✅ Configuración de Vite actualizada" -ForegroundColor Green
    } else {
        Write-Host "✅ Configuración de Vite ya lista" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  No se encontró package.json" -ForegroundColor Yellow
}
Write-Host ""

# Guardar IP en archivo
$ipAddress | Out-File -FilePath ".ip_local.txt" -Encoding UTF8

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   🚀 INICIANDO SERVIDORES" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Iniciar Backend
Write-Host "⏳ Iniciando Backend API..." -ForegroundColor Yellow
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
    `$Host.UI.RawUI.WindowTitle = '🔥 Backend API - Puerto 8000'
    Write-Host '🔥 Backend API corriendo en puerto 8000...' -ForegroundColor Green
    Write-Host ''
    python api_server.py
}" -PassThru

Start-Sleep -Seconds 3

# Iniciar Frontend
Write-Host "⏳ Iniciando Frontend Web..." -ForegroundColor Yellow
$frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
    `$Host.UI.RawUI.WindowTitle = '🎨 Frontend Web - Puerto 5173/5174'
    Write-Host '🎨 Frontend corriendo...' -ForegroundColor Green
    Write-Host ''
    Set-Location examinator-web
    npm run dev
}" -PassThru

Start-Sleep -Seconds 5

Clear-Host
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ SERVIDORES INICIADOS CORRECTAMENTE" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📱 PARA ACCEDER DESDE TU MÓVIL/TABLET:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   1️⃣  Conecta tu dispositivo a la MISMA RED WIFI" -ForegroundColor White
Write-Host ""
Write-Host "   2️⃣  Abre el navegador en tu móvil" -ForegroundColor White
Write-Host ""
Write-Host "   3️⃣  Escribe una de estas direcciones:" -ForegroundColor White
Write-Host ""
Write-Host "       🌐 http://${ipAddress}:5173" -ForegroundColor Yellow -BackgroundColor DarkBlue
Write-Host "       🌐 http://${ipAddress}:5174" -ForegroundColor Yellow -BackgroundColor DarkBlue
Write-Host "          (prueba el segundo si el primero no funciona)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "💻 EN ESTA PC:" -ForegroundColor Cyan
Write-Host "   🌐 http://localhost:5173" -ForegroundColor White
Write-Host "   🌐 http://localhost:5174" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📝 NOTAS:" -ForegroundColor Cyan
Write-Host "   • Los servidores están corriendo en ventanas separadas" -ForegroundColor White
Write-Host "   • Cierra esas ventanas para detener los servidores" -ForegroundColor White
Write-Host "   • Tu IP se guardó en: .ip_local.txt" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

# Intentar abrir navegador local
Start-Sleep -Seconds 2
Write-Host "🌐 Abriendo navegador local..." -ForegroundColor Cyan
try {
    Start-Process "http://localhost:5173"
} catch {
    try {
        Start-Process "http://localhost:5174"
    } catch {
        Write-Host "⚠️  No se pudo abrir el navegador automáticamente" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar (servidores seguirán activos)..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

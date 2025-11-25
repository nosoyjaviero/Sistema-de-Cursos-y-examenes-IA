# Script de Verificación Completa del Sistema
Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🔍 VERIFICACIÓN COMPLETA DEL SISTEMA EXAMINATOR         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$errores = 0
$advertencias = 0

# 1. Verificar que el servidor esté corriendo
Write-Host "📡 1. Verificando servidor backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 3 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Servidor backend activo (Puerto 8000)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Servidor backend NO responde en puerto 8000" -ForegroundColor Red
    Write-Host "      Solución: Ejecutar 'python -m uvicorn api_server:app --host 0.0.0.0 --port 8000'" -ForegroundColor Gray
    $errores++
}

# 2. Verificar que el endpoint generar_practica existe
Write-Host "`n📍 2. Verificando endpoint /api/generar_practica..." -ForegroundColor Yellow
try {
    $openapi = Invoke-RestMethod -Uri "http://localhost:8000/openapi.json" -Method GET -TimeoutSec 3 -ErrorAction Stop
    if ($openapi.paths.'/api/generar_practica') {
        Write-Host "   ✅ Endpoint /api/generar_practica registrado" -ForegroundColor Green
        
        # Verificar métodos
        $metodos = $openapi.paths.'/api/generar_practica'.PSObject.Properties.Name
        if ($metodos -contains 'post') {
            Write-Host "      ✅ Método POST disponible" -ForegroundColor Green
        } else {
            Write-Host "      ❌ Método POST NO disponible" -ForegroundColor Red
            $errores++
        }
    } else {
        Write-Host "   ❌ Endpoint /api/generar_practica NO encontrado" -ForegroundColor Red
        Write-Host "      El archivo api_server.py no tiene el endpoint" -ForegroundColor Gray
        $errores++
    }
} catch {
    Write-Host "   ❌ No se pudo verificar endpoints" -ForegroundColor Red
    $errores++
}

# 3. Probar el endpoint con una solicitud real
Write-Host "`n🧪 3. Probando endpoint con solicitud real..." -ForegroundColor Yellow
$testBody = @{
    prompt = "Test de verificación automática"
    num_flashcards = 1
    tipo_flashcard = "respuesta_corta"
} | ConvertTo-Json

try {
    Write-Host "   ⏳ Enviando solicitud... (puede tomar 20-40 segundos)" -ForegroundColor Gray
    $testResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/generar_practica" `
                                       -Method POST `
                                       -Body $testBody `
                                       -ContentType "application/json" `
                                       -TimeoutSec 90 `
                                       -ErrorAction Stop
    
    if ($testResponse.success) {
        Write-Host "   ✅ Endpoint funciona correctamente" -ForegroundColor Green
        Write-Host "      ├─ Session ID: $($testResponse.session_id)" -ForegroundColor Gray
        Write-Host "      ├─ Total preguntas: $($testResponse.total_preguntas)" -ForegroundColor Gray
        Write-Host "      └─ Tipo de primera pregunta: $($testResponse.preguntas[0].tipo)" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  Endpoint respondió pero success=false" -ForegroundColor Yellow
        $advertencias++
    }
} catch {
    $statusCode = $null
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
    }
    
    if ($statusCode -eq 404) {
        Write-Host "   ❌ ERROR 404 - Endpoint no existe" -ForegroundColor Red
        Write-Host "      El servidor necesita reiniciarse o el código no se cargó" -ForegroundColor Gray
    } elseif ($statusCode -eq 500) {
        Write-Host "   ❌ ERROR 500 - Error interno del servidor" -ForegroundColor Red
        Write-Host "      Revisar logs del servidor para más detalles" -ForegroundColor Gray
    } else {
        Write-Host "   ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    $errores++
}

# 4. Verificar archivos del sistema
Write-Host "`n📁 4. Verificando archivos del sistema..." -ForegroundColor Yellow

$archivosRequeridos = @(
    "api_server.py",
    "generador_unificado.py",
    "config.json"
)

foreach ($archivo in $archivosRequeridos) {
    $ruta = "C:\Users\Fela\Documents\Proyectos\Examinator\$archivo"
    if (Test-Path $ruta) {
        Write-Host "   ✅ $archivo" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $archivo NO ENCONTRADO" -ForegroundColor Red
        $errores++
    }
}

# 5. Verificar modelo Ollama
Write-Host "`n🤖 5. Verificando modelo Ollama..." -ForegroundColor Yellow
try {
    $ollama = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 3 -ErrorAction Stop
    $modeloDefecto = "Meta-Llama-3.1-8B-Instruct-Q4-K-L"
    $modeloEncontrado = $false
    
    foreach ($modelo in $ollama.models) {
        if ($modelo.name -like "*$modeloDefecto*" -or $modelo.name -like "*Meta-Llama-3.1*") {
            Write-Host "   ✅ Modelo Ollama activo: $($modelo.name)" -ForegroundColor Green
            Write-Host "      Tamaño: $([Math]::Round($modelo.size / 1GB, 2)) GB" -ForegroundColor Gray
            $modeloEncontrado = $true
            break
        }
    }
    
    if (-not $modeloEncontrado) {
        Write-Host "   ⚠️  Modelo Meta-Llama-3.1 no encontrado" -ForegroundColor Yellow
        Write-Host "      Modelos disponibles:" -ForegroundColor Gray
        foreach ($modelo in $ollama.models | Select-Object -First 3) {
            Write-Host "      - $($modelo.name)" -ForegroundColor Gray
        }
        $advertencias++
    }
} catch {
    Write-Host "   ⚠️  Ollama no responde (puede estar usando llama-cpp-python)" -ForegroundColor Yellow
    $advertencias++
}

# 6. Verificar configuración
Write-Host "`n⚙️  6. Verificando configuración..." -ForegroundColor Yellow
try {
    $config = Get-Content "C:\Users\Fela\Documents\Proyectos\Examinator\config.json" -Raw | ConvertFrom-Json
    
    Write-Host "   ├─ usar_ollama: $($config.usar_ollama)" -ForegroundColor Gray
    Write-Host "   ├─ modelo_ollama_activo: $($config.modelo_ollama_activo)" -ForegroundColor Gray
    Write-Host "   ├─ gpu_activa: $($config.gpu_activa)" -ForegroundColor Gray
    Write-Host "   └─ n_gpu_layers: $($config.ajustes_avanzados.n_gpu_layers)" -ForegroundColor Gray
    
    if ($config.usar_ollama) {
        Write-Host "   ✅ Configurado para usar Ollama" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Configurado para usar llama-cpp-python" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ⚠️  No se pudo leer config.json" -ForegroundColor Yellow
    $advertencias++
}

# 7. Verificar frontend
Write-Host "`n🌐 7. Verificando frontend React..." -ForegroundColor Yellow
$frontendPath = "C:\Users\Fela\Documents\Proyectos\Examinator\examinator-web"
if (Test-Path $frontendPath) {
    Write-Host "   ✅ Directorio frontend existe" -ForegroundColor Green
    
    if (Test-Path "$frontendPath\src\App.jsx") {
        Write-Host "   ✅ App.jsx encontrado" -ForegroundColor Green
        
        # Verificar que App.jsx tiene la función para generar práctica
        $appContent = Get-Content "$frontendPath\src\App.jsx" -Raw
        if ($appContent -match "generar_practica") {
            Write-Host "   ✅ Código frontend tiene función generar_practica" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  No se encontró referencia a generar_practica en App.jsx" -ForegroundColor Yellow
            $advertencias++
        }
    }
} else {
    Write-Host "   ⚠️  Directorio frontend no encontrado" -ForegroundColor Yellow
    $advertencias++
}

# Resumen final
Write-Host "`n" -NoNewline
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    📊 RESUMEN                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

if ($errores -eq 0 -and $advertencias -eq 0) {
    Write-Host "`n✅ SISTEMA COMPLETAMENTE FUNCIONAL" -ForegroundColor Green
    Write-Host "   Todos los componentes están operativos." -ForegroundColor White
    Write-Host "`n🎯 SIGUIENTE PASO:" -ForegroundColor Yellow
    Write-Host "   1. Abrir http://localhost:3000 en el navegador" -ForegroundColor White
    Write-Host "   2. Presionar Ctrl+Shift+R para limpiar caché" -ForegroundColor White
    Write-Host "   3. Intentar generar una práctica" -ForegroundColor White
    Write-Host "`n   O probar la página de test:" -ForegroundColor Cyan
    Write-Host "   C:\Users\Fela\Documents\Proyectos\Examinator\test_practica.html`n" -ForegroundColor White
} elseif ($errores -eq 0) {
    Write-Host "`n⚠️  SISTEMA FUNCIONAL CON ADVERTENCIAS" -ForegroundColor Yellow
    Write-Host "   Errores: $errores" -ForegroundColor White
    Write-Host "   Advertencias: $advertencias" -ForegroundColor White
    Write-Host "`n   El endpoint debería funcionar, pero revisa las advertencias.`n" -ForegroundColor Gray
} else {
    Write-Host "`n❌ SISTEMA CON ERRORES" -ForegroundColor Red
    Write-Host "   Errores: $errores" -ForegroundColor White
    Write-Host "   Advertencias: $advertencias" -ForegroundColor White
    Write-Host "`n   Revisa los errores arriba y corrígelos antes de continuar.`n" -ForegroundColor Gray
}

Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

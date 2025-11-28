# ========================================
# TEST: Examen desde Dropdown (Carpeta)
# ========================================
# Verifica que los exámenes generados desde dropdown se guarden como examen_*.json

$API_URL = "http://localhost:8000"
$CARPETA_TEST = "Platzi/Prueba/eeeee"

Write-Host "`n" -NoNewline
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  TEST: Examen desde Dropdown - Verificar Nomenclatura Correcta" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# ============================================================
# PASO 0: Limpiar archivos de prueba anteriores
# ============================================================
Write-Host "📋 PASO 0: Limpiar archivos de prueba anteriores" -ForegroundColor Yellow
Write-Host "─" * 70

$carpetaCompleta = "extracciones\$CARPETA_TEST"
if (Test-Path $carpetaCompleta) {
    $archivosAntesLimpieza = Get-ChildItem $carpetaCompleta -Filter "examen_*.json" | Where-Object { 
        $_.LastWriteTime -gt (Get-Date).AddMinutes(-5) 
    }
    
    if ($archivosAntesLimpieza) {
        Write-Host "   🗑️  Eliminando archivos de prueba recientes..." -ForegroundColor DarkYellow
        foreach ($archivo in $archivosAntesLimpieza) {
            Remove-Item $archivo.FullName -Force
            Write-Host "      ❌ $($archivo.Name)" -ForegroundColor Red
        }
    } else {
        Write-Host "   ✅ No hay archivos recientes para limpiar" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  La carpeta no existe todavía" -ForegroundColor DarkYellow
}

Write-Host ""

# ============================================================
# PASO 1: Generar Examen desde Carpeta (simular dropdown)
# ============================================================
Write-Host "📋 PASO 1: Generar Examen desde Carpeta" -ForegroundColor Yellow
Write-Host "─" * 70

$bodyGenerar = @{
    carpeta = $CARPETA_TEST
    cantidad_preguntas = 2
    tipo_carpeta = "CLASE"  # Simular que viene del dropdown
    incluir_subcarpetas = $false
    tipos_pregunta = @("mcq", "verdadero_falso")
} | ConvertTo-Json

Write-Host "   📤 POST /api/generar_examen_carpeta" -ForegroundColor Cyan
Write-Host "      Carpeta: $CARPETA_TEST"
Write-Host "      Cantidad: 2 preguntas"
Write-Host "      Tipo: CLASE (dropdown)"

try {
    $response = Invoke-RestMethod -Uri "$API_URL/api/generar_examen_carpeta" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $bodyGenerar `
        -TimeoutSec 60
    
    if ($response.success) {
        Write-Host "   ✅ Examen generado exitosamente" -ForegroundColor Green
        Write-Host "      Total preguntas: $($response.total_preguntas)"
        Write-Host "      Puntos totales: $($response.puntos_totales)"
        
        $preguntasGeneradas = $response.preguntas
    } else {
        Write-Host "   ❌ Error: $($response.message)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ Error al generar examen: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================
# PASO 2: Evaluar Examen (responder todas incorrectas)
# ============================================================
Write-Host "📋 PASO 2: Evaluar Examen" -ForegroundColor Yellow
Write-Host "─" * 70

# Crear respuestas incorrectas para todas las preguntas
$respuestas = @{}
for ($i = 0; $i -lt $preguntasGeneradas.Count; $i++) {
    $respuestas["$i"] = "respuesta_incorrecta_test"
}

$bodyEvaluar = @{
    preguntas = $preguntasGeneradas
    respuestas = $respuestas
    carpeta_path = $CARPETA_TEST
    es_practica = $false  # 🔥 CLAVE: Es un EXAMEN, no una práctica
} | ConvertTo-Json -Depth 10

Write-Host "   📤 POST /api/evaluar-examen" -ForegroundColor Cyan
Write-Host "      Carpeta: $CARPETA_TEST"
Write-Host "      es_practica: false 🔥" -ForegroundColor Green
Write-Host "      Respuestas: $($respuestas.Count) (todas incorrectas)"

try {
    $responseEvaluar = Invoke-RestMethod -Uri "$API_URL/api/evaluar-examen" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $bodyEvaluar `
        -TimeoutSec 30
    
    if ($responseEvaluar.success) {
        Write-Host "   ✅ Examen evaluado exitosamente" -ForegroundColor Green
        Write-Host "      Puntos: $($responseEvaluar.puntos_obtenidos)/$($responseEvaluar.puntos_totales)"
        Write-Host "      Porcentaje: $($responseEvaluar.porcentaje)%"
        
        $archivoGuardado = $responseEvaluar.archivo_guardado
        Write-Host "      📄 Archivo guardado: $archivoGuardado" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ Error: $($responseEvaluar.message)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ❌ Error al evaluar examen: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================
# PASO 3: Esperar para asegurar que el archivo se escribió
# ============================================================
Write-Host "📋 PASO 3: Esperar 3 segundos..." -ForegroundColor Yellow
Write-Host "─" * 70
Start-Sleep -Seconds 3
Write-Host "   ✅ Tiempo de espera completado" -ForegroundColor Green
Write-Host ""

# ============================================================
# PASO 4: Verificar que el archivo se guardó correctamente
# ============================================================
Write-Host "📋 PASO 4: Verificar Nomenclatura del Archivo" -ForegroundColor Yellow
Write-Host "─" * 70

$archivosExamen = Get-ChildItem $carpetaCompleta -Filter "examen_*.json" | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-1) } |
    Sort-Object LastWriteTime -Descending

$archivosPractica = Get-ChildItem $carpetaCompleta -Filter "practica_*.json" | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-1) } |
    Sort-Object LastWriteTime -Descending

Write-Host "   🔍 Archivos encontrados (último minuto):" -ForegroundColor Cyan
Write-Host "      📊 examen_*.json: $($archivosExamen.Count) archivos"
Write-Host "      📝 practica_*.json: $($archivosPractica.Count) archivos"
Write-Host ""

# ============================================================
# PASO 5: Validar contenido del archivo
# ============================================================
Write-Host "📋 PASO 5: Validar Contenido del Archivo" -ForegroundColor Yellow
Write-Host "─" * 70

if ($archivosExamen.Count -gt 0) {
    $archivoReciente = $archivosExamen[0]
    Write-Host "   📄 Archivo más reciente: $($archivoReciente.Name)" -ForegroundColor Cyan
    Write-Host "      Fecha: $($archivoReciente.LastWriteTime)"
    
    $contenido = Get-Content $archivoReciente.FullName -Raw | ConvertFrom-Json
    
    Write-Host "`n   📋 Campos del archivo:" -ForegroundColor Cyan
    Write-Host "      id: $($contenido.id)"
    Write-Host "      carpeta_ruta: $($contenido.carpeta_ruta)"
    Write-Host "      archivo: $($contenido.archivo)" -ForegroundColor Yellow
    
    if ($contenido.PSObject.Properties.Name -contains "es_practica") {
        Write-Host "      es_practica: $($contenido.es_practica)" -ForegroundColor $(if ($contenido.es_practica -eq $false) { "Green" } else { "Red" })
    } else {
        Write-Host "      es_practica: (campo no presente)" -ForegroundColor DarkGray
    }
    
    Write-Host ""
    
    # Verificaciones
    $errores = @()
    
    # 1. Verificar que el nombre del archivo es correcto (examen_*)
    if ($archivoReciente.Name -notlike "examen_*") {
        $errores += "❌ El archivo NO se guardó como 'examen_*.json' (es: $($archivoReciente.Name))"
    }
    
    # 2. Verificar que carpeta_ruta NO tiene prefijo "Practicas/"
    if ($contenido.carpeta_ruta -like "Practicas/*" -or $contenido.carpeta_ruta -like "practicas/*") {
        $errores += "❌ carpeta_ruta tiene prefijo 'Practicas/': $($contenido.carpeta_ruta)"
    }
    
    # 3. Verificar que el campo 'archivo' (si existe) también es correcto
    if ($contenido.PSObject.Properties.Name -contains "archivo") {
        if ($contenido.archivo -notlike "examen_*") {
            $errores += "❌ El campo 'archivo' NO es 'examen_*': $($contenido.archivo)"
        }
    }
    
    # 4. Verificar que NO hay archivos practica_* recientes
    if ($archivosPractica.Count -gt 0) {
        $errores += "❌ Se encontraron archivos 'practica_*.json' cuando NO debería haberlos"
    }
    
    Write-Host "=" * 70 -ForegroundColor Cyan
    if ($errores.Count -eq 0) {
        Write-Host "  ✅✅✅ TODAS LAS VERIFICACIONES PASARON ✅✅✅" -ForegroundColor Green
        Write-Host "=" * 70 -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  ✅ Nombre de archivo: examen_*.json" -ForegroundColor Green
        Write-Host "  ✅ carpeta_ruta: $($contenido.carpeta_ruta) (sin prefijo 'Practicas/')" -ForegroundColor Green
        Write-Host "  ✅ No hay archivos practica_*.json incorrectos" -ForegroundColor Green
        Write-Host ""
        Write-Host "  🎉 El bug está SOLUCIONADO - Los exámenes del dropdown se guardan correctamente" -ForegroundColor Green
    } else {
        Write-Host "  ❌❌❌ SE ENCONTRARON ERRORES ❌❌❌" -ForegroundColor Red
        Write-Host "=" * 70 -ForegroundColor Cyan
        Write-Host ""
        foreach ($error in $errores) {
            Write-Host "  $error" -ForegroundColor Red
        }
    }
} else {
    Write-Host "   ❌ No se encontró ningún archivo examen_*.json reciente" -ForegroundColor Red
    Write-Host "   ⚠️  Esto indica que el examen NO se guardó correctamente" -ForegroundColor Yellow
    
    if ($archivosPractica.Count -gt 0) {
        Write-Host ""
        Write-Host "   ⚠️  PROBLEMA: Se encontraron archivos practica_*.json:" -ForegroundColor Yellow
        foreach ($archivo in $archivosPractica) {
            Write-Host "      📝 $($archivo.Name) - $($archivo.LastWriteTime)" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "   🔥 Esto confirma el BUG: el examen se guardó como práctica" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

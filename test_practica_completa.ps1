# Script de prueba completa de práctica
Write-Host "`n" -NoNewline
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "🧪 PRUEBA COMPLETA DE PRÁCTICA" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Paso 1: Generar práctica
Write-Host "📝 Paso 1: Generando práctica con 1 pregunta..." -ForegroundColor Yellow

$docPath = "Platzi/Prueba/eeeee/ley_del_cierre__251122_140203.txt"
$body = @{
    documentos = @(
        @{ ruta = $docPath }
    )
    tipo_fuente = "documento"
    num_flashcards = 1
    tipo_flashcard = "respuesta_corta"
    prompt = "Genera una pregunta simple sobre el contenido"
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/generar_practica" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ✅ Práctica generada: $($response.preguntas.Count) preguntas`n" -ForegroundColor Green
    
    $preguntas = $response.preguntas
    $pregunta = $preguntas[0]
    
    Write-Host "   Pregunta generada:" -ForegroundColor Cyan
    Write-Host "   Tipo: $($pregunta.tipo)" -ForegroundColor Gray
    Write-Host "   Texto: $($pregunta.pregunta.Substring(0, [Math]::Min(100, $pregunta.pregunta.Length)))..." -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "   ❌ Error generando práctica: $($_.Exception.Message)`n" -ForegroundColor Red
    exit 1
}

# Paso 2: Guardar práctica
Write-Host "💾 Paso 2: Guardando práctica..." -ForegroundColor Yellow

$timestamp = [int][double]::Parse((Get-Date -UFormat %s))
$practicaId = "practica_test_$timestamp"
$carpetaRuta = "Platzi/Prueba/eeeee"

$nuevaPractica = @{
    id = $practicaId
    carpeta = $carpetaRuta
    carpeta_ruta = $carpetaRuta
    tipo = "documento"
    preguntas = $preguntas
    respuestas = @{}
    fecha = (Get-Date).ToString("o")
    completada = $false
    es_practica = $true
}

$guardarBody = @{
    practica = $nuevaPractica
    carpeta_ruta = $carpetaRuta
} | ConvertTo-Json -Depth 10

try {
    $guardarResponse = Invoke-RestMethod -Uri "http://localhost:8000/datos/practicas/guardar_individual" -Method Post -Body $guardarBody -ContentType "application/json"
    Write-Host "   ✅ Práctica guardada: $($guardarResponse.archivo)`n" -ForegroundColor Green
    $archivoNombre = $guardarResponse.archivo
} catch {
    Write-Host "   ❌ Error guardando: $($_.Exception.Message)`n" -ForegroundColor Red
    exit 1
}

# Paso 3: Responder y evaluar
Write-Host "✏️  Paso 3: Respondiendo pregunta..." -ForegroundColor Yellow

# Simular respuesta
$respuestas = @{
    "0" = "Esta es una respuesta de prueba"
}

$evaluarBody = @{
    preguntas = $preguntas
    respuestas = $respuestas
    carpeta_path = $carpetaRuta
    es_practica = $true
} | ConvertTo-Json -Depth 10

try {
    $evalResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/evaluar-examen" -Method Post -Body $evaluarBody -ContentType "application/json"
    Write-Host "   ✅ Práctica evaluada" -ForegroundColor Green
    Write-Host "   Puntos: $($evalResponse.puntos_obtenidos)/$($evalResponse.puntos_totales)" -ForegroundColor Gray
    Write-Host "   Porcentaje: $($evalResponse.porcentaje)%`n" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Error evaluando: $($_.Exception.Message)`n" -ForegroundColor Red
    exit 1
}

# Paso 4: Esperar 30 segundos
Write-Host "⏳ Paso 4: Esperando 30 segundos..." -ForegroundColor Yellow
for ($i = 30; $i -gt 0; $i--) {
    Write-Host "`r   $i segundos restantes..." -NoNewline -ForegroundColor Gray
    Start-Sleep -Seconds 1
}
Write-Host "`r   ✅ Espera completada`n" -ForegroundColor Green

# Paso 5: Verificar ubicación de archivos
Write-Host "🔍 Paso 5: Verificando ubicación de archivos..." -ForegroundColor Yellow
Write-Host ""

$practicasEncontradas = Get-ChildItem -Path "extracciones" -Filter "practica_*.json" -Recurse -File

Write-Host "   📊 Total archivos practica_*.json: $($practicasEncontradas.Count)" -ForegroundColor Cyan
Write-Host ""

foreach ($archivo in $practicasEncontradas) {
    $relativePath = $archivo.FullName.Replace((Get-Location).Path + '\extracciones\', '')
    $content = Get-Content $archivo.FullName -Raw | ConvertFrom-Json
    
    $esProblematico = $relativePath -like "*Practicas*"
    $color = if ($esProblematico) { "Red" } else { "Green" }
    $icono = if ($esProblematico) { "❌" } else { "✅" }
    
    Write-Host "   $icono $relativePath" -ForegroundColor $color
    Write-Host "      carpeta_ruta: $($content.carpeta_ruta)" -ForegroundColor Gray
    Write-Host "      tipo: $($content.tipo)" -ForegroundColor Gray
    Write-Host ""
}

# Verificar carpeta Practicas
if (Test-Path "extracciones\Practicas") {
    Write-Host "   ❌ PROBLEMA: Carpeta Practicas/ existe" -ForegroundColor Red
    $archivosPracticas = Get-ChildItem "extracciones\Practicas" -Recurse -File
    Write-Host "      Contiene $($archivosPracticas.Count) archivos" -ForegroundColor Red
} else {
    Write-Host "   ✅ CORRECTO: Carpeta Practicas/ NO existe" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "✅ PRUEBA COMPLETADA" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Script de prueba para verificar que los errores corregidos no reaparecen

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🧪 PRUEBA DE CORRECCIÓN DE ERRORES" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# 1. Buscar una práctica con error real (< 60%)
Write-Host "1️⃣ Buscando prácticas con errores..." -ForegroundColor Yellow
$practicas = Get-ChildItem "extracciones\*\resultados_practicas\*.json" -Recurse

$errorEncontrado = $null
$archivoConError = $null

foreach ($archivo in $practicas) {
    $data = Get-Content $archivo.FullName | ConvertFrom-Json
    
    foreach ($i in 0..($data.resultados.Count - 1)) {
        $resultado = $data.resultados[$i]
        $pct = ($resultado.puntos / $resultado.puntos_maximos * 100)
        
        if ($pct -lt 60 -and -not $resultado.corregido) {
            $errorEncontrado = @{
                archivo = $archivo.FullName
                indice = $i
                pregunta = $resultado.pregunta
                porcentaje = $pct
                id = $data.id
            }
            $archivoConError = $archivo.FullName
            break
        }
    }
    
    if ($errorEncontrado) { break }
}

if (-not $errorEncontrado) {
    Write-Host "❌ No se encontraron errores sin corregir (<60%)" -ForegroundColor Red
    Write-Host "   Creando un error de prueba..." -ForegroundColor Gray
    
    # Crear error de prueba modificando una pregunta existente
    $archivoTest = Get-ChildItem "extracciones\*\resultados_practicas\*.json" -Recurse | Select-Object -First 1
    $data = Get-Content $archivoTest.FullName | ConvertFrom-Json
    
    # Modificar la primera pregunta para que sea un error
    $data.resultados[0].puntos = 0
    $data.resultados[0].puntos_maximos = 10
    if ($data.resultados[0].PSObject.Properties['corregido']) {
        $data.resultados[0].corregido = $false
    }
    
    $data | ConvertTo-Json -Depth 10 | Set-Content $archivoTest.FullName -Encoding UTF8
    
    $errorEncontrado = @{
        archivo = $archivoTest.FullName
        indice = 0
        pregunta = $data.resultados[0].pregunta
        porcentaje = 0
        id = $data.id
    }
    $archivoConError = $archivoTest.FullName
    
    Write-Host "   ✅ Error de prueba creado en: $($archivoTest.Name)" -ForegroundColor Green
}

Write-Host "`n✅ Error encontrado:" -ForegroundColor Green
Write-Host "   Archivo: $([System.IO.Path]::GetFileName($errorEncontrado.archivo))" -ForegroundColor White
Write-Host "   ID: $($errorEncontrado.id)" -ForegroundColor Gray
Write-Host "   Pregunta: $($errorEncontrado.pregunta.Substring(0, [Math]::Min(60, $errorEncontrado.pregunta.Length)))..." -ForegroundColor White
Write-Host "   Porcentaje: $([math]::Round($errorEncontrado.porcentaje, 2))%" -ForegroundColor Red

# 2. Marcar como corregido
Write-Host "`n2️⃣ Marcando error como corregido..." -ForegroundColor Yellow

$data = Get-Content $archivoConError | ConvertFrom-Json
$resultado = $data.resultados[$errorEncontrado.indice]

# Agregar propiedades corregido y fechaCorreccion
$resultado | Add-Member -NotePropertyName "corregido" -NotePropertyValue $true -Force
$resultado | Add-Member -NotePropertyName "fechaCorreccion" -NotePropertyValue (Get-Date).ToString("o") -Force

# Guardar
$data | ConvertTo-Json -Depth 10 | Set-Content $archivoConError -Encoding UTF8

Write-Host "   ✅ Marcado como corregido en archivo JSON" -ForegroundColor Green
Write-Host "   📅 Fecha de corrección: $($resultado.fechaCorreccion)" -ForegroundColor Gray

# 3. Verificar con el backend (si está corriendo)
Write-Host "`n3️⃣ Verificando con backend..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/datos/practicas" -Method Get -TimeoutSec 3 -ErrorAction Stop
    
    Write-Host "   ✅ Backend respondió: $($response.Count) prácticas cargadas" -ForegroundColor Green
    
    # Buscar la práctica específica
    $practica = $response | Where-Object { $_.id -eq $errorEncontrado.id }
    
    if ($practica) {
        $preguntaCorregida = $practica.resultados[$errorEncontrado.indice]
        
        Write-Host "`n   📄 Práctica encontrada en backend:" -ForegroundColor Cyan
        Write-Host "      Pregunta: $($preguntaCorregida.pregunta.Substring(0, [Math]::Min(50, $preguntaCorregida.pregunta.Length)))..." -ForegroundColor White
        Write-Host "      Puntos: $($preguntaCorregida.puntos)/$($preguntaCorregida.puntos_maximos)" -ForegroundColor Yellow
        Write-Host "      Corregido: $($preguntaCorregida.corregido)" -ForegroundColor $(if ($preguntaCorregida.corregido) { "Green" } else { "Red" })
        
        if ($preguntaCorregida.corregido) {
            Write-Host "`n   ✅ ¡ÉXITO! El backend carga el flag 'corregido: true'" -ForegroundColor Green
        } else {
            Write-Host "`n   ❌ ERROR: El backend NO muestra corregido=true" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️ Práctica no encontrada en respuesta del backend" -ForegroundColor Yellow
        Write-Host "   IDs disponibles: $($response.id -join ', ')" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "   ⚠️ Backend no está corriendo o no responde" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Gray
    Write-Host "`n   💡 Para probar con el backend:" -ForegroundColor Cyan
    Write-Host "      1. Abre otra terminal PowerShell" -ForegroundColor Gray
    Write-Host "      2. cd C:\Users\Fela\Documents\Proyectos\Examinator" -ForegroundColor Gray
    Write-Host "      3. python api_server.py" -ForegroundColor Gray
    Write-Host "      4. Ejecuta este script de nuevo" -ForegroundColor Gray
}

# 4. Resumen final
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE LA PRUEBA" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Archivo modificado: $([System.IO.Path]::GetFileName($archivoConError))" -ForegroundColor Green
Write-Host "✅ Campo 'corregido' establecido a: true" -ForegroundColor Green
Write-Host "✅ Campo 'fechaCorreccion' agregado" -ForegroundColor Green
Write-Host "Proximo paso: Iniciar una sesion en el navegador" -ForegroundColor Cyan
Write-Host "   y verificar que esta pregunta NO aparece en" -ForegroundColor Gray
Write-Host "   la fase de Corrigiendo Errores Clave" -ForegroundColor Gray
Write-Host "`n   Revisa la consola del navegador (F12) para ver logs" -ForegroundColor Yellow
Write-Host "============================================`n" -ForegroundColor Cyan

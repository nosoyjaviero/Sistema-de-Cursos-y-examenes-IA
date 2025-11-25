# Script de prueba completa - Simula el frontend
Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "🧪 PRUEBA COMPLETA - Simulando Frontend" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

# Simular exactamente lo que envía el frontend
$frontendBody = @{
    prompt = @"
Genera una práctica educativa basada en el contenido proporcionado.

INSTRUCCIONES PERSONALIZADAS:
Test de flashcards de programación

TIPOS DE PREGUNTAS A GENERAR:

**3 Flashcards (RESPUESTA CORTA)** - Formato JSON
"@
    ruta = $null
    tipo_flashcard = "respuesta_corta"
    num_flashcards = 3
    num_mcq = 0
    num_verdadero_falso = 0
    num_cloze = 0
    num_respuesta_corta = 0
    num_open_question = 0
    num_caso_estudio = 0
    num_reading_comprehension = 0
    num_reading_true_false = 0
    num_reading_cloze = 0
    num_reading_skill = 0
    num_reading_matching = 0
    num_reading_sequence = 0
    num_writing_short = 0
    num_writing_paraphrase = 0
    num_writing_correction = 0
    num_writing_transformation = 0
    num_writing_essay = 0
    num_writing_sentence_builder = 0
    num_writing_picture_description = 0
    num_writing_email = 0
} | ConvertTo-Json -Depth 10

Write-Host "`n📤 Enviando solicitud POST (simulando frontend)..." -ForegroundColor Yellow
Write-Host "   URL: http://localhost:8000/api/generar_practica" -ForegroundColor Gray
Write-Host "   Content-Type: application/json" -ForegroundColor Gray
Write-Host "   Body: num_flashcards=3, tipo=respuesta_corta`n" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/generar_practica" `
                                   -Method POST `
                                   -Body $frontendBody `
                                   -ContentType "application/json" `
                                   -TimeoutSec 120 `
                                   -Verbose
    
    Write-Host "`n✅ ÉXITO - El endpoint respondió correctamente!" -ForegroundColor Green
    Write-Host "`n📊 Datos de respuesta:" -ForegroundColor Cyan
    Write-Host "   ├─ success: $($response.success)" -ForegroundColor White
    Write-Host "   ├─ session_id: $($response.session_id)" -ForegroundColor White
    Write-Host "   ├─ total_preguntas: $($response.total_preguntas)" -ForegroundColor White
    Write-Host "   └─ preguntas (array): $($response.preguntas.Count) elementos" -ForegroundColor White
    
    if ($response.preguntas -and $response.preguntas.Count -gt 0) {
        Write-Host "`n📝 Detalles de las preguntas:" -ForegroundColor Cyan
        foreach ($i in 0..([Math]::Min(2, $response.preguntas.Count - 1))) {
            $p = $response.preguntas[$i]
            Write-Host "`n   Pregunta $($i + 1):" -ForegroundColor Yellow
            Write-Host "   ├─ tipo: $($p.tipo)" -ForegroundColor Gray
            Write-Host "   ├─ pregunta: $($p.pregunta.Substring(0, [Math]::Min(70, $p.pregunta.Length)))..." -ForegroundColor Gray
            Write-Host "   ├─ puntos: $($p.puntos)" -ForegroundColor Gray
            if ($p.opciones) {
                Write-Host "   └─ opciones: $($p.opciones.Count) opciones" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host "`n=====================================================" -ForegroundColor Green
    Write-Host "✅ ENDPOINT FUNCIONAL - Frontend debería funcionar" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
    
    Write-Host "`n💡 INSTRUCCIONES PARA EL FRONTEND:" -ForegroundColor Yellow
    Write-Host "   1. Abre la aplicación web en el navegador" -ForegroundColor White
    Write-Host "   2. Presiona Ctrl+Shift+R para limpiar caché" -ForegroundColor White
    Write-Host "   3. Intenta generar una práctica" -ForegroundColor White
    Write-Host "   4. Si sigue fallando, revisa la consola del navegador (F12)`n" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ ERROR - Falló la solicitud" -ForegroundColor Red
    Write-Host "   Mensaje: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "   Status Code: $statusCode" -ForegroundColor Red
        
        if ($statusCode -eq 404) {
            Write-Host "`n⚠️  ERROR 404 - El endpoint no existe" -ForegroundColor Yellow
            Write-Host "   Posibles causas:" -ForegroundColor White
            Write-Host "   1. El servidor no se reinició después de agregar el endpoint" -ForegroundColor White
            Write-Host "   2. El servidor está corriendo una versión antigua del código" -ForegroundColor White
            Write-Host "   3. Hay un error de tipeo en la URL" -ForegroundColor White
        }
        
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $reader.BaseStream.Position = 0
            $reader.DiscardBufferedData()
            $responseBody = $reader.ReadToEnd()
            Write-Host "   Detalle del servidor: $responseBody" -ForegroundColor Red
        } catch {}
    }
    
    Write-Host "`n=====================================================" -ForegroundColor Red
    Write-Host "❌ PRUEBA FALLIDA" -ForegroundColor Red
    Write-Host "=====================================================" -ForegroundColor Red
}

Write-Host "`n"

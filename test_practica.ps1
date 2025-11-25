# Script de prueba para el endpoint generar_practica
Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "🧪 PRUEBA DEL ENDPOINT /api/generar_practica" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Datos de prueba mínimos
$body = @{
    prompt = "Genera 2 flashcards sobre programación en Python"
    num_flashcards = 2
    tipo_flashcard = "respuesta_corta"
} | ConvertTo-Json

Write-Host "`n📤 Enviando solicitud POST a http://localhost:8000/api/generar_practica..." -ForegroundColor Yellow
Write-Host "   Datos: num_flashcards=2, tipo=respuesta_corta`n" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/generar_practica" `
                                   -Method POST `
                                   -Body $body `
                                   -ContentType "application/json" `
                                   -TimeoutSec 120
    
    Write-Host "✅ ÉXITO - El endpoint funciona correctamente!" -ForegroundColor Green
    Write-Host "`n📊 Respuesta recibida:" -ForegroundColor Cyan
    Write-Host "   ├─ Success: $($response.success)" -ForegroundColor White
    Write-Host "   ├─ Session ID: $($response.session_id)" -ForegroundColor White
    Write-Host "   ├─ Total preguntas: $($response.total_preguntas)" -ForegroundColor White
    Write-Host "   └─ Preguntas generadas:" -ForegroundColor White
    
    foreach ($i in 0..($response.preguntas.Count - 1)) {
        $pregunta = $response.preguntas[$i]
        Write-Host "`n      Pregunta $($i+1):" -ForegroundColor Yellow
        Write-Host "      ├─ Tipo: $($pregunta.tipo)" -ForegroundColor Gray
        Write-Host "      ├─ Pregunta: $($pregunta.pregunta.Substring(0, [Math]::Min(60, $pregunta.pregunta.Length)))..." -ForegroundColor Gray
        Write-Host "      └─ Puntos: $($pregunta.puntos)" -ForegroundColor Gray
    }
    
    Write-Host "`n==================================================" -ForegroundColor Green
    Write-Host "✅ PRUEBA EXITOSA - Endpoint completamente funcional" -ForegroundColor Green
    Write-Host "==================================================`n" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ ERROR - El endpoint falló" -ForegroundColor Red
    Write-Host "   Tipo de error: $($_.Exception.GetType().Name)" -ForegroundColor Red
    Write-Host "   Mensaje: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "   Status Code: $statusCode" -ForegroundColor Red
        
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $reader.BaseStream.Position = 0
            $reader.DiscardBufferedData()
            $responseBody = $reader.ReadToEnd()
            Write-Host "   Detalle: $responseBody" -ForegroundColor Red
        } catch {
            Write-Host "   No se pudo leer el cuerpo de la respuesta" -ForegroundColor Red
        }
    }
    
    Write-Host "`n==================================================" -ForegroundColor Red
    Write-Host "❌ PRUEBA FALLIDA" -ForegroundColor Red
    Write-Host "==================================================`n" -ForegroundColor Red
}

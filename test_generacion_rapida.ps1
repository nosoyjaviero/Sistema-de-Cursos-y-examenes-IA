# Test rápido de generación de examen
Write-Host "`n🧪 TEST DE GENERACIÓN DE EXAMEN`n" -ForegroundColor Cyan

$body = @{
    contenido = "El diseño es un proceso que busca resolver problemas de comunicación visual. El diseño gráfico se enfoca en la creación de mensajes visuales efectivos."
    num_multiple = 1
    num_verdadero_falso = 0
    num_corta = 0
    num_desarrollo = 0
    session_id = "test_$(Get-Date -Format 'yyyyMMddHHmmss')"
} | ConvertTo-Json

Write-Host "📤 Enviando request..." -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/generar-examen" -Method POST -Body $body -ContentType "application/json"

Write-Host "`n✅ RESPUESTA RECIBIDA:`n" -ForegroundColor Green
$response | ConvertTo-Json -Depth 10

if ($response.total_preguntas -gt 0) {
    Write-Host "`n✅ ¡ÉXITO! Se generaron $($response.total_preguntas) preguntas" -ForegroundColor Green
    Write-Host "   Pregunta 1:" -ForegroundColor Cyan
    Write-Host "   $($response.preguntas[0].pregunta)" -ForegroundColor White
} else {
    Write-Host "`n❌ FALLO: No se generaron preguntas" -ForegroundColor Red
    Write-Host "   Revisa los logs del servidor para más detalles" -ForegroundColor Yellow
}

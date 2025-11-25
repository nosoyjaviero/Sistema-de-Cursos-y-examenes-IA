# Script para probar la generación de prácticas

# Esperar a que el servidor esté listo
Write-Host "Esperando que el servidor esté listo..."
Start-Sleep 3

# Datos de prueba para generar una práctica
$requestBody = @{
    ruta = ""
    prompt = "Crea una práctica simple sobre matemáticas básicas"
    num_flashcards = 0
    num_mcq = 2
    num_verdadero_falso = 2
    num_cloze = 0
    num_respuesta_corta = 0
    num_open_question = 0
    num_caso_estudio = 0
} | ConvertTo-Json

Write-Host "Enviando solicitud de generación de práctica..."
Write-Host "Body: $requestBody"

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/generar_practica" `
        -Method POST `
        -Headers @{'Content-Type' = 'application/json'} `
        -Body $requestBody `
        -UseBasicParsing `
        -TimeoutSec 30

    Write-Host "✅ Respuesta del servidor:"
    Write-Host $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "❌ Error: $_"
    Write-Host $_.Exception.Response
}

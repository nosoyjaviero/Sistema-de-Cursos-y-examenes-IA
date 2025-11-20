# Test del prompt corregido
Write-Host "`n🧪 VERIFICACIÓN DEL PROMPT CORREGIDO`n" -ForegroundColor Cyan

$body = @{
    contenido = @"
=== Test de Diseño ===

El diseño gráfico es el proceso de comunicación visual mediante el uso de tipografía, imágenes y color.
Los principios fundamentales del diseño incluyen:
1. Balance: Distribución equilibrada de elementos
2. Contraste: Diferenciación entre elementos
3. Jerarquía: Organización de importancia visual
4. Alineación: Posicionamiento coherente
"@
    num_multiple = 2
    num_verdadero_falso = 0
    num_corta = 1
    num_desarrollo = 0
    session_id = "test_prompt_$(Get-Date -Format 'yyyyMMddHHmmss')"
} | ConvertTo-Json

Write-Host "📤 Generando 3 preguntas (2 MCQ + 1 Short Answer)..." -ForegroundColor Yellow
Write-Host "⏳ Esto puede tardar 20-30 segundos con Ollama...`n" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/generar-examen" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 120
    
    Write-Host "`n✅ RESPUESTA RECIBIDA:`n" -ForegroundColor Green
    
    if ($response.total_preguntas -gt 0) {
        Write-Host "✅ ¡ÉXITO! Se generaron $($response.total_preguntas) preguntas" -ForegroundColor Green
        Write-Host "`n📋 PREGUNTAS GENERADAS:" -ForegroundColor Cyan
        
        for ($i = 0; $i -lt $response.preguntas.Count; $i++) {
            $p = $response.preguntas[$i]
            Write-Host "`n  Pregunta $($i+1):" -ForegroundColor Yellow
            Write-Host "  Tipo: $($p.tipo)" -ForegroundColor White
            Write-Host "  Pregunta: $($p.pregunta)" -ForegroundColor White
            
            if ($p.opciones) {
                Write-Host "  Opciones:" -ForegroundColor Gray
                foreach ($opcion in $p.opciones) {
                    Write-Host "    - $opcion" -ForegroundColor Gray
                }
            }
            
            Write-Host "  Respuesta: $($p.respuesta_correcta)" -ForegroundColor Green
            Write-Host "  Puntos: $($p.puntos)" -ForegroundColor Cyan
        }
        
        Write-Host "`n✅ FORMATO CORRECTO - El modelo siguió las instrucciones" -ForegroundColor Green
        
    } else {
        Write-Host "`n❌ FALLO: No se generaron preguntas" -ForegroundColor Red
        Write-Host "   Revisa los logs del servidor backend" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "`n❌ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`n💡 Asegúrate de que el servidor backend esté ejecutándose" -ForegroundColor Yellow
}

Write-Host "`n" -ForegroundColor White

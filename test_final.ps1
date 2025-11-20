# Test Final - Generación de Exámenes
Write-Host "`n╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🧪 TEST FINAL DE GENERACIÓN DE EXÁMENES              ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$contenido = @"
=== Fundamentos de Programación ===

La programación es el proceso de crear un conjunto de instrucciones que le dicen a una computadora cómo realizar una tarea.

Los lenguajes de programación se dividen en dos categorías principales:
1. Lenguajes compilados: El código se traduce completamente a lenguaje máquina antes de ejecutarse (C, C++, Go)
2. Lenguajes interpretados: El código se ejecuta línea por línea (Python, JavaScript, Ruby)

Variables: Son contenedores que almacenan información que puede cambiar durante la ejecución del programa.
Funciones: Bloques de código reutilizables que realizan una tarea específica.
Estructuras de control: Permiten controlar el flujo de ejecución (if, for, while).
"@

Write-Host "📊 Configuración del test:" -ForegroundColor Yellow
Write-Host "   • 2 Preguntas MCQ" -ForegroundColor White
Write-Host "   • 1 Pregunta Corta" -ForegroundColor White
Write-Host "   • 1 Pregunta de Desarrollo`n" -ForegroundColor White

$body = @{
    contenido = $contenido
    num_multiple = 2
    num_corta = 1
    num_desarrollo = 1
    num_verdadero_falso = 0
    session_id = "test_final_$(Get-Date -Format 'yyyyMMddHHmmss')"
} | ConvertTo-Json

Write-Host "🚀 Enviando request al servidor..." -ForegroundColor Yellow
Write-Host "⏳ Esperando respuesta (puede tardar 30-60 segundos)...`n" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/generar-examen" `
        -Method POST `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 180
    
    Write-Host "✅ RESPUESTA RECIBIDA`n" -ForegroundColor Green
    
    if ($response.success -and $response.total_preguntas -gt 0) {
        Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║  ✅ ¡ÉXITO! EXAMEN GENERADO CORRECTAMENTE             ║" -ForegroundColor Green
        Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Green
        
        Write-Host "📊 RESUMEN:" -ForegroundColor Cyan
        Write-Host "   Total de preguntas: $($response.total_preguntas)" -ForegroundColor White
        Write-Host "   Puntos totales: $($response.puntos_totales)`n" -ForegroundColor White
        
        Write-Host "📋 PREGUNTAS GENERADAS:`n" -ForegroundColor Cyan
        
        for ($i = 0; $i -lt $response.preguntas.Count; $i++) {
            $p = $response.preguntas[$i]
            
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
            Write-Host "Pregunta $($i+1) de $($response.preguntas.Count)" -ForegroundColor Yellow
            Write-Host "Tipo: $($p.tipo) | Puntos: $($p.puntos)" -ForegroundColor Gray
            Write-Host ""
            Write-Host "❓ $($p.pregunta)" -ForegroundColor White
            Write-Host ""
            
            if ($p.opciones -and $p.opciones.Count -gt 0) {
                Write-Host "Opciones:" -ForegroundColor Cyan
                foreach ($opcion in $p.opciones) {
                    Write-Host "  $opcion" -ForegroundColor Gray
                }
                Write-Host ""
                Write-Host "✅ Respuesta correcta: $($p.respuesta_correcta)" -ForegroundColor Green
            } else {
                Write-Host "💡 Respuesta esperada:" -ForegroundColor Cyan
                Write-Host "   $($p.respuesta_correcta)" -ForegroundColor Gray
            }
            Write-Host ""
        }
        
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray
        
        # Validaciones
        Write-Host "🔍 VALIDACIONES:" -ForegroundColor Cyan
        $errores = @()
        
        # Validar que cada pregunta tenga los campos requeridos
        foreach ($p in $response.preguntas) {
            if (-not $p.tipo) { $errores += "Pregunta sin campo 'tipo'" }
            if (-not $p.pregunta) { $errores += "Pregunta sin campo 'pregunta'" }
            if (-not $p.respuesta_correcta) { $errores += "Pregunta sin 'respuesta_correcta'" }
            if (-not $p.puntos) { $errores += "Pregunta sin campo 'puntos'" }
            
            # Validar MCQ tiene opciones
            if ($p.tipo -eq "mcq" -and (-not $p.opciones -or $p.opciones.Count -eq 0)) {
                $errores += "Pregunta MCQ sin opciones"
            }
            
            # Validar que no tenga placeholders
            if ($p.pregunta -match '\.\.\.' -or $p.pregunta -match '\[\.\.\.\]') {
                $errores += "Pregunta contiene placeholders (...)"
            }
        }
        
        if ($errores.Count -eq 0) {
            Write-Host "   ✅ Todas las preguntas tienen formato correcto" -ForegroundColor Green
            Write-Host "   ✅ No se detectaron placeholders" -ForegroundColor Green
            Write-Host "   ✅ Campos requeridos presentes" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ Errores encontrados:" -ForegroundColor Yellow
            foreach ($error in $errores) {
                Write-Host "      - $error" -ForegroundColor Red
            }
        }
        
        Write-Host "`n╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║  🎉 TEST COMPLETADO EXITOSAMENTE                      ║" -ForegroundColor Green
        Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Green
        
    } else {
        Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Red
        Write-Host "║  ❌ FALLO - NO SE GENERARON PREGUNTAS                 ║" -ForegroundColor Red
        Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Red
        
        Write-Host "📊 Respuesta del servidor:" -ForegroundColor Yellow
        $response | ConvertTo-Json -Depth 5
        
        Write-Host "`n💡 RECOMENDACIONES:" -ForegroundColor Cyan
        Write-Host "   1. Revisa los logs del servidor backend" -ForegroundColor White
        Write-Host "   2. Busca errores de parsing de JSON" -ForegroundColor White
        Write-Host "   3. Verifica que el modelo esté generando datos reales (no placeholders)" -ForegroundColor White
        Write-Host "   4. Prueba con un modelo más grande si llama32 falla" -ForegroundColor White
    }
    
} catch {
    Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║  ❌ ERROR DE CONEXIÓN                                 ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Red
    
    Write-Host "Error: $($_.Exception.Message)`n" -ForegroundColor Red
    
    Write-Host "💡 SOLUCIONES:" -ForegroundColor Cyan
    Write-Host "   1. Verifica que el servidor backend esté corriendo:" -ForegroundColor White
    Write-Host "      python api_server.py" -ForegroundColor Gray
    Write-Host "   2. Asegúrate de que esté en el puerto 8000" -ForegroundColor White
    Write-Host "   3. Revisa que Ollama esté corriendo:" -ForegroundColor White
    Write-Host "      ollama list" -ForegroundColor Gray
}

Write-Host ""

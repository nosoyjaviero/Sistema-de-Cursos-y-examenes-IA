# ========================================
# TEST MANUAL: Examen desde Dropdown
# ========================================
# Instrucciones para probar manualmente el fix

Write-Host "`n" -NoNewline
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  TEST MANUAL: Verificar Fix de Nomenclatura de Exámenes" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 INSTRUCCIONES:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Abre la aplicación web (http://localhost:3000)" -ForegroundColor White
Write-Host ""
Write-Host "2. Ve a la carpeta: Platzi > Prueba > eeeee" -ForegroundColor White
Write-Host ""
Write-Host "3. Haz clic en uno de los botones del dropdown:" -ForegroundColor White
Write-Host "   - 🎓 CURSO" -ForegroundColor Cyan
Write-Host "   - 📚 CAPÍTULO" -ForegroundColor Cyan
Write-Host "   - 📖 CLASE" -ForegroundColor Cyan
Write-Host "   - 📝 LECCIÓN" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Genera un examen de 2 preguntas" -ForegroundColor White
Write-Host ""
Write-Host "5. Responde las preguntas (cualquier respuesta)" -ForegroundColor White
Write-Host ""
Write-Host "6. Finaliza el examen" -ForegroundColor White
Write-Host ""
Write-Host "7. Presiona ENTER cuando hayas completado estos pasos..." -ForegroundColor Yellow
$null = Read-Host

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  VERIFICANDO RESULTADOS..." -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

$carpetaTest = "extracciones\Platzi\Prueba\eeeee"

# Buscar archivos recientes (últimos 2 minutos)
$archivosExamen = Get-ChildItem $carpetaTest -Filter "examen_*.json" -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-2) } |
    Sort-Object LastWriteTime -Descending

$archivosPractica = Get-ChildItem $carpetaTest -Filter "practica_*.json" -ErrorAction SilentlyContinue | 
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-2) } |
    Sort-Object LastWriteTime -Descending

Write-Host "📊 ARCHIVOS ENCONTRADOS (últimos 2 minutos):" -ForegroundColor Cyan
Write-Host ""
Write-Host "   📄 examen_*.json: $($archivosExamen.Count) archivos" -ForegroundColor $(if ($archivosExamen.Count -gt 0) { "Green" } else { "Red" })
if ($archivosExamen.Count -gt 0) {
    foreach ($archivo in $archivosExamen) {
        Write-Host "      ✅ $($archivo.Name) - $($archivo.LastWriteTime)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "   📝 practica_*.json: $($archivosPractica.Count) archivos" -ForegroundColor $(if ($archivosPractica.Count -eq 0) { "Green" } else { "Red" })
if ($archivosPractica.Count -gt 0) {
    foreach ($archivo in $archivosPractica) {
        Write-Host "      ❌ $($archivo.Name) - $($archivo.LastWriteTime)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan

if ($archivosExamen.Count -gt 0) {
    $archivoReciente = $archivosExamen[0]
    Write-Host "📋 ANALIZANDO ARCHIVO MÁS RECIENTE:" -ForegroundColor Cyan
    Write-Host "   $($archivoReciente.Name)" -ForegroundColor Yellow
    Write-Host ""
    
    $contenido = Get-Content $archivoReciente.FullName -Raw | ConvertFrom-Json
    
    Write-Host "   📌 Campos importantes:" -ForegroundColor Cyan
    Write-Host "      id: $($contenido.id)"
    Write-Host "      carpeta_ruta: $($contenido.carpeta_ruta)" -ForegroundColor $(if ($contenido.carpeta_ruta -notlike "*Practicas*") { "Green" } else { "Red" })
    
    if ($contenido.PSObject.Properties.Name -contains "archivo") {
        Write-Host "      archivo: $($contenido.archivo)" -ForegroundColor $(if ($contenido.archivo -like "examen_*") { "Green" } else { "Red" })
    }
    
    if ($contenido.PSObject.Properties.Name -contains "es_practica") {
        Write-Host "      es_practica: $($contenido.es_practica)" -ForegroundColor $(if ($contenido.es_practica -eq $false) { "Green" } else { "Red" })
    }
    
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor Cyan
    
    # Verificaciones
    $todoOk = $true
    
    if ($archivoReciente.Name -notlike "examen_*") {
        Write-Host "   ❌ ERROR: El archivo NO se guardó como 'examen_*.json'" -ForegroundColor Red
        $todoOk = $false
    } else {
        Write-Host "   ✅ OK: Archivo guardado como 'examen_*.json'" -ForegroundColor Green
    }
    
    if ($contenido.carpeta_ruta -like "*Practicas*" -or $contenido.carpeta_ruta -like "*practicas*") {
        Write-Host "   ❌ ERROR: carpeta_ruta contiene 'Practicas/'" -ForegroundColor Red
        $todoOk = $false
    } else {
        Write-Host "   ✅ OK: carpeta_ruta sin prefijo 'Practicas/'" -ForegroundColor Green
    }
    
    if ($contenido.PSObject.Properties.Name -contains "archivo") {
        if ($contenido.archivo -notlike "examen_*") {
            Write-Host "   ❌ ERROR: Campo 'archivo' NO es 'examen_*'" -ForegroundColor Red
            $todoOk = $false
        } else {
            Write-Host "   ✅ OK: Campo 'archivo' es 'examen_*'" -ForegroundColor Green
        }
    }
    
    if ($archivosPractica.Count -gt 0) {
        Write-Host "   ❌ ERROR: Se encontraron archivos 'practica_*.json' incorrectos" -ForegroundColor Red
        $todoOk = $false
    } else {
        Write-Host "   ✅ OK: No hay archivos 'practica_*.json' incorrectos" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "=" * 70 -ForegroundColor Cyan
    
    if ($todoOk) {
        Write-Host "  🎉🎉🎉 ¡TODO CORRECTO! EL BUG ESTÁ SOLUCIONADO 🎉🎉🎉" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️⚠️⚠️ SE ENCONTRARON PROBLEMAS ⚠️⚠️⚠️" -ForegroundColor Red
    }
    
} else {
    Write-Host "   ❌ No se encontró ningún archivo 'examen_*.json' reciente" -ForegroundColor Red
    Write-Host "   ⚠️  Asegúrate de haber completado el examen correctamente" -ForegroundColor Yellow
    
    if ($archivosPractica.Count -gt 0) {
        Write-Host ""
        Write-Host "   🔥 PROBLEMA DETECTADO: El examen se guardó como 'practica_*.json'" -ForegroundColor Red
        Write-Host "   🔥 Esto indica que el bug AÚN EXISTE" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

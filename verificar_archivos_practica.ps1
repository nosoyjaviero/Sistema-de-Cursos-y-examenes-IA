# ========================================
# TEST: Verificar Archivos Existentes
# ========================================

$carpetaTest = "extracciones\Platzi\Prueba\eeeee"

Write-Host "`n" -NoNewline
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  ANÁLISIS: Archivos practica_*.json Existentes" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

Write-Host "📁 Carpeta: $carpetaTest" -ForegroundColor Cyan
Write-Host ""

# Obtener todos los archivos practica_*.json
$archivosPractica = Get-ChildItem $carpetaTest -Filter "practica_*.json" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending

Write-Host "📊 Total de archivos practica_*.json: $($archivosPractica.Count)" -ForegroundColor Yellow
Write-Host ""

if ($archivosPractica.Count -eq 0) {
    Write-Host "   ✅ No hay archivos practica_*.json en la carpeta" -ForegroundColor Green
    Write-Host ""
    exit 0
}

# Analizar cada archivo
Write-Host "🔍 Analizando cada archivo..." -ForegroundColor Cyan
Write-Host ""

$practicasReales = 0
$examenesIncorrectos = 0

foreach ($archivo in $archivosPractica) {
    $contenido = Get-Content $archivo.FullName -Raw | ConvertFrom-Json
    
    Write-Host "━" * 70 -ForegroundColor DarkGray
    Write-Host "📄 $($archivo.Name)" -ForegroundColor Yellow
    Write-Host "   Fecha: $($archivo.LastWriteTime)"
    
    # Verificar el campo 'archivo' para determinar el tipo original
    $esExamenIncorrecto = $false
    
    if ($contenido.PSObject.Properties.Name -contains "archivo") {
        Write-Host "   archivo: $($contenido.archivo)" -ForegroundColor Cyan
        
        if ($contenido.archivo -like "examen_*") {
            Write-Host "   🔥 PROBLEMA: Este es un EXAMEN guardado incorrectamente como práctica" -ForegroundColor Red
            $esExamenIncorrecto = $true
            $examenesIncorrectos++
        } else {
            Write-Host "   ✅ Es una práctica legítima" -ForegroundColor Green
            $practicasReales++
        }
    } else {
        # Si no tiene el campo 'archivo', verificar otros indicadores
        if ($contenido.PSObject.Properties.Name -contains "es_practica") {
            if ($contenido.es_practica -eq $true) {
                Write-Host "   ✅ es_practica: true (práctica legítima)" -ForegroundColor Green
                $practicasReales++
            } else {
                Write-Host "   🔥 es_practica: false (EXAMEN guardado incorrectamente)" -ForegroundColor Red
                $esExamenIncorrecto = $true
                $examenesIncorrectos++
            }
        } else {
            # Sin indicadores claros
            Write-Host "   ⚠️  Sin indicadores claros (asumir práctica)" -ForegroundColor Yellow
            $practicasReales++
        }
    }
    
    Write-Host "   carpeta_ruta: $($contenido.carpeta_ruta)" -ForegroundColor Gray
    Write-Host "   id: $($contenido.id)" -ForegroundColor Gray
    
    if ($contenido.PSObject.Properties.Name -contains "tipo") {
        Write-Host "   tipo: $($contenido.tipo)" -ForegroundColor Gray
    }
    
    Write-Host ""
}

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "📊 RESUMEN:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   ✅ Prácticas legítimas: $practicasReales" -ForegroundColor Green
Write-Host "   ❌ Exámenes incorrectos: $examenesIncorrectos" -ForegroundColor $(if ($examenesIncorrectos -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($examenesIncorrectos -gt 0) {
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host "  ⚠️  SE ENCONTRARON EXÁMENES GUARDADOS INCORRECTAMENTE" -ForegroundColor Red
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host ""
    Write-Host "  Estos archivos deberían llamarse 'examen_*.json' en lugar de 'practica_*.json'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Para verificar el fix:" -ForegroundColor Cyan
    Write-Host "  1. Genera un nuevo examen desde el dropdown (🎓 CURSO, 📚 CAPÍTULO, etc.)" -ForegroundColor White
    Write-Host "  2. Complétalo" -ForegroundColor White
    Write-Host "  3. Ejecuta este script nuevamente" -ForegroundColor White
    Write-Host "  4. El nuevo archivo debería ser 'examen_*.json', no 'practica_*.json'" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host "  ✅ TODOS LOS ARCHIVOS SON PRÁCTICAS LEGÍTIMAS" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host ""
}

Write-Host ""

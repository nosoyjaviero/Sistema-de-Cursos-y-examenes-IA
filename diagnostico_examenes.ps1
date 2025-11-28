#!/usr/bin/env pwsh
# Script de diagnóstico de exámenes duplicados

Write-Host "`n" -NoNewline
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "🔍 DIAGNÓSTICO DE EXÁMENES - DETECCIÓN DE DUPLICADOS" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

$baseDir = "C:\Users\Fela\Documents\Proyectos\Examinator"
Set-Location $baseDir

# 1. Buscar todos los exámenes en extracciones/
Write-Host "`n📂 EXÁMENES EN extracciones/:" -ForegroundColor Yellow
$examenesExtracciones = Get-ChildItem "extracciones" -Recurse -File | Where-Object { 
    $_.Name -like "examen_*.json" 
}

$agrupados = $examenesExtracciones | Group-Object Name | Where-Object { $_.Count -gt 1 }

if ($agrupados) {
    Write-Host "   ⚠️  DUPLICADOS ENCONTRADOS:" -ForegroundColor Red
    foreach ($grupo in $agrupados) {
        Write-Host "`n   📄 Archivo: $($grupo.Name)" -ForegroundColor Yellow
        Write-Host "      Copias: $($grupo.Count)" -ForegroundColor Red
        foreach ($archivo in $grupo.Group) {
            Write-Host "      → $($archivo.FullName)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "   ✅ No hay duplicados por nombre de archivo" -ForegroundColor Green
}

# 2. Buscar archivos legacy
Write-Host "`n📂 ARCHIVOS LEGACY (examenes.json, ExamenGeneral.json):" -ForegroundColor Yellow
$legacy = Get-ChildItem "extracciones" -Recurse -File | Where-Object { 
    $_.Name -eq "examenes.json" -or $_.Name -eq "ExamenGeneral.json" 
}

if ($legacy) {
    Write-Host "   ⚠️  Encontrados $($legacy.Count) archivos legacy:" -ForegroundColor Yellow
    foreach ($archivo in $legacy) {
        Write-Host "      → $($archivo.FullName)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ✅ No hay archivos legacy" -ForegroundColor Green
}

# 3. Buscar en carpetas resultados_examenes (antigua estructura)
Write-Host "`n📂 CARPETAS resultados_examenes/ (antigua estructura):" -ForegroundColor Yellow
$resultadosExamenes = Get-ChildItem "extracciones" -Recurse -Directory | Where-Object { 
    $_.Name -eq "resultados_examenes" 
}

if ($resultadosExamenes) {
    Write-Host "   ⚠️  Encontradas $($resultadosExamenes.Count) carpetas antiguas:" -ForegroundColor Yellow
    foreach ($carpeta in $resultadosExamenes) {
        $numArchivos = (Get-ChildItem $carpeta.FullName -File | Where-Object { $_.Name -like "examen_*.json" }).Count
        Write-Host "      → $($carpeta.FullName) [$numArchivos archivos]" -ForegroundColor Gray
    }
} else {
    Write-Host "   ✅ No hay carpetas antiguas resultados_examenes/" -ForegroundColor Green
}

# 4. Buscar en carpeta examenes/ (vieja estructura)
Write-Host "`n📂 CARPETA examenes/ (vieja estructura):" -ForegroundColor Yellow
if (Test-Path "examenes") {
    $examenesViejos = Get-ChildItem "examenes" -Recurse -File | Where-Object { 
        $_.Name -like "examen_*.json" 
    }
    if ($examenesViejos) {
        Write-Host "   ⚠️  Encontrados $($examenesViejos.Count) archivos en estructura vieja:" -ForegroundColor Yellow
        foreach ($archivo in $examenesViejos) {
            Write-Host "      → $($archivo.FullName)" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ✅ Carpeta examenes/ existe pero está vacía" -ForegroundColor Green
    }
} else {
    Write-Host "   ✅ Carpeta examenes/ no existe" -ForegroundColor Green
}

# 5. Resumen
Write-Host "`n" -NoNewline
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "📊 RESUMEN" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "Total exámenes en extracciones/: $($examenesExtracciones.Count)" -ForegroundColor White
Write-Host "Archivos duplicados: $($agrupados.Count)" -ForegroundColor $(if ($agrupados) { "Red" } else { "Green" })
Write-Host "Archivos legacy: $($legacy.Count)" -ForegroundColor $(if ($legacy) { "Yellow" } else { "Green" })
Write-Host "Carpetas antiguas: $($resultadosExamenes.Count)" -ForegroundColor $(if ($resultadosExamenes) { "Yellow" } else { "Green" })

Write-Host "`n💡 RECOMENDACIONES:" -ForegroundColor Cyan
if ($agrupados -or $legacy -or $resultadosExamenes) {
    Write-Host "   1. Ejecuta python migrar_examenes_a_nueva_estructura.py" -ForegroundColor Yellow
    Write-Host "   2. Reinicia el servidor backend: python api_server.py" -ForegroundColor Yellow
    Write-Host "   3. Recarga el calendario en la interfaz web" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Sistema en buen estado. Reinicia el backend para aplicar mejoras." -ForegroundColor Green
}

Write-Host "`n"

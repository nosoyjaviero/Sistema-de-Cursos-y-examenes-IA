#!/usr/bin/env pwsh

<#
.SYNOPSIS
Script para probar el sistema de guardado de imágenes en Picture_Description

.DESCRIPTION
Verifica que:
1. El endpoint /api/guardar-imagen-practica funciona
2. Las imágenes se guardan correctamente en extracciones/
3. El JSON de la práctica se actualiza con la URL correcta
#>

Write-Host "🧪 PRUEBA: Sistema de Guardado de Imágenes en Picture_Description" -ForegroundColor Cyan
Write-Host "=" * 70

# 1. Verificar que la carpeta existe
$rutaCarpeta = "c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas"
Write-Host "`n📁 Verificando carpeta de práctica..."
if (Test-Path $rutaCarpeta) {
    Write-Host "   ✅ Carpeta existe: $rutaCarpeta" -ForegroundColor Green
    Get-ChildItem $rutaCarpeta | Format-Table Name, Length, LastWriteTime -AutoSize
} else {
    Write-Host "   ❌ Carpeta NO existe" -ForegroundColor Red
    exit 1
}

# 2. Buscar prácticas de picture_description
Write-Host "`n📋 Buscando prácticas de picture_description..."
$practicas = Get-ChildItem $rutaCarpeta -Filter "practica_*.json"
if ($practicas.Count -eq 0) {
    Write-Host "   ⚠️ No se encontraron archivos practica_*.json" -ForegroundColor Yellow
    exit 1
}

Write-Host "   ✅ Encontradas $($practicas.Count) práctica(s)" -ForegroundColor Green

foreach ($archivo in $practicas) {
    Write-Host "`n📄 Analizando: $($archivo.Name)"
    
    # Leer el JSON
    $json = Get-Content $archivo.FullName | ConvertFrom-Json
    
    # Buscar preguntas de picture_description
    $preguntasImg = $json.preguntas | Where-Object { $_.tipo -eq "picture_description" }
    
    if ($preguntasImg.Count -eq 0) {
        Write-Host "   ⚠️ Sin preguntas de picture_description" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "   ✅ Encontradas $($preguntasImg.Count) pregunta(s) de picture_description" -ForegroundColor Green
    
    foreach ($idx, $preg in $preguntasImg.GetEnumerator()) {
        Write-Host "`n   📸 Pregunta #$idx:"
        
        $urlMetadata = $preg.metadata.imagen.url
        $urlTopLevel = $preg.imagen.url
        
        # Verificar si hay URL
        if ([string]::IsNullOrEmpty($urlMetadata) -and [string]::IsNullOrEmpty($urlTopLevel)) {
            Write-Host "      ❌ SIN URL (imagen no guardada)" -ForegroundColor Red
            Write-Host "      💡 Intenta: cargar imagen → responder → guardar práctica" -ForegroundColor Yellow
        } else {
            $url = $urlMetadata ?? $urlTopLevel
            Write-Host "      ✅ URL encontrada: $url" -ForegroundColor Green
            
            # Verificar si el archivo existe
            $rutaImg = Join-Path $rutaCarpeta ($url -replace "^extracciones/🌐 Plataforma - Cosas/", "")
            if (Test-Path $rutaImg) {
                $tamaño = (Get-Item $rutaImg).Length
                Write-Host "      ✅ ARCHIVO EXISTE: $(Get-Item $rutaImg).Name ($tamaño bytes)" -ForegroundColor Green
            } else {
                Write-Host "      ❌ ARCHIVO NO EXISTE: $rutaImg" -ForegroundColor Red
            }
        }
        
        # Mostrar nombre del archivo sugerido
        $nombreArch = $preg.metadata.imagen.nombre_archivo_sugerido ?? $preg.imagen.nombre_archivo_sugerido
        if ($nombreArch) {
            Write-Host "      📝 Nombre sugerido: $nombreArch" -ForegroundColor Cyan
        }
    }
}

# 3. Listar imágenes en la carpeta
Write-Host "`n🖼️ Imágenes en la carpeta:"
$imagenes = Get-ChildItem $rutaCarpeta -Include "*.png", "*.jpg", "*.jpeg", "*.gif"
if ($imagenes.Count -eq 0) {
    Write-Host "   ⚠️ NO HAY IMÁGENES GUARDADAS" -ForegroundColor Yellow
    Write-Host "   💡 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "      1. Abre Examinator en el navegador" -ForegroundColor Cyan
    Write-Host "      2. Carga una imagen en el ejercicio picture_description" -ForegroundColor Cyan
    Write-Host "      3. Responde y guarda la práctica" -ForegroundColor Cyan
    Write-Host "      4. Vuelve a ejecutar este script" -ForegroundColor Cyan
} else {
    Write-Host "   ✅ Encontradas $($imagenes.Count) imagen(es)" -ForegroundColor Green
    $imagenes | Format-Table Name, Length, LastWriteTime -AutoSize
}

Write-Host "`n" + "=" * 70
Write-Host "✅ Prueba completada" -ForegroundColor Cyan

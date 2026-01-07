#!/usr/bin/env pwsh

Write-Host "Test: Sistema de Guardado de Imagenes" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Ruta de la carpeta
$rutaCarpeta = "c:\Users\Fela\Documents\Proyectos\Examinator\extracciones\🌐 Plataforma - Cosas"

# Verificar carpeta
if (Test-Path $rutaCarpeta) {
    Write-Host "Carpeta encontrada: $rutaCarpeta" -ForegroundColor Green
} else {
    Write-Host "Carpeta NO existe" -ForegroundColor Red
    exit 1
}

# Listar contenido
Write-Host "`nContenido de la carpeta:" -ForegroundColor Cyan
Get-ChildItem $rutaCarpeta -Force | Format-Table Name, Length, LastWriteTime

# Buscar imagenes
Write-Host "`nImagenes (.png, .jpg):" -ForegroundColor Cyan
$imagenes = Get-ChildItem $rutaCarpeta -Include *.png, *.jpg, *.jpeg, *.gif -Force
if ($imagenes.Count -eq 0) {
    Write-Host "NO hay imagenes guardadas" -ForegroundColor Yellow
} else {
    Write-Host "Imagenes encontradas:" -ForegroundColor Green
    $imagenes | Format-Table Name, Length
}

# Leer el ultimo JSON
Write-Host "`nUltima practica JSON:" -ForegroundColor Cyan
$practicas = Get-ChildItem $rutaCarpeta -Filter "practica_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($practicas) {
    Write-Host "Archivo: $($practicas.Name)" -ForegroundColor Green
    $contenido = Get-Content $practicas.FullName | ConvertFrom-Json
    
    # Mostrar estructura
    Write-Host "Preguntas en el JSON:" -ForegroundColor Cyan
    foreach ($preg in $contenido.preguntas) {
        Write-Host "  - Tipo: $($preg.tipo)" -ForegroundColor White
        if ($preg.tipo -eq "picture_description") {
            Write-Host "    Imagen URL: $(if ($preg.imagen.url) { $preg.imagen.url } else { 'VACIA' })" -ForegroundColor $(if ($preg.imagen.url) { 'Green' } else { 'Red' })
            if ($preg.metadata.imagen) {
                Write-Host "    Metadata imagen URL: $(if ($preg.metadata.imagen.url) { $preg.metadata.imagen.url } else { 'VACIA' })" -ForegroundColor $(if ($preg.metadata.imagen.url) { 'Green' } else { 'Red' })
            }
        }
    }
}

Write-Host "`nTest completado" -ForegroundColor Green

# Script para monitorear la creación de archivos de práctica en tiempo real

Write-Host "`n🔍 MONITOREANDO CREACIÓN DE PRÁCTICAS..." -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener`n" -ForegroundColor Gray

$basePath = "extracciones"
$lastCheck = Get-Date

while ($true) {
    Start-Sleep -Seconds 2
    
    # Buscar archivos practica_*.json creados recientemente
    $archivos = Get-ChildItem -Path $basePath -Recurse -File | 
                Where-Object { 
                    $_.Name -like "practica_*.json" -and 
                    $_.LastWriteTime -gt $lastCheck 
                }
    
    if ($archivos) {
        foreach ($archivo in $archivos) {
            Write-Host "`n🎉 NUEVA PRÁCTICA DETECTADA!" -ForegroundColor Green
            Write-Host "📄 Archivo: $($archivo.FullName)" -ForegroundColor Yellow
            Write-Host "📅 Creado: $($archivo.LastWriteTime)" -ForegroundColor Gray
            Write-Host "📏 Tamaño: $([math]::Round($archivo.Length/1KB, 2)) KB" -ForegroundColor Gray
            
            # Leer contenido
            try {
                $json = Get-Content $archivo.FullName -Raw | ConvertFrom-Json
                Write-Host "`n📋 Contenido:" -ForegroundColor Cyan
                Write-Host "   ID: $($json.id)" -ForegroundColor White
                Write-Host "   es_practica: $($json.es_practica)" -ForegroundColor $(if($json.es_practica){"Green"}else{"Red"})
                Write-Host "   carpeta_ruta: $($json.carpeta_ruta)" -ForegroundColor White
                Write-Host "   archivo: $($json.archivo)" -ForegroundColor White
                Write-Host "   preguntas: $($json.preguntas.Count)" -ForegroundColor White
            } catch {
                Write-Host "⚠️  Error leyendo archivo: $_" -ForegroundColor Yellow
            }
            
            Write-Host "`n✅ Verifica en el navegador:" -ForegroundColor Cyan
            Write-Host "   - Calendario: ¿Aparece la práctica?" -ForegroundColor White
            Write-Host "   - Pestaña Prácticas: ¿Está en la lista?" -ForegroundColor White
            Write-Host ""
        }
        $lastCheck = Get-Date
    }
}

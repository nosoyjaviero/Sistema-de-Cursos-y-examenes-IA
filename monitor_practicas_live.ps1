# Monitor en TIEMPO REAL de creación de archivos de práctica
# Muestra INMEDIATAMENTE cuando se crea un archivo practica_*.json

Write-Host "`n🔍 MONITOR EN VIVO - Archivos de Práctica" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "📁 Monitoreando: extracciones/" -ForegroundColor White
Write-Host "🎯 Patrón: practica_*.json" -ForegroundColor White
Write-Host "⏰ Presiona Ctrl+C para detener`n" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Gray

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "extracciones"
$watcher.Filter = "practica_*.json"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    Write-Host "`n🎉 PRÁCTICA DETECTADA! ($changeType) - $timestamp" -ForegroundColor Green
    Write-Host "━" * 60 -ForegroundColor Gray
    Write-Host "📄 Archivo: " -NoNewline -ForegroundColor Cyan
    Write-Host "$([System.IO.Path]::GetFileName($path))" -ForegroundColor White
    Write-Host "📁 Carpeta: " -NoNewline -ForegroundColor Cyan
    Write-Host "$([System.IO.Path]::GetDirectoryName($path).Replace((Get-Location).Path + '\extracciones\', ''))" -ForegroundColor White
    
    # Esperar un momento para que el archivo se termine de escribir
    Start-Sleep -Milliseconds 500
    
    try {
        $content = Get-Content $path -Raw | ConvertFrom-Json
        Write-Host "🆔 ID: " -NoNewline -ForegroundColor Yellow
        Write-Host "$($content.id)" -ForegroundColor White
        Write-Host "✅ es_practica: " -NoNewline -ForegroundColor Yellow
        Write-Host "$($content.es_practica)" -ForegroundColor White
        Write-Host "📂 carpeta_ruta: " -NoNewline -ForegroundColor Yellow
        Write-Host "$($content.carpeta_ruta)" -ForegroundColor White
        Write-Host "📊 Preguntas: " -NoNewline -ForegroundColor Yellow
        Write-Host "$($content.preguntas.Count)" -ForegroundColor White
        
        $fileInfo = Get-Item $path
        Write-Host "💾 Tamaño: " -NoNewline -ForegroundColor Yellow
        Write-Host "$([Math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor White
    } catch {
        Write-Host "⚠️  No se pudo leer el contenido (archivo aún escribiéndose)" -ForegroundColor Red
    }
    
    Write-Host "━" * 60 -ForegroundColor Gray
}

$handlers = @(
    Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action
)

try {
    Write-Host "✅ Monitor activo. Esperando prácticas...`n" -ForegroundColor Green
    
    # Mostrar archivos existentes
    $existentes = Get-ChildItem -Path "extracciones" -Filter "practica_*.json" -Recurse -File
    if ($existentes.Count -gt 0) {
        Write-Host "📋 Archivos existentes encontrados: $($existentes.Count)" -ForegroundColor Magenta
        foreach ($archivo in $existentes) {
            $relativePath = $archivo.FullName.Replace((Get-Location).Path + '\extracciones\', '')
            Write-Host "   📄 $relativePath" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    # Mantener el script ejecutándose
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    # Cleanup
    $handlers | ForEach-Object { Unregister-Event -SourceIdentifier $_.Name }
    $watcher.Dispose()
    Write-Host "`n👋 Monitor detenido" -ForegroundColor Yellow
}

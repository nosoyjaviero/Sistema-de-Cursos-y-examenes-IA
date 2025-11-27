# 🧹 SCRIPT DE LIMPIEZA DE FLASHCARDS CORRUPTAS
# Corrige flashcards con revisionesHoy > 2 y proximaRevision mal formateadas

Write-Host "🔍 BUSCANDO FLASHCARDS CORRUPTAS..." -ForegroundColor Cyan
Write-Host ""

$archivosCorregidos = 0
$flashcardsCorregidas = 0

# Buscar todos los archivos flashcards.json
Get-ChildItem -Path "extracciones" -Recurse -Filter "flashcards.json" | ForEach-Object {
    $archivo = $_.FullName
    $carpeta = $_.DirectoryName
    
    Write-Host "📁 Procesando: $carpeta" -ForegroundColor Yellow
    
    try {
        # Leer archivo
        $flashcards = Get-Content $archivo -Raw | ConvertFrom-Json
        $hubocambios = $false
        
        foreach ($fc in $flashcards) {
            $titulo = if ($fc.titulo) { $fc.titulo } elseif ($fc.frente) { $fc.frente } else { $fc.id }
            $problemas = @()
            
            # PROBLEMA 1: revisionesHoy > 2 (CRÍTICO)
            if ($fc.revisionesHoy -and $fc.revisionesHoy -gt 2) {
                $problemas += "revisionesHoy=$($fc.revisionesHoy) (reseteado a 0)"
                $fc.revisionesHoy = 0
                $huboChangios = $true
            }
            
            # PROBLEMA 2: proximaRevision con hora incorrecta
            if ($fc.proximaRevision -and -not $fc.proximaRevision.EndsWith("T00:00:00.000Z")) {
                # Extraer solo la fecha y normalizar a 00:00:00
                $fecha = [DateTime]::Parse($fc.proximaRevision)
                $fechaNormalizada = $fecha.Date.ToString("yyyy-MM-ddT00:00:00.000Z")
                $problemas += "proximaRevision con hora incorrecta (normalizada a 00:00:00)"
                $fc.proximaRevision = $fechaNormalizada
                $huboChangios = $true
            }
            
            # PROBLEMA 3: revisionesHoy sin ultima_revision (inconsistencia)
            if ($fc.revisionesHoy -gt 0 -and -not $fc.ultima_revision) {
                $problemas += "revisionesHoy sin ultima_revision (reseteado)"
                $fc.revisionesHoy = 0
                $huboChangios = $true
            }
            
            # PROBLEMA 4: ultima_revision de hoy pero revisionesHoy = 0
            if ($fc.ultima_revision) {
                $ultimaRev = [DateTime]::Parse($fc.ultima_revision)
                $hoy = (Get-Date).Date
                
                if ($ultimaRev.Date -eq $hoy -and $fc.revisionesHoy -eq 0) {
                    $problemas += "Revisada hoy pero contador en 0 (corrigiendo a 1)"
                    $fc.revisionesHoy = 1
                    $huboChangios = $true
                }
            }
            
            if ($problemas.Count -gt 0) {
                Write-Host "   ⚠️  $titulo" -ForegroundColor Red
                foreach ($problema in $problemas) {
                    Write-Host "      - $problema" -ForegroundColor Gray
                }
                $flashcardsCorregidas++
            }
        }
        
        # Guardar archivo si hubo cambios
        if ($huboChangios) {
            $flashcards | ConvertTo-Json -Depth 10 | Set-Content $archivo -Encoding UTF8
            Write-Host "   ✅ Archivo guardado con correcciones" -ForegroundColor Green
            $archivosCorregidos++
        } else {
            Write-Host "   ✅ Sin problemas" -ForegroundColor Green
        }
        
    } catch {
        Write-Host "   ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE LIMPIEZA" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Archivos corregidos: $archivosCorregidos" -ForegroundColor Yellow
Write-Host "Flashcards corregidas: $flashcardsCorregidas" -ForegroundColor Yellow
Write-Host ""

if ($flashcardsCorregidas -gt 0) {
    Write-Host "🎉 Limpieza completada. Reinicia el navegador para aplicar cambios." -ForegroundColor Green
} else {
    Write-Host "✅ No se encontraron flashcards corruptas." -ForegroundColor Green
}

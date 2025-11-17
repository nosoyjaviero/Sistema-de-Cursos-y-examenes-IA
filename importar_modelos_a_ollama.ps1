# Script para importar modelos GGUF a Ollama
Write-Host "📦 Importando modelos GGUF a Ollama" -ForegroundColor Cyan
Write-Host ""

$modelosDir = "modelos"
$ollama = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

# Verificar Ollama
if (-not (Test-Path $ollama)) {
    Write-Host "❌ Ollama no está instalado" -ForegroundColor Red
    exit 1
}

# Listar modelos GGUF
$modelos = Get-ChildItem -Path $modelosDir -Filter "*.gguf"

Write-Host "🔍 Modelos GGUF encontrados:" -ForegroundColor Green
$i = 0
foreach ($modelo in $modelos) {
    $i++
    $size = [math]::Round($modelo.Length / 1GB, 2)
    Write-Host "  $i. $($modelo.Name) ($size GB)" -ForegroundColor White
}

Write-Host ""
Write-Host "💡 Para importar un modelo a Ollama:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Crear Modelfile:" -ForegroundColor Cyan
Write-Host '   FROM "./modelos/nombre-modelo.gguf"' -ForegroundColor Gray
Write-Host ""
Write-Host "2. Importar:" -ForegroundColor Cyan
Write-Host '   & "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" create mi-modelo -f Modelfile' -ForegroundColor Gray
Write-Host ""

$respuesta = Read-Host "¿Quieres crear un Modelfile automáticamente? (s/n)"

if ($respuesta -eq "s") {
    Write-Host ""
    Write-Host "Selecciona el número del modelo:" -ForegroundColor Cyan
    $seleccion = Read-Host "Número (1-$i)"
    
    if ($seleccion -match '^\d+$' -and [int]$seleccion -ge 1 -and [int]$seleccion -le $i) {
        $modeloSeleccionado = $modelos[[int]$seleccion - 1]
        $nombreBase = $modeloSeleccionado.BaseName -replace '[^a-zA-Z0-9-]', '-'
        
        # Crear Modelfile
        $modelfilePath = "Modelfile_$nombreBase"
        $contenido = @"
FROM ./modelos/$($modeloSeleccionado.Name)

# Parámetros optimizados para generación de exámenes
PARAMETER temperature 0.25
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 8192

# Template para Llama 3
TEMPLATE "<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|><|start_header_id|>user<|end_header_id|>

{{ .Prompt }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"

SYSTEM "Eres un experto en crear exámenes educativos. Generas preguntas claras y precisas basadas en el contenido proporcionado."
"@
        
        Set-Content -Path $modelfilePath -Value $contenido -Encoding UTF8
        
        Write-Host ""
        Write-Host "✅ Modelfile creado: $modelfilePath" -ForegroundColor Green
        Write-Host ""
        Write-Host "🚀 Para importar a Ollama, ejecuta:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "   & `"$env:LOCALAPPDATA\Programs\Ollama\ollama.exe`" create $nombreBase -f $modelfilePath" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "⏱️  Esto puede tardar unos minutos..." -ForegroundColor Gray
        Write-Host ""
        
        $importar = Read-Host "¿Importar ahora? (s/n)"
        
        if ($importar -eq "s") {
            Write-Host ""
            Write-Host "📥 Importando a Ollama..." -ForegroundColor Cyan
            & $ollama create $nombreBase -f $modelfilePath
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "✅ Modelo importado exitosamente como: $nombreBase" -ForegroundColor Green
                Write-Host ""
                Write-Host "🧪 Para probar:" -ForegroundColor Cyan
                Write-Host "   & `"$env:LOCALAPPDATA\Programs\Ollama\ollama.exe`" run $nombreBase `"Hola`"" -ForegroundColor Gray
                Write-Host ""
                Write-Host "📝 Para usar en tu código:" -ForegroundColor Cyan
                Write-Host '   generador = GeneradorUnificado(usar_ollama=True, modelo_ollama="' + $nombreBase + '")' -ForegroundColor Gray
            } else {
                Write-Host ""
                Write-Host "❌ Error al importar. Revisa el formato del modelo." -ForegroundColor Red
            }
        }
    } else {
        Write-Host "❌ Selección inválida" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📚 Más info: https://github.com/ollama/ollama/blob/main/docs/import.md" -ForegroundColor Gray

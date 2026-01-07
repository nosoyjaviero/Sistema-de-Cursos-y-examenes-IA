#!/usr/bin/env pwsh

Write-Host "🚀 Iniciando servidor Vite de desarrollo..." -ForegroundColor Cyan
Write-Host "Este es NECESARIO para que los cambios en src/App.jsx se actualicen en el navegador" -ForegroundColor Yellow

cd 'c:\Users\Fela\Documents\Proyectos\Examinator\examinator-web'

# Verificar si node_modules existe
if (!(Test-Path 'node_modules')) {
    Write-Host "📦 node_modules no existe, instalando dependencias..." -ForegroundColor Yellow
    npm install
}

# Iniciar servidor dev
Write-Host "`n✅ Ejecutando: npm run dev" -ForegroundColor Green
Write-Host "El servidor estará disponible en: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener el servidor`n" -ForegroundColor Yellow

npm run dev

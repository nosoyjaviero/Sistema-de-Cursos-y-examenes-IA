@echo off
chcp 65001 > nul
echo ================================================================
echo    DIAGNÓSTICO DEL BUSCADOR
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/4] Verificando archivos .txt en extracciones...
echo.
dir /s /b "extracciones\*.txt" 2>nul
echo.

echo [2/4] Contando archivos .txt...
for /f %%i in ('dir /s /b "extracciones\*.txt" 2^>nul ^| find /c /v ""') do set COUNT=%%i
echo Total de archivos .txt: %COUNT%
echo.

echo [3/4] Probando Python y buscador_ia.py...
echo.
venv\Scripts\activate.bat && python -c "from buscador_ia import ConfigBuscador, IndexadorLocal; import os; config = ConfigBuscador(); print('Carpetas configuradas:'); [print(f'  - {c}') for c in config.CARPETAS_RAIZ]; print(f'\nExtensiones: {config.EXTENSIONES_TEXTO}'); indexador = IndexadorLocal(config); archivos = indexador.escanear_archivos(incremental=False); print(f'\n📊 Archivos encontrados por el escáner: {len(archivos)}'); [print(f'  ✓ {a[\"ruta\"]}') for a in archivos[:10]]; print('...' if len(archivos) > 10 else '')"
echo.

echo [4/4] Verificando servidor en puerto 5001...
netstat -ano | findstr ":5001"
echo.

echo ================================================================
echo    FIN DEL DIAGNÓSTICO
echo ================================================================
echo.
pause

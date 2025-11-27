from pathlib import Path
import json

EXTRACCIONES_PATH = Path('extracciones')
ruta = 'Platzi'

carpeta_seleccionada = EXTRACCIONES_PATH / ruta / 'resultados_practicas'
print(f"📂 Ruta completa: {carpeta_seleccionada.absolute()}")
print(f"📂 ¿Existe?: {carpeta_seleccionada.exists()}")

if carpeta_seleccionada.exists():
    archivos_json = list(carpeta_seleccionada.glob("*.json"))
    print(f"📄 Archivos encontrados: {len(archivos_json)}")
    
    for archivo in archivos_json:
        print(f"\n🔍 Archivo: {archivo.name}")
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            es_practica = data.get('es_practica', False)
            print(f"   es_practica: {es_practica} (tipo: {type(es_practica).__name__})")
            print(f"   titulo: {data.get('titulo', 'N/A')}")
            
            if es_practica:
                print("   ✅ ES PRÁCTICA")
            else:
                print(f"   ❌ NO ES PRÁCTICA")
        except Exception as e:
            print(f"   ❌ Error: {e}")
else:
    print("❌ La carpeta NO existe")

from pathlib import Path
import json

EXTRACCIONES_PATH = Path('extracciones')
tipo = 'practicas'
ruta = 'Platzi'

archivos = []
carpetas_practicas = []

print(f"🔍 EXPLORAR: tipo='{tipo}', ruta='{ruta}'")

if tipo == 'practicas':
    extracciones_base = EXTRACCIONES_PATH
    
    if extracciones_base.exists():
        # Si no hay ruta específica, mostrar carpetas disponibles
        if not ruta:
            print("📁 Listando carpetas raíz...")
            for carpeta in extracciones_base.iterdir():
                if carpeta.is_dir():
                    practicas_path = carpeta / 'resultados_practicas'
                    if practicas_path.exists():
                        num_practicas = len(list(practicas_path.glob("*.json")))
                        if num_practicas > 0:
                            carpetas_practicas.append({
                                'nombre': carpeta.name,
                                'ruta': carpeta.name,
                                'num_archivos': num_practicas
                            })
        else:
            # Listar prácticas de la carpeta específica
            carpeta_seleccionada = extracciones_base / ruta / 'resultados_practicas'
            print(f"📂 Buscando prácticas en: {carpeta_seleccionada}")
            print(f"📂 ¿Existe?: {carpeta_seleccionada.exists()}")
            
            if carpeta_seleccionada.exists():
                archivos_encontrados = list(carpeta_seleccionada.glob("*.json"))
                print(f"📄 Archivos JSON encontrados: {len(archivos_encontrados)}")
                
                for archivo_practica in archivos_encontrados:
                    try:
                        print(f"🔍 Leyendo: {archivo_practica.name}")
                        stat = archivo_practica.stat()
                        # Leer el archivo para obtener información
                        with open(archivo_practica, 'r', encoding='utf-8') as f:
                            practica_data = json.load(f)
                        
                        es_practica = practica_data.get('es_practica', False)
                        print(f"   es_practica: {es_practica} (tipo: {type(es_practica)})")
                        
                        # Verificar que tiene es_practica=true
                        if es_practica:
                            titulo = practica_data.get('titulo', practica_data.get('carpeta_nombre', archivo_practica.stem))
                            print(f"   ✅ Agregando práctica: {titulo}")
                            archivos.append({
                                'nombre': f"{titulo}.json",
                                'ruta_completa': str(archivo_practica.relative_to(Path.cwd())),
                                'tipo': 'Práctica',
                                'extension': '.json',
                                'tamaño': stat.st_size,
                                'modificado': stat.st_mtime
                            })
                        else:
                            print(f"   ⚠️ No es práctica (es_practica={es_practica})")
                    except Exception as e:
                        print(f"⚠️ Error leyendo práctica {archivo_practica}: {e}")
                        import traceback
                        traceback.print_exc()

print(f"\n📊 RESULTADO:")
print(f"   Carpetas: {len(carpetas_practicas)}")
print(f"   Archivos: {len(archivos)}")

if archivos:
    print(f"\n📄 Archivos detectados:")
    for archivo in archivos:
        print(f"   - {archivo['nombre']} ({archivo['tipo']})")
else:
    print("\n❌ NO SE DETECTARON ARCHIVOS")

response = {
    'carpetas': carpetas_practicas,
    'archivos': archivos,
    'ruta_actual': ruta,
    'tipo': tipo
}

print(f"\n🌐 Respuesta JSON:")
print(json.dumps(response, indent=2))

"""
Script de prueba para verificar que los resultados de exámenes/prácticas
se guarden correctamente en extracciones/[carpeta]/resultados_examenes/ o resultados_practicas/
"""

import requests
import json
from pathlib import Path
import time

API_URL = "http://localhost:8000"

def test_evaluar_examen_en_extracciones():
    """
    Prueba que al calificar un examen/práctica, los resultados se guarden
    en la carpeta extracciones/[carpeta]/resultados_examenes/ o resultados_practicas/
    """
    
    # Datos de prueba
    carpeta_test = "Platzi"  # Carpeta que ya existe en extracciones
    
    # Crear preguntas de prueba
    preguntas = [
        {
            "id": 1,
            "tipo": "multiple",
            "pregunta": "¿Cuál es la capital de Francia?",
            "opciones": ["París", "Londres", "Berlín", "Madrid"],
            "respuesta_correcta": "París",
            "puntos": 10,
            "metadata": {}
        },
        {
            "id": 2,
            "tipo": "verdadero_falso",
            "pregunta": "La Tierra es plana",
            "respuesta_correcta": "Falso",
            "puntos": 5,
            "metadata": {}
        },
        {
            "id": 3,
            "tipo": "corta",
            "pregunta": "¿Qué es Python?",
            "respuesta_correcta": "Un lenguaje de programación",
            "puntos": 15,
            "metadata": {}
        }
    ]
    
    # Respuestas del usuario (2 correctas, 1 incorrecta)
    respuestas = {
        "0": "París",       # Correcta
        "1": "Verdadero",   # Incorrecta
        "2": "Un lenguaje de programación"  # Correcta
    }
    
    print("="*60)
    print("🧪 PRUEBA: Guardar resultados en extracciones/")
    print("="*60)
    
    # Prueba 1: Examen normal
    print("\n📝 Prueba 1: Calificando EXAMEN en carpeta 'Platzi'...")
    response = requests.post(
        f"{API_URL}/api/evaluar-examen",
        json={
            "preguntas": preguntas,
            "respuestas": respuestas,
            "carpeta_path": carpeta_test,
            "es_practica": False
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Examen calificado exitosamente")
        print(f"   📊 Puntos: {data['puntos_obtenidos']}/{data['puntos_totales']}")
        print(f"   📈 Porcentaje: {data['porcentaje']:.2f}%")
        
        # Verificar que el archivo se guardó
        ruta_esperada = Path("extracciones") / carpeta_test / "resultados_examenes"
        if ruta_esperada.exists():
            archivos = list(ruta_esperada.glob("examen_*.json"))
            if archivos:
                print(f"   ✅ Archivo guardado en: {archivos[-1]}")
                # Leer y mostrar el contenido
                with open(archivos[-1], 'r', encoding='utf-8') as f:
                    contenido = json.load(f)
                    print(f"   📄 Contenido del archivo:")
                    print(f"      - ID: {contenido.get('id')}")
                    print(f"      - Carpeta: {contenido.get('carpeta_nombre')}")
                    print(f"      - Fecha: {contenido.get('fecha_completado')}")
            else:
                print(f"   ❌ No se encontró archivo en: {ruta_esperada}")
        else:
            print(f"   ❌ La carpeta no existe: {ruta_esperada}")
    else:
        print(f"❌ Error al calificar examen: {response.status_code}")
        print(f"   {response.text}")
    
    # Esperar un momento
    time.sleep(1)
    
    # Prueba 2: Práctica
    print("\n📝 Prueba 2: Calificando PRÁCTICA en carpeta 'Platzi'...")
    response = requests.post(
        f"{API_URL}/api/evaluar-examen",
        json={
            "preguntas": preguntas,
            "respuestas": respuestas,
            "carpeta_path": carpeta_test,
            "es_practica": True
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Práctica calificada exitosamente")
        print(f"   📊 Puntos: {data['puntos_obtenidos']}/{data['puntos_totales']}")
        print(f"   📈 Porcentaje: {data['porcentaje']:.2f}%")
        
        # Verificar que el archivo se guardó
        ruta_esperada = Path("extracciones") / carpeta_test / "resultados_practicas"
        if ruta_esperada.exists():
            archivos = list(ruta_esperada.glob("examen_*.json"))
            if archivos:
                print(f"   ✅ Archivo guardado en: {archivos[-1]}")
                # Leer y mostrar el contenido
                with open(archivos[-1], 'r', encoding='utf-8') as f:
                    contenido = json.load(f)
                    print(f"   📄 Contenido del archivo:")
                    print(f"      - ID: {contenido.get('id')}")
                    print(f"      - Carpeta: {contenido.get('carpeta_nombre')}")
                    print(f"      - Fecha: {contenido.get('fecha_completado')}")
                    print(f"      - Es práctica: {contenido.get('es_practica')}")
            else:
                print(f"   ❌ No se encontró archivo en: {ruta_esperada}")
        else:
            print(f"   ❌ La carpeta no existe: {ruta_esperada}")
    else:
        print(f"❌ Error al calificar práctica: {response.status_code}")
        print(f"   {response.text}")
    
    print("\n" + "="*60)
    print("🎯 RESUMEN DE PRUEBAS")
    print("="*60)
    
    # Verificar carpetas creadas
    base_path = Path("extracciones") / carpeta_test
    carpeta_examenes = base_path / "resultados_examenes"
    carpeta_practicas = base_path / "resultados_practicas"
    
    print(f"\n📁 Carpetas creadas en extracciones/{carpeta_test}/:")
    if carpeta_examenes.exists():
        archivos_examenes = list(carpeta_examenes.glob("*.json"))
        print(f"   ✅ resultados_examenes/ ({len(archivos_examenes)} archivos)")
        for archivo in archivos_examenes:
            print(f"      - {archivo.name}")
    else:
        print(f"   ❌ resultados_examenes/ NO EXISTE")
    
    if carpeta_practicas.exists():
        archivos_practicas = list(carpeta_practicas.glob("*.json"))
        print(f"   ✅ resultados_practicas/ ({len(archivos_practicas)} archivos)")
        for archivo in archivos_practicas:
            print(f"      - {archivo.name}")
    else:
        print(f"   ❌ resultados_practicas/ NO EXISTE")
    
    print("\n" + "="*60)
    print("✅ Prueba completada")
    print("="*60)

if __name__ == "__main__":
    try:
        test_evaluar_examen_en_extracciones()
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

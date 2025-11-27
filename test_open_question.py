"""
Script para probar la generación de preguntas de desarrollo (open_question)
"""
import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"

def test_open_question():
    """Prueba la generación de preguntas de desarrollo"""
    
    print("🧪 Probando generación de preguntas de DESARROLLO...")
    print("="*60)
    
    # Crear contenido de prueba más extenso para análisis
    texto_prueba = """
    El diseño centrado en el usuario (UCD - User-Centered Design) es una filosofía y proceso 
    de diseño que sitúa al usuario final en el centro de todo el desarrollo del producto.
    
    Los principios fundamentales del UCD incluyen:
    
    1. Enfoque temprano en usuarios y tareas: Comprender quiénes son los usuarios, 
    qué necesitan hacer y en qué contexto lo harán.
    
    2. Medición empírica: Observar y medir el comportamiento real de los usuarios 
    con prototipos y productos.
    
    3. Diseño iterativo: Ciclos repetidos de diseño, prueba y refinamiento basados 
    en retroalimentación de usuarios.
    
    Beneficios del UCD:
    - Mayor satisfacción del usuario
    - Reducción de costos de desarrollo (menos correcciones posteriores)
    - Productos más intuitivos y fáciles de usar
    - Mejor adopción y retención de usuarios
    
    Metodologías comunes:
    - Investigación de usuarios (entrevistas, encuestas)
    - Creación de personas y escenarios
    - Pruebas de usabilidad
    - Diseño participativo
    """
    
    ruta_temp = Path("temp/test_open_question.txt")
    ruta_temp.parent.mkdir(exist_ok=True)
    ruta_temp.write_text(texto_prueba, encoding='utf-8')
    
    datos = {
        "ruta": str(ruta_temp.absolute()),
        "num_open_question": 2,
        "prompt": "Genera preguntas de desarrollo profundo sobre diseño centrado en usuario"
    }
    
    print(f"📤 Enviando solicitud para {datos['num_open_question']} preguntas de desarrollo...")
    
    response = requests.post(
        f"{API_URL}/api/generar_practica",
        json=datos,
        timeout=120
    )
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Práctica generada exitosamente!")
        print(f"📊 Total de preguntas: {len(resultado.get('preguntas', []))}")
        
        for i, pregunta in enumerate(resultado.get('preguntas', []), 1):
            print(f"\n{'='*60}")
            print(f"Pregunta {i}:")
            print(f"Tipo: {pregunta.get('tipo')}")
            print(f"\n❓ PREGUNTA:")
            print(f"   {pregunta.get('pregunta', 'N/A')}")
            
            if 'metadata' in pregunta:
                metadata = pregunta['metadata']
                if 'key_points' in metadata:
                    print(f"\n🎯 Puntos clave a evaluar:")
                    for j, punto in enumerate(metadata.get('key_points', []), 1):
                        print(f"   {j}. {punto}")
            
            print(f"\n✅ Respuesta modelo esperada:")
            resp = pregunta.get('respuesta_correcta', 'N/A')
            if len(resp) > 200:
                print(f"   {resp[:200]}...")
                print(f"   ... (total: {len(resp)} caracteres)")
            else:
                print(f"   {resp}")
            
            print(f"\n📊 Puntos: {pregunta.get('puntos', 0)}")
        
        print(f"\n{'='*60}")
        print("🎯 Prueba completada!")
        
        # Guardar para inspección
        resultado_path = Path("temp/resultado_open_question.json")
        resultado_path.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"💾 Resultado guardado en: {resultado_path}")
        
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Mensaje: {response.text}")
        return False

if __name__ == "__main__":
    test_open_question()

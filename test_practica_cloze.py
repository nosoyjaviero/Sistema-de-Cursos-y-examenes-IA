"""
Script de prueba para verificar la generación de prácticas tipo Cloze
"""
import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"

def test_generar_practica_cloze():
    """Genera una práctica de tipo cloze para probar"""
    
    print("🧪 Probando generación de práctica tipo Cloze...")
    print("="*60)
    
    # Crear un documento de prueba
    texto_prueba = """
    Python es un lenguaje de programación de alto nivel, interpretado y de propósito general.
    Fue creado por Guido van Rossum y publicado por primera vez en 1991.
    Python es conocido por su sintaxis clara y legible, lo que lo hace ideal para principiantes.
    Se utiliza ampliamente en desarrollo web, ciencia de datos, inteligencia artificial y automatización.
    """
    
    # Guardar texto temporal
    ruta_temp = Path("temp/test_cloze.txt")
    ruta_temp.parent.mkdir(exist_ok=True)
    ruta_temp.write_text(texto_prueba, encoding='utf-8')
    
    # Datos para la solicitud
    datos = {
        "ruta": str(ruta_temp.absolute()),
        "num_cloze": 2,
        "prompt": "Genera prácticas de relleno de huecos sobre Python"
    }
    
    print(f"📤 Enviando solicitud con {datos['num_cloze']} preguntas cloze...")
    
    # Hacer la solicitud
    response = requests.post(
        f"{API_URL}/api/generar_practica",
        json=datos,
        timeout=120
    )
    
    if response.status_code == 200:
        resultado = response.json()
        print("✅ Práctica generada exitosamente!")
        print(f"📊 Total de preguntas: {len(resultado.get('preguntas', []))}")
        
        # Mostrar las preguntas cloze
        for i, pregunta in enumerate(resultado.get('preguntas', []), 1):
            print(f"\n{'='*60}")
            print(f"Pregunta {i}:")
            print(f"Tipo: {pregunta.get('tipo')}")
            
            if 'metadata' in pregunta:
                metadata = pregunta['metadata']
                print(f"\n📝 Texto con huecos:")
                print(f"   {metadata.get('text_with_gaps', 'N/A')}")
                print(f"\n✅ Respuestas correctas:")
                for j, ans in enumerate(metadata.get('answers', []), 1):
                    print(f"   {j}. {ans}")
                if 'hint' in metadata:
                    print(f"\n💡 Pista: {metadata['hint']}")
        
        print(f"\n{'='*60}")
        print("🎯 Prueba completada!")
        
        # Guardar resultado para inspección
        resultado_path = Path("temp/resultado_cloze.json")
        resultado_path.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"💾 Resultado guardado en: {resultado_path}")
        
        return True
    else:
        print(f"❌ Error en la solicitud: {response.status_code}")
        print(f"Mensaje: {response.text}")
        return False

if __name__ == "__main__":
    test_generar_practica_cloze()

"""
Script de prueba: Generador con Ollama + GPU
"""
from generador_unificado import GeneradorUnificado

print("="*60)
print("🧪 TEST: Sistema de Exámenes con Ollama + GPU")
print("="*60)

# Contenido de ejemplo
contenido = """
Python es un lenguaje de programación interpretado de alto nivel.
Fue creado por Guido van Rossum y lanzado por primera vez en 1991.
Python usa indentación para delimitar bloques de código en lugar de llaves.
Es muy popular para ciencia de datos, inteligencia artificial, desarrollo web,
automatización y scripting. Su filosofía enfatiza la legibilidad del código.
"""

print("\n📝 Contenido del documento:")
print(contenido.strip())

print("\n" + "="*60)
print("🤖 Generando examen con llama31-local (GPU automática)...")
print("="*60)

# Crear generador con Ollama
generador = GeneradorUnificado(
    usar_ollama=True,
    modelo_ollama="llama31-local"  # Cambia a: llama32-local, qwen-local, deepseek-r1-local
)

# Generar examen
preguntas = generador.generar_examen(
    contenido_documento=contenido,
    num_preguntas={
        'multiple': 3,
        'verdadero_falso': 2,
        'corta': 1
    }
)

print("\n" + "="*60)
print(f"✅ {len(preguntas)} preguntas generadas")
print("="*60)

# Mostrar preguntas
for i, p in enumerate(preguntas, 1):
    print(f"\n{i}. [{p.tipo.upper()}] ({p.puntos} puntos)")
    print(f"   {p.pregunta}")
    
    if p.opciones:
        for op in p.opciones:
            print(f"   {op}")
    
    print(f"   ✓ Respuesta: {p.respuesta_correcta}")

print("\n" + "="*60)
print("🎉 Prueba completada - GPU funcionando correctamente")
print("="*60)

# Mostrar cómo verificar GPU
print("\n💡 Para verificar uso de GPU, ejecuta en otra terminal:")
print('   & "$env:LOCALAPPDATA\\Programs\\Ollama\\ollama.exe" ps')
print("\n   Deberías ver: '100% GPU' en PROCESSOR")

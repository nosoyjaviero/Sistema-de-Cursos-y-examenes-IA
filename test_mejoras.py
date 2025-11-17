"""
Script de prueba para verificar las mejoras en el generador de exámenes
Ejecuta esto para ver si el modelo genera mejores preguntas con los cambios
"""

from pathlib import Path
from generador_examenes import GeneradorExamenes

def prueba_rapida():
    """Prueba rápida del generador con texto de ejemplo"""
    
    print("="*70)
    print("🧪 PRUEBA DE MEJORAS EN EL GENERADOR")
    print("="*70)
    print()
    
    # Texto de ejemplo limpio
    texto_prueba = """
La resolución de pantalla es la cantidad de píxeles que puede mostrar un dispositivo.
Un píxel es la unidad mínima de color en una pantalla digital.
La profundidad de color representa cuántos colores diferentes puede mostrar cada píxel.

El espacio de color sRGB es el estándar utilizado en la mayoría de monitores y navegadores web.
Define un conjunto específico de colores que pueden ser reproducidos de forma consistente.

Las interfaces responsivas son aquellas que se adaptan a diferentes tamaños de pantalla.
Utilizan unidades relativas como porcentajes en lugar de píxeles fijos.
El diseño fluido permite que el contenido se reorganice según el espacio disponible.

La accesibilidad web asegura que las interfaces sean utilizables por personas con discapacidades.
Incluye consideraciones como contraste de color, tamaño de texto y navegación por teclado.
"""
    
    print("📝 Texto de prueba:")
    print(texto_prueba[:200] + "...")
    print()
    
    # Inicializar generador
    modelo_path = Path("modelos/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf")
    
    if not modelo_path.exists():
        print(f"❌ Modelo no encontrado: {modelo_path}")
        print("ℹ️  Usando solo fallback para demostración")
        generador = GeneradorExamenes()
    else:
        generador = GeneradorExamenes(str(modelo_path))
    
    print()
    print("-"*70)
    print("🚀 Generando 8 preguntas...")
    print("-"*70)
    print()
    
    # Generar examen
    preguntas = generador.generar_examen(
        contenido_documento=texto_prueba,
        num_preguntas={'multiple': 8, 'corta': 0, 'desarrollo': 0}
    )
    
    print()
    print("="*70)
    print("📊 RESULTADO DE LA PRUEBA")
    print("="*70)
    print()
    
    if not preguntas:
        print("❌ No se generaron preguntas")
        return
    
    print(f"✅ Se generaron {len(preguntas)} preguntas\n")
    
    # Mostrar preguntas
    for i, preg in enumerate(preguntas, 1):
        print(f"\n{'='*70}")
        print(f"Pregunta {i} (Tipo: {preg.tipo}, Puntos: {preg.puntos})")
        print(f"{'='*70}")
        print(f"\n{preg.pregunta}\n")
        
        if preg.tipo == 'multiple':
            for opcion in preg.opciones:
                print(f"  {opcion}")
            print(f"\n✓ Respuesta correcta: {preg.respuesta_correcta}")
    
    print("\n" + "="*70)
    print("🎯 EVALUACIÓN DE CALIDAD")
    print("="*70)
    print()
    
    # Analizar calidad
    buenas = 0
    regulares = 0
    malas = 0
    
    palabras_problematicas = ['supongo', 'creo', 'comúnmente', 'tal vez', 
                              'muchas veces', 'varios', 'algunos']
    
    for preg in preguntas:
        preg_lower = preg.pregunta.lower()
        
        # Criterios de calidad
        tiene_problemas = any(palabra in preg_lower for palabra in palabras_problematicas)
        es_muy_corta = len(preg.pregunta) < 20
        es_muy_larga = len(preg.pregunta) > 150
        tiene_concepto_claro = any(palabra in preg_lower for palabra in 
                                   ['resolución', 'píxel', 'color', 'srgb', 
                                    'responsiv', 'accesibilidad', 'diseño'])
        
        if tiene_problemas or es_muy_corta or es_muy_larga:
            malas += 1
            calidad = "❌ MALA"
        elif tiene_concepto_claro and len(preg.pregunta) > 30:
            buenas += 1
            calidad = "✅ BUENA"
        else:
            regulares += 1
            calidad = "⚠️ REGULAR"
        
        print(f"{calidad}: {preg.pregunta[:60]}...")
    
    print()
    print("-"*70)
    print(f"✅ Buenas:    {buenas}/{len(preguntas)} ({buenas*100//len(preguntas)}%)")
    print(f"⚠️ Regulares: {regulares}/{len(preguntas)} ({regulares*100//len(preguntas)}%)")
    print(f"❌ Malas:     {malas}/{len(preguntas)} ({malas*100//len(preguntas)}%)")
    print("-"*70)
    print()
    
    if buenas >= len(preguntas) * 0.6:
        print("🎉 ¡Excelente! La mayoría de preguntas son buenas")
    elif buenas + regulares >= len(preguntas) * 0.7:
        print("👍 Aceptable. Hay margen de mejora pero funciona")
    else:
        print("⚠️ Necesita mejoras. Revisa los logs en logs_generacion/")
    
    print()
    print("="*70)
    print()
    print("💡 CONSEJOS:")
    print()
    print("1. Revisa los logs en 'logs_generacion/' para ver la respuesta cruda del modelo")
    print("2. Si ves muchas preguntas MALAS, el modelo probablemente no está generando JSON")
    print("3. Si ves muchas REGULARES, el fallback está funcionando pero el modelo falla")
    print("4. Si ves muchas BUENAS, ¡las mejoras funcionaron! 🎉")
    print()
    print("="*70)


if __name__ == "__main__":
    prueba_rapida()

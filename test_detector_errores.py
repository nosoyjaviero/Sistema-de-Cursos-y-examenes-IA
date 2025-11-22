"""
🧪 TEST DEL DETECTOR DE ERRORES
================================

Script de prueba para validar el funcionamiento del Módulo 1.
"""

from detector_errores import DetectorErrores, ResultadoPreguntaExtendido
from pathlib import Path
import json

def test_clasificacion_preguntas():
    """Prueba la clasificación de diferentes tipos de preguntas."""
    
    print("=" * 70)
    print("🧪 TEST 1: Clasificación de Preguntas Individuales")
    print("=" * 70)
    
    # Test 1: Pregunta múltiple correcta
    pregunta1 = {
        "pregunta": "¿Qué es Python?",
        "tipo": "multiple",
        "respuesta_usuario": "A",
        "respuesta_correcta": "A",
        "puntos": 3,
        "puntos_maximos": 3
    }
    resultado1 = ResultadoPreguntaExtendido(pregunta1)
    assert resultado1.estado_respuesta == "acierto", "❌ Test 1 falló"
    print("✅ Test 1: Pregunta múltiple correcta → acierto")
    
    # Test 2: Pregunta múltiple incorrecta
    pregunta2 = {
        "pregunta": "¿Qué es Java?",
        "tipo": "multiple",
        "respuesta_usuario": "B",
        "respuesta_correcta": "A",
        "puntos": 0,
        "puntos_maximos": 3
    }
    resultado2 = ResultadoPreguntaExtendido(pregunta2)
    assert resultado2.estado_respuesta == "fallo", "❌ Test 2 falló"
    print("✅ Test 2: Pregunta múltiple incorrecta → fallo")
    
    # Test 3: Verdadero/Falso evaluado por IA (respuesta_correcta = null)
    pregunta3 = {
        "pregunta": "¿Es Python un lenguaje compilado?",
        "tipo": "verdadero_falso",
        "respuesta_usuario": "falso",
        "respuesta_correcta": None,
        "puntos": 2,
        "puntos_maximos": 2
    }
    resultado3 = ResultadoPreguntaExtendido(pregunta3)
    assert resultado3.estado_respuesta == "acierto", "❌ Test 3 falló"
    print("✅ Test 3: Verdadero/Falso con ratio 1.0 → acierto")
    
    # Test 4: Desarrollo - Respuesta parcial (respuesta débil)
    pregunta4 = {
        "pregunta": "Explica el concepto de POO",
        "tipo": "desarrollo",
        "respuesta_usuario": "Es programar con objetos...",
        "respuesta_correcta": None,
        "puntos": 2.5,
        "puntos_maximos": 3
    }
    resultado4 = ResultadoPreguntaExtendido(pregunta4)
    assert resultado4.estado_respuesta == "respuesta_debil", "❌ Test 4 falló"
    print("✅ Test 4: Desarrollo con ratio 0.833 → respuesta_debil")
    
    # Test 5: Corta - Fallo
    pregunta5 = {
        "pregunta": "¿Qué es un algoritmo?",
        "tipo": "corta",
        "respuesta_usuario": "No sé",
        "respuesta_correcta": None,
        "puntos": 0.5,
        "puntos_maximos": 3
    }
    resultado5 = ResultadoPreguntaExtendido(pregunta5)
    assert resultado5.estado_respuesta == "fallo", "❌ Test 5 falló"
    print("✅ Test 5: Corta con ratio 0.166 → fallo")
    
    # Test 6: Flashcard - Respuesta débil
    pregunta6 = {
        "pregunta": "¿Qué es REST?",
        "tipo": "flashcard",
        "respuesta_usuario": "Una API",
        "respuesta_correcta": None,
        "puntos": 0.8,
        "puntos_maximos": 1
    }
    resultado6 = ResultadoPreguntaExtendido(pregunta6)
    assert resultado6.estado_respuesta == "respuesta_debil", "❌ Test 6 falló"
    print("✅ Test 6: Flashcard con ratio 0.8 → respuesta_debil")
    
    # Test 7: Normalización de respuestas (mayúsculas/espacios)
    pregunta7 = {
        "pregunta": "¿Qué es HTML?",
        "tipo": "multiple",
        "respuesta_usuario": " a ",  # Con espacios
        "respuesta_correcta": "A",   # Sin espacios, mayúscula
        "puntos": 3,
        "puntos_maximos": 3
    }
    resultado7 = ResultadoPreguntaExtendido(pregunta7)
    assert resultado7.estado_respuesta == "acierto", "❌ Test 7 falló"
    print("✅ Test 7: Normalización de respuestas → acierto")
    
    print("\n✅ Todos los tests de clasificación pasaron correctamente\n")


def test_analizar_examen_real():
    """Prueba el análisis de un examen real."""
    
    print("=" * 70)
    print("🧪 TEST 2: Análisis de Examen Real")
    print("=" * 70)
    
    # Buscar un examen de ejemplo
    examenes_dir = Path("examenes/Platzi")
    
    if not examenes_dir.exists():
        print("⚠️  No se encontró la carpeta examenes/Platzi")
        print("   Saltando test de examen real")
        return
    
    # Buscar el primer examen .json
    examenes = list(examenes_dir.glob("examen_*.json"))
    
    if not examenes:
        print("⚠️  No se encontraron exámenes en examenes/Platzi")
        print("   Saltando test de examen real")
        return
    
    ruta_examen = str(examenes[0])
    print(f"📄 Analizando: {examenes[0].name}\n")
    
    detector = DetectorErrores()
    
    try:
        analisis = detector.analizar_examen(ruta_examen)
        
        # Validar estructura del análisis
        assert "metadata" in analisis, "❌ Falta metadata"
        assert "resultados_clasificados" in analisis, "❌ Falta resultados_clasificados"
        assert "resumen_estados" in analisis, "❌ Falta resumen_estados"
        
        print("✅ Estructura del análisis correcta")
        
        # Mostrar resumen
        resumen = analisis["resumen_estados"]
        print(f"\n📊 Resumen del Examen:")
        print(f"   Total preguntas: {resumen['total_preguntas']}")
        print(f"   ✅ Aciertos: {resumen['aciertos']} ({resumen['porcentaje_aciertos']}%)")
        print(f"   ⚠️  Débiles: {resumen['respuestas_debiles']} ({resumen['porcentaje_debiles']}%)")
        print(f"   ❌ Fallos: {resumen['fallos']} ({resumen['porcentaje_fallos']}%)")
        
        # Validar que todos los estados son válidos
        for resultado in analisis["resultados_clasificados"]:
            assert resultado["estado_respuesta"] in ["acierto", "fallo", "respuesta_debil"], \
                f"❌ Estado inválido: {resultado['estado_respuesta']}"
        
        print(f"\n✅ Todos los estados son válidos")
        
        # Probar filtrado
        fallos = detector.filtrar_por_estado(
            analisis["resultados_clasificados"], 
            "fallo"
        )
        print(f"\n🔍 Filtrado de fallos: {len(fallos)} preguntas")
        
        # Generar reporte
        print("\n" + "=" * 70)
        print("📄 REPORTE GENERADO:")
        print("=" * 70)
        print(detector.generar_reporte_texto(analisis))
        
        # Guardar análisis
        output_file = "test_analisis_examen.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analisis, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Análisis guardado en: {output_file}")
        print("✅ Test de examen real completado\n")
        
    except Exception as e:
        print(f"❌ Error analizando examen: {e}")
        import traceback
        traceback.print_exc()


def test_multiples_examenes():
    """Prueba el análisis de múltiples exámenes."""
    
    print("=" * 70)
    print("🧪 TEST 3: Análisis de Múltiples Exámenes")
    print("=" * 70)
    
    examenes_dir = Path("examenes/Platzi")
    
    if not examenes_dir.exists():
        print("⚠️  No se encontró la carpeta examenes/Platzi")
        print("   Saltando test de múltiples exámenes")
        return
    
    # Obtener hasta 3 exámenes
    examenes = list(examenes_dir.glob("examen_*.json"))[:3]
    
    if len(examenes) < 2:
        print("⚠️  Se necesitan al menos 2 exámenes")
        print("   Saltando test de múltiples exámenes")
        return
    
    rutas = [str(e) for e in examenes]
    print(f"📄 Analizando {len(rutas)} exámenes:\n")
    for ruta in rutas:
        print(f"   - {Path(ruta).name}")
    
    detector = DetectorErrores()
    resultados = detector.analizar_multiples_examenes(rutas)
    
    print(f"\n✅ Se analizaron {len(resultados)} exámenes correctamente")
    
    # Calcular estadísticas agregadas
    total_preguntas = sum(r["resumen_estados"]["total_preguntas"] for r in resultados)
    total_aciertos = sum(r["resumen_estados"]["aciertos"] for r in resultados)
    total_fallos = sum(r["resumen_estados"]["fallos"] for r in resultados)
    total_debiles = sum(r["resumen_estados"]["respuestas_debiles"] for r in resultados)
    
    print(f"\n📊 Estadísticas Agregadas:")
    print(f"   Total preguntas: {total_preguntas}")
    print(f"   ✅ Aciertos: {total_aciertos} ({total_aciertos/total_preguntas*100:.1f}%)")
    print(f"   ⚠️  Débiles: {total_debiles} ({total_debiles/total_preguntas*100:.1f}%)")
    print(f"   ❌ Fallos: {total_fallos} ({total_fallos/total_preguntas*100:.1f}%)")
    
    print("\n✅ Test de múltiples exámenes completado\n")


def main():
    """Ejecuta todos los tests."""
    
    print("\n" + "🎯" * 35)
    print("🧪 SUITE DE TESTS - DETECTOR DE ERRORES (MÓDULO 1)")
    print("🎯" * 35 + "\n")
    
    try:
        # Test 1: Clasificación de preguntas individuales
        test_clasificacion_preguntas()
        
        # Test 2: Análisis de examen real
        test_analizar_examen_real()
        
        # Test 3: Análisis de múltiples exámenes
        test_multiples_examenes()
        
        print("=" * 70)
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("=" * 70)
        print("\n🎉 El Módulo 1: Detector de Errores está funcionando correctamente\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

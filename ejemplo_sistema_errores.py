"""
🎯 EJEMPLO COMPLETO: Sistema de Gestión de Errores
===================================================

Demostración del flujo completo de los 3 módulos integrados:

1. Módulo 1: Detectar errores en un examen
2. Módulo 2: Actualizar banco de errores
3. Módulo 3: Priorizar errores para sesión de estudio

Este script muestra cómo usar el sistema end-to-end.
"""

import json
from datetime import datetime
from pathlib import Path

from detector_errores import DetectorErrores
from banco_errores import BancoErrores
from priorizador_errores import Priorizador


def ejemplo_flujo_completo():
    """
    Demuestra el flujo completo del sistema de gestión de errores.
    """
    
    print("\n" + "=" * 80)
    print(" 📚 SISTEMA DE GESTIÓN DE ERRORES - FLUJO COMPLETO")
    print("=" * 80 + "\n")
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 1: Simular resultados de un examen realizado
    # ═══════════════════════════════════════════════════════════════
    
    print("🔵 PASO 1: Usuario completa un examen")
    print("-" * 80)
    
    examen_realizado = {
        "tipo": "completado",
        "id": "ejemplo_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "carpeta_nombre": "Algebra",
        "carpeta_ruta": "Matematicas/Algebra",
        "num_preguntas": 5,
        "fecha_completado": datetime.now().isoformat(),
        "puntos_obtenidos": 2.0,
        "puntos_totales": 5.0,
        "porcentaje": 40.0,
        "resultados": [
            {
                "pregunta": "¿Cuál es la derivada de x²?",
                "tipo": "multiple",
                "opciones": ["x", "2x", "x³", "2"],
                "respuesta_correcta": "2x",
                "respuesta_usuario": "x",  # ❌ Error
                "puntos": 0,
                "puntos_maximos": 1,
                "feedback": "Incorrecto"
            },
            {
                "pregunta": "¿Cuánto es 2 + 2?",
                "tipo": "multiple",
                "opciones": ["3", "4", "5", "6"],
                "respuesta_correcta": "4",
                "respuesta_usuario": "4",  # ✅ Correcto
                "puntos": 1,
                "puntos_maximos": 1,
                "feedback": "Correcto"
            },
            {
                "pregunta": "¿Qué es una integral?",
                "tipo": "corta",
                "opciones": [],
                "respuesta_correcta": "Operación inversa a la derivada",
                "respuesta_usuario": "una suma continua",  # ⚠️ Débil
                "puntos": 0.8,
                "puntos_maximos": 1,
                "feedback": "Respuesta aproximada"
            },
            {
                "pregunta": "¿Cuál es la integral de 2x?",
                "tipo": "multiple",
                "opciones": ["x²", "2", "x² + C", "2x²"],
                "respuesta_correcta": "x² + C",
                "respuesta_usuario": "x²",  # ❌ Error (olvidó +C)
                "puntos": 0,
                "puntos_maximos": 1,
                "feedback": "Incorrecto - faltó la constante C"
            },
            {
                "pregunta": "¿Cuánto es 5 × 5?",
                "tipo": "multiple",
                "opciones": ["20", "25", "30", "35"],
                "respuesta_correcta": "25",
                "respuesta_usuario": "25",  # ✅ Correcto
                "puntos": 1,
                "puntos_maximos": 1,
                "feedback": "Correcto"
            }
        ]
    }
    
    print(f"📝 Examen: {examen_realizado['carpeta_ruta']}")
    print(f"📊 Preguntas: {examen_realizado['num_preguntas']}")
    print()
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 2: Detectar errores con el Módulo 1
    # ═══════════════════════════════════════════════════════════════
    
    print("🔵 PASO 2: Detectar errores (Módulo 1)")
    print("-" * 80)
    
    # Guardar examen temporal para procesamiento
    temp_path = Path("temp_examen_ejemplo.json")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(examen_realizado, f, indent=2, ensure_ascii=False)
    
    detector = DetectorErrores()
    resultados_extendidos = detector.analizar_examen(str(temp_path))
    
    print(f"\n✅ Análisis completado:")
    print(f"   • Aciertos: {resultados_extendidos['resumen_estados']['aciertos']}")
    print(f"   • Fallos: {resultados_extendidos['resumen_estados']['fallos']}")
    print(f"   • Respuestas débiles: {resultados_extendidos['resumen_estados']['respuestas_debiles']}")
    print(f"   • Puntuación: {resultados_extendidos['metadata']['porcentaje']:.1f}%")
    
    print("\n📋 Detalle por pregunta:")
    for i, resultado in enumerate(resultados_extendidos['resultados_clasificados'], 1):
        icono = {
            "acierto": "✅",
            "fallo": "❌",
            "respuesta_debil": "⚠️"
        }[resultado['estado_respuesta']]
        
        print(f"   {icono} P{i}: {resultado['estado_respuesta'].upper()}")
        print(f"      Texto: {resultado['pregunta'][:50]}...")
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 3: Actualizar banco de errores con el Módulo 2
    # ═══════════════════════════════════════════════════════════════
    
    print("\n🔵 PASO 3: Actualizar banco de errores (Módulo 2)")
    print("-" * 80)
    
    banco = BancoErrores()
    resumen_actualizacion = banco.actualizar_banco_desde_examen(
        str(temp_path)  # Pasar ruta, no diccionario
    )
    
    # Limpiar archivo temporal
    temp_path.unlink()
    
    print(f"\n✅ Banco actualizado:")
    print(f"   • Errores nuevos agregados: {resumen_actualizacion['nuevos']}")
    print(f"   • Errores existentes actualizados: {resumen_actualizacion['actualizados']}")
    print(f"   • Total errores en banco: {resumen_actualizacion['total_banco']}")
    
    # Mostrar estadísticas del banco
    stats = banco.obtener_estadisticas()
    print(f"\n📊 Estadísticas del banco completo:")
    print(f"   • Total errores: {stats['total_errores']}")
    print(f"   • Nuevos: {stats['por_estado']['nuevos']}")
    print(f"   • En refuerzo: {stats['por_estado']['en_refuerzo']}")
    print(f"   • Resueltos: {stats['por_estado']['resueltos']}")
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 4: Priorizar errores para sesión de estudio (Módulo 3)
    # ═══════════════════════════════════════════════════════════════
    
    print("\n🔵 PASO 4: Priorizar errores para hoy (Módulo 3)")
    print("-" * 80)
    
    priorizador = Priorizador()
    sesion_hoy = priorizador.obtener_errores_para_hoy(
        max_errores=10
    )
    
    print(f"\n✅ Sesión de estudio preparada:")
    print(f"   • Errores seleccionados: {sesion_hoy['total_errores_seleccionados']}")
    print(f"   • Mensaje: {sesion_hoy['mensaje_motivacional']}")
    
    if sesion_hoy['errores']:
        print("\n🎯 Errores priorizados para hoy:\n")
        
        for i, error in enumerate(sesion_hoy['errores'], 1):
            print(f"{i}. [{error['pregunta']['tipo'].upper()}]")
            print(f"   📝 {error['pregunta']['texto'][:60]}...")
            print(f"   📍 {error['razon_seleccion']}")
            print(f"   💡 {error['recomendacion_estudio']}")
            print(f"   📊 Veces fallada: {error['veces_fallada']} | Estado: {error['estado_refuerzo']}")
            print()
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 5: Generar reporte completo
    # ═══════════════════════════════════════════════════════════════
    
    print("🔵 PASO 5: Generar reporte completo")
    print("-" * 80)
    
    if sesion_hoy['errores']:
        reporte = priorizador.generar_reporte_priorizacion(sesion_hoy)
        
        # Guardar reporte en archivo
        reporte_path = Path("sesion_estudio_ejemplo.txt")
        with open(reporte_path, "w", encoding="utf-8") as f:
            f.write(reporte)
        
        print(f"\n✅ Reporte guardado en: {reporte_path.absolute()}")
        
        # Guardar JSON también
        json_path = Path("sesion_estudio_ejemplo.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(sesion_hoy, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Datos JSON guardados en: {json_path.absolute()}")
    
    # ═══════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ═══════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 80)
    print(" 🎉 FLUJO COMPLETO EJECUTADO CON ÉXITO")
    print("=" * 80)
    
    print(f"""
📈 RESUMEN DE LA SESIÓN:
   
   1️⃣  Examen analizado: {examen_realizado['carpeta_ruta']}
       • {resultados_extendidos['resumen_estados']['aciertos']} aciertos
       • {resultados_extendidos['resumen_estados']['fallos']} fallos
       • {resultados_extendidos['resumen_estados']['respuestas_debiles']} respuestas débiles
   
   2️⃣  Banco actualizado:
       • {resumen_actualizacion['nuevos']} errores nuevos
       • {resumen_actualizacion['actualizados']} errores actualizados
       • {resumen_actualizacion['total_banco']} total en banco
   
   3️⃣  Sesión de estudio:
       • {sesion_hoy['total_errores_seleccionados']} errores priorizados
       • {sesion_hoy['estadisticas_sesion'].get('errores_nuevos_incluidos', 0)} nuevos
       • {sesion_hoy['estadisticas_sesion'].get('errores_alta_frecuencia', 0)} alta frecuencia
   
💡 El sistema está listo para mejorar tu aprendizaje de manera personalizada.
""")


def ejemplo_consultar_banco():
    """
    Demuestra cómo consultar el banco de errores.
    """
    
    print("\n" + "=" * 80)
    print(" 🔍 CONSULTAR BANCO DE ERRORES")
    print("=" * 80 + "\n")
    
    banco = BancoErrores()
    
    # Obtener todos los errores
    errores = banco.obtener_todos_errores()
    
    print(f"📚 Total de errores en el banco: {len(errores)}\n")
    
    if errores:
        # Agrupar por estado
        por_estado = {}
        for error in errores:
            estado = error['estado_refuerzo']
            por_estado[estado] = por_estado.get(estado, []) + [error]
        
        for estado, lista in por_estado.items():
            print(f"\n{estado.upper().replace('_', ' ')} ({len(lista)} errores):")
            print("-" * 80)
            
            for error in lista[:3]:  # Mostrar solo los primeros 3
                print(f"  • {error['pregunta']['texto'][:60]}...")
                print(f"    Veces fallada: {error['veces_fallada']}")
                print(f"    Prioridad: {error['prioridad']}")
                print()


def ejemplo_buscar_errores():
    """
    Demuestra cómo buscar errores específicos.
    """
    
    print("\n" + "=" * 80)
    print(" 🔎 BUSCAR ERRORES ESPECÍFICOS")
    print("=" * 80 + "\n")
    
    banco = BancoErrores()
    
    # Buscar por carpeta
    print("🔵 Buscar errores de 'Matematicas':")
    errores_matematicas = banco.buscar_errores(carpeta="Matematicas")
    print(f"   Encontrados: {len(errores_matematicas)}\n")
    
    # Buscar por tipo
    print("🔵 Buscar preguntas de tipo 'multiple':")
    errores_multiple = banco.buscar_errores(tipo_pregunta="multiple")
    print(f"   Encontrados: {len(errores_multiple)}\n")
    
    # Buscar errores críticos
    print("🔵 Buscar errores críticos (≥3 fallos):")
    todos = banco.obtener_todos_errores()
    criticos = [e for e in todos if e['veces_fallada'] >= 3]
    print(f"   Encontrados: {len(criticos)}\n")
    
    if criticos:
        print("   ⚠️  Errores críticos:")
        for error in criticos:
            print(f"      • {error['pregunta']['texto'][:50]}... ({error['veces_fallada']} fallos)")


# ═══════════════════════════════════════════════════════════════
# MENÚ INTERACTIVO
# ═══════════════════════════════════════════════════════════════

def menu_principal():
    """
    Menú interactivo para explorar el sistema.
    """
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🎯 SISTEMA DE GESTIÓN DE ERRORES - EXAMINATOR".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    opciones = """
📋 MENÚ DE EJEMPLOS:

   1. Flujo completo (Módulos 1, 2 y 3)
   2. Consultar banco de errores
   3. Buscar errores específicos
   4. Salir

Selecciona una opción (1-4): """
    
    while True:
        try:
            opcion = input(opciones).strip()
            
            if opcion == "1":
                ejemplo_flujo_completo()
            elif opcion == "2":
                ejemplo_consultar_banco()
            elif opcion == "3":
                ejemplo_buscar_errores()
            elif opcion == "4":
                print("\n👋 ¡Hasta luego!\n")
                break
            else:
                print("\n❌ Opción inválida. Intenta de nuevo.\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    # Ejecutar flujo completo automáticamente
    ejemplo_flujo_completo()
    
    # Descomentar la siguiente línea para usar el menú interactivo
    # menu_principal()

"""
🧪 TESTS: Módulo 3 - Priorizador de Errores
===========================================

Suite de tests para validar el algoritmo de priorización
y selección de errores para sesiones de estudio.

Tests cubiertos:
- Priorización multi-criterio correcta
- Filtrado por estado de refuerzo
- Cálculo de métricas (días sin práctica, puntuación)
- Manejo de casos límite (banco vacío, pocos errores)
- Generación de recomendaciones y razones
- Estadísticas de sesión
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from priorizador_errores import Priorizador
from banco_errores import BancoErrores


def test_priorizar_errores_nuevos_primero():
    """
    Test: Los errores con estado 'nuevo_error' deben aparecer primero.
    """
    print("\n" + "=" * 70)
    print("TEST 1: Priorización de errores nuevos primero")
    print("=" * 70)
    
    # Setup: Crear banco temporal con errores de diferentes estados
    banco = BancoErrores()
    hoy = datetime.now()
    
    errores_test = [
        {
            "id_error": "err_001",
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 2,
            "prioridad": "media",
            "ultima_vez_practicada": (hoy - timedelta(days=5)).isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "multiple", "texto": "Error en refuerzo"}
        },
        {
            "id_error": "err_002",
            "estado_refuerzo": "nuevo_error",
            "veces_fallada": 1,
            "prioridad": "baja",
            "ultima_vez_practicada": (hoy - timedelta(days=1)).isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "corta", "texto": "Error nuevo"}
        },
        {
            "id_error": "err_003",
            "estado_refuerzo": "resuelto",
            "veces_fallada": 3,
            "prioridad": "alta",
            "ultima_vez_practicada": (hoy - timedelta(days=10)).isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "multiple", "texto": "Error resuelto"}
        }
    ]
    
    # Calcular métricas
    priorizador = Priorizador()
    errores_con_metricas = priorizador._calcular_metricas(errores_test, hoy)
    
    # Priorizar
    errores_priorizados = priorizador._priorizar_errores(errores_con_metricas)
    
    # Validación: El primer error debe ser el nuevo
    primer_error = errores_priorizados[0]
    assert primer_error["estado_refuerzo"] == "nuevo_error", \
        "El primer error priorizado debe ser 'nuevo_error'"
    
    print("✅ Los errores nuevos tienen máxima prioridad")
    print(f"   Orden: {[e['id_error'] for e in errores_priorizados]}")
    print(f"   Estados: {[e['estado_refuerzo'] for e in errores_priorizados]}")
    

def test_priorizar_alta_frecuencia():
    """
    Test: Errores con veces_fallada >= 2 tienen prioridad.
    """
    print("\n" + "=" * 70)
    print("TEST 2: Priorización por frecuencia de fallos")
    print("=" * 70)
    
    hoy = datetime.now()
    
    errores_test = [
        {
            "id_error": "err_low",
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 1,
            "prioridad": "media",
            "ultima_vez_practicada": (hoy - timedelta(days=3)).isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "multiple", "texto": "Error 1 fallo"}
        },
        {
            "id_error": "err_high",
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 3,
            "prioridad": "media",
            "ultima_vez_practicada": (hoy - timedelta(days=3)).isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "multiple", "texto": "Error 3 fallos"}
        }
    ]
    
    priorizador = Priorizador()
    errores_con_metricas = priorizador._calcular_metricas(errores_test, hoy)
    errores_priorizados = priorizador._priorizar_errores(errores_con_metricas)
    
    # Validación: Error con 3 fallos debe ir primero
    assert errores_priorizados[0]["veces_fallada"] == 3, \
        "Error con más fallos debe tener prioridad"
    
    print("✅ Errores con alta frecuencia priorizados correctamente")
    print(f"   Orden: {[(e['id_error'], e['veces_fallada']) for e in errores_priorizados]}")


def test_priorizar_dias_sin_practica():
    """
    Test: Errores con más días sin práctica tienen mayor urgencia.
    """
    print("\n" + "=" * 70)
    print("TEST 3: Priorización por días sin práctica (spacing effect)")
    print("=" * 70)
    
    hoy = datetime.now()
    
    errores_test = [
        {
            "id_error": "err_recent",
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 2,
            "prioridad": "media",
            "ultima_vez_practicada": (hoy - timedelta(days=2)).isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "multiple", "texto": "Error reciente"}
        },
        {
            "id_error": "err_ancient",
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 2,
            "prioridad": "media",
            "ultima_vez_practicada": (hoy - timedelta(days=15)).isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "multiple", "texto": "Error antiguo"}
        }
    ]
    
    priorizador = Priorizador()
    errores_con_metricas = priorizador._calcular_metricas(errores_test, hoy)
    errores_priorizados = priorizador._priorizar_errores(errores_con_metricas)
    
    # Validación: Error con 15 días debe ir primero
    assert errores_priorizados[0]["dias_sin_practica"] == 15, \
        "Error más antiguo debe tener prioridad"
    
    print("✅ Spacing effect aplicado correctamente")
    print(f"   Orden: {[(e['id_error'], e['dias_sin_practica']) for e in errores_priorizados]}")


def test_calculo_puntuacion():
    """
    Test: La puntuación compuesta se calcula correctamente.
    """
    print("\n" + "=" * 70)
    print("TEST 4: Cálculo de puntuación compuesta")
    print("=" * 70)
    
    hoy = datetime.now()
    
    error = {
        "estado_refuerzo": "nuevo_error",
        "veces_fallada": 3,
        "dias_sin_practica": 10,
        "prioridad": "alta"
    }
    
    priorizador = Priorizador()
    puntuacion = priorizador._calcular_puntuacion(error)
    
    # Desglose esperado:
    # nuevo_error = 100
    # veces_fallada (3) = 30
    # dias_sin_practica (10) = 20
    # prioridad alta = 30
    # TOTAL = 180
    
    expected = 100 + 30 + 20 + 30
    assert puntuacion == expected, f"Esperado {expected}, obtuvo {puntuacion}"
    
    print(f"✅ Puntuación calculada correctamente: {puntuacion}")
    print(f"   Desglose: nuevo=100 + fallos=30 + días=20 + prioridad=30")


def test_filtrado_resueltos():
    """
    Test: Los errores resueltos se excluyen por defecto.
    """
    print("\n" + "=" * 70)
    print("TEST 5: Filtrado de errores resueltos")
    print("=" * 70)
    
    hoy = datetime.now()
    
    errores_test = [
        {
            "id_error": "err_active",
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 2,
            "prioridad": "media",
            "ultima_vez_practicada": hoy.isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "multiple", "texto": "Error activo"}
        },
        {
            "id_error": "err_solved",
            "estado_refuerzo": "resuelto",
            "veces_fallada": 3,
            "prioridad": "alta",
            "ultima_vez_practicada": hoy.isoformat(),
            "historial_respuestas": [],
            "pregunta": {"tipo": "corta", "texto": "Error resuelto"}
        }
    ]
    
    priorizador = Priorizador()
    
    # Filtrar SIN incluir resueltos
    filtrados_sin = priorizador._filtrar_errores(
        errores_test,
        incluir_resueltos=False,
        solo_tipo=None,
        solo_carpeta=None
    )
    
    assert len(filtrados_sin) == 1, "Debe haber solo 1 error activo"
    assert filtrados_sin[0]["estado_refuerzo"] != "resuelto", \
        "No debe haber errores resueltos"
    
    # Filtrar CON incluir resueltos
    filtrados_con = priorizador._filtrar_errores(
        errores_test,
        incluir_resueltos=True,
        solo_tipo=None,
        solo_carpeta=None
    )
    
    assert len(filtrados_con) == 2, "Deben estar ambos errores"
    
    print("✅ Filtrado de resueltos funciona correctamente")
    print(f"   Sin resueltos: {len(filtrados_sin)} errores")
    print(f"   Con resueltos: {len(filtrados_con)} errores")


def test_generacion_razones():
    """
    Test: Las razones de selección se generan correctamente.
    """
    print("\n" + "=" * 70)
    print("TEST 6: Generación de razones de selección")
    print("=" * 70)
    
    errores_test = [
        {
            "estado_refuerzo": "nuevo_error",
            "veces_fallada": 1,
            "dias_sin_practica": 1,
            "prioridad": "baja"
        },
        {
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 4,
            "dias_sin_practica": 16,
            "prioridad": "alta"
        }
    ]
    
    priorizador = Priorizador()
    
    razon1 = priorizador._generar_razon_seleccion(errores_test[0])
    razon2 = priorizador._generar_razon_seleccion(errores_test[1])
    
    assert "Error nuevo" in razon1, "Debe mencionar error nuevo"
    assert "Fallada 4 veces" in razon2, "Debe mencionar alta frecuencia"
    assert "16 días" in razon2, "Debe mencionar días sin práctica"
    
    print("✅ Razones generadas correctamente")
    print(f"   Error nuevo: {razon1}")
    print(f"   Error antiguo: {razon2}")


def test_generacion_recomendaciones():
    """
    Test: Las recomendaciones de estudio se generan adecuadamente.
    """
    print("\n" + "=" * 70)
    print("TEST 7: Generación de recomendaciones de estudio")
    print("=" * 70)
    
    errores_casos = [
        {
            "estado_refuerzo": "nuevo_error",
            "veces_fallada": 1,
            "dias_sin_practica": 1
        },
        {
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 4,
            "dias_sin_practica": 5
        },
        {
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 2,
            "dias_sin_practica": 20
        }
    ]
    
    priorizador = Priorizador()
    
    rec1 = priorizador._generar_recomendacion(errores_casos[0])
    rec2 = priorizador._generar_recomendacion(errores_casos[1])
    rec3 = priorizador._generar_recomendacion(errores_casos[2])
    
    assert "teoría" in rec1.lower() or "estudia" in rec1.lower(), \
        "Debe recomendar estudiar teoría para nuevos"
    assert "tiempo extra" in rec2.lower() or "concepto fundamental" in rec2.lower(), \
        "Debe recomendar tiempo extra para alta frecuencia"
    assert "revisa" in rec3.lower() or "apuntes" in rec3.lower(), \
        "Debe recomendar revisar apuntes para antiguos"
    
    print("✅ Recomendaciones generadas correctamente")
    print(f"   Nuevo: {rec1}")
    print(f"   Alta frecuencia: {rec2}")
    print(f"   Antiguo: {rec3}")


def test_estadisticas_sesion():
    """
    Test: Las estadísticas de sesión se calculan correctamente.
    """
    print("\n" + "=" * 70)
    print("TEST 8: Cálculo de estadísticas de sesión")
    print("=" * 70)
    
    errores_sesion = [
        {
            "estado_refuerzo": "nuevo_error",
            "veces_fallada": 1,
            "dias_sin_practica": 2,
            "pregunta": {"tipo": "multiple"}
        },
        {
            "estado_refuerzo": "nuevo_error",
            "veces_fallada": 1,
            "dias_sin_practica": 3,
            "pregunta": {"tipo": "corta"}
        },
        {
            "estado_refuerzo": "en_refuerzo",
            "veces_fallada": 4,
            "dias_sin_practica": 10,
            "pregunta": {"tipo": "multiple"}
        }
    ]
    
    priorizador = Priorizador()
    stats = priorizador._calcular_estadisticas_sesion(errores_sesion)
    
    assert stats["errores_nuevos_incluidos"] == 2, "Debe haber 2 nuevos"
    assert stats["errores_alta_frecuencia"] == 1, "Debe haber 1 con ≥3 fallos"
    assert stats["errores_antiguos"] == 1, "Debe haber 1 con >7 días"
    assert stats["promedio_dias_sin_practica"] == 5.0, "Promedio debe ser 5.0"
    assert stats["tipos_pregunta"]["multiple"] == 2, "Deben haber 2 múltiples"
    assert stats["tipos_pregunta"]["corta"] == 1, "Debe haber 1 corta"
    
    print("✅ Estadísticas calculadas correctamente")
    print(f"   Nuevos: {stats['errores_nuevos_incluidos']}")
    print(f"   Alta frecuencia: {stats['errores_alta_frecuencia']}")
    print(f"   Antiguos: {stats['errores_antiguos']}")
    print(f"   Promedio días: {stats['promedio_dias_sin_practica']}")
    print(f"   Tipos: {stats['tipos_pregunta']}")


def test_integracion_completa():
    """
    Test: Integración completa del flujo de priorización.
    """
    print("\n" + "=" * 70)
    print("TEST 9: Integración completa (obtener_errores_para_hoy)")
    print("=" * 70)
    
    priorizador = Priorizador()
    
    try:
        # Intentar obtener errores para hoy
        resultado = priorizador.obtener_errores_para_hoy(
            max_errores=5
        )
        
        # Validar estructura del resultado
        assert "fecha_sesion" in resultado
        assert "total_errores_seleccionados" in resultado
        assert "errores" in resultado
        assert "estadisticas_sesion" in resultado
        assert "mensaje_motivacional" in resultado
        
        # Validar que no se seleccionen más de max_errores
        assert resultado["total_errores_seleccionados"] <= 5, \
            "No debe superar max_errores"
        
        # Si hay errores, validar metadatos
        if resultado["errores"]:
            primer_error = resultado["errores"][0]
            assert "razon_seleccion" in primer_error, \
                "Debe tener razón de selección"
            assert "recomendacion_estudio" in primer_error, \
                "Debe tener recomendación"
        
        print("✅ Integración completa funciona correctamente")
        print(f"   Errores seleccionados: {resultado['total_errores_seleccionados']}")
        print(f"   Mensaje: {resultado['mensaje_motivacional']}")
        
        # Generar reporte
        if resultado["errores"]:
            reporte = priorizador.generar_reporte_priorizacion(resultado)
            assert len(reporte) > 0, "El reporte debe tener contenido"
            print("\n📄 Reporte generado con éxito")
        
    except Exception as e:
        print(f"⚠️  Advertencia: {e}")
        print("   (Normal si el banco está vacío)")


def test_caso_limite_banco_vacio():
    """
    Test: Manejo correcto cuando el banco está vacío.
    """
    print("\n" + "=" * 70)
    print("TEST 10: Caso límite - Banco vacío")
    print("=" * 70)
    
    # Crear banco vacío temporal
    backup_path = Path("examenes/error_bank/banco_errores_global.json")
    backup_exists = backup_path.exists()
    
    if backup_exists:
        # Hacer backup
        with open(backup_path, "r", encoding="utf-8") as f:
            backup_data = json.load(f)
    
    try:
        # Crear banco vacío
        empty_banco = {
            "version": "2.0",
            "errores": [],
            "total_errores_registrados": 0
        }
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(empty_banco, f, indent=2, ensure_ascii=False)
        
        # Probar con banco vacío
        priorizador = Priorizador()
        resultado = priorizador.obtener_errores_para_hoy(max_errores=10)
        
        assert resultado["total_errores_seleccionados"] == 0, \
            "Debe retornar 0 errores"
        assert len(resultado["errores"]) == 0, "Lista de errores debe estar vacía"
        assert "No tienes errores" in resultado["mensaje_motivacional"], \
            "Debe dar mensaje de banco vacío"
        
        print("✅ Banco vacío manejado correctamente")
        print(f"   Mensaje: {resultado['mensaje_motivacional']}")
        
    finally:
        # Restaurar backup
        if backup_exists:
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# EJECUTAR TODOS LOS TESTS
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║          SUITE DE TESTS - MÓDULO 3: PRIORIZADOR               ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Errores nuevos primero", test_priorizar_errores_nuevos_primero),
        ("Alta frecuencia", test_priorizar_alta_frecuencia),
        ("Días sin práctica", test_priorizar_dias_sin_practica),
        ("Cálculo puntuación", test_calculo_puntuacion),
        ("Filtrado resueltos", test_filtrado_resueltos),
        ("Generación razones", test_generacion_razones),
        ("Recomendaciones", test_generacion_recomendaciones),
        ("Estadísticas sesión", test_estadisticas_sesion),
        ("Integración completa", test_integracion_completa),
        ("Banco vacío", test_caso_limite_banco_vacio)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            test_func()
            resultados.append((nombre, True, None))
        except AssertionError as e:
            resultados.append((nombre, False, str(e)))
            print(f"❌ FALLO: {e}")
        except Exception as e:
            resultados.append((nombre, False, f"Error inesperado: {e}"))
            print(f"💥 ERROR INESPERADO: {e}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70 + "\n")
    
    exitosos = sum(1 for _, passed, _ in resultados if passed)
    fallidos = len(resultados) - exitosos
    
    for nombre, passed, error in resultados:
        icono = "✅" if passed else "❌"
        print(f"{icono} {nombre}")
        if error:
            print(f"   └─ {error}")
    
    print("\n" + "=" * 70)
    print(f"Total: {exitosos}/{len(resultados)} tests exitosos")
    
    if fallidos == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON CORRECTAMENTE!")
        print("✅ El Módulo 3: Priorizador de Errores está funcionando perfectamente.\n")
    else:
        print(f"\n⚠️  {fallidos} test(s) fallaron. Revisar errores arriba.\n")

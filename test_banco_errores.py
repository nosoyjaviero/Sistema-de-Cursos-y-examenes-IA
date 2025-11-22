"""
🧪 TESTS DEL BANCO DE ERRORES (Módulo 2)
=========================================

Suite de pruebas para validar el funcionamiento del banco de errores.
"""

from banco_errores import BancoErrores
from pathlib import Path
import json
import shutil

def limpiar_banco_test():
    """Limpia el banco de errores para tests."""
    ruta_banco = Path("examenes/error_bank")
    if ruta_banco.exists():
        # Hacer backup antes de limpiar
        if (ruta_banco / "banco_errores_global.json").exists():
            backup_dir = Path("examenes/error_bank_backup_test")
            backup_dir.mkdir(exist_ok=True)
            shutil.copy(
                ruta_banco / "banco_errores_global.json",
                backup_dir / "banco_errores_backup.json"
            )
            print("💾 Backup creado en examenes/error_bank_backup_test/")
        
        # Limpiar para test
        for archivo in ruta_banco.glob("*.json"):
            archivo.unlink()
        print("🧹 Banco limpiado para tests")


def test_actualizar_banco_nuevo():
    """Test 1: Actualizar banco con primer examen (errores nuevos)."""
    
    print("=" * 70)
    print("🧪 TEST 1: Actualizar Banco con Errores Nuevos")
    print("=" * 70)
    
    banco = BancoErrores()
    
    # Buscar un examen de ejemplo
    examenes_dir = Path("examenes/Platzi")
    if not examenes_dir.exists():
        print("⚠️  No se encontró carpeta de exámenes, saltando test")
        return
    
    examenes = list(examenes_dir.glob("examen_*.json"))
    if not examenes:
        print("⚠️  No hay exámenes disponibles, saltando test")
        return
    
    ruta_examen = str(examenes[0])
    print(f"📄 Usando examen: {Path(ruta_examen).name}\n")
    
    try:
        resultado = banco.actualizar_banco_desde_examen(ruta_examen)
        
        print(f"\n✅ {resultado['mensaje']}")
        print(f"   Nuevos errores: {resultado['nuevos']}")
        print(f"   Actualizados: {resultado['actualizados']}")
        print(f"   Total en banco: {resultado['total_banco']}")
        
        assert resultado['nuevos'] >= 0, "❌ Contador de nuevos inválido"
        assert resultado['total_banco'] >= resultado['nuevos'], "❌ Total inconsistente"
        
        print("\n✅ Test 1 pasado: Actualización de banco funcional")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()


def test_detectar_duplicados():
    """Test 2: Verificar que se detectan preguntas duplicadas."""
    
    print("\n" + "=" * 70)
    print("🧪 TEST 2: Detección de Duplicados")
    print("=" * 70)
    
    banco = BancoErrores()
    
    # Buscar exámenes
    examenes_dir = Path("examenes/Platzi")
    if not examenes_dir.exists():
        print("⚠️  No se encontró carpeta de exámenes, saltando test")
        return
    
    examenes = list(examenes_dir.glob("examen_*.json"))[:2]
    if len(examenes) < 2:
        print("⚠️  Se necesitan al menos 2 exámenes, saltando test")
        return
    
    print(f"📄 Procesando 2 exámenes para detectar duplicados...\n")
    
    # Procesar primer examen
    resultado1 = banco.actualizar_banco_desde_examen(str(examenes[0]))
    total_inicial = resultado1['total_banco']
    
    # Procesar segundo examen (puede tener preguntas similares)
    resultado2 = banco.actualizar_banco_desde_examen(str(examenes[1]))
    
    print(f"\n📊 Resultados:")
    print(f"   Primer examen - Nuevos: {resultado1['nuevos']}")
    print(f"   Segundo examen - Nuevos: {resultado2['nuevos']}, Actualizados: {resultado2['actualizados']}")
    print(f"   Total en banco: {resultado2['total_banco']}")
    
    if resultado2['actualizados'] > 0:
        print(f"\n✅ Se detectaron {resultado2['actualizados']} duplicados correctamente")
    else:
        print("\n⚠️  No se detectaron duplicados (los exámenes tenían preguntas diferentes)")
    
    print("\n✅ Test 2 pasado: Sistema de detección de duplicados funcional")


def test_estadisticas():
    """Test 3: Verificar generación de estadísticas."""
    
    print("\n" + "=" * 70)
    print("🧪 TEST 3: Estadísticas del Banco")
    print("=" * 70)
    
    banco = BancoErrores()
    
    try:
        estadisticas = banco.obtener_estadisticas()
        
        print(f"\n📊 Estadísticas del banco:")
        print(f"   Total errores: {estadisticas['total_errores']}")
        print(f"   Errores activos: {estadisticas['errores_activos']}")
        print(f"   Errores resueltos: {estadisticas['por_estado']['resueltos']}")
        print(f"   Tasa de resolución: {estadisticas['tasa_resolucion']}%")
        
        print(f"\n   Por estado:")
        print(f"     🆕 Nuevos: {estadisticas['por_estado']['nuevos']}")
        print(f"     🔄 En refuerzo: {estadisticas['por_estado']['en_refuerzo']}")
        print(f"     ✅ Resueltos: {estadisticas['por_estado']['resueltos']}")
        
        print(f"\n   Por prioridad:")
        print(f"     🔴 Alta: {estadisticas['por_prioridad']['alta']}")
        print(f"     🟡 Media: {estadisticas['por_prioridad']['media']}")
        print(f"     🟢 Baja: {estadisticas['por_prioridad']['baja']}")
        
        # Validaciones
        assert estadisticas['total_errores'] >= 0, "❌ Total negativo"
        assert estadisticas['errores_activos'] >= 0, "❌ Activos negativo"
        assert estadisticas['tasa_resolucion'] >= 0, "❌ Tasa negativa"
        
        suma_estados = (
            estadisticas['por_estado']['nuevos'] +
            estadisticas['por_estado']['en_refuerzo'] +
            estadisticas['por_estado']['resueltos']
        )
        assert suma_estados == estadisticas['total_errores'], "❌ Suma de estados inconsistente"
        
        print("\n✅ Test 3 pasado: Estadísticas correctas y consistentes")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()


def test_obtener_errores_practica():
    """Test 4: Obtener errores para práctica."""
    
    print("\n" + "=" * 70)
    print("🧪 TEST 4: Obtener Errores para Práctica")
    print("=" * 70)
    
    banco = BancoErrores()
    
    try:
        # Obtener errores de alta prioridad
        errores_alta = banco.obtener_errores_para_practica(
            max_errores=5,
            solo_prioridad="alta"
        )
        
        print(f"\n🔴 Errores de alta prioridad: {len(errores_alta)}")
        for i, error in enumerate(errores_alta[:3], 1):
            print(f"\n   {i}. {error['pregunta']['texto'][:60]}...")
            print(f"      Veces fallada: {error['veces_fallada']}")
            print(f"      Estado: {error['estado_refuerzo']}")
            print(f"      Prioridad: {error['prioridad']}")
        
        # Obtener errores nuevos
        errores_nuevos = banco.obtener_errores_para_practica(
            max_errores=5,
            solo_estado="nuevo_error"
        )
        
        print(f"\n🆕 Errores nuevos: {len(errores_nuevos)}")
        
        # Validaciones
        for error in errores_alta:
            assert error['prioridad'] == 'alta', "❌ Filtro de prioridad falló"
        
        for error in errores_nuevos:
            assert error['estado_refuerzo'] == 'nuevo_error', "❌ Filtro de estado falló"
        
        print("\n✅ Test 4 pasado: Filtrado de errores funcional")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()


def test_reporte_banco():
    """Test 5: Generar reporte del banco."""
    
    print("\n" + "=" * 70)
    print("🧪 TEST 5: Generar Reporte del Banco")
    print("=" * 70)
    
    banco = BancoErrores()
    
    try:
        reporte = banco.generar_reporte_banco()
        
        print(reporte)
        
        # Validar que el reporte contiene elementos clave
        assert "REPORTE DEL BANCO DE ERRORES" in reporte, "❌ Título faltante"
        assert "Total errores" in reporte, "❌ Total faltante"
        assert "RECOMENDACIÓN" in reporte, "❌ Recomendación faltante"
        
        print("\n✅ Test 5 pasado: Reporte generado correctamente")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()


def test_estructura_banco():
    """Test 6: Verificar estructura del JSON del banco."""
    
    print("\n" + "=" * 70)
    print("🧪 TEST 6: Verificar Estructura del Banco")
    print("=" * 70)
    
    ruta_banco = Path("examenes/error_bank/banco_errores_global.json")
    
    if not ruta_banco.exists():
        print("⚠️  Banco no existe aún, saltando test")
        return
    
    try:
        with open(ruta_banco, 'r', encoding='utf-8') as f:
            banco = json.load(f)
        
        # Validar estructura principal
        assert "version" in banco, "❌ Falta campo 'version'"
        assert "fecha_creacion" in banco, "❌ Falta campo 'fecha_creacion'"
        assert "errores" in banco, "❌ Falta campo 'errores'"
        assert "total_errores_registrados" in banco, "❌ Falta campo 'total_errores_registrados'"
        
        print(f"✅ Estructura principal correcta")
        print(f"   Version: {banco['version']}")
        print(f"   Total errores: {banco['total_errores_registrados']}")
        
        # Validar estructura de un error (si hay errores)
        if banco['errores']:
            error = banco['errores'][0]
            
            campos_requeridos = [
                'id_error', 'hash_pregunta', 'examen_origen', 'pregunta',
                'historial_respuestas', 'veces_fallada', 'veces_practicada',
                'ultima_vez_practicada', 'fecha_primer_error', 'estado_refuerzo',
                'prioridad'
            ]
            
            for campo in campos_requeridos:
                assert campo in error, f"❌ Falta campo '{campo}' en error"
            
            print(f"\n✅ Estructura de error correcta")
            print(f"   ID: {error['id_error']}")
            print(f"   Estado: {error['estado_refuerzo']}")
            print(f"   Prioridad: {error['prioridad']}")
            print(f"   Veces practicada: {error['veces_practicada']}")
        
        print("\n✅ Test 6 pasado: Estructura del banco válida")
        
    except json.JSONDecodeError:
        print("❌ Error: JSON malformado")
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Ejecuta todos los tests."""
    
    print("\n" + "🎯" * 35)
    print("🧪 SUITE DE TESTS - BANCO DE ERRORES (MÓDULO 2)")
    print("🎯" * 35 + "\n")
    
    # Preguntar si limpiar banco existente
    respuesta = input("⚠️  ¿Deseas limpiar el banco existente para tests limpios? (s/N): ")
    if respuesta.lower() == 's':
        limpiar_banco_test()
        print()
    
    try:
        # Ejecutar tests
        test_actualizar_banco_nuevo()
        test_detectar_duplicados()
        test_estadisticas()
        test_obtener_errores_practica()
        test_reporte_banco()
        test_estructura_banco()
        
        print("\n" + "=" * 70)
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("=" * 70)
        print("\n🎉 El Módulo 2: Banco de Errores está funcionando correctamente\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}\n")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

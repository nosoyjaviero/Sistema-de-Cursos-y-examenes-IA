"""
🎯 Script para Procesar el Último Examen Completado
====================================================

Encuentra automáticamente el examen más reciente y:
1. Detecta errores (Módulo 1)
2. Actualiza banco de errores (Módulo 2)  
3. Muestra sesión de estudio recomendada (Módulo 3)
"""

import json
from pathlib import Path
from datetime import datetime

from detector_errores import DetectorErrores
from banco_errores import BancoErrores
from priorizador_errores import Priorizador


def encontrar_ultimo_examen():
    """Encuentra el examen completado más reciente."""
    examenes_dir = Path("examenes")
    
    # Buscar todos los archivos JSON de exámenes
    examenes = []
    for archivo in examenes_dir.rglob("examen_*.json"):
        if "banco" not in archivo.name:
            examenes.append(archivo)
    
    if not examenes:
        return None
    
    # Ordenar por fecha de modificación (más reciente primero)
    examenes.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return examenes[0]


def procesar_ultimo_examen():
    """Procesa el examen más reciente con los 3 módulos."""
    
    print("\n" + "=" * 80)
    print("🔍 BUSCANDO ÚLTIMO EXAMEN COMPLETADO...")
    print("=" * 80 + "\n")
    
    # PASO 1: Encontrar examen
    ruta_examen = encontrar_ultimo_examen()
    
    if not ruta_examen:
        print("❌ No se encontraron exámenes en la carpeta 'examenes/'")
        return
    
    print(f"✅ Examen encontrado: {ruta_examen.name}")
    print(f"   Ruta: {ruta_examen}")
    print(f"   Carpeta: {ruta_examen.parent.name}\n")
    
    # Verificar que esté completado
    with open(ruta_examen, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    if datos.get("tipo") != "completado":
        print(f"⚠️  Este examen no está completado (tipo: {datos.get('tipo')})")
        print("   Solo se pueden procesar exámenes completados.")
        return
    
    # PASO 2: Analizar con Módulo 1 (Detector)
    print("=" * 80)
    print("📊 MÓDULO 1: DETECCIÓN DE ERRORES")
    print("=" * 80 + "\n")
    
    detector = DetectorErrores()
    resultados = detector.analizar_examen(str(ruta_examen))
    
    print(f"📝 Examen: {resultados['metadata']['carpeta']}")
    print(f"📅 Fecha: {resultados['metadata']['fecha_completado']}")
    print(f"🎯 Puntuación: {resultados['metadata']['puntos_obtenidos']}/{resultados['metadata']['puntos_totales']} ({resultados['metadata']['porcentaje']:.1f}%)\n")
    
    print(f"📊 Resultados:")
    print(f"   ✅ Aciertos: {resultados['resumen_estados']['aciertos']}")
    print(f"   ❌ Fallos: {resultados['resumen_estados']['fallos']}")
    print(f"   ⚠️  Respuestas débiles: {resultados['resumen_estados']['respuestas_debiles']}")
    
    # Mostrar detalle de errores
    errores_y_debiles = [
        p for p in resultados['resultados_clasificados']
        if p['estado_respuesta'] in ['fallo', 'respuesta_debil']
    ]
    
    if errores_y_debiles:
        print(f"\n❌ ERRORES DETECTADOS ({len(errores_y_debiles)}):")
        print("-" * 80)
        for i, pregunta in enumerate(errores_y_debiles, 1):
            icono = "❌" if pregunta['estado_respuesta'] == 'fallo' else "⚠️"
            print(f"\n{i}. {icono} [{pregunta['tipo'].upper()}]")
            print(f"   Pregunta: {pregunta['pregunta'][:70]}...")
            print(f"   Tu respuesta: {pregunta['respuesta_usuario']}")
            if pregunta.get('respuesta_correcta'):
                print(f"   Correcta: {pregunta['respuesta_correcta']}")
            print(f"   Puntos: {pregunta['puntos']}/{pregunta['puntos_maximos']}")
    else:
        print("\n🎉 ¡No hubo errores! Examen perfecto.")
    
    # PASO 3: Actualizar banco (Módulo 2)
    print("\n" + "=" * 80)
    print("💾 MÓDULO 2: ACTUALIZANDO BANCO DE ERRORES")
    print("=" * 80 + "\n")
    
    banco = BancoErrores()
    resumen = banco.actualizar_banco_desde_examen(str(ruta_examen))
    
    print(f"\n✅ Banco actualizado:")
    print(f"   • Errores nuevos agregados: {resumen['nuevos']}")
    print(f"   • Errores actualizados: {resumen['actualizados']}")
    print(f"   • Total en banco: {resumen['total_banco']}")
    
    # PASO 4: Obtener sesión de estudio (Módulo 3)
    print("\n" + "=" * 80)
    print("🎯 MÓDULO 3: SESIÓN DE ESTUDIO RECOMENDADA")
    print("=" * 80 + "\n")
    
    priorizador = Priorizador()
    sesion = priorizador.obtener_errores_para_hoy(max_errores=10)
    
    print(f"💬 {sesion['mensaje_motivacional']}\n")
    print(f"📊 Composición de la sesión:")
    print(f"   • Errores nuevos: {sesion['estadisticas_sesion'].get('errores_nuevos_incluidos', 0)}")
    print(f"   • Alta frecuencia (≥3 fallos): {sesion['estadisticas_sesion'].get('errores_alta_frecuencia', 0)}")
    print(f"   • Antiguos (>7 días): {sesion['estadisticas_sesion'].get('errores_antiguos', 0)}")
    
    if sesion['errores']:
        print(f"\n🎓 ERRORES PRIORIZADOS PARA HOY ({len(sesion['errores'])}):")
        print("=" * 80)
        
        for i, error in enumerate(sesion['errores'][:5], 1):  # Mostrar primeros 5
            print(f"\n{i}. [{error['pregunta']['tipo'].upper()}]")
            print(f"   📝 {error['pregunta']['texto'][:70]}...")
            print(f"   📍 {error['razon_seleccion']}")
            print(f"   💡 {error['recomendacion_estudio']}")
            print(f"   📊 Veces fallada: {error['veces_fallada']} | Días sin práctica: {error['dias_sin_practica']}")
        
        if len(sesion['errores']) > 5:
            print(f"\n   ... y {len(sesion['errores']) - 5} errores más.")
    
    # PASO 5: Guardar reporte
    print("\n" + "=" * 80)
    print("💾 GUARDANDO REPORTES")
    print("=" * 80 + "\n")
    
    # Guardar JSON
    output_json = Path("mi_sesion_estudio.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(sesion, f, indent=2, ensure_ascii=False)
    print(f"✅ Sesión guardada: {output_json.absolute()}")
    
    # Guardar TXT
    if sesion['errores']:
        reporte_txt = priorizador.generar_reporte_priorizacion(sesion)
        output_txt = Path("mi_sesion_estudio.txt")
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(reporte_txt)
        print(f"✅ Reporte guardado: {output_txt.absolute()}")
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📈 RESUMEN FINAL")
    print("=" * 80)
    print(f"""
✅ Examen procesado: {ruta_examen.name}
   • Aciertos: {resultados['resumen_estados']['aciertos']}
   • Fallos: {resultados['resumen_estados']['fallos']}
   • Débiles: {resultados['resumen_estados']['respuestas_debiles']}

✅ Banco actualizado:
   • +{resumen['nuevos']} nuevos errores
   • ~{resumen['actualizados']} errores actualizados
   • {resumen['total_banco']} total en banco

✅ Sesión preparada:
   • {sesion['total_errores_seleccionados']} errores priorizados
   • Listos para practicar

💡 Próximo paso: Revisa "mi_sesion_estudio.txt" para ver tu plan de estudio.
""")


if __name__ == "__main__":
    try:
        procesar_ultimo_examen()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

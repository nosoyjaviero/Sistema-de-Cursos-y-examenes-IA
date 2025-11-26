"""
Demostración del flujo completo: Generar y Calificar
Este script simula el flujo real que experimentará un usuario
"""
import requests
import json
from pathlib import Path
from datetime import datetime

API_URL = "http://localhost:8000"

def mostrar_separador(texto):
    print("\n" + "="*70)
    print(f"  {texto}")
    print("="*70 + "\n")

def demo_flujo_completo():
    mostrar_separador("🎬 DEMOSTRACIÓN: FLUJO COMPLETO DE USUARIO")
    
    # Simular que el usuario tiene una carpeta de estudio
    carpeta_estudio = "Juan de La torre"
    
    print(f"👤 Usuario trabajando en carpeta: '{carpeta_estudio}'")
    print(f"📁 Ubicación: extracciones/{carpeta_estudio}/")
    
    # Paso 1: Generar práctica (simulado - en realidad viene del generador)
    mostrar_separador("1️⃣  GENERAR PRÁCTICA (simulado)")
    
    preguntas_generadas = [
        {
            "id": 1,
            "tipo": "multiple",
            "pregunta": "¿Cuál es el concepto principal de programación orientada a objetos?",
            "opciones": ["Encapsulamiento", "Goto", "Variables globales", "Procedimientos"],
            "respuesta_correcta": "Encapsulamiento",
            "puntos": 10,
            "metadata": {}
        },
        {
            "id": 2,
            "tipo": "verdadero_falso",
            "pregunta": "Python es un lenguaje de tipado fuerte",
            "respuesta_correcta": "Verdadero",
            "puntos": 5,
            "metadata": {}
        },
        {
            "id": 3,
            "tipo": "corta",
            "pregunta": "¿Qué significa POO?",
            "respuesta_correcta": "Programación Orientada a Objetos",
            "puntos": 10,
            "metadata": {}
        },
        {
            "id": 4,
            "tipo": "multiple",
            "pregunta": "¿Qué es una clase en POO?",
            "opciones": ["Una plantilla", "Una función", "Un archivo", "Un error"],
            "respuesta_correcta": "Una plantilla",
            "puntos": 10,
            "metadata": {}
        }
    ]
    
    print(f"✅ Práctica generada con {len(preguntas_generadas)} preguntas")
    print(f"📊 Puntos totales: {sum(p['puntos'] for p in preguntas_generadas)}")
    
    # Paso 2: Usuario responde las preguntas
    mostrar_separador("2️⃣  USUARIO RESPONDE PREGUNTAS")
    
    respuestas_usuario = {
        "0": "Encapsulamiento",     # ✅ Correcta
        "1": "Falso",               # ❌ Incorrecta (debería ser Verdadero)
        "2": "Programación Orientada a Objetos",  # ✅ Correcta
        "3": "Una plantilla"        # ✅ Correcta
    }
    
    for idx, respuesta in respuestas_usuario.items():
        print(f"   Pregunta {int(idx)+1}: {respuesta}")
    
    # Paso 3: Enviar para calificar
    mostrar_separador("3️⃣  CALIFICAR PRÁCTICA")
    
    print("📤 Enviando respuestas al servidor...")
    
    response = requests.post(
        f"{API_URL}/api/evaluar-examen",
        json={
            "preguntas": preguntas_generadas,
            "respuestas": respuestas_usuario,
            "carpeta_path": carpeta_estudio,
            "es_practica": True
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Práctica calificada exitosamente")
        print(f"")
        print(f"   📊 Puntos obtenidos: {data['puntos_obtenidos']}")
        print(f"   📈 Puntos totales:   {data['puntos_totales']}")
        print(f"   🎯 Porcentaje:       {data['porcentaje']:.1f}%")
        
        # Mostrar resultados por pregunta
        print(f"\n   📝 Detalles por pregunta:")
        for i, resultado in enumerate(data['resultados'], 1):
            emoji = "✅" if resultado['puntos'] > 0 else "❌"
            print(f"      {emoji} Pregunta {i}: {resultado['puntos']}/{resultado['puntos_maximos']} puntos")
        
        # Paso 4: Verificar dónde se guardó
        mostrar_separador("4️⃣  VERIFICAR GUARDADO")
        
        carpeta_resultados = Path("extracciones") / carpeta_estudio / "resultados_practicas"
        
        if carpeta_resultados.exists():
            archivos = list(carpeta_resultados.glob("*.json"))
            archivo_mas_reciente = max(archivos, key=lambda x: x.stat().st_mtime)
            
            print(f"✅ Resultado guardado en:")
            print(f"   📁 {carpeta_resultados}")
            print(f"   📄 {archivo_mas_reciente.name}")
            print(f"")
            
            # Leer el archivo guardado
            with open(archivo_mas_reciente, 'r', encoding='utf-8') as f:
                contenido = json.load(f)
            
            print(f"   📋 Contenido del archivo:")
            print(f"      ID:               {contenido['id']}")
            print(f"      Carpeta:          {contenido['carpeta_nombre']}")
            print(f"      Fecha:            {contenido['fecha_completado'][:19]}")
            print(f"      Es práctica:      {contenido['es_practica']}")
            print(f"      Próxima revisión: {contenido['proximaRevision'][:19]}")
            print(f"      Intervalo:        {contenido['intervalo']} día(s)")
            print(f"")
            
            # Mostrar estructura completa de archivos
            mostrar_separador("5️⃣  ESTRUCTURA FINAL DE LA CARPETA")
            
            print(f"📁 extracciones/{carpeta_estudio}/")
            
            # Listar todos los archivos y subcarpetas
            carpeta_base = Path("extracciones") / carpeta_estudio
            for item in sorted(carpeta_base.rglob("*")):
                if item.is_file():
                    relpath = item.relative_to(carpeta_base)
                    indent = "   " * (len(relpath.parts) - 1)
                    if relpath.parts[0].startswith("resultados_"):
                        print(f"   {indent}📄 {relpath}")
            
            print("")
            print(f"✨ Todo el contenido de estudio está organizado en un solo lugar!")
            
        else:
            print(f"❌ No se encontró la carpeta: {carpeta_resultados}")
    
    else:
        print(f"❌ Error al calificar: {response.status_code}")
        print(response.text)
    
    mostrar_separador("✅ DEMOSTRACIÓN COMPLETADA")
    print("🎯 Resumen:")
    print("   1. Usuario genera práctica desde una carpeta")
    print("   2. Usuario responde las preguntas")
    print("   3. Sistema califica automáticamente")
    print("   4. Resultado se guarda en: extracciones/[carpeta]/resultados_practicas/")
    print("   5. Todo queda organizado en la misma ubicación")
    print("")

if __name__ == "__main__":
    try:
        demo_flujo_completo()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

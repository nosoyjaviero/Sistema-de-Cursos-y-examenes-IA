"""
Test Controlado de Generación de Práctica con Spaced Repetition

Genera una práctica de prueba con 2 flashcards y 1 MCQ, verificando que:
1. Todos los campos de Spaced Repetition están presentes
2. practicas.json se actualiza correctamente
3. No hay estructuras nulas
"""

import requests
import json
from pathlib import Path
import time

# Configuración
API_URL = "http://localhost:8000"
CARPETA_PRUEBA = "Platzi"

def print_separador():
    print("\n" + "="*80 + "\n")

def test_generar_practica():
    """Test principal de generación de práctica"""
    print_separador()
    print("🧪 TEST CONTROLADO - GENERACIÓN DE PRÁCTICA CON SPACED REPETITION")
    print_separador()
    
    # PASO 1: Verificar estado inicial
    print("📋 PASO 1: Verificar estado inicial de practicas.json")
    practicas_path = Path(f"extracciones/{CARPETA_PRUEBA}/practicas.json")
    
    if practicas_path.exists():
        with open(practicas_path, 'r', encoding='utf-8') as f:
            practicas_inicial = json.load(f)
        print(f"   ✅ Archivo existe")
        print(f"   📊 Prácticas actuales: {len(practicas_inicial)}")
    else:
        print(f"   ⚠️  Archivo no existe aún")
        practicas_inicial = []
    
    # PASO 2: Generar práctica de prueba
    print_separador()
    print("📋 PASO 2: Generar práctica (2 flashcards + 1 MCQ)")
    
    payload = {
        "ruta": CARPETA_PRUEBA,
        "prompt": "Genera preguntas sobre conceptos básicos de programación y diseño",
        "num_flashcards": 2,
        "tipo_flashcard": "respuesta_corta",
        "num_mcq": 1,
        "num_verdadero_falso": 0,
        "num_cloze": 0,
        "num_respuesta_corta": 0,
        "num_open_question": 0,
        "num_caso_estudio": 0,
        "session_id": f"test_controlado_{int(time.time())}"
    }
    
    print(f"   📤 Enviando solicitud a POST /api/generar_practica")
    print(f"   📊 Configuración: 2 flashcards + 1 MCQ")
    
    try:
        response = requests.post(
            f"{API_URL}/api/generar_practica",
            json=payload,
            timeout=300  # 5 minutos de timeout
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"   ✅ Respuesta exitosa")
            print(f"   📝 Preguntas generadas: {resultado.get('total_preguntas', 0)}")
            
            # PASO 3: Verificar campos en cada pregunta
            print_separador()
            print("📋 PASO 3: Verificar campos de Spaced Repetition")
            
            preguntas = resultado.get('preguntas', [])
            campos_requeridos = ['id', 'ease_factor', 'interval', 'repetitions', 'next_review', 'last_review', 'state']
            
            errores = []
            for i, pregunta in enumerate(preguntas):
                print(f"\n   🔍 Pregunta {i+1} (tipo: {pregunta.get('tipo', 'desconocido')})")
                
                # Verificar cada campo requerido
                for campo in campos_requeridos:
                    if campo in pregunta:
                        valor = pregunta[campo]
                        print(f"      ✅ {campo}: {valor}")
                    else:
                        error_msg = f"      ❌ FALTA campo '{campo}' en pregunta {i+1}"
                        print(error_msg)
                        errores.append(error_msg)
                
                # Verificar valores por defecto
                if pregunta.get('ease_factor') != 2.5:
                    errores.append(f"      ⚠️  ease_factor debería ser 2.5, es {pregunta.get('ease_factor')}")
                if pregunta.get('interval') != 0:
                    errores.append(f"      ⚠️  interval debería ser 0, es {pregunta.get('interval')}")
                if pregunta.get('repetitions') != 0:
                    errores.append(f"      ⚠️  repetitions debería ser 0, es {pregunta.get('repetitions')}")
                if pregunta.get('state') != 'new':
                    errores.append(f"      ⚠️  state debería ser 'new', es {pregunta.get('state')}")
            
            # PASO 4: Guardar práctica
            print_separador()
            print("📋 PASO 4: Guardar práctica en practicas.json")
            
            nueva_practica = {
                "id": f"practica_test_{int(time.time())}",
                "titulo": "🧪 Práctica de Prueba - Spaced Repetition",
                "carpeta": CARPETA_PRUEBA,
                "fecha_creacion": time.strftime("%Y-%m-%d %H:%M:%S"),
                "preguntas": preguntas
            }
            
            save_payload = {
                "carpeta": CARPETA_PRUEBA,
                "practica": nueva_practica
            }
            
            save_response = requests.post(
                f"{API_URL}/datos/practicas/carpeta",
                json=save_payload
            )
            
            if save_response.status_code == 200:
                print(f"   ✅ Práctica guardada exitosamente")
            else:
                error_msg = f"   ❌ Error guardando práctica: {save_response.status_code}"
                print(error_msg)
                errores.append(error_msg)
            
            # PASO 5: Verificar practicas.json actualizado
            print_separador()
            print("📋 PASO 5: Verificar actualización de practicas.json")
            
            time.sleep(1)  # Esperar un momento para que se escriba el archivo
            
            if practicas_path.exists():
                with open(practicas_path, 'r', encoding='utf-8') as f:
                    try:
                        practicas_actualizado = json.load(f)
                        print(f"   ✅ Archivo leído correctamente")
                        print(f"   📊 Total prácticas: {len(practicas_actualizado)}")
                        
                        # Verificar que no sea null
                        if practicas_actualizado is None:
                            errores.append("   ❌ practicas.json es null")
                        elif not isinstance(practicas_actualizado, list):
                            errores.append(f"   ❌ practicas.json no es un array, es {type(practicas_actualizado)}")
                        else:
                            print(f"   ✅ Estructura válida (array de {len(practicas_actualizado)} elementos)")
                            
                            # Verificar última práctica guardada
                            if practicas_actualizado:
                                ultima = practicas_actualizado[-1]
                                print(f"\n   🔍 Última práctica guardada:")
                                print(f"      ID: {ultima.get('id', 'SIN ID')}")
                                print(f"      Título: {ultima.get('titulo', 'SIN TÍTULO')}")
                                print(f"      Preguntas: {len(ultima.get('preguntas', []))}")
                                
                                # Verificar campos SR en preguntas guardadas
                                preguntas_guardadas = ultima.get('preguntas', [])
                                for i, p in enumerate(preguntas_guardadas):
                                    if not all(campo in p for campo in campos_requeridos):
                                        faltantes = [c for c in campos_requeridos if c not in p]
                                        errores.append(f"      ❌ Pregunta {i+1} guardada sin campos: {faltantes}")
                                
                    except json.JSONDecodeError as e:
                        error_msg = f"   ❌ Error parseando JSON: {e}"
                        print(error_msg)
                        errores.append(error_msg)
            else:
                error_msg = "   ❌ practicas.json no existe después de guardar"
                print(error_msg)
                errores.append(error_msg)
            
            # PASO 6: Cargar práctica para verificar normalización automática
            print_separador()
            print("📋 PASO 6: Cargar prácticas (verificar normalización automática)")
            
            load_response = requests.get(
                f"{API_URL}/datos/practicas",
                params={"carpeta": CARPETA_PRUEBA}
            )
            
            if load_response.status_code == 200:
                practicas_cargadas = load_response.json()
                print(f"   ✅ Prácticas cargadas: {len(practicas_cargadas)}")
                
                # Verificar normalización en preguntas cargadas
                if practicas_cargadas:
                    for p in practicas_cargadas[-1].get('preguntas', []):
                        if not all(campo in p for campo in campos_requeridos):
                            faltantes = [c for c in campos_requeridos if c not in p]
                            errores.append(f"   ❌ Pregunta cargada sin campos SR: {faltantes}")
            else:
                error_msg = f"   ❌ Error cargando prácticas: {load_response.status_code}"
                print(error_msg)
                errores.append(error_msg)
            
            # RESUMEN FINAL
            print_separador()
            print("📊 RESUMEN FINAL")
            print_separador()
            
            if errores:
                print(f"❌ TEST FALLIDO - {len(errores)} errores encontrados:\n")
                for error in errores:
                    print(error)
            else:
                print("✅ ¡TEST EXITOSO!")
                print("\n🎉 Verificaciones completadas:")
                print("   ✅ Todas las preguntas tienen campos de Spaced Repetition")
                print("   ✅ ease_factor = 2.5")
                print("   ✅ interval = 0")
                print("   ✅ repetitions = 0")
                print("   ✅ state = 'new'")
                print("   ✅ next_review y last_review presentes")
                print("   ✅ practicas.json actualizado correctamente")
                print("   ✅ Sin estructuras nulas")
                print("   ✅ Normalización automática funcionando")
            
            print_separador()
            
            return len(errores) == 0
            
        else:
            print(f"   ❌ Error en respuesta: {response.status_code}")
            print(f"   📄 Detalle: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout - La generación tardó más de 5 minutos")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Iniciando test controlado...")
    print("⚠️  Asegúrate de que el servidor esté corriendo en http://localhost:8000\n")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        print("✅ Servidor detectado\n")
    except:
        print("❌ ERROR: Servidor no está corriendo")
        print("   Ejecuta: python api_server.py")
        exit(1)
    
    # Ejecutar test
    exito = test_generar_practica()
    
    if exito:
        print("\n🎉 Test completado exitosamente")
        exit(0)
    else:
        print("\n❌ Test fallido - Revisa los errores arriba")
        exit(1)

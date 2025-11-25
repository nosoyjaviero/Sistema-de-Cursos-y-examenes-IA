#!/usr/bin/env python3
"""
Test de contexto largo y búsqueda web
Prueba si el chatbot retiene información en conversaciones extensas
"""
import requests
import json
import time

API_URL = "http://localhost:8000/api/chat"

def enviar_mensaje(mensaje, historial, buscar_web=False):
    """Envía un mensaje y devuelve la respuesta"""
    
    # Agregar el mensaje actual al historial
    mensaje_obj = {
        "tipo": "usuario",
        "texto": mensaje
    }
    
    if buscar_web:
        mensaje_obj["busqueda_web"] = True
    
    historial.append(mensaje_obj)
    
    payload = {
        "mensaje": mensaje,
        "historial": historial,
        "ajustes": {
            "temperature": 0.7,
            "max_tokens": 768
        }
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=180)
        response.raise_for_status()
        data = response.json()
        respuesta = data.get("respuesta", "Sin respuesta")
        
        # Agregar respuesta del asistente al historial
        historial.append({
            "tipo": "asistente",
            "texto": respuesta
        })
        
        return respuesta, historial
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"ERROR: {str(e)}", historial

def main():
    print("="*80)
    print("🧪 TEST DE CONTEXTO LARGO Y BÚSQUEDA WEB")
    print("="*80)
    print()
    
    historial = []
    
    # === TEST 1: BÚSQUEDA WEB ===
    print("\n" + "="*80)
    print("🌐 TEST 1: BÚSQUEDA WEB")
    print("="*80)
    
    pregunta = "¿Cuál es el clima en Madrid hoy?"
    print(f"\n👤 Usuario: {pregunta}")
    print("🔍 Activando búsqueda web...")
    
    respuesta, historial = enviar_mensaje(pregunta, historial, buscar_web=True)
    print(f"🤖 Asistente: {respuesta[:500]}...")
    
    # Verificar si buscó
    if "temperatura" in respuesta.lower() or "clima" in respuesta.lower() or "°C" in respuesta or "grados" in respuesta.lower():
        print("✅ BÚSQUEDA WEB: FUNCIONA - Contiene información meteorológica")
    else:
        print("❌ BÚSQUEDA WEB: FALLA - No parece tener información actualizada")
    
    time.sleep(2)
    
    # === TEST 2: CONTEXTO LARGO (12 INTERCAMBIOS) ===
    print("\n" + "="*80)
    print("🧠 TEST 2: CONTEXTO LARGO - 12 INTERCAMBIOS CON MUCHOS DETALLES")
    print("="*80)
    
    # Reiniciar historial para test de contexto
    historial = []
    
    conversacion = [
        # Intercambio 1-2
        ("Hola, mi nombre es Carlos y tengo 28 años. Soy ingeniero de software.", None),
        ("Estoy estudiando Machine Learning en la Universidad Politécnica de Madrid.", None),
        
        # Intercambio 3-4
        ("Mi materia favorita es Redes Neuronales Profundas. Es fascinante.", None),
        ("Tengo un gato llamado Whiskers que tiene 3 años y es de color naranja.", None),
        
        # Intercambio 5-6
        ("Mi hobby principal es tocar la guitarra, especialmente rock clásico.", None),
        ("Mi color favorito es el azul marino, me recuerda al océano.", None),
        
        # Intercambio 7-8
        ("Trabajo en una empresa llamada TechCorp desde hace 5 años.", None),
        ("Mi proyecto actual es desarrollar un sistema de reconocimiento de voz.", None),
        
        # Intercambio 9-10
        ("Mi comida favorita es la paella valenciana, especialmente la de mi abuela.", None),
        ("Viví en Barcelona durante 3 años antes de mudarme a Madrid.", None),
        
        # Intercambio 11-12
        ("Mi película favorita es Inception de Christopher Nolan.", None),
        ("Tengo dos hermanos: Juan (32) y María (25).", None),
    ]
    
    detalles_compartidos = []
    print("\n📝 Compartiendo información...\n")
    
    for i, (msg, buscar) in enumerate(conversacion, 1):
        print(f"👤 Usuario ({i}): {msg}")
        respuesta, historial = enviar_mensaje(msg, historial, buscar_web=bool(buscar))
        print(f"🤖 Asistente: {respuesta[:200]}...")
        print()
        time.sleep(1)
        
        # Guardar detalles clave
        if i == 1:
            detalles_compartidos.append("nombre: Carlos")
            detalles_compartidos.append("edad: 28 años")
            detalles_compartidos.append("profesión: ingeniero de software")
        elif i == 2:
            detalles_compartidos.append("estudiando: Machine Learning")
            detalles_compartidos.append("universidad: Politécnica de Madrid")
        elif i == 3:
            detalles_compartidos.append("materia favorita: Redes Neuronales Profundas")
        elif i == 4:
            detalles_compartidos.append("mascota: gato Whiskers, 3 años, naranja")
        elif i == 5:
            detalles_compartidos.append("hobby: tocar guitarra, rock clásico")
        elif i == 6:
            detalles_compartidos.append("color favorito: azul marino")
        elif i == 7:
            detalles_compartidos.append("empresa: TechCorp, 5 años")
        elif i == 8:
            detalles_compartidos.append("proyecto: sistema reconocimiento de voz")
        elif i == 9:
            detalles_compartidos.append("comida favorita: paella valenciana")
        elif i == 10:
            detalles_compartidos.append("vivió: Barcelona 3 años antes de Madrid")
        elif i == 11:
            detalles_compartidos.append("película favorita: Inception, Christopher Nolan")
        elif i == 12:
            detalles_compartidos.append("hermanos: Juan (32) y María (25)")
    
    # === PREGUNTA FINAL: RECORDAR TODO ===
    print("\n" + "="*80)
    print("🎯 PREGUNTA FINAL: ¿Recuerdas todos los detalles?")
    print("="*80)
    
    pregunta_final = """Hazme un resumen completo de todo lo que te he contado sobre mí. 
Incluye: mi nombre, edad, profesión, estudios, universidad, materia favorita, mascota, 
hobby, color favorito, empresa, proyecto actual, comida favorita, ciudad anterior, 
película favorita y hermanos."""
    
    print(f"\n👤 Usuario: {pregunta_final}")
    respuesta_final, historial = enviar_mensaje(pregunta_final, historial)
    print(f"\n🤖 Asistente:\n{respuesta_final}\n")
    
    # === VERIFICACIÓN ===
    print("\n" + "="*80)
    print("📊 VERIFICACIÓN DE MEMORIA")
    print("="*80)
    print(f"\nTotal de intercambios: {len(conversacion) + 1}")
    print(f"Total de mensajes en historial: {len(historial)}")
    print(f"\nDetalles compartidos: {len(detalles_compartidos)}")
    print("\n✅ Verificando qué detalles recuerda:\n")
    
    recordados = 0
    olvidados = []
    
    respuesta_lower = respuesta_final.lower()
    
    checks = [
        ("nombre: Carlos", "carlos"),
        ("edad: 28 años", "28"),
        ("profesión: ingeniero de software", "ingeniero"),
        ("estudiando: Machine Learning", "machine learning"),
        ("universidad: Politécnica de Madrid", "politécnica"),
        ("materia favorita: Redes Neuronales", "redes neuronales"),
        ("mascota: gato Whiskers", "whiskers" or "gato"),
        ("hobby: guitarra", "guitarra"),
        ("color favorito: azul marino", "azul"),
        ("empresa: TechCorp", "techcorp"),
        ("proyecto: reconocimiento de voz", "reconocimiento" or "voz"),
        ("comida: paella", "paella"),
        ("vivió: Barcelona", "barcelona"),
        ("película: Inception", "inception"),
        ("hermanos: Juan y María", "juan" or "maría"),
    ]
    
    for detalle, keyword in checks:
        if keyword in respuesta_lower:
            print(f"  ✅ {detalle}")
            recordados += 1
        else:
            print(f"  ❌ {detalle}")
            olvidados.append(detalle)
    
    porcentaje = (recordados / len(checks)) * 100
    
    print(f"\n{'='*80}")
    print(f"📈 RESULTADO FINAL")
    print(f"{'='*80}")
    print(f"✅ Detalles recordados: {recordados}/{len(checks)} ({porcentaje:.1f}%)")
    
    if olvidados:
        print(f"❌ Detalles olvidados: {len(olvidados)}")
        for detalle in olvidados:
            print(f"   - {detalle}")
    
    if porcentaje >= 90:
        print(f"\n🎉 EXCELENTE - Memoria de contexto largo funciona perfectamente")
    elif porcentaje >= 70:
        print(f"\n✅ BUENO - Memoria funcional pero mejorable")
    elif porcentaje >= 50:
        print(f"\n⚠️ REGULAR - Pierde algunos detalles importantes")
    else:
        print(f"\n❌ INSUFICIENTE - Problemas serios de memoria")
    
    print(f"\n{'='*80}")
    print("🏁 TEST COMPLETADO")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()

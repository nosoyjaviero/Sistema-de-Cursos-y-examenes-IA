"""
Script de validación del sistema de generación de exámenes
Verifica que los tipos de pregunta se mapean correctamente para la UI
"""
import requests
import json

API_URL = "http://localhost:8000/api/generar_examen_bloque"

# Test con archivo real
payload = {
    "archivos": ["Platzi/Diseño de Producto y UX/Resumen_251116_083114.txt"],
    "config": {
        "num_multiple": 2,
        "num_corta": 1,
        "num_vf": 1,
        "num_desarrollo": 1
    }
}

print("=" * 80)
print("🔍 VALIDACIÓN COMPLETA DEL SISTEMA")
print("=" * 80)
print(f"📡 Endpoint: {API_URL}")
print(f"📄 Payload:")
print(json.dumps(payload, indent=2, ensure_ascii=False))
print()

try:
    response = requests.post(API_URL, json=payload, timeout=600)
    
    if response.status_code == 200:
        data = response.json()
        preguntas = data.get('preguntas', [])
        
        print(f"✅ SUCCESS - {len(preguntas)} preguntas generadas")
        print()
        print("=" * 80)
        print("📋 RESUMEN DE PREGUNTAS GENERADAS")
        print("=" * 80)
        
        tipos_esperados = {
            'multiple': 0,
            'corta': 0,
            'verdadero-falso': 0,
            'desarrollo': 0
        }
        
        for i, p in enumerate(preguntas, 1):
            tipo = p.get('tipo', 'DESCONOCIDO')
            pregunta_texto = p.get('pregunta', '')[:70]
            puntos = p.get('puntos', 0)
            
            print(f"\n{i}. Tipo: [{tipo.upper()}] | Puntos: {puntos}")
            print(f"   Pregunta: {pregunta_texto}...")
            
            if tipo in tipos_esperados:
                tipos_esperados[tipo] += 1
            else:
                print(f"   ⚠️  ADVERTENCIA: Tipo '{tipo}' no reconocido por la UI")
        
        print()
        print("=" * 80)
        print("📊 DISTRIBUCIÓN DE TIPOS")
        print("=" * 80)
        
        config = payload['config']
        print(f"{'Tipo':<20} {'Solicitado':<15} {'Generado':<15} {'Estado'}")
        print("-" * 80)
        
        validacion_ok = True
        
        for tipo_ui, tipo_config in [
            ('multiple', 'num_multiple'),
            ('corta', 'num_corta'),
            ('verdadero-falso', 'num_vf'),
            ('desarrollo', 'num_desarrollo')
        ]:
            solicitado = config.get(tipo_config, 0)
            generado = tipos_esperados[tipo_ui]
            estado = "✅" if generado == solicitado else "❌"
            
            if generado != solicitado:
                validacion_ok = False
            
            print(f"{tipo_ui:<20} {solicitado:<15} {generado:<15} {estado}")
        
        print()
        print("=" * 80)
        
        if validacion_ok:
            print("✅ VALIDACIÓN EXITOSA - Todos los tipos coinciden")
            print("✅ El sistema está listo para usar en la UI")
        else:
            print("⚠️  ADVERTENCIA - Algunos tipos no coinciden")
            print("   Esto puede deberse a que la IA generó tipos diferentes")
        
        print("=" * 80)
        
        # Guardar respuesta completa para inspección
        with open('test_response_completo.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Respuesta completa guardada en: test_response_completo.json")
        
    else:
        print(f"❌ ERROR {response.status_code}")
        print(f"📄 Response: {response.text}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

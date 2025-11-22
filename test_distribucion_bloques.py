"""
Test: Verificar que no se generan más preguntas de las solicitadas
Simula el comportamiento de múltiples bloques
"""

def calcular_distribucion_bloques(config, num_bloques):
    """Simula la distribución de preguntas entre bloques (NUEVA LÓGICA)"""
    
    total_deseadas = (config['num_multiple'] + 
                     config['num_corta'] + 
                     config['num_vf'] + 
                     config['num_desarrollo'])
    
    # Config por bloque usando floor
    config_por_bloque = {
        'num_multiple': config['num_multiple'] // num_bloques,
        'num_corta': config['num_corta'] // num_bloques,
        'num_vf': config['num_vf'] // num_bloques,
        'num_desarrollo': config['num_desarrollo'] // num_bloques
    }
    
    # Calcular residuos
    residuos = {
        'num_multiple': config['num_multiple'] % num_bloques,
        'num_corta': config['num_corta'] % num_bloques,
        'num_vf': config['num_vf'] % num_bloques,
        'num_desarrollo': config['num_desarrollo'] % num_bloques
    }
    
    # Simular cada bloque
    total_generadas = 0
    bloques_detalle = []
    
    for i in range(num_bloques):
        config_bloque_actual = {
            'num_multiple': config_por_bloque['num_multiple'] + (1 if i < residuos['num_multiple'] else 0),
            'num_corta': config_por_bloque['num_corta'] + (1 if i < residuos['num_corta'] else 0),
            'num_vf': config_por_bloque['num_vf'] + (1 if i < residuos['num_vf'] else 0),
            'num_desarrollo': config_por_bloque['num_desarrollo'] + (1 if i < residuos['num_desarrollo'] else 0)
        }
        total_bloque = sum(config_bloque_actual.values())
        total_generadas += total_bloque
        bloques_detalle.append({'bloque': i+1, 'config': config_bloque_actual, 'total': total_bloque})
    
    return {
        'config_original': config,
        'total_deseadas': total_deseadas,
        'num_bloques': num_bloques,
        'config_base': config_por_bloque,
        'residuos': residuos,
        'bloques_detalle': bloques_detalle,
        'total_generadas': total_generadas,
        'diferencia': total_generadas - total_deseadas
    }


# Casos de prueba
casos = [
    {'config': {'num_multiple': 2, 'num_corta': 2, 'num_vf': 2, 'num_desarrollo': 1}, 'bloques': 1},
    {'config': {'num_multiple': 2, 'num_corta': 2, 'num_vf': 2, 'num_desarrollo': 1}, 'bloques': 2},
    {'config': {'num_multiple': 6, 'num_corta': 3, 'num_vf': 3, 'num_desarrollo': 2}, 'bloques': 3},
    {'config': {'num_multiple': 10, 'num_corta': 5, 'num_vf': 5, 'num_desarrollo': 3}, 'bloques': 4},
]

print("=" * 100)
print("📊 SIMULACIÓN DE DISTRIBUCIÓN DE PREGUNTAS POR BLOQUES (NUEVA LÓGICA)")
print("=" * 100)

for i, caso in enumerate(casos, 1):
    resultado = calcular_distribucion_bloques(caso['config'], caso['bloques'])
    
    print(f"\n{'='*100}")
    print(f"Caso #{i}")
    print(f"{'='*100}")
    print(f"Config solicitada: {resultado['config_original']}")
    print(f"Total deseadas: {resultado['total_deseadas']}")
    print(f"Número de bloques: {resultado['num_bloques']}")
    print(f"-" * 100)
    print(f"Config base (floor): {resultado['config_base']}")
    print(f"Residuos a distribuir: {resultado['residuos']}")
    print(f"-" * 100)
    
    for bloque in resultado['bloques_detalle']:
        print(f"Bloque {bloque['bloque']}: {bloque['config']} = {bloque['total']} preguntas")
    
    print(f"-" * 100)
    print(f"Total generadas (todos los bloques): {resultado['total_generadas']}")
    print(f"-" * 100)
    
    if resultado['diferencia'] == 0:
        print(f"✅ PERFECTO - Se generan exactamente {resultado['total_deseadas']} preguntas")
    else:
        print(f"❌ ERROR - Diferencia de {resultado['diferencia']} preguntas")

print(f"\n{'='*100}")
print("💡 CONCLUSIÓN")
print("=" * 100)
print("✅ Con la nueva lógica (floor + distribución de residuos),")
print("   se generan EXACTAMENTE las preguntas solicitadas.")
print("   NO hay exceso ni falta de preguntas.")
print("=" * 100)

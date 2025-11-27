"""
Script para normalizar examen_20251126_231507.json existente
Aplica correcciones de tipos, intervalos y rutas
"""

import json
from pathlib import Path

def normalizar_pregunta(pregunta):
    """Normaliza una pregunta individual"""
    # Mapeo de tipos
    tipo_map = {
        "verdadero-falso": "verdadero_falso",
        "verdadero_falso": "verdadero_falso",
        "multiple": "mcq",
        "mcq": "mcq",
        "corta": "short_answer",
        "short_answer": "short_answer",
        "desarrollo": "open_question",
        "open_question": "open_question"
    }
    
    # Normalizar tipo
    if "tipo" in pregunta:
        tipo_original = pregunta["tipo"]
        pregunta["tipo"] = tipo_map.get(tipo_original, tipo_original)
    
    # Normalizar intervalo (debe ser entero >= 1)
    if "intervalo" in pregunta:
        try:
            intervalo = float(pregunta["intervalo"])
            pregunta["intervalo"] = max(1, int(round(intervalo)))
        except (ValueError, TypeError):
            pregunta["intervalo"] = 1
    
    # Asegurar campos SM-2 en español
    campos_sm2 = {
        "facilidad": pregunta.get("facilidad", pregunta.get("ease_factor", 2.5)),
        "intervalo": pregunta.get("intervalo", pregunta.get("interval", 1)),
        "repeticiones": pregunta.get("repeticiones", pregunta.get("repetitions", 0)),
        "ultimaRevision": pregunta.get("ultimaRevision", pregunta.get("last_review")),
        "proximaRevision": pregunta.get("proximaRevision", pregunta.get("next_review")),
        "estadoRevision": pregunta.get("estadoRevision", pregunta.get("review_state", "nueva"))
    }
    
    # Remover campos en inglés si existen
    for campo_ingles in ["ease_factor", "interval", "repetitions", "last_review", "next_review", "review_state"]:
        pregunta.pop(campo_ingles, None)
    
    # Actualizar con campos en español
    pregunta.update(campos_sm2)
    
    return pregunta

def normalizar_examen(examen_path):
    """Normaliza un examen completo"""
    print(f"\n🔄 Normalizando: {examen_path}")
    
    with open(examen_path, 'r', encoding='utf-8') as f:
        examen = json.load(f)
    
    print(f"📊 Estado inicial:")
    print(f"   carpeta_ruta: {examen.get('carpeta_ruta')}")
    
    # 1️⃣ Normalizar carpeta_ruta (backslash → forward slash)
    if "carpeta_ruta" in examen:
        original = examen["carpeta_ruta"]
        examen["carpeta_ruta"] = original.replace("\\", "/")
        print(f"   ✅ carpeta_ruta: {original} → {examen['carpeta_ruta']}")
    
    # 2️⃣ Normalizar intervalo del examen
    if "intervalo" in examen:
        try:
            intervalo_original = examen["intervalo"]
            examen["intervalo"] = max(1, int(round(float(intervalo_original))))
            print(f"   ✅ intervalo: {intervalo_original} → {examen['intervalo']}")
        except (ValueError, TypeError):
            examen["intervalo"] = 1
    
    # 3️⃣ Normalizar preguntas
    if "preguntas" in examen and isinstance(examen["preguntas"], list):
        print(f"\n📝 Normalizando {len(examen['preguntas'])} preguntas...")
        for i, pregunta in enumerate(examen["preguntas"], 1):
            tipo_antes = pregunta.get("tipo", "N/A")
            intervalo_antes = pregunta.get("intervalo", "N/A")
            
            examen["preguntas"][i-1] = normalizar_pregunta(pregunta)
            
            tipo_despues = examen["preguntas"][i-1].get("tipo")
            intervalo_despues = examen["preguntas"][i-1].get("intervalo")
            
            if tipo_antes != tipo_despues or intervalo_antes != intervalo_despues:
                print(f"   Pregunta {i}:")
                if tipo_antes != tipo_despues:
                    print(f"      tipo: {tipo_antes} → {tipo_despues}")
                if intervalo_antes != intervalo_despues:
                    print(f"      intervalo: {intervalo_antes} → {intervalo_despues}")
    
    # 4️⃣ Normalizar resultados
    if "resultados" in examen and isinstance(examen["resultados"], list):
        print(f"\n📊 Normalizando {len(examen['resultados'])} resultados...")
        for i, resultado in enumerate(examen["resultados"]):
            examen["resultados"][i] = normalizar_pregunta(resultado)
    
    # 5️⃣ Guardar normalizado
    with open(examen_path, 'w', encoding='utf-8') as f:
        json.dump(examen, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Examen normalizado guardado: {examen_path}")
    return examen

if __name__ == "__main__":
    # Normalizar el examen existente
    examen_path = Path("examenes/Platzi/Prueba/sadas/examen_20251126_231507.json")
    
    if not examen_path.exists():
        print(f"❌ No se encontró: {examen_path}")
    else:
        examen_normalizado = normalizar_examen(examen_path)
        
        print(f"\n{'='*70}")
        print(f"📋 RESUMEN DE NORMALIZACIÓN")
        print(f"{'='*70}")
        print(f"✅ carpeta_ruta: {examen_normalizado.get('carpeta_ruta')}")
        print(f"✅ intervalo: {examen_normalizado.get('intervalo')}")
        print(f"✅ Preguntas normalizadas: {len(examen_normalizado.get('preguntas', []))}")
        print(f"✅ Resultados normalizados: {len(examen_normalizado.get('resultados', []))}")
        
        # Mostrar primer pregunta como ejemplo
        if examen_normalizado.get("preguntas"):
            p1 = examen_normalizado["preguntas"][0]
            print(f"\n📝 Ejemplo - Primera pregunta:")
            print(f"   tipo: {p1.get('tipo')}")
            print(f"   intervalo: {p1.get('intervalo')}")
            print(f"   facilidad: {p1.get('facilidad')}")
            print(f"   repeticiones: {p1.get('repeticiones')}")

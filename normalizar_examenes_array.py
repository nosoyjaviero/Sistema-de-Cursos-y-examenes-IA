"""
Normalización de array de exámenes desde examenes.json
Aplica correcciones de tipos, intervalos y rutas a TODO el array
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def normalizar_pregunta_individual(pregunta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza una pregunta individual
    """
    # 1️⃣ Normalizar tipo: "verdadero-falso" → "verdadero_falso"
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
    
    if "tipo" in pregunta:
        tipo_original = pregunta["tipo"]
        pregunta["tipo"] = tipo_map.get(tipo_original, tipo_original)
    
    # 2️⃣ Normalizar intervalo (debe ser entero >= 1)
    if "intervalo" in pregunta:
        try:
            intervalo = float(pregunta["intervalo"])
            # Si es 0.5 o menor a 1, forzar a 1
            pregunta["intervalo"] = max(1, int(round(intervalo)))
        except (ValueError, TypeError):
            pregunta["intervalo"] = 1
    
    # 3️⃣ Asegurar campos SM-2 consistentes
    if "facilidad" not in pregunta:
        pregunta["facilidad"] = 2.5
    if "repeticiones" not in pregunta:
        pregunta["repeticiones"] = 0
    if "estadoRevision" not in pregunta:
        pregunta["estadoRevision"] = "nueva"
    
    return pregunta


def normalizar_examen_individual(examen: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza un examen individual del array
    """
    # 1️⃣ Normalizar rutas de carpeta (backslash → forward slash)
    for campo_ruta in ["carpeta", "carpeta_ruta"]:
        if campo_ruta in examen and isinstance(examen[campo_ruta], str):
            examen[campo_ruta] = examen[campo_ruta].replace("\\", "/")
    
    # 2️⃣ Normalizar intervalo del examen (nivel raíz)
    if "intervalo" in examen:
        try:
            intervalo = float(examen["intervalo"])
            examen["intervalo"] = max(1, int(round(intervalo)))
        except (ValueError, TypeError):
            examen["intervalo"] = 1
    
    # 3️⃣ Normalizar preguntas[]
    if "preguntas" in examen and isinstance(examen["preguntas"], list):
        for i in range(len(examen["preguntas"])):
            examen["preguntas"][i] = normalizar_pregunta_individual(examen["preguntas"][i])
    
    # 4️⃣ Normalizar resultado.resultados[]
    if "resultado" in examen and isinstance(examen["resultado"], dict):
        if "resultados" in examen["resultado"] and isinstance(examen["resultado"]["resultados"], list):
            for i in range(len(examen["resultado"]["resultados"])):
                examen["resultado"]["resultados"][i] = normalizar_pregunta_individual(
                    examen["resultado"]["resultados"][i]
                )
    
    # 5️⃣ Asegurar campos SM-2 en nivel raíz
    if "facilidad" not in examen:
        examen["facilidad"] = 2.5
    if "repeticiones" not in examen:
        examen["repeticiones"] = 0
    if "estadoRevision" not in examen:
        examen["estadoRevision"] = "nueva"
    
    return examen


def normalizar_examenes(examenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normaliza un array completo de exámenes (como el de examenes.json)
    
    Aplica:
    1. Normalización de tipos: "verdadero-falso" → "verdadero_falso"
    2. Normalización de intervalos: 0.5 → 1, asegura enteros >= 1
    3. Normalización de rutas: "Platzi\\Prueba" → "Platzi/Prueba"
    
    Args:
        examenes: Array de exámenes desde examenes.json
    
    Returns:
        Array de exámenes normalizado (modifica in-place y devuelve)
    """
    if not isinstance(examenes, list):
        print("⚠️ examenes no es un array, retornando sin cambios")
        return examenes
    
    print(f"\n🔄 Normalizando {len(examenes)} exámenes...")
    
    cambios_totales = {
        "tipos_normalizados": 0,
        "intervalos_corregidos": 0,
        "rutas_normalizadas": 0
    }
    
    for idx, examen in enumerate(examenes):
        # Guardar estado previo para contar cambios
        carpeta_antes = examen.get("carpeta", "")
        
        # Normalizar examen
        examenes[idx] = normalizar_examen_individual(examen)
        
        # Contar cambios de rutas
        carpeta_despues = examenes[idx].get("carpeta", "")
        if carpeta_antes != carpeta_despues:
            cambios_totales["rutas_normalizadas"] += 1
        
        # Contar tipos normalizados en preguntas
        if "preguntas" in examenes[idx]:
            for p in examenes[idx]["preguntas"]:
                if p.get("tipo") in ["verdadero_falso", "mcq", "short_answer", "open_question"]:
                    cambios_totales["tipos_normalizados"] += 1
        
        # Contar intervalos corregidos
        if "resultado" in examenes[idx] and "resultados" in examenes[idx]["resultado"]:
            for r in examenes[idx]["resultado"]["resultados"]:
                if r.get("intervalo", 0) >= 1:
                    cambios_totales["intervalos_corregidos"] += 1
    
    print(f"\n📊 Resumen de normalización:")
    print(f"   ✅ Exámenes procesados: {len(examenes)}")
    print(f"   ✅ Rutas normalizadas: {cambios_totales['rutas_normalizadas']}")
    print(f"   ✅ Tipos normalizados: {cambios_totales['tipos_normalizados']}")
    print(f"   ✅ Intervalos corregidos: {cambios_totales['intervalos_corregidos']}")
    
    return examenes


# ========================================
# EJEMPLO DE USO - BACKEND (FastAPI)
# ========================================

def ejemplo_uso_backend():
    """
    Ejemplo de cómo integrar en FastAPI
    """
    # Leer examenes.json
    examenes_path = Path("examenes.json")
    
    if not examenes_path.exists():
        print(f"❌ No se encontró: {examenes_path}")
        return
    
    with open(examenes_path, 'r', encoding='utf-8') as f:
        examenes = json.load(f)
    
    print(f"📖 Leídos {len(examenes)} exámenes desde examenes.json")
    
    # 🔥 NORMALIZAR ANTES DE USAR
    examenes_normalizados = normalizar_examenes(examenes)
    
    # Guardar versión normalizada
    backup_path = examenes_path.parent / "examenes_backup.json"
    examenes_path.rename(backup_path)
    print(f"💾 Backup guardado en: {backup_path}")
    
    with open(examenes_path, 'w', encoding='utf-8') as f:
        json.dump(examenes_normalizados, f, ensure_ascii=False, indent=2)
    
    print(f"✅ examenes.json normalizado guardado")
    
    # Mostrar ejemplo de primer examen
    if examenes_normalizados:
        primer_examen = examenes_normalizados[0]
        print(f"\n📋 Ejemplo - Primer examen:")
        print(f"   carpeta: {primer_examen.get('carpeta')}")
        print(f"   carpeta_ruta: {primer_examen.get('carpeta_ruta')}")
        print(f"   intervalo: {primer_examen.get('intervalo')}")
        
        if primer_examen.get("preguntas"):
            p1 = primer_examen["preguntas"][0]
            print(f"\n   Primera pregunta:")
            print(f"      tipo: {p1.get('tipo')}")
            print(f"      intervalo: {p1.get('intervalo', 'N/A')}")


if __name__ == "__main__":
    ejemplo_uso_backend()

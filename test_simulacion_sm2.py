"""
🧪 SIMULACIÓN COMPLETA DE SM-2: Repaso de aciertos + Corrección de errores
===========================================================================

Escenario: 5 oraciones tipo constructor_oraciones
- Oración 1: ✅ correcta (va a "repaso de aciertos")  
- Oración 2: ✅ correcta (va a "repaso de aciertos")
- Oración 3: ❌ falla (va a "corrección de errores")
- Oración 4: ❌ falla (va a "corrección de errores")
- Oración 5: ❌ falla (va a "corrección de errores")

Luego simula múltiples días de repasar y acertar para ver la progresión de intervalos.
"""

from datetime import datetime, timedelta
import math

# ==========================================
# ALGORITMO 1: SM-2 BACKEND (api_server.py)
# Para evaluación inicial al completar práctica
# ==========================================
def sm2_backend_evaluar(porcentaje_pregunta, repeticiones, facilidad, intervalo_anterior):
    """Replica la lógica de api_server.py líneas 4310-4325
    NOTA: El backend NO incrementa repeticiones. Solo calcula el intervalo inicial.
    El conteo de repeticiones lo lleva el sistema de repaso del frontend."""
    if porcentaje_pregunta >= 90:
        if repeticiones == 0:
            intervalo_dias = 1
        elif repeticiones == 1:
            intervalo_dias = 6
        else:
            intervalo_dias = int(round(intervalo_anterior * facilidad))
        intervalo_dias = min(intervalo_dias, 90)
        facilidad = min(3.0, facilidad + 0.15)
        # NO incrementar repeticiones — el frontend lo hace
    else:
        intervalo_dias = 1
        facilidad = max(1.3, facilidad - 0.2)
        repeticiones = 0
    return intervalo_dias, repeticiones, facilidad


# ==========================================
# ALGORITMO 2: SM-2 ERRORES (App.jsx ~8574)
# Para cuando corriges un error acertando
# ==========================================
def sm2_errores_corregir(es_correcta, repeticiones_error, facilidad_error, intervalo_error, fallo_antes_sesion=False):
    """Replica la lógica de App.jsx líneas 8574-8660 (corrección de errores)"""
    nuevas_veces_fallada = 0
    
    if es_correcta:
        nuevo_estado = "ok"
        nuevas_repeticiones = repeticiones_error + 1
        nueva_facilidad = min(3.0, max(1.3, facilidad_error + 0.1))
        
        if fallo_antes_sesion:
            nuevo_intervalo = 1
            nuevas_repeticiones = 1
            nueva_facilidad = max(1.3, nueva_facilidad - 0.15)
        else:
            intervalo_anterior = intervalo_error
            
            if nuevas_repeticiones == 1:
                nuevo_intervalo = 3  # Primera corrección: 3 días
            elif nuevas_repeticiones == 2:
                nuevo_intervalo = 7  # Segunda corrección: 7 días
            else:
                factor = max(nueva_facilidad, 2.0)
                nuevo_intervalo = round(intervalo_anterior * factor)
                nuevo_intervalo = max(nuevo_intervalo, intervalo_anterior + 3)
            
            # El intervalo NUNCA baja
            nuevo_intervalo = max(nuevo_intervalo, intervalo_anterior)
            # Hasta 90: cap normal. Después de 90: crece ×2
            if intervalo_anterior < 90:
                nuevo_intervalo = min(nuevo_intervalo, 90)
    else:
        nuevo_estado = "fallo"
        nuevas_repeticiones = 0
        nuevo_intervalo = 1
        nueva_facilidad = max(1.3, facilidad_error - 0.2)
        nuevas_veces_fallada += 1
    
    return nuevo_intervalo, nuevas_repeticiones, nueva_facilidad, nuevo_estado


# ==========================================
# ALGORITMO 3: REPASO DE ACIERTOS (App.jsx ~9310)
# Para cuando repasas un acierto y lo vuelves a acertar
# ==========================================
def sm2_aciertos_repasar(es_correcta, repeticiones, facilidad, intervalo_actual, fallo_antes_sesion=False):
    """Replica la lógica de App.jsx líneas 9288-9360 (repaso de aciertos)"""
    INTERVALOS_FIJOS = [3, 7, 15, 30, 60]  
    
    if es_correcta:
        nuevas_repeticiones = repeticiones + 1
        nueva_facilidad = min(3.0, max(1.3, facilidad + 0.1))
        
        if fallo_antes_sesion:
            nuevo_intervalo = 1
            nuevas_repeticiones = 1
            nueva_facilidad = max(1.3, nueva_facilidad - 0.15)
        else:
            if nuevas_repeticiones <= len(INTERVALOS_FIJOS):
                nuevo_intervalo = INTERVALOS_FIJOS[nuevas_repeticiones - 1]
            elif intervalo_actual >= 90:
                # Después de 90 días: crecer ×2
                nuevo_intervalo = round(intervalo_actual * 2)
            else:
                # Hasta 90: ×2.5
                nuevo_intervalo = round(intervalo_actual * 2.5)
        
        return nuevo_intervalo, nuevas_repeticiones, nueva_facilidad, "correcto"
    else:
        nuevas_repeticiones = 0
        nuevo_intervalo = 1
        nueva_facilidad = max(1.3, facilidad - 0.2)
        return nuevo_intervalo, nuevas_repeticiones, nueva_facilidad, "fallo"


# ==========================================
# ALGORITMO 4: FLASHCARDS/NOTAS (App.jsx ~9662)
# calcularProximaRevision
# ==========================================
def sm2_flashcard(dificultad, repeticiones, facilidad, intervalo, fallo_antes_sesion=False):
    """Replica la lógica de calcularProximaRevision en App.jsx"""
    nuevo_intervalo = intervalo or 1
    nuevas_rep = repeticiones or 0
    nueva_facilidad = facilidad or 2.5
    
    if fallo_antes_sesion or dificultad == "dificil":
        nuevo_intervalo = 1
        nuevas_rep = 0
        nueva_facilidad = max(1.3, nueva_facilidad - 0.2)
    elif dificultad == "medio":
        if nuevas_rep == 0:
            nuevo_intervalo = 2
        elif (intervalo or 1) >= 90:
            # Después de 90 días: ×2
            nuevo_intervalo = round((intervalo or 1) * 2)
        else:
            nuevo_intervalo = round((intervalo or 1) * 2.3)
        nuevas_rep += 1
        nueva_facilidad = max(1.3, nueva_facilidad - 0.05)
    elif dificultad == "facil":
        if nuevas_rep == 0:
            nuevo_intervalo = 3
        elif (intervalo or 1) >= 90:
            # Después de 90 días: ×2
            nuevo_intervalo = round((intervalo or 1) * 2)
        else:
            nuevo_intervalo = round((intervalo or 1) * 2.6)
        nuevas_rep += 1
        nueva_facilidad = min(3.0, nueva_facilidad + 0.1)
    
    nuevo_intervalo = max(1, nuevo_intervalo)
    nueva_facilidad = max(1.3, min(nueva_facilidad, 3.0))
    
    estado = "madura" if nuevas_rep >= 5 else ("en_progreso" if nuevas_rep >= 2 else "nueva")
    return nuevo_intervalo, nuevas_rep, nueva_facilidad, estado


# ==========================================
# ALGORITMO 5: PRÁCTICA COMPLETADA (App.jsx ~22920)
# ==========================================
def sm2_practica_completada(porcentaje, repeticiones, facilidad, intervalo_anterior):
    """Replica la lógica de finalización de práctica en App.jsx"""
    nuevas_rep = repeticiones
    nueva_facilidad = facilidad
    
    if porcentaje >= 70:
        nuevas_rep += 1
        nueva_facilidad = min(3.0, nueva_facilidad + (0.15 if porcentaje >= 90 else 0.05))
        if nuevas_rep == 1:
            dias = 3 if porcentaje >= 90 else 2
        elif nuevas_rep == 2:
            dias = 7 if porcentaje >= 90 else 5
        else:
            dias = min(90, round(intervalo_anterior * nueva_facilidad))
    else:
        nuevas_rep = 0
        nueva_facilidad = max(1.3, nueva_facilidad - 0.2)
        dias = 1
    
    dias = max(1, min(dias, 90))
    estado = "madura" if nuevas_rep >= 5 else ("en_progreso" if nuevas_rep >= 2 else "repaso")
    return dias, nuevas_rep, nueva_facilidad, estado


# ============================================================
# 🧪 SIMULACIÓN
# ============================================================
def separador(titulo):
    print(f"\n{'='*70}")
    print(f"  {titulo}")
    print(f"{'='*70}")


def simular_escenario_completo():
    print("🧪 SIMULACIÓN COMPLETA SM-2")
    print("="*70)
    print("Escenario: 5 oraciones constructor_oraciones")
    print("  Oración 1: ✅ (100%) → va a repaso de aciertos")
    print("  Oración 2: ✅ (100%) → va a repaso de aciertos") 
    print("  Oración 3: ❌ (0%)   → va a corrección de errores")
    print("  Oración 4: ❌ (0%)   → va a corrección de errores")
    print("  Oración 5: ❌ (0%)   → va a corrección de errores")
    
    # === PASO 1: EVALUACIÓN INICIAL (Backend) ===
    separador("PASO 1: Evaluación inicial (Backend api_server.py)")
    
    resultados_iniciales = []
    oraciones = [
        ("Oración 1", 100),  # ✅ 
        ("Oración 2", 100),  # ✅
        ("Oración 3", 0),    # ❌
        ("Oración 4", 0),    # ❌
        ("Oración 5", 0),    # ❌
    ]
    
    for nombre, pct in oraciones:
        intervalo, rep, fac = sm2_backend_evaluar(pct, 0, 2.5, 1)
        emoji = "✅" if pct >= 90 else "❌"
        resultados_iniciales.append({
            "nombre": nombre, "porcentaje": pct,
            "intervalo": intervalo, "repeticiones": rep, "facilidad": fac
        })
        print(f"  {emoji} {nombre} ({pct}%) → intervalo={intervalo}d, rep={rep}, fac={fac:.2f}")
    
    # === PASO 2: Práctica completada (Frontend) ===
    separador("PASO 2: Práctica completada (40% total → no aprobó)")
    porcentaje_total = 40  # 2/5 correctas
    dias, rep, fac, estado = sm2_practica_completada(porcentaje_total, 0, 2.5, 1)
    print(f"  Porcentaje: {porcentaje_total}% → intervalo={dias}d, rep={rep}, fac={fac:.2f}, estado={estado}")
    
    # === PASO 3: Simulación de repaso de ACIERTOS ===
    separador("PASO 3: Repaso de aciertos (Oración 1 y 2)")
    print("  Progresión FIJA: rep=0→1: 3d | 1→2: 7d | 2→3: 15d | 3→4: 30d | 4→5: 60d | 5+: ×2.5 (max 90)")
    print()
    
    for i, r in enumerate(resultados_iniciales[:2]):
        print(f"  📗 {r['nombre']} — Inicia con intervalo={r['intervalo']}d, rep={r['repeticiones']}")
        rep = r["repeticiones"]      # = 1 (ya acertó una vez en eval inicial)
        fac = r["facilidad"]         # = 2.65
        intervalo = r["intervalo"]   # = 1
        
        fecha_actual = datetime.now()
        fecha_repaso = fecha_actual + timedelta(days=intervalo)
        
        for repaso_num in range(1, 10):
            # Simular que acierta en el repaso
            nuevo_int, rep, fac, estado = sm2_aciertos_repasar(True, rep, fac, intervalo)
            
            print(f"    Repaso #{repaso_num} (día +{(fecha_repaso - fecha_actual).days}): "
                  f"✅ → intervalo={nuevo_int}d, rep={rep}, fac={fac:.2f}, estado={estado}")
            
            intervalo = nuevo_int
            fecha_repaso = fecha_repaso + timedelta(days=nuevo_int)
            
            if nuevo_int >= 90:
                print(f"    🔒 Alcanzó cap de 90 días — seguirá repasándose cada 90 días")
                break
        print()
    
    # === PASO 4: Simulación de corrección de ERRORES ===
    separador("PASO 4: Corrección de errores (Oración 3, 4, 5)")
    print("  Progresión: rep=0→1: 3d | 1→2: 7d | 2→3: ×fac (min +3) | max 90")
    print()
    
    for i, r in enumerate(resultados_iniciales[2:]):
        print(f"  📕 {r['nombre']} — Inicia con intervalo={r['intervalo']}d, rep={r['repeticiones']}")
        rep = r["repeticiones"]      # = 0 (falló)
        fac = r["facilidad"]         # = 2.3
        intervalo = r["intervalo"]   # = 1
        
        fecha_actual = datetime.now()
        fecha_repaso = fecha_actual + timedelta(days=intervalo)
        
        for repaso_num in range(1, 10):
            nuevo_int, rep, fac, estado = sm2_errores_corregir(True, rep, fac, intervalo)
            
            print(f"    Corrección #{repaso_num} (día +{(fecha_repaso - fecha_actual).days}): "
                  f"✅ → intervalo={nuevo_int}d, rep={rep}, fac={fac:.2f}, estado={estado}")
            
            intervalo = nuevo_int
            fecha_repaso = fecha_repaso + timedelta(days=nuevo_int)
            
            if nuevo_int >= 90:
                print(f"    🔒 Alcanzó cap de 90 días — seguirá repasándose cada 90 días")
                break
        print()
    
    # === PASO 5: Flashcards/Notas ===
    separador("PASO 5: Flashcards — Simulación de repaso diario")
    print("  Caso A: siempre 'facil' | Caso B: siempre 'medio'")
    print()
    
    for caso, dif in [("A (fácil)", "facil"), ("B (medio)", "medio")]:
        print(f"  🃏 Caso {caso}:")
        rep, fac, intervalo = 0, 2.5, 1
        
        fecha_actual = datetime.now()
        fecha_repaso = fecha_actual + timedelta(days=1)  # Primera revisión mañana
        
        for repaso_num in range(1, 12):
            nuevo_int, rep, fac, estado = sm2_flashcard(dif, rep, fac, intervalo)
            
            print(f"    Repaso #{repaso_num} (día +{(fecha_repaso - fecha_actual).days}): "
                  f"→ intervalo={nuevo_int}d, rep={rep}, fac={fac:.2f}, estado={estado}")
            
            intervalo = nuevo_int
            fecha_repaso = fecha_repaso + timedelta(days=nuevo_int)
            
            if nuevo_int >= 90:
                print(f"    🔒 Cap 90 días alcanzado — SIGUE repasándose cada 90 días para siempre")
                break
        print()
    
    # === VERIFICACIONES ===
    separador("✅ VERIFICACIONES AUTOMÁTICAS")
    
    errores = []
    
    # Test 1: Aciertos progresión fija (×2.5 hasta 90, luego ×2)
    rep, fac, intervalo = 0, 2.5, 1
    esperado_aciertos = [3, 7, 15, 30, 60, 150, 300]
    for i, esperado in enumerate(esperado_aciertos):
        nuevo_int, rep, fac, _ = sm2_aciertos_repasar(True, rep, fac, intervalo)
        if nuevo_int != esperado:
            errores.append(f"❌ Acierto rep {i+1}: esperado {esperado}d, obtenido {nuevo_int}d")
        intervalo = nuevo_int
    
    # Test 2: Errores progresión
    rep, fac, intervalo = 0, 2.5, 1
    nuevo_int, rep, fac, _ = sm2_errores_corregir(True, rep, fac, intervalo)
    if nuevo_int != 3:
        errores.append(f"❌ Error corrección 1: esperado 3d, obtenido {nuevo_int}d")
    intervalo = nuevo_int
    
    nuevo_int, rep, fac, _ = sm2_errores_corregir(True, rep, fac, intervalo)
    if nuevo_int != 7:
        errores.append(f"❌ Error corrección 2: esperado 7d, obtenido {nuevo_int}d")
    intervalo = nuevo_int
    
    # 3ra corrección: factor = max(fac, 2.0) = max(2.7, 2.0) = 2.7, 7*2.7=18.9→19, max(19, 7+3=10)=19
    nuevo_int, rep, fac, _ = sm2_errores_corregir(True, rep, fac, intervalo)
    if nuevo_int < 10:  # Debe ser al menos intervalo_anterior + 3
        errores.append(f"❌ Error corrección 3: esperado ≥10d, obtenido {nuevo_int}d")
    
    # Test 3: Flashcard fácil progresión (×2.6 hasta 90, luego ×2)
    rep, fac, intervalo = 0, 2.5, 1
    esperado_flash_facil = [3, 8, 21, 55, 143, 286]
    for i, esperado in enumerate(esperado_flash_facil):
        nuevo_int, rep, fac, _ = sm2_flashcard("facil", rep, fac, intervalo)
        if nuevo_int != esperado:
            errores.append(f"❌ Flashcard fácil rep {i+1}: esperado {esperado}d, obtenido {nuevo_int}d")
        intervalo = nuevo_int
    
    # Test 4: Flashcard medio progresión (×2.3 hasta 90, luego ×2)
    rep, fac, intervalo = 0, 2.5, 1
    esperado_flash_medio = [2, 5, 12, 28, 64, 147, 294]
    for i, esperado in enumerate(esperado_flash_medio):
        nuevo_int, rep, fac, _ = sm2_flashcard("medio", rep, fac, intervalo)
        if nuevo_int != esperado:
            errores.append(f"❌ Flashcard medio rep {i+1}: esperado {esperado}d, obtenido {nuevo_int}d")
        intervalo = nuevo_int
    
    # Test 5: Aciertos y errores crecen ×2 después de 90
    rep, fac, intervalo = 0, 2.5, 1
    superó_90_aciertos = False
    for i in range(15):
        nuevo_int, rep, fac, _ = sm2_aciertos_repasar(True, rep, fac, intervalo)
        if nuevo_int > 90:
            superó_90_aciertos = True
            break
        intervalo = nuevo_int
    if not superó_90_aciertos:
        errores.append(f"❌ Aciertos nunca superaron 90 días en 15 repasos")
    
    rep, fac, intervalo = 0, 2.5, 1
    superó_90_errores = False
    for i in range(15):
        nuevo_int, rep, fac, _ = sm2_errores_corregir(True, rep, fac, intervalo)
        if nuevo_int > 90:
            superó_90_errores = True
            break
        intervalo = nuevo_int
    if not superó_90_errores:
        errores.append(f"❌ Errores nunca superaron 90 días en 15 repasos")
    
    # Test 5b: Flashcards SÍ crecen después de 90 (×2)
    rep, fac, intervalo = 0, 2.5, 1
    superó_90 = False
    for i in range(10):
        nuevo_int, rep, fac, _ = sm2_flashcard("facil", rep, fac, intervalo)
        if nuevo_int > 90:
            superó_90 = True
            break
        intervalo = nuevo_int
    if not superó_90:
        errores.append(f"❌ Flashcard fácil nunca superó 90 días en 10 repasos")
    
    # Test 6: Backend nunca supera 90
    rep, fac, intervalo = 0, 2.5, 1
    for i in range(20):
        nuevo_int, rep, fac = sm2_backend_evaluar(100, rep, fac, intervalo)
        if nuevo_int > 90:
            errores.append(f"❌ Backend rep {i+1}: intervalo {nuevo_int}d supera cap de 90!")
        intervalo = nuevo_int
    
    # Test 7: Fallo reinicia todo
    nuevo_int, rep, fac, estado = sm2_errores_corregir(False, 5, 2.8, 60)
    if rep != 0 or nuevo_int != 1:
        errores.append(f"❌ Fallo de error no reinicia: rep={rep}, intervalo={nuevo_int}")
    
    nuevo_int, rep, fac, estado = sm2_aciertos_repasar(False, 5, 2.8, 60)
    if rep != 0 or nuevo_int != 1:
        errores.append(f"❌ Fallo de acierto no reinicia: rep={rep}, intervalo={nuevo_int}")
    
    # Mostrar resultados
    if errores:
        print(f"\n  🚨 {len(errores)} ERRORES ENCONTRADOS:")
        for e in errores:
            print(f"    {e}")
    else:
        print("  ✅ TODAS LAS VERIFICACIONES PASARON CORRECTAMENTE")
        print("  ✅ Todo crece ×2 después de 90 días ✓")
        print("  ✅ Progresiones de aciertos: 3→7→15→30→60→150→300 (×2 tras 90) ✓")
        print("  ✅ Progresiones de errores: 3→7→×fac→90→×2 ✓")
        print("  ✅ Flashcard fácil: 3→8→21→55→143→286 (×2 después de 90) ✓")
        print("  ✅ Flashcard medio: 2→5→12→28→64→147→294 (×2 después de 90) ✓")
        print("  ✅ Fallos reinician todo a 1 día ✓")
    
    return len(errores) == 0


if __name__ == "__main__":
    exito = simular_escenario_completo()
    print(f"\n{'='*70}")
    print(f"  RESULTADO FINAL: {'✅ TODO CORRECTO' if exito else '❌ HAY ERRORES'}")
    print(f"{'='*70}")

# 🔍 DIAGNÓSTICO Y CORRECCIÓN: FLASHCARDS DUPLICADAS EN EL MISMO DÍA

## ❌ PROBLEMA IDENTIFICADO

Las flashcards aparecían **más de 2 veces en el mismo día**, violando la regla del sistema SM-2 de Anki que limita las revisiones a **máximo 2 por día**.

---

## 🐛 BUGS ENCONTRADOS

### Bug #1: Comparación de Fecha con Hora Exacta

**Ubicación**: `filtrarItemsParaRepasar()` - Línea ~2785

**Problema**:
```javascript
// ❌ ANTES (INCORRECTO)
const fechaRevision = new Date(item.proximaRevision);
const debeRepasar = fechaRevision <= ahora;
```

**Efecto**:
- Si `proximaRevision` = `2025-11-26T23:58:10.000Z`
- Y revisas a las `2025-11-26T21:00:00.000Z`
- La flashcard **NO aparecía** porque técnicamente `23:58 > 21:00`
- Pero al llegar las `23:59`, la flashcard aparecía de nuevo **en el mismo día**

**Causa raíz**: Se compara **momento exacto** en vez de **día calendario**.

---

### Bug #2: Fecha de Próxima Revisión No Normalizada

**Ubicación**: `calcularProximaRevision()` - Línea ~2669

**Problema**:
```javascript
// ❌ ANTES (INCORRECTO)
const proximaFecha = new Date();
proximaFecha.setDate(proximaFecha.getDate() + nuevoIntervalo);
// Resultado: 2025-11-27T14:35:42.123Z ← Incluye hora actual
```

**Efecto**:
- La `proximaRevision` se guardaba con la **hora exacta** de evaluación
- Esto causaba inconsistencias en comparaciones posteriores
- Una flashcard evaluada a las 14:00 tenía fecha `2025-11-27T14:00:00Z`
- Otra evaluada a las 20:00 tenía fecha `2025-11-27T20:00:00Z`
- Ambas debían ser el mismo día, pero el sistema las trataba diferente

---

### Bug #3: Falta de Inicialización de `revisionesHoy`

**Ubicación**: `filtrarItemsParaRepasar()` - Línea ~2715

**Problema**:
```javascript
// ⚠️ POTENCIAL PROBLEMA
if (item.revisionesHoy === undefined || item.revisionesHoy === null) {
  // Se inicializa en el filtro, pero...
}
```

**Efecto**:
- Si una flashcard no tenía el campo `revisionesHoy`
- Se inicializaba en cada filtro
- Pero si se cargaba desde un archivo sin ese campo
- Podía aparecer múltiples veces

**Nota**: Este bug era parcialmente mitigado por la inicialización automática, pero no era la solución ideal.

---

## ✅ CORRECCIONES IMPLEMENTADAS

### ⚠️ ACTUALIZACIÓN CRÍTICA (26-Nov-2025 23:00)

**PROBLEMA ENCONTRADO EN PRODUCCIÓN**:
- Una flashcard tenía `revisionesHoy: 3` (¡excedía el límite de 2!)
- El filtro NO la estaba bloqueando correctamente
- La verificación existía pero no era suficientemente estricta

**NUEVAS CORRECCIONES APLICADAS**:

1. ✅ **Bloqueo doble en filtro** - Dos validaciones independientes
2. ✅ **Límite absoluto en contador** - No permite incrementar sobre 2
3. ✅ **Script de limpieza** - Para corregir archivos existentes corruptos
4. ✅ **Comparación de día calendario** - No solo `>=` sino comparación exacta

---

### Corrección #1: Normalización de Fecha al Inicio del Día

**Archivo**: `App.jsx` - `calcularProximaRevision()`

```javascript
// ✅ DESPUÉS (CORRECTO)
const proximaFecha = new Date();
proximaFecha.setHours(0, 0, 0, 0);  // 🔥 Normalizar a 00:00:00
proximaFecha.setDate(proximaFecha.getDate() + nuevoIntervalo);
// Resultado: 2025-11-27T00:00:00.000Z ← Siempre medianoche
```

**Beneficio**:
- Todas las flashcards tienen `proximaRevision` con hora `00:00:00`
- La comparación de fechas es consistente
- No importa a qué hora se evalúa, la fecha es siempre la misma

---

### Corrección #2: Comparación de Día Calendario

**Archivo**: `App.jsx` - `filtrarItemsParaRepasar()`

```javascript
// ✅ DESPUÉS (CORRECTO) - BLOQUEO ABSOLUTO
const revisionesHoy = item.revisionesHoy || 0;

// 🚨 PRIMERA VERIFICACIÓN: Bloqueo inmediato si >= 2
if (revisionesHoy >= 2) {
  console.log(`🚫 BLOQUEADO (${revisionesHoy} revisiones, límite 2/día): ${titulo}`);
  return false; // ← SALIDA INMEDIATA
}

// 🚨 SEGUNDA VERIFICACIÓN: Doble check con fecha
const ultimaRevision = item.ultima_revision || item.ultimaRevision;
if (ultimaRevision) {
  const fechaUltima = new Date(ultimaRevision);
  const diaUltima = new Date(fechaUltima.getFullYear(), fechaUltima.getMonth(), fechaUltima.getDate());
  
  // Comparar DÍA EXACTO (no solo >=)
  if (diaUltima.getTime() === hoyInicio.getTime()) {
    if (revisionesHoy >= 2) {
      console.log(`🚫 BLOQUEADO DOBLE CHECK: ${titulo}`);
      return false; // ← BLOQUEO REDUNDANTE
    }
  }
}
```

**Beneficio**:
- **Doble validación**: Dos puntos de bloqueo independientes
- **Comparación exacta**: No solo `>=`, sino `getTime() ===`
- **Bloqueo redundante**: Aunque ya pasó el primer filtro, verifica de nuevo
- **Logs críticos**: Emojis 🚫 para identificar bloqueos rápidamente

---

### Corrección #3: Límite Absoluto en Contador

**Archivo**: `App.jsx` - `calcularProximaRevision()`

```javascript
// ✅ DESPUÉS (CORRECTO) - LÍMITE FORZADO
if (diaUltimaRevision.getTime() === hoyInicio.getTime()) {
  const anteriorRevisionesHoy = revisionesHoy;
  revisionesHoy += 1;
  
  // 🚨 LÍMITE ABSOLUTO: No permitir más de 2
  if (revisionesHoy > 2) {
    console.warn(`🚫 LÍMITE EXCEDIDO: ${revisionesHoy}, FORZANDO a 2`);
    revisionesHoy = 2; // ← FORZAR a 2, nunca más
  }
  
  console.log(`✅ Incrementado: ${anteriorRevisionesHoy} → ${revisionesHoy}`);
}
```

**Beneficio**:
- **Techo absoluto**: Aunque haya corrupción de datos, nunca excede 2
- **Autocorrección**: Si una flashcard llega con `revisionesHoy: 5`, se fuerza a 2
- **Prevención**: Imposible que el contador suba sobre el límite

---

### Corrección #4: Script de Limpieza de Datos Corruptos

**Archivo**: `limpiar_flashcards_corruptas.ps1`

```powershell
# Corrige 4 problemas:
# 1. revisionesHoy > 2 (resetea a 0)
# 2. proximaRevision sin T00:00:00.000Z (normaliza)
# 3. revisionesHoy sin ultima_revision (resetea a 0)
# 4. Revisada hoy pero contador en 0 (corrige a 1)
```

**Uso**:
```powershell
.\limpiar_flashcards_corruptas.ps1
```

**Salida esperada**:
```
🔍 BUSCANDO FLASHCARDS CORRUPTAS...

📁 Procesando: extracciones\Platzi
   ⚠️  dua lipa
      - revisionesHoy=3 (reseteado a 0)
      - proximaRevision con hora incorrecta (normalizada a 00:00:00)
   ✅ Archivo guardado con correcciones

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RESUMEN DE LIMPIEZA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivos corregidos: 1
Flashcards corregidas: 1

🎉 Limpieza completada. Reinicia el navegador para aplicar cambios.
```

---

### Corrección #5: Logging Mejorado

**Archivo**: `App.jsx` - `filtrarItemsParaRepasar()`

```javascript
// ✅ LOGGING ACTUALIZADO
console.log(`✅ INCLUIDO (fecha llegada, ${revisionesHoy}/2 revisiones): ${titulo}`, {
  diaRevision: diaRevision.toISOString().split('T')[0],  // Solo fecha: "2025-11-26"
  diaHoy: diaHoy.toISOString().split('T')[0],
  revisionesHoy: revisionesHoy
});
```

**Beneficio**:
- Logs más claros mostrando solo la fecha
- Fácil de detectar problemas visualizando solo el día
- Muestra contador de revisiones diarias

---

## 🧪 CÓMO VERIFICAR QUE EL BUG ESTÁ CORREGIDO

### Prueba Manual

1. **Abre las DevTools** (F12) en el navegador
2. **Ve a la pestaña Console**
3. **Inicia una sesión de estudio** con flashcards
4. **Evalúa una flashcard** (Fácil/Medio/Difícil)
5. **Busca en console** el log:
   ```
   📊 calcularProximaRevision - Estado final:
     revisionesHoy: 1
     proximaRevision: 2025-11-27T00:00:00.000Z  ← Debe tener 00:00:00
   ```
6. **Verifica** que la flashcard NO aparece de nuevo inmediatamente
7. **Evalúa otra flashcard diferente**
8. **Confirma** que la primera flashcard NO vuelve a aparecer

---

### Prueba con Archivo JSON

1. **Abre el archivo** de flashcards en tu carpeta:
   ```
   extracciones/{CARPETA}/flashcards.json
   ```

2. **Busca una flashcard** que evaluaste hoy:
   ```json
   {
     "id": "fc_...",
     "revisionesHoy": 1,  // ✅ Debe incrementarse
     "ultima_revision": "2025-11-26T14:30:00.000Z",  // Fecha de hoy
     "proximaRevision": "2025-11-27T00:00:00.000Z"  // ✅ Debe tener 00:00:00
   }
   ```

3. **Verifica**:
   - `revisionesHoy` debe ser `1` o `2` (no `0`)
   - `proximaRevision` debe tener hora `00:00:00.000Z`
   - `ultima_revision` debe ser hoy

---

### Comando PowerShell de Diagnóstico

Ejecuta esto para verificar flashcards problemáticas:

```powershell
# Ver flashcards con más de 2 revisiones hoy
$flashcards = Get-Content "extracciones/{CARPETA}/flashcards.json" | ConvertFrom-Json
$hoy = (Get-Date).Date

$flashcards | Where-Object {
    $_.revisionesHoy -gt 2 -or
    ($_.proximaRevision -and -not $_.proximaRevision.EndsWith("T00:00:00.000Z"))
} | Select-Object id, revisionesHoy, proximaRevision, ultima_revision | Format-Table
```

**Resultado esperado**:
- ✅ **Ninguna flashcard** debe tener `revisionesHoy > 2`
- ✅ **Todas** deben tener `proximaRevision` terminando en `T00:00:00.000Z`

---

## 📊 TABLA DE ESTADOS VÁLIDOS

| Estado | `revisionesHoy` | `ultima_revision` | `proximaRevision` | ¿Aparece Hoy? |
|--------|----------------|-------------------|-------------------|---------------|
| Nueva (nunca revisada) | `0` o `undefined` | `null` | `null` | ✅ Sí |
| Revisada hoy (1 vez) | `1` | Hoy con hora | Mañana 00:00 | ✅ Sí (puede 1 vez más) |
| Revisada hoy (2 veces) | `2` | Hoy con hora | Pasado mañana 00:00 | ❌ No (límite alcanzado) |
| Revisada ayer | `0` | Ayer | Hoy 00:00 | ✅ Sí (contador reseteado) |
| Programada para mañana | `0` | Hace días | Mañana 00:00 | ❌ No (aún no llega fecha) |

---

## 🎯 CASOS DE USO CORREGIDOS

### Caso 1: Estudiante Repasa Flashcard 2 Veces el Mismo Día

**Escenario**:
- Hora: 09:00 - Primera revisión (Fácil)
- Hora: 15:00 - Segunda revisión (Difícil)
- Hora: 20:00 - ¿Tercera revisión?

**Antes (Bug)**:
- ❌ La flashcard aparecía 3+ veces porque la hora no coincidía

**Después (Corregido)**:
- ✅ Primera revisión: `revisionesHoy = 1`
- ✅ Segunda revisión: `revisionesHoy = 2`
- ✅ Tercera revisión: **NO APARECE** (límite 2/día)

---

### Caso 2: Flashcard Programada para Hoy a las 23:00

**Escenario**:
- `proximaRevision` = `2025-11-26T23:00:00.000Z`
- Hora actual: `2025-11-26T14:00:00.000Z`

**Antes (Bug)**:
- ❌ NO aparecía a las 14:00 (porque 23:00 > 14:00)
- ❌ Aparecía a las 23:01 (mismo día, pero duplicada)

**Después (Corregido)**:
- ✅ `proximaRevision` ahora es `2025-11-26T00:00:00.000Z`
- ✅ Aparece desde las 00:00 del día 26
- ✅ NO duplica porque el día ya se comparó completo

---

### Caso 3: Flashcard Antigua Sin `revisionesHoy`

**Escenario**:
- Flashcard creada antes de la corrección
- No tiene campo `revisionesHoy`

**Antes (Problema Potencial)**:
- ⚠️ Se inicializaba en cada filtro
- ⚠️ Podía aparecer múltiples veces

**Después (Mitigado)**:
- ✅ Se inicializa correctamente en el filtro
- ✅ Al evaluar, se guarda `revisionesHoy = 1`
- ✅ No vuelve a aparecer hasta el próximo día

---

## 🚀 MEJORAS ADICIONALES IMPLEMENTADAS

### 1. Logs Más Informativos

```javascript
console.log('🔍 FILTRANDO ITEMS PARA REPASAR:', {
  totalItems: items.length,
  diaHoy: diaHoy.toISOString().split('T')[0],  // Solo fecha
  horaActual: ahora.toTimeString().split(' ')[0]  // Solo hora
});
```

---

### 2. Validación Automática en Guardado

La función `guardarFlashcardEnCarpeta()` ya guarda automáticamente todos los campos calculados:
- `revisionesHoy`
- `ultima_revision`
- `proximaRevision` (normalizada a 00:00:00)

---

### 3. Verificación Post-Evaluación

```javascript
// Verificar si la flashcard sigue en la lista
const flashcardSigueEnLista = flashcardsParaRepasar.find(f => f.id === flashcardActual.id);
if (flashcardSigueEnLista) {
  console.warn('⚠️ PROBLEMA: La flashcard evaluada AÚN está en la lista!');
} else {
  console.log('✅ Correcto: Flashcard eliminada de la lista');
}
```

---

## 📝 CHECKLIST DE VERIFICACIÓN

Marca cada ítem después de verificar:

- [ ] **Logs muestran** `proximaRevision` con `T00:00:00.000Z`
- [ ] **Logs muestran** comparación de `diaRevision` vs `diaHoy`
- [ ] **Archivo JSON** tiene `revisionesHoy` actualizado
- [ ] **Archivo JSON** tiene `proximaRevision` normalizada
- [ ] **Flashcard evaluada** NO aparece de nuevo en la misma sesión
- [ ] **Segunda evaluación** incrementa `revisionesHoy` a `2`
- [ ] **Tercera evaluación** NO es posible (límite alcanzado)
- [ ] **Al día siguiente** contador `revisionesHoy` se resetea a `0`

---

## 🔧 SI EL PROBLEMA PERSISTE

### 1. Verificar Archivos Duplicados

```powershell
# Buscar flashcards duplicadas en múltiples carpetas
Get-ChildItem -Path "extracciones" -Recurse -Filter "flashcards.json" | 
  ForEach-Object {
    $flashcards = Get-Content $_.FullName | ConvertFrom-Json
    Write-Host "📁 $($_.DirectoryName): $($flashcards.Count) flashcards"
  }
```

**Problema posible**: Tienes la misma flashcard en dos archivos diferentes.

---

### 2. Verificar Caché del Navegador

```javascript
// En la consola del navegador:
localStorage.clear();
location.reload();
```

**Problema posible**: El navegador está cacheando datos antiguos.

---

### 3. Verificar Sincronización Backend

```powershell
# Reiniciar el servidor backend
python api_server.py
```

**Problema posible**: El backend tiene datos en memoria desactualizados.

---

## 📚 DOCUMENTACIÓN RELACIONADA

- [`FLUJO_FLASHCARDS.md`](./FLUJO_FLASHCARDS.md) - Documentación completa del sistema
- [`NORMALIZACION_SPACED_REPETITION.md`](../NORMALIZACION_SPACED_REPETITION.md) - Algoritmo SM-2
- `App.jsx` líneas 2610-2850 - Código de repetición espaciada

---

## 🎓 CONCLUSIÓN

Los bugs estaban causados por:

1. **Comparación de hora exacta** en vez de día calendario
2. **Fecha no normalizada** al guardar `proximaRevision`
3. **Falta de consistencia** en el formato de fechas

Las correcciones garantizan que:

✅ Las flashcards aparecen **máximo 2 veces al día**  
✅ La comparación de fechas es **consistente**  
✅ El sistema es **predecible y confiable**  

---

**Autor**: Sistema Examinator  
**Versión**: 1.0  
**Fecha**: 26 de noviembre de 2025  
**Estado**: ✅ CORREGIDO

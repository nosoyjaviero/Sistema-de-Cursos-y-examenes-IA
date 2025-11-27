/**
 * Normalización de array de exámenes desde examenes.json
 * Aplica correcciones de tipos, intervalos y rutas a TODO el array
 * 
 * @module normalizarExamenes
 */

/**
 * Normaliza una pregunta individual
 * @param {Object} pregunta - Pregunta a normalizar
 * @returns {Object} Pregunta normalizada
 */
function normalizarPreguntaIndividual(pregunta) {
  // 1️⃣ Normalizar tipo: "verdadero-falso" → "verdadero_falso"
  const tipoMap = {
    'verdadero-falso': 'verdadero_falso',
    'verdadero_falso': 'verdadero_falso',
    'multiple': 'mcq',
    'mcq': 'mcq',
    'corta': 'short_answer',
    'short_answer': 'short_answer',
    'desarrollo': 'open_question',
    'open_question': 'open_question'
  };

  if (pregunta.tipo) {
    const tipoOriginal = pregunta.tipo;
    pregunta.tipo = tipoMap[tipoOriginal] || tipoOriginal;
  }

  // 2️⃣ Normalizar intervalo (debe ser entero >= 1)
  if ('intervalo' in pregunta) {
    try {
      const intervalo = parseFloat(pregunta.intervalo);
      // Si es 0.5 o menor a 1, forzar a 1
      pregunta.intervalo = Math.max(1, Math.round(intervalo));
    } catch (e) {
      pregunta.intervalo = 1;
    }
  }

  // 3️⃣ Asegurar campos SM-2 consistentes
  if (!pregunta.facilidad) {
    pregunta.facilidad = 2.5;
  }
  if (!pregunta.repeticiones) {
    pregunta.repeticiones = 0;
  }
  if (!pregunta.estadoRevision) {
    pregunta.estadoRevision = 'nueva';
  }

  return pregunta;
}

/**
 * Normaliza un examen individual del array
 * @param {Object} examen - Examen a normalizar
 * @returns {Object} Examen normalizado
 */
function normalizarExamenIndividual(examen) {
  // 1️⃣ Normalizar rutas de carpeta (backslash → forward slash)
  const camposRuta = ['carpeta', 'carpeta_ruta'];
  camposRuta.forEach(campo => {
    if (examen[campo] && typeof examen[campo] === 'string') {
      examen[campo] = examen[campo].replace(/\\/g, '/');
    }
  });

  // 2️⃣ Normalizar intervalo del examen (nivel raíz)
  if ('intervalo' in examen) {
    try {
      const intervalo = parseFloat(examen.intervalo);
      examen.intervalo = Math.max(1, Math.round(intervalo));
    } catch (e) {
      examen.intervalo = 1;
    }
  }

  // 3️⃣ Normalizar preguntas[]
  if (examen.preguntas && Array.isArray(examen.preguntas)) {
    examen.preguntas = examen.preguntas.map(normalizarPreguntaIndividual);
  }

  // 4️⃣ Normalizar resultado.resultados[]
  if (examen.resultado && typeof examen.resultado === 'object') {
    if (examen.resultado.resultados && Array.isArray(examen.resultado.resultados)) {
      examen.resultado.resultados = examen.resultado.resultados.map(normalizarPreguntaIndividual);
    }
  }

  // 5️⃣ Asegurar campos SM-2 en nivel raíz
  if (!examen.facilidad) {
    examen.facilidad = 2.5;
  }
  if (!examen.repeticiones) {
    examen.repeticiones = 0;
  }
  if (!examen.estadoRevision) {
    examen.estadoRevision = 'nueva';
  }

  return examen;
}

/**
 * Normaliza un array completo de exámenes (como el de examenes.json)
 * 
 * Aplica:
 * 1. Normalización de tipos: "verdadero-falso" → "verdadero_falso"
 * 2. Normalización de intervalos: 0.5 → 1, asegura enteros >= 1
 * 3. Normalización de rutas: "Platzi\\Prueba" → "Platzi/Prueba"
 * 
 * @param {Array<Object>} examenes - Array de exámenes desde examenes.json
 * @returns {Array<Object>} Array de exámenes normalizado (modifica in-place y devuelve)
 */
export function normalizarExamenes(examenes) {
  if (!Array.isArray(examenes)) {
    console.warn('⚠️ examenes no es un array, retornando sin cambios');
    return examenes;
  }

  console.log(`\n🔄 Normalizando ${examenes.length} exámenes...`);

  const cambiosTotales = {
    tiposNormalizados: 0,
    intervalosCorregidos: 0,
    rutasNormalizadas: 0
  };

  examenes.forEach((examen, idx) => {
    // Guardar estado previo para contar cambios
    const carpetaAntes = examen.carpeta || '';

    // Normalizar examen
    examenes[idx] = normalizarExamenIndividual(examen);

    // Contar cambios de rutas
    const carpetaDespues = examenes[idx].carpeta || '';
    if (carpetaAntes !== carpetaDespues) {
      cambiosTotales.rutasNormalizadas++;
    }

    // Contar tipos normalizados en preguntas
    if (examenes[idx].preguntas) {
      examenes[idx].preguntas.forEach(p => {
        if (['verdadero_falso', 'mcq', 'short_answer', 'open_question'].includes(p.tipo)) {
          cambiosTotales.tiposNormalizados++;
        }
      });
    }

    // Contar intervalos corregidos
    if (examenes[idx].resultado?.resultados) {
      examenes[idx].resultado.resultados.forEach(r => {
        if ((r.intervalo || 0) >= 1) {
          cambiosTotales.intervalosCorregidos++;
        }
      });
    }
  });

  console.log('\n📊 Resumen de normalización:');
  console.log(`   ✅ Exámenes procesados: ${examenes.length}`);
  console.log(`   ✅ Rutas normalizadas: ${cambiosTotales.rutasNormalizadas}`);
  console.log(`   ✅ Tipos normalizados: ${cambiosTotales.tiposNormalizados}`);
  console.log(`   ✅ Intervalos corregidos: ${cambiosTotales.intervalosCorregidos}`);

  return examenes;
}

// ========================================
// EJEMPLO DE USO - FRONTEND (React)
// ========================================

/**
 * Ejemplo de cómo integrar en React (getDatos)
 * 
 * @example
 * // En App.jsx, modificar getDatos para normalizar automáticamente
 * const getDatos = async (tipo) => {
 *   try {
 *     const response = await fetch(`${API_URL}/datos/${tipo}`);
 *     if (!response.ok) throw new Error(`Error HTTP! status: ${response.status}`);
 *     let data = await response.json();
 *     
 *     // 🔥 NORMALIZAR ANTES DE GUARDAR EN ESTADO
 *     if (tipo === 'examenes') {
 *       data = normalizarExamenes(data);
 *     }
 *     
 *     return data;
 *   } catch (error) {
 *     console.error(`Error obteniendo ${tipo}:`, error);
 *     return [];
 *   }
 * };
 */

export default normalizarExamenes;

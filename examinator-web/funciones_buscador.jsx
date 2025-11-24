// Funciones para el Buscador IA
// Agregar estas funciones en App.jsx después de las funciones de flashcards

// Función para buscar con la API
const buscarConIA = async () => {
  if (!queryBusqueda.trim()) {
    setMensaje({ tipo: 'error', texto: 'Escribe algo para buscar' });
    return;
  }

  setBuscando(true);
  setResultadosBusqueda([]);

  try {
    const response = await fetch('http://localhost:5001/api/buscar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: queryBusqueda,
        tipo: filtroBusquedaTipo === 'todos' ? null : filtroBusquedaTipo,
        max_resultados: 20
      })
    });

    if (!response.ok) {
      throw new Error('Error en la búsqueda');
    }

    const data = await response.json();
    setResultadosBusqueda(data.resultados || []);
    setMensaje({ 
      tipo: 'exito', 
      texto: `✅ ${data.total} resultados en ${data.tiempo}s` 
    });

  } catch (error) {
    console.error('Error buscando:', error);
    setMensaje({ 
      tipo: 'error', 
      texto: '❌ Error al buscar. Asegúrate de que el servidor esté corriendo (python api_buscador.py)' 
    });
  } finally {
    setBuscando(false);
  }
};

// Función para actualizar el índice
const actualizarIndice = async (completo = false) => {
  if (actualizandoIndice) return;

  setActualizandoIndice(true);
  setMensaje({ 
    tipo: 'info', 
    texto: completo ? '🔄 Reindexando todo...' : '🔄 Actualizando índice...' 
  });

  try {
    const response = await fetch('http://localhost:5001/api/actualizar_indice', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ completo })
    });

    if (!response.ok) {
      throw new Error('Error actualizando índice');
    }

    const data = await response.json();
    setMensaje({ 
      tipo: 'exito', 
      texto: `✅ Índice actualizado: ${data.archivos_procesados} archivos, ${data.chunks_indexados} chunks. Total: ${data.total_chunks}` 
    });

    // Actualizar estado
    cargarEstadoIndice();

  } catch (error) {
    console.error('Error actualizando índice:', error);
    setMensaje({ 
      tipo: 'error', 
      texto: '❌ Error al actualizar índice. Servidor no disponible.' 
    });
  } finally {
    setActualizandoIndice(false);
  }
};

// Función para cargar estado del índice
const cargarEstadoIndice = async () => {
  try {
    const response = await fetch('http://localhost:5001/api/estado');
    
    if (response.ok) {
      const data = await response.json();
      setEstadoIndice(data);
    }
  } catch (error) {
    console.error('Error cargando estado:', error);
  }
};

// Función para abrir archivo desde resultado
const abrirArchivoBusqueda = (ruta) => {
  // Detectar tipo y navegar
  const rutaLower = ruta.toLowerCase();
  
  if (rutaLower.includes('flashcard')) {
    setSelectedMenu('flashcards');
    // Extraer carpeta
    const carpeta = ruta.split('\\').slice(0, -1).join('\\');
    cargarCarpetasFlashcards(carpeta.split('flashcards\\')[1] || '');
  } else if (rutaLower.includes('nota')) {
    setSelectedMenu('notas');
    const carpeta = ruta.split('\\').slice(0, -1).join('\\');
    cargarCarpetasNotas(carpeta.split('notas\\')[1] || '');
  } else if (rutaLower.includes('curso')) {
    setSelectedMenu('cursos');
    const carpeta = ruta.split('\\').slice(0, -1).join('\\');
    cargarCarpeta(carpeta.split('cursos\\')[1] || '');
  } else {
    setMensaje({ tipo: 'info', texto: `📁 Archivo: ${ruta}` });
  }
};

// useEffect para cargar estado al montar
useEffect(() => {
  if (selectedMenu === 'buscar' && !estadoIndice) {
    cargarEstadoIndice();
  }
}, [selectedMenu]);

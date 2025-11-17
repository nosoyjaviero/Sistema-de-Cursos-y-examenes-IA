import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [selectedMenu, setSelectedMenu] = useState('inicio')
  const [rutaActual, setRutaActual] = useState('')
  const [carpetas, setCarpetas] = useState([])
  const [documentos, setDocumentos] = useState([])
  const [loading, setLoading] = useState(false)
  const [mensaje, setMensaje] = useState(null)
  const [visorAbierto, setVisorAbierto] = useState(false)
  const [documentoActual, setDocumentoActual] = useState(null)
  const [modoEdicion, setModoEdicion] = useState(false)
  const [contenidoEditado, setContenidoEditado] = useState('')
  const [leyendo, setLeyendo] = useState(false)
  const [pausado, setPausado] = useState(false)
  const [posicionLectura, setPosicionLectura] = useState({ inicio: 0, fin: 0 })
  const [menuAbierto, setMenuAbierto] = useState(null)
  const [moverCarpeta, setMoverCarpeta] = useState(null)
  const [modalMoverAbierto, setModalMoverAbierto] = useState(false)
  const [rutaDestinoSeleccionada, setRutaDestinoSeleccionada] = useState('')
  const [carpetasDestino, setCarpetasDestino] = useState([])
  const [modelosDisponibles, setModelosDisponibles] = useState([])
  const [configuracion, setConfiguracion] = useState(null)
  const [modeloSeleccionado, setModeloSeleccionado] = useState(null)
  const [cargandoConfig, setCargandoConfig] = useState(false)
  const [modelosParaDescargar, setModelosParaDescargar] = useState([])
  const [mostrarDescarga, setMostrarDescarga] = useState(false)
  const [mensajesChat, setMensajesChat] = useState([])
  const [inputChat, setInputChat] = useState('')
  const [cargandoChat, setCargandoChat] = useState(false)
  const [editandoMensaje, setEditandoMensaje] = useState(null)
  const [textoEditado, setTextoEditado] = useState('')
  const [historialChats, setHistorialChats] = useState([])
  const [chatActualId, setChatActualId] = useState(null)
  const [nombreChatNuevo, setNombreChatNuevo] = useState('')
  const [mostrarModalHistorial, setMostrarModalHistorial] = useState(false)
  const [archivoContexto, setArchivoContexto] = useState(null)
  const [contenidoContexto, setContenidoContexto] = useState('')
  const [nombreArchivoContexto, setNombreArchivoContexto] = useState('')
  const [busquedaWebActiva, setBusquedaWebActiva] = useState(false)
  
  // Estados para carpetas de chats (proyectos)
  const [carpetasChats, setCarpetasChats] = useState([])
  const [carpetaChatActual, setCarpetaChatActual] = useState('')
  const [mostrarModalCarpetas, setMostrarModalCarpetas] = useState(false)
  
  // Estados para exámenes
  const [examenActivo, setExamenActivo] = useState(null)
  const [preguntasExamen, setPreguntasExamen] = useState([])
  const [respuestasUsuario, setRespuestasUsuario] = useState({})
  const [resultadoExamen, setResultadoExamen] = useState(null)
  const [carpetaExamen, setCarpetaExamen] = useState(null)
  const [generandoExamen, setGenerandoExamen] = useState(false)
  const [abortController, setAbortController] = useState(null)
  const [progresoGeneracion, setProgresoGeneracion] = useState(0)
  const [mensajeProgreso, setMensajeProgreso] = useState('')
  const [sessionIdGeneracion, setSessionIdGeneracion] = useState(null)
  const [modalExamenAbierto, setModalExamenAbierto] = useState(false)
  const [configExamen, setConfigExamen] = useState({
    num_multiple: 8,
    num_corta: 5,
    num_desarrollo: 3
  })
  const [examenesGuardados, setExamenesGuardados] = useState({
    completados: [],
    enProgreso: []
  })
  const [viendoExamen, setViendoExamen] = useState(null)
  const [modalListaExamenes, setModalListaExamenes] = useState(false)
  
  // Estados para modal de configuración de generación de examen
  const [modalConfigExamen, setModalConfigExamen] = useState(false)
  const [carpetaConfigExamen, setCarpetaConfigExamen] = useState(null)
  const [archivosDisponibles, setArchivosDisponibles] = useState([])
  const [archivosSeleccionados, setArchivosSeleccionados] = useState([])
  const [promptPersonalizado, setPromptPersonalizado] = useState('')
  const [promptSistema, setPromptSistema] = useState('')
  const [rutaExploracion, setRutaExploracion] = useState('')
  const [carpetasExploracion, setCarpetasExploracion] = useState([])
  
  // Estados para navegación de carpetas de exámenes
  const [rutaActualExamenes, setRutaActualExamenes] = useState('')
  const [carpetasExamenes, setCarpetasExamenes] = useState([])
  const [examenesCompletados, setExamenesCompletados] = useState([])
  const [examenesProgreso, setExamenesProgreso] = useState([])
  const [examenesProgresoGlobal, setExamenesProgresoGlobal] = useState([])
  
  // Estados para reconocimiento de voz
  const [reconocimientoVoz, setReconocimientoVoz] = useState(null)
  const [escuchandoPregunta, setEscuchandoPregunta] = useState(null)
  const [transcripcionTemp, setTranscripcionTemp] = useState('')
  
  // Estados para menú móvil
  const [menuMovilAbierto, setMenuMovilAbierto] = useState(false)
  
  // Estados para ajustes avanzados
  const [ajustesAvanzados, setAjustesAvanzados] = useState({
    n_ctx: 4096,
    temperature: 0.7,
    max_tokens: 512,
    top_p: 0.9,
    repeat_penalty: 1.15,
    n_gpu_layers: 35
  })
  const [mostrarAjustesAvanzados, setMostrarAjustesAvanzados] = useState(false)
  
  // Estados para Ollama
  const [modelosOllama, setModelosOllama] = useState([])
  const [pestanaModelos, setPestanaModelos] = useState('ollama') // 'ollama' o 'gguf'

  // Estados para navegación en modal de historial
  const [rutaHistorialModal, setRutaHistorialModal] = useState('')
  const [carpetasHistorialModal, setCarpetasHistorialModal] = useState([])
  const [chatsHistorialModal, setChatsHistorialModal] = useState([])
  const [loadingHistorialModal, setLoadingHistorialModal] = useState(false)

  // Detectar automáticamente la URL del API
  // Si accedes desde otra IP (móvil/tablet), usa esa IP para el backend
  // Si accedes desde localhost, usa localhost
  const getApiUrl = () => {
    const hostname = window.location.hostname
    const apiUrl = (hostname === 'localhost' || hostname === '127.0.0.1') 
      ? 'http://localhost:8000' 
      : `http://${hostname}:8000`
    
    // Debug: mostrar en consola qué URL está usando
    console.log(`🌐 Frontend: ${window.location.hostname}:${window.location.port}`)
    console.log(`🔌 Backend API: ${apiUrl}`)
    
    return apiUrl
  }

  const API_URL = getApiUrl()

  // Auto-ocultar mensajes después de 8 segundos
  useEffect(() => {
    if (mensaje) {
      const timer = setTimeout(() => {
        setMensaje(null)
      }, 8000)
      
      return () => clearTimeout(timer)
    }
  }, [mensaje])

  // Recargar exámenes cuando se cambia a la pestaña "generar"
  useEffect(() => {
    if (selectedMenu === 'generar') {
      cargarCarpetasExamenes()
    }
  }, [selectedMenu])

  // Cargar prompt del sistema al inicio (solo una vez)
  useEffect(() => {
    const cargarPromptInicial = async () => {
      try {
        console.log('🔄 Cargando prompt del sistema...')
        const promptResp = await fetch(`${API_URL}/api/prompt-personalizado`)
        const promptData = await promptResp.json()
        
        if (promptData.prompt) {
          // Hay un prompt guardado, usarlo
          console.log('✅ Prompt guardado cargado')
          setPromptSistema(promptData.prompt)
        } else {
          // No hay prompt guardado, cargar el template
          console.log('📝 Cargando template predeterminado...')
          const templateResp = await fetch(`${API_URL}/api/prompt-template`)
          const templateData = await templateResp.json()
          setPromptSistema(templateData.template)
          console.log('✅ Template cargado')
        }
      } catch (error) {
        console.error('❌ Error cargando prompt inicial:', error)
        // Si hay error, cargar un prompt por defecto simple
        setPromptSistema('Eres un profesor universitario experto. Crea preguntas basadas en:\n{contenido}\n\nGenera {total_preguntas} preguntas en formato JSON.')
      }
    }
    
    cargarPromptInicial()
  }, [])  // Solo se ejecuta una vez al montar el componente

  // Cargar configuración del modelo al inicio
  useEffect(() => {
    cargarConfiguracion()
  }, [])  // Solo una vez al montar
  
  // Cargar carpetas de exámenes (estructura paralela)
  const cargarCarpetasExamenes = async (ruta = '') => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/examenes/carpetas?ruta=${encodeURIComponent(ruta)}`)
      const data = await response.json()
      
      setCarpetasExamenes(data.carpetas || [])
      setExamenesCompletados(data.examenes_completados || [])
      setExamenesProgreso(data.examenes_progreso || [])
      setExamenesProgresoGlobal(data.examenes_progreso_global || [])
      setRutaActualExamenes(ruta)
      
      console.log('Carpetas exámenes:', data.carpetas)
      console.log('Exámenes en progreso (carpeta actual):', data.examenes_progreso)
      console.log('Exámenes en progreso (global):', data.examenes_progreso_global)
    } catch (error) {
      console.error('Error cargando exámenes:', error)
      setMensaje({
        tipo: 'error',
        texto: '❌ Error al cargar exámenes'
      })
    } finally {
      setLoading(false)
    }
  }

  // Cargar contenido de carpeta
  const cargarCarpeta = async (ruta = '') => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/carpetas?ruta=${encodeURIComponent(ruta)}`)
      const data = await response.json()
      setCarpetas(data.carpetas || [])
      setDocumentos(data.documentos || [])
      setRutaActual(ruta)
    } catch (error) {
      console.error('Error al cargar carpeta:', error)
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al cargar carpeta: ${error.message}`
      })
    } finally {
      setLoading(false)
    }
  }

  // Crear carpeta
  const crearCarpeta = async () => {
    const nombre = prompt('Nombre de la nueva carpeta:')
    if (!nombre) return

    try {
      const response = await fetch(`${API_URL}/api/carpetas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          ruta_padre: rutaActual, 
          nombre: nombre 
        })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Carpeta "${nombre}" creada exitosamente`
        })
        cargarCarpeta(rutaActual)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al crear carpeta: ${error.message}`
      })
    }
  }

  // Eliminar carpeta
  const eliminarCarpeta = async (ruta, nombre) => {
    const confirmMsg = `¿Eliminar la carpeta "${nombre}"?\n\nSi tiene contenido, se eliminará TODO (carpetas y documentos dentro).`
    if (!confirm(confirmMsg)) return

    try {
      const response = await fetch(`${API_URL}/api/carpetas?ruta=${encodeURIComponent(ruta)}&forzar=true`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Carpeta eliminada'
        })
        cargarCarpeta(rutaActual)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ ${error.message}`
      })
    }
  }

  // Eliminar carpeta de exámenes
  const eliminarCarpetaExamenes = async (ruta, nombre) => {
    const confirmMsg = `¿Eliminar la carpeta de exámenes "${nombre}"?\n\nSe eliminarán TODOS los exámenes dentro (completados y en progreso).`
    if (!confirm(confirmMsg)) return

    try {
      const response = await fetch(`${API_URL}/api/examenes/carpeta?ruta=${encodeURIComponent(ruta)}&forzar=true`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Carpeta de exámenes eliminada'
        })
        cargarCarpetasExamenes(rutaActualExamenes)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ ${error.message}`
      })
    }
  }

  // Eliminar examen individual
  const eliminarExamen = async (examen, tipo) => {
    const tipoTexto = tipo === 'progreso' ? 'en progreso' : 'completado'
    const confirmMsg = `¿Eliminar el examen ${tipoTexto} "${examen.carpeta_nombre}"?`
    if (!confirm(confirmMsg)) return

    try {
      // Determinar el nombre del archivo según el tipo
      let nombreArchivo
      if (tipo === 'progreso') {
        // Los exámenes en progreso están en examenes_progreso/
        nombreArchivo = examen.archivo || `examen_progreso_${examen.id}.json`
      } else {
        // Los exámenes completados están en la raíz de la carpeta
        nombreArchivo = examen.archivo || `examen_${examen.id}.json`
      }

      const ruta = examen.carpeta_ruta || rutaActualExamenes
      const response = await fetch(`${API_URL}/api/examenes/examen?ruta=${encodeURIComponent(ruta)}&archivo=${encodeURIComponent(nombreArchivo)}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Examen eliminado'
        })
        cargarCarpetasExamenes(rutaActualExamenes)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ ${error.message}`
      })
    }
  }

  // Renombrar carpeta
  const renombrarCarpeta = async (ruta, nombreActual) => {
    const nuevoNombre = prompt(`Renombrar carpeta "${nombreActual}":`, nombreActual)
    if (!nuevoNombre || nuevoNombre === nombreActual) return

    try {
      const response = await fetch(`${API_URL}/api/carpetas/renombrar`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          ruta_actual: ruta,
          nuevo_nombre: nuevoNombre 
        })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Carpeta renombrada a "${nuevoNombre}"`
        })
        cargarCarpeta(rutaActual)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ ${error.message}`
      })
    }
  }

  // Iniciar proceso de mover carpeta
  const iniciarMoverCarpeta = (carpeta) => {
    setMoverCarpeta(carpeta)
    setMenuAbierto(null)
    setModalMoverAbierto(true)
    setRutaDestinoSeleccionada(rutaActual)
    cargarCarpetasDestino(rutaActual)
  }

  // Cargar carpetas para selector de destino
  const cargarCarpetasDestino = async (ruta = '') => {
    try {
      const response = await fetch(`${API_URL}/api/carpetas?ruta=${encodeURIComponent(ruta)}`)
      const data = await response.json()
      setCarpetasDestino(data.carpetas || [])
      setRutaDestinoSeleccionada(ruta)
    } catch (error) {
      console.error('Error al cargar carpetas destino:', error)
    }
  }

  // Confirmar mover carpeta
  const confirmarMoverCarpeta = async () => {
    if (!moverCarpeta) return

    // Obtener la ruta padre de la carpeta actual
    const rutaPadreOrigen = moverCarpeta.ruta.split('\\').slice(0, -1).join('\\')

    // Validar que no se esté moviendo a su misma ubicación (mismo padre)
    if (rutaPadreOrigen === rutaDestinoSeleccionada) {
      setMensaje({
        tipo: 'error',
        texto: '❌ No puedes mover una carpeta a su misma ubicación actual'
      })
      return
    }

    // Validar que no se esté moviendo dentro de sí misma
    if (rutaDestinoSeleccionada.startsWith(moverCarpeta.ruta + '\\') || 
        rutaDestinoSeleccionada === moverCarpeta.ruta) {
      setMensaje({
        tipo: 'error',
        texto: '❌ No puedes mover una carpeta dentro de sí misma'
      })
      return
    }

    try {
      const response = await fetch(`${API_URL}/api/carpetas/mover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ruta_origen: moverCarpeta.ruta,
          ruta_destino: rutaDestinoSeleccionada
        })
      })

      const data = await response.json()
      
      if (response.ok && data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Carpeta "${moverCarpeta.nombre}" movida exitosamente`
        })
        setMoverCarpeta(null)
        setModalMoverAbierto(false)
        cargarCarpeta(rutaDestinoSeleccionada) // Recargar la carpeta destino
      } else {
        setMensaje({
          tipo: 'error',
          texto: `❌ ${data.detail || data.error || 'Error al mover carpeta'}`
        })
        setModalMoverAbierto(false)
      }
    } catch (error) {
      console.error('Error al mover carpeta:', error)
      setMensaje({
        tipo: 'error',
        texto: `❌ Error de conexión: ${error.message}`
      })
      setModalMoverAbierto(false)
    }
  }

  // Cancelar mover carpeta
  const cancelarMoverCarpeta = () => {
    setMoverCarpeta(null)
    setModalMoverAbierto(false)
    setRutaDestinoSeleccionada('')
    setCarpetasDestino([])
  }

  // Cargar configuración y modelos
  const cargarConfiguracion = async () => {
    setCargandoConfig(true)
    try {
      // Cargar configuración actual
      const configResponse = await fetch(`${API_URL}/api/config`)
      const configData = await configResponse.json()
      console.log('Configuración cargada:', configData)
      setConfiguracion(configData)
      setModeloSeleccionado(configData.modelo_path || null)
      
      // Cargar ajustes avanzados si existen en la configuración
      if (configData.ajustes_avanzados) {
        setAjustesAvanzados({
          n_ctx: configData.ajustes_avanzados.n_ctx || 4096,
          temperature: configData.ajustes_avanzados.temperature || 0.7,
          max_tokens: configData.ajustes_avanzados.max_tokens || 512,
          top_p: configData.ajustes_avanzados.top_p || 0.9,
          repeat_penalty: configData.ajustes_avanzados.repeat_penalty || 1.15
        })
        console.log('⚙️ Ajustes avanzados cargados:', configData.ajustes_avanzados)
      }

      // Cargar modelos instalados
      const modelosResponse = await fetch(`${API_URL}/api/modelos`)
      const modelosData = await modelosResponse.json()
      console.log('Modelos instalados:', modelosData)
      setModelosDisponibles(modelosData.modelos || [])

      // Cargar modelos disponibles para descargar
      const descargablesResponse = await fetch(`${API_URL}/api/modelos/disponibles`)
      const descargablesData = await descargablesResponse.json()
      console.log('Modelos para descargar:', descargablesData)
      setModelosParaDescargar(descargablesData.modelos || [])
    } catch (error) {
      console.error('Error al cargar configuración:', error)
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al cargar configuración: ${error.message}`
      })
    } finally {
      setCargandoConfig(false)
    }
  }

  // Guardar configuración
  const guardarConfiguracion = async () => {
    if (!modeloSeleccionado) {
      setMensaje({
        tipo: 'error',
        texto: '❌ Debes seleccionar un modelo'
      })
      return
    }

    setCargandoConfig(true)
    try {
      const response = await fetch(`${API_URL}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          modelo_path: modeloSeleccionado,
          ajustes_avanzados: ajustesAvanzados
        })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Modelo cambiado exitosamente. Recarga la configuración para verificar.'
        })
        // Recargar configuración para verificar
        cargarConfiguracion()
      } else {
        setMensaje({
          tipo: 'error',
          texto: `❌ ${data.message || 'Error al cambiar modelo'}`
        })
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    } finally {
      setCargandoConfig(false)
    }
  }

  // Guardar solo ajustes avanzados (sin mostrar mensaje)
  const guardarAjustesAvanzados = async () => {
    try {
      // Obtener configuración actual
      const configResponse = await fetch(`${API_URL}/api/config`)
      const configData = await configResponse.json()
      
      // Guardar con ajustes actualizados
      await fetch(`${API_URL}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          modelo_path: configData.modelo_path,
          ajustes_avanzados: ajustesAvanzados
        })
      })
      
      console.log('⚙️ Ajustes avanzados guardados:', ajustesAvanzados)
    } catch (error) {
      console.error('Error guardando ajustes:', error)
    }
  }

  // Enviar mensaje al chat
  const enviarMensajeChat = async () => {
    if (!inputChat.trim() || cargandoChat) return

    const mensaje = inputChat.trim()
    setInputChat('')
    
    // Agregar mensaje del usuario
    const horaNueva = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    const mensajeUsuario = {
      tipo: 'usuario',
      texto: mensaje,
      hora: horaNueva
    }
    
    // Si hay archivo de contexto, agregarlo al mensaje
    if (archivoContexto) {
      mensajeUsuario.archivo = nombreArchivoContexto
    }
    
    // Si hay búsqueda web activa, agregarlo
    if (busquedaWebActiva) {
      mensajeUsuario.busqueda_web = true
    }
    
    setMensajesChat(prev => [...prev, mensajeUsuario])

    // Crear AbortController para poder cancelar la petición
    const controller = new AbortController()
    setAbortController(controller)

    setCargandoChat(true)
    try {
      console.log('⚙️ Configuración avanzada:', ajustesAvanzados)
      
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mensaje,
          contexto: contenidoContexto || null,
          buscar_web: busquedaWebActiva,
          historial: mensajesChat,  // Enviar historial completo para mantener contexto
          ajustes: ajustesAvanzados  // Enviar configuración avanzada
        }),
        signal: controller.signal
      })

      const data = await response.json()
      
      // Agregar respuesta del asistente
      const nuevaRespuesta = {
        tipo: 'asistente',
        texto: data.respuesta || 'Error al obtener respuesta',
        hora: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
      }
      setMensajesChat(prev => {
        const nuevosMensajes = [...prev, nuevaRespuesta]
        // Guardar automáticamente después de cada respuesta
        guardarAutomaticamente(nuevosMensajes)
        return nuevosMensajes
      })
    } catch (error) {
      if (error.name === 'AbortError') {
        setMensajesChat(prev => [...prev, {
          tipo: 'asistente',
          texto: '⚠️ Consulta cancelada por el usuario',
          hora: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
        }])
      } else {
        setMensajesChat(prev => [...prev, {
          tipo: 'asistente',
          texto: `❌ Error: ${error.message}`,
          hora: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
        }])
      }
    } finally {
      setCargandoChat(false)
      setAbortController(null)
    }
  }

  // Detener/cancelar la consulta
  const detenerConsulta = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
      setCargandoChat(false)
    }
  }

  // Editar mensaje del usuario
  const iniciarEdicionMensaje = (index) => {
    setEditandoMensaje(index)
    setTextoEditado(mensajesChat[index].texto)
  }

  const cancelarEdicion = () => {
    setEditandoMensaje(null)
    setTextoEditado('')
  }

  const guardarEdicionMensaje = async (index) => {
    if (!textoEditado.trim() || cargandoChat) return

    const mensajeEditado = textoEditado.trim()
    
    // Actualizar el mensaje editado
    const nuevosMensajes = [...mensajesChat]
    nuevosMensajes[index].texto = mensajeEditado
    
    // Eliminar mensajes posteriores (respuesta del asistente y mensajes siguientes)
    const mensajesHastaEditado = nuevosMensajes.slice(0, index + 1)
    setMensajesChat(mensajesHastaEditado)
    
    setEditandoMensaje(null)
    setTextoEditado('')
    
    // Crear AbortController para poder cancelar la petición
    const controller = new AbortController()
    setAbortController(controller)
    
    // Reenviar el mensaje editado al asistente
    setCargandoChat(true)
    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mensaje: mensajeEditado,
          historial: mensajesHastaEditado  // Enviar historial actualizado
        }),
        signal: controller.signal
      })

      const data = await response.json()
      
      // Agregar nueva respuesta del asistente
      setMensajesChat(prev => [...prev, {
        tipo: 'asistente',
        texto: data.respuesta || 'Error al obtener respuesta',
        hora: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
      }])
    } catch (error) {
      if (error.name === 'AbortError') {
        setMensajesChat(prev => [...prev, {
          tipo: 'asistente',
          texto: '⚠️ Consulta cancelada por el usuario',
          hora: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
        }])
      } else {
        setMensajesChat(prev => [...prev, {
          tipo: 'asistente',
          texto: `❌ Error: ${error.message}`,
          hora: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
        }])
      }
    } finally {
      setCargandoChat(false)
      setAbortController(null)
    }
  }

  // Manejar carga de archivo al chat
  const handleArchivoContexto = async (e) => {
    const archivo = e.target.files[0]
    if (!archivo) return

    const extension = archivo.name.split('.').pop().toLowerCase()
    
    if (extension === 'txt') {
      // Leer archivo TXT directamente
      const reader = new FileReader()
      reader.onload = (event) => {
        setContenidoContexto(event.target.result)
        setNombreArchivoContexto(archivo.name)
        setArchivoContexto(archivo)
        setMensaje({
          tipo: 'success',
          texto: `✅ Archivo ${archivo.name} cargado (${(archivo.size / 1024).toFixed(1)} KB)`
        })
      }
      reader.readAsText(archivo)
    } else if (extension === 'pdf') {
      // Procesar PDF en el backend
      const formData = new FormData()
      formData.append('file', archivo)

      try {
        const response = await fetch(`${API_URL}/api/extraer-texto-simple`, {
          method: 'POST',
          body: formData
        })

        const data = await response.json()
        if (data.texto) {
          setContenidoContexto(data.texto)
          setNombreArchivoContexto(archivo.name)
          setArchivoContexto(archivo)
          setMensaje({
            tipo: 'success',
            texto: `✅ PDF ${archivo.name} procesado (${data.caracteres} caracteres)`
          })
        }
      } catch (error) {
        setMensaje({
          tipo: 'error',
          texto: `❌ Error al procesar PDF: ${error.message}`
        })
      }
    } else {
      setMensaje({
        tipo: 'error',
        texto: '❌ Solo se permiten archivos PDF o TXT'
      })
    }
  }

  // Remover archivo de contexto
  const removerArchivoContexto = () => {
    setArchivoContexto(null)
    setContenidoContexto('')
    setNombreArchivoContexto('')
    setMensaje({
      tipo: 'success',
      texto: '✅ Archivo removido del contexto'
    })
  }

  // Cargar historial de chats
  const cargarHistorialChats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/chats/historial`)
      const data = await response.json()
      setHistorialChats(data.chats || [])
    } catch (error) {
      console.error('Error al cargar historial:', error)
    }
  }

  // ===== FUNCIONES PARA NAVEGACIÓN EN MODAL HISTORIAL =====
  
  // Cargar contenido del modal historial
  const cargarContenidoHistorialModal = async (ruta = '') => {
    setLoadingHistorialModal(true)
    try {
      const response = await fetch(`${API_URL}/api/chats/contenido?ruta=${encodeURIComponent(ruta)}`)
      const data = await response.json()
      setCarpetasHistorialModal(data.carpetas || [])
      setChatsHistorialModal(data.chats || [])
      setRutaHistorialModal(ruta)
    } catch (error) {
      console.error('Error al cargar contenido:', error)
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al cargar contenido`
      })
    } finally {
      setLoadingHistorialModal(false)
    }
  }

  // Crear carpeta en modal historial
  const crearCarpetaHistorialModal = async () => {
    const nombre = prompt('Nombre de la nueva carpeta:')
    if (!nombre) return

    try {
      const response = await fetch(`${API_URL}/api/chats/carpetas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          nombre,
          ruta_padre: rutaHistorialModal
        })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Carpeta "${nombre}" creada`
        })
        cargarContenidoHistorialModal(rutaHistorialModal)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    }
  }

  // Navegar a carpeta en modal
  const navegarCarpetaHistorialModal = (ruta) => {
    cargarContenidoHistorialModal(ruta)
  }

  // Navegar atrás en modal
  const navegarAtrasHistorialModal = () => {
    const partes = rutaHistorialModal.split(/[\\\/]/).filter(p => p)
    partes.pop()
    const nuevaRuta = partes.join('\\')
    cargarContenidoHistorialModal(nuevaRuta)
  }

  // Cargar chat desde modal
  const cargarChatDesdeModal = async (chatId) => {
    try {
      const response = await fetch(`${API_URL}/api/chats/${chatId}`)
      const data = await response.json()
      setMensajesChat(data.mensajes || [])
      setChatActualId(data.id)
      setNombreChatNuevo(data.nombre)
      setCarpetaChatActual(data.carpeta || '')
      setMostrarModalHistorial(false)
      setMensaje({
        tipo: 'success',
        texto: `✅ Chat "${data.nombre}" cargado`
      })
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al cargar chat`
      })
    }
  }

  // Eliminar chat desde modal
  const eliminarChatModal = async (chatId, nombreChat) => {
    if (!confirm(`¿Eliminar el chat "${nombreChat}"?`)) return

    try {
      const response = await fetch(`${API_URL}/api/chats/${chatId}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Chat eliminado`
        })
        cargarContenidoHistorialModal(rutaHistorialModal)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    }
  }

  // Eliminar carpeta desde modal
  const eliminarCarpetaModal = async (ruta, nombre) => {
    if (!confirm(`¿Eliminar la carpeta "${nombre}" y todo su contenido?`)) return

    try {
      const response = await fetch(`${API_URL}/api/chats/carpetas/${encodeURIComponent(ruta)}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Carpeta "${nombre}" eliminada`
        })
        cargarContenidoHistorialModal(rutaHistorialModal)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    }
  }

  // Renombrar carpeta desde modal
  const renombrarCarpetaModal = async (ruta, nombreActual) => {
    const nuevoNombre = prompt(`Renombrar carpeta "${nombreActual}":`, nombreActual)
    if (!nuevoNombre || nuevoNombre === nombreActual) return

    try {
      const response = await fetch(`${API_URL}/api/chats/carpetas/${encodeURIComponent(ruta)}/renombrar`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nuevo_nombre: nuevoNombre })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Carpeta renombrada a "${nuevoNombre}"`
        })
        cargarContenidoHistorialModal(rutaHistorialModal)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    }
  }

  // Renombrar chat desde modal
  const renombrarChatModal = async (chatId, nombreActual) => {
    const nuevoNombre = prompt(`Renombrar chat:`, nombreActual)
    if (!nuevoNombre || nuevoNombre === nombreActual) return

    try {
      const response = await fetch(`${API_URL}/api/chats/${chatId}/renombrar`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nuevo_nombre: nuevoNombre })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Chat renombrado a "${nuevoNombre}"`
        })
        cargarContenidoHistorialModal(rutaHistorialModal)
        
        // Si es el chat actual, actualizar el nombre
        if (chatActualId === chatId) {
          setNombreChatNuevo(nuevoNombre)
        }
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    }
  }

  // Cargar contenido cuando se abre el modal
  const abrirModalHistorial = () => {
    setMostrarModalHistorial(true)
    cargarContenidoHistorialModal('')
  }

  // Guardar chat actual
  const guardarChatActual = async () => {
    if (mensajesChat.length === 0) {
      setMensaje({
        tipo: 'error',
        texto: '❌ No hay mensajes para guardar'
      })
      return
    }

    const nombre = prompt('Nombre para este chat:', nombreChatNuevo || `Chat ${new Date().toLocaleDateString()}`)
    if (!nombre) return

    try {
      const response = await fetch(`${API_URL}/api/chats/guardar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: chatActualId,
          nombre: nombre,
          mensajes: mensajesChat
        })
      })

      const data = await response.json()
      if (data.success) {
        setChatActualId(data.id)
        setMensaje({
          tipo: 'success',
          texto: '✅ Chat guardado exitosamente'
        })
        cargarHistorialChats()
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al guardar: ${error.message}`
      })
    }
  }

  // Cargar un chat del historial
  const cargarChat = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/chats/${id}`)
      const data = await response.json()
      
      setMensajesChat(data.mensajes || [])
      setChatActualId(id)
      setNombreChatNuevo(data.nombre || '')
      setMostrarModalHistorial(false)
      setSelectedMenu('chat')
      
      setMensaje({
        tipo: 'success',
        texto: `✅ Chat "${data.nombre}" cargado`
      })
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al cargar chat: ${error.message}`
      })
    }
  }

  // Eliminar un chat del historial
  const eliminarChat = async (id, nombre) => {
    if (!confirm(`¿Eliminar el chat "${nombre}"?`)) return

    try {
      const response = await fetch(`${API_URL}/api/chats/${id}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Chat eliminado'
        })
        cargarHistorialChats()
        
        // Si era el chat actual, limpiar
        if (chatActualId === id) {
          setMensajesChat([])
          setChatActualId(null)
          setNombreChatNuevo('')
        }
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al eliminar: ${error.message}`
      })
    }
  }

  // Crear nuevo chat
  const nuevoChat = () => {
    if (mensajesChat.length > 0 && !confirm('¿Iniciar un nuevo chat? Los mensajes actuales no guardados se perderán.')) {
      return
    }
    setMensajesChat([])
    setChatActualId(null)
    setNombreChatNuevo('')
  }

  // ===== FUNCIONES PARA CARPETAS DE CHATS =====
  
  // Cargar carpetas de chats
  const cargarCarpetasChats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/chats/carpetas`)
      const data = await response.json()
      setCarpetasChats(data.carpetas || [])
    } catch (error) {
      console.error('Error al cargar carpetas:', error)
    }
  }

  // Crear nueva carpeta de chats
  const crearCarpetaChat = async () => {
    const nombre = prompt('Nombre de la carpeta/proyecto:')
    if (!nombre) return

    try {
      const response = await fetch(`${API_URL}/api/chats/carpetas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Carpeta "${nombre}" creada`
        })
        cargarCarpetasChats()
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    }
  }

  // Guardado automático silencioso
  const guardarAutomaticamente = async (mensajes) => {
    try {
      // Generar nombre automático si no existe
      const nombre = nombreChatNuevo || `Chat ${new Date().toLocaleDateString('es-ES')}`
      
      const response = await fetch(`${API_URL}/api/chats/guardar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: chatActualId,
          nombre: nombre,
          mensajes: mensajes,
          carpeta: carpetaChatActual
        })
      })

      const data = await response.json()
      if (data.success) {
        // Actualizar ID del chat si es nuevo
        if (!chatActualId) {
          setChatActualId(data.id)
          setNombreChatNuevo(nombre)
        }
      }
    } catch (error) {
      console.error('Error en guardado automático:', error)
    }
  }

  // Mover chat a carpeta específica
  const moverChatACarpeta = async (carpeta = '') => {
    if (mensajesChat.length === 0) {
      setMensaje({
        tipo: 'error',
        texto: '❌ No hay mensajes para mover'
      })
      return
    }

    const nombre = nombreChatNuevo || `Chat ${new Date().toLocaleDateString('es-ES')}`

    try {
      const response = await fetch(`${API_URL}/api/chats/guardar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: chatActualId,
          nombre: nombre,
          mensajes: mensajesChat,
          carpeta: carpeta
        })
      })

      const data = await response.json()
      if (data.success) {
        setChatActualId(data.id)
        setCarpetaChatActual(carpeta)
        setMensaje({
          tipo: 'success',
          texto: `✅ Chat movido${carpeta ? ` a "${carpeta}"` : ' a la raíz'}`
        })
        cargarHistorialChats()
        setMostrarModalCarpetas(false)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    }
  }

  // Effect para cargar historial cuando se abre el chat
  useEffect(() => {
    if (selectedMenu === 'chat') {
      cargarHistorialChats()
      cargarCarpetasChats()
    }
  }, [selectedMenu])

  // Eliminar documento
  const eliminarDocumento = async (ruta, nombre) => {
    if (!confirm(`¿Eliminar el documento "${nombre}"?`)) return

    try {
      const response = await fetch(`${API_URL}/api/documentos?ruta=${encodeURIComponent(ruta)}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Documento eliminado'
        })
        cargarCarpeta(rutaActual)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    }
  }

  const renombrarDocumento = async (ruta, nombreActual) => {
    // Extraer extensión de forma más robusta
    const lastDotIndex = nombreActual.lastIndexOf('.')
    
    // Tiene extensión si el punto no está al inicio y hay caracteres después
    let extension = ''
    let nombreSinExt = nombreActual
    
    if (lastDotIndex > 0 && lastDotIndex < nombreActual.length - 1) {
      extension = nombreActual.substring(lastDotIndex)
      nombreSinExt = nombreActual.substring(0, lastDotIndex)
    }
    
    console.log('DEBUG Renombrar:', { 
      nombreActual, 
      lastDotIndex,
      extension, 
      nombreSinExt 
    })
    
    const nuevoNombreSinExt = prompt(`Renombrar documento (sin extensión):`, nombreSinExt)
    
    if (!nuevoNombreSinExt || nuevoNombreSinExt.trim() === '') return
    if (nuevoNombreSinExt.trim() === nombreSinExt) return
    
    const nuevoNombreCompleto = nuevoNombreSinExt.trim() + extension
    
    console.log('DEBUG Enviando:', { 
      ruta_actual: ruta, 
      nuevo_nombre: nuevoNombreCompleto,
      extension_agregada: extension
    })

    try {
      const response = await fetch(`${API_URL}/api/documentos/renombrar`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          ruta_actual: ruta,
          nuevo_nombre: nuevoNombreCompleto
        })
      })

      const data = await response.json()
      console.log('DEBUG Respuesta:', data)
      
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: `✅ Documento renombrado a "${nuevoNombreCompleto}"`
        })
        cargarCarpeta(rutaActual)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ ${error.message}`
      })
    }
  }

  // Cargar configuración cuando se selecciona el menú
  useEffect(() => {
    if (selectedMenu === 'configuracion') {
      cargarConfiguracion()
    }
  }, [selectedMenu])

  // Subir PDF
  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setLoading(true)
    setMensaje(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('carpeta', rutaActual)

      const response = await fetch(`${API_URL}/api/extraer-pdf`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()
      
      if (data.success) {
        const ubicacion = data.carpeta === 'raíz' ? 'la raíz' : `"${data.carpeta}"`
        setMensaje({
          tipo: 'success',
          texto: `✅ Documento guardado en ${ubicacion}: ${data.palabras} palabras extraídas`
        })
        if (selectedMenu === 'cursos') {
          cargarCarpeta(rutaActual)
        }
      } else {
        setMensaje({
          tipo: 'error',
          texto: '❌ Error al procesar el documento'
        })
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error: ${error.message}`
      })
    } finally {
      setLoading(false)
      event.target.value = '' // Reset input
    }
  }

  // Navegar hacia atrás
  const navegarAtras = () => {
    const partes = rutaActual.split('\\').filter(p => p)
    partes.pop()
    const nuevaRuta = partes.join('\\')
    cargarCarpeta(nuevaRuta)
  }

  // Ver documento
  const verDocumento = async (ruta, nombre) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/documentos/contenido?ruta=${encodeURIComponent(ruta)}`)
      const data = await response.json()
      
      setDocumentoActual({
        nombre: nombre,
        ruta: ruta,
        contenido: data.contenido,
        tamaño_kb: data.tamaño_kb,
        lineas: data.lineas
      })
      setContenidoEditado(data.contenido)
      setModoEdicion(false)
      setVisorAbierto(true)
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al cargar documento: ${error.message}`
      })
    } finally {
      setLoading(false)
    }
  }

  // Activar modo edición
  const activarEdicion = () => {
    setModoEdicion(true)
  }

  // Cancelar edición de documento
  const cancelarEdicionDocumento = () => {
    setContenidoEditado(documentoActual.contenido)
    setModoEdicion(false)
  }

  // Guardar cambios del documento
  const guardarDocumento = async () => {
    try {
      const response = await fetch(`${API_URL}/api/documentos/contenido`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ruta: documentoActual.ruta,
          contenido: contenidoEditado
        })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Documento guardado exitosamente'
        })
        setDocumentoActual({
          ...documentoActual,
          contenido: contenidoEditado,
          tamaño_kb: data.tamaño_kb,
          lineas: data.lineas
        })
        setModoEdicion(false)
        cargarCarpeta(rutaActual)
      }
    } catch (error) {
      setMensaje({
        tipo: 'error',
        texto: `❌ Error al guardar: ${error.message}`
      })
    }
  }

  // Cerrar visor
  const cerrarVisor = () => {
    detenerLectura()
    setVisorAbierto(false)
    setDocumentoActual(null)
    setModoEdicion(false)
    setContenidoEditado('')
    setPosicionLectura({ inicio: 0, fin: 0 })
  }

  // Control de voz - Leer documento
  const leerDocumento = () => {
    if (!documentoActual) return
    
    // Verificar si el navegador soporta Web Speech API
    if (!('speechSynthesis' in window)) {
      setMensaje({
        tipo: 'error',
        texto: '❌ Tu navegador no soporta síntesis de voz'
      })
      return
    }

    // Si ya está leyendo y pausado, reanudar
    if (pausado) {
      window.speechSynthesis.resume()
      setPausado(false)
      setLeyendo(true)
      return
    }

    // Si ya está leyendo, no hacer nada
    if (leyendo) return

    // Crear nueva instancia de lectura
    const utterance = new SpeechSynthesisUtterance(documentoActual.contenido)
    
    // Configurar voz en español si está disponible
    const voices = window.speechSynthesis.getVoices()
    const spanishVoice = voices.find(voice => voice.lang.startsWith('es'))
    if (spanishVoice) {
      utterance.voice = spanishVoice
    }
    utterance.lang = 'es-ES'
    utterance.rate = 1.0 // Velocidad normal
    utterance.pitch = 1.0 // Tono normal
    utterance.volume = 1.0 // Volumen máximo

    // Eventos
    utterance.onstart = () => {
      setLeyendo(true)
      setPausado(false)
      setPosicionLectura({ inicio: 0, fin: 0 })
    }

    utterance.onboundary = (event) => {
      // Actualizar posición de lectura cuando cambia de palabra
      if (event.name === 'word') {
        setPosicionLectura({
          inicio: event.charIndex,
          fin: event.charIndex + (event.charLength || 0)
        })
      }
    }

    utterance.onend = () => {
      setLeyendo(false)
      setPausado(false)
      setPosicionLectura({ inicio: 0, fin: 0 })
    }

    utterance.onerror = (error) => {
      console.error('Error en síntesis de voz:', error)
      setLeyendo(false)
      setPausado(false)
      setPosicionLectura({ inicio: 0, fin: 0 })
      setMensaje({
        tipo: 'error',
        texto: '❌ Error al leer el documento'
      })
    }

    // Iniciar lectura
    window.speechSynthesis.speak(utterance)
  }

  // Pausar lectura
  const pausarLectura = () => {
    if (leyendo && !pausado) {
      window.speechSynthesis.pause()
      setPausado(true)
      setLeyendo(false)
    }
  }

  // Detener lectura
  const detenerLectura = () => {
    window.speechSynthesis.cancel()
    setLeyendo(false)
    setPausado(false)
    setPosicionLectura({ inicio: 0, fin: 0 })
  }

  // ============= FUNCIONES DE EXÁMENES =============
  
  // Verificar examen local al inicio (sin cargar del servidor)
  useEffect(() => {
    // Verificar si hay un examen guardado localmente
    const hayExamenLocal = cargarExamenLocal()
    if (hayExamenLocal) {
      console.log('✅ Examen local recuperado')
    }
  }, [])
  
  const cargarExamenesGuardados = async () => {
    try {
      const response = await fetch(`${API_URL}/api/examenes/listar`)
      const data = await response.json()
      if (data.success) {
        setExamenesGuardados({
          completados: data.completados || [],
          enProgreso: data.enProgreso || []
        })
      }
    } catch (error) {
      console.error('Error cargando exámenes:', error)
    }
  }
  
  // Generar examen desde carpeta
  const generarExamenDesdeCarpeta = async (carpeta) => {
    console.log('🎓 Preparando generación de examen desde carpeta:', carpeta.nombre)
    
    try {
      // Obtener archivos de la carpeta
      const response = await fetch(`${API_URL}/api/carpetas?ruta=${encodeURIComponent(carpeta.ruta)}`)
      const data = await response.json()
      
      console.log('📁 Datos recibidos:', data)
      
      if (!data.documentos || data.documentos.length === 0) {
        setMensaje({
          tipo: 'error',
          texto: '❌ La carpeta no contiene documentos para generar el examen'
        })
        return
      }
      
      console.log('📄 Archivos encontrados:', data.documentos.length)
      
      // Abrir modal de configuración (el prompt ya está cargado desde el useEffect inicial)
      setCarpetaConfigExamen(carpeta)
      setArchivosDisponibles(data.documentos)
      setArchivosSeleccionados(data.documentos.map(doc => doc.ruta))
      setPromptPersonalizado('')
      setRutaExploracion(carpeta.ruta)
      setCarpetasExploracion(data.carpetas || [])
      setModalConfigExamen(true)
      
      console.log('✅ Modal de configuración debería abrirse ahora')
      
    } catch (error) {
      console.error('Error preparando examen:', error)
      setMensaje({
        tipo: 'error',
        texto: '❌ Error al preparar la generación del examen'
      })
    }
  }

  const toggleSeleccionArchivo = (ruta) => {
    setArchivosSeleccionados(prev => {
      if (prev.includes(ruta)) {
        return prev.filter(r => r !== ruta)
      } else {
        return [...prev, ruta]
      }
    })
  }

  const cargarArchivosSubcarpeta = async (rutaSubcarpeta) => {
    try {
      const response = await fetch(`${API_URL}/api/carpetas?ruta=${encodeURIComponent(rutaSubcarpeta)}`)
      const data = await response.json()
      
      // Agregar nuevos archivos que no estén ya en la lista
      const nuevosArchivos = data.documentos.filter(
        doc => !archivosDisponibles.some(a => a.ruta === doc.ruta)
      )
      
      if (nuevosArchivos.length > 0) {
        setArchivosDisponibles(prev => [...prev, ...nuevosArchivos])
        setArchivosSeleccionados(prev => [...prev, ...nuevosArchivos.map(doc => doc.ruta)])
      }
      
      setRutaExploracion(rutaSubcarpeta)
      setCarpetasExploracion(data.carpetas || [])
      
    } catch (error) {
      console.error('Error cargando subcarpeta:', error)
    }
  }

  const volverCarpetaPadre = () => {
    const partes = rutaExploracion.split(/[/\\\\]/).filter(Boolean)
    partes.pop()
    const nuevaRuta = partes.join('/')
    cargarArchivosSubcarpeta(nuevaRuta || carpetaConfigExamen.ruta)
  }

  const confirmarGeneracionExamen = async () => {
    if (archivosSeleccionados.length === 0) {
      setMensaje({
        tipo: 'error',
        texto: '❌ Debes seleccionar al menos un archivo'
      })
      return
    }

    setModalConfigExamen(false)
    setGenerandoExamen(true)
    setProgresoGeneracion(0)
    setMensajeProgreso('Preparando generación...')
    
    // Crear nuevo AbortController para esta generación
    const controller = new AbortController()
    setAbortController(controller)
    setMensaje(null)
    
    // Generar ID de sesión único
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    setSessionIdGeneracion(sessionId)
    
    // Conectar al stream de progreso SSE
    const eventSource = new EventSource(`${API_URL}/api/progreso-examen/${sessionId}`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setProgresoGeneracion(data.progreso)
        setMensajeProgreso(data.mensaje)
        
        if (data.completado) {
          eventSource.close()
          if (data.error) {
            console.error('Error en generación:', data.error)
          }
        }
      } catch (error) {
        console.error('Error parseando evento SSE:', error)
      }
    }
    
    eventSource.onerror = (error) => {
      console.error('Error en EventSource:', error)
      eventSource.close()
    }
    
    try {
      // Leer contenido solo de los archivos seleccionados
      setProgresoGeneracion(5)
      setMensajeProgreso('Leyendo archivos seleccionados...')
      let contenidoCompleto = ''
      
      console.log('📚 Cargando archivos para el examen:')
      console.log(`   Total de archivos seleccionados: ${archivosSeleccionados.length}`)
      
      for (const rutaArchivo of archivosSeleccionados) {
        try {
          const archivo = archivosDisponibles.find(a => a.ruta === rutaArchivo)
          console.log(`   📄 Cargando: ${archivo?.nombre || rutaArchivo}`)
          
          const respDoc = await fetch(`${API_URL}/api/documentos/contenido?ruta=${encodeURIComponent(rutaArchivo)}`, {
            signal: controller.signal
          })
          const dataDoc = await respDoc.json()
          
          console.log(`      ✓ Cargado: ${dataDoc.contenido?.length || 0} caracteres`)
          contenidoCompleto += `\n\n=== ${archivo?.nombre || 'Documento'} ===\n${dataDoc.contenido}\n`
        } catch (error) {
          if (error.name === 'AbortError') {
            eventSource.close()
            throw error
          }
          console.error(`      ✗ Error leyendo archivo:`, error)
        }
      }
      
      console.log(`✅ Total de contenido cargado: ${contenidoCompleto.length} caracteres`)
      
      if (!contenidoCompleto.trim()) {
        eventSource.close()
        setMensaje({
          tipo: 'error',
          texto: '❌ No se pudo leer el contenido de los documentos'
        })
        setGenerandoExamen(false)
        return
      }
      
      // Logging de configuración
      console.log('⚙️ Configuración de generación:')
      console.log(`   Prompt personalizado: ${promptPersonalizado ? 'SÍ (' + promptPersonalizado.length + ' caracteres)' : 'NO'}`)
      console.log(`   Prompt sistema: ${promptSistema ? 'SÍ (' + promptSistema.length + ' caracteres)' : 'NO'}`)
      console.log(`   Preguntas: ${configExamen.num_multiple} múltiple, ${configExamen.num_corta} corta, ${configExamen.num_desarrollo} desarrollo`)
      
      // Generar examen con la IA
      const respExamen = await fetch(`${API_URL}/api/generar-examen`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contenido: contenidoCompleto,
          prompt_personalizado: promptPersonalizado,
          prompt_sistema: promptSistema || null,  // Enviar el prompt del sistema si existe
          num_multiple: configExamen.num_multiple,
          num_corta: configExamen.num_corta,
          num_desarrollo: configExamen.num_desarrollo,
          session_id: sessionId
        }),
        signal: controller.signal
      })
      
      const dataExamen = await respExamen.json()
      
      if (dataExamen.success) {
        setPreguntasExamen(dataExamen.preguntas)
        setExamenActivo(true)
        setCarpetaExamen(carpetaConfigExamen)
        setRespuestasUsuario({})
        setResultadoExamen(null)
        setModalExamenAbierto(true)
        setMensaje({
          tipo: 'success',
          texto: `✅ Examen generado: ${dataExamen.total_preguntas} preguntas (${dataExamen.puntos_totales} puntos)`
        })
      } else {
        throw new Error(dataExamen.message || 'Error al generar examen')
      }
    } catch (error) {
      eventSource.close()
      if (error.name === 'AbortError') {
        console.log('⏹️ Generación de examen cancelada')
        setMensaje({
          tipo: 'info',
          texto: '⏹️ Generación de examen cancelada'
        })
      } else {
        console.error('Error generando examen:', error)
        setMensaje({
          tipo: 'error',
          texto: '❌ Error al generar el examen: ' + error.message
        })
      }
    } finally {
      setGenerandoExamen(false)
      setAbortController(null)
      setProgresoGeneracion(0)
      setMensajeProgreso('')
      setSessionIdGeneracion(null)
    }
  }

  const cancelarGeneracionExamen = () => {
    if (abortController) {
      abortController.abort()
      console.log('🛑 Cancelando generación de examen...')
    }
  }

  const guardarPromptSistema = async () => {
    try {
      const response = await fetch(`${API_URL}/api/prompt-personalizado`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptSistema })
      })
      
      const data = await response.json()
      
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Prompt guardado exitosamente'
        })
      }
    } catch (error) {
      console.error('Error guardando prompt:', error)
      setMensaje({
        tipo: 'error',
        texto: '❌ Error al guardar el prompt'
      })
    }
  }

  const cargarPromptPredeterminado = async () => {
    // Cargar directamente el template por defecto sin depender del servidor
    const templateDefault = `Eres un profesor universitario experto. Tu trabajo es crear preguntas de examen QUE EVALÚEN DIRECTAMENTE EL CONTENIDO del material proporcionado.

⚠️ CRÍTICO: Todas las preguntas DEBEN estar basadas en información ESPECÍFICA del documento. NO inventes conceptos que no aparecen en el texto.

CONTENIDO DEL MATERIAL DE ESTUDIO:
{contenido}

OBJETIVO: Crear preguntas que evalúen si el estudiante LEYÓ Y COMPRENDIÓ el material proporcionado.

⚠️ REGLAS ABSOLUTAS:
1. Cada pregunta debe referirse a INFORMACIÓN ESPECÍFICA que aparece en el documento
2. Menciona conceptos, nombres, términos o ideas QUE ESTÁN EN EL TEXTO
3. NO inventes preguntas sobre temas generales
4. Las respuestas correctas deben estar JUSTIFICADAS por el contenido del documento

INSTRUCCIONES ESTRICTAS:
Genera EXACTAMENTE {total_preguntas} preguntas siguiendo esta distribución:
- {num_multiple} preguntas de opción múltiple
- {num_corta} preguntas de respuesta corta
- {num_desarrollo} preguntas de desarrollo

CRITERIOS DE CALIDAD OBLIGATORIOS:

1. PREGUNTAS DE OPCIÓN MÚLTIPLE (tipo: "multiple"):
   - Deben evaluar COMPRENSIÓN, no solo memoria
   - Incluir casos prácticos o escenarios reales
   - Opciones incorrectas deben ser plausibles pero claramente erróneas
   - Evitar preguntas triviales tipo "¿Qué es...?"
   - Formato de respuesta: Solo la letra (A, B, C o D)
   - Valor: 3 puntos cada una

2. PREGUNTAS DE RESPUESTA CORTA (tipo: "corta"):
   - Pedir EXPLICACIONES de conceptos clave
   - Solicitar COMPARACIONES entre ideas
   - Preguntar CÓMO aplicar el conocimiento
   - Requieren 2-4 oraciones de respuesta
   - La respuesta_correcta debe ser una guía detallada de lo que se espera
   - Valor: 4 puntos cada una

3. PREGUNTAS DE DESARROLLO (tipo: "desarrollo"):
   - Requieren ANÁLISIS PROFUNDO y ARGUMENTACIÓN
   - Deben conectar múltiples conceptos del material
   - Pedir ejemplos, aplicaciones o críticas fundamentadas
   - La respuesta_correcta debe listar criterios de evaluación específicos
   - Valor: 6 puntos cada una

FORMATO DE RESPUESTA (JSON ESTRICTO - sin comentarios):
{
  "preguntas": [
    {
      "tipo": "multiple",
      "pregunta": "[Pregunta práctica sobre aplicación del concepto]",
      "opciones": ["A) [Opción plausible pero incorrecta]", "B) [Respuesta correcta bien justificada]", "C) [Error conceptual común]", "D) [Otro error plausible]"],
      "respuesta_correcta": "B",
      "puntos": 3
    },
    {
      "tipo": "corta",
      "pregunta": "[Pregunta que requiere explicación clara]",
      "respuesta_correcta": "Debe explicar: [punto 1], mencionar [punto 2], y ejemplificar con [punto 3]",
      "puntos": 4
    },
    {
      "tipo": "desarrollo",
      "pregunta": "[Pregunta que requiere análisis profundo]",
      "respuesta_correcta": "Criterios: 1) Identifica los conceptos clave [específicos], 2) Analiza la relación entre ellos, 3) Proporciona ejemplos concretos, 4) Argumenta conclusiones lógicas",
      "puntos": 6
    }
  ]
}

IMPORTANTE: 
- Responde SOLO con el JSON válido
- NO agregues texto antes o después del JSON
- Asegúrate que las preguntas cubran TODO el contenido importante
- Las preguntas deben ser DESAFIANTES pero JUSTAS
- Enfócate en comprensión y aplicación, NO en memorización

JSON:`
    
    setPromptSistema(templateDefault)
    setMensaje({
      tipo: 'success',
      texto: '✅ Prompt predeterminado cargado'
    })
  }
  
  // Actualizar respuesta del usuario
  const actualizarRespuesta = (indice, respuesta) => {
    const nuevasRespuestas = {
      ...respuestasUsuario,
      [indice]: respuesta
    }
    setRespuestasUsuario(nuevasRespuestas)
    
    // Guardar automáticamente en archivo local (mediante servidor)
    if (examenActivo && preguntasExamen.length > 0) {
      guardarExamenLocal(nuevasRespuestas)
    }
  }
  
  // Guardar examen en archivo local (a través del servidor)
  const guardarExamenLocal = async (respuestas = respuestasUsuario) => {
    try {
      await fetch(`${API_URL}/api/examenes/guardar-temporal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          preguntas: preguntasExamen,
          respuestas: respuestas,
          carpeta: carpetaExamen
        })
      })
      // No mostrar mensaje para no molestar al usuario
    } catch (error) {
      // Ignorar errores silenciosamente (servidor podría estar apagado)
      console.log('Guardado automático sin servidor - OK')
    }
  }
  
  // Cargar examen desde archivo local
  const cargarExamenLocal = async () => {
    try {
      const response = await fetch(`${API_URL}/api/examenes/cargar-temporal`)
      const data = await response.json()
      
      if (data.success && data.examen) {
        const examen = data.examen
        setPreguntasExamen(examen.preguntas)
        setRespuestasUsuario(examen.respuestas || {})
        setCarpetaExamen(examen.carpeta)
        setExamenActivo(true)
        setModalExamenAbierto(true)
        setMensaje({
          tipo: 'success',
          texto: '📋 Examen recuperado desde última sesión'
        })
        return true
      }
    } catch (error) {
      console.log('No hay examen temporal para cargar')
    }
    return false
  }
  
  // Limpiar examen local
  const limpiarExamenLocal = async () => {
    try {
      await fetch(`${API_URL}/api/examenes/limpiar-temporal`, {
        method: 'DELETE'
      })
    } catch (error) {
      console.log('No se pudo limpiar examen temporal')
    }
  }
  
  // Inicializar reconocimiento de voz
  const iniciarReconocimientoVoz = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setMensaje({
        tipo: 'error',
        texto: '❌ Tu navegador no soporta reconocimiento de voz. Prueba con Chrome o Edge.'
      })
      return null
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    
    recognition.lang = 'es-ES'
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 1
    
    return recognition
  }
  
  // Alternar escucha de voz para una pregunta
  const alternarEscuchaVoz = (indicePregunta) => {
    // Si ya está escuchando esta pregunta, detener
    if (escuchandoPregunta === indicePregunta) {
      if (reconocimientoVoz) {
        reconocimientoVoz.stop()
      }
      setEscuchandoPregunta(null)
      setTranscripcionTemp('')
      return
    }
    
    // Si hay otro reconocimiento activo, detenerlo
    if (reconocimientoVoz) {
      reconocimientoVoz.stop()
    }
    
    // Crear nuevo reconocimiento
    const nuevoReconocimiento = iniciarReconocimientoVoz()
    if (!nuevoReconocimiento) return
    
    // Eventos del reconocimiento
    nuevoReconocimiento.onstart = () => {
      setEscuchandoPregunta(indicePregunta)
      setTranscripcionTemp('')
    }
    
    nuevoReconocimiento.onresult = (event) => {
      let transcripcionInterina = ''
      let transcripcionFinal = ''
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          transcripcionFinal += transcript + ' '
        } else {
          transcripcionInterina += transcript
        }
      }
      
      // Actualizar transcripción temporal
      if (transcripcionInterina) {
        setTranscripcionTemp(transcripcionInterina)
      }
      
      // Si hay transcripción final, agregar a la respuesta
      if (transcripcionFinal) {
        const respuestaActual = respuestasUsuario[indicePregunta] || ''
        const nuevaRespuesta = respuestaActual + transcripcionFinal
        actualizarRespuesta(indicePregunta, nuevaRespuesta)
        setTranscripcionTemp('')
      }
    }
    
    nuevoReconocimiento.onerror = (event) => {
      console.error('Error en reconocimiento de voz:', event.error)
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        setMensaje({
          tipo: 'error',
          texto: '❌ Error en el reconocimiento de voz: ' + event.error
        })
      }
      setEscuchandoPregunta(null)
      setTranscripcionTemp('')
    }
    
    nuevoReconocimiento.onend = () => {
      // Si se detuvo inesperadamente y seguimos queriendo escuchar, reiniciar
      if (escuchandoPregunta === indicePregunta) {
        try {
          nuevoReconocimiento.start()
        } catch (e) {
          setEscuchandoPregunta(null)
          setTranscripcionTemp('')
        }
      }
    }
    
    setReconocimientoVoz(nuevoReconocimiento)
    nuevoReconocimiento.start()
  }
  
  // Limpiar reconocimiento al cerrar examen
  const detenerReconocimientoVoz = () => {
    if (reconocimientoVoz) {
      reconocimientoVoz.stop()
      setReconocimientoVoz(null)
    }
    setEscuchandoPregunta(null)
    setTranscripcionTemp('')
  }
  
  // Enviar examen para calificar
  const enviarExamen = async () => {
    if (Object.keys(respuestasUsuario).length === 0) {
      setMensaje({
        tipo: 'error',
        texto: '❌ Debes responder al menos una pregunta'
      })
      return
    }
    
    setGenerandoExamen(true)
    
    try {
      const response = await fetch(`${API_URL}/api/evaluar-examen`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          preguntas: preguntasExamen,
          respuestas: respuestasUsuario,
          carpeta_path: carpetaExamen?.ruta || ''
        })
      })
      
      const data = await response.json()
      
      if (data.success || data.resultados) {
        limpiarExamenLocal() // Limpiar guardado local
        setResultadoExamen(data)
        setMensaje({
          tipo: 'success',
          texto: `✅ Examen calificado: ${data.puntos_obtenidos}/${data.puntos_totales} puntos (${data.porcentaje.toFixed(1)}%)`
        })
        // Recargar lista de exámenes guardados
        cargarExamenesGuardados()
        // Recargar carpetas de exámenes para actualizar contadores
        cargarCarpetasExamenes(rutaActualExamenes)
      } else {
        throw new Error(data.message || 'Error al evaluar')
      }
    } catch (error) {
      console.error('Error evaluando examen:', error)
      setMensaje({
        tipo: 'error',
        texto: '❌ Error al calificar el examen: ' + error.message
      })
    } finally {
      setGenerandoExamen(false)
    }
  }
  
  // Pausar examen (guardar progreso)
  const pausarExamen = async () => {
    if (!carpetaExamen || preguntasExamen.length === 0) return
    
    try {
      const response = await fetch(`${API_URL}/api/examenes/pausar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          carpeta_ruta: carpetaExamen.ruta,
          carpeta_nombre: carpetaExamen.nombre,
          preguntas: preguntasExamen,
          respuestas: respuestasUsuario,
          fecha_inicio: new Date().toISOString()
        })
      })
      
      const data = await response.json()
      if (data.success) {
        limpiarExamenLocal() // Limpiar guardado local
        setMensaje({
          tipo: 'success',
          texto: '⏸️ Examen pausado correctamente. Ve a la pestaña "Generar Exámenes" para continuarlo'
        })
        cerrarExamen()
        cargarExamenesGuardados()
        // Cambiar automáticamente a la pestaña de generar exámenes
        setTimeout(() => {
          setSelectedMenu('generar')
        }, 2000)
      }
    } catch (error) {
      console.error('Error pausando examen:', error)
      setMensaje({
        tipo: 'error',
        texto: '❌ Error al pausar el examen'
      })
    }
  }
  
  // Continuar examen pausado
  const continuarExamen = (examen) => {
    limpiarExamenLocal() // Limpiar cualquier examen local anterior
    setPreguntasExamen(examen.preguntas)
    setRespuestasUsuario(examen.respuestas || {})
    setCarpetaExamen({
      ruta: examen.carpeta_ruta,
      nombre: examen.carpeta_nombre
    })
    setExamenActivo(true)
    setResultadoExamen(null)
    setModalExamenAbierto(true)
    setModalListaExamenes(false)
    // Guardar en localStorage para continuar trabajando sin servidor
    guardarExamenLocal(examen.respuestas || {})
  }
  
  // Ver resultado de examen completado
  const verResultadoExamen = (examen) => {
    setViendoExamen(examen)
    setModalListaExamenes(false)
  }
  
  // Reintentar examen completado
  const reintentarExamen = (examen) => {
    // Cargar las preguntas del examen
    setPreguntasExamen(examen.resultados.map((r, idx) => ({
      pregunta: r.pregunta,
      tipo: r.tipo,
      opciones: r.opciones || [],
      respuesta_correcta: r.respuesta_correcta,
      puntos: r.puntos_maximos
    })))
    
    // Configurar la carpeta
    setCarpetaExamen({
      ruta: examen.carpeta_ruta,
      nombre: examen.carpeta_nombre
    })
    
    // Limpiar respuestas y abrir modal
    setRespuestasUsuario({})
    setResultadoExamen(null)
    setExamenActivo(true)
    setModalExamenAbierto(true)
    setViendoExamen(null)
    
    setMensaje({
      tipo: 'info',
      texto: '🔄 Reintentando examen. ¡Buena suerte!'
    })
  }
  
  // Cerrar examen
  const cerrarExamen = () => {
    detenerReconocimientoVoz() // Detener reconocimiento de voz
    setModalExamenAbierto(false)
    setExamenActivo(null)
    setPreguntasExamen([])
    setRespuestasUsuario({})
    setResultadoExamen(null)
    setCarpetaExamen(null)
  }
  
  // Reiniciar examen
  const reiniciarExamen = () => {
    detenerReconocimientoVoz() // Detener reconocimiento de voz
    setRespuestasUsuario({})
    setResultadoExamen(null)
  }

  return (
    <div className="app-container">
      {/* Botón menú móvil */}
      <button 
        className="mobile-menu-btn"
        onClick={() => setMenuMovilAbierto(!menuMovilAbierto)}
        aria-label="Menú"
      >
        <span className="icon">{menuMovilAbierto ? '✕' : '☰'}</span>
      </button>

      {/* Overlay para cerrar menú */}
      <div 
        className={`sidebar-overlay ${menuMovilAbierto ? 'show' : ''}`}
        onClick={() => setMenuMovilAbierto(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${menuMovilAbierto ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>📝 Examinator</h2>
        </div>
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${selectedMenu === 'inicio' ? 'active' : ''}`}
            onClick={() => { 
              setSelectedMenu('inicio'); 
              setMenuMovilAbierto(false); 
            }}
          >
            <span className="icon">🏠</span>
            <span>Inicio</span>
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'cursos' ? 'active' : ''}`}
            onClick={() => { 
              setSelectedMenu('cursos'); 
              cargarCarpeta(''); 
              setMenuMovilAbierto(false); 
            }}
          >
            <span className="icon">📚</span>
            <span>Mis Cursos</span>
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'generar' ? 'active' : ''}`}
            onClick={() => { 
              setSelectedMenu('generar'); 
              setMenuMovilAbierto(false); 
            }}
          >
            <span className="icon">✨</span>
            <span>Examenes</span>
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'historial' ? 'active' : ''}`}
            onClick={() => { 
              setSelectedMenu('historial'); 
              setMenuMovilAbierto(false); 
            }}
          >
            <span className="icon">📋</span>
            <span>Historial</span>
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'chat' ? 'active' : ''}`}
            onClick={() => { 
              setSelectedMenu('chat'); 
              setMenuMovilAbierto(false); 
            }}
          >
            <span className="icon">💬</span>
            <span>Chat con IA</span>
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'configuracion' ? 'active' : ''}`}
            onClick={() => { 
              setSelectedMenu('configuracion'); 
              setMenuMovilAbierto(false); 
            }}
          >
            <span className="icon">⚙️</span>
            <span>Configuración</span>
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Banner de debug para verificar la URL del API */}
        {window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1' && (
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            fontSize: '0.85rem',
            fontFamily: 'monospace'
          }}>
            🌐 Accediendo desde: <strong>{window.location.hostname}:{window.location.port}</strong><br/>
            🔌 API Backend: <strong>{API_URL}</strong>
          </div>
        )}
        
        {mensaje && (
          <div className={`mensaje ${mensaje.tipo}`}>
            {mensaje.texto}
            <button onClick={() => setMensaje(null)}>✕</button>
          </div>
        )}

        {selectedMenu === 'inicio' && (
          <div className="welcome-section">
            <h1>Bienvenido a Examinator</h1>
            <p className="subtitle">Genera exámenes personalizados con inteligencia artificial</p>
            
            <div className="feature-cards">
              <div className="feature-card upload-card">
                <div className="feature-icon">📄</div>
                <h3>Carga documentos</h3>
                <p>Sube archivos PDF con el contenido de estudio</p>
                
                <div className="upload-section">
                  <label className="btn-upload">
                    {loading ? '⏳ Procesando...' : '📤 Subir PDF'}
                    <input 
                      type="file" 
                      accept=".pdf" 
                      onChange={handleFileUpload}
                      disabled={loading}
                      style={{display: 'none'}}
                    />
                  </label>
                  
                  <p style={{color: '#a0a0b0', fontSize: '0.9rem', marginTop: '0.5rem'}}>
                    Los PDFs se guardarán en la carpeta raíz. Organízalos desde "Mis Cursos"
                  </p>
                </div>
              </div>

              <div className="feature-card">
                <div className="feature-icon">🤖</div>
                <h3>IA Avanzada</h3>
                <p>Utiliza modelos de lenguaje para generar preguntas inteligentes</p>
              </div>
              
              <div className="feature-card">
                <div className="feature-icon">✅</div>
                <h3>Personalizable</h3>
                <p>Ajusta el tipo y cantidad de preguntas según tus necesidades</p>
              </div>
            </div>

            <div className="quick-actions">
              <button 
                className="btn-primary"
                onClick={() => { setSelectedMenu('cursos'); cargarCarpeta(''); }}
              >
                Organizar Carpetas
              </button>
              <button 
                className="btn-secondary"
                onClick={() => setSelectedMenu('generar')}
              >
                Generar Examen
              </button>
            </div>
          </div>
        )}

        {selectedMenu === 'cursos' && (
          <div className="content-section">
            <div className="carpetas-header">
              <h1>📁 {rutaActual ? rutaActual.split('\\').pop() || 'Mis Cursos' : 'Mis Cursos'} 🎓</h1>
              <div className="carpetas-actions">
                <button onClick={crearCarpeta} className="btn-primary">
                  ➕ Nueva Carpeta
                </button>
                <label className="btn-secondary">
                  {loading ? '⏳' : `📤 Subir PDF ${rutaActual ? 'aquí' : ''}`}
                  <input 
                    type="file" 
                    accept=".pdf" 
                    onChange={handleFileUpload}
                    disabled={loading}
                    style={{display: 'none'}}
                  />
                </label>
              </div>
            </div>

            {rutaActual && (
              <div className="ruta-info">
                📍 Ubicación actual: <strong>{rutaActual || 'Raíz'}</strong>
                <br />
                <small style={{color: '#a0a0b0'}}>Los PDFs se guardarán en esta carpeta</small>
              </div>
            )}

            {/* Breadcrumb */}
            <div className="breadcrumb">
              {rutaActual && (
                <button 
                  onClick={() => {
                    const partes = rutaActual.split('\\').filter(p => p);
                    const rutaPadre = partes.slice(0, -1).join('\\');
                    cargarCarpeta(rutaPadre);
                  }}
                  className="btn-atras"
                  title="Volver a carpeta anterior"
                >
                  ← Atrás
                </button>
              )}
              <button onClick={() => cargarCarpeta('')} className="breadcrumb-item">
                🏠 Inicio
              </button>
              {rutaActual && rutaActual.split('\\').filter(p => p).map((parte, idx, arr) => {
                const rutaParcial = arr.slice(0, idx + 1).join('\\')
                return (
                  <span key={idx}>
                    <span className="breadcrumb-separator">/</span>
                    <button 
                      onClick={() => cargarCarpeta(rutaParcial)}
                      className="breadcrumb-item"
                    >
                      {parte}
                    </button>
                  </span>
                )
              })}
            </div>

            {loading ? (
              <p className="loading">Cargando...</p>
            ) : generandoExamen ? (
              <div className="loading-examen">
                <div className="spinner"></div>
                <p>⏳ Generando examen con IA...</p>
                
                {/* Barra de progreso */}
                <div className="progreso-container">
                  <div className="progreso-barra">
                    <div 
                      className="progreso-fill" 
                      style={{width: `${progresoGeneracion}%`}}
                    >
                      <span className="progreso-texto">{progresoGeneracion}%</span>
                    </div>
                  </div>
                  <p className="progreso-mensaje">{mensajeProgreso}</p>
                </div>
                
                <p className="hint">Esto puede tomar varios minutos dependiendo del modelo</p>
                <button 
                  onClick={cancelarGeneracionExamen}
                  className="btn-cancelar-generacion"
                >
                  ⏹️ Cancelar Generación
                </button>
              </div>
            ) : (
              <>
                {/* Carpetas */}
                {carpetas.length > 0 && (
                  <div className="items-section">
                    <h3>📂 Carpetas (Generar Examen disponible)</h3>
                    <div className="items-grid">
                      {carpetas.map(carpeta => (
                        <div 
                          key={carpeta.ruta} 
                          className="item-card carpeta-item"
                          onClick={() => cargarCarpeta(carpeta.ruta)}
                          style={{cursor: 'pointer'}}
                        >
                          <div className="item-icon">📁</div>
                          <div className="item-info">
                            <h4>{carpeta.nombre}</h4>
                            <p>
                              {carpeta.num_documentos} docs · {carpeta.num_subcarpetas} carpetas
                            </p>
                          </div>
                          <div className="item-actions">
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                setMenuAbierto(menuAbierto === carpeta.ruta ? null : carpeta.ruta);
                              }}
                              className="btn-menu"
                            >
                              ⋮
                            </button>
                            {menuAbierto === carpeta.ruta && (
                              <div className="dropdown-menu">
                                <button onClick={(e) => {
                                  e.stopPropagation();
                                  setMenuAbierto(null);
                                  generarExamenDesdeCarpeta(carpeta);
                                }}>
                                  📝 Generar Examen
                                </button>
                                <button onClick={(e) => {
                                  e.stopPropagation();
                                  setMenuAbierto(null);
                                  renombrarCarpeta(carpeta.ruta, carpeta.nombre);
                                }}>
                                  ✏️ Renombrar
                                </button>
                                <button onClick={(e) => {
                                  e.stopPropagation();
                                  setMenuAbierto(null);
                                  iniciarMoverCarpeta(carpeta);
                                }}>
                                  📦 Mover
                                </button>
                                <button onClick={(e) => {
                                  e.stopPropagation();
                                  setMenuAbierto(null);
                                  eliminarCarpeta(carpeta.ruta, carpeta.nombre);
                                }} className="btn-menu-eliminar">
                                  🗑️ Eliminar
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Documentos */}
                {documentos.length > 0 && (
                  <div className="items-section">
                    <h3>📄 Documentos</h3>
                    <div className="items-grid">
                      {documentos.map(doc => (
                        <div key={doc.ruta} className="item-card documento-item">
                          <div className="item-icon">📄</div>
                          <div className="item-info">
                            <h4>{doc.nombre}</h4>
                            <p>{doc.tamaño_kb} KB</p>
                          </div>
                          <div className="item-actions">
                            <button 
                              onClick={() => verDocumento(doc.ruta, doc.nombre)}
                              className="btn-ver"
                            >
                              👁️ Ver
                            </button>
                            <button 
                              onClick={() => renombrarDocumento(doc.ruta, doc.nombre)}
                              className="btn-renombrar"
                              title="Renombrar documento"
                            >
                              ✏️
                            </button>
                            <button 
                              onClick={() => eliminarDocumento(doc.ruta, doc.nombre)}
                              className="btn-eliminar"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {carpetas.length === 0 && documentos.length === 0 && (
                  <div className="empty-state">
                    <p>📭 Esta carpeta está vacía</p>
                    <p className="empty-hint">Crea una carpeta o sube un PDF para comenzar</p>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Visor de documentos */}
        {visorAbierto && documentoActual && (
          <div className="modal-overlay" onClick={cerrarVisor}>
            <div className="modal-content modal-content-editor" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>📄 {documentoActual.nombre}</h2>
                <div className="modal-info">
                  <span>{documentoActual.tamaño_kb} KB</span>
                  <span>•</span>
                  <span>{documentoActual.lineas} líneas</span>
                </div>
                <div className="modal-actions">
                  {!modoEdicion ? (
                    <>
                      <button onClick={activarEdicion} className="btn-editar" title="Editar documento">
                        ✏️ Editar
                      </button>
                      {!leyendo && !pausado && (
                        <button onClick={leerDocumento} className="btn-leer" title="Leer documento con voz">
                          🔊 Leer
                        </button>
                      )}
                      {leyendo && (
                        <button onClick={pausarLectura} className="btn-pausar" title="Pausar lectura">
                          ⏸️ Pausar
                        </button>
                      )}
                      {pausado && (
                        <button onClick={leerDocumento} className="btn-reanudar" title="Reanudar lectura">
                          ▶️ Reanudar
                        </button>
                      )}
                      {(leyendo || pausado) && (
                        <button onClick={detenerLectura} className="btn-detener" title="Detener lectura">
                          ⏹️ Detener
                        </button>
                      )}
                    </>
                  ) : (
                    <>
                      <button onClick={guardarDocumento} className="btn-guardar" title="Guardar cambios">
                        💾 Guardar
                      </button>
                      <button onClick={cancelarEdicionDocumento} className="btn-cancelar" title="Cancelar edición">
                        ❌ Cancelar
                      </button>
                    </>
                  )}
                  <button onClick={cerrarVisor} className="btn-close">✕</button>
                </div>
              </div>
              <div className="modal-body">
                {!modoEdicion ? (
                  <pre className="documento-contenido">
                    {posicionLectura.inicio > 0 ? (
                      <>
                        {documentoActual.contenido.substring(0, posicionLectura.inicio)}
                        <span className="texto-leyendo">
                          {documentoActual.contenido.substring(posicionLectura.inicio, posicionLectura.fin)}
                        </span>
                        {documentoActual.contenido.substring(posicionLectura.fin)}
                      </>
                    ) : (
                      documentoActual.contenido
                    )}
                  </pre>
                ) : (
                  <textarea 
                    className="documento-editor"
                    value={contenidoEditado}
                    onChange={(e) => setContenidoEditado(e.target.value)}
                    autoFocus
                  />
                )}
              </div>
            </div>
          </div>
        )}

        {selectedMenu === 'generar' && (
          <div className="content-section">
            <h1>📝 Mis Exámenes</h1>
            
            {/* Navegación de ruta */}
            <div className="ruta-navegacion">
              <button 
                className="btn-ruta"
                onClick={() => cargarCarpetasExamenes('')}
              >
                🏠 Exámenes
              </button>
              {rutaActualExamenes && rutaActualExamenes.split(/[/\\]/).map((parte, idx, arr) => {
                const rutaParcial = arr.slice(0, idx + 1).join('/')
                return (
                  <span key={idx}>
                    <span className="separador-ruta"> › </span>
                    <button 
                      className="btn-ruta"
                      onClick={() => cargarCarpetasExamenes(rutaParcial)}
                    >
                      {parte}
                    </button>
                  </span>
                )
              })}
            </div>

            {loading ? (
              <div className="loading">Cargando exámenes...</div>
            ) : (
              <>
                {/* Exámenes en Progreso GLOBALES (solo en raíz) */}
                {!rutaActualExamenes && examenesProgresoGlobal.length > 0 && (
                  <div className="examenes-section">
                    <h2>⏳ Exámenes Pendientes ({examenesProgresoGlobal.length})</h2>
                    <p className="section-hint">Todos tus exámenes sin completar de todas las carpetas</p>
                    <div className="examenes-grid">
                      {examenesProgresoGlobal.map((examen, idx) => (
                        <div key={idx} className="examen-card en-progreso">
                          <div className="examen-card-header">
                            <h3>📝 {examen.carpeta_nombre}</h3>
                            <div className="header-badges">
                              <span className="badge badge-warning">En Progreso</span>
                              <button 
                                className="btn-menu-dots"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setMenuAbierto(menuAbierto === `examen-progreso-global-${idx}` ? null : `examen-progreso-global-${idx}`);
                                }}
                              >
                                ⋮
                              </button>
                              {menuAbierto === `examen-progreso-global-${idx}` && (
                                <div className="menu-dropdown">
                                  <button onClick={(e) => {
                                    e.stopPropagation();
                                    setMenuAbierto(null);
                                    eliminarExamen(examen, 'progreso');
                                  }} className="btn-menu-eliminar">
                                    🗑️ Eliminar
                                  </button>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="examen-card-body">
                            <p className="examen-fecha">
                              Iniciado: {new Date(examen.fecha_inicio).toLocaleString('es-ES')}
                            </p>
                            <p className="examen-info">
                              {examen.preguntas.length} preguntas • {Object.keys(examen.respuestas || {}).length} respondidas
                            </p>
                            <div className="examen-progreso">
                              <div className="progreso-bar">
                                <div 
                                  className="progreso-fill"
                                  style={{
                                    width: `${(Object.keys(examen.respuestas || {}).length / examen.preguntas.length) * 100}%`
                                  }}
                                ></div>
                              </div>
                              <span className="progreso-texto">
                                {Math.round((Object.keys(examen.respuestas || {}).length / examen.preguntas.length) * 100)}% completado
                              </span>
                            </div>
                          </div>
                          <div className="examen-card-actions">
                            <button 
                              className="btn-continuar"
                              onClick={() => continuarExamen(examen)}
                            >
                              ▶️ Continuar
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Carpetas */}
                {carpetasExamenes.length > 0 && (
                  <div className="carpetas-section">
                    <h2>📁 Carpetas</h2>
                    <div className="carpetas-grid">
                      {carpetasExamenes.map((carpeta, idx) => (
                        <div 
                          key={idx}
                          className="carpeta-card"
                        >
                          <div 
                            className="carpeta-card-clickable"
                            onClick={() => cargarCarpetasExamenes(carpeta.ruta)}
                          >
                            <div className="carpeta-card-icon">📁</div>
                            <div className="carpeta-card-content">
                              <h4>{carpeta.nombre}</h4>
                              {carpeta.total_examenes > 0 ? (
                                <p className="carpeta-stats">
                                  {carpeta.num_completados > 0 && (
                                    <span className="stat-badge completado">
                                      ✅ {carpeta.num_completados}
                                    </span>
                                  )}
                                  {carpeta.num_progreso > 0 && (
                                    <span className="stat-badge progreso">
                                      ⏳ {carpeta.num_progreso}
                                    </span>
                                  )}
                                </p>
                              ) : (
                                <p className="carpeta-stats">
                                  <span className="stat-badge vacio">Sin exámenes</span>
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="carpeta-menu">
                            <button 
                              className="btn-menu-dots"
                              onClick={(e) => {
                                e.stopPropagation();
                                setMenuAbierto(menuAbierto === `carpeta-examen-${idx}` ? null : `carpeta-examen-${idx}`);
                              }}
                            >
                              ⋮
                            </button>
                            {menuAbierto === `carpeta-examen-${idx}` && (
                              <div className="menu-dropdown">
                                <button onClick={(e) => {
                                  e.stopPropagation();
                                  setMenuAbierto(null);
                                  eliminarCarpetaExamenes(carpeta.ruta, carpeta.nombre);
                                }} className="btn-menu-eliminar">
                                  🗑️ Eliminar
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Exámenes en Progreso en esta carpeta */}
                {examenesProgreso.length > 0 && (
                  <div className="examenes-section">
                    <h2>⏳ Por Completar ({examenesProgreso.length})</h2>
                    <div className="examenes-grid">
                      {examenesProgreso.map((examen, idx) => (
                        <div key={idx} className="examen-card en-progreso">
                          <div className="examen-card-header">
                            <h3>📝 {examen.carpeta_nombre}</h3>
                            <div className="header-badges">
                              <span className="badge badge-warning">En Progreso</span>
                              <button 
                                className="btn-menu-dots"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setMenuAbierto(menuAbierto === `examen-progreso-${idx}` ? null : `examen-progreso-${idx}`);
                                }}
                              >
                                ⋮
                              </button>
                              {menuAbierto === `examen-progreso-${idx}` && (
                                <div className="menu-dropdown">
                                  <button onClick={(e) => {
                                    e.stopPropagation();
                                    setMenuAbierto(null);
                                    eliminarExamen(examen, 'progreso');
                                  }} className="btn-menu-eliminar">
                                    🗑️ Eliminar
                                  </button>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="examen-card-body">
                            <p className="examen-fecha">
                              Iniciado: {new Date(examen.fecha_inicio).toLocaleString('es-ES')}
                            </p>
                            <p className="examen-info">
                              {examen.preguntas.length} preguntas • {Object.keys(examen.respuestas || {}).length} respondidas
                            </p>
                            <div className="examen-progreso">
                              <div className="progreso-bar">
                                <div 
                                  className="progreso-fill"
                                  style={{
                                    width: `${(Object.keys(examen.respuestas || {}).length / examen.preguntas.length) * 100}%`
                                  }}
                                ></div>
                              </div>
                              <span className="progreso-texto">
                                {Math.round((Object.keys(examen.respuestas || {}).length / examen.preguntas.length) * 100)}% completado
                              </span>
                            </div>
                          </div>
                          <div className="examen-card-actions">
                            <button 
                              className="btn-continuar"
                              onClick={() => continuarExamen(examen)}
                            >
                              ▶️ Continuar
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Exámenes Completados en esta carpeta */}
                {examenesCompletados.length > 0 && (
                  <div className="examenes-section">
                    <h2>✅ Completados ({examenesCompletados.length})</h2>
                    <div className="examenes-grid">
                      {examenesCompletados.map((examen, idx) => (
                        <div key={idx} className="examen-card completado">
                          <div className="examen-card-header">
                            <h3>📝 {examen.carpeta_nombre}</h3>
                            <div className="header-badges">
                              <span 
                                className={`badge ${
                                  examen.porcentaje >= 70 ? 'badge-success' : 
                                  examen.porcentaje >= 50 ? 'badge-warning' : 
                                  'badge-danger'
                                }`}
                              >
                                {examen.porcentaje.toFixed(1)}%
                              </span>
                              <button 
                                className="btn-menu-dots"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setMenuAbierto(menuAbierto === `examen-completado-${idx}` ? null : `examen-completado-${idx}`);
                                }}
                              >
                                ⋮
                              </button>
                              {menuAbierto === `examen-completado-${idx}` && (
                                <div className="menu-dropdown">
                                  <button onClick={(e) => {
                                    e.stopPropagation();
                                    setMenuAbierto(null);
                                    eliminarExamen(examen, 'completado');
                                  }} className="btn-menu-eliminar">
                                    🗑️ Eliminar
                                  </button>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="examen-card-body">
                            <p className="examen-fecha">
                              Completado: {new Date(examen.fecha_completado).toLocaleString('es-ES')}
                            </p>
                            <div className="examen-resultado">
                              <div className="resultado-item">
                                <span className="resultado-label">Puntuación:</span>
                                <span className="resultado-valor">
                                  {examen.puntos_obtenidos} / {examen.puntos_totales}
                                </span>
                              </div>
                              <div className="resultado-item">
                                <span className="resultado-label">Estado:</span>
                                <span className={`resultado-estado ${
                                  examen.porcentaje >= 70 ? 'aprobado' : 
                                  examen.porcentaje >= 50 ? 'regular' : 
                                  'reprobado'
                                }`}>
                                  {examen.porcentaje >= 70 ? '✅ Aprobado' : 
                                   examen.porcentaje >= 50 ? '⚠️ Regular' : 
                                   '❌ Reprobado'}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="examen-card-actions">
                            <button 
                              className="btn-ver-resultado"
                              onClick={() => verResultadoExamen(examen)}
                            >
                              👁️ Ver Detalles
                            </button>
                            <button 
                              className="btn-reintentar"
                              onClick={() => reintentarExamen(examen)}
                            >
                              🔄 Reintentar
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Mensaje cuando no hay nada */}
                {carpetasExamenes.length === 0 && examenesCompletados.length === 0 && examenesProgreso.length === 0 && (
                  <div className="no-data">
                    <p>📭 No hay exámenes en esta carpeta</p>
                    <p className="hint">Ve a Cursos y genera un examen desde una carpeta</p>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {selectedMenu === 'historial' && (
          <div className="content-section">
            <h1>Historial</h1>
            <p>Revisa los exámenes generados anteriormente...</p>
          </div>
        )}

        {selectedMenu === 'chat' && (
          <div className="chat-section">
            <div className="chat-header">
              <div className="chat-header-actions">
                <button 
                  className="btn-chat-action"
                  onClick={abrirModalHistorial}
                  title="Ver historial de chats"
                >
                  📚 Historial ({historialChats.length})
                </button>
                <button 
                  className="btn-chat-action"
                  onClick={nuevoChat}
                  title="Nuevo chat"
                >
                  ➕ Nuevo
                </button>
                {mensajesChat.length > 0 && (
                  <>
                    <button 
                      className="btn-chat-action btn-move"
                      onClick={() => setMostrarModalCarpetas(true)}
                      title="Mover chat a carpeta"
                    >
                      📁 Mover
                    </button>
                  </>
                )}
              </div>
            </div>
            {carpetaChatActual && (
              <div className="chat-carpeta-actual">
                📁 {carpetaChatActual}
              </div>
            )}
            {nombreChatNuevo && (
              <div className="chat-nombre-actual">
                💬 {nombreChatNuevo} • Guardado automático
              </div>
            )}

            {!configuracion?.modelo_path || !configuracion?.modelo_activo ? (
              <div className="no-data">
                {!configuracion?.modelo_path ? (
                  <>
                    <p>⚠️ No hay modelo configurado</p>
                    <p>Ve a Configuración y selecciona un modelo para comenzar a chatear</p>
                  </>
                ) : (
                  <>
                    <p>⚠️ El modelo está configurado pero no cargado</p>
                    <p>Recarga la página o reinicia el servidor para cargar el modelo</p>
                  </>
                )}
                <button 
                  className="btn-primary"
                  onClick={() => setSelectedMenu('configuracion')}
                >
                  Ir a Configuración
                </button>
              </div>
            ) : (
              <>
                <div className="chat-container">
                  <div className="chat-messages">
                    {mensajesChat.length === 0 ? (
                      <div className="chat-empty">
                        <div className="chat-empty-icon">🤖</div>
                        <h3>¡Hola! Soy tu asistente de IA</h3>
                        <p>Escribe un mensaje para comenzar la conversación</p>
                        <div className="chat-suggestions">
                          <button 
                            className="suggestion-btn"
                            onClick={() => setInputChat('Explícame sobre la fotosíntesis')}
                          >
                            Explícame sobre la fotosíntesis
                          </button>
                          <button 
                            className="suggestion-btn"
                            onClick={() => setInputChat('¿Qué es la inteligencia artificial?')}
                          >
                            ¿Qué es la inteligencia artificial?
                          </button>
                          <button 
                            className="suggestion-btn"
                            onClick={() => setInputChat('Genera 3 preguntas sobre matemáticas')}
                          >
                            Genera 3 preguntas sobre matemáticas
                          </button>
                        </div>
                      </div>
                    ) : (
                      mensajesChat.map((msg, idx) => (
                        <div key={idx} className={`chat-message ${msg.tipo}`}>
                          <div className="message-icon">
                            {msg.tipo === 'usuario' ? '👤' : '🤖'}
                          </div>
                          <div className="message-content">
                            {editandoMensaje === idx && msg.tipo === 'usuario' ? (
                              <div className="message-edit-container">
                                <textarea
                                  className="message-edit-input"
                                  value={textoEditado}
                                  onChange={(e) => setTextoEditado(e.target.value)}
                                  rows={3}
                                  autoFocus
                                />
                                <div className="message-edit-actions">
                                  <button 
                                    className="btn-edit-save"
                                    onClick={() => guardarEdicionMensaje(idx)}
                                    disabled={!textoEditado.trim()}
                                  >
                                    ✓ Guardar
                                  </button>
                                  <button 
                                    className="btn-edit-cancel"
                                    onClick={cancelarEdicion}
                                  >
                                    ✕ Cancelar
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <>
                                <div className="message-text">
                                  {msg.archivo && (
                                    <div className="message-archivo">
                                      📎 {msg.archivo}
                                    </div>
                                  )}
                                  {msg.busqueda_web && (
                                    <div className="message-web">
                                      🌐 Búsqueda web
                                    </div>
                                  )}
                                  {msg.texto}
                                </div>
                                <div className="message-footer">
                                  <div className="message-time">{msg.hora}</div>
                                  {msg.tipo === 'usuario' && !cargandoChat && (
                                    <button 
                                      className="btn-edit-message"
                                      onClick={() => iniciarEdicionMensaje(idx)}
                                      title="Editar mensaje"
                                    >
                                      ✏️
                                    </button>
                                  )}
                                </div>
                              </>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                    {cargandoChat && (
                      <div className="chat-message asistente">
                        <div className="message-icon">🤖</div>
                        <div className="message-content">
                          <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Área de archivo de contexto */}
                {archivoContexto && (
                  <div className="contexto-archivo">
                    <div className="contexto-info">
                      <span className="contexto-icon">📎</span>
                      <span className="contexto-nombre">{nombreArchivoContexto}</span>
                      <span className="contexto-size">({(contenidoContexto.length / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button 
                      className="btn-remover-contexto"
                      onClick={removerArchivoContexto}
                      title="Remover archivo"
                    >
                      ✕
                    </button>
                  </div>
                )}

                <div className="chat-input-container">
                  <div className="chat-input-wrapper">
                    <textarea
                      className="chat-input"
                      placeholder="Escribe tu mensaje aquí..."
                      value={inputChat}
                      onChange={(e) => setInputChat(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          enviarMensajeChat();
                        }
                      }}
                      disabled={cargandoChat}
                      rows={3}
                    />
                    <div className="chat-input-actions">
                      <label className="btn-adjuntar" title="Adjuntar PDF o TXT">
                        📎
                        <input 
                          type="file" 
                          accept=".pdf,.txt"
                          onChange={handleArchivoContexto}
                          style={{ display: 'none' }}
                        />
                      </label>
                      <button 
                        className={`btn-busqueda-web ${busquedaWebActiva ? 'activo' : ''}`}
                        onClick={() => setBusquedaWebActiva(!busquedaWebActiva)}
                        title={busquedaWebActiva ? "Búsqueda web activada" : "Activar búsqueda web"}
                      >
                        🌐
                      </button>
                      {cargandoChat ? (
                        <button 
                          className="btn-stop-chat"
                          onClick={detenerConsulta}
                          title="Detener consulta"
                        >
                          ⏹️ Detener
                        </button>
                      ) : (
                        <button 
                          className="btn-send-chat"
                          onClick={enviarMensajeChat}
                          disabled={!inputChat.trim()}
                        >
                          📤 Enviar
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {selectedMenu === 'configuracion' && (
          <div className="content-section">
            <h1>⚙️ Configuración</h1>
            <p className="subtitle">Ajusta el modelo de IA para generar exámenes</p>

            {cargandoConfig ? (
              <p className="loading">Cargando configuración...</p>
            ) : (
              <>
                {/* Modelo actual */}
                <div className="config-section">
                  <h2>🤖 Modelo Actual</h2>
                  {configuracion?.modelo_path ? (
                    <div className="modelo-actual-card">
                      <div className="modelo-actual-info">
                        <h3>✅ Modelo configurado</h3>
                        <p className="modelo-nombre">{configuracion.modelo_path.split('\\').pop().split('/').pop()}</p>
                        {configuracion.modelo_cargado && (
                          <p className="modelo-estado">
                            {configuracion.modelo_activo ? (
                              <span className="estado-activo">🟢 Activo en memoria</span>
                            ) : (
                              <span className="estado-inactivo">⚪ No cargado</span>
                            )}
                          </p>
                        )}
                        {configuracion.modelo_cargado && configuracion.modelo_cargado !== configuracion.modelo_path && (
                          <p className="modelo-advertencia">
                            ⚠️ El modelo en memoria es diferente al configurado. 
                            Genera un examen para aplicar el cambio.
                          </p>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="modelo-actual-card sin-modelo">
                      <div className="modelo-actual-info">
                        <h3>⚠️ Sin modelo configurado</h3>
                        <p>Selecciona un modelo para comenzar a generar exámenes</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Motor de IA (GPU/CPU) */}
                <div className="config-section">
                  <h2>🎮 Modo de Ejecución</h2>
                  <p className="subtitle" style={{marginBottom: '1.5rem'}}>
                    Selecciona si quieres usar GPU o CPU
                  </p>

                  <div className="motor-selector">
                    <div 
                      className={`motor-opcion ${configuracion?.gpu_activa ? 'seleccionada' : ''}`}
                      onClick={async () => {
                        try {
                          setLoading(true)
                          const response = await fetch(`${API_URL}/api/motor/cambiar`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                              usar_ollama: true,
                              modelo_ollama: configuracion?.modelo_ollama_activo || 'llama31-local',
                              n_gpu_layers: 35
                            })
                          })
                          const data = await response.json()
                          if (data.success) {
                            setMensaje({tipo: 'exito', texto: '✅ Modo GPU activado'})
                            cargarConfiguracion()
                          }
                        } catch (error) {
                          setMensaje({tipo: 'error', texto: '❌ Error: ' + error.message})
                        } finally {
                          setLoading(false)
                        }
                      }}
                    >
                      <div className="motor-icon">🎮</div>
                      <h3>Modo GPU</h3>
                      <div className="motor-badge motor-badge-gpu">Recomendado</div>
                      <p className="motor-descripcion">
                        Usa tu tarjeta gráfica para procesar más rápido
                      </p>
                    </div>

                    <div 
                      className={`motor-opcion ${!configuracion?.gpu_activa ? 'seleccionada' : ''}`}
                      onClick={async () => {
                        if (!configuracion?.modelo_path) {
                          setMensaje({tipo: 'error', texto: '⚠️ Primero configura un modelo GGUF abajo'})
                          return
                        }
                        try {
                          setLoading(true)
                          const response = await fetch(`${API_URL}/api/motor/cambiar`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                              usar_ollama: false,
                              modelo_gguf: configuracion.modelo_path,
                              n_gpu_layers: 0
                            })
                          })
                          const data = await response.json()
                          if (data.success) {
                            setMensaje({tipo: 'exito', texto: '✅ Modo CPU activado'})
                            cargarConfiguracion()
                          }
                        } catch (error) {
                          setMensaje({tipo: 'error', texto: '❌ Error: ' + error.message})
                        } finally {
                          setLoading(false)
                        }
                      }}
                    >
                      <div className="motor-icon">💻</div>
                      <h3>Modo CPU</h3>
                      <div className="motor-badge motor-badge-manual">Más lento</div>
                      <p className="motor-descripcion">
                        Usa solo el procesador (no requiere GPU)
                      </p>
                    </div>
                  </div>

                  {/* Estado actual */}
                  <div className="motor-estado-actual">
                    {configuracion?.gpu_activa ? (
                      <div className="estado-activo">
                        🎮 <strong>Modo activo:</strong> GPU | 
                        🤖 <strong>Modelo:</strong> {configuracion.modelo_cargado || 'N/A'}
                      </div>
                    ) : (
                      <div className="estado-activo">
                        💻 <strong>Modo activo:</strong> CPU | 
                        🤖 <strong>Modelo:</strong> {configuracion.modelo_cargado ? configuracion.modelo_cargado.split('\\').pop() : 'N/A'}
                      </div>
                    )}
                  </div>
                </div>

                {/* Modelos con pestañas */}
                <div className="config-section">
                  <h2>🤖 Gestión de Modelos</h2>
                  
                  {/* Pestañas */}
                  <div className="pestanas-modelos">
                    <button 
                      className={`pestana-btn ${pestanaModelos === 'ollama' ? 'activa' : ''}`}
                      onClick={() => setPestanaModelos('ollama')}
                    >
                      🎮 Modelos Ollama (GPU)
                    </button>
                    <button 
                      className={`pestana-btn ${pestanaModelos === 'gguf' ? 'activa' : ''}`}
                      onClick={() => setPestanaModelos('gguf')}
                    >
                      💻 Modelos GGUF (CPU)
                    </button>
                  </div>

                  {/* Contenido de Ollama */}
                  {pestanaModelos === 'ollama' && (
                    <div className="pestana-contenido">
                      <p className="subtitle">Modelos que usan GPU automáticamente</p>
                      
                      <button 
                        onClick={async () => {
                          try {
                            setLoading(true)
                            const response = await fetch(`${API_URL}/api/ollama/modelos`)
                            const data = await response.json()
                            if (data.success) {
                              setModelosOllama(data.modelos)
                              setMensaje({tipo: 'exito', texto: `✅ ${data.total} modelos encontrados`})
                            } else {
                              setMensaje({tipo: 'error', texto: '⚠️ ' + data.mensaje})
                            }
                          } catch (error) {
                            setMensaje({tipo: 'error', texto: '❌ Error: ' + error.message})
                          } finally {
                            setLoading(false)
                          }
                        }}
                        className="btn-refrescar-ollama"
                        disabled={loading}
                      >
                        🔄 Cargar Modelos de Ollama
                      </button>

                      {modelosOllama.length > 0 ? (
                        <div className="modelos-ollama-grid">
                          {modelosOllama.map(modelo => (
                            <div 
                              key={modelo.nombre}
                              className={`modelo-ollama-card ${configuracion?.modelo_ollama_activo === modelo.nombre ? 'seleccionado' : ''}`}
                            >
                              <div className="modelo-ollama-header">
                                <h3>🤖 {modelo.nombre}</h3>
                                <span className="modelo-badge modelo-badge-gpu">{modelo.tipo}</span>
                              </div>
                              <div className="modelo-ollama-info">
                                <div className="info-item">
                                  <span className="info-label">Tamaño:</span>
                                  <span className="info-value">{modelo.tamaño_gb} GB</span>
                                </div>
                                <div className="info-item">
                                  <span className="info-label">Velocidad:</span>
                                  <span className="info-value">{modelo.velocidad}</span>
                                </div>
                                <div className="info-item">
                                  <span className="info-label">ID:</span>
                                  <span className="info-value" style={{fontSize: '0.8rem'}}>{modelo.digest}</span>
                                </div>
                              </div>
                              <div className="modelo-ollama-actions">
                                <button
                                  className="btn-activar-modelo"
                                  onClick={async (e) => {
                                    e.stopPropagation()
                                    try {
                                      setLoading(true)
                                      const responseMotor = await fetch(`${API_URL}/api/motor/cambiar`, {
                                        method: 'POST',
                                        headers: {'Content-Type': 'application/json'},
                                        body: JSON.stringify({
                                          usar_ollama: true,
                                          modelo_ollama: modelo.nombre,
                                          n_gpu_layers: 35
                                        })
                                      })
                                      const dataMotor = await responseMotor.json()
                                      
                                      if (dataMotor.success) {
                                        setMensaje({tipo: 'exito', texto: `✅ Modelo ${modelo.nombre} activado con GPU`})
                                        cargarConfiguracion()
                                      }
                                    } catch (error) {
                                      setMensaje({tipo: 'error', texto: '❌ Error: ' + error.message})
                                    } finally {
                                      setLoading(false)
                                    }
                                  }}
                                  disabled={configuracion?.modelo_ollama_activo === modelo.nombre}
                                >
                                  {configuracion?.modelo_ollama_activo === modelo.nombre ? '✓ Activo' : '🚀 Activar'}
                                </button>
                                <button
                                  className="btn-eliminar-modelo"
                                  onClick={async (e) => {
                                    e.stopPropagation()
                                    if (!window.confirm(`¿Estás seguro de eliminar el modelo "${modelo.nombre}"?\n\nEsto liberará ${modelo.tamaño_gb} GB de espacio.`)) {
                                      return
                                    }
                                    try {
                                      setLoading(true)
                                      const response = await fetch(`${API_URL}/api/ollama/modelo/${encodeURIComponent(modelo.nombre)}`, {
                                        method: 'DELETE'
                                      })
                                      const data = await response.json()
                                      
                                      if (data.success) {
                                        setMensaje({tipo: 'exito', texto: data.mensaje})
                                        // Recargar lista de modelos
                                        const responseModelos = await fetch(`${API_URL}/api/ollama/modelos`)
                                        const dataModelos = await responseModelos.json()
                                        if (dataModelos.success) {
                                          setModelosOllama(dataModelos.modelos)
                                        }
                                      } else {
                                        setMensaje({tipo: 'error', texto: data.mensaje})
                                      }
                                    } catch (error) {
                                      setMensaje({tipo: 'error', texto: '❌ Error: ' + error.message})
                                    } finally {
                                      setLoading(false)
                                    }
                                  }}
                                  disabled={configuracion?.modelo_ollama_activo === modelo.nombre}
                                  title={configuracion?.modelo_ollama_activo === modelo.nombre ? 'No puedes eliminar el modelo activo' : 'Eliminar modelo'}
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="empty-state">
                          <p>📭 No hay modelos de Ollama cargados</p>
                          <p className="empty-hint">
                            Haz clic en "Cargar Modelos" o instala modelos con: <code>ollama pull llama3.2:3b</code>
                          </p>
                          <div style={{marginTop: '1rem', padding: '1rem', background: 'rgba(100, 108, 255, 0.1)', borderRadius: '8px'}}>
                            <p style={{fontSize: '0.9rem', color: '#b0b0c0', margin: 0}}>
                              <strong>Modelos recomendados:</strong>
                            </p>
                            <ul style={{fontSize: '0.85rem', color: '#999', marginTop: '0.5rem'}}>
                              <li><code>ollama pull llama3.2:3b</code> - Rápido y ligero (2 GB)</li>
                              <li><code>ollama pull qwen2.5:7b</code> - Excelente en español (4.4 GB)</li>
                              <li><code>ollama pull llama3.1:8b</code> - Balance perfecto (4.9 GB)</li>
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Contenido de GGUF */}
                  {pestanaModelos === 'gguf' && (
                    <div className="pestana-contenido">
                      <p className="subtitle">Modelos que se ejecutan en CPU</p>
                      
                      {modelosDisponibles.length > 0 ? (
                        <div className="modelos-grid">
                          {modelosDisponibles.map(modelo => (
                            <div 
                              key={modelo.ruta}
                              className={`modelo-card ${modeloSeleccionado === modelo.ruta ? 'seleccionado' : ''}`}
                              onClick={async () => {
                                try {
                                  setLoading(true)
                                  setModeloSeleccionado(modelo.ruta)
                                  
                                  // Cambiar a modo CPU con este modelo
                                  const response = await fetch(`${API_URL}/api/motor/cambiar`, {
                                    method: 'POST',
                                    headers: {'Content-Type': 'application/json'},
                                    body: JSON.stringify({
                                      usar_ollama: false,
                                      modelo_gguf: modelo.ruta,
                                      n_gpu_layers: 0
                                    })
                                  })
                                  const data = await response.json()
                                  
                                  if (data.success) {
                                    // Guardar configuración
                                    await fetch(`${API_URL}/api/config`, {
                                      method: 'POST',
                                      headers: {'Content-Type': 'application/json'},
                                      body: JSON.stringify({
                                        modelo_path: modelo.ruta,
                                        ajustes_avanzados: ajustesAvanzados
                                      })
                                    })
                                    
                                    setMensaje({tipo: 'exito', texto: `✅ Modelo ${modelo.nombre} activado en CPU`})
                                    cargarConfiguracion()
                                  }
                                } catch (error) {
                                  setMensaje({tipo: 'error', texto: '❌ Error: ' + error.message})
                                } finally {
                                  setLoading(false)
                                }
                              }}
                            >
                              <div className="modelo-header">
                                <h3>🤖 {modelo.nombre}</h3>
                                <span className="modelo-badge modelo-badge-manual">{modelo.tamaño_modelo}</span>
                              </div>
                              
                              <div className="modelo-stats">
                                <div className="stat">
                                  <span className="stat-label">Tamaño:</span>
                                  <span className="stat-value">{modelo.tamaño_gb} GB</span>
                                </div>
                                <div className="stat">
                                  <span className="stat-label">Parámetros:</span>
                                  <span className="stat-value">{modelo.parametros}</span>
                                </div>
                                <div className="stat">
                                  <span className="stat-label">Velocidad:</span>
                                  <span className="stat-value">{modelo.velocidad}</span>
                                </div>
                                <div className="stat">
                                  <span className="stat-label">RAM necesaria:</span>
                                  <span className="stat-value">{modelo.ram_necesaria}</span>
                                </div>
                              </div>

                              <div className="modelo-descripcion">
                                <p><strong>Calidad:</strong> {modelo.calidad}</p>
                                <p>{modelo.descripcion}</p>
                              </div>

                              {!configuracion?.gpu_activa && configuracion?.modelo_path === modelo.ruta && (
                                <div className="modelo-seleccionado-badge">
                                  ✓ Activo en CPU
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="empty-state">
                          <p>💭 No hay modelos GGUF instalados</p>
                          <p className="empty-hint">Descarga modelos desde la sección de abajo</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Modelos disponibles para descargar */}
                <div className="config-section">
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <h2>📥 Descargar Modelos</h2>
                    <button 
                      onClick={() => setMostrarDescarga(!mostrarDescarga)}
                      className="btn-toggle-descarga"
                    >
                      {mostrarDescarga ? '▼ Ocultar' : '▶ Mostrar'} ({modelosParaDescargar.length} disponibles)
                    </button>
                  </div>
                  
                  {mostrarDescarga && (
                    <>
                      <p style={{color: '#b0b0c0', marginBottom: '1.5rem'}}>
                        Modelos optimizados para generar exámenes. Los modelos marcados con 🔒 requieren autenticación de HuggingFace.
                      </p>
                      <div className="modelos-descarga-grid">
                        {modelosParaDescargar.map(modelo => (
                          <div key={modelo.id} className={`modelo-descarga-card ${modelo.descargado ? 'descargado' : ''}`}>
                            <div className="modelo-header">
                              <div>
                                <h3>🤖 {modelo.nombre}</h3>
                                {modelo.recomendado && <span className="badge-recomendado">⭐ Recomendado</span>}
                              </div>
                              <span className="modelo-badge">{modelo.tamaño_modelo}</span>
                            </div>

                            <div className="modelo-stats">
                              <div className="stat">
                                <span className="stat-label">Tamaño:</span>
                                <span className="stat-value">{modelo.tamaño_gb} GB</span>
                              </div>
                              <div className="stat">
                                <span className="stat-label">Parámetros:</span>
                                <span className="stat-value">{modelo.parametros}</span>
                              </div>
                              <div className="stat">
                                <span className="stat-label">Velocidad:</span>
                                <span className="stat-value">{modelo.velocidad}</span>
                              </div>
                              <div className="stat">
                                <span className="stat-label">RAM necesaria:</span>
                                <span className="stat-value">{modelo.ram_necesaria}</span>
                              </div>
                            </div>

                            <div className="modelo-descripcion">
                              <p><strong>Calidad:</strong> {modelo.calidad}</p>
                              <p>{modelo.descripcion}</p>
                            </div>

                            {modelo.descargado ? (
                              <div className="modelo-descargado-badge">
                                ✅ Ya descargado
                              </div>
                            ) : (
                              <div className="modelo-descarga-accion">
                                {modelo.requiere_auth ? (
                                  <div className="descarga-manual">
                                    <p style={{fontSize: '0.9rem', color: '#ff9800', marginBottom: '0.5rem'}}>
                                      🔒 Requiere autenticación de HuggingFace
                                    </p>
                                    <a 
                                      href={modelo.url.replace('/resolve/', '/blob/')} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="btn-descargar-manual"
                                    >
                                      📥 Descargar desde HuggingFace
                                    </a>
                                    <p style={{fontSize: '0.8rem', color: '#a0a0b0', marginTop: '0.5rem'}}>
                                      Guarda el archivo en la carpeta "modelos"
                                    </p>
                                  </div>
                                ) : (
                                  <a 
                                    href={modelo.url}
                                    download={modelo.archivo}
                                    className="btn-descargar"
                                  >
                                    ⬇️ Descargar ({modelo.tamaño_gb} GB)
                                  </a>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      
                      <div style={{marginTop: '1.5rem', padding: '1rem', background: 'rgba(100, 108, 255, 0.1)', borderRadius: '8px', borderLeft: '3px solid #646cff'}}>
                        <p style={{color: '#b0b0c0', margin: 0, fontSize: '0.9rem'}}>
                          💡 <strong>Tip:</strong> Después de descargar un modelo, recarga esta página para que aparezca en "Modelos Disponibles".
                        </p>
                      </div>
                    </>
                  )}
                </div>

                {/* Ajustes Avanzados */}
                <div className="config-section">
                  <div 
                    style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer'}}
                    onClick={() => setMostrarAjustesAvanzados(!mostrarAjustesAvanzados)}
                  >
                    <h2>🔧 Ajustes Avanzados</h2>
                    <span style={{fontSize: '1.5rem'}}>{mostrarAjustesAvanzados ? '▼' : '▶'}</span>
                  </div>
                  
                  {mostrarAjustesAvanzados && (
                    <div style={{marginTop: '1rem'}}>
                      <p style={{color: '#b0b0c0', marginBottom: '1.5rem'}}>
                        Estos ajustes controlan cómo trabaja el modelo de IA. Solo modifícalos si sabes lo que haces.
                      </p>

                      {/* Tamaño del Contexto */}
                      <div className="ajuste-item">
                        <div className="ajuste-header">
                          <label>📏 Tamaño del Contexto (n_ctx)</label>
                          <span className="ajuste-valor">{ajustesAvanzados.n_ctx} tokens</span>
                        </div>
                        <input 
                          type="range" 
                          min="1024" 
                          max="32768" 
                          step="1024"
                          value={ajustesAvanzados.n_ctx}
                          onChange={(e) => setAjustesAvanzados({...ajustesAvanzados, n_ctx: parseInt(e.target.value)})}
                          onMouseUp={guardarAjustesAvanzados}
                          onTouchEnd={guardarAjustesAvanzados}
                          className="ajuste-slider"
                        />
                        <div className="ajuste-explicacion">
                          <p><strong>¿Qué es?</strong> Cantidad de texto que el modelo puede "recordar" a la vez.</p>
                          <div className="pros-cons">
                            <div className="pros">
                              <strong>✅ Más tokens (8192+):</strong>
                              <ul>
                                <li>Puede analizar documentos más largos</li>
                                <li>Conversaciones más extensas con memoria</li>
                                <li>Mejor para PDFs grandes</li>
                              </ul>
                            </div>
                            <div className="cons">
                              <strong>❌ Más tokens consume:</strong>
                              <ul>
                                <li>Mucha más RAM (puede usar 8-16 GB extra)</li>
                                <li>Respuestas más lentas</li>
                                <li>Puede congelar si no tienes suficiente RAM</li>
                              </ul>
                            </div>
                          </div>
                          <p className="recomendacion">
                            <strong>💡 Recomendado:</strong> 4096 tokens (3-4 páginas de texto) para uso normal. 
                            Solo aumenta si necesitas analizar documentos muy largos Y tienes 16GB+ de RAM.
                          </p>
                        </div>
                      </div>

                      {/* Temperatura */}
                      <div className="ajuste-item">
                        <div className="ajuste-header">
                          <label>🌡️ Temperatura (Creatividad)</label>
                          <span className="ajuste-valor">{ajustesAvanzados.temperature}</span>
                        </div>
                        <input 
                          type="range" 
                          min="0.1" 
                          max="2.0" 
                          step="0.1"
                          value={ajustesAvanzados.temperature}
                          onChange={(e) => setAjustesAvanzados({...ajustesAvanzados, temperature: parseFloat(e.target.value)})}
                          onMouseUp={guardarAjustesAvanzados}
                          onTouchEnd={guardarAjustesAvanzados}
                          className="ajuste-slider"
                        />
                        <div className="ajuste-explicacion">
                          <p><strong>¿Qué es?</strong> Controla qué tan "creativo" o "predecible" es el modelo.</p>
                          <div className="pros-cons">
                            <div className="pros">
                              <strong>🔥 Temperatura alta (1.0-2.0):</strong>
                              <ul>
                                <li>Respuestas más variadas y creativas</li>
                                <li>Bueno para generar ideas diferentes</li>
                                <li>Menos repetitivo</li>
                              </ul>
                            </div>
                            <div className="cons">
                              <strong>❄️ Temperatura baja (0.1-0.5):</strong>
                              <ul>
                                <li>Respuestas más precisas y consistentes</li>
                                <li>Mejor para tareas técnicas</li>
                                <li>Menos errores o "alucinaciones"</li>
                              </ul>
                            </div>
                          </div>
                          <p className="recomendacion">
                            <strong>💡 Recomendado:</strong> 0.7 para uso general. Baja a 0.3-0.5 para exámenes técnicos. 
                            Sube a 1.0+ si quieres preguntas más creativas o variadas.
                          </p>
                        </div>
                      </div>

                      {/* Máximo de tokens de respuesta */}
                      <div className="ajuste-item">
                        <div className="ajuste-header">
                          <label>📝 Longitud Máxima de Respuesta</label>
                          <span className="ajuste-valor">{ajustesAvanzados.max_tokens} tokens (~{Math.round(ajustesAvanzados.max_tokens * 0.75)} palabras)</span>
                        </div>
                        <input 
                          type="range" 
                          min="128" 
                          max="2048" 
                          step="128"
                          value={ajustesAvanzados.max_tokens}
                          onChange={(e) => setAjustesAvanzados({...ajustesAvanzados, max_tokens: parseInt(e.target.value)})}
                          onMouseUp={guardarAjustesAvanzados}
                          onTouchEnd={guardarAjustesAvanzados}
                          className="ajuste-slider"
                        />
                        <div className="ajuste-explicacion">
                          <p><strong>¿Qué es?</strong> Cuánto texto puede generar el modelo en una sola respuesta.</p>
                          <div className="pros-cons">
                            <div className="pros">
                              <strong>✅ Más tokens (1024+):</strong>
                              <ul>
                                <li>Respuestas más completas y detalladas</li>
                                <li>Puede generar textos largos de una vez</li>
                                <li>Mejor para explicaciones extensas</li>
                              </ul>
                            </div>
                            <div className="cons">
                              <strong>❌ Más tokens significa:</strong>
                              <ul>
                                <li>Esperas más tiempo por cada respuesta</li>
                                <li>Mayor consumo de recursos</li>
                                <li>A veces genera relleno innecesario</li>
                              </ul>
                            </div>
                          </div>
                          <p className="recomendacion">
                            <strong>💡 Recomendado:</strong> 512 tokens para chat normal (respuestas de 1-2 párrafos). 
                            Sube a 1024+ si necesitas generar exámenes completos o textos largos.
                          </p>
                        </div>
                      </div>

                      {/* Top P */}
                      <div className="ajuste-item">
                        <div className="ajuste-header">
                          <label>🎯 Top P (Selección de palabras)</label>
                          <span className="ajuste-valor">{ajustesAvanzados.top_p}</span>
                        </div>
                        <input 
                          type="range" 
                          min="0.1" 
                          max="1.0" 
                          step="0.05"
                          value={ajustesAvanzados.top_p}
                          onChange={(e) => setAjustesAvanzados({...ajustesAvanzados, top_p: parseFloat(e.target.value)})}
                          onMouseUp={guardarAjustesAvanzados}
                          onTouchEnd={guardarAjustesAvanzados}
                          className="ajuste-slider"
                        />
                        <div className="ajuste-explicacion">
                          <p><strong>¿Qué es?</strong> Controla qué tan diversas pueden ser las palabras que elige el modelo.</p>
                          <div className="pros-cons">
                            <div className="pros">
                              <strong>✅ Top P bajo (0.5-0.7):</strong>
                              <ul>
                                <li>Más preciso y enfocado</li>
                                <li>Menos errores o "alucinaciones"</li>
                                <li>Mejor para tareas técnicas</li>
                              </ul>
                            </div>
                            <div className="cons">
                              <strong>⚠️ Top P alto (0.9-1.0):</strong>
                              <ul>
                                <li>Más variedad en las respuestas</li>
                                <li>Puede ser menos predecible</li>
                                <li>A veces genera ideas interesantes</li>
                              </ul>
                            </div>
                          </div>
                          <p className="recomendacion">
                            <strong>💡 Recomendado:</strong> 0.9 para la mayoría de casos. Si quieres respuestas más directas y precisas, baja a 0.7.
                          </p>
                        </div>
                      </div>

                      {/* Repeat Penalty */}
                      <div className="ajuste-item">
                        <div className="ajuste-header">
                          <label>🔁 Penalización por Repetición</label>
                          <span className="ajuste-valor">{ajustesAvanzados.repeat_penalty}</span>
                        </div>
                        <input 
                          type="range" 
                          min="1.0" 
                          max="1.5" 
                          step="0.05"
                          value={ajustesAvanzados.repeat_penalty}
                          onChange={(e) => setAjustesAvanzados({...ajustesAvanzados, repeat_penalty: parseFloat(e.target.value)})}
                          onMouseUp={guardarAjustesAvanzados}
                          onTouchEnd={guardarAjustesAvanzados}
                          className="ajuste-slider"
                        />
                        <div className="ajuste-explicacion">
                          <p><strong>¿Qué es?</strong> Evita que el modelo repita las mismas palabras o frases constantemente.</p>
                          <div className="pros-cons">
                            <div className="pros">
                              <strong>✅ Penalty bajo (1.0-1.1):</strong>
                              <ul>
                                <li>Más natural y fluido</li>
                                <li>Puede usar palabras clave repetidas</li>
                                <li>Mejor para textos técnicos</li>
                              </ul>
                            </div>
                            <div className="cons">
                              <strong>⚠️ Penalty alto (1.3-1.5):</strong>
                              <ul>
                                <li>Evita mucho la repetición</li>
                                <li>Más variedad de vocabulario</li>
                                <li>A veces usa sinónimos raros</li>
                              </ul>
                            </div>
                          </div>
                          <p className="recomendacion">
                            <strong>💡 Recomendado:</strong> 1.15 para la mayoría de casos. Si el modelo repite mucho, sube a 1.3.
                          </p>
                        </div>
                      </div>

                      {/* GPU Layers */}
                      <div className="ajuste-item">
                        <div className="ajuste-header">
                          <label>🎮 Capas en GPU (Aceleración)</label>
                          <span className="ajuste-valor">{ajustesAvanzados.n_gpu_layers === -1 ? 'Todas' : ajustesAvanzados.n_gpu_layers}</span>
                        </div>
                        <input 
                          type="range" 
                          min="0" 
                          max="50" 
                          step="5"
                          value={ajustesAvanzados.n_gpu_layers === -1 ? 50 : ajustesAvanzados.n_gpu_layers}
                          onChange={(e) => {
                            const val = parseInt(e.target.value);
                            setAjustesAvanzados({...ajustesAvanzados, n_gpu_layers: val === 50 ? -1 : val});
                          }}
                          onMouseUp={guardarAjustesAvanzados}
                          onTouchEnd={guardarAjustesAvanzados}
                          className="ajuste-slider"
                        />
                        <div className="ajuste-escala">
                          <span>0 (Solo CPU)</span>
                          <span>25</span>
                          <span>50 (Todas)</span>
                        </div>
                        <div className="ajuste-explicacion">
                          <p><strong>¿Qué es?</strong> Cuántas partes del modelo se cargan en tu tarjeta gráfica (GPU) para hacerlo más rápido.</p>
                          <div className="pros-cons">
                            <div className="pros">
                              <strong>✅ Más capas en GPU (30-50):</strong>
                              <ul>
                                <li>⚡ Mucho más rápido</li>
                                <li>✨ Respuestas instantáneas</li>
                                <li>🚀 Mejor para generar exámenes</li>
                              </ul>
                            </div>
                            <div className="cons">
                              <strong>⚠️ Pocas capas (0-15):</strong>
                              <ul>
                                <li>🐌 Más lento</li>
                                <li>💻 Usa CPU en lugar de GPU</li>
                                <li>⏰ Puede tardar minutos</li>
                              </ul>
                            </div>
                          </div>
                          <p className="recomendacion">
                            <strong>💡 Guía según tu GPU:</strong>
                          </p>
                          <ul style={{fontSize: '0.9rem', marginTop: '0.5rem', color: '#999'}}>
                            <li><strong>4GB VRAM:</strong> Usa 20-25 capas</li>
                            <li><strong>6GB VRAM:</strong> Usa 30-35 capas</li>
                            <li><strong>8GB+ VRAM:</strong> Usa 40-45 capas</li>
                            <li><strong>12GB+ VRAM:</strong> Usa 50 (todas las capas)</li>
                            <li><strong>Sin GPU o GPU débil:</strong> Usa 0 (solo CPU)</li>
                          </ul>
                          <p style={{fontSize: '0.85rem', color: '#ff9800', marginTop: '0.8rem'}}>
                            ⚠️ <strong>Si tu PC se congela o da error de memoria:</strong> Baja el número de capas. Empieza con 0 y sube gradualmente.
                          </p>
                        </div>
                      </div>

                      {/* Aviso de aplicación */}
                      <div style={{marginTop: '1.5rem', padding: '1rem', background: 'rgba(255, 152, 0, 0.1)', borderRadius: '8px', borderLeft: '3px solid #ff9800'}}>
                        <p style={{color: '#ffb84d', margin: 0, fontSize: '0.9rem'}}>
                          ⚠️ <strong>Nota:</strong> Estos ajustes se aplicarán la próxima vez que uses el chatbot o generes un examen. 
                          Si cambias el contexto a un valor muy alto y tu PC se congela, reinicia y bájalo de nuevo.
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Botón guardar */}
                {modelosDisponibles.length > 0 && (
                  <div className="config-actions">
                    <button 
                      onClick={guardarConfiguracion}
                      className="btn-guardar-config"
                      disabled={cargandoConfig || !modeloSeleccionado}
                    >
                      {cargandoConfig ? '⏳ Guardando...' : '💾 Guardar Configuración'}
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>

      {/* Modal para mover carpeta */}
      {modalMoverAbierto && moverCarpeta && (
        <div className="modal-overlay" onClick={cancelarMoverCarpeta}>
          <div className="modal-content modal-mover" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📦 Mover carpeta: {moverCarpeta.nombre}</h2>
              <button onClick={cancelarMoverCarpeta} className="btn-cerrar-modal">✕</button>
            </div>
            
            <div className="modal-body">
              <p className="modal-instrucciones">
                Selecciona la carpeta de destino donde quieres mover "{moverCarpeta.nombre}"
              </p>

              {/* Breadcrumb de navegación en el modal */}
              <div className="breadcrumb modal-breadcrumb">
                <button 
                  onClick={() => cargarCarpetasDestino('')} 
                  className="breadcrumb-item"
                >
                  🏠 Raíz
                </button>
                {rutaDestinoSeleccionada && rutaDestinoSeleccionada.split('\\').filter(p => p).map((parte, idx, arr) => {
                  const rutaParcial = arr.slice(0, idx + 1).join('\\')
                  return (
                    <span key={idx}>
                      <span className="breadcrumb-separator">/</span>
                      <button 
                        onClick={() => cargarCarpetasDestino(rutaParcial)}
                        className="breadcrumb-item"
                      >
                        {parte}
                      </button>
                    </span>
                  )
                })}
              </div>

              {/* Lista de carpetas disponibles */}
              <div className="carpetas-destino-lista">
                {carpetasDestino.length > 0 ? (
                  carpetasDestino
                    .filter(c => c.ruta !== moverCarpeta.ruta) // No mostrar la carpeta que se está moviendo
                    .map(carpeta => (
                      <div 
                        key={carpeta.ruta}
                        className="carpeta-destino-item"
                        onClick={() => cargarCarpetasDestino(carpeta.ruta)}
                      >
                        <div className="carpeta-destino-icon">📁</div>
                        <div className="carpeta-destino-info">
                          <h4>{carpeta.nombre}</h4>
                          <p>{carpeta.num_subcarpetas} carpetas · {carpeta.num_documentos} docs</p>
                        </div>
                        <div className="carpeta-destino-arrow">→</div>
                      </div>
                    ))
                ) : (
                  <div className="empty-state-modal">
                    <p>📭 No hay subcarpetas en esta ubicación</p>
                  </div>
                )}
              </div>

              {/* Botón para ir a carpeta padre */}
              {rutaDestinoSeleccionada && (
                <button 
                  className="btn-carpeta-padre"
                  onClick={() => {
                    const partes = rutaDestinoSeleccionada.split('\\').filter(p => p);
                    const rutaPadre = partes.slice(0, -1).join('\\');
                    cargarCarpetasDestino(rutaPadre);
                  }}
                >
                  ⬆️ Subir a carpeta padre
                </button>
              )}
            </div>

            <div className="modal-footer">
              <div className="destino-actual">
                <strong>Destino:</strong> {rutaDestinoSeleccionada || 'Raíz'}
              </div>
              <div className="modal-actions">
                <button onClick={cancelarMoverCarpeta} className="btn-modal-cancelar">
                  Cancelar
                </button>
                <button onClick={confirmarMoverCarpeta} className="btn-modal-confirmar">
                  ✓ Mover aquí
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de historial de chats */}
      {mostrarModalHistorial && (
        <div className="modal-overlay" onClick={() => setMostrarModalHistorial(false)}>
          <div className="modal-content modal-historial" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📚 Historial de Chats</h2>
              <div style={{display: 'flex', gap: '0.5rem'}}>
                <button 
                  className="btn-crear-carpeta-modal"
                  onClick={crearCarpetaHistorialModal}
                  title="Crear carpeta"
                >
                  ➕ Nueva Carpeta
                </button>
                <button onClick={() => setMostrarModalHistorial(false)} className="btn-close">✕</button>
              </div>
            </div>
            <div className="modal-body">
              {/* Breadcrumbs */}
              {rutaHistorialModal && (
                <div className="breadcrumbs-modal">
                  <button 
                    className="breadcrumb-item-modal"
                    onClick={() => cargarContenidoHistorialModal('')}
                  >
                    🏠 Inicio
                  </button>
                  {rutaHistorialModal.split(/[\\\/]/).filter(p => p).map((parte, index, arr) => {
                    const rutaParcial = arr.slice(0, index + 1).join('\\')
                    return (
                      <span key={index}>
                        <span className="breadcrumb-separator"> / </span>
                        <button 
                          className="breadcrumb-item-modal"
                          onClick={() => cargarContenidoHistorialModal(rutaParcial)}
                        >
                          📁 {parte}
                        </button>
                      </span>
                    )
                  })}
                </div>
              )}

              {/* Botón atrás */}
              {rutaHistorialModal && (
                <button 
                  className="btn-atras-modal"
                  onClick={navegarAtrasHistorialModal}
                >
                  ⬅️ Atrás
                </button>
              )}

              {loadingHistorialModal ? (
                <div className="loading-modal">Cargando...</div>
              ) : (
                <>
                  {/* Carpetas */}
                  {carpetasHistorialModal.length > 0 && (
                    <div className="seccion-carpetas-modal">
                      <h3 className="titulo-seccion-modal">📂 Carpetas</h3>
                      <div className="carpetas-grid">
                        {carpetasHistorialModal.map((carpeta, index) => (
                          <div 
                            key={index}
                            className="carpeta-card-wrapper"
                          >
                            <div 
                              className="carpeta-card"
                              onClick={() => navegarCarpetaHistorialModal(carpeta.ruta)}
                            >
                              <div className="carpeta-card-icon">📁</div>
                              <div className="carpeta-card-nombre">{carpeta.nombre}</div>
                              <div className="carpeta-stats">
                                <div className="carpeta-stat-item">
                                  <span className="stat-icon">💬</span>
                                  <span className="stat-value">{carpeta.num_chats} chat{carpeta.num_chats !== 1 ? 's' : ''}</span>
                              </div>
                            </div>
                            </div>
                            <div className="carpeta-acciones-modal">
                              <button 
                                className="btn-renombrar-carpeta-modal"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  renombrarCarpetaModal(carpeta.ruta, carpeta.nombre)
                                }}
                                title="Renombrar carpeta"
                              >
                                ✏️
                              </button>
                              <button 
                                className="btn-eliminar-carpeta-modal"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  eliminarCarpetaModal(carpeta.ruta, carpeta.nombre)
                                }}
                                title="Eliminar carpeta"
                              >
                                🗑️
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Chats */}
                  {chatsHistorialModal.length > 0 && (
                    <div className="seccion-chats-modal">
                      <h3 className="titulo-seccion-modal">💬 Chats</h3>
                      <div className="historial-lista">
                        {chatsHistorialModal.map(chat => (
                          <div key={chat.id} className="historial-item">
                            <div className="historial-info" onClick={() => cargarChatDesdeModal(chat.id)}>
                              <div className="historial-icon">💬</div>
                              <div className="historial-detalles">
                                <h4>{chat.nombre}</h4>
                                <p>{chat.num_mensajes} mensajes · {new Date(chat.fecha).toLocaleDateString()}</p>
                              </div>
                            </div>
                            <div className="historial-acciones">
                              <button 
                                className="btn-renombrar-historial"
                                onClick={() => renombrarChatModal(chat.id, chat.nombre)}
                                title="Renombrar chat"
                              >
                                ✏️
                              </button>
                              <button 
                                className="btn-eliminar-historial"
                                onClick={() => eliminarChatModal(chat.id, chat.nombre)}
                                title="Eliminar chat"
                              >
                                🗑️
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Estado vacío */}
                  {carpetasHistorialModal.length === 0 && chatsHistorialModal.length === 0 && (
                    <div className="empty-state-modal">
                      <div className="empty-icon">📭</div>
                      <p>No hay carpetas ni chats en esta ubicación</p>
                      <p className="empty-hint">Crea una carpeta para organizar tus conversaciones</p>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal para mover a carpeta */}
      {mostrarModalCarpetas && (
        <div className="modal-overlay" onClick={() => setMostrarModalCarpetas(false)}>
          <div className="modal-content modal-carpetas-visual" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📁 Mover Chat a Proyecto</h2>
              <button onClick={() => setMostrarModalCarpetas(false)} className="btn-close">✕</button>
            </div>
            <div className="modal-body">
              <p style={{color: '#b0b0c0', marginBottom: '1.5rem', fontSize: '0.95rem'}}>
                Organiza tus conversaciones por proyectos o temas
              </p>

              {/* Grid de carpetas */}
              <div className="carpetas-grid">
                {/* Opción: Sin carpeta */}
                <div 
                  className="carpeta-card sin-carpeta"
                  onClick={() => moverChatACarpeta('')}
                >
                  <div className="carpeta-card-icon">💬</div>
                  <div className="carpeta-card-content">
                    <h4>Sin Proyecto</h4>
                    <p>Mover a la raíz</p>
                  </div>
                </div>

                {/* Tarjetas de carpetas existentes */}
                {carpetasChats.map((carpeta, index) => (
                  <div 
                    key={index}
                    className="carpeta-card"
                    onClick={() => moverChatACarpeta(typeof carpeta === 'string' ? carpeta : carpeta.nombre)}
                  >
                    <div className="carpeta-card-icon">📁</div>
                    <div className="carpeta-card-content">
                      <h4>{typeof carpeta === 'string' ? carpeta : carpeta.nombre}</h4>
                      {carpeta.num_chats !== undefined && (
                        <div className="carpeta-stats">
                          <span className="stat-item">
                            💬 {carpeta.num_chats} {carpeta.num_chats === 1 ? 'chat' : 'chats'}
                          </span>
                          {carpeta.fecha_reciente && (
                            <span className="stat-item stat-fecha">
                              🕐 {new Date(carpeta.fecha_reciente).toLocaleDateString('es-ES', { 
                                day: 'numeric', 
                                month: 'short' 
                              })}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Tarjeta para crear nueva carpeta */}
                <div 
                  className="carpeta-card crear-nueva"
                  onClick={crearCarpetaChat}
                >
                  <div className="carpeta-card-icon">➕</div>
                  <div className="carpeta-card-content">
                    <h4>Nuevo Proyecto</h4>
                    <p>Crear carpeta</p>
                  </div>
                </div>
              </div>

              {carpetasChats.length === 0 && (
                <div className="carpetas-empty">
                  <p>🗂️ No tienes proyectos aún</p>
                  <p className="hint">Crea tu primer proyecto para organizar tus chats</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal de Configuración de Examen */}
      {modalConfigExamen && (
        <div className="modal-overlay" onClick={() => setModalConfigExamen(false)}>
          {console.log('🎨 Renderizando modal de configuración')}
          <div className="modal-content modal-config-examen" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>⚙️ Configurar Generación de Examen</h2>
              <button onClick={() => setModalConfigExamen(false)} className="btn-close">✕</button>
            </div>
            
            <div className="modal-body">
              {/* Prompt Personalizado */}
              <div className="config-section">
                <label className="config-label">
                  💬 Instrucciones Adicionales (opcional)
                  <span className="hint-text">Agrega instrucciones específicas que se añadirán al prompt del sistema</span>
                </label>
                <textarea
                  className="prompt-textarea"
                  placeholder="Ejemplo: Enfócate en conceptos prácticos, incluye ejemplos del mundo real..."
                  value={promptPersonalizado}
                  onChange={(e) => setPromptPersonalizado(e.target.value)}
                  rows={3}
                />
              </div>

              {/* Prompt del Sistema */}
              <div className="config-section">
                <label className="config-label">
                  🎨 Prompt del Sistema (avanzado)
                  <span className="hint-text">
                    {promptSistema 
                      ? `${promptSistema.length} caracteres cargados - Puedes editarlo libremente`
                      : 'Esperando carga... Si no aparece, usa el botón "Cargar Predeterminado"'
                    }
                  </span>
                </label>
                <div className="prompt-sistema-container">
                  <textarea
                    className="prompt-textarea prompt-sistema"
                    placeholder="Cargando prompt del sistema...&#10;&#10;Si no carga automáticamente, haz click en '🔄 Cargar Predeterminado'&#10;&#10;El prompt te permitirá personalizar completamente cómo la IA genera los exámenes."
                    value={promptSistema}
                    onChange={(e) => setPromptSistema(e.target.value)}
                    rows={12}
                  />
                  <div className="prompt-sistema-info">
                    <span className="prompt-info-text">
                      Variables: {'{contenido}'}, {'{num_multiple}'}, {'{num_corta}'}, {'{num_desarrollo}'}
                    </span>
                  </div>
                  <div className="prompt-sistema-acciones">
                    <button 
                      className="btn-cargar-template"
                      onClick={cargarPromptPredeterminado}
                    >
                      🔄 Cargar Predeterminado
                    </button>
                    <button 
                      className="btn-guardar-prompt"
                      onClick={guardarPromptSistema}
                      disabled={!promptSistema}
                    >
                      💾 Guardar Prompt
                    </button>
                  </div>
                </div>
              </div>

              {/* Explorador de Carpetas */}
              <div className="config-section">
                <label className="config-label">
                  📁 Explorar Carpetas
                  <span className="hint-text">Navega a subcarpetas para agregar más archivos</span>
                </label>
                <div className="explorador-carpetas">
                  <div className="ruta-actual">
                    {rutaExploracion !== carpetaConfigExamen?.ruta && (
                      <button 
                        className="btn-volver"
                        onClick={volverCarpetaPadre}
                      >
                        ⬅️ Volver
                      </button>
                    )}
                    <span className="ruta-texto">📂 {rutaExploracion || 'Raíz'}</span>
                  </div>
                  
                  {carpetasExploracion.length > 0 && (
                    <div className="subcarpetas-lista">
                      {carpetasExploracion.map((carpeta, idx) => (
                        <button
                          key={idx}
                          className="subcarpeta-item"
                          onClick={() => cargarArchivosSubcarpeta(carpeta.ruta)}
                        >
                          📁 {carpeta.nombre}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Lista de Archivos */}
              <div className="config-section">
                <label className="config-label">
                  📄 Archivos Seleccionados ({archivosSeleccionados.length}/{archivosDisponibles.length})
                  <span className="hint-text">Marca/desmarca los archivos que quieres incluir</span>
                </label>
                <div className="archivos-lista">
                  {archivosDisponibles.map((archivo, idx) => (
                    <label key={idx} className="archivo-item">
                      <input
                        type="checkbox"
                        checked={archivosSeleccionados.includes(archivo.ruta)}
                        onChange={() => toggleSeleccionArchivo(archivo.ruta)}
                      />
                      <div className="archivo-info">
                        <span className="archivo-nombre">📄 {archivo.nombre}</span>
                        <span className="archivo-detalles">{archivo.tamaño_kb} KB</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Configuración de Preguntas */}
              <div className="config-section">
                <label className="config-label">
                  📋 Cantidad de Preguntas
                </label>
                <div className="config-preguntas">
                  <div className="config-item">
                    <label>Opción Múltiple:</label>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={configExamen.num_multiple}
                      onChange={(e) => setConfigExamen({...configExamen, num_multiple: parseInt(e.target.value) || 0})}
                    />
                  </div>
                  <div className="config-item">
                    <label>Respuesta Corta:</label>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={configExamen.num_corta}
                      onChange={(e) => setConfigExamen({...configExamen, num_corta: parseInt(e.target.value) || 0})}
                    />
                  </div>
                  <div className="config-item">
                    <label>Desarrollo:</label>
                    <input
                      type="number"
                      min="0"
                      max="20"
                      value={configExamen.num_desarrollo}
                      onChange={(e) => setConfigExamen({...configExamen, num_desarrollo: parseInt(e.target.value) || 0})}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="btn-cancelar"
                onClick={() => setModalConfigExamen(false)}
              >
                ❌ Cancelar
              </button>
              <button 
                className="btn-generar"
                onClick={confirmarGeneracionExamen}
                disabled={archivosSeleccionados.length === 0}
              >
                ✨ Generar Examen
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Examen */}
      {modalExamenAbierto && (
        <div className="modal-overlay" onClick={cerrarExamen}>
          <div className="modal-examen" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📝 Examen - {carpetaExamen?.nombre}</h2>
              <button onClick={cerrarExamen} className="btn-close">✕</button>
            </div>
            
            <div className="modal-body examen-body">
              {!resultadoExamen ? (
                <>
                  {/* Formulario de Examen */}
                  <div className="examen-info">
                    <p>Total de preguntas: <strong>{preguntasExamen.length}</strong></p>
                    <p>Puntos totales: <strong>{preguntasExamen.reduce((sum, p) => sum + p.puntos, 0)}</strong></p>
                  </div>

                  <div className="preguntas-lista">
                    {preguntasExamen.map((pregunta, index) => (
                      <div key={index} className="pregunta-card">
                        <div className="pregunta-header">
                          <span className="pregunta-numero">Pregunta {index + 1}</span>
                          <span className="pregunta-tipo">{
                            pregunta.tipo === 'multiple' ? '📋 Selección' : 
                            pregunta.tipo === 'verdadero_falso' ? '✓✗ Verdadero/Falso' :
                            pregunta.tipo === 'corta' ? '✍️ Respuesta Corta' : 
                            '📖 Desarrollo'
                          }</span>
                          <span className="pregunta-puntos">{pregunta.puntos} pts</span>
                        </div>
                        
                        <p className="pregunta-texto">{pregunta.pregunta}</p>
                        
                        {/* Respuesta según tipo */}
                        {pregunta.tipo === 'multiple' && (
                          <div className="opciones-multiple">
                            {pregunta.opciones && pregunta.opciones.length > 0 ? (
                              pregunta.opciones.map((opcion, i) => (
                                <label key={i} className="opcion-radio">
                                  <input
                                    type="radio"
                                    name={`pregunta-${index}`}
                                    value={opcion.charAt(0)}
                                    checked={respuestasUsuario[index] === opcion.charAt(0)}
                                    onChange={(e) => actualizarRespuesta(index, e.target.value)}
                                  />
                                  <span>{opcion}</span>
                                </label>
                              ))
                            ) : (
                              <div className="opciones-no-disponibles">
                                ⚠️ Las opciones no están disponibles para este examen. 
                                Solo puedes reintentar exámenes generados recientemente.
                              </div>
                            )}
                          </div>
                        )}
                        
                        {pregunta.tipo === 'verdadero_falso' && (
                          <div className="opciones-verdadero-falso">
                            <label className="opcion-vf">
                              <input
                                type="radio"
                                name={`pregunta-${index}`}
                                value="verdadero"
                                checked={respuestasUsuario[index] === 'verdadero'}
                                onChange={(e) => actualizarRespuesta(index, e.target.value)}
                              />
                              <span className="texto-vf verdadero">✓ Verdadero</span>
                            </label>
                            <label className="opcion-vf">
                              <input
                                type="radio"
                                name={`pregunta-${index}`}
                                value="falso"
                                checked={respuestasUsuario[index] === 'falso'}
                                onChange={(e) => actualizarRespuesta(index, e.target.value)}
                              />
                              <span className="texto-vf falso">✗ Falso</span>
                            </label>
                          </div>
                        )}
                        
                        {pregunta.tipo === 'corta' && (
                          <div className="respuesta-con-voz">
                            <textarea
                              className="respuesta-corta"
                              placeholder="Escribe tu respuesta aquí (2-3 líneas)..."
                              value={respuestasUsuario[index] || ''}
                              onChange={(e) => actualizarRespuesta(index, e.target.value)}
                              rows="3"
                            />
                            <button
                              type="button"
                              className={`btn-microfono ${escuchandoPregunta === index ? 'escuchando' : ''}`}
                              onClick={() => alternarEscuchaVoz(index)}
                              title={escuchandoPregunta === index ? 'Detener grabación' : 'Responder con voz'}
                            >
                              {escuchandoPregunta === index ? '🔴' : '🎤'}
                            </button>
                            {escuchandoPregunta === index && transcripcionTemp && (
                              <div className="transcripcion-temp">
                                Escuchando: "{transcripcionTemp}"
                              </div>
                            )}
                          </div>
                        )}
                        
                        {pregunta.tipo === 'desarrollo' && (
                          <div className="respuesta-con-voz">
                            <textarea
                              className="respuesta-desarrollo"
                              placeholder="Desarrolla tu respuesta completa aquí..."
                              value={respuestasUsuario[index] || ''}
                              onChange={(e) => actualizarRespuesta(index, e.target.value)}
                              rows="8"
                            />
                            <button
                              type="button"
                              className={`btn-microfono ${escuchandoPregunta === index ? 'escuchando' : ''}`}
                              onClick={() => alternarEscuchaVoz(index)}
                              title={escuchandoPregunta === index ? 'Detener grabación' : 'Responder con voz'}
                            >
                              {escuchandoPregunta === index ? '🔴' : '🎤'}
                            </button>
                            {escuchandoPregunta === index && transcripcionTemp && (
                              <div className="transcripcion-temp">
                                Escuchando: "{transcripcionTemp}"
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  <div className="examen-info-guardado">
                    <p className="info-autosave">💾 Tus respuestas se guardan automáticamente en archivo local</p>
                    <p className="info-hint">Sobrevive al reinicio de PC. Para guardar en el servidor, haz clic en "Pausar"</p>
                  </div>

                  <div className="examen-acciones">
                    <button onClick={enviarExamen} className="btn-enviar-examen" disabled={generandoExamen}>
                      {generandoExamen ? '⏳ Calificando...' : '✅ Enviar Examen'}
                    </button>
                    <button onClick={pausarExamen} className="btn-pausar-examen">
                      ⏸️ Pausar
                    </button>
                    <button onClick={cerrarExamen} className="btn-cancelar">
                      Cancelar
                    </button>
                  </div>
                </>
              ) : (
                <>
                  {/* Resultados del Examen */}
                  <div className="resultado-header">
                    <div className="resultado-puntuacion">
                      <h3>Calificación: {resultadoExamen.puntos_obtenidos} / {resultadoExamen.puntos_totales}</h3>
                      <div className="resultado-porcentaje" style={{
                        color: resultadoExamen.porcentaje >= 70 ? '#22c55e' : resultadoExamen.porcentaje >= 50 ? '#fbbf24' : '#ef4444'
                      }}>
                        {resultadoExamen.porcentaje.toFixed(1)}%
                      </div>
                    </div>
                    
                    <div className="resultado-estado">
                      {resultadoExamen.porcentaje >= 70 ? (
                        <span className="estado-aprobado">✅ APROBADO</span>
                      ) : resultadoExamen.porcentaje >= 50 ? (
                        <span className="estado-regular">⚠️ REGULAR</span>
                      ) : (
                        <span className="estado-reprobado">❌ REPROBADO</span>
                      )}
                    </div>
                  </div>

                  <div className="resultados-detalle">
                    {resultadoExamen.resultados.map((resultado, index) => (
                      <div key={index} className="resultado-pregunta">
                        <div className="resultado-pregunta-header">
                          <span className="pregunta-numero">Pregunta {index + 1}</span>
                          <span className="resultado-puntos" style={{
                            color: resultado.puntos === resultado.puntos_maximos ? '#22c55e' : 
                                   resultado.puntos > 0 ? '#fbbf24' : '#ef4444'
                          }}>
                            {resultado.puntos} / {resultado.puntos_maximos} pts
                          </span>
                        </div>
                        
                        <p className="resultado-pregunta-texto">{resultado.pregunta}</p>
                        
                        <div className="resultado-respuesta">
                          <strong>Tu respuesta:</strong>
                          <p>{resultado.respuesta_usuario || '(Sin respuesta)'}</p>
                        </div>
                        
                        <div className="resultado-feedback" style={{
                          borderLeftColor: resultado.puntos === resultado.puntos_maximos ? '#22c55e' : 
                                          resultado.puntos > 0 ? '#fbbf24' : '#ef4444'
                        }}>
                          <strong>Retroalimentación:</strong>
                          <p>{resultado.feedback}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="examen-acciones">
                    <button onClick={reiniciarExamen} className="btn-reintentar">
                      🔄 Reintentar Examen
                    </button>
                    <button onClick={cerrarExamen} className="btn-close-resultado">
                      Cerrar
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal para Ver Resultado de Examen Completado */}
      {viendoExamen && (
        <div className="modal-overlay" onClick={() => setViendoExamen(null)}>
          <div className="modal-examen" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📊 Resultado - {viendoExamen.carpeta_nombre}</h2>
              <button onClick={() => setViendoExamen(null)} className="btn-close">✕</button>
            </div>
            
            <div className="modal-body examen-body">
              <div className="resultado-header">
                <div className="resultado-puntuacion">
                  <h3>Calificación: {viendoExamen.puntos_obtenidos} / {viendoExamen.puntos_totales}</h3>
                  <div className="resultado-porcentaje" style={{
                    color: viendoExamen.porcentaje >= 70 ? '#22c55e' : viendoExamen.porcentaje >= 50 ? '#fbbf24' : '#ef4444'
                  }}>
                    {viendoExamen.porcentaje.toFixed(1)}%
                  </div>
                </div>
                
                <div className="resultado-estado">
                  {viendoExamen.porcentaje >= 70 ? (
                    <span className="estado-aprobado">✅ APROBADO</span>
                  ) : viendoExamen.porcentaje >= 50 ? (
                    <span className="estado-regular">⚠️ REGULAR</span>
                  ) : (
                    <span className="estado-reprobado">❌ REPROBADO</span>
                  )}
                </div>
              </div>

              <div className="resultados-detalle">
                {viendoExamen.resultados.map((resultado, index) => (
                  <div key={index} className="resultado-pregunta">
                    <div className="resultado-pregunta-header">
                      <span className="pregunta-numero">Pregunta {index + 1}</span>
                      <span className="resultado-puntos" style={{
                        color: resultado.puntos === resultado.puntos_maximos ? '#22c55e' : 
                               resultado.puntos > 0 ? '#fbbf24' : '#ef4444'
                      }}>
                        {resultado.puntos} / {resultado.puntos_maximos} pts
                      </span>
                    </div>
                    
                    <p className="resultado-pregunta-texto">{resultado.pregunta}</p>
                    
                    <div className="resultado-respuesta">
                      <strong>Tu respuesta:</strong>
                      <p>{resultado.respuesta_usuario || '(Sin respuesta)'}</p>
                    </div>
                    
                    {resultado.respuesta_correcta && (
                      <div className="resultado-respuesta-correcta">
                        <strong>Respuesta correcta:</strong>
                        <p>{resultado.respuesta_correcta}</p>
                      </div>
                    )}
                    
                    <div className="resultado-feedback" style={{
                      borderLeftColor: resultado.puntos === resultado.puntos_maximos ? '#22c55e' : 
                                      resultado.puntos > 0 ? '#fbbf24' : '#ef4444'
                    }}>
                      <strong>Retroalimentación:</strong>
                      <p>{resultado.feedback}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="examen-acciones">
                <button onClick={() => setViendoExamen(null)} className="btn-close-resultado">
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App

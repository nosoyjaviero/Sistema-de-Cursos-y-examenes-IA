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
  
  // Estados para ajustes avanzados
  const [ajustesAvanzados, setAjustesAvanzados] = useState({
    n_ctx: 4096,
    temperature: 0.7,
    max_tokens: 512
  })
  const [mostrarAjustesAvanzados, setMostrarAjustesAvanzados] = useState(false)

  // Control de cancelación de peticiones
  const [abortController, setAbortController] = useState(null)

  // Estados para navegación en modal de historial
  const [rutaHistorialModal, setRutaHistorialModal] = useState('')
  const [carpetasHistorialModal, setCarpetasHistorialModal] = useState([])
  const [chatsHistorialModal, setChatsHistorialModal] = useState([])
  const [loadingHistorialModal, setLoadingHistorialModal] = useState(false)

  const API_URL = 'http://localhost:8000'

  // Auto-ocultar mensajes después de 8 segundos
  useEffect(() => {
    if (mensaje) {
      const timer = setTimeout(() => {
        setMensaje(null)
      }, 8000)
      
      return () => clearTimeout(timer)
    }
  }, [mensaje])

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
        body: JSON.stringify({ modelo_path: modeloSeleccionado })
      })

      const data = await response.json()
      if (data.success) {
        setMensaje({
          tipo: 'success',
          texto: '✅ Configuración guardada exitosamente'
        })
        setConfiguracion({ modelo_path: modeloSeleccionado })
      } else {
        setMensaje({
          tipo: 'error',
          texto: `❌ ${data.message || 'Error al guardar configuración'}`
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
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mensaje,
          contexto: contenidoContexto || null,
          buscar_web: busquedaWebActiva,
          historial: mensajesChat  // Enviar historial completo para mantener contexto
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
        contenido: data.contenido,
        tamaño_kb: data.tamaño_kb,
        lineas: data.lineas
      })
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

  // Cerrar visor
  const cerrarVisor = () => {
    setVisorAbierto(false)
    setDocumentoActual(null)
  }

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>📝 Examinator</h2>
        </div>
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${selectedMenu === 'inicio' ? 'active' : ''}`}
            onClick={() => setSelectedMenu('inicio')}
          >
            <span className="icon">🏠</span>
            Inicio
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'cursos' ? 'active' : ''}`}
            onClick={() => { setSelectedMenu('cursos'); cargarCarpeta(''); }}
          >
            <span className="icon">📚</span>
            Mis Cursos
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'generar' ? 'active' : ''}`}
            onClick={() => setSelectedMenu('generar')}
          >
            <span className="icon">✨</span>
            Generar Examen
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'historial' ? 'active' : ''}`}
            onClick={() => setSelectedMenu('historial')}
          >
            <span className="icon">📋</span>
            Historial
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'chat' ? 'active' : ''}`}
            onClick={() => setSelectedMenu('chat')}
          >
            <span className="icon">💬</span>
            Chat con IA
          </button>
          <button 
            className={`nav-item ${selectedMenu === 'configuracion' ? 'active' : ''}`}
            onClick={() => setSelectedMenu('configuracion')}
          >
            <span className="icon">⚙️</span>
            Configuración
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
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
              <h1>📁 {rutaActual ? rutaActual.split('\\').pop() || 'Mis Cursos' : 'Mis Cursos'}</h1>
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
            ) : (
              <>
                {/* Carpetas */}
                {carpetas.length > 0 && (
                  <div className="items-section">
                    <h3>📂 Carpetas</h3>
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
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>📄 {documentoActual.nombre}</h2>
                <div className="modal-info">
                  <span>{documentoActual.tamaño_kb} KB</span>
                  <span>•</span>
                  <span>{documentoActual.lineas} líneas</span>
                </div>
                <button onClick={cerrarVisor} className="btn-close">✕</button>
              </div>
              <div className="modal-body">
                <pre className="documento-contenido">{documentoActual.contenido}</pre>
              </div>
            </div>
          </div>
        )}

        {selectedMenu === 'generar' && (
          <div className="content-section">
            <h1>Generar Examen</h1>
            <p>Aquí podrás generar nuevos exámenes...</p>
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

            {!configuracion?.modelo_path ? (
              <div className="no-data">
                <p>⚠️ No hay modelo configurado</p>
                <p>Ve a Configuración y selecciona un modelo para comenzar a chatear</p>
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

                {/* Modelos disponibles */}
                <div className="config-section">
                  <h2>📂 Modelos Disponibles</h2>
                  {modelosDisponibles.length > 0 ? (
                    <div className="modelos-grid">
                      {modelosDisponibles.map(modelo => (
                        <div 
                          key={modelo.ruta}
                          className={`modelo-card ${modeloSeleccionado === modelo.ruta ? 'seleccionado' : ''}`}
                          onClick={() => setModeloSeleccionado(modelo.ruta)}
                        >
                          <div className="modelo-header">
                            <h3>🤖 {modelo.nombre}</h3>
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

                          {modeloSeleccionado === modelo.ruta && (
                            <div className="modelo-seleccionado-badge">
                              ✓ Seleccionado
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      <p>💭 No hay modelos instalados</p>
                      <p className="empty-hint">Descarga un modelo desde la sección de abajo</p>
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
                            <button 
                              className="btn-eliminar-historial"
                              onClick={() => eliminarChatModal(chat.id, chat.nombre)}
                              title="Eliminar chat"
                            >
                              🗑️
                            </button>
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
    </div>
  )
}

export default App

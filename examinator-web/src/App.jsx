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

  const API_URL = 'http://localhost:8000'

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

        {selectedMenu === 'configuracion' && (
          <div className="content-section">
            <h1>Configuración</h1>
            <p>Ajusta las preferencias de la aplicación...</p>
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
    </div>
  )
}

export default App

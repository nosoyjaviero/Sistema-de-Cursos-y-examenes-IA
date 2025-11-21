const ProgrammingCanvas = ({ value, onChange, placeholder }) => {
  return (
    <div style={{
      background: 'rgba(139, 92, 246, 0.05)',
      border: '2px solid rgba(139, 92, 246, 0.3)',
      borderRadius: '10px',
      padding: '1rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Editor de texto descriptivo */}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Describe tu diagrama de programación usando [Componentes]...\n\nEjemplo UML:\n[Clase] Usuario {+id: int, +nombre: string} {+login(), +logout()}\n[Clase] Producto {-precio: float} {+getDescuento()}\n[Herencia] Producto --|> Item\n\nEjemplo Flujo:\n[Inicio] Validar usuario\n[Proceso] Verificar credenciales\n[Decisión] ¿Usuario válido?\n[Proceso] Dar acceso\n[Fin] Terminar\n\nEjemplo Grafo:\n[Nodo] A\n[Nodo] B\n[Nodo] C\n[Arista] A --> B (peso: 5)\n[Arista] B --> C (peso: 3)\n\nEjemplo Autómata:\n[Estado Inicial] q0\n[Transición] q0 --a--> q1\n[Transición] q1 --b--> q2\n[Estado Aceptación] q2"}
        style={{
          minHeight: '250px',
          padding: '1rem',
          background: 'rgba(17, 24, 39, 0.5)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          borderRadius: '8px',
          color: '#e9d5ff',
          fontFamily: 'monospace',
          fontSize: '0.95rem',
          lineHeight: '1.6',
          resize: 'vertical',
          width: '100%'
        }}
      />

      {/* Vista previa (texto formateado) */}
      <div style={{
        background: 'rgba(17, 24, 39, 0.5)',
        border: '1px solid rgba(139, 92, 246, 0.3)',
        borderRadius: '8px',
        padding: '1rem',
        minHeight: '150px'
      }}>
        <div style={{
          fontSize: '0.85rem',
          fontWeight: '600',
          color: '#c4b5fd',
          marginBottom: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          📐 Vista Previa
        </div>
        <pre style={{
          margin: 0,
          color: '#e9d5ff',
          fontFamily: 'monospace',
          fontSize: '0.9rem',
          lineHeight: '1.8',
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word'
        }}>
          {value || '(Vacío - Comienza a escribir arriba)'}
        </pre>
      </div>

      {/* Guía rápida */}
      <div style={{
        padding: '1rem',
        background: 'rgba(139, 92, 246, 0.08)',
        borderLeft: '4px solid #8b5cf6',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#ddd6fe',
        lineHeight: '1.6'
      }}>
        <strong style={{color: '#e9d5ff'}}>💡 Formato de componentes:</strong><br/>
        
        <div style={{marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.4rem'}}>
          <div>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#c4b5fd'}}>
              [Clase] NombreClase {'{'} +atributos {'}'} {'{'} +métodos() {'}'}
            </code> - Clase UML
          </div>
          <div>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#c4b5fd'}}>
              [Decisión] ¿Condición?
            </code> - Decisión en flujo
          </div>
          <div>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#c4b5fd'}}>
              [Nodo] valor
            </code> - Nodo de grafo/árbol
          </div>
          <div>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#c4b5fd'}}>
              [Transición] q0 --a--> q1
            </code> - Transición de autómata
          </div>
          <div>
            <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px', color: '#c4b5fd'}}>
              [Paso | Acción] 1. Inicializar variables
            </code> - Tabla de algoritmo
          </div>
        </div>

        <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(139, 92, 246, 0.2)'}}>
          <strong style={{color: '#e9d5ff'}}>🎯 Categorías disponibles:</strong><br/>
          🟣 UML • 🟡 Diagramas Flujo • 🟩 Tablas Algoritmos • 🔵 Árboles/Grafos • 🟠 Autómatas
        </div>
      </div>
    </div>
  );
};

export default ProgrammingCanvas;

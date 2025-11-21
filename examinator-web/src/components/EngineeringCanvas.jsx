import { useState, useEffect } from 'react';

const EngineeringCanvas = ({ value, onChange, placeholder }) => {
  const [components, setComponents] = useState([]);
  const [textMode, setText

] = useState(value || '');

  useEffect(() => {
    setText(value || '');
  }, [value]);

  const handleTextChange = (e) => {
    const newValue = e.target.value;
    setText(newValue);
    onChange(newValue);
  };

  const addComponent = (comp) => {
    // Agregar como texto descriptivo
    const newText = textMode 
      ? textMode + '\n\n' + `[${comp.nombre}] ${comp.latex || comp.descripcion}`
      : `[${comp.nombre}] ${comp.latex || comp.descripcion}`;
    
    setText(newText);
    onChange(newText);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Editor de texto para diagrama */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <label style={{
          color: '#fca5a5',
          fontSize: '0.9rem',
          fontWeight: '600',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          Editor de Diagramas de Ingeniería
        </label>
        
        <textarea
          value={textMode}
          onChange={handleTextChange}
          placeholder={placeholder || 'Describe tu circuito, diagrama o sistema...\nEj:\n[Resistencia] R = 10Ω\n[Capacitor] C = 100μF\n[Fuente DC] V = 12V'}
          style={{
            minHeight: '250px',
            maxHeight: '450px',
            padding: '1rem',
            background: 'rgba(30, 41, 59, 0.6)',
            border: '2px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            color: '#e2e8f0',
            fontSize: '0.95rem',
            fontFamily: 'monospace',
            resize: 'vertical',
            outline: 'none',
            transition: 'border-color 0.2s',
            lineHeight: '1.6'
          }}
          onFocus={(e) => e.currentTarget.style.borderColor = '#ef4444'}
          onBlur={(e) => e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.3)'}
        />
      </div>

      {/* Vista previa (opcional) */}
      {textMode && (
        <div style={{
          padding: '1rem',
          background: 'rgba(30, 41, 59, 0.8)',
          border: '2px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          fontSize: '0.9rem',
          color: '#cbd5e1',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          lineHeight: '1.8'
        }}>
          {textMode}
        </div>
      )}

      {/* Guía de uso */}
      <div style={{
        padding: '0.75rem',
        background: 'rgba(239, 68, 68, 0.1)',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#fca5a5',
        lineHeight: '1.6'
      }}>
        <strong>📐 Cómo usar:</strong>
        <ul style={{ margin: '0.5rem 0 0 1.5rem', paddingLeft: 0 }}>
          <li><strong>Circuitos:</strong> Lista componentes (R, L, C) con valores y conexiones</li>
          <li><strong>FBD:</strong> Describe fuerzas con magnitud y dirección (↑, →, ↓, ←)</li>
          <li><strong>Vigas:</strong> Especifica apoyos, cargas y dimensiones</li>
          <li><strong>Materiales:</strong> Indica fase, temperatura, composición</li>
          <li><strong>Formato:</strong> <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>[Componente] Parámetros</code></li>
        </ul>
      </div>
    </div>
  );
};

export default EngineeringCanvas;

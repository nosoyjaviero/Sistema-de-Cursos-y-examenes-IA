import { useState, useEffect } from 'react';
import { BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

const PhysicsEditor = ({ value, onChange, placeholder }) => {
  const [latex, setLatex] = useState(value || '');

  useEffect(() => {
    setLatex(value || '');
  }, [value]);

  const handleChange = (e) => {
    const newValue = e.target.value;
    setLatex(newValue);
    onChange(newValue);
  };

  const insertLineBreak = () => {
    const newValue = latex + '\n\n';
    setLatex(newValue);
    onChange(newValue);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Editor de entrada */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <label style={{
            color: '#fbbf24',
            fontSize: '0.9rem',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            Editor LaTeX de Física
          </label>
          <button
            onClick={insertLineBreak}
            style={{
              padding: '0.4rem 0.8rem',
              background: 'rgba(245, 158, 11, 0.2)',
              border: '1px solid rgba(245, 158, 11, 0.4)',
              borderRadius: '6px',
              color: '#fbbf24',
              cursor: 'pointer',
              fontSize: '0.75rem',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '0.3rem',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(245, 158, 11, 0.3)';
              e.currentTarget.style.borderColor = '#f59e0b';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(245, 158, 11, 0.2)';
              e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.4)';
            }}
          >
            ↩ Salto de línea
          </button>
        </div>
        
        <textarea
          value={latex}
          onChange={handleChange}
          placeholder={placeholder || 'Escribe LaTeX o selecciona plantillas del panel...'}
          style={{
            minHeight: '200px',
            maxHeight: '400px',
            padding: '1rem',
            background: 'rgba(30, 41, 59, 0.6)',
            border: '2px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '8px',
            color: '#e2e8f0',
            fontSize: '0.95rem',
            fontFamily: 'monospace',
            resize: 'vertical',
            outline: 'none',
            transition: 'border-color 0.2s'
          }}
          onFocus={(e) => e.currentTarget.style.borderColor = '#f59e0b'}
          onBlur={(e) => e.currentTarget.style.borderColor = 'rgba(245, 158, 11, 0.3)'}
        />
      </div>

      {/* Vista previa renderizada */}
      {latex && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          <label style={{
            color: '#fbbf24',
            fontSize: '0.9rem',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            Vista Previa
          </label>
          <div style={{
            minHeight: '100px',
            padding: '1.5rem',
            background: 'rgba(30, 41, 59, 0.8)',
            border: '2px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '8px',
            overflowX: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem'
          }}>
            {latex.split('\n\n').map((line, idx) => (
              line.trim() && (
                <div key={idx} style={{
                  color: '#f1f5f9',
                  fontSize: '1.1rem'
                }}>
                  <BlockMath math={line.trim()} />
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Guía de ayuda */}
      <div style={{
        padding: '0.75rem',
        background: 'rgba(245, 158, 11, 0.1)',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#fcd34d',
        lineHeight: '1.6'
      }}>
        <strong>📚 Ayuda rápida:</strong>
        <ul style={{ margin: '0.5rem 0 0 1.5rem', paddingLeft: 0 }}>
          <li>Vectores: <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>\vec{'{F}'}</code></li>
          <li>Derivadas: <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>\frac{'{d}{dx}'}</code></li>
          <li>Integrales: <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>\int_{'{a}'}^{'{b}'}</code></li>
          <li>Subíndices: <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>F_{'{x}'}</code> | Superíndices: <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>x^{'{2}'}</code></li>
          <li>Griegas: <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>\alpha \beta \gamma \theta \omega \mu \epsilon</code></li>
          <li>Operadores: <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.3rem', borderRadius: '3px' }}>\nabla \cdot \times \partial \hbar</code></li>
          <li><strong>SHIFT + ENTER</strong> para salto de línea en el editor</li>
        </ul>
      </div>
    </div>
  );
};

export default PhysicsEditor;

import { useState } from 'react';
import { renderMixedContent } from '../utils/renderMixedContent';

function GeometryCanvas({ value, onChange, placeholder }) {
  const [preview, setPreview] = useState(true);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Editor de texto */}
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
            fontSize: '0.85rem',
            fontWeight: '600',
            color: '#22c55e'
          }}>
            ✍️ Editor Geométrico
          </label>
          <button
            type="button"
            onClick={() => setPreview(!preview)}
            style={{
              padding: '0.35rem 0.75rem',
              background: preview ? 'rgba(34, 197, 94, 0.2)' : 'rgba(100, 116, 139, 0.2)',
              border: '1px solid rgba(34, 197, 94, 0.3)',
              borderRadius: '6px',
              color: '#d1fae5',
              fontSize: '0.75rem',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            {preview ? '👁️ Preview ON' : '👁️ Preview OFF'}
          </button>
        </div>

        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          style={{
            width: '100%',
            minHeight: '180px',
            padding: '1rem',
            background: 'rgba(34, 197, 94, 0.05)',
            border: '2px solid rgba(34, 197, 94, 0.2)',
            borderRadius: '8px',
            color: '#d1fae5',
            fontSize: '1rem',
            fontFamily: 'monospace',
            resize: 'vertical',
            lineHeight: '1.8',
            outline: 'none'
          }}
          onFocus={(e) => e.target.style.borderColor = '#22c55e'}
          onBlur={(e) => e.target.style.borderColor = 'rgba(34, 197, 94, 0.2)'}
        />
      </div>

      {/* Vista previa */}
      {preview && value && (
        <div style={{
          padding: '1.5rem',
          background: 'rgba(34, 197, 94, 0.05)',
          border: '2px solid rgba(34, 197, 94, 0.2)',
          borderRadius: '8px',
          minHeight: '120px'
        }}>
          <div style={{
            fontSize: '0.85rem',
            fontWeight: '600',
            color: '#22c55e',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>📐</span>
            Vista Previa Geométrica
          </div>
          <div style={{
            color: '#d1fae5',
            fontSize: '1.2rem',
            lineHeight: '2',
            fontFamily: 'serif',
            whiteSpace: 'pre-wrap',
            letterSpacing: '0.3px'
          }}>
            {renderMixedContent(value)}
          </div>
        </div>
      )}

      {/* Guía de símbolos */}
      <div style={{
        padding: '1rem',
        background: 'rgba(34, 197, 94, 0.05)',
        borderRadius: '8px',
        borderLeft: '4px solid #22c55e'
      }}>
        <div style={{
          fontSize: '0.8rem',
          color: '#bbf7d0',
          lineHeight: '1.8'
        }}>
          <strong style={{color: '#22c55e', fontSize: '0.85rem'}}>📐 Guía de Símbolos Geométricos:</strong>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.5rem'}}>
            <div>
              <strong style={{color: '#22c55e'}}>Puntos:</strong> • A, • B, • C, P(x,y)<br/>
              <strong style={{color: '#22c55e'}}>Rectas:</strong> AB̅ (segmento), ↔ (recta), → (semirrecta)<br/>
              <strong style={{color: '#22c55e'}}>Ángulos:</strong> ∠ABC, π/6, π/4, π/3, 90°<br/>
              <strong style={{color: '#22c55e'}}>Relaciones:</strong> ⟂ (perpendicular), ∥ (paralelo)
            </div>
            <div>
              <strong style={{color: '#22c55e'}}>Polígonos:</strong> △ABC, □ABCD, ◊, ▱<br/>
              <strong style={{color: '#22c55e'}}>Círculos:</strong> ○ (circunferencia), r (radio), d (diámetro)<br/>
              <strong style={{color: '#22c55e'}}>Construcciones:</strong> Mediatriz, Bisectriz, Altura<br/>
              <strong style={{color: '#22c55e'}}>Trigonometría:</strong> sen θ, cos θ, tan θ, a²+b²=c²
            </div>
          </div>
          <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(34, 197, 94, 0.2)'}}>
            <strong style={{color: '#22c55e'}}>💡 Ejemplos:</strong><br/>
            • Triángulo: <code style={{background: 'rgba(34, 197, 94, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>△ABC con ∠B = 90°, a = 3, b = 4, c = 5</code><br/>
            • Ángulo: <code style={{background: 'rgba(34, 197, 94, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>∠ABC = π/4 (45°)</code><br/>
            • Segmento: <code style={{background: 'rgba(34, 197, 94, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>AB̅ = 5 cm, AB̅ ⟂ CD</code><br/>
            • Construcción: <code style={{background: 'rgba(34, 197, 94, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>[Mediatriz] AB̅ → punto M (punto medio)</code>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GeometryCanvas;

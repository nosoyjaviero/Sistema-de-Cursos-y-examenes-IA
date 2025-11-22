import { useState } from 'react';
import { renderMixedContent } from '../utils/renderMixedContent';

function AdvancedChemistryCanvas({ value, onChange, placeholder }) {
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
            color: '#a855f7'
          }}>
            ✍️ Editor de Química Avanzada
          </label>
          <button
            type="button"
            onClick={() => setPreview(!preview)}
            style={{
              padding: '0.35rem 0.75rem',
              background: preview ? 'rgba(168, 85, 247, 0.2)' : 'rgba(100, 116, 139, 0.2)',
              border: '1px solid rgba(168, 85, 247, 0.3)',
              borderRadius: '6px',
              color: '#e9d5ff',
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
            minHeight: '200px',
            padding: '1rem',
            background: 'rgba(168, 85, 247, 0.05)',
            border: '2px solid rgba(168, 85, 247, 0.2)',
            borderRadius: '8px',
            color: '#e9d5ff',
            fontSize: '1rem',
            fontFamily: 'monospace',
            resize: 'vertical',
            lineHeight: '1.8',
            outline: 'none'
          }}
          onFocus={(e) => e.target.style.borderColor = '#a855f7'}
          onBlur={(e) => e.target.style.borderColor = 'rgba(168, 85, 247, 0.2)'}
        />
      </div>

      {/* Vista previa */}
      {preview && value && (
        <div style={{
          padding: '1.5rem',
          background: 'rgba(168, 85, 247, 0.05)',
          border: '2px solid rgba(168, 85, 247, 0.2)',
          borderRadius: '8px',
          minHeight: '140px'
        }}>
          <div style={{
            fontSize: '0.85rem',
            fontWeight: '600',
            color: '#a855f7',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>🧬</span>
            Vista Previa Química Avanzada
          </div>
          <div style={{
            color: '#e9d5ff',
            fontSize: '1.15rem',
            lineHeight: '2.2',
            fontFamily: 'monospace',
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
        background: 'rgba(168, 85, 247, 0.05)',
        borderRadius: '8px',
        borderLeft: '4px solid #a855f7'
      }}>
        <div style={{
          fontSize: '0.8rem',
          color: '#ddd6fe',
          lineHeight: '1.8'
        }}>
          <strong style={{color: '#a855f7', fontSize: '0.85rem'}}>🧬 Guía de Química Avanzada:</strong>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '0.75rem'}}>
            <div>
              <strong style={{color: '#a855f7'}}>Orbitales:</strong> [1s] ○, [2px] ∞, [3dxy] ✥<br/>
              <strong style={{color: '#a855f7'}}>Hibridación:</strong> [sp] ←A→, [sp²] ⟁ A, [sp³] ⧓ A<br/>
              <strong style={{color: '#a855f7'}}>VSEPR:</strong> [AX₂], [AX₃], [AX₄], [AX₆]<br/>
              <strong style={{color: '#a855f7'}}>Movimiento e⁻:</strong> ↷ (curva), Nu:⁻ → E⁺
            </div>
            <div>
              <strong style={{color: '#a855f7'}}>Cargas:</strong> δ⁺, δ⁻, → (dipolo)<br/>
              <strong style={{color: '#a855f7'}}>MO:</strong> σ, σ*, π, π*, ↑↓ (electrones)<br/>
              <strong style={{color: '#a855f7'}}>Pares e⁻:</strong> ••, •, ⊙ (nube)<br/>
              <strong style={{color: '#a855f7'}}>Enlaces:</strong> σ, π, ═, ≡, →
            </div>
          </div>
          <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(168, 85, 247, 0.2)'}}>
            <strong style={{color: '#a855f7'}}>💡 Ejemplos:</strong><br/>
            • Hibridación: <code style={{background: 'rgba(168, 85, 247, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>[sp³] Carbono ⧓ (109.5°)</code><br/>
            • VSEPR: <code style={{background: 'rgba(168, 85, 247, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>[AX₄] Metano CH₄ tetraédrico</code><br/>
            • Mecanismo: <code style={{background: 'rgba(168, 85, 247, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>Nu:⁻ ↷ C⁺ (ataque nucleofílico)</code><br/>
            • MO: <code style={{background: 'rgba(168, 85, 247, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>[MO O₂] σ₂s ↑↓, π₂p ↑ ↑ (paramagnético)</code><br/>
            • Resonancia: <code style={{background: 'rgba(168, 85, 247, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>[Benceno] C₆H₆ ⇌ (6 estructuras)</code>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdvancedChemistryCanvas;

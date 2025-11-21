import { useState } from 'react';

function MusicCanvas({ value, onChange, placeholder }) {
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
            color: '#ec4899'
          }}>
            ✍️ Editor Musical
          </label>
          <button
            onClick={() => setPreview(!preview)}
            style={{
              padding: '0.35rem 0.75rem',
              background: preview ? 'rgba(236, 72, 153, 0.2)' : 'rgba(100, 116, 139, 0.2)',
              border: '1px solid rgba(236, 72, 153, 0.3)',
              borderRadius: '6px',
              color: '#fce7f3',
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
            background: 'rgba(236, 72, 153, 0.05)',
            border: '2px solid rgba(236, 72, 153, 0.2)',
            borderRadius: '8px',
            color: '#fce7f3',
            fontSize: '1rem',
            fontFamily: 'monospace',
            resize: 'vertical',
            lineHeight: '1.8',
            outline: 'none'
          }}
          onFocus={(e) => e.target.style.borderColor = '#ec4899'}
          onBlur={(e) => e.target.style.borderColor = 'rgba(236, 72, 153, 0.2)'}
        />
      </div>

      {/* Vista previa */}
      {preview && value && (
        <div style={{
          padding: '1.5rem',
          background: 'rgba(236, 72, 153, 0.05)',
          border: '2px solid rgba(236, 72, 153, 0.2)',
          borderRadius: '8px',
          minHeight: '120px'
        }}>
          <div style={{
            fontSize: '0.85rem',
            fontWeight: '600',
            color: '#ec4899',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>🎼</span>
            Vista Previa Musical
          </div>
          <div style={{
            color: '#fce7f3',
            fontSize: '1.3rem',
            lineHeight: '2',
            fontFamily: 'serif',
            whiteSpace: 'pre-wrap',
            letterSpacing: '0.5px'
          }}>
            {value}
          </div>
        </div>
      )}

      {/* Guía de símbolos */}
      <div style={{
        padding: '1rem',
        background: 'rgba(236, 72, 153, 0.05)',
        borderRadius: '8px',
        borderLeft: '4px solid #ec4899'
      }}>
        <div style={{
          fontSize: '0.8rem',
          color: '#fbcfe8',
          lineHeight: '1.8'
        }}>
          <strong style={{color: '#ec4899', fontSize: '0.85rem'}}>🎵 Guía de Símbolos Musicales:</strong>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.5rem'}}>
            <div>
              <strong style={{color: '#ec4899'}}>Claves:</strong> 𝄞 (Sol), 𝄢 (Fa), 𝄡 (Do)<br/>
              <strong style={{color: '#ec4899'}}>Notas:</strong> 𝅝 (redonda), 𝅗𝅥 (blanca), ♩ (negra), ♪ (corchea)<br/>
              <strong style={{color: '#ec4899'}}>Alteraciones:</strong> ♯ (sostenido), ♭ (bemol), ♮ (becuadro)
            </div>
            <div>
              <strong style={{color: '#ec4899'}}>Silencios:</strong> 𝄻 𝄼 𝄽 𝄾 𝄿<br/>
              <strong style={{color: '#ec4899'}}>Intervalos:</strong> m3, M3, P4, P5, m7, M7<br/>
              <strong style={{color: '#ec4899'}}>Progresiones:</strong> | I | IV | V | → | I |
            </div>
          </div>
          <div style={{marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(236, 72, 153, 0.2)'}}>
            <strong style={{color: '#ec4899'}}>💡 Ejemplos:</strong><br/>
            • Pentagrama: <code style={{background: 'rgba(236, 72, 153, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>𝄞 | C ♩ D ♩ E ♩ F ♩ | G 𝅗𝅥 |</code><br/>
            • Acorde: <code style={{background: 'rgba(236, 72, 153, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>Cmaj7 → Am7 → Dm7 → G7</code><br/>
            • Escala: <code style={{background: 'rgba(236, 72, 153, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>[Mayor] C-D-E-F-G-A-B-C</code><br/>
            • Progresión: <code style={{background: 'rgba(236, 72, 153, 0.15)', padding: '2px 6px', borderRadius: '4px'}}>| I | vi | IV | V | (Pop)</code>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MusicCanvas;

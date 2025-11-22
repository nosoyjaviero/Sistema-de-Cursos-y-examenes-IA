import { useState } from 'react';
import { renderMixedContent } from './utils/renderMixedContent';

/**
 * 🎲 CANVAS DE PROBABILIDAD Y ESTADÍSTICA
 * Editor con preview para elementos estadísticos
 */
export default function ProbabilityCanvas({ value, onChange }) {
  const [showPreview, setShowPreview] = useState(true);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Toggle Preview */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <label style={{
          color: '#cbd5e1',
          fontSize: '0.9rem',
          fontWeight: '600',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span>🎲</span>
          Contenido Estadístico
        </label>
        <button
          type="button"
          onClick={() => setShowPreview(!showPreview)}
          style={{
            background: showPreview ? 'rgba(139, 92, 246, 0.2)' : 'rgba(71, 85, 105, 0.3)',
            color: showPreview ? '#a78bfa' : '#94a3b8',
            border: showPreview ? '2px solid #8b5cf6' : '2px solid rgba(71, 85, 105, 0.5)',
            padding: '0.5rem 1rem',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '0.85rem',
            fontWeight: '600',
            transition: 'all 0.2s'
          }}
        >
          {showPreview ? '👁️ Vista previa ON' : '👁️ Vista previa OFF'}
        </button>
      </div>

      {/* Editor */}
      <textarea
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Haz clic en los botones de arriba para insertar árboles, diagramas de Venn, tablas, distribuciones...

Ejemplos:
• Árbol de probabilidad con ramas editables
• P(A|B) = □ (completa el valor)
• Normal: N(μ=□, σ=□)
• Tabla 2×2 de contingencia

Todos los □ son espacios para completar."
        style={{
          width: '100%',
          minHeight: '200px',
          background: 'rgba(15, 23, 42, 0.8)',
          color: '#e2e8f0',
          border: '2px solid rgba(139, 92, 246, 0.3)',
          borderRadius: '10px',
          padding: '1rem',
          fontSize: '0.95rem',
          fontFamily: 'monospace',
          lineHeight: '1.6',
          resize: 'vertical'
        }}
      />

      {/* Preview */}
      {showPreview && value && (
        <div style={{
          background: 'rgba(139, 92, 246, 0.05)',
          border: '2px solid rgba(139, 92, 246, 0.2)',
          borderRadius: '10px',
          padding: '1.5rem'
        }}>
          <div style={{
            color: '#a78bfa',
            fontSize: '0.85rem',
            fontWeight: '600',
            marginBottom: '0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <span>👁️</span>
            Vista Previa
          </div>
          <pre style={{
            color: '#e0e7ff',
            fontSize: '1.1rem',
            fontFamily: 'monospace',
            lineHeight: '2',
            whiteSpace: 'pre-wrap',
            margin: 0
          }}>
            {renderMixedContent(value)}
          </pre>
        </div>
      )}

      {/* Guía */}
      <div style={{
        background: 'rgba(139, 92, 246, 0.08)',
        padding: '1rem',
        borderRadius: '8px',
        fontSize: '0.85rem',
        color: '#c4b5fd',
        lineHeight: '1.6'
      }}>
        <strong style={{color: '#a78bfa'}}>💡 Ejemplos de uso:</strong><br/>
        <br/>
        <strong>Árbol de probabilidad:</strong><br/>
        <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
          {'    ●\n   / \\\n  □   □\n / \\ / \\\n□  □□  □'}
        </code>
        <br/><br/>
        <strong>Teorema de Bayes:</strong><br/>
        <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
          P(A|B) = P(B|A)·P(A) / P(B)
        </code>
        <br/><br/>
        <strong>Distribución Normal:</strong><br/>
        <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px'}}>
          N(μ=100, σ=15)
        </code>
        <br/><br/>
        <strong>Tabla 2×2:</strong><br/>
        <code style={{background: 'rgba(139, 92, 246, 0.2)', padding: '2px 6px', borderRadius: '4px', whiteSpace: 'pre'}}>
          {'     | Sí | No |\nH    | 20 | 30 |\nM    | 15 | 35 |'}
        </code>
      </div>
    </div>
  );
}

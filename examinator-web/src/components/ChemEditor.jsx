import { useEffect, useRef, useState } from 'react'
import SmilesDrawer from 'smiles-drawer'

/**
 * Editor Químico Interactivo
 * 
 * Permite crear estructuras químicas con:
 * - Hexágonos (anillos aromáticos)
 * - Enlaces simples, dobles, triples
 * - Átomos personalizables
 * - Grupos funcionales
 */

const ChemEditor = ({ value, onChange, placeholder = 'Estructura química...' }) => {
  const canvasRef = useRef(null)
  const [smilesDrawer] = useState(() => new SmilesDrawer.SmiDrawer({
    width: 500,
    height: 300,
    bondThickness: 2,
    bondLength: 15,
    shortBondLength: 0.85,
    bondSpacing: 0.18 * 15,
    atomVisualization: 'default',
    isomeric: true,
    debug: false,
    terminalCarbons: false,
    explicitHydrogens: false,
    themes: {
      dark: {
        C: '#e9d5ff',
        O: '#ef4444',
        N: '#3b82f6',
        F: '#10b981',
        CL: '#10b981',
        BR: '#f59e0b',
        I: '#a855f7',
        P: '#f97316',
        S: '#eab308',
        B: '#ec4899',
        SI: '#94a3b8',
        H: '#cbd5e1',
        BACKGROUND: 'rgba(30, 41, 59, 0.8)'
      }
    }
  }))

  const [inputSmiles, setInputSmiles] = useState(value || '')
  const [error, setError] = useState(null)

  useEffect(() => {
    if (canvasRef.current && inputSmiles) {
      try {
        SmilesDrawer.parse(inputSmiles, (tree) => {
          smilesDrawer.draw(tree, canvasRef.current, 'dark', false)
          setError(null)
        }, (err) => {
          setError('Estructura no válida')
          console.error('Error parsing SMILES:', err)
        })
      } catch (e) {
        setError('Error al dibujar')
        console.error('Error drawing:', e)
      }
    }
  }, [inputSmiles, smilesDrawer])

  const handleChange = (newValue) => {
    setInputSmiles(newValue)
    onChange?.(newValue)
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      {/* Input para SMILES */}
      <input
        type="text"
        value={inputSmiles}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%',
          padding: '12px 16px',
          fontSize: '14px',
          fontFamily: 'monospace',
          borderRadius: '8px',
          border: '2px solid rgba(16, 185, 129, 0.3)',
          background: 'rgba(16, 185, 129, 0.05)',
          color: '#d1fae5',
          outline: 'none'
        }}
      />

      {/* Canvas para la estructura */}
      <div style={{
        background: 'rgba(30, 41, 59, 0.8)',
        borderRadius: '8px',
        border: '2px solid rgba(16, 185, 129, 0.3)',
        padding: '1rem',
        minHeight: '300px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        {error ? (
          <div style={{ color: '#ef4444', textAlign: 'center' }}>
            {error}<br/>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
              Verifica la notación SMILES
            </span>
          </div>
        ) : inputSmiles ? (
          <canvas ref={canvasRef} />
        ) : (
          <div style={{ 
            color: '#6ee7b7', 
            textAlign: 'center',
            fontSize: '0.9rem'
          }}>
            Ingresa una estructura SMILES o usa el panel de herramientas
          </div>
        )}
      </div>
    </div>
  )
}

export default ChemEditor

import { useEffect, useRef } from 'react'
import 'mathlive'

/**
 * Editor Matemático Interactivo estilo Wolfram/Mathematica
 * 
 * Características:
 * - Plantillas visuales interactivas con cajas editables (□)
 * - Renderizado en tiempo real con MathLive
 * - Navegación con TAB entre cajas
 * - Panel de herramientas con 10 categorías
 * - Usuario NUNCA ve LaTeX crudo, solo la versión renderizada
 */

const MathEditor = ({ value, onChange, placeholder = 'Escribe matemáticas...' }) => {
  const mathFieldRef = useRef(null)

  useEffect(() => {
    if (mathFieldRef.current) {
      const mf = mathFieldRef.current

      // Configurar opciones del editor
      mf.setOptions({
        fontsDirectory: 'https://unpkg.com/mathlive/dist/fonts',
        virtualKeyboardMode: 'manual',
        smartMode: true, // Conversión automática
        smartFence: true,
        smartSuperscript: true,
        removeExtraneousParentheses: true,
        locale: 'es-ES'
      })

      // Establecer valor inicial
      if (value) {
        mf.setValue(value)
      }

      // Escuchar cambios
      const handleInput = () => {
        const latex = mf.getValue('latex')
        onChange?.(latex)
      }

      mf.addEventListener('input', handleInput)

      return () => {
        mf.removeEventListener('input', handleInput)
      }
    }
  }, [onChange])

  // Actualizar valor cuando cambia externamente
  useEffect(() => {
    if (mathFieldRef.current && value !== mathFieldRef.current.getValue('latex')) {
      mathFieldRef.current.setValue(value || '')
    }
  }, [value])

  return (
    <math-field
      ref={mathFieldRef}
      style={{
        width: '100%',
        minHeight: '200px',
        maxHeight: '400px',
        fontSize: '18px',
        padding: '16px',
        borderRadius: '8px',
        border: '2px solid rgba(147, 51, 234, 0.3)',
        background: 'rgba(147, 51, 234, 0.05)',
        color: '#e9d5ff',
        fontFamily: 'inherit',
        '--caret-color': '#a855f7',
        '--selection-background-color': 'rgba(147, 51, 234, 0.3)',
        '--placeholder-color': '#9333ea80',
        overflowY: 'auto'
      }}
    >
      {placeholder}
    </math-field>
  )
}

export default MathEditor

import { useState, useEffect, useRef } from 'react'
import katex from 'katex'
import 'katex/dist/katex.min.css'

/**
 * Botón de plantilla con renderizado KaTeX
 */
const MathButton = ({ plantilla, onClick }) => {
  const previewRef = useRef(null)

  useEffect(() => {
    if (previewRef.current) {
      try {
        katex.render(plantilla.preview, previewRef.current, {
          throwOnError: false,
          displayMode: false,
          output: 'html'
        })
      } catch (e) {
        console.error('Error renderizando KaTeX:', e)
      }
    }
  }, [plantilla.preview])

  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        background: 'rgba(147, 51, 234, 0.08)',
        border: '1px solid rgba(147, 51, 234, 0.2)',
        borderRadius: '8px',
        padding: '12px 8px',
        cursor: 'pointer',
        transition: 'all 0.2s',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '8px'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'rgba(147, 51, 234, 0.15)'
        e.currentTarget.style.borderColor = '#a855f7'
        e.currentTarget.style.transform = 'translateY(-2px)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'rgba(147, 51, 234, 0.08)'
        e.currentTarget.style.borderColor = 'rgba(147, 51, 234, 0.2)'
        e.currentTarget.style.transform = 'translateY(0)'
      }}
    >
      {/* Preview renderizado con KaTeX */}
      <div 
        ref={previewRef}
        className="katex-preview"
        style={{
          fontSize: '18px',
          color: '#e9d5ff',
          minHeight: '40px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '4px'
        }}
      />
      
      {/* Nombre */}
      <div style={{
        fontSize: '11px',
        color: '#c4b5fd',
        textAlign: 'center',
        lineHeight: '1.3'
      }}>
        {plantilla.nombre}
      </div>
    </button>
  )
}

/**
 * Panel de Herramientas Matemáticas estilo Wolfram
 * 
 * 10 categorías con plantillas listas para usar:
 * - Fracciones
 * - Potencias/Subíndices
 * - Raíces
 * - Derivadas
 * - Límites
 * - Integrales
 * - Sumatorias y Productos
 * - Matrices y Vectores
 * - Símbolos Griegos
 * - Operadores Comunes
 */

const CATEGORIAS = {
  formato: {
    nombre: 'Formato',
    icono: '⏎',
    plantillas: [
      { nombre: 'Salto de línea', latex: '\\\\', preview: '\\text{línea 1}\\\\\\text{línea 2}' },
      { nombre: 'Espacio pequeño', latex: '\\,', preview: 'a\\,b' },
      { nombre: 'Espacio mediano', latex: '\\:', preview: 'a\\:b' },
      { nombre: 'Espacio grande', latex: '\\;', preview: 'a\\;b' },
      { nombre: 'Texto normal', latex: '\\text{#?}', preview: '\\text{texto}' },
    ]
  },
  fracciones: {
    nombre: 'Fracciones',
    icono: '➗',
    plantillas: [
      { nombre: 'Fracción', latex: '\\frac{#?}{#?}', preview: '\\frac{a}{b}' },
      { nombre: 'Fracción mixta', latex: '#?\\frac{#?}{#?}', preview: '1\\frac{1}{2}' },
      { nombre: 'Binomio', latex: '\\binom{#?}{#?}', preview: '\\binom{n}{k}' },
    ]
  },
  potencias: {
    nombre: 'Potencias/Subíndices',
    icono: '𝑥²',
    plantillas: [
      { nombre: 'Potencia', latex: '#?^{#?}', preview: 'x^{2}' },
      { nombre: 'Subíndice', latex: '#?_{#?}', preview: 'a_{n}' },
      { nombre: 'Potencia y subíndice', latex: '#?_{#?}^{#?}', preview: 'x_{i}^{2}' },
      { nombre: 'Exponencial', latex: 'e^{#?}', preview: 'e^{x}' },
    ]
  },
  raices: {
    nombre: 'Raíces',
    icono: '√',
    plantillas: [
      { nombre: 'Raíz cuadrada', latex: '\\sqrt{#?}', preview: '\\sqrt{x}' },
      { nombre: 'Raíz n-ésima', latex: '\\sqrt[#?]{#?}', preview: '\\sqrt[3]{x}' },
      { nombre: 'Raíz cúbica', latex: '\\sqrt[3]{#?}', preview: '\\sqrt[3]{27}' },
    ]
  },
  derivadas: {
    nombre: 'Derivadas',
    icono: "f'",
    plantillas: [
      { nombre: 'Derivada', latex: '\\frac{d}{dx}#?', preview: '\\frac{d}{dx}f(x)' },
      { nombre: 'Derivada parcial', latex: '\\frac{\\partial}{\\partial #?}#?', preview: '\\frac{\\partial}{\\partial x}f' },
      { nombre: 'Derivada de orden n', latex: '\\frac{d^{#?}}{dx^{#?}}#?', preview: '\\frac{d^{2}}{dx^{2}}f' },
      { nombre: 'Notación prima', latex: "#?'", preview: "f'" },
      { nombre: 'Notación de Leibniz', latex: '\\frac{d#?}{d#?}', preview: '\\frac{dy}{dx}' },
    ]
  },
  limites: {
    nombre: 'Límites',
    icono: 'lim',
    plantillas: [
      { nombre: 'Límite', latex: '\\lim_{#?\\to#?}#?', preview: '\\lim_{x\\to\\infty}f(x)' },
      { nombre: 'Límite bilateral', latex: '\\lim_{#?\\to#?^{\\pm}}#?', preview: '\\lim_{x\\to 0^{+}}f(x)' },
      { nombre: 'Límite superior', latex: '\\limsup_{#?\\to#?}#?', preview: '\\limsup_{n\\to\\infty}a_n' },
      { nombre: 'Límite inferior', latex: '\\liminf_{#?\\to#?}#?', preview: '\\liminf_{n\\to\\infty}a_n' },
    ]
  },
  integrales: {
    nombre: 'Integrales',
    icono: '∫',
    plantillas: [
      { nombre: 'Integral indefinida', latex: '\\int #?\\,d#?', preview: '\\int f(x)\\,dx' },
      { nombre: 'Integral definida', latex: '\\int_{#?}^{#?}#?\\,d#?', preview: '\\int_{a}^{b}f(x)\\,dx' },
      { nombre: 'Integral doble', latex: '\\iint_{#?}#?\\,dA', preview: '\\iint_{D}f(x,y)\\,dA' },
      { nombre: 'Integral triple', latex: '\\iiint_{#?}#?\\,dV', preview: '\\iiint_{V}f\\,dV' },
      { nombre: 'Integral de contorno', latex: '\\oint_{#?}#?\\,d#?', preview: '\\oint_{C}F\\,ds' },
    ]
  },
  sumatorias: {
    nombre: 'Sumatorias y Productos',
    icono: '∑',
    plantillas: [
      { nombre: 'Sumatoria', latex: '\\sum_{#?}^{#?}#?', preview: '\\sum_{i=1}^{n}i' },
      { nombre: 'Productoria', latex: '\\prod_{#?}^{#?}#?', preview: '\\prod_{i=1}^{n}i' },
      { nombre: 'Coproducto', latex: '\\coprod_{#?}^{#?}#?', preview: '\\coprod_{i=1}^{n}X_i' },
      { nombre: 'Unión', latex: '\\bigcup_{#?}^{#?}#?', preview: '\\bigcup_{i=1}^{n}A_i' },
      { nombre: 'Intersección', latex: '\\bigcap_{#?}^{#?}#?', preview: '\\bigcap_{i=1}^{n}A_i' },
    ]
  },
  matrices: {
    nombre: 'Matrices y Vectores',
    icono: '⎡⎤',
    plantillas: [
      { nombre: 'Matriz 2×2', latex: '\\begin{pmatrix}#?&#?\\\\#?&#?\\end{pmatrix}', preview: '\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}' },
      { nombre: 'Matriz 3×3', latex: '\\begin{pmatrix}#?&#?&#?\\\\#?&#?&#?\\\\#?&#?&#?\\end{pmatrix}', preview: '\\begin{pmatrix}1&0&0\\\\0&1&0\\\\0&0&1\\end{pmatrix}' },
      { nombre: 'Determinante', latex: '\\begin{vmatrix}#?&#?\\\\#?&#?\\end{vmatrix}', preview: '\\begin{vmatrix}a&b\\\\c&d\\end{vmatrix}' },
      { nombre: 'Vector columna', latex: '\\begin{bmatrix}#?\\\\#?\\\\#?\\end{bmatrix}', preview: '\\begin{bmatrix}x\\\\y\\\\z\\end{bmatrix}' },
      { nombre: 'Vector fila', latex: '\\begin{bmatrix}#?&#?&#?\\end{bmatrix}', preview: '\\begin{bmatrix}1&2&3\\end{bmatrix}' },
    ]
  },
  griegos: {
    nombre: 'Símbolos Griegos',
    icono: 'αβγ',
    plantillas: [
      { nombre: 'α (alpha)', latex: '\\alpha', preview: '\\alpha' },
      { nombre: 'β (beta)', latex: '\\beta', preview: '\\beta' },
      { nombre: 'γ (gamma)', latex: '\\gamma', preview: '\\gamma' },
      { nombre: 'δ (delta)', latex: '\\delta', preview: '\\delta' },
      { nombre: 'ε (epsilon)', latex: '\\epsilon', preview: '\\epsilon' },
      { nombre: 'θ (theta)', latex: '\\theta', preview: '\\theta' },
      { nombre: 'λ (lambda)', latex: '\\lambda', preview: '\\lambda' },
      { nombre: 'μ (mu)', latex: '\\mu', preview: '\\mu' },
      { nombre: 'π (pi)', latex: '\\pi', preview: '\\pi' },
      { nombre: 'σ (sigma)', latex: '\\sigma', preview: '\\sigma' },
      { nombre: 'φ (phi)', latex: '\\phi', preview: '\\phi' },
      { nombre: 'ω (omega)', latex: '\\omega', preview: '\\omega' },
      { nombre: 'Δ (Delta)', latex: '\\Delta', preview: '\\Delta' },
      { nombre: 'Θ (Theta)', latex: '\\Theta', preview: '\\Theta' },
      { nombre: 'Σ (Sigma)', latex: '\\Sigma', preview: '\\Sigma' },
      { nombre: 'Ω (Omega)', latex: '\\Omega', preview: '\\Omega' },
    ]
  },
  operadores: {
    nombre: 'Operadores',
    icono: '±×',
    plantillas: [
      { nombre: '±', latex: '\\pm', preview: '\\pm' },
      { nombre: '∓', latex: '\\mp', preview: '\\mp' },
      { nombre: '×', latex: '\\times', preview: '\\times' },
      { nombre: '÷', latex: '\\div', preview: '\\div' },
      { nombre: '≤', latex: '\\leq', preview: '\\leq' },
      { nombre: '≥', latex: '\\geq', preview: '\\geq' },
      { nombre: '≠', latex: '\\neq', preview: '\\neq' },
      { nombre: '≈', latex: '\\approx', preview: '\\approx' },
      { nombre: '∞', latex: '\\infty', preview: '\\infty' },
      { nombre: '∈', latex: '\\in', preview: '\\in' },
      { nombre: '∉', latex: '\\notin', preview: '\\notin' },
      { nombre: '⊂', latex: '\\subset', preview: '\\subset' },
      { nombre: '∪', latex: '\\cup', preview: '\\cup' },
      { nombre: '∩', latex: '\\cap', preview: '\\cap' },
      { nombre: '→', latex: '\\to', preview: '\\to' },
      { nombre: '⇒', latex: '\\Rightarrow', preview: '\\Rightarrow' },
      { nombre: '⇔', latex: '\\Leftrightarrow', preview: '\\Leftrightarrow' },
      { nombre: '∀', latex: '\\forall', preview: '\\forall' },
      { nombre: '∃', latex: '\\exists', preview: '\\exists' },
      { nombre: '∇', latex: '\\nabla', preview: '\\nabla' },
    ]
  }
}

const MathToolbar = ({ onInsertTemplate }) => {
  const [categoriaActiva, setCategoriaActiva] = useState('fracciones')

  const handleInsert = (latex) => {
    onInsertTemplate(latex)
  }

  return (
    <div style={{
      background: 'rgba(17, 24, 39, 0.95)',
      border: '1px solid rgba(147, 51, 234, 0.3)',
      borderRadius: '12px',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      height: '100%'
    }}>
      {/* Tabs de categorías */}
      <div style={{
        display: 'flex',
        gap: '4px',
        padding: '12px',
        borderBottom: '1px solid rgba(147, 51, 234, 0.2)',
        overflowX: 'auto',
        flexWrap: 'wrap'
      }}>
        {Object.entries(CATEGORIAS_MATH).map(([key, cat]) => (
          <button
            type="button"
            key={key}
            onClick={() => setCategoriaActiva(key)}
            style={{
              padding: '8px 16px',
              background: categoriaActiva === key 
                ? 'linear-gradient(135deg, #9333ea, #7c3aed)' 
                : 'rgba(147, 51, 234, 0.1)',
              color: categoriaActiva === key ? '#fff' : '#c4b5fd',
              border: categoriaActiva === key 
                ? '1px solid #a855f7' 
                : '1px solid rgba(147, 51, 234, 0.2)',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: categoriaActiva === key ? '600' : '500',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap'
            }}
            onMouseEnter={(e) => {
              if (categoriaActiva !== key) {
                e.target.style.background = 'rgba(147, 51, 234, 0.2)'
              }
            }}
            onMouseLeave={(e) => {
              if (categoriaActiva !== key) {
                e.target.style.background = 'rgba(147, 51, 234, 0.1)'
              }
            }}
          >
            <span style={{ marginRight: '6px' }}>{cat.icono}</span>
            {cat.nombre}
          </button>
        ))}
      </div>

      {/* Grid de plantillas */}
      <div style={{
        padding: '16px',
        overflowY: 'auto',
        flex: 1
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
          gap: '12px'
        }}>
          {CATEGORIAS[categoriaActiva]?.plantillas.map((plantilla, idx) => (
            <MathButton
              key={idx}
              plantilla={plantilla}
              onClick={() => handleInsert(plantilla.latex)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default MathToolbar

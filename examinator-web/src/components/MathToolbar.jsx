import { useState, useEffect, useRef } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

/**
 * Botón de plantilla con renderizado KaTeX
 */
const MathButton = ({ plantilla, onClick }) => {
  const previewRef = useRef(null);

  useEffect(() => {
    if (previewRef.current) {
      try {
        katex.render(plantilla.preview, previewRef.current, {
          throwOnError: false,
          displayMode: false,
          output: "html",
        });
      } catch (e) {
        console.error("Error renderizando KaTeX:", e);
      }
    }
  }, [plantilla.preview]);

  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        background: "rgba(147, 51, 234, 0.08)",
        border: "1px solid rgba(147, 51, 234, 0.2)",
        borderRadius: "8px",
        padding: "12px 8px",
        cursor: "pointer",
        transition: "all 0.2s",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "8px",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "rgba(147, 51, 234, 0.15)";
        e.currentTarget.style.borderColor = "#a855f7";
        e.currentTarget.style.transform = "translateY(-2px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "rgba(147, 51, 234, 0.08)";
        e.currentTarget.style.borderColor = "rgba(147, 51, 234, 0.2)";
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      {/* Preview renderizado con KaTeX */}
      <div
        ref={previewRef}
        className="katex-preview"
        style={{
          fontSize: "18px",
          color: "#e9d5ff",
          minHeight: "40px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "4px",
        }}
      />

      {/* Nombre */}
      <div
        style={{
          fontSize: "11px",
          color: "#c4b5fd",
          textAlign: "center",
          lineHeight: "1.3",
        }}
      >
        {plantilla.nombre}
      </div>
    </button>
  );
};

/**
 * Panel de Herramientas Matemáticas Completo
 *
 * Cobertura: Precálculo → Cálculo I/II/III → Cálculo Superior
 * 20+ categorías con 300+ plantillas
 */

const CATEGORIAS = {
  // === BÁSICO Y FORMATO ===
  formato: {
    nombre: "Formato",
    icono: "⏎",
    plantillas: [
      {
        nombre: "Salto de línea",
        latex: "\\\\",
        preview: "\\text{línea 1}\\\\\\text{línea 2}",
      },
      { nombre: "Espacio pequeño", latex: "\\,", preview: "a\\,b" },
      { nombre: "Espacio mediano", latex: "\\:", preview: "a\\:b" },
      { nombre: "Espacio grande", latex: "\\;", preview: "a\\;b" },
      { nombre: "Texto normal", latex: "\\text{#?}", preview: "\\text{texto}" },
      {
        nombre: "Paréntesis auto",
        latex: "\\left(#?\\right)",
        preview: "\\left(\\frac{a}{b}\\right)",
      },
      {
        nombre: "Corchetes auto",
        latex: "\\left[#?\\right]",
        preview: "\\left[\\frac{a}{b}\\right]",
      },
      {
        nombre: "Llaves auto",
        latex: "\\left\\{#?\\right\\}",
        preview: "\\left\\{x\\right\\}",
      },
      {
        nombre: "Valor absoluto",
        latex: "\\left|#?\\right|",
        preview: "\\left|x\\right|",
      },
      {
        nombre: "Norma",
        latex: "\\left\\|#?\\right\\|",
        preview: "\\left\\|v\\right\\|",
      },
      {
        nombre: "Techo",
        latex: "\\lceil#?\\rceil",
        preview: "\\lceil x \\rceil",
      },
      {
        nombre: "Piso",
        latex: "\\lfloor#?\\rfloor",
        preview: "\\lfloor x \\rfloor",
      },
    ],
  },

  // === ARITMÉTICA Y ÁLGEBRA ===
  fracciones: {
    nombre: "Fracciones",
    icono: "➗",
    plantillas: [
      {
        nombre: "Fracción simple",
        latex: "\\frac{#?}{#?}",
        preview: "\\frac{a}{b}",
      },
      {
        nombre: "Fracción mixta",
        latex: "#?\\frac{#?}{#?}",
        preview: "1\\frac{1}{2}",
      },
      {
        nombre: "Fracción pequeña",
        latex: "\\tfrac{#?}{#?}",
        preview: "\\tfrac{1}{2}",
      },
      {
        nombre: "Fracción grande",
        latex: "\\dfrac{#?}{#?}",
        preview: "\\dfrac{a}{b}",
      },
      {
        nombre: "Fracción continua",
        latex: "\\cfrac{#?}{#?}",
        preview: "\\cfrac{1}{1+\\cfrac{1}{2}}",
      },
      { nombre: "Binomio", latex: "\\binom{#?}{#?}", preview: "\\binom{n}{k}" },
      {
        nombre: "Coef. binomial",
        latex: "\\dbinom{#?}{#?}",
        preview: "\\dbinom{n}{r}",
      },
    ],
  },
  potencias: {
    nombre: "Potencias",
    icono: "x²",
    plantillas: [
      { nombre: "Potencia", latex: "#?^{#?}", preview: "x^{2}" },
      { nombre: "Subíndice", latex: "#?_{#?}", preview: "a_{n}" },
      {
        nombre: "Potencia y subíndice",
        latex: "#?_{#?}^{#?}",
        preview: "x_{i}^{2}",
      },
      { nombre: "Exponencial e^x", latex: "e^{#?}", preview: "e^{x}" },
      { nombre: "Exponencial a^x", latex: "#?^{#?}", preview: "a^{x}" },
      { nombre: "10 elevado", latex: "10^{#?}", preview: "10^{n}" },
      { nombre: "Factorial", latex: "#?!", preview: "n!" },
      { nombre: "Doble factorial", latex: "#?!!", preview: "n!!" },
    ],
  },
  raices: {
    nombre: "Raíces",
    icono: "√",
    plantillas: [
      { nombre: "Raíz cuadrada", latex: "\\sqrt{#?}", preview: "\\sqrt{x}" },
      {
        nombre: "Raíz cúbica",
        latex: "\\sqrt[3]{#?}",
        preview: "\\sqrt[3]{x}",
      },
      {
        nombre: "Raíz n-ésima",
        latex: "\\sqrt[#?]{#?}",
        preview: "\\sqrt[n]{x}",
      },
      {
        nombre: "Raíz cuarta",
        latex: "\\sqrt[4]{#?}",
        preview: "\\sqrt[4]{x}",
      },
      { nombre: "Raíz con exponente", latex: "#?^{1/#?}", preview: "x^{1/n}" },
      {
        nombre: "Raíz compleja",
        latex: "\\sqrt{#?+#?i}",
        preview: "\\sqrt{a+bi}",
      },
    ],
  },

  // === TRIGONOMETRÍA ===
  trigonometria: {
    nombre: "Trigonometría",
    icono: "sin",
    plantillas: [
      // Funciones básicas
      { nombre: "Seno", latex: "\\sin(#?)", preview: "\\sin(x)" },
      { nombre: "Coseno", latex: "\\cos(#?)", preview: "\\cos(x)" },
      { nombre: "Tangente", latex: "\\tan(#?)", preview: "\\tan(x)" },
      { nombre: "Cotangente", latex: "\\cot(#?)", preview: "\\cot(x)" },
      { nombre: "Secante", latex: "\\sec(#?)", preview: "\\sec(x)" },
      { nombre: "Cosecante", latex: "\\csc(#?)", preview: "\\csc(x)" },
      // Sin paréntesis
      { nombre: "sin θ", latex: "\\sin\\theta", preview: "\\sin\\theta" },
      { nombre: "cos θ", latex: "\\cos\\theta", preview: "\\cos\\theta" },
      { nombre: "tan θ", latex: "\\tan\\theta", preview: "\\tan\\theta" },
      // Cuadrados
      { nombre: "sin²", latex: "\\sin^{2}(#?)", preview: "\\sin^{2}(x)" },
      { nombre: "cos²", latex: "\\cos^{2}(#?)", preview: "\\cos^{2}(x)" },
      { nombre: "tan²", latex: "\\tan^{2}(#?)", preview: "\\tan^{2}(x)" },
    ],
  },
  trigonometriaInversa: {
    nombre: "Trig. Inversas",
    icono: "arc",
    plantillas: [
      { nombre: "Arcoseno", latex: "\\arcsin(#?)", preview: "\\arcsin(x)" },
      { nombre: "Arcocoseno", latex: "\\arccos(#?)", preview: "\\arccos(x)" },
      { nombre: "Arcotangente", latex: "\\arctan(#?)", preview: "\\arctan(x)" },
      { nombre: "sin⁻¹", latex: "\\sin^{-1}(#?)", preview: "\\sin^{-1}(x)" },
      { nombre: "cos⁻¹", latex: "\\cos^{-1}(#?)", preview: "\\cos^{-1}(x)" },
      { nombre: "tan⁻¹", latex: "\\tan^{-1}(#?)", preview: "\\tan^{-1}(x)" },
      {
        nombre: "arccot",
        latex: "\\text{arccot}(#?)",
        preview: "\\text{arccot}(x)",
      },
      {
        nombre: "arcsec",
        latex: "\\text{arcsec}(#?)",
        preview: "\\text{arcsec}(x)",
      },
      {
        nombre: "arccsc",
        latex: "\\text{arccsc}(#?)",
        preview: "\\text{arccsc}(x)",
      },
    ],
  },
  hiperbolicas: {
    nombre: "Hiperbólicas",
    icono: "sinh",
    plantillas: [
      { nombre: "Seno hiperbólico", latex: "\\sinh(#?)", preview: "\\sinh(x)" },
      {
        nombre: "Coseno hiperbólico",
        latex: "\\cosh(#?)",
        preview: "\\cosh(x)",
      },
      {
        nombre: "Tangente hiperbólica",
        latex: "\\tanh(#?)",
        preview: "\\tanh(x)",
      },
      { nombre: "Cotangente hip.", latex: "\\coth(#?)", preview: "\\coth(x)" },
      {
        nombre: "Secante hip.",
        latex: "\\text{sech}(#?)",
        preview: "\\text{sech}(x)",
      },
      {
        nombre: "Cosecante hip.",
        latex: "\\text{csch}(#?)",
        preview: "\\text{csch}(x)",
      },
      // Inversas hiperbólicas
      {
        nombre: "arcsinh",
        latex: "\\text{arcsinh}(#?)",
        preview: "\\text{arcsinh}(x)",
      },
      {
        nombre: "arccosh",
        latex: "\\text{arccosh}(#?)",
        preview: "\\text{arccosh}(x)",
      },
      {
        nombre: "arctanh",
        latex: "\\text{arctanh}(#?)",
        preview: "\\text{arctanh}(x)",
      },
    ],
  },

  // === LOGARITMOS Y EXPONENCIALES ===
  logaritmos: {
    nombre: "Logaritmos",
    icono: "log",
    plantillas: [
      { nombre: "Log natural", latex: "\\ln(#?)", preview: "\\ln(x)" },
      { nombre: "Log base 10", latex: "\\log(#?)", preview: "\\log(x)" },
      {
        nombre: "Log base n",
        latex: "\\log_{#?}(#?)",
        preview: "\\log_{a}(x)",
      },
      { nombre: "Log base 2", latex: "\\log_{2}(#?)", preview: "\\log_{2}(x)" },
      { nombre: "e^x", latex: "e^{#?}", preview: "e^{x}" },
      { nombre: "exp(x)", latex: "\\exp(#?)", preview: "\\exp(x)" },
      { nombre: "a^x", latex: "#?^{#?}", preview: "a^{x}" },
      { nombre: "ln(e^x)", latex: "\\ln(e^{#?})", preview: "\\ln(e^{x})" },
      { nombre: "e^(ln x)", latex: "e^{\\ln(#?)}", preview: "e^{\\ln(x)}" },
    ],
  },

  // === CÁLCULO DIFERENCIAL ===
  derivadas: {
    nombre: "Derivadas",
    icono: "f'",
    plantillas: [
      {
        nombre: "d/dx",
        latex: "\\frac{d}{dx}#?",
        preview: "\\frac{d}{dx}f(x)",
      },
      { nombre: "dy/dx", latex: "\\frac{dy}{dx}", preview: "\\frac{dy}{dx}" },
      {
        nombre: "Derivada parcial",
        latex: "\\frac{\\partial #?}{\\partial #?}",
        preview: "\\frac{\\partial f}{\\partial x}",
      },
      {
        nombre: "∂f/∂x",
        latex: "\\frac{\\partial f}{\\partial x}",
        preview: "\\frac{\\partial f}{\\partial x}",
      },
      {
        nombre: "Segunda derivada",
        latex: "\\frac{d^{2}#?}{dx^{2}}",
        preview: "\\frac{d^{2}y}{dx^{2}}",
      },
      {
        nombre: "Derivada n-ésima",
        latex: "\\frac{d^{#?}#?}{dx^{#?}}",
        preview: "\\frac{d^{n}y}{dx^{n}}",
      },
      { nombre: "f'(x)", latex: "f'(#?)", preview: "f'(x)" },
      { nombre: "f''(x)", latex: "f''(#?)", preview: "f''(x)" },
      { nombre: "f'''(x)", latex: "f'''(#?)", preview: "f'''(x)" },
      { nombre: "f⁽ⁿ⁾(x)", latex: "f^{(#?)}(#?)", preview: "f^{(n)}(x)" },
      { nombre: "Diferencial df", latex: "df", preview: "df" },
      { nombre: "Diferencial dx", latex: "dx", preview: "dx" },
      { nombre: "Δx", latex: "\\Delta x", preview: "\\Delta x" },
      {
        nombre: "Jacobiano",
        latex: "\\frac{\\partial(#?,#?)}{\\partial(#?,#?)}",
        preview: "\\frac{\\partial(u,v)}{\\partial(x,y)}",
      },
    ],
  },
  limites: {
    nombre: "Límites",
    icono: "lim",
    plantillas: [
      {
        nombre: "Límite",
        latex: "\\lim_{#?\\to#?}#?",
        preview: "\\lim_{x\\to a}f(x)",
      },
      {
        nombre: "Límite infinito",
        latex: "\\lim_{#?\\to\\infty}#?",
        preview: "\\lim_{x\\to\\infty}f(x)",
      },
      {
        nombre: "Límite -∞",
        latex: "\\lim_{#?\\to-\\infty}#?",
        preview: "\\lim_{x\\to-\\infty}f(x)",
      },
      {
        nombre: "Límite derecha",
        latex: "\\lim_{#?\\to#?^{+}}#?",
        preview: "\\lim_{x\\to a^{+}}f(x)",
      },
      {
        nombre: "Límite izquierda",
        latex: "\\lim_{#?\\to#?^{-}}#?",
        preview: "\\lim_{x\\to a^{-}}f(x)",
      },
      {
        nombre: "Límite 0⁺",
        latex: "\\lim_{#?\\to 0^{+}}#?",
        preview: "\\lim_{x\\to 0^{+}}f(x)",
      },
      {
        nombre: "Límite 0⁻",
        latex: "\\lim_{#?\\to 0^{-}}#?",
        preview: "\\lim_{x\\to 0^{-}}f(x)",
      },
      {
        nombre: "lim sup",
        latex: "\\limsup_{#?\\to#?}#?",
        preview: "\\limsup_{n\\to\\infty}a_n",
      },
      {
        nombre: "lim inf",
        latex: "\\liminf_{#?\\to#?}#?",
        preview: "\\liminf_{n\\to\\infty}a_n",
      },
    ],
  },

  // === CÁLCULO INTEGRAL ===
  integrales: {
    nombre: "Integrales",
    icono: "∫",
    plantillas: [
      {
        nombre: "Integral indefinida",
        latex: "\\int #?\\,d#?",
        preview: "\\int f(x)\\,dx",
      },
      {
        nombre: "Integral definida",
        latex: "\\int_{#?}^{#?}#?\\,d#?",
        preview: "\\int_{a}^{b}f(x)\\,dx",
      },
      {
        nombre: "Integral evaluada",
        latex: "\\left[#?\\right]_{#?}^{#?}",
        preview: "\\left[F(x)\\right]_{a}^{b}",
      },
      {
        nombre: "Integral doble",
        latex: "\\iint_{#?}#?\\,dA",
        preview: "\\iint_{D}f\\,dA",
      },
      {
        nombre: "Integral triple",
        latex: "\\iiint_{#?}#?\\,dV",
        preview: "\\iiint_{V}f\\,dV",
      },
      {
        nombre: "Integral de línea",
        latex: "\\int_{#?}#?\\,ds",
        preview: "\\int_{C}F\\,ds",
      },
      {
        nombre: "Integral cerrada",
        latex: "\\oint_{#?}#?\\,d#?",
        preview: "\\oint_{C}F\\,ds",
      },
      {
        nombre: "Integral superficie",
        latex: "\\iint_{#?}#?\\,dS",
        preview: "\\iint_{S}F\\,dS",
      },
      {
        nombre: "Integral impropia",
        latex: "\\int_{#?}^{\\infty}#?\\,d#?",
        preview: "\\int_{0}^{\\infty}f\\,dx",
      },
    ],
  },

  // === SERIES Y SUCESIONES ===
  series: {
    nombre: "Series",
    icono: "∑",
    plantillas: [
      {
        nombre: "Sumatoria",
        latex: "\\sum_{#?}^{#?}#?",
        preview: "\\sum_{i=1}^{n}a_i",
      },
      {
        nombre: "Sumatoria infinita",
        latex: "\\sum_{#?}^{\\infty}#?",
        preview: "\\sum_{n=0}^{\\infty}a_n",
      },
      {
        nombre: "Productoria",
        latex: "\\prod_{#?}^{#?}#?",
        preview: "\\prod_{i=1}^{n}a_i",
      },
      {
        nombre: "Serie de Taylor",
        latex: "\\sum_{n=0}^{\\infty}\\frac{f^{(n)}(a)}{n!}(x-a)^n",
        preview: "\\sum_{n=0}^{\\infty}\\frac{f^{(n)}(a)}{n!}(x-a)^n",
      },
      {
        nombre: "Serie Maclaurin",
        latex: "\\sum_{n=0}^{\\infty}\\frac{f^{(n)}(0)}{n!}x^n",
        preview: "\\sum_{n=0}^{\\infty}\\frac{f^{(n)}(0)}{n!}x^n",
      },
      {
        nombre: "Serie geométrica",
        latex: "\\sum_{n=0}^{\\infty}ar^n",
        preview: "\\sum_{n=0}^{\\infty}ar^n",
      },
      {
        nombre: "Serie potencias",
        latex: "\\sum_{n=0}^{\\infty}c_n(x-a)^n",
        preview: "\\sum_{n=0}^{\\infty}c_n(x-a)^n",
      },
      {
        nombre: "Sucesión",
        latex: "\\{a_n\\}_{n=#?}^{#?}",
        preview: "\\{a_n\\}_{n=1}^{\\infty}",
      },
      { nombre: "Convergencia", latex: "a_n\\to#?", preview: "a_n\\to L" },
    ],
  },

  // === ÁLGEBRA LINEAL ===
  matrices: {
    nombre: "Matrices",
    icono: "⎡⎤",
    plantillas: [
      {
        nombre: "Matriz 2×2",
        latex: "\\begin{pmatrix}#?&#?\\\\#?&#?\\end{pmatrix}",
        preview: "\\begin{pmatrix}a&b\\\\c&d\\end{pmatrix}",
      },
      {
        nombre: "Matriz 3×3",
        latex: "\\begin{pmatrix}#?&#?&#?\\\\#?&#?&#?\\\\#?&#?&#?\\end{pmatrix}",
        preview: "\\begin{pmatrix}a&b&c\\\\d&e&f\\\\g&h&i\\end{pmatrix}",
      },
      {
        nombre: "Matriz corchetes",
        latex: "\\begin{bmatrix}#?&#?\\\\#?&#?\\end{bmatrix}",
        preview: "\\begin{bmatrix}a&b\\\\c&d\\end{bmatrix}",
      },
      {
        nombre: "Determinante",
        latex: "\\begin{vmatrix}#?&#?\\\\#?&#?\\end{vmatrix}",
        preview: "\\begin{vmatrix}a&b\\\\c&d\\end{vmatrix}",
      },
      {
        nombre: "Det 3×3",
        latex: "\\begin{vmatrix}#?&#?&#?\\\\#?&#?&#?\\\\#?&#?&#?\\end{vmatrix}",
        preview: "\\begin{vmatrix}a&b&c\\\\d&e&f\\\\g&h&i\\end{vmatrix}",
      },
      {
        nombre: "Vector columna",
        latex: "\\begin{bmatrix}#?\\\\#?\\\\#?\\end{bmatrix}",
        preview: "\\begin{bmatrix}x\\\\y\\\\z\\end{bmatrix}",
      },
      {
        nombre: "Vector fila",
        latex: "\\begin{bmatrix}#?&#?&#?\\end{bmatrix}",
        preview: "\\begin{bmatrix}x&y&z\\end{bmatrix}",
      },
      { nombre: "Matriz identidad", latex: "I_{#?}", preview: "I_{n}" },
      { nombre: "Matriz inversa", latex: "#?^{-1}", preview: "A^{-1}" },
      { nombre: "Matriz transpuesta", latex: "#?^{T}", preview: "A^{T}" },
      { nombre: "det(A)", latex: "\\det(#?)", preview: "\\det(A)" },
      { nombre: "tr(A)", latex: "\\text{tr}(#?)", preview: "\\text{tr}(A)" },
      {
        nombre: "rank(A)",
        latex: "\\text{rank}(#?)",
        preview: "\\text{rank}(A)",
      },
    ],
  },
  vectores: {
    nombre: "Vectores",
    icono: "→",
    plantillas: [
      { nombre: "Vector con flecha", latex: "\\vec{#?}", preview: "\\vec{v}" },
      {
        nombre: "Vector negrita",
        latex: "\\mathbf{#?}",
        preview: "\\mathbf{v}",
      },
      { nombre: "Vector unitario î", latex: "\\hat{i}", preview: "\\hat{i}" },
      { nombre: "Vector unitario ĵ", latex: "\\hat{j}", preview: "\\hat{j}" },
      { nombre: "Vector unitario k̂", latex: "\\hat{k}", preview: "\\hat{k}" },
      { nombre: "Vector unitario", latex: "\\hat{#?}", preview: "\\hat{u}" },
      {
        nombre: "Producto punto",
        latex: "\\vec{#?}\\cdot\\vec{#?}",
        preview: "\\vec{a}\\cdot\\vec{b}",
      },
      {
        nombre: "Producto cruz",
        latex: "\\vec{#?}\\times\\vec{#?}",
        preview: "\\vec{a}\\times\\vec{b}",
      },
      { nombre: "Magnitud", latex: "|\\vec{#?}|", preview: "|\\vec{v}|" },
      { nombre: "Norma", latex: "\\|\\vec{#?}\\|", preview: "\\|\\vec{v}\\|" },
      {
        nombre: "Componentes",
        latex: "\\langle#?,#?,#?\\rangle",
        preview: "\\langle x,y,z\\rangle",
      },
    ],
  },

  // === CÁLCULO VECTORIAL ===
  calculoVectorial: {
    nombre: "Cálc. Vectorial",
    icono: "∇",
    plantillas: [
      { nombre: "Gradiente", latex: "\\nabla #?", preview: "\\nabla f" },
      {
        nombre: "Divergencia",
        latex: "\\nabla\\cdot\\vec{#?}",
        preview: "\\nabla\\cdot\\vec{F}",
      },
      {
        nombre: "Rotacional",
        latex: "\\nabla\\times\\vec{#?}",
        preview: "\\nabla\\times\\vec{F}",
      },
      { nombre: "Laplaciano", latex: "\\nabla^{2}#?", preview: "\\nabla^{2}f" },
      { nombre: "Laplaciano Δ", latex: "\\Delta #?", preview: "\\Delta f" },
      {
        nombre: "Derivada direccional",
        latex: "D_{\\vec{u}}#?",
        preview: "D_{\\vec{u}}f",
      },
      {
        nombre: "Grad ∂/∂x",
        latex:
          "\\frac{\\partial #?}{\\partial x}\\hat{i}+\\frac{\\partial #?}{\\partial y}\\hat{j}",
        preview:
          "\\frac{\\partial f}{\\partial x}\\hat{i}+\\frac{\\partial f}{\\partial y}\\hat{j}",
      },
      {
        nombre: "Campo vectorial",
        latex: "\\vec{F}(x,y,z)",
        preview: "\\vec{F}(x,y,z)",
      },
      {
        nombre: "T. Stokes",
        latex:
          "\\oint_{C}\\vec{F}\\cdot d\\vec{r}=\\iint_{S}(\\nabla\\times\\vec{F})\\cdot d\\vec{S}",
        preview: "\\oint_C\\vec{F}\\cdot d\\vec{r}",
      },
      {
        nombre: "T. Divergencia",
        latex:
          "\\iiint_{V}\\nabla\\cdot\\vec{F}\\,dV=\\iint_{S}\\vec{F}\\cdot d\\vec{S}",
        preview: "\\iiint_V\\nabla\\cdot\\vec{F}\\,dV",
      },
    ],
  },

  // === ECUACIONES DIFERENCIALES ===
  ecuacionesDif: {
    nombre: "Ec. Diferenciales",
    icono: "dy",
    plantillas: [
      {
        nombre: "EDO primer orden",
        latex: "\\frac{dy}{dx}+P(x)y=Q(x)",
        preview: "\\frac{dy}{dx}+P(x)y=Q(x)",
      },
      {
        nombre: "EDO segundo orden",
        latex: "\\frac{d^2y}{dx^2}+#?\\frac{dy}{dx}+#?y=#?",
        preview: "\\frac{d^2y}{dx^2}+a\\frac{dy}{dx}+by=f",
      },
      {
        nombre: "Separable",
        latex: "\\frac{dy}{dx}=f(x)g(y)",
        preview: "\\frac{dy}{dx}=f(x)g(y)",
      },
      { nombre: "Homogénea", latex: "y=vx", preview: "y=vx" },
      {
        nombre: "Factor integrante",
        latex: "e^{\\int P(x)dx}",
        preview: "e^{\\int P(x)dx}",
      },
      {
        nombre: "Sol. general",
        latex: "y=C_1e^{#?x}+C_2e^{#?x}",
        preview: "y=C_1e^{r_1x}+C_2e^{r_2x}",
      },
      {
        nombre: "Wronskiano",
        latex: "W(y_1,y_2)=\\begin{vmatrix}y_1&y_2\\\\y_1'&y_2'\\end{vmatrix}",
        preview: "W(y_1,y_2)",
      },
      { nombre: "y'", latex: "y'", preview: "y'" },
      { nombre: "y''", latex: "y''", preview: "y''" },
      { nombre: "ẏ (punto)", latex: "\\dot{y}", preview: "\\dot{y}" },
      { nombre: "ÿ (doble punto)", latex: "\\ddot{y}", preview: "\\ddot{y}" },
    ],
  },

  // === TRANSFORMADAS ===
  transformadas: {
    nombre: "Transformadas",
    icono: "ℒ",
    plantillas: [
      {
        nombre: "Laplace",
        latex: "\\mathcal{L}\\{#?\\}",
        preview: "\\mathcal{L}\\{f(t)\\}",
      },
      {
        nombre: "Laplace inversa",
        latex: "\\mathcal{L}^{-1}\\{#?\\}",
        preview: "\\mathcal{L}^{-1}\\{F(s)\\}",
      },
      {
        nombre: "Laplace integral",
        latex: "\\int_0^{\\infty}#?e^{-st}dt",
        preview: "\\int_0^{\\infty}f(t)e^{-st}dt",
      },
      {
        nombre: "Fourier",
        latex: "\\mathcal{F}\\{#?\\}",
        preview: "\\mathcal{F}\\{f(t)\\}",
      },
      {
        nombre: "Fourier inversa",
        latex: "\\mathcal{F}^{-1}\\{#?\\}",
        preview: "\\mathcal{F}^{-1}\\{F(\\omega)\\}",
      },
      {
        nombre: "Serie Fourier",
        latex: "a_0+\\sum_{n=1}^{\\infty}(a_n\\cos(nx)+b_n\\sin(nx))",
        preview: "a_0+\\sum a_n\\cos+b_n\\sin",
      },
      {
        nombre: "Transformada Z",
        latex: "\\mathcal{Z}\\{#?\\}",
        preview: "\\mathcal{Z}\\{f[n]\\}",
      },
      { nombre: "Convolución", latex: "(#?*#?)(t)", preview: "(f*g)(t)" },
      { nombre: "u(t) escalón", latex: "u(t-#?)", preview: "u(t-a)" },
      { nombre: "δ(t) delta", latex: "\\delta(t-#?)", preview: "\\delta(t-a)" },
    ],
  },

  // === GEOMETRÍA ===
  geometria: {
    nombre: "Geometría",
    icono: "⬡",
    plantillas: [
      { nombre: "Ángulo", latex: "\\angle #?", preview: "\\angle ABC" },
      { nombre: "Grados", latex: "#?°", preview: "90°" },
      { nombre: "Paralelo", latex: "\\parallel", preview: "\\parallel" },
      { nombre: "Perpendicular", latex: "\\perp", preview: "\\perp" },
      { nombre: "Congruente", latex: "\\cong", preview: "\\cong" },
      { nombre: "Similar", latex: "\\sim", preview: "\\sim" },
      {
        nombre: "Triángulo",
        latex: "\\triangle #?",
        preview: "\\triangle ABC",
      },
      {
        nombre: "Segmento",
        latex: "\\overline{#?}",
        preview: "\\overline{AB}",
      },
      { nombre: "Arco", latex: "\\widehat{#?}", preview: "\\widehat{AB}" },
      { nombre: "Radio", latex: "r=#?", preview: "r=5" },
      { nombre: "Diámetro", latex: "d=2r", preview: "d=2r" },
      { nombre: "Área círculo", latex: "A=\\pi r^2", preview: "A=\\pi r^2" },
      { nombre: "Circunferencia", latex: "C=2\\pi r", preview: "C=2\\pi r" },
    ],
  },

  // === PROBABILIDAD Y ESTADÍSTICA ===
  probabilidad: {
    nombre: "Probabilidad",
    icono: "P",
    plantillas: [
      { nombre: "P(A)", latex: "P(#?)", preview: "P(A)" },
      { nombre: "P(A|B)", latex: "P(#?|#?)", preview: "P(A|B)" },
      { nombre: "P(A∩B)", latex: "P(#?\\cap#?)", preview: "P(A\\cap B)" },
      { nombre: "P(A∪B)", latex: "P(#?\\cup#?)", preview: "P(A\\cup B)" },
      { nombre: "E[X]", latex: "E[#?]", preview: "E[X]" },
      { nombre: "Var(X)", latex: "\\text{Var}(#?)", preview: "\\text{Var}(X)" },
      { nombre: "σ² varianza", latex: "\\sigma^2", preview: "\\sigma^2" },
      { nombre: "σ desv.est.", latex: "\\sigma", preview: "\\sigma" },
      { nombre: "μ media", latex: "\\mu", preview: "\\mu" },
      { nombre: "x̄ promedio", latex: "\\bar{x}", preview: "\\bar{x}" },
      {
        nombre: "Cov(X,Y)",
        latex: "\\text{Cov}(#?,#?)",
        preview: "\\text{Cov}(X,Y)",
      },
      {
        nombre: "Normal",
        latex: "N(\\mu,\\sigma^2)",
        preview: "N(\\mu,\\sigma^2)",
      },
      {
        nombre: "Binomial",
        latex: "\\binom{n}{k}p^k(1-p)^{n-k}",
        preview: "\\binom{n}{k}p^k(1-p)^{n-k}",
      },
    ],
  },

  // === CONJUNTOS Y LÓGICA ===
  conjuntos: {
    nombre: "Conjuntos",
    icono: "∈",
    plantillas: [
      { nombre: "Pertenece", latex: "#?\\in#?", preview: "x\\in A" },
      { nombre: "No pertenece", latex: "#?\\notin#?", preview: "x\\notin A" },
      {
        nombre: "Subconjunto",
        latex: "#?\\subseteq#?",
        preview: "A\\subseteq B",
      },
      {
        nombre: "Subconj. propio",
        latex: "#?\\subset#?",
        preview: "A\\subset B",
      },
      { nombre: "Unión", latex: "#?\\cup#?", preview: "A\\cup B" },
      { nombre: "Intersección", latex: "#?\\cap#?", preview: "A\\cap B" },
      { nombre: "Complemento", latex: "#?^c", preview: "A^c" },
      {
        nombre: "Diferencia",
        latex: "#?\\setminus#?",
        preview: "A\\setminus B",
      },
      { nombre: "Conjunto vacío", latex: "\\emptyset", preview: "\\emptyset" },
      { nombre: "Naturales", latex: "\\mathbb{N}", preview: "\\mathbb{N}" },
      { nombre: "Enteros", latex: "\\mathbb{Z}", preview: "\\mathbb{Z}" },
      { nombre: "Racionales", latex: "\\mathbb{Q}", preview: "\\mathbb{Q}" },
      { nombre: "Reales", latex: "\\mathbb{R}", preview: "\\mathbb{R}" },
      { nombre: "Complejos", latex: "\\mathbb{C}", preview: "\\mathbb{C}" },
      { nombre: "Para todo", latex: "\\forall #?", preview: "\\forall x" },
      { nombre: "Existe", latex: "\\exists #?", preview: "\\exists x" },
    ],
  },

  // === SÍMBOLOS GRIEGOS ===
  griegosMin: {
    nombre: "Griegas min.",
    icono: "αβγ",
    plantillas: [
      { nombre: "α alpha", latex: "\\alpha", preview: "\\alpha" },
      { nombre: "β beta", latex: "\\beta", preview: "\\beta" },
      { nombre: "γ gamma", latex: "\\gamma", preview: "\\gamma" },
      { nombre: "δ delta", latex: "\\delta", preview: "\\delta" },
      { nombre: "ε epsilon", latex: "\\epsilon", preview: "\\epsilon" },
      { nombre: "ζ zeta", latex: "\\zeta", preview: "\\zeta" },
      { nombre: "η eta", latex: "\\eta", preview: "\\eta" },
      { nombre: "θ theta", latex: "\\theta", preview: "\\theta" },
      { nombre: "ι iota", latex: "\\iota", preview: "\\iota" },
      { nombre: "κ kappa", latex: "\\kappa", preview: "\\kappa" },
      { nombre: "λ lambda", latex: "\\lambda", preview: "\\lambda" },
      { nombre: "μ mu", latex: "\\mu", preview: "\\mu" },
      { nombre: "ν nu", latex: "\\nu", preview: "\\nu" },
      { nombre: "ξ xi", latex: "\\xi", preview: "\\xi" },
      { nombre: "π pi", latex: "\\pi", preview: "\\pi" },
      { nombre: "ρ rho", latex: "\\rho", preview: "\\rho" },
      { nombre: "σ sigma", latex: "\\sigma", preview: "\\sigma" },
      { nombre: "τ tau", latex: "\\tau", preview: "\\tau" },
      { nombre: "φ phi", latex: "\\phi", preview: "\\phi" },
      { nombre: "χ chi", latex: "\\chi", preview: "\\chi" },
      { nombre: "ψ psi", latex: "\\psi", preview: "\\psi" },
      { nombre: "ω omega", latex: "\\omega", preview: "\\omega" },
    ],
  },
  griegosMay: {
    nombre: "Griegas may.",
    icono: "ΔΣΩ",
    plantillas: [
      { nombre: "Γ Gamma", latex: "\\Gamma", preview: "\\Gamma" },
      { nombre: "Δ Delta", latex: "\\Delta", preview: "\\Delta" },
      { nombre: "Θ Theta", latex: "\\Theta", preview: "\\Theta" },
      { nombre: "Λ Lambda", latex: "\\Lambda", preview: "\\Lambda" },
      { nombre: "Ξ Xi", latex: "\\Xi", preview: "\\Xi" },
      { nombre: "Π Pi", latex: "\\Pi", preview: "\\Pi" },
      { nombre: "Σ Sigma", latex: "\\Sigma", preview: "\\Sigma" },
      { nombre: "Φ Phi", latex: "\\Phi", preview: "\\Phi" },
      { nombre: "Ψ Psi", latex: "\\Psi", preview: "\\Psi" },
      { nombre: "Ω Omega", latex: "\\Omega", preview: "\\Omega" },
      {
        nombre: "ε varepsilon",
        latex: "\\varepsilon",
        preview: "\\varepsilon",
      },
      { nombre: "ϑ vartheta", latex: "\\vartheta", preview: "\\vartheta" },
      { nombre: "φ varphi", latex: "\\varphi", preview: "\\varphi" },
    ],
  },

  // === OPERADORES Y RELACIONES ===
  operadores: {
    nombre: "Operadores",
    icono: "±×",
    plantillas: [
      { nombre: "±", latex: "\\pm", preview: "\\pm" },
      { nombre: "∓", latex: "\\mp", preview: "\\mp" },
      { nombre: "×", latex: "\\times", preview: "\\times" },
      { nombre: "÷", latex: "\\div", preview: "\\div" },
      { nombre: "·", latex: "\\cdot", preview: "\\cdot" },
      { nombre: "∘", latex: "\\circ", preview: "\\circ" },
      { nombre: "⊗", latex: "\\otimes", preview: "\\otimes" },
      { nombre: "⊕", latex: "\\oplus", preview: "\\oplus" },
      { nombre: "=", latex: "=", preview: "=" },
      { nombre: "≠", latex: "\\neq", preview: "\\neq" },
      { nombre: "<", latex: "<", preview: "<" },
      { nombre: ">", latex: ">", preview: ">" },
      { nombre: "≤", latex: "\\leq", preview: "\\leq" },
      { nombre: "≥", latex: "\\geq", preview: "\\geq" },
      { nombre: "≪", latex: "\\ll", preview: "\\ll" },
      { nombre: "≫", latex: "\\gg", preview: "\\gg" },
      { nombre: "≈", latex: "\\approx", preview: "\\approx" },
      { nombre: "≡", latex: "\\equiv", preview: "\\equiv" },
      { nombre: "∝", latex: "\\propto", preview: "\\propto" },
      { nombre: "∞", latex: "\\infty", preview: "\\infty" },
      { nombre: "→", latex: "\\to", preview: "\\to" },
      { nombre: "⇒", latex: "\\Rightarrow", preview: "\\Rightarrow" },
      { nombre: "⇔", latex: "\\Leftrightarrow", preview: "\\Leftrightarrow" },
      { nombre: "∴", latex: "\\therefore", preview: "\\therefore" },
      { nombre: "∵", latex: "\\because", preview: "\\because" },
    ],
  },

  // === COMPLEJOS Y AVANZADOS ===
  complejos: {
    nombre: "Complejos",
    icono: "i",
    plantillas: [
      { nombre: "i imaginario", latex: "i", preview: "i" },
      { nombre: "a + bi", latex: "#?+#?i", preview: "a+bi" },
      {
        nombre: "Conjugado",
        latex: "\\overline{#?}",
        preview: "\\overline{z}",
      },
      { nombre: "|z| módulo", latex: "|z|", preview: "|z|" },
      { nombre: "Re(z)", latex: "\\text{Re}(#?)", preview: "\\text{Re}(z)" },
      { nombre: "Im(z)", latex: "\\text{Im}(#?)", preview: "\\text{Im}(z)" },
      {
        nombre: "Forma polar",
        latex: "r(\\cos\\theta+i\\sin\\theta)",
        preview: "r(\\cos\\theta+i\\sin\\theta)",
      },
      { nombre: "Euler", latex: "re^{i\\theta}", preview: "re^{i\\theta}" },
      { nombre: "e^(iπ)", latex: "e^{i\\pi}=-1", preview: "e^{i\\pi}=-1" },
    ],
  },

  // === FUNCIONES ESPECIALES ===
  funciones: {
    nombre: "Funciones",
    icono: "f(x)",
    plantillas: [
      { nombre: "f(x)", latex: "f(#?)", preview: "f(x)" },
      { nombre: "g(x)", latex: "g(#?)", preview: "g(x)" },
      { nombre: "f⁻¹(x)", latex: "f^{-1}(#?)", preview: "f^{-1}(x)" },
      { nombre: "f∘g", latex: "(f\\circ g)(#?)", preview: "(f\\circ g)(x)" },
      { nombre: "max", latex: "\\max(#?)", preview: "\\max(a,b)" },
      { nombre: "min", latex: "\\min(#?)", preview: "\\min(a,b)" },
      { nombre: "sup", latex: "\\sup(#?)", preview: "\\sup(A)" },
      { nombre: "inf", latex: "\\inf(#?)", preview: "\\inf(A)" },
      {
        nombre: "arg max",
        latex: "\\arg\\max_{#?}#?",
        preview: "\\arg\\max_{x}f(x)",
      },
      { nombre: "sgn", latex: "\\text{sgn}(#?)", preview: "\\text{sgn}(x)" },
      { nombre: "mod", latex: "#?\\mod#?", preview: "a\\mod b" },
      { nombre: "gcd", latex: "\\gcd(#?,#?)", preview: "\\gcd(a,b)" },
      {
        nombre: "lcm",
        latex: "\\text{lcm}(#?,#?)",
        preview: "\\text{lcm}(a,b)",
      },
    ],
  },
};

const MathToolbar = ({ onInsertTemplate }) => {
  const [categoriaActiva, setCategoriaActiva] = useState("fracciones");

  const handleInsert = (latex) => {
    onInsertTemplate(latex);
  };

  return (
    <div
      style={{
        background: "rgba(17, 24, 39, 0.95)",
        border: "1px solid rgba(147, 51, 234, 0.3)",
        borderRadius: "12px",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        height: "100%",
      }}
    >
      {/* Tabs de categorías */}
      <div
        style={{
          display: "flex",
          gap: "4px",
          padding: "12px",
          borderBottom: "1px solid rgba(147, 51, 234, 0.2)",
          overflowX: "auto",
          flexWrap: "wrap",
        }}
      >
        {Object.entries(CATEGORIAS).map(([key, cat]) => (
          <button
            type="button"
            key={key}
            onClick={() => setCategoriaActiva(key)}
            style={{
              padding: "8px 16px",
              background:
                categoriaActiva === key
                  ? "linear-gradient(135deg, #9333ea, #7c3aed)"
                  : "rgba(147, 51, 234, 0.1)",
              color: categoriaActiva === key ? "#fff" : "#c4b5fd",
              border:
                categoriaActiva === key
                  ? "1px solid #a855f7"
                  : "1px solid rgba(147, 51, 234, 0.2)",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "13px",
              fontWeight: categoriaActiva === key ? "600" : "500",
              transition: "all 0.2s",
              whiteSpace: "nowrap",
            }}
            onMouseEnter={(e) => {
              if (categoriaActiva !== key) {
                e.target.style.background = "rgba(147, 51, 234, 0.2)";
              }
            }}
            onMouseLeave={(e) => {
              if (categoriaActiva !== key) {
                e.target.style.background = "rgba(147, 51, 234, 0.1)";
              }
            }}
          >
            <span style={{ marginRight: "6px" }}>{cat.icono}</span>
            {cat.nombre}
          </button>
        ))}
      </div>

      {/* Grid de plantillas */}
      <div
        style={{
          padding: "16px",
          overflowY: "auto",
          flex: 1,
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
            gap: "12px",
          }}
        >
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
  );
};

export default MathToolbar;

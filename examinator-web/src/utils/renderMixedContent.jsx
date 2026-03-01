import { InlineMath, BlockMath } from "react-katex";
import "katex/dist/katex.min.css";

/**
 * Funciones auxiliares para conversión de colores
 */
const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
};

const rgbToCmyk = (r, g, b) => {
  if (r === 0 && g === 0 && b === 0) return { c: 0, m: 0, y: 0, k: 100 };
  const rP = r / 255,
    gP = g / 255,
    bP = b / 255;
  const k = 1 - Math.max(rP, gP, bP);
  const c = ((1 - rP - k) / (1 - k)) * 100;
  const m = ((1 - gP - k) / (1 - k)) * 100;
  const y = ((1 - bP - k) / (1 - k)) * 100;
  return {
    c: Math.round(c),
    m: Math.round(m),
    y: Math.round(y),
    k: Math.round(k * 100),
  };
};

/**
 * Componente para renderizar un color con todas sus conversiones
 */
const ColorSwatch = ({ hex }) => {
  const rgb = hexToRgb(hex);
  if (!rgb)
    return <span style={{ color: "#ef4444" }}>⚠️ Color inválido: {hex}</span>;

  const cmyk = rgbToCmyk(rgb.r, rgb.g, rgb.b);

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "1rem",
        padding: "0.75rem 1rem",
        background: "rgba(30, 41, 59, 0.6)",
        borderRadius: "12px",
        border: "2px solid rgba(244, 63, 94, 0.3)",
        margin: "0.5rem 0",
        flexWrap: "wrap",
      }}
    >
      {/* Muestra del color */}
      <div
        style={{
          width: "60px",
          height: "60px",
          background: hex,
          borderRadius: "10px",
          boxShadow: `0 4px 15px ${hex}50`,
          border: "2px solid rgba(255, 255, 255, 0.2)",
          flexShrink: 0,
        }}
      />

      {/* Valores */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "0.3rem",
          fontSize: "0.85rem",
        }}
      >
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span style={{ color: "#60a5fa", fontWeight: "600", width: "50px" }}>
            HEX:
          </span>
          <code
            style={{
              color: "#e2e8f0",
              fontFamily: "monospace",
              background: "rgba(59, 130, 246, 0.15)",
              padding: "2px 8px",
              borderRadius: "4px",
            }}
          >
            {hex}
          </code>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span style={{ color: "#10b981", fontWeight: "600", width: "50px" }}>
            RGB:
          </span>
          <code
            style={{
              color: "#e2e8f0",
              fontFamily: "monospace",
              background: "rgba(16, 185, 129, 0.15)",
              padding: "2px 8px",
              borderRadius: "4px",
            }}
          >
            rgb({rgb.r}, {rgb.g}, {rgb.b})
          </code>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span style={{ color: "#8b5cf6", fontWeight: "600", width: "50px" }}>
            RGBA:
          </span>
          <code
            style={{
              color: "#e2e8f0",
              fontFamily: "monospace",
              background: "rgba(139, 92, 246, 0.15)",
              padding: "2px 8px",
              borderRadius: "4px",
            }}
          >
            rgba({rgb.r}, {rgb.g}, {rgb.b}, 1)
          </code>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <span style={{ color: "#f59e0b", fontWeight: "600", width: "50px" }}>
            CMYK:
          </span>
          <code
            style={{
              color: "#e2e8f0",
              fontFamily: "monospace",
              background: "rgba(245, 158, 11, 0.15)",
              padding: "2px 8px",
              borderRadius: "4px",
            }}
          >
            cmyk({cmyk.c}%, {cmyk.m}%, {cmyk.y}%, {cmyk.k}%)
          </code>
        </div>
      </div>
    </div>
  );
};

/**
 * Componente para renderizar múltiples colores (combinación/paleta)
 */
const ColorCombination = ({ colors }) => {
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.5rem",
        padding: "0.75rem 1rem",
        background: "rgba(139, 92, 246, 0.1)",
        borderRadius: "12px",
        border: "2px solid rgba(139, 92, 246, 0.3)",
        margin: "0.5rem 0",
        flexWrap: "wrap",
      }}
    >
      <span
        style={{ color: "#a78bfa", fontWeight: "600", marginRight: "0.5rem" }}
      >
        🎨 Combinación:
      </span>
      {colors.map((hex, idx) => {
        const rgb = hexToRgb(hex);
        return (
          <div
            key={idx}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "0.25rem",
            }}
          >
            <div
              style={{
                width: "45px",
                height: "45px",
                background: hex,
                borderRadius: "8px",
                boxShadow: `0 3px 10px ${hex}40`,
                border: "2px solid rgba(255, 255, 255, 0.2)",
              }}
            />
            <code
              style={{
                color: "#e2e8f0",
                fontSize: "0.65rem",
                fontFamily: "monospace",
              }}
            >
              {hex}
            </code>
            {rgb && (
              <span style={{ color: "#94a3b8", fontSize: "0.55rem" }}>
                {rgb.r},{rgb.g},{rgb.b}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
};

/**
 * Componente para renderizar mezcla de colores con resultado
 */
const ColorMix = ({ colors, result }) => {
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.5rem",
        padding: "1rem",
        background: "rgba(16, 185, 129, 0.1)",
        borderRadius: "12px",
        border: "2px solid rgba(16, 185, 129, 0.3)",
        margin: "0.5rem 0",
        flexWrap: "wrap",
      }}
    >
      <span
        style={{ color: "#34d399", fontWeight: "600", marginRight: "0.25rem" }}
      >
        🧪 Mezcla:
      </span>

      {/* Colores originales */}
      {colors.map((hex, idx) => (
        <div key={idx} style={{ display: "flex", alignItems: "center" }}>
          <div
            style={{
              width: "35px",
              height: "35px",
              background: hex,
              borderRadius: "6px",
              border: "2px solid rgba(255, 255, 255, 0.2)",
            }}
            title={hex}
          />
          {idx < colors.length - 1 && (
            <span
              style={{
                color: "#94a3b8",
                margin: "0 0.35rem",
                fontSize: "1rem",
                fontWeight: "bold",
              }}
            >
              +
            </span>
          )}
        </div>
      ))}

      {/* Flecha */}
      <span
        style={{ color: "#6ee7b7", margin: "0 0.5rem", fontSize: "1.2rem" }}
      >
        →
      </span>

      {/* Resultado */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "0.25rem",
        }}
      >
        <div
          style={{
            width: "55px",
            height: "55px",
            background: result,
            borderRadius: "10px",
            border: "3px solid rgba(16, 185, 129, 0.5)",
            boxShadow: `0 4px 15px ${result}50`,
          }}
        />
        <code
          style={{
            color: "#a7f3d0",
            fontSize: "0.75rem",
            fontFamily: "monospace",
          }}
        >
          {result}
        </code>
      </div>
    </div>
  );
};

/**
 * Renderiza texto mixto con LaTeX embebido y colores
 * Detecta $...$ para inline math, $$...$$ para display math, y [COLOR:#hex] para colores
 * También soporta [COLORS:#hex1+#hex2...] y [COLORMIX:#hex1+#hex2=#result]
 * Detecta LaTeX puro como \begin{pmatrix} sin necesidad de delimitadores
 * Detecta composiciones geométricas como "⬤ Círculo (#3b82f6, pos: 250,191)"
 * @param {string} text - Texto con LaTeX y colores embebidos
 * @returns {React.ReactNode} - Componentes renderizados
 */
export const renderMixedContent = (text) => {
  if (!text) return null;

  // Preprocesar documentos LaTeX completos (detectar \documentclass o \begin{document})
  if (text.includes('\\documentclass') || text.includes('\\begin{document}')) {
    return renderLatexDocument(text);
  }

  const parts = [];
  let currentIndex = 0;

  // Regex combinada para LaTeX y colores (orden importa - más específicos primero)
  // 1. COLORMIX: [COLORMIX:#hex1+#hex2=#result]
  // 2. COLORS: [COLORS:#hex1+#hex2+...]
  // 3. COLOR: [COLOR:#hex]
  // 4. Display math: $$...$$
  // 5. Inline math: $...$
  // 6. LaTeX puro: \begin{...}...\end{...}
  // 7. Composición geométrica: ⬤ Círculo (#hex, pos: x,y)
  const combinedRegex =
    /\[COLORMIX:((?:#[a-fA-F0-9]{6}\+?)+)=(#[a-fA-F0-9]{6})\]|\[COLORS:((?:#[a-fA-F0-9]{6}\+?)+)\]|\[COLOR:(#[a-fA-F0-9]{6}|#[a-fA-F0-9]{3})\]|\$\$([^\$]+)\$\$|\$([^\$]+)\$|(\\begin\{[a-zA-Z]+\}[\s\S]*?\\end\{[a-zA-Z]+\})|([⬤●◯○▲△■□◆◇★☆▼▽◀◁▶▷]\s*(?:Círculo|Cuadrado|Triángulo|Rectángulo|Línea|Punto|Estrella|Flecha|Rombo)\s*\(#[a-fA-F0-9]{6}[^)]*\))/g;
  let match;

  while ((match = combinedRegex.exec(text)) !== null) {
    // Añade texto antes del match
    if (match.index > currentIndex) {
      parts.push({
        type: "text",
        content: text.slice(currentIndex, match.index),
      });
    }

    if (match[1] && match[2]) {
      // COLORMIX: [COLORMIX:#hex1+#hex2=#result]
      const colors = match[1].split("+").filter((c) => c);
      parts.push({ type: "colormix", colors, result: match[2] });
    } else if (match[3]) {
      // COLORS: [COLORS:#hex1+#hex2+...]
      const colors = match[3].split("+").filter((c) => c);
      parts.push({ type: "colors", colors });
    } else if (match[4]) {
      // COLOR: [COLOR:#hex]
      parts.push({ type: "color", content: match[4] });
    } else if (match[5]) {
      // Display math $$...$$
      parts.push({ type: "block", content: match[5] });
    } else if (match[6]) {
      // Inline math $...$
      parts.push({ type: "inline", content: match[6] });
    } else if (match[7]) {
      // LaTeX puro sin delimitadores (como \begin{pmatrix})
      parts.push({ type: "block", content: match[7] });
    } else if (match[8]) {
      // Composición geométrica
      parts.push({ type: "geometry", content: match[8] });
    }

    currentIndex = match.index + match[0].length;
  }

  // Añade texto restante
  if (currentIndex < text.length) {
    parts.push({ type: "text", content: text.slice(currentIndex) });
  }

  // Si no hay elementos especiales, devuelve el texto original
  if (parts.length === 0) {
    return text;
  }

  // Renderiza las partes
  return parts.map((part, idx) => {
    if (part.type === "block") {
      try {
        return <BlockMath key={idx} math={part.content} />;
      } catch (e) {
        return <span key={idx} style={{color: '#fca5a5', fontFamily: 'monospace', fontSize: '0.85rem'}}>{part.content}</span>;
      }
    } else if (part.type === "inline") {
      try {
        return <InlineMath key={idx} math={part.content} />;
      } catch (e) {
        return <span key={idx} style={{color: '#fca5a5'}}>{part.content}</span>;
      }
    } else if (part.type === "color") {
      return <ColorSwatch key={idx} hex={part.content} />;
    } else if (part.type === "colors") {
      return <ColorCombination key={idx} colors={part.colors} />;
    } else if (part.type === "colormix") {
      return <ColorMix key={idx} colors={part.colors} result={part.result} />;
    } else if (part.type === "geometry") {
      return <GeometryShape key={idx} content={part.content} />;
    } else {
      return <span key={idx}>{part.content}</span>;
    }
  });
};

/**
 * Componente para renderizar figuras geométricas con colores reales
 */
const GeometryShape = ({ content }) => {
  // Parsear: ⬤ Círculo (#3b82f6, pos: 250,191)
  const shapeMatch = content.match(/([⬤●◯○▲△■□◆◇★☆▼▽◀◁▶▷])\s*(Círculo|Cuadrado|Triángulo|Rectángulo|Línea|Punto|Estrella|Flecha|Rombo)\s*\((#[a-fA-F0-9]{6})(?:,\s*pos:\s*(\d+),(\d+))?\)/i);
  
  if (!shapeMatch) {
    return <span>{content}</span>;
  }

  const [, symbol, shapeName, color, posX, posY] = shapeMatch;
  
  // Determinar la forma SVG basada en el nombre
  const renderSvgShape = () => {
    const size = 40;
    const commonStyle = {
      fill: color,
      filter: `drop-shadow(0 2px 4px ${color}60)`,
    };

    switch (shapeName.toLowerCase()) {
      case 'círculo':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <circle cx="20" cy="20" r="18" style={commonStyle} />
          </svg>
        );
      case 'cuadrado':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <rect x="2" y="2" width="36" height="36" style={commonStyle} />
          </svg>
        );
      case 'triángulo':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <polygon points="20,2 38,38 2,38" style={commonStyle} />
          </svg>
        );
      case 'rectángulo':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <rect x="2" y="8" width="36" height="24" style={commonStyle} />
          </svg>
        );
      case 'rombo':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <polygon points="20,2 38,20 20,38 2,20" style={commonStyle} />
          </svg>
        );
      case 'estrella':
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <polygon points="20,2 24,15 38,15 27,24 31,38 20,30 9,38 13,24 2,15 16,15" style={commonStyle} />
          </svg>
        );
      default:
        return (
          <svg width={size} height={size} viewBox="0 0 40 40">
            <circle cx="20" cy="20" r="18" style={commonStyle} />
          </svg>
        );
    }
  };

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.5rem',
      padding: '0.35rem 0.75rem',
      background: `${color}15`,
      borderRadius: '8px',
      border: `1px solid ${color}40`,
      margin: '0.25rem',
    }}>
      {renderSvgShape()}
      <span style={{ color: '#e2e8f0', fontSize: '0.85rem' }}>
        {shapeName}
      </span>
      <code style={{
        color: color,
        fontSize: '0.75rem',
        fontFamily: 'monospace',
        background: 'rgba(30, 41, 59, 0.6)',
        padding: '2px 6px',
        borderRadius: '4px',
      }}>
        {color}
      </code>
      {posX && posY && (
        <span style={{ color: '#94a3b8', fontSize: '0.7rem' }}>
          ({posX}, {posY})
        </span>
      )}
    </span>
  );
};

/**
 * Renderiza un documento LaTeX completo, extrayendo las fórmulas
 * y convirtiendo comandos de estructura a HTML
 */
const renderLatexDocument = (text) => {
  // Eliminar preámbulo del documento
  let content = text
    .replace(/\\documentclass(\[[^\]]*\])?\{[^}]*\}/g, '')
    .replace(/\\usepackage(\[[^\]]*\])?\{[^}]*\}/g, '')
    .replace(/\\begin\{document\}/g, '')
    .replace(/\\end\{document\}/g, '')
    .replace(/\\maketitle/g, '');

  const elements = [];
  let key = 0;

  // Primero extraer todos los bloques \[...\] (pueden ser multilinea)
  const displayMathRegex = /\\\[([\s\S]*?)\\\]/g;
  let lastIndex = 0;
  let match;
  const segments = [];
  
  while ((match = displayMathRegex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: 'text', content: content.slice(lastIndex, match.index) });
    }
    segments.push({ type: 'displaymath', content: match[1] });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < content.length) {
    segments.push({ type: 'text', content: content.slice(lastIndex) });
  }

  // Procesar cada segmento
  for (const segment of segments) {
    if (segment.type === 'displaymath') {
      try {
        elements.push(
          <div key={key++} style={{
            margin: '1rem 0',
            padding: '1rem',
            background: 'rgba(59, 130, 246, 0.08)',
            borderRadius: '8px',
            borderLeft: '3px solid #3b82f6',
            overflow: 'auto'
          }}>
            <BlockMath math={segment.content.trim()} />
          </div>
        );
      } catch (e) {
        elements.push(
          <pre key={key++} style={{color: '#fca5a5', fontFamily: 'monospace', fontSize: '0.85rem', margin: '0.5rem 0', whiteSpace: 'pre-wrap'}}>
            {segment.content}
          </pre>
        );
      }
    } else {
      // Procesar texto con secciones, inline math, etc.
      const textLines = segment.content.split('\n');
      let currentText = '';

      for (const line of textLines) {
        const trimmed = line.trim();
        if (!trimmed) {
          if (currentText) {
            elements.push(<p key={key++} style={{margin: '0.5rem 0', color: '#e2e8f0', lineHeight: '1.6'}}>{currentText}</p>);
            currentText = '';
          }
          continue;
        }

        // Sección
        const sectionMatch = trimmed.match(/\\section\*?\{([^}]+)\}/);
        if (sectionMatch) {
          if (currentText) {
            elements.push(<p key={key++} style={{margin: '0.5rem 0', color: '#e2e8f0'}}>{currentText}</p>);
            currentText = '';
          }
          elements.push(
            <h2 key={key++} style={{
              color: '#60a5fa',
              fontWeight: '700',
              fontSize: '1.4rem',
              marginTop: '1.5rem',
              marginBottom: '0.75rem',
              borderBottom: '2px solid rgba(96, 165, 250, 0.3)',
              paddingBottom: '0.5rem'
            }}>
              {sectionMatch[1]}
            </h2>
          );
          continue;
        }

        // Subsección
        const subsectionMatch = trimmed.match(/\\subsection\*?\{([^}]+)\}/);
        if (subsectionMatch) {
          if (currentText) {
            elements.push(<p key={key++} style={{margin: '0.5rem 0', color: '#e2e8f0'}}>{currentText}</p>);
            currentText = '';
          }
          elements.push(
            <h3 key={key++} style={{
              color: '#a78bfa',
              fontWeight: '600',
              fontSize: '1.15rem',
              marginTop: '1rem',
              marginBottom: '0.5rem'
            }}>
              {subsectionMatch[1]}
            </h3>
          );
          continue;
        }

        // Texto normal - procesar comandos inline
        let processedLine = trimmed
          .replace(/\\textbf\{([^}]+)\}/g, (_, text) => `**${text}**`)
          .replace(/\\textit\{([^}]+)\}/g, (_, text) => `*${text}*`)
          .replace(/\\quad/g, '    ')
          .replace(/\\\\/g, ' ')
          .replace(/\\ /g, ' ');

        // Buscar math inline \(...\) y convertir a $...$
        processedLine = processedLine.replace(/\\\(([^)]+)\\\)/g, '$$$$1$$');

        // Si tiene math inline, renderizar
        if (processedLine.includes('$')) {
          if (currentText) {
            elements.push(<p key={key++} style={{margin: '0.5rem 0', color: '#e2e8f0'}}>{currentText}</p>);
            currentText = '';
          }
          elements.push(
            <div key={key++} style={{margin: '0.5rem 0', color: '#e2e8f0', lineHeight: '1.8'}}>
              {renderMixedContentSimple(processedLine)}
            </div>
          );
        } else if (processedLine.includes('**') || processedLine.includes('*')) {
          // Procesar negritas y cursivas
          if (currentText) {
            elements.push(<p key={key++} style={{margin: '0.5rem 0', color: '#e2e8f0'}}>{currentText}</p>);
            currentText = '';
          }
          const parts = processedLine.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g).filter(Boolean);
          elements.push(
            <div key={key++} style={{margin: '0.5rem 0', color: '#e2e8f0', lineHeight: '1.8'}}>
              {parts.map((part, i) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                  return <strong key={i} style={{color: '#fbbf24'}}>{part.slice(2, -2)}</strong>;
                } else if (part.startsWith('*') && part.endsWith('*')) {
                  return <em key={i}>{part.slice(1, -1)}</em>;
                }
                return <span key={i}>{part}</span>;
              })}
            </div>
          );
        } else {
          // Solo texto normal
          currentText += (currentText ? ' ' : '') + processedLine;
        }
      }

      // Texto restante
      if (currentText) {
        elements.push(<p key={key++} style={{margin: '0.5rem 0', color: '#e2e8f0'}}>{currentText}</p>);
      }
    }
  }

  return (
    <div style={{
      padding: '1rem',
      background: 'rgba(30, 41, 59, 0.4)',
      borderRadius: '12px',
      border: '1px solid rgba(59, 130, 246, 0.2)'
    }}>
      {elements.length > 0 ? elements : <span style={{color: '#94a3b8'}}>Sin contenido</span>}
    </div>
  );
};

/**
 * Versión simplificada de renderMixedContent para evitar recursión infinita
 * Solo procesa LaTeX inline y display
 */
const renderMixedContentSimple = (text) => {
  if (!text) return null;

  const parts = [];
  let currentIndex = 0;

  // Solo LaTeX: $$...$$ y $...$
  const latexRegex = /\$\$([^\$]+)\$\$|\$([^\$]+)\$/g;
  let match;

  while ((match = latexRegex.exec(text)) !== null) {
    if (match.index > currentIndex) {
      parts.push({ type: "text", content: text.slice(currentIndex, match.index) });
    }

    if (match[1]) {
      parts.push({ type: "block", content: match[1] });
    } else if (match[2]) {
      parts.push({ type: "inline", content: match[2] });
    }

    currentIndex = match.index + match[0].length;
  }

  if (currentIndex < text.length) {
    parts.push({ type: "text", content: text.slice(currentIndex) });
  }

  if (parts.length === 0) return text;

  return parts.map((part, idx) => {
    if (part.type === "block") {
      try {
        return <BlockMath key={idx} math={part.content} />;
      } catch (e) {
        return <code key={idx} style={{color: '#fca5a5'}}>{part.content}</code>;
      }
    } else if (part.type === "inline") {
      try {
        return <InlineMath key={idx} math={part.content} />;
      } catch (e) {
        return <code key={idx} style={{color: '#fca5a5'}}>{part.content}</code>;
      }
    }
    return <span key={idx}>{part.content}</span>;
  });
};

/**
 * Renderiza contenido de Arte y Diseño con colores visuales
 * Convierte █ #hex en cuadrados de colores reales
 * Soporta paletas, figuras y composiciones
 * @param {string} text - Contenido de arte con colores
 * @returns {React.ReactNode} - Contenido renderizado con colores visuales
 */
export const renderArtContent = (text) => {
  if (!text) return null;

  // Dividir por líneas para mejor formato
  const lineas = text.split("\n");

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "0.75rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      {lineas.map((linea, lineaIdx) => {
        if (!linea.trim())
          return <div key={lineaIdx} style={{ height: "0.5rem" }} />;

        // Detectar si es una línea de paleta (contiene █ y #hex)
        const colorRegex = /█\s*(#[a-fA-F0-9]{6}|#[a-fA-F0-9]{3})/g;
        const hasColors = colorRegex.test(linea);
        colorRegex.lastIndex = 0; // Reset

        if (hasColors) {
          // Extraer título si existe (texto antes del primer █)
          const primerIndex = linea.indexOf("█");
          const titulo =
            primerIndex > 0 ? linea.slice(0, primerIndex).trim() : "";

          // Extraer todos los colores
          const colores = [];
          let match;
          while ((match = colorRegex.exec(linea)) !== null) {
            colores.push(match[1]);
          }

          return (
            <div
              key={lineaIdx}
              style={{
                background: "rgba(139, 92, 246, 0.08)",
                borderRadius: "12px",
                padding: "1rem",
                border: "1px solid rgba(139, 92, 246, 0.2)",
              }}
            >
              {titulo && (
                <div
                  style={{
                    color: "#c4b5fd",
                    fontWeight: "600",
                    marginBottom: "0.75rem",
                    fontSize: "0.95rem",
                  }}
                >
                  {titulo}
                </div>
              )}
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "0.75rem",
                  alignItems: "center",
                }}
              >
                {colores.map((hex, idx) => {
                  const rgb = hexToRgb(hex);
                  const isNeon =
                    [
                      "#ff00ff",
                      "#00ffff",
                      "#ffff00",
                      "#ff1493",
                      "#00ff00",
                      "#ff0000",
                      "#00ff7f",
                      "#ff6b00",
                    ].some((n) => n.toLowerCase() === hex.toLowerCase()) ||
                    (rgb &&
                      (rgb.r > 200 || rgb.g > 200 || rgb.b > 200) &&
                      (rgb.r === 0 ||
                        rgb.g === 0 ||
                        rgb.b === 0 ||
                        rgb.r === 255 ||
                        rgb.g === 255 ||
                        rgb.b === 255));

                  return (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        gap: "0.35rem",
                      }}
                    >
                      <div
                        style={{
                          width: "50px",
                          height: "50px",
                          background: hex,
                          borderRadius: "10px",
                          boxShadow: isNeon
                            ? `0 0 15px ${hex}, 0 0 30px ${hex}60, inset 0 0 10px rgba(255,255,255,0.2)`
                            : `0 4px 12px ${hex}40`,
                          border: "2px solid rgba(255, 255, 255, 0.25)",
                          transition: "transform 0.2s, box-shadow 0.2s",
                        }}
                        title={hex}
                      />
                      <code
                        style={{
                          color: "#e2e8f0",
                          fontSize: "0.7rem",
                          fontFamily: "monospace",
                          background: "rgba(30, 41, 59, 0.6)",
                          padding: "2px 6px",
                          borderRadius: "4px",
                        }}
                      >
                        {hex}
                      </code>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        }

        // Detectar composiciones/layouts (contienen ┌ ─ │ └)
        const isComposition = /[┌┐└┘─│├┤┬┴┼▢▬●◼▲⬤]/.test(linea);

        if (isComposition) {
          return (
            <div
              key={lineaIdx}
              style={{
                fontFamily: "monospace",
                whiteSpace: "pre",
                color: "#94a3b8",
                background: "rgba(30, 41, 59, 0.6)",
                padding: "0.25rem 0.5rem",
                borderRadius: "4px",
                lineHeight: "1.4",
                fontSize: "0.85rem",
              }}
            >
              {linea}
            </div>
          );
        }

        // Línea normal de texto
        return (
          <div
            key={lineaIdx}
            style={{
              color: "#e2e8f0",
              lineHeight: "1.5",
            }}
          >
            {linea}
          </div>
        );
      })}
    </div>
  );
};

/**
 * Versión compacta de ColorSwatch para vistas previas de tarjetas
 */
const ColorSwatchMini = ({ hex }) => {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.25rem',
        padding: '0.15rem 0.4rem',
        background: 'rgba(30, 41, 59, 0.6)',
        borderRadius: '6px',
        border: `1px solid ${hex}40`,
        fontSize: '0.75rem',
      }}
    >
      <span
        style={{
          width: '14px',
          height: '14px',
          background: hex,
          borderRadius: '3px',
          boxShadow: `0 1px 3px ${hex}50`,
          border: '1px solid rgba(255, 255, 255, 0.2)',
          flexShrink: 0,
        }}
      />
      <code style={{ color: '#94a3b8', fontSize: '0.7rem' }}>{hex}</code>
    </span>
  );
};

/**
 * Versión compacta de GeometryShape para vistas previas
 */
const GeometryShapeMini = ({ content }) => {
  const shapeMatch = content.match(/([⬤●◯○▲△■□◆◇★☆▼▽◀◁▶▷])\s*(Círculo|Cuadrado|Triángulo|Rectángulo|Línea|Punto|Estrella|Flecha|Rombo)\s*\((#[a-fA-F0-9]{6})(?:,\s*pos:\s*(\d+),(\d+))?\)/i);
  
  if (!shapeMatch) {
    return <span style={{ fontSize: '0.75rem' }}>{content}</span>;
  }

  const [, , shapeName, color] = shapeMatch;
  
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.25rem',
      padding: '0.15rem 0.4rem',
      background: `${color}15`,
      borderRadius: '6px',
      border: `1px solid ${color}40`,
      fontSize: '0.75rem',
    }}>
      <svg width="14" height="14" viewBox="0 0 20 20" style={{ flexShrink: 0 }}>
        {shapeName.toLowerCase() === 'círculo' ? (
          <circle cx="10" cy="10" r="8" fill={color} />
        ) : shapeName.toLowerCase() === 'cuadrado' ? (
          <rect x="2" y="2" width="16" height="16" fill={color} />
        ) : shapeName.toLowerCase() === 'triángulo' ? (
          <polygon points="10,2 18,18 2,18" fill={color} />
        ) : (
          <circle cx="10" cy="10" r="8" fill={color} />
        )}
      </svg>
      <span style={{ color: '#94a3b8' }}>{shapeName}</span>
    </span>
  );
};

/**
 * Mini indicador de código para preview
 */
const CodeBlockMini = ({ lang, content }) => (
  <span style={{
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.25rem',
    padding: '0.15rem 0.4rem',
    background: 'rgba(20, 184, 166, 0.15)',
    borderRadius: '6px',
    border: '1px solid rgba(20, 184, 166, 0.3)',
    fontSize: '0.7rem',
  }}>
    <span style={{ color: '#5eead4' }}>💻</span>
    <code style={{ color: '#5eead4' }}>{lang || 'code'}</code>
    <span style={{ color: '#94a3b8', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
      {content?.slice(0, 30)}...
    </span>
  </span>
);

/**
 * Mini indicador de fórmula química para preview
 */
const ChemicalFormulaMini = ({ formula }) => (
  <span style={{
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.25rem',
    padding: '0.15rem 0.4rem',
    background: 'rgba(16, 185, 129, 0.15)',
    borderRadius: '6px',
    border: '1px solid rgba(16, 185, 129, 0.3)',
    fontSize: '0.75rem',
  }}>
    <span style={{ color: '#6ee7b7' }}>⚗️</span>
    <span style={{ 
      color: '#6ee7b7', 
      fontFamily: 'monospace',
      letterSpacing: '-0.5px',
    }}>
      {formula.replace(/(\d+)/g, '₍$1₎').replace(/₍/g, '').replace(/₎/g, '')}
    </span>
  </span>
);

/**
 * Mini indicador de SMILES para preview
 */
const SmilesMini = ({ smiles }) => (
  <span style={{
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.25rem',
    padding: '0.15rem 0.4rem',
    background: 'rgba(236, 72, 153, 0.15)',
    borderRadius: '6px',
    border: '1px solid rgba(236, 72, 153, 0.3)',
    fontSize: '0.7rem',
  }}>
    <span style={{ color: '#f472b6' }}>🧬</span>
    <code style={{ color: '#f472b6', maxWidth: '80px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
      {smiles.slice(0, 20)}{smiles.length > 20 ? '...' : ''}
    </code>
  </span>
);

/**
 * Versión compacta de renderMixedContent para vistas previas en tarjetas
 * Muestra colores, geometría, LaTeX, código y fórmulas químicas de forma más pequeña
 * @param {string} text - Texto con contenido mixto
 * @param {object} options - Opciones adicionales (imagenes, tipo, etc.)
 * @returns {React.ReactNode} - Contenido renderizado de forma compacta
 */
export const renderMixedContentPreview = (text, options = {}) => {
  if (!text) return null;

  try {
    const parts = [];
    let currentIndex = 0;

    // Regex simplificado para detectar elementos especiales (sin lookbehind para compatibilidad)
    const combinedRegex =
      /\[COLORMIX:((?:#[a-fA-F0-9]{6}\+?)+)=(#[a-fA-F0-9]{6})\]|\[COLORS:((?:#[a-fA-F0-9]{6}\+?)+)\]|\[COLOR:(#[a-fA-F0-9]{6}|#[a-fA-F0-9]{3})\]|\$\$([^\$]+)\$\$|\$([^\$]+)\$|(\\begin\{[a-zA-Z]+\}[\s\S]*?\\end\{[a-zA-Z]+\})|([⬤●◯○▲△■□◆◇★☆▼▽◀◁▶▷]\s*(?:Círculo|Cuadrado|Triángulo|Rectángulo|Línea|Punto|Estrella|Flecha|Rombo)\s*\(#[a-fA-F0-9]{6}[^)]*\))|```(\w*)\n?([\s\S]*?)```|\[SMILES:([^\]]+)\]/g;
    let match;

    while ((match = combinedRegex.exec(text)) !== null) {
      if (match.index > currentIndex) {
        parts.push({ type: "text", content: text.slice(currentIndex, match.index) });
      }

      if (match[1] && match[2]) {
        // COLORMIX - mostrar solo colores mini
        const colors = match[1].split("+").filter((c) => c);
        parts.push({ type: "colormix", colors, result: match[2] });
      } else if (match[3]) {
        // COLORS - múltiples colores mini
        const colors = match[3].split("+").filter((c) => c);
        parts.push({ type: "colors", colors });
      } else if (match[4]) {
        // COLOR - un solo color mini
        parts.push({ type: "color", content: match[4] });
      } else if (match[5]) {
        // Display math $$...$$ - mostrar inline
        parts.push({ type: "math", content: match[5] });
      } else if (match[6]) {
        // Inline math $...$
        parts.push({ type: "math", content: match[6] });
      } else if (match[7]) {
        // LaTeX puro (como \begin{pmatrix})
        parts.push({ type: "math", content: match[7] });
      } else if (match[8]) {
        // Geometría
        parts.push({ type: "geometry", content: match[8] });
      } else if (match[9] !== undefined || match[10]) {
        // Código ```lang\n...```
        parts.push({ type: "code", lang: match[9], content: match[10] });
      } else if (match[11]) {
        // SMILES [SMILES:...]
        parts.push({ type: "smiles", content: match[11] });
      }

      currentIndex = match.index + match[0].length;
    }

    if (currentIndex < text.length) {
      parts.push({ type: "text", content: text.slice(currentIndex) });
    }

    if (parts.length === 0) return <span>{text}</span>;

    return (
      <span style={{ display: 'inline-flex', flexWrap: 'wrap', alignItems: 'center', gap: '0.25rem' }}>
        {parts.map((part, idx) => {
          if (part.type === "math") {
            try {
              return <InlineMath key={idx} math={part.content} />;
            } catch (e) {
              return <code key={idx} style={{ color: '#a78bfa', fontSize: '0.75rem' }}>LaTeX</code>;
            }
          } else if (part.type === "color") {
            return <ColorSwatchMini key={idx} hex={part.content} />;
          } else if (part.type === "colors") {
            return (
              <span key={idx} style={{ display: 'inline-flex', gap: '0.15rem', alignItems: 'center' }}>
                {part.colors.slice(0, 3).map((c, i) => (
                  <span key={i} style={{
                    width: '12px',
                    height: '12px',
                    background: c,
                    borderRadius: '3px',
                    border: '1px solid rgba(255,255,255,0.2)',
                  }} title={c} />
                ))}
                {part.colors.length > 3 && <span style={{ color: '#94a3b8', fontSize: '0.7rem' }}>+{part.colors.length - 3}</span>}
              </span>
            );
          } else if (part.type === "colormix") {
            return (
              <span key={idx} style={{ display: 'inline-flex', gap: '0.15rem', alignItems: 'center' }}>
                {part.colors.map((c, i) => (
                  <span key={i} style={{
                    width: '10px',
                    height: '10px',
                    background: c,
                    borderRadius: '2px',
                  }} />
                ))}
                <span style={{ color: '#6ee7b7', fontSize: '0.7rem' }}>→</span>
                <span style={{
                  width: '14px',
                  height: '14px',
                  background: part.result,
                  borderRadius: '3px',
                  border: '1px solid rgba(255,255,255,0.2)',
                }} />
              </span>
            );
          } else if (part.type === "geometry") {
            return <GeometryShapeMini key={idx} content={part.content} />;
          } else if (part.type === "code") {
            return <CodeBlockMini key={idx} lang={part.lang} content={part.content} />;
          } else if (part.type === "smiles") {
            return <SmilesMini key={idx} smiles={part.content} />;
          } else if (part.type === "chemical") {
            return <ChemicalFormulaMini key={idx} formula={part.content} />;
          } else {
            return <span key={idx}>{part.content}</span>;
          }
        })}
      </span>
    );
  } catch (error) {
    // Si hay cualquier error, mostrar texto plano
    console.warn("Error en renderMixedContentPreview:", error);
    return <span>{text}</span>;
  }
};

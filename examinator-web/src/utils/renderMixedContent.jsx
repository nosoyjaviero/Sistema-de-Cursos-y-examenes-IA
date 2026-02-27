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
 * @param {string} text - Texto con LaTeX y colores embebidos
 * @returns {React.ReactNode} - Componentes renderizados
 */
export const renderMixedContent = (text) => {
  if (!text) return null;

  const parts = [];
  let currentIndex = 0;

  // Regex combinada para LaTeX y colores (orden importa - más específicos primero)
  // 1. COLORMIX: [COLORMIX:#hex1+#hex2=#result]
  // 2. COLORS: [COLORS:#hex1+#hex2+...]
  // 3. COLOR: [COLOR:#hex]
  // 4. Display math: $$...$$
  // 5. Inline math: $...$
  const combinedRegex =
    /\[COLORMIX:((?:#[a-fA-F0-9]{6}\+?)+)=(#[a-fA-F0-9]{6})\]|\[COLORS:((?:#[a-fA-F0-9]{6}\+?)+)\]|\[COLOR:(#[a-fA-F0-9]{6}|#[a-fA-F0-9]{3})\]|\$\$([^\$]+)\$\$|\$([^\$]+)\$/g;
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
      return <BlockMath key={idx} math={part.content} />;
    } else if (part.type === "inline") {
      return <InlineMath key={idx} math={part.content} />;
    } else if (part.type === "color") {
      return <ColorSwatch key={idx} hex={part.content} />;
    } else if (part.type === "colors") {
      return <ColorCombination key={idx} colors={part.colors} />;
    } else if (part.type === "colormix") {
      return <ColorMix key={idx} colors={part.colors} result={part.result} />;
    } else {
      return <span key={idx}>{part.content}</span>;
    }
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

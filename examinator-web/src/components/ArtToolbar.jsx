import { useState } from "react";
import ShapeEditor from "./ShapeEditor";

const ArtToolbar = ({ onInsertElement }) => {
  const [activeTab, setActiveTab] = useState("editor");

  // Estado para el selector de colores
  const [colorInput, setColorInput] = useState("#ff5733");
  const [colorFormat, setColorFormat] = useState("hex");

  // Estado para múltiples colores (combinaciones/mezclas)
  const [coloresSeleccionados, setColoresSeleccionados] = useState([]);

  // Funciones de conversión de colores
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

  const rgbToHex = (r, g, b) => {
    return (
      "#" +
      [r, g, b]
        .map((x) => {
          const hex = Math.max(0, Math.min(255, Math.round(x))).toString(16);
          return hex.length === 1 ? "0" + hex : hex;
        })
        .join("")
    );
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

  const cmykToRgb = (c, m, y, k) => {
    const r = 255 * (1 - c / 100) * (1 - k / 100);
    const g = 255 * (1 - m / 100) * (1 - k / 100);
    const b = 255 * (1 - y / 100) * (1 - k / 100);
    return { r: Math.round(r), g: Math.round(g), b: Math.round(b) };
  };

  const parseColorInput = (input, format) => {
    try {
      if (format === "hex") {
        const hex = input.startsWith("#") ? input : "#" + input;
        const rgb = hexToRgb(hex);
        if (rgb) return { hex, rgb, cmyk: rgbToCmyk(rgb.r, rgb.g, rgb.b) };
      } else if (format === "rgb" || format === "rgba") {
        const match = input.match(
          /(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?/,
        );
        if (match) {
          const r = parseInt(match[1]),
            g = parseInt(match[2]),
            b = parseInt(match[3]);
          const a = match[4] ? parseFloat(match[4]) : 1;
          return {
            hex: rgbToHex(r, g, b),
            rgb: { r, g, b, a },
            cmyk: rgbToCmyk(r, g, b),
          };
        }
      } else if (format === "cmyk") {
        const match = input.match(/(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
        if (match) {
          const c = parseInt(match[1]),
            m = parseInt(match[2]),
            y = parseInt(match[3]),
            k = parseInt(match[4]);
          const rgb = cmykToRgb(c, m, y, k);
          return {
            hex: rgbToHex(rgb.r, rgb.g, rgb.b),
            rgb,
            cmyk: { c, m, y, k },
          };
        }
      }
    } catch (e) {
      console.error("Error parsing color:", e);
    }
    return null;
  };

  const currentColor = parseColorInput(colorInput, colorFormat);

  // Función para mezclar colores (mezcla sustractiva para pinturas)
  const mezclarColores = (hexColors) => {
    if (hexColors.length === 0) return null;
    if (hexColors.length === 1) return hexColors[0];

    // Mezcla sustractiva (simulación de pinturas)
    // Usa modelo CMYK para mezcla más realista
    let totalC = 0,
      totalM = 0,
      totalY = 0,
      totalK = 0;

    hexColors.forEach((hex) => {
      const rgb = hexToRgb(hex);
      if (rgb) {
        const cmyk = rgbToCmyk(rgb.r, rgb.g, rgb.b);
        totalC += cmyk.c;
        totalM += cmyk.m;
        totalY += cmyk.y;
        totalK += cmyk.k;
      }
    });

    // Promediar y limitar valores
    const n = hexColors.length;
    const avgC = Math.min(100, totalC / n);
    const avgM = Math.min(100, totalM / n);
    const avgY = Math.min(100, totalY / n);
    const avgK = Math.min(100, totalK / n + (n - 1) * 5); // Oscurece ligeramente la mezcla

    const rgbResult = cmykToRgb(avgC, avgM, avgY, Math.min(100, avgK));
    return rgbToHex(rgbResult.r, rgbResult.g, rgbResult.b);
  };

  // Agregar color a la lista de combinación
  const agregarColorACombi = () => {
    if (currentColor && !coloresSeleccionados.includes(currentColor.hex)) {
      setColoresSeleccionados([...coloresSeleccionados, currentColor.hex]);
    }
  };

  // Quitar color de la lista
  const quitarColorDeCombi = (hexToRemove) => {
    setColoresSeleccionados(
      coloresSeleccionados.filter((c) => c !== hexToRemove),
    );
  };

  // Color mezclado resultante
  const colorMezclado = mezclarColores(coloresSeleccionados);

  const tabs = [
    { id: "editor", nombre: "✏️ Editor", color: "#a855f7" },
    { id: "figuras", nombre: "🔷 Figuras", color: "#3b82f6" },
    { id: "paletas", nombre: "🎨 Paletas", color: "#ec4899" },
    { id: "colores", nombre: "🌈 Colores", color: "#f43f5e" },
    { id: "composiciones", nombre: "📐 Layouts", color: "#8b5cf6" },
    { id: "estilos", nombre: "🖼️ Estilos", color: "#f59e0b" },
    { id: "iconos", nombre: "✨ Iconos", color: "#10b981" },
  ];

  const elementos = {
    figuras: [
      { nombre: "Círculo", simbolo: "●", template: "⬤ (tamaño: □)" },
      { nombre: "Cuadrado", simbolo: "■", template: "◼ (tamaño: □)" },
      { nombre: "Triángulo", simbolo: "▲", template: "▲ (tamaño: □)" },
      { nombre: "Rectángulo", simbolo: "▭", template: "▬ (ancho: □, alto: □)" },
      {
        nombre: "Rectángulo redondeado",
        simbolo: "▢",
        template: "▢ (ancho: □, alto: □, radio: □)",
      },
      { nombre: "Línea recta", simbolo: "─", template: "━━━━━ (longitud: □)" },
      {
        nombre: "Línea curva",
        simbolo: "〰",
        template: "〰️〰️〰️ (amplitud: □)",
      },
      { nombre: "Flecha derecha", simbolo: "→", template: "➡️ (tamaño: □)" },
      { nombre: "Flecha izquierda", simbolo: "←", template: "⬅️ (tamaño: □)" },
      { nombre: "Flecha arriba", simbolo: "↑", template: "⬆️ (tamaño: □)" },
      { nombre: "Flecha abajo", simbolo: "↓", template: "⬇️ (tamaño: □)" },
      {
        nombre: "Estrella",
        simbolo: "★",
        template: "⭐ (tamaño: □, puntas: □)",
      },
    ],
    paletas: [
      {
        nombre: "Pastel",
        colores: ["#ffd1dc", "#ffb3ba", "#bae1ff", "#baffc9", "#ffffba"],
        preview: "🧁",
        descripcion: "Suaves y delicados",
      },
      {
        nombre: "Neón",
        colores: ["#ff00ff", "#00ffff", "#ffff00", "#ff1493", "#00ff00"],
        preview: "⚡",
        descripcion: "Vibrantes y brillantes",
      },
      {
        nombre: "Tierra",
        colores: ["#8b4513", "#d2691e", "#daa520", "#cd853f", "#f4a460"],
        preview: "🌍",
        descripcion: "Cálidos y naturales",
      },
      {
        nombre: "Retro",
        colores: ["#ff6b6b", "#4ecdc4", "#ffe66d", "#a8e6cf", "#ff8b94"],
        preview: "📻",
        descripcion: "Vintage años 70-80",
      },
      {
        nombre: "Minimalista",
        colores: ["#000000", "#ffffff", "#808080", "#c0c0c0", "#404040"],
        preview: "⬛",
        descripcion: "Blanco y negro elegante",
      },
      {
        nombre: "Acuarela",
        colores: ["#a8dadc", "#f1faee", "#e63946", "#f4a261", "#2a9d8f"],
        preview: "🎨",
        descripcion: "Suaves y artísticos",
      },
      {
        nombre: "Alto contraste",
        colores: ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff"],
        preview: "🌈",
        descripcion: "Máxima visibilidad",
      },
      {
        nombre: "Océano",
        colores: ["#006994", "#1a8cba", "#5eb3d6", "#a2d5e8", "#d0ecf5"],
        preview: "🌊",
        descripcion: "Azules profundos",
      },
    ],
    composiciones: [
      {
        nombre: "2 Columnas equilibradas",
        simbolo: "▮▮",
        template: `
┌────────┬────────┐
│        │        │
│   □    │   □    │
│        │        │
└────────┴────────┘`,
        descripcion: "División vertical 50/50",
      },
      {
        nombre: "Caja + Texto",
        simbolo: "▯T",
        template: `
┌─────────┐
│    □    │
├─────────┤
│ Texto:  │
│ □       │
└─────────┘`,
        descripcion: "Elemento visual arriba",
      },
      {
        nombre: "Dos bloques + Icono",
        simbolo: "⊞⊞",
        template: `
      ★
┌──────┐┌──────┐
│  □   ││  □   │
└──────┘└──────┘`,
        descripcion: "Icono central superior",
      },
      {
        nombre: "Figura + Descripción",
        simbolo: "●→",
        template: `
    ●  →  □ Título
          □ Texto
          □ Detalle`,
        descripcion: "Concepto lateral izquierdo",
      },
      {
        nombre: "División diagonal",
        simbolo: "◢◣",
        template: `
┌──────────┐
│  □   ╱   │
│    ╱  □  │
│  ╱       │
└──────────┘`,
        descripcion: "Elegante y dinámica",
      },
      {
        nombre: "Grid 3×3",
        simbolo: "⊞",
        template: `
┌───┬───┬───┐
│ □ │ □ │ □ │
├───┼───┼───┤
│ □ │ □ │ □ │
├───┼───┼───┤
│ □ │ □ │ □ │
└───┴───┴───┘`,
        descripcion: "Cuadrícula organizada",
      },
      {
        nombre: "Timeline horizontal",
        simbolo: "━●━",
        template: `
□──●──□──●──□──●──□
1     2     3     4`,
        descripcion: "Línea de tiempo",
      },
      {
        nombre: "Pirámide",
        simbolo: "△",
        template: `
        ▲
       ▲ ▲
      ▲ ▲ ▲
     □ □ □ □`,
        descripcion: "Jerarquía visual",
      },
    ],
    estilos: [
      {
        nombre: "Impresionismo",
        simbolo: "🌅",
        filtro: "blur(0.5px) brightness(1.1) saturate(1.3)",
        descripcion: "Monet - Luz y pinceladas sueltas",
      },
      {
        nombre: "Cubismo",
        simbolo: "📐",
        filtro: "contrast(1.3) saturate(0.8)",
        descripcion: "Picasso - Geometría fragmentada",
      },
      {
        nombre: "Surrealismo",
        simbolo: "🌙",
        filtro: "hue-rotate(30deg) saturate(1.5)",
        descripcion: "Dalí - Onírico e ilógico",
      },
      {
        nombre: "Barroco",
        simbolo: "👑",
        filtro: "brightness(0.9) contrast(1.4) sepia(0.2)",
        descripcion: "Caravaggio - Drama y luz",
      },
      {
        nombre: "Modernismo",
        simbolo: "🏛️",
        filtro: "saturate(0.7) brightness(1.05)",
        descripcion: "Klimt - Elegancia decorativa",
      },
      {
        nombre: "Bauhaus",
        simbolo: "▲■●",
        filtro: "contrast(1.5) saturate(1.2)",
        descripcion: "Minimalista - Formas puras",
      },
      {
        nombre: "Ukiyo-e",
        simbolo: "🌸",
        filtro: "saturate(1.4) contrast(1.1)",
        descripcion: "Hokusai - Grabados japoneses",
      },
      {
        nombre: "Pop Art",
        simbolo: "💥",
        filtro: "contrast(1.6) saturate(2) brightness(1.1)",
        descripcion: "Warhol - Colores vibrantes",
      },
    ],
    iconos: [
      { nombre: "Pincel", simbolo: "🖌️", descripcion: "Herramienta artística" },
      { nombre: "Paleta", simbolo: "🎨", descripcion: "Mezcla de colores" },
      {
        nombre: "Busto clásico",
        simbolo: "🗿",
        descripcion: "Escultura antigua",
      },
      { nombre: "Marco", simbolo: "🖼️", descripcion: "Obra enmarcada" },
      { nombre: "Museo", simbolo: "🏛️", descripcion: "Institución cultural" },
      { nombre: "Estatua", simbolo: "🗽", descripcion: "Escultura monumental" },
      { nombre: "Cámara", simbolo: "📷", descripcion: "Fotografía artística" },
      { nombre: "Ojo", simbolo: "👁️", descripcion: "Percepción visual" },
      { nombre: "Corona", simbolo: "👑", descripcion: "Arte clásico" },
      { nombre: "Estrella", simbolo: "⭐", descripcion: "Obra destacada" },
      { nombre: "Luz", simbolo: "💡", descripcion: "Iluminación" },
      { nombre: "Corazón", simbolo: "❤️", descripcion: "Emoción artística" },
    ],
  };

  const tabActual = tabs.find((t) => t.id === activeTab);

  return (
    <div style={{ width: "100%" }}>
      {/* Tabs superiores */}
      <div
        style={{
          display: "flex",
          gap: "0.5rem",
          marginBottom: "1rem",
          borderBottom: "2px solid rgba(255, 255, 255, 0.1)",
          paddingBottom: "0.5rem",
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: "0.6rem 1.2rem",
              background:
                activeTab === tab.id
                  ? `linear-gradient(135deg, ${tab.color}30, ${tab.color}15)`
                  : "transparent",
              border:
                activeTab === tab.id
                  ? `2px solid ${tab.color}`
                  : "2px solid transparent",
              borderRadius: "8px",
              color: activeTab === tab.id ? tab.color : "#94a3b8",
              cursor: "pointer",
              fontSize: "0.9rem",
              fontWeight: activeTab === tab.id ? "600" : "500",
              transition: "all 0.2s",
              whiteSpace: "nowrap",
            }}
          >
            {tab.nombre}
          </button>
        ))}
      </div>

      {/* Contenido del tab activo */}
      {/* TAB DE EDITOR GRÁFICO SVG */}
      {activeTab === "editor" && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
          }}
        >
          <div
            style={{
              background: "rgba(168, 85, 247, 0.1)",
              padding: "1rem",
              borderRadius: "10px",
              border: "1px solid rgba(168, 85, 247, 0.3)",
            }}
          >
            <h3
              style={{
                color: "#e9d5ff",
                margin: "0 0 0.5rem 0",
                fontSize: "1rem",
              }}
            >
              ✏️ Editor de Figuras Geométricas
            </h3>
            <p style={{ color: "#94a3b8", fontSize: "0.85rem", margin: 0 }}>
              Crea composiciones con círculos, cuadrados, triángulos, líneas y
              más. Haz clic en el canvas blanco para agregar figuras,
              selecciónalas para editar su tamaño y color.
            </p>
          </div>
          <ShapeEditor onInsert={(texto) => onInsertElement(texto)} />
        </div>
      )}

      {activeTab === "figuras" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))",
            gap: "0.75rem",
          }}
        >
          {elementos.figuras.map((fig, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onInsertElement(fig.template)}
              style={{
                padding: "1rem",
                background:
                  "linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.03))",
                border: "2px solid rgba(59, 130, 246, 0.2)",
                borderRadius: "10px",
                cursor: "pointer",
                transition: "all 0.2s",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "0.5rem",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.08))";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.03))";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div style={{ fontSize: "2rem", color: "#60a5fa" }}>
                {fig.simbolo}
              </div>
              <div
                style={{
                  fontSize: "0.75rem",
                  color: "#94a3b8",
                  textAlign: "center",
                }}
              >
                {fig.nombre}
              </div>
            </button>
          ))}
        </div>
      )}

      {activeTab === "paletas" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
            gap: "1rem",
          }}
        >
          {elementos.paletas.map((pal, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                const paletaTexto = `🎨 Paleta ${pal.nombre} (${pal.descripcion}):\n${pal.colores.map((c, i) => `█ ${c}`).join(" ")}`;
                onInsertElement(paletaTexto);
              }}
              style={{
                padding: "1rem",
                background:
                  "linear-gradient(135deg, rgba(236, 72, 153, 0.08), rgba(236, 72, 153, 0.03))",
                border: "2px solid rgba(236, 72, 153, 0.2)",
                borderRadius: "10px",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(236, 72, 153, 0.08))";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(236, 72, 153, 0.08), rgba(236, 72, 153, 0.03))";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>
                {pal.preview}
              </div>
              <div
                style={{
                  fontSize: "0.85rem",
                  color: "#f9a8d4",
                  fontWeight: "600",
                  marginBottom: "0.5rem",
                }}
              >
                {pal.nombre}
              </div>
              <div
                style={{
                  fontSize: "0.7rem",
                  color: "#94a3b8",
                  marginBottom: "0.75rem",
                }}
              >
                {pal.descripcion}
              </div>
              <div
                style={{
                  display: "flex",
                  gap: "4px",
                  justifyContent: "center",
                }}
              >
                {pal.colores.map((color, i) => (
                  <div
                    key={i}
                    style={{
                      width: "24px",
                      height: "24px",
                      background: color,
                      borderRadius: "4px",
                      border: "1px solid rgba(255, 255, 255, 0.2)",
                    }}
                  />
                ))}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* 🌈 TAB DE COLORES PERSONALIZADOS */}
      {activeTab === "colores" && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "1.5rem",
          }}
        >
          {/* Selector de formato */}
          <div
            style={{
              display: "flex",
              gap: "0.5rem",
              flexWrap: "wrap",
            }}
          >
            {["hex", "rgb", "rgba", "cmyk"].map((fmt) => (
              <button
                key={fmt}
                type="button"
                onClick={() => setColorFormat(fmt)}
                style={{
                  padding: "0.5rem 1rem",
                  background:
                    colorFormat === fmt
                      ? "linear-gradient(135deg, rgba(244, 63, 94, 0.2), rgba(244, 63, 94, 0.1))"
                      : "rgba(100, 116, 139, 0.1)",
                  border:
                    colorFormat === fmt
                      ? "2px solid #f43f5e"
                      : "2px solid rgba(148, 163, 184, 0.2)",
                  borderRadius: "8px",
                  color: colorFormat === fmt ? "#fb7185" : "#94a3b8",
                  cursor: "pointer",
                  fontSize: "0.85rem",
                  fontWeight: "600",
                  textTransform: "uppercase",
                }}
              >
                {fmt}
              </button>
            ))}
          </div>

          {/* Input de color */}
          <div
            style={{
              display: "flex",
              gap: "1rem",
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >
            <div style={{ flex: 1, minWidth: "200px" }}>
              <label
                style={{
                  display: "block",
                  color: "#94a3b8",
                  fontSize: "0.8rem",
                  marginBottom: "0.5rem",
                }}
              >
                {colorFormat === "hex" && "Introduce color HEX (ej: #ff5733)"}
                {colorFormat === "rgb" && "Introduce RGB (ej: 255, 87, 51)"}
                {colorFormat === "rgba" &&
                  "Introduce RGBA (ej: 255, 87, 51, 0.8)"}
                {colorFormat === "cmyk" && "Introduce CMYK (ej: 0, 66, 80, 0)"}
              </label>
              <input
                type="text"
                value={colorInput}
                onChange={(e) => setColorInput(e.target.value)}
                placeholder={
                  colorFormat === "hex"
                    ? "#ff5733"
                    : colorFormat === "rgb"
                      ? "255, 87, 51"
                      : colorFormat === "rgba"
                        ? "255, 87, 51, 0.8"
                        : "0, 66, 80, 0"
                }
                style={{
                  width: "100%",
                  padding: "0.75rem 1rem",
                  background: "rgba(30, 41, 59, 0.6)",
                  border: "2px solid rgba(244, 63, 94, 0.3)",
                  borderRadius: "8px",
                  color: "#e2e8f0",
                  fontSize: "1rem",
                  fontFamily: "monospace",
                }}
              />
            </div>

            {/* Color picker nativo */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "0.25rem",
              }}
            >
              <label style={{ color: "#94a3b8", fontSize: "0.75rem" }}>
                Selector
              </label>
              <input
                type="color"
                value={currentColor?.hex || "#ff5733"}
                onChange={(e) => {
                  setColorFormat("hex");
                  setColorInput(e.target.value);
                }}
                style={{
                  width: "50px",
                  height: "50px",
                  border: "none",
                  borderRadius: "8px",
                  cursor: "pointer",
                }}
              />
            </div>
          </div>

          {/* Vista previa del color */}
          {currentColor && (
            <div
              style={{
                background: "rgba(30, 41, 59, 0.5)",
                padding: "1.5rem",
                borderRadius: "12px",
                border: "2px solid rgba(244, 63, 94, 0.2)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  gap: "1.5rem",
                  alignItems: "flex-start",
                  flexWrap: "wrap",
                }}
              >
                {/* Muestra grande del color */}
                <div
                  style={{
                    width: "120px",
                    height: "120px",
                    background: currentColor.hex,
                    borderRadius: "12px",
                    boxShadow: `0 4px 20px ${currentColor.hex}40`,
                    border: "3px solid rgba(255, 255, 255, 0.2)",
                    flexShrink: 0,
                  }}
                />

                {/* Valores en todos los formatos */}
                <div style={{ flex: 1, minWidth: "200px" }}>
                  <h4
                    style={{
                      color: "#f43f5e",
                      marginBottom: "1rem",
                      fontSize: "1rem",
                    }}
                  >
                    🎨 Conversiones del color
                  </h4>
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.75rem",
                    }}
                  >
                    <div
                      style={{
                        padding: "0.6rem 1rem",
                        background: "rgba(59, 130, 246, 0.1)",
                        borderRadius: "6px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <span style={{ color: "#60a5fa", fontWeight: "600" }}>
                        HEX
                      </span>
                      <code
                        style={{ color: "#e2e8f0", fontFamily: "monospace" }}
                      >
                        {currentColor.hex}
                      </code>
                    </div>
                    <div
                      style={{
                        padding: "0.6rem 1rem",
                        background: "rgba(16, 185, 129, 0.1)",
                        borderRadius: "6px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <span style={{ color: "#10b981", fontWeight: "600" }}>
                        RGB
                      </span>
                      <code
                        style={{ color: "#e2e8f0", fontFamily: "monospace" }}
                      >
                        rgb({currentColor.rgb.r}, {currentColor.rgb.g},{" "}
                        {currentColor.rgb.b})
                      </code>
                    </div>
                    <div
                      style={{
                        padding: "0.6rem 1rem",
                        background: "rgba(139, 92, 246, 0.1)",
                        borderRadius: "6px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <span style={{ color: "#8b5cf6", fontWeight: "600" }}>
                        RGBA
                      </span>
                      <code
                        style={{ color: "#e2e8f0", fontFamily: "monospace" }}
                      >
                        rgba({currentColor.rgb.r}, {currentColor.rgb.g},{" "}
                        {currentColor.rgb.b}, {currentColor.rgb.a || 1})
                      </code>
                    </div>
                    <div
                      style={{
                        padding: "0.6rem 1rem",
                        background: "rgba(245, 158, 11, 0.1)",
                        borderRadius: "6px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <span style={{ color: "#f59e0b", fontWeight: "600" }}>
                        CMYK
                      </span>
                      <code
                        style={{ color: "#e2e8f0", fontFamily: "monospace" }}
                      >
                        cmyk({currentColor.cmyk.c}%, {currentColor.cmyk.m}%,{" "}
                        {currentColor.cmyk.y}%, {currentColor.cmyk.k}%)
                      </code>
                    </div>
                  </div>
                </div>
              </div>

              {/* Botón para insertar */}
              <button
                type="button"
                onClick={() => {
                  const colorTexto =
                    `[COLOR:${currentColor.hex}]\n` +
                    `  HEX: ${currentColor.hex}\n` +
                    `  RGB: rgb(${currentColor.rgb.r}, ${currentColor.rgb.g}, ${currentColor.rgb.b})\n` +
                    `  RGBA: rgba(${currentColor.rgb.r}, ${currentColor.rgb.g}, ${currentColor.rgb.b}, 1)\n` +
                    `  CMYK: cmyk(${currentColor.cmyk.c}%, ${currentColor.cmyk.m}%, ${currentColor.cmyk.y}%, ${currentColor.cmyk.k}%)`;
                  onInsertElement(colorTexto);
                }}
                style={{
                  marginTop: "1.5rem",
                  width: "100%",
                  padding: "0.9rem 1.5rem",
                  background: "linear-gradient(135deg, #f43f5e, #ec4899)",
                  border: "none",
                  borderRadius: "10px",
                  color: "white",
                  fontSize: "1rem",
                  fontWeight: "600",
                  cursor: "pointer",
                  transition: "all 0.2s",
                  boxShadow: "0 4px 15px rgba(244, 63, 94, 0.3)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-2px)";
                  e.currentTarget.style.boxShadow =
                    "0 6px 20px rgba(244, 63, 94, 0.4)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow =
                    "0 4px 15px rgba(244, 63, 94, 0.3)";
                }}
              >
                ➕ Insertar este color
              </button>
            </div>
          )}

          {/* Colores favoritos predefinidos */}
          <div>
            <h4
              style={{
                color: "#fb7185",
                marginBottom: "0.75rem",
                fontSize: "0.9rem",
              }}
            >
              ⭐ Colores rápidos
            </h4>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
              {[
                "#ff0000",
                "#00ff00",
                "#0000ff",
                "#ffff00",
                "#ff00ff",
                "#00ffff",
                "#ff5733",
                "#c70039",
                "#900c3f",
                "#581845",
                "#1a1a2e",
                "#16213e",
              ].map((color, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setColorFormat("hex");
                    setColorInput(color);
                  }}
                  style={{
                    width: "40px",
                    height: "40px",
                    background: color,
                    border:
                      colorInput === color
                        ? "3px solid white"
                        : "2px solid rgba(255, 255, 255, 0.2)",
                    borderRadius: "8px",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                  title={color}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = "scale(1.1)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "scale(1)";
                  }}
                />
              ))}
            </div>
          </div>

          {/* 🎨 SECCIÓN DE COMBINACIÓN/MEZCLA DE COLORES */}
          <div
            style={{
              background: "rgba(139, 92, 246, 0.1)",
              border: "2px solid rgba(139, 92, 246, 0.3)",
              borderRadius: "12px",
              padding: "1.25rem",
            }}
          >
            <h4
              style={{
                color: "#a78bfa",
                marginBottom: "1rem",
                fontSize: "1rem",
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
              }}
            >
              🎨 Combinación de Colores
              <span
                style={{
                  fontSize: "0.75rem",
                  color: "#94a3b8",
                  fontWeight: "normal",
                }}
              >
                (para mezclas y paletas)
              </span>
            </h4>

            {/* Botón para añadir color actual a la combinación */}
            {currentColor && (
              <button
                type="button"
                onClick={agregarColorACombi}
                disabled={coloresSeleccionados.includes(currentColor.hex)}
                style={{
                  width: "100%",
                  padding: "0.7rem 1rem",
                  background: coloresSeleccionados.includes(currentColor.hex)
                    ? "rgba(100, 116, 139, 0.2)"
                    : "linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(59, 130, 246, 0.3))",
                  border: "2px solid rgba(139, 92, 246, 0.4)",
                  borderRadius: "8px",
                  color: coloresSeleccionados.includes(currentColor.hex)
                    ? "#64748b"
                    : "#c4b5fd",
                  cursor: coloresSeleccionados.includes(currentColor.hex)
                    ? "not-allowed"
                    : "pointer",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                  marginBottom: "1rem",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "0.5rem",
                }}
              >
                <span
                  style={{
                    display: "inline-block",
                    width: "20px",
                    height: "20px",
                    background: currentColor.hex,
                    borderRadius: "4px",
                    border: "2px solid white",
                  }}
                />
                {coloresSeleccionados.includes(currentColor.hex)
                  ? "Color ya añadido"
                  : `➕ Añadir ${currentColor.hex} a la combinación`}
              </button>
            )}

            {/* Lista de colores seleccionados */}
            {coloresSeleccionados.length > 0 && (
              <div style={{ marginBottom: "1rem" }}>
                <div
                  style={{
                    display: "flex",
                    gap: "0.5rem",
                    flexWrap: "wrap",
                    marginBottom: "1rem",
                  }}
                >
                  {coloresSeleccionados.map((hex, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "0.25rem",
                        background: "rgba(30, 41, 59, 0.6)",
                        padding: "0.4rem 0.6rem",
                        borderRadius: "8px",
                        border: "1px solid rgba(148, 163, 184, 0.2)",
                      }}
                    >
                      <div
                        style={{
                          width: "28px",
                          height: "28px",
                          background: hex,
                          borderRadius: "6px",
                          border: "2px solid rgba(255, 255, 255, 0.3)",
                        }}
                      />
                      <code style={{ color: "#e2e8f0", fontSize: "0.75rem" }}>
                        {hex}
                      </code>
                      <button
                        type="button"
                        onClick={() => quitarColorDeCombi(hex)}
                        style={{
                          background: "rgba(239, 68, 68, 0.2)",
                          border: "none",
                          borderRadius: "4px",
                          color: "#f87171",
                          cursor: "pointer",
                          fontSize: "0.7rem",
                          padding: "0.2rem 0.4rem",
                          marginLeft: "0.25rem",
                        }}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>

                {/* Si hay 2+ colores, mostrar mezcla */}
                {coloresSeleccionados.length >= 2 && colorMezclado && (
                  <div
                    style={{
                      background: "rgba(16, 185, 129, 0.1)",
                      padding: "1rem",
                      borderRadius: "8px",
                      border: "1px solid rgba(16, 185, 129, 0.3)",
                      marginBottom: "1rem",
                    }}
                  >
                    <div
                      style={{
                        color: "#34d399",
                        fontSize: "0.85rem",
                        marginBottom: "0.5rem",
                        fontWeight: "600",
                      }}
                    >
                      🧪 Resultado de mezcla (simulación pintura):
                    </div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "1rem",
                      }}
                    >
                      {/* Colores originales */}
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "0.25rem",
                        }}
                      >
                        {coloresSeleccionados.map((hex, idx) => (
                          <div
                            key={idx}
                            style={{ display: "flex", alignItems: "center" }}
                          >
                            <div
                              style={{
                                width: "30px",
                                height: "30px",
                                background: hex,
                                borderRadius: "6px",
                                border: "2px solid rgba(255, 255, 255, 0.3)",
                              }}
                            />
                            {idx < coloresSeleccionados.length - 1 && (
                              <span
                                style={{
                                  color: "#94a3b8",
                                  margin: "0 0.25rem",
                                  fontSize: "1.2rem",
                                }}
                              >
                                +
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                      <span style={{ color: "#94a3b8", fontSize: "1.5rem" }}>
                        =
                      </span>
                      {/* Color mezclado */}
                      <div
                        style={{
                          width: "50px",
                          height: "50px",
                          background: colorMezclado,
                          borderRadius: "8px",
                          border: "3px solid rgba(16, 185, 129, 0.5)",
                          boxShadow: `0 4px 15px ${colorMezclado}50`,
                        }}
                      />
                      <code
                        style={{
                          color: "#a7f3d0",
                          fontFamily: "monospace",
                          fontSize: "0.85rem",
                        }}
                      >
                        {colorMezclado}
                      </code>
                    </div>
                  </div>
                )}

                {/* Botones de inserción */}
                <div
                  style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}
                >
                  {/* Insertar combinación (todos los colores) */}
                  <button
                    type="button"
                    onClick={() => {
                      const colorTag = `[COLORS:${coloresSeleccionados.join("+")}]`;
                      onInsertElement(colorTag);
                    }}
                    style={{
                      flex: 1,
                      minWidth: "140px",
                      padding: "0.7rem 1rem",
                      background: "linear-gradient(135deg, #8b5cf6, #6366f1)",
                      border: "none",
                      borderRadius: "8px",
                      color: "white",
                      fontSize: "0.85rem",
                      fontWeight: "600",
                      cursor: "pointer",
                      transition: "all 0.2s",
                    }}
                  >
                    🎨 Insertar combinación
                  </button>

                  {/* Insertar mezcla resultante */}
                  {coloresSeleccionados.length >= 2 && colorMezclado && (
                    <button
                      type="button"
                      onClick={() => {
                        const mixTag = `[COLORMIX:${coloresSeleccionados.join("+")}=${colorMezclado}]`;
                        onInsertElement(mixTag);
                      }}
                      style={{
                        flex: 1,
                        minWidth: "140px",
                        padding: "0.7rem 1rem",
                        background: "linear-gradient(135deg, #10b981, #059669)",
                        border: "none",
                        borderRadius: "8px",
                        color: "white",
                        fontSize: "0.85rem",
                        fontWeight: "600",
                        cursor: "pointer",
                        transition: "all 0.2s",
                      }}
                    >
                      🧪 Insertar mezcla
                    </button>
                  )}

                  {/* Limpiar */}
                  <button
                    type="button"
                    onClick={() => setColoresSeleccionados([])}
                    style={{
                      padding: "0.7rem 1rem",
                      background: "rgba(239, 68, 68, 0.2)",
                      border: "2px solid rgba(239, 68, 68, 0.3)",
                      borderRadius: "8px",
                      color: "#f87171",
                      fontSize: "0.85rem",
                      fontWeight: "600",
                      cursor: "pointer",
                    }}
                  >
                    🗑️ Limpiar
                  </button>
                </div>
              </div>
            )}

            {coloresSeleccionados.length === 0 && (
              <p
                style={{
                  color: "#94a3b8",
                  fontSize: "0.8rem",
                  textAlign: "center",
                  margin: 0,
                }}
              >
                Selecciona un color arriba y haz clic en "Añadir a la
                combinación"
                <br />
                para crear paletas o simular mezclas de pinturas.
              </p>
            )}
          </div>
        </div>
      )}

      {activeTab === "composiciones" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
            gap: "1rem",
          }}
        >
          {elementos.composiciones.map((comp, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onInsertElement(comp.template)}
              style={{
                padding: "1rem",
                background:
                  "linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(139, 92, 246, 0.03))",
                border: "2px solid rgba(139, 92, 246, 0.2)",
                borderRadius: "10px",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(139, 92, 246, 0.08))";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(139, 92, 246, 0.03))";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div
                style={{
                  fontSize: "2rem",
                  color: "#a78bfa",
                  marginBottom: "0.5rem",
                }}
              >
                {comp.simbolo}
              </div>
              <div
                style={{
                  fontSize: "0.85rem",
                  color: "#c4b5fd",
                  fontWeight: "600",
                  marginBottom: "0.25rem",
                }}
              >
                {comp.nombre}
              </div>
              <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>
                {comp.descripcion}
              </div>
            </button>
          ))}
        </div>
      )}

      {activeTab === "estilos" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
            gap: "1rem",
          }}
        >
          {elementos.estilos.map((est, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                const estiloTexto = `🖼️ Estilo: ${est.nombre}\n📝 ${est.descripcion}\n✨ Características: ${est.filtro}`;
                onInsertElement(estiloTexto);
              }}
              style={{
                padding: "1rem",
                background:
                  "linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.03))",
                border: "2px solid rgba(245, 158, 11, 0.2)",
                borderRadius: "10px",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.08))";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.03))";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
                {est.simbolo}
              </div>
              <div
                style={{
                  fontSize: "0.85rem",
                  color: "#fbbf24",
                  fontWeight: "600",
                  marginBottom: "0.25rem",
                }}
              >
                {est.nombre}
              </div>
              <div
                style={{
                  fontSize: "0.7rem",
                  color: "#94a3b8",
                  lineHeight: "1.4",
                }}
              >
                {est.descripcion}
              </div>
            </button>
          ))}
        </div>
      )}

      {activeTab === "iconos" && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))",
            gap: "0.75rem",
          }}
        >
          {elementos.iconos.map((ico, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onInsertElement(ico.simbolo)}
              style={{
                padding: "1rem",
                background:
                  "linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.03))",
                border: "2px solid rgba(16, 185, 129, 0.2)",
                borderRadius: "10px",
                cursor: "pointer",
                transition: "all 0.2s",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "0.5rem",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08))";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.03))";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div style={{ fontSize: "2.5rem" }}>{ico.simbolo}</div>
              <div
                style={{
                  fontSize: "0.75rem",
                  color: "#6ee7b7",
                  fontWeight: "600",
                  textAlign: "center",
                }}
              >
                {ico.nombre}
              </div>
              <div
                style={{
                  fontSize: "0.65rem",
                  color: "#94a3b8",
                  textAlign: "center",
                }}
              >
                {ico.descripcion}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ArtToolbar;

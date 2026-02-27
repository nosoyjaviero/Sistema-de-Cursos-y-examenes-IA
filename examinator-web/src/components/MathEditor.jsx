import {
  useEffect,
  useRef,
  useState,
  useImperativeHandle,
  forwardRef,
} from "react";
import { BlockMath } from "react-katex";
import "katex/dist/katex.min.css";

// Importar MathLive directamente
import "mathlive";

/**
 * Editor Matemático Interactivo DUAL
 *
 * Características:
 * - Modo VISUAL: Editor interactivo estilo Wolfram (MathLive)
 * - Modo CÓDIGO: Textarea para pegar LaTeX de ChatGPT
 * - Vista PREVIA: Renderizado en tiempo real con KaTeX
 * - Sincronización bidireccional entre modos
 */

const MathEditor = forwardRef(
  ({ value, onChange, placeholder = "Escribe matemáticas..." }, ref) => {
    const mathFieldRef = useRef(null);
    const textareaRef = useRef(null);
    const [error, setError] = useState(null);
    const [isMounted, setIsMounted] = useState(false);
    const [mathLiveAvailable, setMathLiveAvailable] = useState(false);

    // Modo de edición: 'visual' | 'codigo'
    const [modoEdicion, setModoEdicion] = useState("visual");

    // Estado para mostrar/ocultar vista previa
    const [mostrarPreview, setMostrarPreview] = useState(true);

    // Exponer funciones al padre
    useImperativeHandle(ref, () => ({
      insertLatex: (latex) => {
        if (modoEdicion === "codigo" || !mathLiveAvailable) {
          // Modo código: insertar en textarea
          const textarea = textareaRef.current;
          if (textarea) {
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const currentValue = textarea.value || "";
            const processedLatex = latex.replace(/#\?/g, "□");
            const newValue =
              currentValue.slice(0, start) +
              processedLatex +
              currentValue.slice(end);
            onChange?.(newValue);
            setTimeout(() => {
              const newCursorPos = start + processedLatex.length;
              textarea.focus();
              textarea.setSelectionRange(newCursorPos, newCursorPos);
            }, 0);
          }
        } else {
          // Modo visual: usar MathLive
          const mathField = mathFieldRef.current;
          if (mathField) {
            mathField.executeCommand(["insert", latex]);
            mathField.focus();
          }
        }
      },
      focus: () => {
        if (modoEdicion === "codigo" || !mathLiveAvailable) {
          textareaRef.current?.focus();
        } else {
          mathFieldRef.current?.focus();
        }
      },
      getValue: () => value || "",
      setMode: (mode) => setModoEdicion(mode),
    }));

    // Verificar disponibilidad de MathLive al montar
    useEffect(() => {
      // MathLive se registra automáticamente al importarse
      // Verificamos que el custom element exista
      const checkReady = () => {
        if (
          typeof customElements !== "undefined" &&
          customElements.get("math-field")
        ) {
          setMathLiveAvailable(true);
          setIsMounted(true);
        } else {
          // Reintentar en caso de que tarde
          setTimeout(checkReady, 100);
        }
      };

      // Dar tiempo a que se registre
      setTimeout(checkReady, 50);

      // Fallback después de 2 segundos
      const fallback = setTimeout(() => {
        if (!isMounted) {
          console.warn(
            "MathLive custom element no detectado, habilitando de todos modos",
          );
          setMathLiveAvailable(true); // Intentar de todos modos
          setIsMounted(true);
        }
      }, 2000);

      return () => clearTimeout(fallback);
    }, []);

    // Configurar MathLive cuando esté disponible
    useEffect(() => {
      if (!isMounted || !mathLiveAvailable || modoEdicion !== "visual") return;

      try {
        if (mathFieldRef.current) {
          const mf = mathFieldRef.current;
          mf.setOptions({
            fontsDirectory: "https://unpkg.com/mathlive/dist/fonts",
            virtualKeyboardMode: "manual",
            smartMode: true,
            smartFence: true,
            smartSuperscript: true,
            removeExtraneousParentheses: true,
            locale: "es-ES",
          });

          if (value) {
            mf.setValue(value);
          }

          const handleInput = () => {
            try {
              const latex = mf.getValue("latex");
              onChange?.(latex);
            } catch (e) {
              console.error("Error getting LaTeX:", e);
            }
          };

          mf.addEventListener("input", handleInput);
          setError(null);

          return () => {
            mf.removeEventListener("input", handleInput);
          };
        }
      } catch (e) {
        console.error("Error initializing MathLive:", e);
        setError("Error al inicializar editor visual");
      }
    }, [onChange, isMounted, mathLiveAvailable, modoEdicion]);

    // Sincronizar valor con MathLive
    useEffect(() => {
      if (!isMounted || !mathLiveAvailable || modoEdicion !== "visual") return;

      try {
        if (
          mathFieldRef.current &&
          value !== mathFieldRef.current.getValue("latex")
        ) {
          mathFieldRef.current.setValue(value || "");
        }
      } catch (e) {
        console.error("Error syncing value:", e);
      }
    }, [value, isMounted, mathLiveAvailable, modoEdicion]);

    // Renderizar vista previa con KaTeX
    const renderPreview = () => {
      if (!value || !mostrarPreview) return null;

      try {
        return (
          <div
            style={{
              background: "rgba(30, 41, 59, 0.8)",
              padding: "1.5rem",
              borderRadius: "8px",
              border: "2px solid rgba(147, 51, 234, 0.3)",
              marginTop: "1rem",
            }}
          >
            <div
              style={{
                color: "#c4b5fd",
                fontSize: "0.85rem",
                fontWeight: "600",
                marginBottom: "1rem",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span>👁️ Vista Previa (así se verá en repaso)</span>
              <button
                type="button"
                onClick={() => setMostrarPreview(false)}
                style={{
                  background: "rgba(239, 68, 68, 0.2)",
                  color: "#fca5a5",
                  border: "1px solid rgba(239, 68, 68, 0.3)",
                  borderRadius: "4px",
                  padding: "2px 8px",
                  fontSize: "0.75rem",
                  cursor: "pointer",
                }}
              >
                ✕ Ocultar
              </button>
            </div>
            <div
              style={{
                background: "rgba(147, 51, 234, 0.08)",
                padding: "1rem",
                borderRadius: "8px",
                fontSize: "1.2rem",
                color: "#e9d5ff",
                textAlign: "center",
                overflowX: "auto",
              }}
            >
              <BlockMath math={value} />
            </div>
          </div>
        );
      } catch (e) {
        return (
          <div
            style={{
              background: "rgba(239, 68, 68, 0.1)",
              padding: "1rem",
              borderRadius: "8px",
              marginTop: "1rem",
              color: "#fca5a5",
              fontSize: "0.9rem",
            }}
          >
            ⚠️ Error de LaTeX: {e.message}
          </div>
        );
      }
    };

    // Botones de modo
    const renderModeButtons = () => (
      <div
        style={{
          display: "flex",
          gap: "0.5rem",
          marginBottom: "1rem",
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <button
          type="button"
          onClick={() => setModoEdicion("visual")}
          disabled={!mathLiveAvailable}
          style={{
            padding: "0.5rem 1rem",
            background:
              modoEdicion === "visual"
                ? "linear-gradient(135deg, #9333ea, #7c3aed)"
                : "rgba(147, 51, 234, 0.1)",
            color: modoEdicion === "visual" ? "#fff" : "#c4b5fd",
            border:
              modoEdicion === "visual"
                ? "1px solid #a855f7"
                : "1px solid rgba(147, 51, 234, 0.3)",
            borderRadius: "8px",
            cursor: mathLiveAvailable ? "pointer" : "not-allowed",
            fontSize: "0.9rem",
            fontWeight: modoEdicion === "visual" ? "600" : "500",
            transition: "all 0.2s",
            opacity: mathLiveAvailable ? 1 : 0.5,
          }}
        >
          🎨 Visual (como en clase)
        </button>

        <button
          type="button"
          onClick={() => setModoEdicion("codigo")}
          style={{
            padding: "0.5rem 1rem",
            background:
              modoEdicion === "codigo"
                ? "linear-gradient(135deg, #9333ea, #7c3aed)"
                : "rgba(147, 51, 234, 0.1)",
            color: modoEdicion === "codigo" ? "#fff" : "#c4b5fd",
            border:
              modoEdicion === "codigo"
                ? "1px solid #a855f7"
                : "1px solid rgba(147, 51, 234, 0.3)",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "0.9rem",
            fontWeight: modoEdicion === "codigo" ? "600" : "500",
            transition: "all 0.2s",
          }}
        >
          📝 Código LaTeX (pegar de ChatGPT)
        </button>

        {!mostrarPreview && (
          <button
            type="button"
            onClick={() => setMostrarPreview(true)}
            style={{
              padding: "0.5rem 1rem",
              background: "rgba(34, 197, 94, 0.1)",
              color: "#86efac",
              border: "1px solid rgba(34, 197, 94, 0.3)",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "0.9rem",
              marginLeft: "auto",
            }}
          >
            👁️ Mostrar preview
          </button>
        )}
      </div>
    );

    // Editor visual (MathLive)
    const renderVisualEditor = () => {
      if (!mathLiveAvailable) {
        return (
          <div
            style={{
              padding: "1rem",
              background: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "8px",
              color: "#fca5a5",
              textAlign: "center",
            }}
          >
            Editor visual no disponible. Usa el modo código.
          </div>
        );
      }

      return (
        <div>
          <div
            style={{
              color: "#86efac",
              fontSize: "0.8rem",
              marginBottom: "0.5rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            ✨ Escribe directamente o usa el toolbar arriba
            <span
              style={{
                background: "rgba(34, 197, 94, 0.2)",
                padding: "2px 8px",
                borderRadius: "4px",
              }}
            >
              TAB para navegar entre □
            </span>
          </div>
          <math-field
            ref={mathFieldRef}
            style={{
              width: "100%",
              minHeight: "150px",
              maxHeight: "300px",
              fontSize: "18px",
              padding: "16px",
              borderRadius: "8px",
              border: "2px solid rgba(147, 51, 234, 0.3)",
              background: "rgba(147, 51, 234, 0.05)",
              color: "#e9d5ff",
              fontFamily: "inherit",
              "--caret-color": "#a855f7",
              "--selection-background-color": "rgba(147, 51, 234, 0.3)",
              "--placeholder-color": "#9333ea80",
              overflowY: "auto",
            }}
          >
            {placeholder}
          </math-field>
        </div>
      );
    };

    // Editor de código LaTeX
    const renderCodeEditor = () => (
      <div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "0.5rem",
          }}
        >
          <div
            style={{
              color: "#93c5fd",
              fontSize: "0.8rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
            }}
          >
            📋 Pega código LaTeX aquí (de ChatGPT, libros, etc.)
          </div>
          <button
            type="button"
            onClick={async () => {
              try {
                const text = await navigator.clipboard.readText();
                const newValue = (value || "") + text;
                onChange?.(newValue);
              } catch (e) {
                console.error("Error leyendo clipboard:", e);
              }
            }}
            style={{
              padding: "4px 12px",
              background: "rgba(59, 130, 246, 0.2)",
              color: "#93c5fd",
              border: "1px solid rgba(59, 130, 246, 0.3)",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "0.8rem",
            }}
          >
            📋 Pegar del portapapeles
          </button>
        </div>

        <textarea
          ref={textareaRef}
          value={value || ""}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder={`Escribe o pega código LaTeX aquí...

Ejemplos:
\\frac{a}{b}     → fracción
x^{2}           → exponente
\\sqrt{x}       → raíz cuadrada
\\int_{a}^{b}   → integral
\\sum_{i=1}^{n} → sumatoria

Puedes pegar LaTeX largo de ChatGPT:`}
          style={{
            width: "100%",
            minHeight: "200px",
            padding: "1rem",
            background: "rgba(30, 41, 59, 0.8)",
            border: "2px solid rgba(59, 130, 246, 0.3)",
            borderRadius: "8px",
            color: "#93c5fd",
            fontFamily: '"Fira Code", "Consolas", monospace',
            fontSize: "0.95rem",
            resize: "vertical",
            outline: "none",
            lineHeight: "1.6",
          }}
          onFocus={(e) => {
            e.target.style.borderColor = "#3b82f6";
            e.target.style.boxShadow = "0 0 10px rgba(59, 130, 246, 0.3)";
          }}
          onBlur={(e) => {
            e.target.style.borderColor = "rgba(59, 130, 246, 0.3)";
            e.target.style.boxShadow = "none";
          }}
        />

        {/* Guía rápida de LaTeX */}
        <details style={{ marginTop: "0.75rem" }}>
          <summary
            style={{
              color: "#c4b5fd",
              fontSize: "0.85rem",
              cursor: "pointer",
              padding: "0.5rem",
              background: "rgba(147, 51, 234, 0.1)",
              borderRadius: "6px",
            }}
          >
            📖 Guía rápida de LaTeX (click para expandir)
          </summary>
          <div
            style={{
              marginTop: "0.5rem",
              padding: "1rem",
              background: "rgba(30, 41, 59, 0.6)",
              borderRadius: "8px",
              fontSize: "0.8rem",
              color: "#94a3b8",
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "1rem",
            }}
          >
            <div>
              <strong style={{ color: "#a5b4fc" }}>Fracciones:</strong>
              <br />
              <code>
                \frac{"{num}"}
                {"{den}"}
              </code>
              <br />
              <code>
                \dfrac{"{a}"}
                {"{b}"}
              </code>{" "}
              (grande)
            </div>
            <div>
              <strong style={{ color: "#a5b4fc" }}>
                Exponentes/Subíndices:
              </strong>
              <br />
              <code>x^{"{2}"}</code> - exponente
              <br />
              <code>a_{"{n}"}</code> - subíndice
            </div>
            <div>
              <strong style={{ color: "#a5b4fc" }}>Raíces:</strong>
              <br />
              <code>\sqrt{"{x}"}</code>
              <br />
              <code>\sqrt[3]{"{x}"}</code> - cúbica
            </div>
            <div>
              <strong style={{ color: "#a5b4fc" }}>Integrales:</strong>
              <br />
              <code>
                \int_{"{a}"}^{"{b}"} f(x)dx
              </code>
              <br />
              <code>\iint, \iiint</code>
            </div>
            <div>
              <strong style={{ color: "#a5b4fc" }}>Límites:</strong>
              <br />
              <code>\lim_{"{x \\to a}"} f(x)</code>
              <br />
              <code>\lim_{"{n \\to \\infty}"}</code>
            </div>
            <div>
              <strong style={{ color: "#a5b4fc" }}>Sumatorias:</strong>
              <br />
              <code>
                \sum_{"{i=1}"}^{"{n}"} a_i
              </code>
              <br />
              <code>
                \prod_{"{i=1}"}^{"{n}"}
              </code>
            </div>
            <div>
              <strong style={{ color: "#a5b4fc" }}>Matrices:</strong>
              <br />
              <code>
                \begin{"{pmatrix}"} a & b \\ c & d \end{"{pmatrix}"}
              </code>
            </div>
            <div>
              <strong style={{ color: "#a5b4fc" }}>Griegos:</strong>
              <br />
              <code>\alpha \beta \gamma \delta</code>
              <br />
              <code>\theta \pi \sigma \omega</code>
            </div>
          </div>
        </details>
      </div>
    );

    if (!isMounted) {
      return (
        <div
          style={{
            padding: "2rem",
            textAlign: "center",
            color: "#c4b5fd",
            background: "rgba(147, 51, 234, 0.05)",
            borderRadius: "8px",
            border: "2px solid rgba(147, 51, 234, 0.3)",
          }}
        >
          ⏳ Cargando editor matemático...
        </div>
      );
    }

    return (
      <div
        style={{
          padding: "1rem",
          background: "rgba(147, 51, 234, 0.05)",
          border: "2px solid rgba(147, 51, 234, 0.3)",
          borderRadius: "12px",
        }}
      >
        {renderModeButtons()}

        {modoEdicion === "visual" ? renderVisualEditor() : renderCodeEditor()}

        {renderPreview()}
      </div>
    );
  },
);

MathEditor.displayName = "MathEditor";

export default MathEditor;

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

    // Modo de edición: 'visual' | 'codigo' | 'documento'
    const [modoEdicion, setModoEdicion] = useState("visual");

    // Estado para mostrar/ocultar vista previa
    const [mostrarPreview, setMostrarPreview] = useState(true);

    // 🔥 Detectar si el contenido es un documento LaTeX completo
    // (que MathLive no puede renderizar)
    const esDocumentoLatexCompleto = (texto) => {
      if (!texto) return false;
      // Patrones que indican documento LaTeX completo (no solo fórmulas)
      const patronesDocumento = [
        /\\documentclass/i,
        /\\begin\s*\{document\}/i,
        /\\end\s*\{document\}/i,
        /\\usepackage/i,
        /\\section\*?\s*\{/i,
        /\\subsection\*?\s*\{/i,
        /\\textbf\s*\{/i,
        /\\title\s*\{/i,
        /\\author\s*\{/i,
      ];
      return patronesDocumento.some(patron => patron.test(texto));
    };

    // 🔥 CONVERTIR documento LaTeX a formato que MathLive puede renderizar
    const convertirDocumentoAMatematicas = (texto) => {
      if (!texto) return "";
      
      let resultado = texto;
      
      // 1. Eliminar preámbulo de documento completo
      resultado = resultado.replace(/\\documentclass(\[.*?\])?\{.*?\}/gi, '');
      resultado = resultado.replace(/\\usepackage(\[.*?\])?\{.*?\}/gi, '');
      resultado = resultado.replace(/\\begin\s*\{document\}/gi, '');
      resultado = resultado.replace(/\\end\s*\{document\}/gi, '');
      resultado = resultado.replace(/\\title\s*\{[^}]*\}/gi, '');
      resultado = resultado.replace(/\\author\s*\{[^}]*\}/gi, '');
      resultado = resultado.replace(/\\date\s*\{[^}]*\}/gi, '');
      resultado = resultado.replace(/\\maketitle/gi, '');
      
      // 2. Convertir secciones y subsecciones a texto matemático
      resultado = resultado.replace(/\\section\*?\s*\{([^}]*)\}/gi, '\\text{\\textbf{$1}}');
      resultado = resultado.replace(/\\subsection\*?\s*\{([^}]*)\}/gi, '\\text{\\textbf{$1}}');
      
      // 3. Convertir \textbf{} a \text{\textbf{}} para math mode
      resultado = resultado.replace(/\\textbf\s*\{([^}]*)\}/gi, '\\text{$1}');
      
      // 4. Extraer contenido de bloques matemáticos \[...\] 
      resultado = resultado.replace(/\\\[/g, '\n');
      resultado = resultado.replace(/\\\]/g, '\n');
      
      // 5. Eliminar $$ delimitadores si existen
      resultado = resultado.replace(/\$\$/g, '');
      resultado = resultado.replace(/\$/g, '');
      
      // 6. Procesar líneas y construir contenido multilínea
      const lineas = resultado.split('\n')
        .map(l => l.trim())
        .filter(l => l.length > 0);
      
      // 7. Envolver en gathered para visualización vertical
      if (lineas.length > 1) {
        const contenidoFormateado = lineas.join(' \\\\\n');
        resultado = `\\begin{gathered}\n${contenidoFormateado}\n\\end{gathered}`;
      } else {
        resultado = lineas.join('');
      }
      
      return resultado;
    };

    // 🔥 Auto-detectar y cambiar modo si es documento LaTeX
    useEffect(() => {
      if (value && esDocumentoLatexCompleto(value) && modoEdicion === "visual") {
        console.log("🔍 Detectado documento LaTeX completo, cambiando a modo código");
        setModoEdicion("codigo");
      }
    }, [value]);


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

      // Dar un pequeño delay para que el math-field se monte correctamente
      const initTimer = setTimeout(() => {
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

            // Establecer el valor si existe - usar setValue con opción específica
            if (value) {
              // Forzar la actualización del valor con un pequeño delay adicional
              setTimeout(() => {
                if (mathFieldRef.current) {
                  mathFieldRef.current.setValue(value, { suppressChangeNotifications: true });
                }
              }, 50);
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

            // Cleanup guardado para el timeout
            mathFieldRef.current._cleanupHandler = () => {
              mf.removeEventListener("input", handleInput);
            };
          }
        } catch (e) {
          console.error("Error initializing MathLive:", e);
          setError("Error al inicializar editor visual");
        }
      }, 100);

      return () => {
        clearTimeout(initTimer);
        if (mathFieldRef.current?._cleanupHandler) {
          mathFieldRef.current._cleanupHandler();
        }
      };
    }, [onChange, isMounted, mathLiveAvailable, modoEdicion, value]);

    // Sincronizar valor con MathLive cuando cambia el valor o el modo
    useEffect(() => {
      if (!isMounted || !mathLiveAvailable || modoEdicion !== "visual") return;

      // Dar tiempo al math-field para montarse en el DOM
      const syncTimer = setTimeout(() => {
        try {
          if (mathFieldRef.current && value) {
            const mf = mathFieldRef.current;
            const currentValue = mf.getValue("latex");
            
            // Solo actualizar si el valor es diferente
            if (value !== currentValue) {
              mf.setValue(value, { suppressChangeNotifications: true });
            }
          }
        } catch (e) {
          console.error("Error syncing value:", e);
        }
      }, 150);
      
      return () => clearTimeout(syncTimer);
    }, [value, isMounted, mathLiveAvailable, modoEdicion]);

    // Renderizar vista previa con KaTeX - maneja documentos LaTeX completos
    const renderPreview = () => {
      if (!value || !mostrarPreview) return null;

      // 🔥 Función para parsear y renderizar documento LaTeX mixto
      const renderContenidoMixto = (texto) => {
        // Limpiar preámbulo de documento
        let contenido = texto
          .replace(/\\documentclass(\[.*?\])?\{.*?\}/gi, '')
          .replace(/\\usepackage(\[.*?\])?\{.*?\}/gi, '')
          .replace(/\\begin\s*\{document\}/gi, '')
          .replace(/\\end\s*\{document\}/gi, '')
          .replace(/\\title\s*\{[^}]*\}/gi, '')
          .replace(/\\author\s*\{[^}]*\}/gi, '')
          .replace(/\\date\s*\{[^}]*\}/gi, '')
          .replace(/\\maketitle/gi, '')
          .trim();

        // Separar en bloques: texto normal vs bloques matemáticos
        const partes = [];
        let resto = contenido;
        
        // Buscar bloques \[...\]
        const regexBloqueMath = /\\\[([\s\S]*?)\\\]/g;
        let match;
        let ultimoIndice = 0;
        
        while ((match = regexBloqueMath.exec(contenido)) !== null) {
          // Texto antes del bloque matemático
          if (match.index > ultimoIndice) {
            const textoAntes = contenido.slice(ultimoIndice, match.index).trim();
            if (textoAntes) {
              partes.push({ tipo: 'texto', contenido: textoAntes });
            }
          }
          // Bloque matemático
          partes.push({ tipo: 'math', contenido: match[1].trim() });
          ultimoIndice = match.index + match[0].length;
        }
        
        // Texto después del último bloque
        if (ultimoIndice < contenido.length) {
          const textoFinal = contenido.slice(ultimoIndice).trim();
          if (textoFinal) {
            partes.push({ tipo: 'texto', contenido: textoFinal });
          }
        }

        // Si no encontró bloques \[...\], buscar $$ ... $$
        if (partes.length === 0) {
          const regexDoubleDollar = /\$\$([\s\S]*?)\$\$/g;
          ultimoIndice = 0;
          while ((match = regexDoubleDollar.exec(contenido)) !== null) {
            if (match.index > ultimoIndice) {
              const textoAntes = contenido.slice(ultimoIndice, match.index).trim();
              if (textoAntes) {
                partes.push({ tipo: 'texto', contenido: textoAntes });
              }
            }
            partes.push({ tipo: 'math', contenido: match[1].trim() });
            ultimoIndice = match.index + match[0].length;
          }
          if (ultimoIndice < contenido.length) {
            const textoFinal = contenido.slice(ultimoIndice).trim();
            if (textoFinal) {
              partes.push({ tipo: 'texto', contenido: textoFinal });
            }
          }
        }

        // Si sigue vacío, es contenido sin delimitadores - intentar renderizar todo como math
        if (partes.length === 0) {
          partes.push({ tipo: 'math', contenido: contenido });
        }

        return partes.map((parte, idx) => {
          if (parte.tipo === 'math') {
            try {
              return (
                <div key={idx} style={{ margin: '0.75rem 0' }}>
                  <BlockMath math={parte.contenido} />
                </div>
              );
            } catch (e) {
              return (
                <div key={idx} style={{ 
                  color: '#fca5a5', 
                  fontFamily: 'monospace',
                  fontSize: '0.85rem',
                  padding: '0.5rem',
                  background: 'rgba(239, 68, 68, 0.1)',
                  borderRadius: '4px',
                  margin: '0.5rem 0',
                }}>
                  ⚠️ Error: {e.message}
                  <pre style={{ marginTop: '0.25rem', opacity: 0.7 }}>{parte.contenido.slice(0, 100)}...</pre>
                </div>
              );
            }
          } else {
            // Procesar texto: convertir \textbf{} a negrita, etc.
            let textoHtml = parte.contenido
              .replace(/\\textbf\s*\{([^}]*)\}/g, '<strong>$1</strong>')
              .replace(/\\section\*?\s*\{([^}]*)\}/g, '<h3 style="color:#a78bfa;margin:0.5rem 0">$1</h3>')
              .replace(/\\subsection\*?\s*\{([^}]*)\}/g, '<h4 style="color:#c4b5fd;margin:0.5rem 0">$1</h4>')
              .replace(/\n/g, '<br/>');
            
            return (
              <div 
                key={idx} 
                style={{ 
                  color: '#e2e8f0', 
                  fontSize: '1rem',
                  margin: '0.5rem 0',
                  lineHeight: '1.6',
                }}
                dangerouslySetInnerHTML={{ __html: textoHtml }}
              />
            );
          }
        });
      };

      try {
        // Si es documento LaTeX completo, usar renderizado mixto
        const usarRenderizadoMixto = esDocumentoLatexCompleto(value) || 
          value.includes('\\[') || 
          value.includes('\\textbf');

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
                overflowX: "auto",
              }}
            >
              {usarRenderizadoMixto ? renderContenidoMixto(value) : <BlockMath math={value} />}
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
          onClick={() => {
            // 🔥 Advertir si es documento LaTeX completo
            if (esDocumentoLatexCompleto(value)) {
              console.warn("⚠️ El contenido es un documento LaTeX completo. El modo visual sólo puede renderizar fórmulas matemáticas puras.");
            }
            setModoEdicion("visual");
          }}
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

        <button
          type="button"
          onClick={() => setModoEdicion("documento")}
          style={{
            padding: "0.5rem 1rem",
            background:
              modoEdicion === "documento"
                ? "linear-gradient(135deg, #10b981, #059669)"
                : "rgba(16, 185, 129, 0.1)",
            color: modoEdicion === "documento" ? "#fff" : "#6ee7b7",
            border:
              modoEdicion === "documento"
                ? "1px solid #10b981"
                : "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "0.9rem",
            fontWeight: modoEdicion === "documento" ? "600" : "500",
            transition: "all 0.2s",
          }}
        >
          📄 Documento LaTeX (vista estructurada)
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
              flexWrap: "wrap",
            }}
          >
            <span style={{
              background: "linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(16, 185, 129, 0.1))",
              padding: "4px 10px",
              borderRadius: "6px",
              border: "1px solid rgba(34, 197, 94, 0.3)",
            }}>
              ✨ Edita directamente en el recuadro - las fórmulas se ven renderizadas mientras escribes
            </span>
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
            key={`mathfield-${modoEdicion}-${value ? 'hasValue' : 'empty'}`}
            ref={mathFieldRef}
            default-mode="math"
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
          />
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

        {/* Botón prominente para editar visualmente */}
        {value && mathLiveAvailable && (
          <div style={{
            marginTop: "0.75rem",
            padding: "0.75rem",
            background: "linear-gradient(135deg, rgba(147, 51, 234, 0.2), rgba(168, 85, 247, 0.1))",
            borderRadius: "8px",
            border: "2px dashed rgba(147, 51, 234, 0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "1rem",
          }}>
            <span style={{ color: "#c4b5fd", fontSize: "0.9rem" }}>
              ✨ ¿Quieres editar la fórmula directamente con formato visual?
            </span>
            <button
              type="button"
              onClick={() => setModoEdicion("visual")}
              style={{
                padding: "0.5rem 1.25rem",
                background: "linear-gradient(135deg, #9333ea, #7c3aed)",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "0.9rem",
                fontWeight: "600",
                boxShadow: "0 2px 10px rgba(147, 51, 234, 0.4)",
                transition: "transform 0.2s, box-shadow 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "scale(1.02)";
                e.currentTarget.style.boxShadow = "0 4px 15px rgba(147, 51, 234, 0.5)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "scale(1)";
                e.currentTarget.style.boxShadow = "0 2px 10px rgba(147, 51, 234, 0.4)";
              }}
            >
              🎨 Editar Visualmente
            </button>
          </div>
        )}

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

    // Parser de documento LaTeX completo
    const parseLatexDocument = (content) => {
      if (!content) return [];
      
      const sections = [];
      
      // Extraer contenido entre \begin{document} y \end{document}
      const docMatch = content.match(/\\begin\{document\}([\s\S]*?)\\end\{document\}/);
      const docContent = docMatch ? docMatch[1] : content;
      
      // Regex para detectar secciones, subsecciones y fórmulas
      const patterns = [
        { type: 'section', regex: /\\section\*?\{([^}]+)\}/g },
        { type: 'subsection', regex: /\\subsection\*?\{([^}]+)\}/g },
        { type: 'displaymath', regex: /\\\[([\s\S]*?)\\\]/g },
        { type: 'cases', regex: /\\begin\{cases\}([\s\S]*?)\\end\{cases\}/g },
        { type: 'array', regex: /\\begin\{array\}([\s\S]*?)\\end\{array\}/g },
        { type: 'matrix', regex: /\\left\[([\s\S]*?)\\right\]/g },
      ];
      
      // Dividir el contenido en bloques
      let remaining = docContent;
      let lastIndex = 0;
      let elements = [];
      
      // Buscar todas las secciones
      const sectionRegex = /\\section\*?\{([^}]+)\}|\\subsection\*?\{([^}]+)\}|\\\[([\s\S]*?)\\\]|\\begin\{cases\}([\s\S]*?)\\end\{cases\}/g;
      let match;
      
      while ((match = sectionRegex.exec(docContent)) !== null) {
        // Agregar texto entre matches
        if (match.index > lastIndex) {
          const textBetween = docContent.slice(lastIndex, match.index).trim();
          if (textBetween) {
            // Limpiar comandos LaTeX del texto
            const cleanText = textBetween
              .replace(/\\textbf\{([^}]+)\}/g, '$1')
              .replace(/\\textit\{([^}]+)\}/g, '$1')
              .replace(/\\[a-z]+/gi, '')
              .replace(/\{|\}/g, '')
              .trim();
            if (cleanText) {
              elements.push({ type: 'text', content: cleanText });
            }
          }
        }
        
        if (match[1]) {
          elements.push({ type: 'section', content: match[1] });
        } else if (match[2]) {
          elements.push({ type: 'subsection', content: match[2] });
        } else if (match[3]) {
          elements.push({ type: 'math', content: match[3] });
        } else if (match[4]) {
          elements.push({ type: 'math', content: `\\begin{cases}${match[4]}\\end{cases}` });
        }
        
        lastIndex = match.index + match[0].length;
      }
      
      // Agregar el resto del texto
      if (lastIndex < docContent.length) {
        const textRemaining = docContent.slice(lastIndex).trim();
        if (textRemaining) {
          const cleanText = textRemaining
            .replace(/\\textbf\{([^}]+)\}/g, '$1')
            .replace(/\\textit\{([^}]+)\}/g, '$1')
            .replace(/\\quad|\\qquad|\\;|\\,/g, ' ')
            .replace(/\\[a-z]+/gi, '')
            .replace(/\{|\}/g, '')
            .trim();
          if (cleanText) {
            elements.push({ type: 'text', content: cleanText });
          }
        }
      }
      
      return elements;
    };

    // Renderizar documento LaTeX estructurado
    const renderDocumentEditor = () => {
      const elements = parseLatexDocument(value);
      const isLatexDoc = value?.includes('\\documentclass') || value?.includes('\\begin{document}');
      
      return (
        <div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1rem',
          }}>
            <div style={{
              color: '#6ee7b7',
              fontSize: '0.85rem',
            }}>
              📄 Vista estructurada de documento LaTeX
              {isLatexDoc && <span style={{ marginLeft: '0.5rem', color: '#86efac' }}>✓ Documento detectado</span>}
            </div>
            <button
              type="button"
              onClick={async () => {
                try {
                  const text = await navigator.clipboard.readText();
                  onChange?.(text);
                } catch (e) {
                  console.error("Error leyendo clipboard:", e);
                }
              }}
              style={{
                padding: '4px 12px',
                background: 'rgba(16, 185, 129, 0.2)',
                color: '#6ee7b7',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.8rem',
              }}
            >
              📋 Pegar documento de ChatGPT
            </button>
          </div>

          {/* Área de edición de código fuente (colapsable) */}
          <details style={{ marginBottom: '1rem' }}>
            <summary style={{
              color: '#94a3b8',
              fontSize: '0.85rem',
              cursor: 'pointer',
              padding: '0.5rem',
              background: 'rgba(100, 116, 139, 0.1)',
              borderRadius: '6px',
              marginBottom: '0.5rem',
            }}>
              📝 Ver/Editar código fuente LaTeX
            </summary>
            <textarea
              value={value || ''}
              onChange={(e) => onChange?.(e.target.value)}
              placeholder="Pega aquí el documento LaTeX completo..."
              style={{
                width: '100%',
                minHeight: '150px',
                padding: '1rem',
                background: 'rgba(30, 41, 59, 0.8)',
                border: '1px solid rgba(100, 116, 139, 0.3)',
                borderRadius: '8px',
                color: '#94a3b8',
                fontFamily: '"Fira Code", "Consolas", monospace',
                fontSize: '0.85rem',
                resize: 'vertical',
                outline: 'none',
              }}
            />
          </details>

          {/* Vista estructurada */}
          <div style={{
            background: 'rgba(16, 185, 129, 0.05)',
            border: '2px solid rgba(16, 185, 129, 0.2)',
            borderRadius: '12px',
            padding: '1.5rem',
            maxHeight: '500px',
            overflowY: 'auto',
          }}>
            {elements.length === 0 ? (
              <div style={{
                textAlign: 'center',
                color: '#94a3b8',
                padding: '2rem',
              }}>
                📄 Pega un documento LaTeX para ver su estructura
              </div>
            ) : (
              elements.map((el, idx) => {
                if (el.type === 'section') {
                  return (
                    <h2 key={idx} style={{
                      color: '#6ee7b7',
                      fontSize: '1.3rem',
                      fontWeight: '700',
                      borderBottom: '2px solid rgba(16, 185, 129, 0.3)',
                      paddingBottom: '0.5rem',
                      marginTop: idx > 0 ? '1.5rem' : 0,
                      marginBottom: '1rem',
                    }}>
                      📗 {el.content}
                    </h2>
                  );
                } else if (el.type === 'subsection') {
                  return (
                    <h3 key={idx} style={{
                      color: '#86efac',
                      fontSize: '1.1rem',
                      fontWeight: '600',
                      marginTop: '1.25rem',
                      marginBottom: '0.75rem',
                      paddingLeft: '0.5rem',
                      borderLeft: '3px solid rgba(16, 185, 129, 0.4)',
                    }}>
                      📎 {el.content}
                    </h3>
                  );
                } else if (el.type === 'math') {
                  try {
                    return (
                      <div key={idx} style={{
                        background: 'rgba(147, 51, 234, 0.1)',
                        border: '1px solid rgba(147, 51, 234, 0.3)',
                        borderRadius: '8px',
                        padding: '1rem',
                        margin: '0.75rem 0',
                        overflowX: 'auto',
                      }}>
                        <BlockMath math={el.content} />
                      </div>
                    );
                  } catch (e) {
                    return (
                      <div key={idx} style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        borderRadius: '8px',
                        padding: '0.75rem',
                        margin: '0.5rem 0',
                        color: '#fca5a5',
                        fontSize: '0.9rem',
                      }}>
                        ⚠️ Error al renderizar: {e.message}
                        <code style={{ display: 'block', marginTop: '0.5rem', fontSize: '0.8rem' }}>
                          {el.content.substring(0, 100)}...
                        </code>
                      </div>
                    );
                  }
                } else {
                  // Texto normal - buscar fórmulas inline $...$
                  const parts = el.content.split(/(\$[^\$]+\$)/g);
                  return (
                    <p key={idx} style={{
                      color: '#e2e8f0',
                      fontSize: '1rem',
                      lineHeight: '1.7',
                      margin: '0.5rem 0',
                    }}>
                      {parts.map((part, i) => {
                        if (part.startsWith('$') && part.endsWith('$')) {
                          try {
                            return <BlockMath key={i} math={part.slice(1, -1)} />;
                          } catch {
                            return <code key={i}>{part}</code>;
                          }
                        }
                        return <span key={i}>{part}</span>;
                      })}
                    </p>
                  );
                }
              })
            )}
          </div>
        </div>
      );
    };

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

        {/* 🔥 Advertencia y conversión cuando es documento LaTeX completo */}
        {esDocumentoLatexCompleto(value) && (
          <div style={{
            background: "rgba(251, 191, 36, 0.15)",
            border: "1px solid rgba(251, 191, 36, 0.4)",
            borderRadius: "8px",
            padding: "0.75rem 1rem",
            marginBottom: "1rem",
            color: "#fbbf24",
            fontSize: "0.85rem",
          }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem", marginBottom: "0.75rem" }}>
              <span style={{ fontSize: "1.2rem" }}>⚠️</span>
              <div>
                <strong>Documento LaTeX detectado:</strong> El contenido incluye comandos de documento que el editor visual no puede mostrar directamente.
              </div>
            </div>
            
            {/* Botón de conversión */}
            <div style={{
              display: "flex",
              gap: "0.75rem",
              flexWrap: "wrap",
              alignItems: "center",
              marginTop: "0.5rem",
              paddingTop: "0.75rem",
              borderTop: "1px solid rgba(251, 191, 36, 0.3)",
            }}>
              <button
                type="button"
                onClick={() => {
                  const convertido = convertirDocumentoAMatematicas(value);
                  onChange?.(convertido);
                  setModoEdicion("visual");
                }}
                style={{
                  padding: "0.5rem 1rem",
                  background: "linear-gradient(135deg, #10b981, #059669)",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontSize: "0.9rem",
                  fontWeight: "600",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  boxShadow: "0 2px 10px rgba(16, 185, 129, 0.4)",
                }}
              >
                🔄 Convertir a formato visual
              </button>
              <span style={{ fontSize: "0.8rem", opacity: 0.9 }}>
                Extrae las fórmulas y permite editarlas con la paleta de símbolos
              </span>
            </div>
          </div>
        )}

        {modoEdicion === "visual" 
          ? renderVisualEditor() 
          : modoEdicion === "codigo" 
            ? renderCodeEditor()
            : renderDocumentEditor()}

        {modoEdicion !== "documento" && renderPreview()}
      </div>
    );
  },
);

MathEditor.displayName = "MathEditor";

export default MathEditor;

/**
 * CodeBlock - Componente para visualización de código con syntax highlighting
 * Estilo VS Code con soporte para:
 * - Múltiples lenguajes de programación
 * - Resaltado de líneas con errores
 * - Números de línea
 * - Modo oscuro/claro
 * - Diferencias (añadido/eliminado)
 */

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  vscDarkPlus,
  vs,
} from "react-syntax-highlighter/dist/esm/styles/prism";
import { useState } from "react";

// Mapeo de lenguajes comunes a los identificadores de Prism
const languageMap = {
  js: "javascript",
  ts: "typescript",
  py: "python",
  rb: "ruby",
  cs: "csharp",
  cpp: "cpp",
  "c++": "cpp",
  c: "c",
  java: "java",
  go: "go",
  rust: "rust",
  rs: "rust",
  php: "php",
  swift: "swift",
  kotlin: "kotlin",
  kt: "kotlin",
  scala: "scala",
  html: "markup",
  xml: "markup",
  css: "css",
  scss: "scss",
  sass: "sass",
  less: "less",
  json: "json",
  yaml: "yaml",
  yml: "yaml",
  md: "markdown",
  markdown: "markdown",
  sql: "sql",
  bash: "bash",
  sh: "bash",
  shell: "bash",
  powershell: "powershell",
  ps1: "powershell",
  dockerfile: "docker",
  docker: "docker",
  graphql: "graphql",
  gql: "graphql",
  jsx: "jsx",
  tsx: "tsx",
  vue: "markup",
  r: "r",
  matlab: "matlab",
  lua: "lua",
  perl: "perl",
  haskell: "haskell",
  hs: "haskell",
  elixir: "elixir",
  ex: "elixir",
  clojure: "clojure",
  clj: "clojure",
  dart: "dart",
  assembly: "nasm",
  asm: "nasm",
};

/**
 * Normaliza el lenguaje a un identificador válido de Prism
 */
const normalizeLanguage = (lang) => {
  if (!lang) return "javascript";
  const normalized = lang.toLowerCase().trim();
  return languageMap[normalized] || normalized;
};

/**
 * Componente principal de bloque de código
 */
const CodeBlock = ({
  code = "",
  language = "javascript",
  showLineNumbers = true,
  highlightLines = [], // Líneas a resaltar (ej: [3, 5, 7])
  errorLines = [], // Líneas con error (se muestran en rojo)
  addedLines = [], // Líneas añadidas (verde)
  removedLines = [], // Líneas eliminadas (rojo tachado)
  startingLineNumber = 1,
  maxHeight = "400px",
  darkMode = true,
  showCopyButton = true,
  title = "",
  fileName = "",
  wrapLongLines = false,
  annotations = {}, // {lineNumber: "comentario"}
  inline = false, // Para código en línea
  className = "",
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Error copiando código:", err);
    }
  };

  // Para código inline (sin bloque)
  if (inline) {
    return (
      <code
        className={`code-inline ${className}`}
        style={{
          backgroundColor: darkMode ? "#1e1e1e" : "#f3f4f6",
          color: darkMode ? "#d4d4d4" : "#1f2937",
          padding: "2px 6px",
          borderRadius: "4px",
          fontFamily: "'Fira Code', 'Consolas', 'Monaco', monospace",
          fontSize: "0.9em",
        }}
      >
        {code}
      </code>
    );
  }

  const normalizedLang = normalizeLanguage(language);
  const style = darkMode ? vscDarkPlus : vs;

  // Función para determinar el estilo de fondo de cada línea
  const lineProps = (lineNumber) => {
    const props = { style: { display: "block" } };

    if (errorLines.includes(lineNumber)) {
      props.style.backgroundColor = "rgba(239, 68, 68, 0.3)"; // Rojo para errores
      props.style.borderLeft = "3px solid #ef4444";
    } else if (addedLines.includes(lineNumber)) {
      props.style.backgroundColor = "rgba(34, 197, 94, 0.2)"; // Verde para añadidas
      props.style.borderLeft = "3px solid #22c55e";
    } else if (removedLines.includes(lineNumber)) {
      props.style.backgroundColor = "rgba(239, 68, 68, 0.2)"; // Rojo claro para eliminadas
      props.style.textDecoration = "line-through";
      props.style.opacity = "0.7";
    } else if (highlightLines.includes(lineNumber)) {
      props.style.backgroundColor = darkMode
        ? "rgba(59, 130, 246, 0.2)"
        : "rgba(59, 130, 246, 0.15)"; // Azul para resaltadas
    }

    return props;
  };

  return (
    <div
      className={`code-block-container ${className}`}
      style={{
        borderRadius: "8px",
        overflow: "hidden",
        backgroundColor: darkMode ? "#1e1e1e" : "#ffffff",
        border: darkMode ? "1px solid #3c3c3c" : "1px solid #e5e7eb",
        marginBlock: "12px",
      }}
    >
      {/* Header con título/archivo y botón copiar */}
      {(title || fileName || showCopyButton) && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "8px 12px",
            backgroundColor: darkMode ? "#252526" : "#f3f4f6",
            borderBottom: darkMode ? "1px solid #3c3c3c" : "1px solid #e5e7eb",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {fileName && (
              <span
                style={{
                  color: darkMode ? "#9cdcfe" : "#0066cc",
                  fontFamily: "'Consolas', monospace",
                  fontSize: "0.85rem",
                }}
              >
                📄 {fileName}
              </span>
            )}
            {title && !fileName && (
              <span
                style={{
                  color: darkMode ? "#d4d4d4" : "#374151",
                  fontSize: "0.85rem",
                  fontWeight: "500",
                }}
              >
                {title}
              </span>
            )}
            <span
              style={{
                color: darkMode ? "#808080" : "#6b7280",
                fontSize: "0.75rem",
                padding: "2px 8px",
                backgroundColor: darkMode ? "#333333" : "#e5e7eb",
                borderRadius: "4px",
                textTransform: "uppercase",
              }}
            >
              {normalizedLang}
            </span>
          </div>

          {showCopyButton && (
            <button
              onClick={handleCopy}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                color: darkMode ? "#808080" : "#6b7280",
                padding: "4px 8px",
                borderRadius: "4px",
                fontSize: "0.8rem",
                display: "flex",
                alignItems: "center",
                gap: "4px",
                transition: "all 0.2s",
              }}
              onMouseOver={(e) => {
                e.target.style.backgroundColor = darkMode
                  ? "#333333"
                  : "#e5e7eb";
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = "transparent";
              }}
            >
              {copied ? "✓ Copiado" : "📋 Copiar"}
            </button>
          )}
        </div>
      )}

      {/* Código con syntax highlighting */}
      <div style={{ maxHeight, overflow: "auto" }}>
        <SyntaxHighlighter
          language={normalizedLang}
          style={style}
          showLineNumbers={showLineNumbers}
          startingLineNumber={startingLineNumber}
          wrapLines={true}
          wrapLongLines={wrapLongLines}
          lineProps={lineProps}
          customStyle={{
            margin: 0,
            padding: "12px",
            fontSize: "0.9rem",
            fontFamily:
              "'Fira Code', 'Consolas', 'Monaco', 'SF Mono', monospace",
            backgroundColor: darkMode ? "#1e1e1e" : "#ffffff",
          }}
          codeTagProps={{
            style: {
              fontFamily:
                "'Fira Code', 'Consolas', 'Monaco', 'SF Mono', monospace",
            },
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>

      {/* Anotaciones/comentarios de líneas específicas */}
      {Object.keys(annotations).length > 0 && (
        <div
          style={{
            padding: "8px 12px",
            backgroundColor: darkMode ? "#252526" : "#f9fafb",
            borderTop: darkMode ? "1px solid #3c3c3c" : "1px solid #e5e7eb",
          }}
        >
          <div
            style={{
              fontSize: "0.8rem",
              color: darkMode ? "#808080" : "#6b7280",
              marginBottom: "4px",
            }}
          >
            📝 Anotaciones:
          </div>
          {Object.entries(annotations).map(([line, comment]) => (
            <div
              key={line}
              style={{
                fontSize: "0.85rem",
                color: darkMode ? "#d4d4d4" : "#374151",
                padding: "4px 0",
                display: "flex",
                gap: "8px",
              }}
            >
              <span
                style={{
                  color: errorLines.includes(parseInt(line))
                    ? "#ef4444"
                    : "#3b82f6",
                  fontWeight: "600",
                }}
              >
                L{line}:
              </span>
              <span>{comment}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * Componente para mostrar código con error a corregir
 */
export const CodeWithError = ({
  code,
  language = "javascript",
  errorLine,
  errorDescription,
  darkMode = true,
}) => {
  return (
    <div className="code-with-error">
      <CodeBlock
        code={code}
        language={language}
        errorLines={[errorLine]}
        darkMode={darkMode}
        annotations={{ [errorLine]: errorDescription }}
      />
    </div>
  );
};

/**
 * Componente para mostrar código con diferencias (antes/después)
 */
export const CodeDiff = ({
  originalCode,
  modifiedCode,
  language = "javascript",
  darkMode = true,
  showSideBySide = false,
}) => {
  if (showSideBySide) {
    return (
      <div
        style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}
      >
        <div>
          <div
            style={{
              color: "#ef4444",
              fontWeight: "600",
              marginBottom: "8px",
              fontSize: "0.9rem",
            }}
          >
            ❌ Original (con error)
          </div>
          <CodeBlock
            code={originalCode}
            language={language}
            darkMode={darkMode}
            title="Antes"
          />
        </div>
        <div>
          <div
            style={{
              color: "#22c55e",
              fontWeight: "600",
              marginBottom: "8px",
              fontSize: "0.9rem",
            }}
          >
            ✅ Corregido
          </div>
          <CodeBlock
            code={modifiedCode}
            language={language}
            darkMode={darkMode}
            title="Después"
          />
        </div>
      </div>
    );
  }

  // Calcular líneas añadidas/eliminadas (simplificado)
  const originalLines = originalCode.split("\n");
  const modifiedLines = modifiedCode.split("\n");

  const removedLineNumbers = [];
  const addedLineNumbers = [];

  // Comparación simple línea por línea
  const maxLines = Math.max(originalLines.length, modifiedLines.length);
  for (let i = 0; i < maxLines; i++) {
    if (originalLines[i] !== modifiedLines[i]) {
      if (i < originalLines.length) removedLineNumbers.push(i + 1);
      if (i < modifiedLines.length) addedLineNumbers.push(i + 1);
    }
  }

  return (
    <div>
      <CodeBlock
        code={modifiedCode}
        language={language}
        darkMode={darkMode}
        addedLines={addedLineNumbers}
        title="Código corregido"
      />
    </div>
  );
};

/**
 * Componente para preguntas de código MCQ
 */
export const CodeMCQ = ({
  code,
  language = "javascript",
  question,
  options,
  selectedOption,
  correctOption,
  showAnswer = false,
  onSelect,
  darkMode = true,
  highlightLines = [],
}) => {
  return (
    <div className="code-mcq">
      {/* Pregunta */}
      <div
        style={{
          marginBottom: "16px",
          fontSize: "1.1rem",
          fontWeight: "500",
          color: darkMode ? "#e5e7eb" : "#1f2937",
        }}
      >
        {question}
      </div>

      {/* Código */}
      <CodeBlock
        code={code}
        language={language}
        darkMode={darkMode}
        highlightLines={highlightLines}
      />

      {/* Opciones */}
      <div
        style={{
          marginTop: "16px",
          display: "flex",
          flexDirection: "column",
          gap: "8px",
        }}
      >
        {options.map((option, index) => {
          const letter = String.fromCharCode(65 + index); // A, B, C, D...
          const isSelected = selectedOption === letter;
          const isCorrect = correctOption === letter;

          let backgroundColor = darkMode ? "#2d2d2d" : "#f9fafb";
          let borderColor = darkMode ? "#3c3c3c" : "#e5e7eb";

          if (showAnswer) {
            if (isCorrect) {
              backgroundColor = "rgba(34, 197, 94, 0.2)";
              borderColor = "#22c55e";
            } else if (isSelected && !isCorrect) {
              backgroundColor = "rgba(239, 68, 68, 0.2)";
              borderColor = "#ef4444";
            }
          } else if (isSelected) {
            backgroundColor = darkMode
              ? "rgba(59, 130, 246, 0.2)"
              : "rgba(59, 130, 246, 0.1)";
            borderColor = "#3b82f6";
          }

          return (
            <button
              key={letter}
              onClick={() => !showAnswer && onSelect && onSelect(letter)}
              disabled={showAnswer}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "12px",
                padding: "12px 16px",
                backgroundColor,
                border: `2px solid ${borderColor}`,
                borderRadius: "8px",
                cursor: showAnswer ? "default" : "pointer",
                textAlign: "left",
                transition: "all 0.2s",
              }}
            >
              <span
                style={{
                  fontWeight: "600",
                  color:
                    isCorrect && showAnswer
                      ? "#22c55e"
                      : isSelected
                        ? "#3b82f6"
                        : darkMode
                          ? "#9ca3af"
                          : "#6b7280",
                  minWidth: "24px",
                }}
              >
                {letter})
              </span>
              {/* Si la opción contiene código, mostrarlo formateado */}
              {option.includes("\n") || option.includes("```") ? (
                <CodeBlock
                  code={option.replace(/```\w*\n?/g, "").replace(/```/g, "")}
                  language={language}
                  darkMode={darkMode}
                  showLineNumbers={false}
                  showCopyButton={false}
                  maxHeight="150px"
                />
              ) : (
                <span
                  style={{
                    color: darkMode ? "#e5e7eb" : "#1f2937",
                    fontFamily: option.match(/[{}\[\]();=<>]/)
                      ? "'Fira Code', 'Consolas', monospace"
                      : "inherit",
                  }}
                >
                  {option}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

/**
 * Componente para ejercicios de completar código
 */
export const CodeComplete = ({
  codeTemplate,
  blanks = [], // [{id: 1, placeholder: "___", hint: "pista"}]
  language = "javascript",
  userAnswers = {},
  onAnswerChange,
  showAnswers = false,
  correctAnswers = {},
  darkMode = true,
}) => {
  // Reemplazar los placeholders con inputs
  let displayCode = codeTemplate;

  blanks.forEach((blank, index) => {
    const inputPlaceholder = `<input_${blank.id}>`;
    displayCode = displayCode.replace(blank.placeholder, inputPlaceholder);
  });

  return (
    <div className="code-complete">
      <CodeBlock code={displayCode} language={language} darkMode={darkMode} />

      {/* Campos de entrada para cada espacio */}
      <div
        style={{
          marginTop: "16px",
          display: "flex",
          flexDirection: "column",
          gap: "12px",
          padding: "16px",
          backgroundColor: darkMode ? "#252526" : "#f9fafb",
          borderRadius: "8px",
        }}
      >
        <div
          style={{
            color: darkMode ? "#9ca3af" : "#6b7280",
            fontSize: "0.9rem",
            marginBottom: "8px",
          }}
        >
          Completa los espacios:
        </div>
        {blanks.map((blank) => {
          const userValue = userAnswers[blank.id] || "";
          const correctValue = correctAnswers[blank.id];
          const isCorrect =
            showAnswers && userValue.trim() === correctValue?.trim();
          const isWrong =
            showAnswers &&
            userValue &&
            userValue.trim() !== correctValue?.trim();

          return (
            <div
              key={blank.id}
              style={{ display: "flex", alignItems: "center", gap: "12px" }}
            >
              <span
                style={{
                  color: darkMode ? "#808080" : "#6b7280",
                  fontWeight: "500",
                  minWidth: "80px",
                }}
              >
                Espacio {blank.id}:
              </span>
              <input
                type="text"
                value={userValue}
                onChange={(e) =>
                  onAnswerChange && onAnswerChange(blank.id, e.target.value)
                }
                placeholder={blank.hint || "Tu respuesta..."}
                disabled={showAnswers}
                style={{
                  flex: 1,
                  padding: "8px 12px",
                  backgroundColor: darkMode ? "#1e1e1e" : "#ffffff",
                  border: `2px solid ${
                    isCorrect
                      ? "#22c55e"
                      : isWrong
                        ? "#ef4444"
                        : darkMode
                          ? "#3c3c3c"
                          : "#e5e7eb"
                  }`,
                  borderRadius: "6px",
                  color: darkMode ? "#d4d4d4" : "#1f2937",
                  fontFamily: "'Fira Code', 'Consolas', monospace",
                  fontSize: "0.95rem",
                }}
              />
              {showAnswers && (
                <span
                  style={{
                    color: isCorrect ? "#22c55e" : "#ef4444",
                    fontWeight: "500",
                  }}
                >
                  {isCorrect ? "✓" : `✗ (${correctValue})`}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CodeBlock;

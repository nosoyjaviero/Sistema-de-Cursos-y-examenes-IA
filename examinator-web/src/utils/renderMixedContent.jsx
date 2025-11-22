import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

/**
 * Renderiza texto mixto con LaTeX embebido
 * Detecta $...$ para inline math y $$...$$ para display math
 * @param {string} text - Texto con LaTeX embebido
 * @returns {React.ReactNode} - Componentes renderizados
 */
export const renderMixedContent = (text) => {
  if (!text) return null;
  
  const parts = [];
  let currentIndex = 0;
  
  // Regex para detectar LaTeX inline $...$ y display $$...$$
  const latexRegex = /\$\$([^\$]+)\$\$|\$([^\$]+)\$/g;
  let match;
  
  while ((match = latexRegex.exec(text)) !== null) {
    // Añade texto antes del LaTeX
    if (match.index > currentIndex) {
      parts.push({ type: 'text', content: text.slice(currentIndex, match.index) });
    }
    
    // Añade LaTeX (display o inline)
    if (match[1]) {
      // Display math $$...$$
      parts.push({ type: 'block', content: match[1] });
    } else if (match[2]) {
      // Inline math $...$
      parts.push({ type: 'inline', content: match[2] });
    }
    
    currentIndex = match.index + match[0].length;
  }
  
  // Añade texto restante
  if (currentIndex < text.length) {
    parts.push({ type: 'text', content: text.slice(currentIndex) });
  }
  
  // Si no hay LaTeX, devuelve el texto original
  if (parts.length === 0) {
    return text;
  }
  
  // Renderiza las partes
  return parts.map((part, idx) => {
    if (part.type === 'block') {
      return <BlockMath key={idx} math={part.content} />;
    } else if (part.type === 'inline') {
      return <InlineMath key={idx} math={part.content} />;
    } else {
      return <span key={idx}>{part.content}</span>;
    }
  });
};

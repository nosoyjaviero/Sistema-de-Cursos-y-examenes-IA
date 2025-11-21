# 🧠 Guía del Asistente LaTeX Inteligente

## 📚 Sistema de 6 Niveles para Flashcards Matemáticas

---

## 🎯 ¿Qué hace el Asistente?

El Asistente LaTeX convierte **lenguaje natural** en **LaTeX perfecto** automáticamente, permitiéndote crear flashcards matemáticas sin conocer la sintaxis LaTeX.

### Características principales:
- ✅ Conversión automática de texto natural a LaTeX
- ✅ 6 niveles de complejidad (básico → avanzado)
- ✅ Vista previa en tiempo real con KaTeX
- ✅ Edición manual del LaTeX generado
- ✅ Inserción directa en flashcards

---

## 🟢 NIVEL 1: Expresiones Básicas

### Potencias y exponentes

**Lenguaje natural:**
```
2 elevado a 5
x a la 3
```

**LaTeX generado:**
```latex
2^{5}
x^{3}
```

**Resultado:** 2⁵, x³

### Operaciones aritméticas

**Lenguaje natural:**
```
3x + 2 = 11
```

**LaTeX generado:**
```latex
3x + 2 = 11
```

---

## 🔵 NIVEL 2: Fracciones y Raíces

### Fracciones

**Lenguaje natural:**
```
fracción de 3x+2 sobre x-4
a dividido b
```

**LaTeX generado:**
```latex
\frac{3x+2}{x-4}
\frac{a}{b}
```

**Resultado:** 
$$\frac{3x+2}{x-4}$$

### Raíces cuadradas

**Lenguaje natural:**
```
raíz cuadrada de x+1
```

**LaTeX generado:**
```latex
\sqrt{x+1}
```

**Resultado:** √(x+1)

### Raíces n-ésimas

**Lenguaje natural:**
```
raíz 3-ésima de x
raíz n de 27
```

**LaTeX generado:**
```latex
\sqrt[3]{x}
\sqrt[n]{27}
```

**Resultado:** ∛x

---

## 🟣 NIVEL 3: Integrales, Sumatorias y Límites

### Integrales definidas

**Lenguaje natural:**
```
integral de 0 a 1 de x^2
```

**LaTeX generado:**
```latex
\int_{0}^{1} x^2 \, dx
```

**Resultado:** 
$$\int_{0}^{1} x^2 \, dx$$

### Integrales indefinidas

**Lenguaje natural:**
```
integral de cos x
```

**LaTeX generado:**
```latex
\int \cos x \, dx
```

### Sumatorias

**Lenguaje natural:**
```
sumatoria de k=1 a n
suma de i=0 a infinito
```

**LaTeX generado:**
```latex
\sum_{k=1}^{n}
\sum_{i=0}^{\infty}
```

**Resultado:** 
$$\sum_{k=1}^{n}$$

### Límites

**Lenguaje natural:**
```
límite de x→0 de seno x sobre x
```

**LaTeX generado:**
```latex
\lim_{x \to 0} \frac{\sin x}{x}
```

**Resultado:**
$$\lim_{x \to 0} \frac{\sin x}{x}$$

---

## 🟡 NIVEL 4: Matrices y Vectores

### Matrices

**Lenguaje natural:**
```
matriz de 2x2 con 1 2 3 4
```

**LaTeX generado:**
```latex
\begin{pmatrix}
1 & 2 \\
3 & 4
\end{pmatrix}
```

**Resultado:**
$$\begin{pmatrix}
1 & 2 \\
3 & 4
\end{pmatrix}$$

### Vectores columna

**Lenguaje natural:**
```
vector columna 1 2 3
```

**LaTeX generado:**
```latex
\begin{pmatrix} 1 \\ 2 \\ 3 \end{pmatrix}
```

**Resultado:**
$$\begin{pmatrix} 1 \\ 2 \\ 3 \end{pmatrix}$$

---

## 🟠 NIVEL 5: Álgebra Lineal

### Producto punto

**Lenguaje natural:**
```
producto punto de a y b
producto escalar de v con w
```

**LaTeX generado:**
```latex
\vec{a} \cdot \vec{b}
\vec{v} \cdot \vec{w}
```

**Resultado:** a⃗·b⃗

### Norma

**Lenguaje natural:**
```
norma de v
```

**LaTeX generado:**
```latex
\|v\|
```

**Resultado:** ‖v‖

### Transpuesta

**Lenguaje natural:**
```
transpuesta de A
```

**LaTeX generado:**
```latex
A^T
```

**Resultado:** Aᵀ

---

## 🔴 NIVEL 6: Ecuaciones Diferenciales

### Derivadas de primer orden

**Lenguaje natural:**
```
derivada dy/dx = 3x
```

**LaTeX generado:**
```latex
\frac{dy}{dx} = 3x
```

**Resultado:**
$$\frac{dy}{dx} = 3x$$

### Derivadas simples

**Lenguaje natural:**
```
derivada de x^3
```

**LaTeX generado:**
```latex
\frac{d}{dx} x^3
```

### Derivadas de segundo orden

**Lenguaje natural:**
```
segunda derivada de f
```

**LaTeX generado:**
```latex
\frac{d^2}{dx^2} f
```

### Serie de Taylor

**Lenguaje natural:**
```
taylor
```

**LaTeX generado:**
```latex
f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n
```

**Resultado:**
$$f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n$$

---

## 🎓 Flujo de Trabajo Completo

### Paso 1: Crear Flashcard Matemática

1. Abre carpeta (ej: "Matemáticas/Cálculo")
2. Click **➕ Nueva Flashcard**
3. Selecciona tipo: **🔢 Matemática**

### Paso 2: Activar LaTeX

4. Marca el checkbox: **📐 Contiene fórmulas matemáticas (LaTeX)**

### Paso 3: Usar Asistente

5. Click en **🧠 Asistente LaTeX Inteligente**
6. En el campo "Describe tu expresión matemática", escribe:
   ```
   fracción de 3x más 2 sobre x menos 4
   ```
7. Click **✨ Generar LaTeX**

### Paso 4: Revisar y Editar

8. Revisa la **Vista Previa** renderizada
9. Si es necesario, edita el LaTeX manualmente en el campo "LaTeX Generado"
10. Click **✅ Insertar en Flashcard**

### Paso 5: Completar Flashcard

11. Agrega **Título**: "Función racional"
12. Agrega **Respuesta**: La explicación de la función
13. Opcional: Agrega imágenes/archivos
14. Click **➕ Crear Flashcard**

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Flashcard de Integral

**Prompt natural:**
```
integral de 0 a pi de seno x
```

**Flashcard resultante:**
- **Título:** Integral de seno
- **Contenido:** ∫₀^π sin(x) dx
- **Respuesta:** 2
- **Tipo:** Matemática

### Ejemplo 2: Flashcard de Matriz

**Prompt natural:**
```
matriz de 3x3 con 1 0 0 0 1 0 0 0 1
```

**Flashcard resultante:**
- **Título:** Matriz identidad 3×3
- **Contenido:** Matriz renderizada
- **Respuesta:** Es la matriz identidad I₃
- **Tipo:** Matemática

### Ejemplo 3: Flashcard de Límite

**Prompt natural:**
```
límite de x→infinito de 1/x
```

**Flashcard resultante:**
- **Título:** Límite al infinito
- **Contenido:** lim_{x→∞} 1/x
- **Respuesta:** 0
- **Tipo:** Matemática

---

## 🔧 Funcionalidades Adicionales

### Vista Completa con LaTeX

- Click en cualquier flashcard matemática
- Se abre modal fullscreen
- LaTeX renderizado con KaTeX perfecto
- Fondo oscuro profesional

### Zoom de Imágenes

- Click en cualquier imagen
- Modal fullscreen con imagen ampliada
- Botón ✕ para cerrar

### Descarga de Archivos

- Botón **📥 Descargar** en cada archivo
- Funciona con archivos base64
- Descarga con nombre original

### Persistencia Base64

- Todos los archivos se convierten a base64 automáticamente
- Almacenamiento permanente en localStorage
- Sin URLs temporales que caduquen

---

## 🎨 Diseño y Estética

### Flashcards Matemáticas

- **Faja superior:** Azul (#3b82f6) con icono 🔢
- **Contenido:** Fondo azul claro con LaTeX renderizado
- **Badge:** "📐 LaTeX" visible en la tarjeta
- **Footer:** Tema y subtema claramente visibles

### Modal Asistente

- **Gradiente:** Púrpura (#667eea → #764ba2)
- **Vista previa:** Fondo blanco con fórmula renderizada
- **Botones:** Gradientes azul y púrpura
- **Hints:** Ejemplos de uso incluidos

---

## 🚀 Tips y Trucos

### 1. Combina niveles

```
integral de 0 a 1 de fracción de x sobre x+1
```

Genera:
```latex
\int_{0}^{1} \frac{x}{x+1} \, dx
```

### 2. Edita el LaTeX generado

Si el asistente no entiende perfectamente, genera una aproximación y luego edítala manualmente.

### 3. Usa subtemas

- **Tema:** Cálculo
- **Subtema:** Integrales definidas

Esto ayuda a organizar mejor tus flashcards.

### 4. Agrega explicaciones visuales

Combina LaTeX con imágenes:
- Gráfica de la función
- Diagrama del área bajo la curva
- Tabla de valores

### 5. Crea flashcards MCQ matemáticas

- **Pregunta:** ∫₀¹ x² dx = ?
- **Opciones:**
  - A) 1/2
  - B) 1/3 ✅
  - C) 1/4
  - D) 1

---

## 📊 Casos de Uso

### Para Estudiantes de Cálculo

- Integrales
- Derivadas
- Límites
- Serie de Taylor

### Para Estudiantes de Álgebra Lineal

- Matrices
- Vectores
- Producto punto
- Transpuestas

### Para Estudiantes de Ecuaciones Diferenciales

- EDO de primer orden
- EDO de segundo orden
- Sistemas de ecuaciones

### Para Profesores

- Crear bancos de preguntas matemáticas
- Generar exámenes tipo quiz
- Material de estudio para estudiantes

---

## ⚠️ Limitaciones Conocidas

1. **Sintaxis compleja:** Para ecuaciones muy complejas, es mejor escribir LaTeX directamente
2. **Ambigüedad:** Si el prompt es ambiguo, el asistente hace su mejor intento
3. **Notación específica:** Algunas notaciones especializadas requieren LaTeX manual

---

## 🎯 Próximos Pasos

### Experimenta con:
1. Crear flashcards de todos los niveles
2. Combinar LaTeX con imágenes
3. Usar subtemas para organización
4. Crear mazos de práctica por tema

### Practica con:
- Cálculo diferencial
- Cálculo integral
- Álgebra lineal
- Ecuaciones diferenciales

---

## 📞 Soporte

Si el asistente no entiende un tipo de expresión, puedes:
1. Reformular el prompt en lenguaje natural
2. Escribir el LaTeX directamente en el campo de contenido
3. Usar la vista previa para verificar el resultado

---

**¡Tu sistema de flashcards matemáticas está listo! 🚀**

Ahora puedes crear flashcards ricas con LaTeX perfecto, imágenes, archivos y toda la potencia de KaTeX para renderizado matemático profesional.

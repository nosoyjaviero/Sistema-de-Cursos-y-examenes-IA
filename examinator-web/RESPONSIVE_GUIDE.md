# 📱 Guía de Diseño Responsive - Examinator Web

## ✅ Implementación Completa

Se ha implementado un diseño **totalmente responsive** para móvil y tablet en la interfaz web de Examinator.

---

## 🎯 Características Implementadas

### 1. **Menú Hamburguesa (Mobile)**
- Botón flotante superior izquierdo
- Sidebar deslizable desde la izquierda
- Overlay oscuro al abrir menú
- Cierre automático al seleccionar opción
- Animaciones suaves

### 2. **Breakpoints Definidos**

```css
/* Desktop: > 1024px (diseño original) */
/* Tablet: 769px - 1024px */
/* Mobile: ≤ 768px */
/* Mobile pequeño: ≤ 480px */
/* Landscape móvil: altura < 500px */
```

### 3. **Adaptaciones por Dispositivo**

#### 📱 **Mobile (≤ 768px)**
- Sidebar oculta por defecto, se muestra con hamburguesa
- Contenido al 100% del ancho (sin margen izquierdo)
- Grids de 1 columna (carpetas, documentos, modelos)
- Botones ocupan ancho completo
- Modales al 95% del viewport
- Formularios con `font-size: 16px` (previene zoom en iOS)
- Touch targets mínimo 44x44px
- Tabs en 2 columnas
- Stats y configuraciones apilados verticalmente

#### 📱 **Mobile Pequeño (≤ 480px)**
- Modales a pantalla completa (sin border-radius)
- Padding reducido (0.75rem)
- Fuentes más pequeñas
- Botones más compactos

#### 📱 **Landscape Móvil**
- Sidebar con scroll
- Altura de modal optimizada
- Padding reducido para aprovechar espacio horizontal

#### 💻 **Tablet (769px - 1024px)**
- Sidebar reducida (220px vs 260px)
- Grids de 2 columnas donde tiene sentido
- Padding intermedio (1.5rem)
- Modales al 90% con max-width 700px

---

## 🛠️ Componentes Adaptados

### ✅ **Sidebar & Navegación**
- Modo desktop: fija, visible siempre
- Modo mobile: deslizable con overlay
- Transición suave (0.3s)

### ✅ **Formularios**
- Inputs con font-size 16px en mobile (evita zoom iOS)
- Labels y campos apilados verticalmente
- Selectores y textareas adaptados

### ✅ **Cards & Grids**
```css
/* Desktop */
.carpetas-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }

/* Mobile */
.carpetas-grid { grid-template-columns: 1fr !important; }
```

### ✅ **Modales**
- Desktop: centrados, tamaño fijo
- Tablet: 90% ancho, max-width 700px
- Mobile: 95% viewport
- Mobile pequeño: pantalla completa

### ✅ **Exámenes**
- Headers apilados verticalmente
- Stats en columna
- Navegación de preguntas adaptada
- Opciones de respuesta con padding táctil
- Botones de navegación al 100% en mobile

### ✅ **Documentos & Carpetas**
- Grid adaptativo
- Acciones en botones compactos
- Iconos claramente visibles

### ✅ **Configuración**
- Secciones apiladas
- Modelos en lista vertical
- Ranges y sliders adaptados

---

## 🎨 Detalles de Diseño

### **Espaciados**
```css
/* Desktop */
padding: 2rem;
gap: 2rem;

/* Tablet */
padding: 1.5rem;
gap: 1.5rem;

/* Mobile */
padding: 1rem;
gap: 1rem;

/* Mobile pequeño */
padding: 0.75rem;
gap: 0.75rem;
```

### **Tipografía Responsive**
```css
/* Títulos principales */
h1: 3rem → 2.5rem → 2rem → 1.75rem

/* Subtítulos */
h2: 2rem → 1.75rem → 1.5rem

/* Párrafos */
p: 1rem → 0.95rem → 0.9rem
```

### **Touch Targets**
```css
@media (hover: none) and (pointer: coarse) {
  button, .nav-item, .opcion-item {
    min-height: 44px; /* Recomendación Apple/Google */
    min-width: 44px;
  }
}
```

---

## 🚀 Cómo Probar

### 1. **En Chrome DevTools**
1. Abre la aplicación: `http://localhost:5173`
2. Presiona `F12` o `Ctrl+Shift+I`
3. Click en icono de dispositivos móviles (o `Ctrl+Shift+M`)
4. Prueba diferentes dispositivos:
   - iPhone 12/13/14 (390x844)
   - iPhone SE (375x667)
   - Pixel 5 (393x851)
   - iPad (768x1024)
   - iPad Pro (1024x1366)

### 2. **En Dispositivos Reales**
1. Asegúrate que el servidor esté accesible en tu red local
2. Encuentra tu IP: `ipconfig` (Windows) o `ifconfig` (Mac/Linux)
3. Accede desde el móvil: `http://TU_IP:5173`

### 3. **Qué Verificar**

#### ✅ **Menú Móvil**
- [ ] Botón hamburguesa visible en mobile
- [ ] Sidebar se desliza suavemente
- [ ] Overlay oscurece el fondo
- [ ] Cierra al tocar overlay
- [ ] Cierra al seleccionar opción
- [ ] Icono cambia (☰ → ✕)

#### ✅ **Layout General**
- [ ] Sin scroll horizontal
- [ ] Todo el contenido visible
- [ ] Espaciados apropiados
- [ ] Texto legible sin zoom

#### ✅ **Formularios**
- [ ] No hace zoom al enfocar inputs (iOS)
- [ ] Teclado no tapa campos
- [ ] Botones táctiles grandes

#### ✅ **Modales**
- [ ] Se ven completos
- [ ] Botones accesibles
- [ ] Scroll funciona dentro del modal
- [ ] Cierre fácil de encontrar

#### ✅ **Exámenes**
- [ ] Preguntas legibles
- [ ] Opciones fáciles de tocar
- [ ] Navegación clara
- [ ] Inputs de texto cómodos

#### ✅ **Performance**
- [ ] Animaciones fluidas
- [ ] Sin lag al abrir menú
- [ ] Scroll suave

---

## 🐛 Problemas Comunes y Soluciones

### **1. Zoom automático en iOS al enfocar inputs**
✅ **Solucionado**: Todos los inputs tienen `font-size: 16px` en mobile

### **2. Scroll horizontal no deseado**
✅ **Solucionado**: 
```css
.main-content {
  width: 100% !important;
  margin-left: 0 !important;
}
```

### **3. Botones muy pequeños para tocar**
✅ **Solucionado**: Touch targets mínimos de 44x44px

### **4. Modales muy grandes**
✅ **Solucionado**: 
- Mobile: 95% viewport
- Mobile pequeño: pantalla completa

### **5. Sidebar tapa contenido en mobile**
✅ **Solucionado**: 
- Sidebar fuera de vista por defecto
- Overlay para cerrar
- Contenido sin margen izquierdo

---

## 📦 Archivos Modificados

### `examinator-web/src/App.css`
- Agregado CSS responsive completo al final
- Breakpoints: 1024px, 768px, 480px
- Clases: `.mobile-menu-btn`, `.sidebar-overlay`
- Media queries con `!important` para sobrescribir estilos desktop

### `examinator-web/src/App.jsx`
- Estado: `menuMovilAbierto`
- Componente: `<button className="mobile-menu-btn">`
- Componente: `<div className="sidebar-overlay">`
- Sidebar con clase dinámica: `className={sidebar ${menuMovilAbierto ? 'open' : ''}}`
- Nav items cierran menú al hacer clic

---

## 🎯 Testing Checklist

### Desktop (> 1024px)
- [ ] Diseño original intacto
- [ ] Sidebar fija visible
- [ ] Grids multi-columna
- [ ] Botón hamburguesa oculto

### Tablet (769px - 1024px)
- [ ] Sidebar más estrecha (220px)
- [ ] Grids de 2 columnas
- [ ] Modales medianos
- [ ] Todo funcional

### Mobile (≤ 768px)
- [ ] Botón hamburguesa visible
- [ ] Sidebar deslizable
- [ ] Grids de 1 columna
- [ ] Botones full-width
- [ ] Modales grandes

### Mobile Pequeño (≤ 480px)
- [ ] Modales pantalla completa
- [ ] Fuentes reducidas
- [ ] Padding mínimo
- [ ] Todo legible

---

## 💡 Mejoras Futuras (Opcional)

1. **Gestos táctiles**
   - Swipe desde el borde izquierdo para abrir menú
   - Swipe en exámenes para cambiar pregunta

2. **Modo oscuro específico mobile**
   - Menor brillo para ahorro de batería
   - Contraste optimizado para exteriores

3. **PWA (Progressive Web App)**
   - Instalar en pantalla de inicio
   - Funcionar offline
   - Notificaciones push

4. **Optimizaciones de carga**
   - Lazy loading de imágenes
   - Code splitting por rutas
   - Service Workers para cache

5. **Accesibilidad mejorada**
   - Screen reader support
   - Navegación por teclado
   - Contraste WCAG AA

---

## 📱 Capturas de Pantalla Recomendadas

Para documentar, captura pantallas de:
1. Menu hamburguesa cerrado (mobile)
2. Menu hamburguesa abierto con overlay (mobile)
3. Vista de examen en mobile
4. Modal de configuración en mobile
5. Vista de carpetas en tablet
6. Comparativa desktop vs mobile

---

## 🆘 Soporte

Si encuentras problemas:
1. Verifica que no haya CSS conflictivo de versiones anteriores
2. Limpia caché del navegador (`Ctrl+F5`)
3. Revisa la consola del navegador (F12)
4. Prueba en modo incógnito
5. Verifica que el servidor esté corriendo

---

**Fecha de implementación**: 17 de noviembre de 2025  
**Versión**: 1.0  
**Estado**: ✅ Producción

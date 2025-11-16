from pypdf import PdfReader
from pathlib import Path
from typing import Optional, List
import argparse
import sys
import re

import re


def limpiar_texto(texto: str, agresivo: bool = False) -> str:
    """Limpia y normaliza el texto eliminando saltos de línea raros y espacios extras.
    
    Args:
        texto: El texto a limpiar
        agresivo: Si es True, une líneas de manera agresiva. Si es False, solo normaliza espacios.
    """
    if not agresivo:
        # Limpieza suave: solo normalizar espacios y eliminar líneas completamente vacías extras
        lineas = []
        for linea in texto.split('\n'):
            # Mantener la línea pero limpiar espacios internos
            limpia = re.sub(r' +', ' ', linea.strip())
            lineas.append(limpia)
        
        # Unir y normalizar saltos de línea múltiples (máximo 2)
        texto_limpio = '\n'.join(lineas)
        texto_limpio = re.sub(r'\n{3,}', '\n\n', texto_limpio)
        # Eliminar espacios antes de puntuación
        texto_limpio = re.sub(r' +([.,;:!?)])', r'\1', texto_limpio)
        return texto_limpio.strip()
    
    # Limpieza agresiva (modo original)
    lineas = texto.split('\n')
    resultado = []
    
    for i, linea in enumerate(lineas):
        linea_limpia = linea.strip()
        
        if not linea_limpia:
            # Línea vacía - mantenerla como separador de párrafo
            if resultado and resultado[-1] != '':
                resultado.append('')
            continue
        
        # Si la línea anterior existe y no está vacía, y la actual no empieza con mayúscula
        # o la anterior no termina con puntuación, unir con espacio
        if resultado and resultado[-1] and resultado[-1] != '':
            ultima = resultado[-1].rstrip()
            # Verificar si debe unirse a la línea anterior
            if ultima and not ultima[-1] in '.!?:;' and linea_limpia and not linea_limpia[0].isupper():
                resultado[-1] = ultima + ' ' + linea_limpia
                continue
        
        resultado.append(linea_limpia)
    
    # Unir líneas y normalizar espacios múltiples
    texto_unido = '\n'.join(resultado)
    # Normalizar espacios múltiples a uno solo
    texto_unido = re.sub(r' +', ' ', texto_unido)
    # Eliminar espacios antes de puntuación
    texto_unido = re.sub(r' +([.,;:!?)])', r'\1', texto_unido)
    # Normalizar múltiples saltos de línea a máximo 2
    texto_unido = re.sub(r'\n{3,}', '\n\n', texto_unido)
    
    return texto_unido.strip()


def dividir_en_secciones(texto: str) -> List[dict]:
    """Divide el texto en secciones detectando títulos/capítulos.
    
    Retorna una lista de diccionarios con 'titulo' y 'contenido'.
    """
    secciones = []
    
    # Patrones para detectar títulos (capítulos, secciones, etc.)
    patrones_titulo = [
        r'^(CAPÍTULO|CAPÍTULO|Capítulo|CHAPTER|Chapter)\s+[IVXLCDM\d]+[:.\s]*.+$',
        r'^(SECCIÓN|SECCION|Sección|Seccion|SECTION|Section)\s+[\d]+[:.\s]*.+$',
        r'^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{10,}$',  # TEXTO EN MAYÚSCULAS (mínimo 10 chars)
        r'^\d+\.\s+[A-ZÁÉÍÓÚÑ].+$',  # 1. Título con mayúscula inicial
    ]
    
    patron_combinado = re.compile('|'.join(patrones_titulo), re.MULTILINE)
    
    lineas = texto.split('\n')
    seccion_actual = {'titulo': 'Inicio', 'contenido': []}
    
    for linea in lineas:
        linea_limpia = linea.strip()
        
        if not linea_limpia:
            seccion_actual['contenido'].append('')
            continue
        
        # Verificar si es un título
        if patron_combinado.match(linea_limpia):
            # Guardar sección anterior si tiene contenido
            if seccion_actual['contenido']:
                seccion_actual['contenido'] = '\n'.join(seccion_actual['contenido']).strip()
                if seccion_actual['contenido']:
                    secciones.append(seccion_actual)
            # Iniciar nueva sección
            seccion_actual = {'titulo': linea_limpia, 'contenido': []}
        else:
            seccion_actual['contenido'].append(linea_limpia)
    
    # Agregar última sección
    if seccion_actual['contenido']:
        seccion_actual['contenido'] = '\n'.join(seccion_actual['contenido']).strip()
        if seccion_actual['contenido']:
            secciones.append(seccion_actual)
    
    return secciones


def leer_pdf(ruta: str, sin_limpiar: bool = False, agresivo: bool = False, verbose: bool = False) -> str:
    reader = PdfReader(ruta)
    total_paginas = len(reader.pages)
    
    if verbose:
        print(f"Procesando PDF con {total_paginas} páginas...", file=sys.stderr)
    
    # Usar lista para mejor rendimiento con concatenación de strings
    partes = []
    paginas_con_error = []
    paginas_vacias = []
    
    for i, page in enumerate(reader.pages):
        if verbose and (i + 1) % 10 == 0:
            print(f"  Procesando página {i+1}/{total_paginas}...", file=sys.stderr)
        
        contenido_extraido = None
        metodo_usado = None
        
        try:
            # Método 1: Layout mode (mejor para PDFs con formato complejo)
            try:
                contenido_extraido = page.extract_text(extraction_mode="layout")
                if contenido_extraido and contenido_extraido.strip():
                    metodo_usado = "layout"
            except Exception:
                pass
            
            # Método 2: Modo normal (si layout falla)
            if not contenido_extraido or not contenido_extraido.strip():
                try:
                    contenido_extraido = page.extract_text()
                    if contenido_extraido and contenido_extraido.strip():
                        metodo_usado = "normal"
                except Exception:
                    pass
            
            # Método 3: Extracción simple (fallback)
            if not contenido_extraido or not contenido_extraido.strip():
                try:
                    contenido_extraido = page.extract_text(extraction_mode="plain")
                    if contenido_extraido and contenido_extraido.strip():
                        metodo_usado = "plain"
                except Exception:
                    pass
            
            if contenido_extraido and contenido_extraido.strip():
                partes.append(contenido_extraido)
                # Agregar separador de página con marca
                if i < total_paginas - 1:
                    partes.append(f"\n\n--- Página {i+1} ---\n\n")
                
                if verbose:
                    print(f"  Página {i+1}: {len(contenido_extraido)} caracteres (método: {metodo_usado})", file=sys.stderr)
            else:
                paginas_vacias.append(i + 1)
                if verbose:
                    print(f"  Página {i+1}: VACIA o sin texto extraíble", file=sys.stderr)
                    
        except Exception as e:
            paginas_con_error.append(i + 1)
            if verbose:
                print(f"  ERROR en página {i+1}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
    
    if verbose:
        print(f"\n=== RESUMEN DE EXTRACCIÓN ===", file=sys.stderr)
        print(f"Total de páginas en PDF: {total_paginas}", file=sys.stderr)
        print(f"Páginas procesadas exitosamente: {total_paginas - len(paginas_con_error) - len(paginas_vacias)}", file=sys.stderr)
        print(f"Páginas vacías/sin texto: {len(paginas_vacias)}", file=sys.stderr)
        print(f"Páginas con errores: {len(paginas_con_error)}", file=sys.stderr)
        
        if paginas_vacias:
            print(f"  Páginas vacías: {', '.join(map(str, paginas_vacias[:20]))}", file=sys.stderr)
            if len(paginas_vacias) > 20:
                print(f"  ... y {len(paginas_vacias) - 20} más", file=sys.stderr)
        
        if paginas_con_error:
            print(f"  Páginas con error: {', '.join(map(str, paginas_con_error))}", file=sys.stderr)
    
    # Unir todas las partes de una vez (más eficiente que concatenar strings)
    texto = ''.join(partes)
    
    if verbose:
        print(f"\nTexto total extraído:", file=sys.stderr)
        print(f"  Caracteres: {len(texto):,}", file=sys.stderr)
        print(f"  Palabras (aprox): {len(texto.split()):,}", file=sys.stderr)
        print(f"  Líneas: {len(texto.splitlines()):,}", file=sys.stderr)
    
    if not texto.strip():
        raise ValueError(f"No se pudo extraer texto del PDF. El archivo puede estar protegido, ser solo imágenes, o estar corrupto.")
    
    if sin_limpiar:
        return texto
    
    if verbose:
        print("\nAplicando limpieza de texto...", file=sys.stderr)
    
    return limpiar_texto(texto, agresivo=agresivo)


def leer_txt(ruta: str, sin_limpiar: bool = False, agresivo: bool = False, verbose: bool = False) -> str:
    if verbose:
        print(f"Leyendo archivo de texto: {ruta}", file=sys.stderr)
    
    with open(ruta, "r", encoding="utf-8") as f:
        texto = f.read()
    
    if verbose:
        print(f"Texto leído: {len(texto):,} caracteres", file=sys.stderr)
    
    if sin_limpiar:
        return texto
    return limpiar_texto(texto, agresivo=agresivo)


def obtener_texto(ruta: str, sin_limpiar: bool = False, agresivo: bool = False, verbose: bool = False) -> str:
    path = Path(ruta)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    suf = path.suffix.lower()
    if suf == ".pdf":
        return leer_pdf(str(path), sin_limpiar=sin_limpiar, agresivo=agresivo, verbose=verbose)
    elif suf in {".txt", ".log", ".md"}:
        return leer_txt(str(path), sin_limpiar=sin_limpiar, agresivo=agresivo, verbose=verbose)
    else:
        raise ValueError(
            f"Extensión no soportada '{path.suffix}'. Usa .pdf o .txt"
        )


def seleccionar_archivo() -> Optional[str]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    root = tk.Tk()
    root.withdraw()
    # Primer filtro combinado para ver PDF y texto a la vez.
    ruta = filedialog.askopenfilename(
        title="Selecciona un archivo",
        filetypes=[
            ("PDF y Texto", "*.pdf *.txt *.log *.md"),
            ("PDF", "*.pdf"),
            ("Texto", "*.txt *.log *.md"),
            ("Todos los archivos", "*.*"),
        ],
    )
    try:
        root.destroy()
    except Exception:
        pass
    return ruta or None


def generar_ruta_salida(ruta_entrada: str, carpeta_proyecto: str = None) -> Path:
    """Genera una ruta de salida organizada basada en el archivo de entrada.
    
    Args:
        ruta_entrada: Ruta del archivo de entrada
        carpeta_proyecto: Carpeta raíz del proyecto (por defecto, carpeta actual del script)
    
    Returns:
        Path objeto con la ruta de salida sugerida
    """
    entrada = Path(ruta_entrada)
    
    # Carpeta del proyecto (donde está el script)
    if carpeta_proyecto is None:
        carpeta_proyecto = Path(__file__).parent
    else:
        carpeta_proyecto = Path(carpeta_proyecto)
    
    # Crear carpeta 'extracciones' en el proyecto
    carpeta_salida = carpeta_proyecto / "extracciones"
    
    # Crear subcarpeta con fecha actual
    from datetime import datetime
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    carpeta_fecha = carpeta_salida / fecha_hoy
    
    # Nombre del archivo de salida: mismo nombre pero con .txt
    nombre_base = entrada.stem
    # Limpiar el nombre de caracteres extraños
    nombre_limpio = re.sub(r'[^\w\s-]', '', nombre_base)
    nombre_limpio = re.sub(r'[-\s]+', '_', nombre_limpio)
    
    # Ruta completa de salida
    ruta_salida = carpeta_fecha / f"{nombre_limpio}.txt"
    
    # Si el archivo ya existe, agregar sufijo numérico
    contador = 1
    while ruta_salida.exists():
        ruta_salida = carpeta_fecha / f"{nombre_limpio}_{contador}.txt"
        contador += 1
    
    return ruta_salida


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Extrae texto de archivos PDF o TXT y lo muestra o guarda."
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        help="Ruta al archivo de entrada (.pdf o .txt). Si se omite, se abrirá un selector de archivos.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Ruta de salida para guardar el texto (opcional). Si no se indica junto con --auto-save, se genera automáticamente.",
    )
    parser.add_argument(
        "--auto-save",
        action="store_true",
        help="Guardar automáticamente en carpeta 'extracciones' del proyecto organizada por fecha.",
    )
    parser.add_argument(
        "-s",
        "--secciones",
        action="store_true",
        help="Dividir el texto en secciones por capítulos/títulos.",
    )
    parser.add_argument(
        "--sin-limpiar",
        action="store_true",
        help="No aplicar limpieza de texto (preservar formato original).",
    )
    parser.add_argument(
        "--limpieza-agresiva",
        action="store_true",
        help="Aplicar limpieza agresiva uniendo líneas de párrafos.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Mostrar información detallada del proceso de extracción.",
    )

    args = parser.parse_args(argv)

    ruta_archivo = args.archivo
    if not ruta_archivo:
        ruta_archivo = seleccionar_archivo()
        if not ruta_archivo:
            print(
                "No se seleccionó ni se proporcionó archivo. Pasa una ruta o intenta de nuevo.",
                file=sys.stderr,
            )
            return 3

    try:
        texto = obtener_texto(
            ruta_archivo,
            sin_limpiar=args.sin_limpiar,
            agresivo=args.limpieza_agresiva,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Determinar ruta de salida
    ruta_salida = None
    if args.output:
        ruta_salida = Path(args.output)
    elif args.auto_save:
        ruta_salida = generar_ruta_salida(ruta_archivo)
        if args.verbose:
            print(f"\nRuta de salida automática: {ruta_salida}", file=sys.stderr)

    # Dividir en secciones si se solicita
    if args.secciones:
        secciones = dividir_en_secciones(texto)
        if ruta_salida:
            # Guardar cada sección en un archivo separado
            base_path = ruta_salida
            base_name = base_path.stem
            base_dir = base_path.parent
            ext = base_path.suffix
            
            # Crear directorio si no existe
            base_dir.mkdir(parents=True, exist_ok=True)
            
            for i, seccion in enumerate(secciones, 1):
                nombre_seccion = re.sub(r'[^\w\s-]', '', seccion['titulo'])[:50]
                nombre_archivo = f"{base_name}_seccion_{i:02d}_{nombre_seccion}{ext}"
                ruta_seccion = base_dir / nombre_archivo
                
                contenido_seccion = f"# {seccion['titulo']}\n\n{seccion['contenido']}"
                ruta_seccion.write_text(contenido_seccion, encoding="utf-8")
            
            print(f"{len(secciones)} secciones guardadas en: {base_dir}")
        else:
            # Imprimir secciones con separadores
            for i, seccion in enumerate(secciones, 1):
                print(f"\n{'='*80}")
                print(f"SECCIÓN {i}: {seccion['titulo']}")
                print(f"{'='*80}\n")
                print(seccion['contenido'])
        return 0

    if ruta_salida:
        try:
            # Crear directorio si no existe
            ruta_salida.parent.mkdir(parents=True, exist_ok=True)
            ruta_salida.write_text(texto, encoding="utf-8")
            print(f"Texto guardado en: {ruta_salida}")
        except Exception as e:
            print(f"No se pudo escribir el archivo de salida: {e}", file=sys.stderr)
            return 2
    else:
        print(texto)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

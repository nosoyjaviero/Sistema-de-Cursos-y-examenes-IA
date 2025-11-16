from pypdf import PdfReader
from pathlib import Path
from typing import Optional
import argparse
import sys

def leer_pdf(ruta: str) -> str:
    reader = PdfReader(ruta)
    texto = ""
    for page in reader.pages:
        contenido = page.extract_text() or ""
        texto += contenido + "\n"
    return texto


def leer_txt(ruta: str) -> str:
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()


def obtener_texto(ruta: str) -> str:
    path = Path(ruta)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    suf = path.suffix.lower()
    if suf == ".pdf":
        return leer_pdf(str(path))
    elif suf in {".txt", ".log", ".md"}:
        return leer_txt(str(path))
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
        help="Ruta de salida para guardar el texto (opcional). Si no se indica, imprime en pantalla.",
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
        texto = obtener_texto(ruta_archivo)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if args.output:
        try:
            Path(args.output).write_text(texto, encoding="utf-8")
            print(f"Texto guardado en: {args.output}")
        except Exception as e:
            print(f"No se pudo escribir el archivo de salida: {e}", file=sys.stderr)
            return 2
    else:
        print(texto)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Sistema interactivo de exámenes con IA
"""
from pathlib import Path
from typing import List
import argparse
import sys
from generador_examenes import GeneradorExamenes, PreguntaExamen, guardar_examen, cargar_examen
from generador_unificado import GeneradorUnificado


def limpiar_pantalla():
    """Limpia la pantalla de la terminal"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_pregunta(num: int, pregunta: PreguntaExamen):
    """Muestra una pregunta formateada"""
    print(f"\n{'='*80}")
    print(f"PREGUNTA {num} [{pregunta.tipo.upper()}] - {pregunta.puntos} puntos")
    print(f"{'='*80}")
    print(f"\n{pregunta.pregunta}\n")
    
    if pregunta.opciones:
        for opcion in pregunta.opciones:
            print(f"  {opcion}")
        print()


def obtener_respuesta(pregunta: PreguntaExamen) -> str:
    """Obtiene la respuesta del usuario según el tipo de pregunta"""
    if pregunta.tipo == 'multiple':
        while True:
            respuesta = input("Tu respuesta (A/B/C/D): ").strip().upper()
            if respuesta in ['A', 'B', 'C', 'D']:
                return respuesta
            print("Por favor ingresa A, B, C o D")
    
    elif pregunta.tipo == 'combo':
        print("Selecciona una o más opciones (ejemplo: A,C,D):")
        respuesta = input("Tu respuesta: ").strip().upper()
        return respuesta
    
    elif pregunta.tipo == 'corta':
        print("Respuesta corta (2-4 líneas):")
        return input("Tu respuesta: ").strip()
    
    elif pregunta.tipo == 'desarrollo':
        print("Respuesta de desarrollo (presiona Enter dos veces para finalizar):")
        lineas = []
        linea_vacia = False
        while True:
            linea = input()
            if not linea:
                if linea_vacia:
                    break
                linea_vacia = True
            else:
                linea_vacia = False
                lineas.append(linea)
        return '\n'.join(lineas)


def realizar_examen_interactivo(preguntas: List[PreguntaExamen], generador: GeneradorExamenes):
    """Realiza el examen de forma interactiva"""
    print("\n" + "="*80)
    print("EXAMEN GENERADO POR IA")
    print("="*80)
    print(f"\nTotal de preguntas: {len(preguntas)}")
    print(f"Puntos totales: {sum(p.puntos for p in preguntas)}")
    print("\nPresiona Enter para comenzar...")
    input()
    
    respuestas = []
    puntos_obtenidos = 0
    puntos_totales = sum(p.puntos for p in preguntas)
    
    for i, pregunta in enumerate(preguntas, 1):
        limpiar_pantalla()
        mostrar_pregunta(i, pregunta)
        respuesta = obtener_respuesta(pregunta)
        pregunta.respuesta_usuario = respuesta
        respuestas.append((pregunta, respuesta))
        
        print("\nRespuesta guardada. ✓")
        if i < len(preguntas):
            input("\nPresiona Enter para continuar...")
    
    # Evaluar todas las respuestas
    print("\n" + "="*80)
    print("EVALUANDO RESPUESTAS...")
    print("="*80)
    
    resultados = []
    for i, (pregunta, respuesta) in enumerate(respuestas, 1):
        print(f"\nEvaluando pregunta {i}/{len(preguntas)}...")
        puntos, feedback = generador.evaluar_respuesta(pregunta, respuesta)
        pregunta.puntos_obtenidos = puntos
        puntos_obtenidos += puntos
        resultados.append((i, pregunta, puntos, feedback))
    
    # Mostrar resultados
    limpiar_pantalla()
    print("\n" + "="*80)
    print("RESULTADOS DEL EXAMEN")
    print("="*80)
    
    for num, pregunta, puntos, feedback in resultados:
        print(f"\n--- Pregunta {num} ---")
        print(f"Tipo: {pregunta.tipo}")
        print(f"Puntos: {puntos}/{pregunta.puntos}")
        print(f"Feedback: {feedback}")
        if pregunta.tipo in ['corta', 'desarrollo']:
            print(f"\nTu respuesta:")
            print(f"  {pregunta.respuesta_usuario[:200]}...")
    
    # Calificación final
    porcentaje = (puntos_obtenidos / puntos_totales) * 100
    print("\n" + "="*80)
    print("CALIFICACIÓN FINAL")
    print("="*80)
    print(f"Puntos obtenidos: {puntos_obtenidos}/{puntos_totales}")
    print(f"Porcentaje: {porcentaje:.1f}%")
    
    if porcentaje >= 90:
        print("¡EXCELENTE! 🌟")
    elif porcentaje >= 70:
        print("¡BIEN HECHO! 👍")
    elif porcentaje >= 50:
        print("APROBADO ✓")
    else:
        print("NECESITAS MEJORAR 📚")
    
    return resultados, puntos_obtenidos, puntos_totales


def main():
    parser = argparse.ArgumentParser(
        description="Sistema interactivo de exámenes con IA"
    )
    parser.add_argument(
        "documento",
        help="Ruta al documento de texto extraído"
    )
    parser.add_argument(
        "--modelo",
        help="Ruta al modelo GGUF de llama.cpp (opcional, usa modo ejemplo sin modelo)",
        default=None
    )
    parser.add_argument(
        "--num-multiple",
        type=int,
        default=5,
        help="Número de preguntas de opción múltiple"
    )
    parser.add_argument(
        "--num-corta",
        type=int,
        default=3,
        help="Número de preguntas de respuesta corta"
    )
    parser.add_argument(
        "--num-desarrollo",
        type=int,
        default=2,
        help="Número de preguntas de desarrollo"
    )
    parser.add_argument(
        "--guardar-examen",
        help="Guardar el examen generado en un archivo JSON"
    )
    parser.add_argument(
        "--cargar-examen",
        help="Cargar un examen previamente generado desde JSON"
    )
    
    args = parser.parse_args()
    
    # Leer documento
    documento_path = Path(args.documento)
    if not documento_path.exists():
        print(f"Error: No se encontró el documento: {args.documento}")
        return 1
    
    print("Cargando documento...")
    with open(documento_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    print(f"Documento cargado: {len(contenido)} caracteres")
    
    # Inicializar generador con Ollama (GPU automática)
    print("🚀 Usando Ollama con GPU...")
    generador = GeneradorUnificado(
        usar_ollama=True,
        modelo_ollama="llama31-local",  # Puedes cambiar a: llama32-local, qwen-local, deepseek-r1-local
        modelo_path_gguf=args.modelo,
        n_gpu_layers=35
    )
    
    # Generar o cargar examen
    if args.cargar_examen:
        print(f"Cargando examen desde: {args.cargar_examen}")
        preguntas = cargar_examen(Path(args.cargar_examen))
    else:
        num_preguntas = {
            'multiple': args.num_multiple,
            'corta': args.num_corta,
            'desarrollo': args.num_desarrollo
        }
        
        print("\nGenerando examen...")
        preguntas = generador.generar_examen(contenido, num_preguntas)
        print(f"Examen generado: {len(preguntas)} preguntas")
        
        if args.guardar_examen:
            ruta_guardar = Path(args.guardar_examen)
            guardar_examen(preguntas, ruta_guardar)
            print(f"Examen guardado en: {ruta_guardar}")
    
    # Realizar examen
    input("\nPresiona Enter para comenzar el examen...")
    resultados, puntos, total = realizar_examen_interactivo(preguntas, generador)
    
    # Guardar resultados
    carpeta_resultados = documento_path.parent / "resultados"
    carpeta_resultados.mkdir(exist_ok=True)
    
    from datetime import datetime
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_resultado = carpeta_resultados / f"resultado_{fecha}.txt"
    
    with open(archivo_resultado, 'w', encoding='utf-8') as f:
        f.write("RESULTADOS DEL EXAMEN\n")
        f.write("="*80 + "\n\n")
        f.write(f"Documento: {documento_path.name}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Calificación: {puntos}/{total} ({(puntos/total)*100:.1f}%)\n\n")
        
        for num, pregunta, pts, feedback in resultados:
            f.write(f"\nPregunta {num}:\n")
            f.write(f"{pregunta.pregunta}\n")
            f.write(f"Respuesta: {pregunta.respuesta_usuario}\n")
            f.write(f"Puntos: {pts}/{pregunta.puntos}\n")
            f.write(f"Feedback: {feedback}\n")
            f.write("-"*80 + "\n")
    
    print(f"\nResultados guardados en: {archivo_resultado}")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nExamen cancelado por el usuario.")
        sys.exit(1)

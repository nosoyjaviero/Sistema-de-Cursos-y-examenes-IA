"""
Módulo para realizar búsquedas en internet usando DuckDuckGo
"""
from ddgs import DDGS
import json
from typing import List, Dict


def buscar_duckduckgo(query: str, max_resultados: int = 5) -> List[Dict]:
    """
    Busca en DuckDuckGo usando la biblioteca oficial ddgs
    
    Args:
        query: Término de búsqueda
        max_resultados: Número máximo de resultados a retornar
        
    Returns:
        Lista de diccionarios con título, snippet y url
    """
    try:
        # Limpiar y mejorar la consulta
        query_limpia = query.strip()
        
        # Correcciones comunes de ortografía
        correcciones = {
            'ulyimo': 'último',
            'ultimos': 'últimos',
            'costarica': 'Costa Rica',
            'seleccion': 'selección',
            'futbol': 'fútbol'
        }
        
        for error, correccion in correcciones.items():
            query_limpia = query_limpia.replace(error, correccion)
        
        print(f"[DEBUG] Consulta original: {query}")
        if query_limpia != query:
            print(f"[DEBUG] Consulta corregida: {query_limpia}")
        
        resultados = []
        
        # Usar la biblioteca ddgs
        with DDGS() as ddgs:
            # Realizar búsqueda de texto con región en español
            search_results = ddgs.text(
                query_limpia, 
                max_results=max_resultados,
                region='es-es',  # Forzar resultados en español
                safesearch='off'
            )
            
            print(f"[DEBUG] Búsqueda completada")
            
            for resultado in search_results:
                titulo = resultado.get('title', '')
                snippet = resultado.get('body', '')
                url = resultado.get('href', '')
                
                if titulo and url:
                    resultados.append({
                        'titulo': titulo,
                        'snippet': snippet,
                        'url': url
                    })
                    print(f"[DEBUG] ✓ Resultado agregado: {titulo[:50]}...")
        
        print(f"[DEBUG] Total de resultados extraídos: {len(resultados)}")
        return resultados
        
    except Exception as e:
        print(f"[ERROR] Error en búsqueda: {e}")
        import traceback
        traceback.print_exc()
        return []


def buscar_y_resumir(query: str, max_resultados: int = 3) -> Dict:
    """
    Busca en internet y resume los resultados encontrados
    
    Args:
        query: Término de búsqueda
        max_resultados: Número de resultados a procesar
        
    Returns:
        Diccionario con resultados y resumen combinado
    """
    resultados = buscar_duckduckgo(query, max_resultados)
    
    if not resultados:
        return {
            'exito': False,
            'mensaje': 'No se encontraron resultados',
            'resultados': []
        }
    
    # Crear resumen combinado
    resumen_partes = []
    
    for i, resultado in enumerate(resultados, 1):
        resumen_partes.append(f"{i}. {resultado['titulo']}")
        if resultado['snippet']:
            resumen_partes.append(f"   {resultado['snippet']}")
        resumen_partes.append(f"   Fuente: {resultado['url']}")
        resumen_partes.append("")
    
    resumen_texto = "\n".join(resumen_partes)
    
    return {
        'exito': True,
        'query': query,
        'num_resultados': len(resultados),
        'resultados': resultados,
        'resumen': resumen_texto
    }


if __name__ == "__main__":
    # Prueba
    resultado = buscar_y_resumir("Python programming", 3)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

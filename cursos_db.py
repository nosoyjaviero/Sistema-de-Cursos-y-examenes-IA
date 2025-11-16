"""
Sistema de gestión de carpetas y documentos para Examinator
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict


class CursosDatabase:
    """Maneja la navegación de carpetas y documentos"""
    
    def __init__(self, base_path: str = "extracciones"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def listar_carpetas(self, ruta_relativa: str = "") -> List[dict]:
        """Lista todas las carpetas en una ruta"""
        ruta_completa = self.base_path / ruta_relativa
        
        if not ruta_completa.exists():
            return []
        
        carpetas = []
        for item in sorted(ruta_completa.iterdir()):
            if item.is_dir() and item.name != "resultados":
                # Contar documentos y subcarpetas
                num_documentos = len(list(item.glob("*.txt")))
                num_subcarpetas = len([x for x in item.iterdir() if x.is_dir() and x.name != "resultados"])
                
                carpetas.append({
                    "nombre": item.name,
                    "ruta": str(item.relative_to(self.base_path)),
                    "ruta_completa": str(item),
                    "num_documentos": num_documentos,
                    "num_subcarpetas": num_subcarpetas,
                    "fecha_modificacion": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
        
        return carpetas
    
    def listar_documentos(self, ruta_relativa: str = "") -> List[dict]:
        """Lista todos los documentos .txt en una ruta"""
        ruta_completa = self.base_path / ruta_relativa
        
        if not ruta_completa.exists():
            return []
        
        documentos = []
        for archivo in sorted(ruta_completa.glob("*.txt")):
            if archivo.parent.name == "resultados":
                continue
            
            stat = archivo.stat()
            documentos.append({
                "nombre": archivo.stem,
                "nombre_completo": archivo.name,
                "ruta": str(archivo.relative_to(self.base_path)),
                "ruta_completa": str(archivo),
                "tamaño_kb": round(stat.st_size / 1024, 2),
                "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return documentos
    
    def crear_carpeta(self, ruta_relativa: str, nombre: str) -> dict:
        """Crea una nueva carpeta"""
        ruta_completa = self.base_path / ruta_relativa / nombre
        
        if ruta_completa.exists():
            raise ValueError(f"La carpeta '{nombre}' ya existe")
        
        ruta_completa.mkdir(parents=True, exist_ok=True)
        
        return {
            "nombre": nombre,
            "ruta": str(ruta_completa.relative_to(self.base_path)),
            "ruta_completa": str(ruta_completa),
            "mensaje": f"Carpeta '{nombre}' creada exitosamente"
        }
    
    def eliminar_carpeta(self, ruta_relativa: str, forzar: bool = False) -> bool:
        """Elimina una carpeta (forzar=True elimina con contenido)"""
        ruta_completa = self.base_path / ruta_relativa
        
        if not ruta_completa.exists():
            return False
        
        if not forzar:
            # Verificar que esté vacía
            if any(ruta_completa.iterdir()):
                raise ValueError("La carpeta no está vacía. Usa forzar=True para eliminar con contenido.")
        else:
            # Eliminar recursivamente
            import shutil
            shutil.rmtree(ruta_completa)
            return True
        
        ruta_completa.rmdir()
        return True
    
    def mover_carpeta(self, ruta_origen: str, ruta_destino: str = "") -> dict:
        """Mueve una carpeta a otra ubicación"""
        import shutil
        
        ruta_origen_completa = self.base_path / ruta_origen
        
        if not ruta_origen_completa.exists():
            raise ValueError("La carpeta de origen no existe")
        
        if not ruta_origen_completa.is_dir():
            raise ValueError("La ruta de origen no es una carpeta")
        
        # Construir ruta destino
        nombre_carpeta = ruta_origen_completa.name
        ruta_destino_completa = self.base_path / ruta_destino / nombre_carpeta
        
        # Verificar que no exista ya en el destino
        if ruta_destino_completa.exists():
            raise ValueError(f"Ya existe una carpeta con el nombre '{nombre_carpeta}' en el destino")
        
        # Verificar que no se esté moviendo dentro de sí misma
        try:
            ruta_destino_completa.relative_to(ruta_origen_completa)
            raise ValueError("No se puede mover una carpeta dentro de sí misma")
        except ValueError as e:
            # Si no es relativo, está bien (el ValueError es esperado)
            if "No se puede mover" in str(e):
                raise e
            # Si es otro ValueError (no es relativo), continuar
            pass
        
        # Crear carpeta padre del destino si no existe
        ruta_destino_completa.parent.mkdir(parents=True, exist_ok=True)
        
        # Mover la carpeta
        shutil.move(str(ruta_origen_completa), str(ruta_destino_completa))
        
        return {
            "nombre": nombre_carpeta,
            "ruta_origen": ruta_origen,
            "ruta_destino": str(ruta_destino_completa.relative_to(self.base_path)),
            "mensaje": f"Carpeta '{nombre_carpeta}' movida exitosamente"
        }
    
    def renombrar_carpeta(self, ruta_actual: str, nuevo_nombre: str) -> dict:
        """Renombra una carpeta"""
        ruta_completa = self.base_path / ruta_actual
        
        if not ruta_completa.exists():
            raise ValueError("La carpeta no existe")
        
        if not ruta_completa.is_dir():
            raise ValueError("La ruta no es una carpeta")
        
        # Construir nueva ruta (mantener el padre, cambiar solo el nombre)
        carpeta_padre = ruta_completa.parent
        nueva_ruta = carpeta_padre / nuevo_nombre
        
        if nueva_ruta.exists():
            raise ValueError("Ya existe una carpeta con ese nombre")
        
        # Renombrar carpeta
        ruta_completa.rename(nueva_ruta)
        
        return {
            "nombre_anterior": ruta_completa.name,
            "nombre_nuevo": nuevo_nombre,
            "nueva_ruta": str(nueva_ruta.relative_to(self.base_path)),
            "mensaje": f"Carpeta renombrada a '{nuevo_nombre}'"
        }
    
    def eliminar_documento(self, ruta_relativa: str) -> bool:
        """Elimina un documento"""
        ruta_completa = self.base_path / ruta_relativa
        
        if not ruta_completa.exists():
            return False
        
        ruta_completa.unlink()
        return True
    
    def renombrar_documento(self, ruta_actual: str, nuevo_nombre: str) -> dict:
        """Renombra un documento"""
        ruta_completa = self.base_path / ruta_actual
        
        if not ruta_completa.exists():
            raise ValueError("El documento no existe")
        
        if not ruta_completa.is_file():
            raise ValueError("La ruta no es un archivo")
        
        # Guardar nombre anterior y extensión antes de renombrar
        nombre_anterior = ruta_completa.name
        extension_original = ruta_completa.suffix  # Obtiene .txt, .pdf, etc.
        
        # Si el nuevo nombre no tiene extensión, agregar la original
        if not nuevo_nombre.endswith(extension_original) and extension_original:
            nuevo_nombre_final = nuevo_nombre + extension_original
        else:
            nuevo_nombre_final = nuevo_nombre
        
        # Construir nueva ruta (mantener el padre, cambiar solo el nombre)
        carpeta_padre = ruta_completa.parent
        nueva_ruta = carpeta_padre / nuevo_nombre_final
        
        if nueva_ruta.exists():
            raise ValueError("Ya existe un documento con ese nombre")
        
        # Renombrar documento
        ruta_completa.rename(nueva_ruta)
        
        return {
            "nombre_anterior": nombre_anterior,
            "nombre_nuevo": nuevo_nombre_final,
            "nueva_ruta": str(nueva_ruta.relative_to(self.base_path)),
            "mensaje": f"Documento renombrado a '{nuevo_nombre_final}'"
        }
    
    def obtener_ruta_completa(self, ruta_relativa: str) -> str:
        """Convierte una ruta relativa a absoluta"""
        return str(self.base_path / ruta_relativa)
    
    def buscar_documentos(self, query: str) -> List[dict]:
        """Busca documentos por nombre"""
        query_lower = query.lower()
        resultados = []
        
        for archivo in self.base_path.rglob("*.txt"):
            if archivo.parent.name == "resultados":
                continue
            
            if query_lower in archivo.stem.lower():
                stat = archivo.stat()
                resultados.append({
                    "nombre": archivo.stem,
                    "ruta": str(archivo.relative_to(self.base_path)),
                    "ruta_completa": str(archivo),
                    "carpeta": str(archivo.parent.relative_to(self.base_path)),
                    "tamaño_kb": round(stat.st_size / 1024, 2)
                })
        
        return resultados
    
    def obtener_contenido_documento(self, ruta_relativa: str) -> dict:
        """Obtiene el contenido de un documento"""
        ruta_completa = self.base_path / ruta_relativa
        
        if not ruta_completa.exists():
            raise ValueError("Documento no encontrado")
        
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        return {
            "nombre": ruta_completa.stem,
            "ruta": ruta_relativa,
            "contenido": contenido,
            "tamaño_kb": round(ruta_completa.stat().st_size / 1024, 2),
            "lineas": len(contenido.split('\n'))
        }
    
    def obtener_arbol(self, ruta_relativa: str = "", max_depth: int = 3, depth: int = 0) -> dict:
        """Obtiene el árbol de carpetas y documentos"""
        if depth >= max_depth:
            return None
        
        ruta_completa = self.base_path / ruta_relativa
        
        if not ruta_completa.exists():
            return None
        
        arbol = {
            "nombre": ruta_completa.name if ruta_relativa else "extracciones",
            "ruta": ruta_relativa,
            "tipo": "carpeta",
            "carpetas": [],
            "documentos": []
        }
        
        # Agregar subcarpetas
        for item in sorted(ruta_completa.iterdir()):
            if item.is_dir() and item.name != "resultados":
                subarbol = self.obtener_arbol(
                    str(item.relative_to(self.base_path)), 
                    max_depth, 
                    depth + 1
                )
                if subarbol:
                    arbol["carpetas"].append(subarbol)
        
        # Agregar documentos
        for archivo in sorted(ruta_completa.glob("*.txt")):
            arbol["documentos"].append({
                "nombre": archivo.stem,
                "ruta": str(archivo.relative_to(self.base_path))
            })
        
        return arbol


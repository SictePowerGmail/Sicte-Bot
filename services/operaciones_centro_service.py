import os
import pandas as pd
from datetime import datetime
from repositories.operaciones_centro_repository import PreoperacionalOperacionesCentroRepository

class OperacionesCentroPreoperacionalService:
    """Servicio para manejar la lógica de negocio de Operaciones Centro (Preoperacional)."""
    
    def __init__(self):
        self.repo = PreoperacionalOperacionesCentroRepository()

    def generar_excel_preoperacional_centro(self):
        """
        Consulta preoperacional operaciones centro, genera un archivo Excel y devuelve la ruta.
        Si no hay datos, retorna None.
        """
        data, columnas = self.repo.get_preoperacional_operaciones_centro()
        
        if not data:
            return None
            
        # Crear DataFrame
        df = pd.DataFrame(data, columns=columnas)
        
        # Crear nombre de archivo temporal
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"Preoperacional_Operaciones_R4_{fecha_str}.xlsx"
        
        # Guardar como Excel
        df.to_excel(file_path, index=False)
        
        return file_path

# Instancia global del servicio
preoperacional_centro_service_instance = OperacionesCentroPreoperacionalService()

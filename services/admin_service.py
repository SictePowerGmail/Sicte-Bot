import os
import pandas as pd
from datetime import datetime
from repositories.admin_repository import AdminRepository

class AdminService:
    """Servicio para manejar la lógica de negocio de Administrador (Penalizaciones)."""
    
    def __init__(self):
        self.repo = AdminRepository()

    def generar_excel_penalizaciones(self):
        """
        Consulta las penalizaciones, genera un archivo Excel y devuelve la ruta.
        Si no hay datos, retorna None.
        """
        data, columnas = self.repo.get_penalizaciones()
        
        if not data:
            return None
            
        # Crear DataFrame
        df = pd.DataFrame(data, columns=columnas)
        
        # Crear nombre de archivo temporal
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"Consolidado_Penalizaciones_{fecha_str}.xlsx"
        
        # Guardar como Excel
        df.to_excel(file_path, index=False)
        
        return file_path

# Instancia global del servicio
admin_service_instance = AdminService()

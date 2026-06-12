from repositories.enel_repository import EnelRepository

class EnelService:
    """Servicio para manejar la lógica de negocio de Enel."""
    
    def __init__(self):
        self.enel_repo = EnelRepository()

    def consultar_orden(self, orden):
        """Consulta la información de una orden específica, incluyendo baremos y materiales."""
        resultado = self.enel_repo.get_orden_detalle(orden)
        resultado_baremos = self.enel_repo.get_orden_baremos(orden)
        resultado_material = self.enel_repo.get_orden_material(orden)
        
        return resultado, resultado_baremos, resultado_material

    def consultar_rotulo(self, rotulo):
        """Consulta todas las órdenes asociadas a un rótulo."""
        ordenes = self.enel_repo.get_ordenes_by_rotulo(rotulo)
        
        if not ordenes:
            return 0, []
        
        detalles = []
        for orden in ordenes:
            resultado = self.enel_repo.get_orden_detalle(orden)
            if not resultado: continue
            
            resultado_baremos = self.enel_repo.get_orden_baremos(orden)
            resultado_material = self.enel_repo.get_orden_material(orden)
            
            detalles.append((resultado, resultado_baremos, resultado_material))
            
        return len(ordenes), detalles

# Instancia global del servicio
enel_service_instance = EnelService()

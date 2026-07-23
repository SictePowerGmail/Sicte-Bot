import pymysql
from database.db_railway import RailwayDBManager

class AdminRepository:
    """Repositorio para acceder a la vista de penalizaciones (Railway)."""
    
    def __init__(self):
        self.db = RailwayDBManager()

    def get_penalizaciones(self):
        """Obtiene todos los registros de la vista vw_penalizaciones."""
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                # Se asume que la vista se llama vw_penalizaciones
                sql = "SELECT * FROM vw_penalizaciones"
                cursor.execute(sql)
                data = cursor.fetchall()
                # Obtener los nombres de las columnas
                columnas = [desc[0] for desc in cursor.description] if cursor.description else []
                return data, columnas

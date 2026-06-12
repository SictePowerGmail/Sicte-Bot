import pymysql
from database.db_servidor_san_cipriano import ServidorSanCiprianoDBManager

class AdminRepository:
    """Repositorio para acceder a la base de datos de administración (San Cipriano)."""
    
    def __init__(self):
        self.db = ServidorSanCiprianoDBManager()

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

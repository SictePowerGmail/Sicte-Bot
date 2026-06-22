import pymysql
from database.db_usuarios import UsuariosDBManager

class PreoperacionalOperacionesCentroRepository:
    """Repositorio para acceder a la base de datos de administración (San Cipriano)."""
    
    def __init__(self):
        self.db = UsuariosDBManager()

    def get_preoperacional_operaciones_centro(self):
        """Obtiene todos los registros de la vista vw_sis_preoperacional."""
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                # Se asume que la vista se llama vw_penalizaciones
                sql = "SELECT * FROM vw_sis_preoperacional"
                cursor.execute(sql)
                data = cursor.fetchall()
                # Obtener los nombres de las columnas
                columnas = [desc[0] for desc in cursor.description] if cursor.description else []
                return data, columnas

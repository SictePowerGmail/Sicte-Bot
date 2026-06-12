import pymysql
from database.db_enel import EnelDBManager

class EnelRepository:
    """Repositorio para manejar el acceso a la base de datos de Enel."""
    
    def __init__(self):
        self.db = EnelDBManager()

    def get_orden_detalle(self, orden):
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                sql = """
                SELECT ORDEN, ROTULO, ESTADO, FECHA_ESTADO, LOCALIDAD, TIPO_MOVIL
                FROM vw_ordenes WHERE ORDEN = %s ORDER BY FECHA_ESTADO DESC LIMIT 1
                """
                cursor.execute(sql, (orden,))
                return cursor.fetchone()

    def get_orden_baremos(self, orden):
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                sql = """
                SELECT Id_Item_3, Cantidad_Instalada, amap, Item
                FROM vw_baremos WHERE orden = %s
                """
                cursor.execute(sql, (orden,))
                return cursor.fetchall()

    def get_orden_material(self, orden):
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                sql = """
                SELECT Id_Item_3, Cantidad_Instalada, Item
                FROM vw_material_instalado
                WHERE orden = %s AND Id_Item_3 <> 0
                """
                cursor.execute(sql, (orden,))
                return cursor.fetchall()

    def get_ordenes_by_rotulo(self, rotulo):
        with self.db.get_connection() as conexion:
            with conexion.cursor() as cursor:
                sql = "SELECT DISTINCT ORDEN FROM vw_ordenes WHERE ROTULO = %s"
                cursor.execute(sql, (rotulo,))
                return [row[0] for row in cursor.fetchall()]

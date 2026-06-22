import pymysql
from database.db_usuarios import UsuariosDBManager

class UserRepository:
    """Repositorio para manejar el acceso a datos relacionados con Usuarios y Roles."""
    
    def __init__(self):
        self.db = UsuariosDBManager()

    def verificar_cedula_existe(self, cedula):
        with self.db.get_connection() as conexion:
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT cedula FROM `user` WHERE cedula = %s LIMIT 1"
                cursor.execute(sql, (cedula,))
                return cursor.fetchone() is not None

    def obtener_usuario_por_cedula(self, cedula):
        with self.db.get_connection() as conexion:
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT cedula, contrasena FROM `user` WHERE cedula = %s LIMIT 1"
                cursor.execute(sql, (cedula,))
                return cursor.fetchone()

    def obtener_roles_usuario(self, cedula):
        roles = []
        with self.db.get_connection() as conexion:
            with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT enelApConsultas, wfmOperacionesNorte, penalizaciones, wfmOperacionesCentro FROM rol_chatbot_telegram WHERE cedula = %s LIMIT 1"
                cursor.execute(sql, (cedula,))
                resultado = cursor.fetchone()
                
                if resultado:
                    if resultado.get('enelApConsultas'):
                        roles.append('enel')
                    if resultado.get('wfmOperacionesNorte'):
                        roles.append('operaciones')
                    if resultado.get('penalizaciones'):
                        roles.append('admin')
                    if resultado.get('wfmOperacionesCentro'):
                        roles.append('operaciones_centro')
        return roles

    def agregar_usuario_db(self, cedula, hashed_password, rol):
        with self.db.get_connection() as conexion:
            try:
                with conexion.cursor() as cursor:
                    sql_user = "INSERT INTO `user` (cedula, contrasena) VALUES (%s, %s)"
                    cursor.execute(sql_user, (cedula, hashed_password))
                    
                    columna_rol = ""
                    if rol == 'enel': columna_rol = "enelApConsultas"
                    elif rol == 'operaciones': columna_rol = "wfmOperacionesNorte"
                    elif rol == 'admin': columna_rol = "penalizaciones"
                    elif rol == 'operaciones_centro': columna_rol = "wfmOperacionesCentro"
                    
                    sql_rol = f"INSERT INTO rol_chatbot_telegram (cedula, {columna_rol}) VALUES (%s, %s)"
                    cursor.execute(sql_rol, (cedula, 'X'))
                conexion.commit()
                return True
            except pymysql.MySQLError as e:
                conexion.rollback()
                raise e

import pymysql
import bcrypt
from datetime import datetime
from database.db_usuarios import obtener_conexion_usuarios
from models.user import User

# Diccionario en memoria para mantener las sesiones iniciadas rápidamente
# Estructura: { chat_id: User }
active_sessions = {}

def verificar_cedula_existe(cedula):
    """Verifica si la cédula existe en la tabla user."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        
        sql = "SELECT cedula FROM `user` WHERE cedula = %s LIMIT 1"
        cursor.execute(sql, (cedula,))
        resultado = cursor.fetchone()
        
        return resultado is not None
    except pymysql.MySQLError as e:
        print(f"Error de DB verificando cédula: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

def obtener_roles_usuario(cedula):
    """Consulta la tabla rol_chatbot_telegram para obtener los roles basados en la cédula o si es invitado."""
    conexion = None
    cursor = None
    roles = []
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        
        sql = "SELECT enelApConsultas, wfmOperacionesNorte, penalizaciones FROM rol_chatbot_telegram WHERE cedula = %s LIMIT 1"
        cursor.execute(sql, (cedula,))
        resultado = cursor.fetchone()
        
        if resultado:
            if resultado.get('enelApConsultas'):
                roles.append('enel')
            if resultado.get('wfmOperacionesNorte'):
                roles.append('operaciones')
            if resultado.get('penalizaciones'):
                roles.append('admin')
                
        return roles
    except pymysql.MySQLError as e:
        print(f"Error de DB obteniendo roles: {e}")
        return []
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

def autenticar_usuario(cedula, password, telegram_id):
    """
    Verifica las credenciales y el hash en la tabla user.
    Si son válidas, obtiene los roles y devuelve el objeto User.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        
        sql = "SELECT cedula, contrasena FROM `user` WHERE cedula = %s LIMIT 1"
        cursor.execute(sql, (cedula,))
        resultado = cursor.fetchone()
        
        if resultado:
            # Obtener el hash de la base de datos
            hash_db = resultado['contrasena'].encode('utf-8')
            
            # Validar la contraseña proporcionada contra el hash con bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), hash_db):
                
                roles = obtener_roles_usuario(cedula)
                user = User(telegram_id=telegram_id, roles=roles, cedula=cedula)
                active_sessions[telegram_id] = user
                return user
            else:
                print(f"Inicio de sesión fallido para la cédula '{cedula}': Contraseña incorrecta. (Telegram ID: {telegram_id})")
        else:
            print(f"Inicio de sesión fallido: La cédula '{cedula}' no existe. (Telegram ID: {telegram_id})")
                
        return None
        
    except pymysql.MySQLError as e:
        print(f"Error de DB autenticando usuario: {e}")
        return None
    except Exception as e:
        print(f"Error de autenticación: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

def logear_invitado(telegram_id):
    """Logea a un usuario como invitado consultando directamente la tabla de roles."""
    roles = obtener_roles_usuario("Invitado")
    user = User(telegram_id=telegram_id, roles=roles, cedula="Invitado")
    active_sessions[telegram_id] = user
    return user

def get_session(telegram_id):
    """Retorna la sesión activa para el telegram_id dado."""
    return active_sessions.get(telegram_id)

def logout_usuario(telegram_id):
    """Cierra la sesión del usuario limpiando en memoria."""
    if telegram_id in active_sessions:
        del active_sessions[telegram_id]

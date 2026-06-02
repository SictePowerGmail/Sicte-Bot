import pymysql
from database.db_usuarios import obtener_conexion_usuarios
from models.user import User

# Diccionario en memoria para mantener las sesiones iniciadas
# Estructura: { chat_id: User }
active_sessions = {}

def autenticar_usuario(username, password, telegram_id):
    """
    Verifica las credenciales en la base de datos de aplicativos_claro.
    Si son válidas, registra la sesión y devuelve el objeto User.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        
        # NOTA: Asegúrate de que los nombres de los campos coincidan con tu tabla 'usuarios'
        sql = "SELECT id, usuario, rol FROM usuarios WHERE usuario = %s AND password = %s LIMIT 1"
        cursor.execute(sql, (username, password))
        resultado = cursor.fetchone()
        
        if resultado:
            user = User(telegram_id=telegram_id, role=resultado['rol'], username=resultado['usuario'])
            active_sessions[telegram_id] = user
            return user
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

def get_session(telegram_id):
    """Retorna la sesión activa para el telegram_id dado, o None si no está logueado."""
    return active_sessions.get(telegram_id)

def logout_usuario(telegram_id):
    """Cierra la sesión del usuario."""
    if telegram_id in active_sessions:
        del active_sessions[telegram_id]

import pymysql
import bcrypt
from datetime import datetime
from database.db_usuarios import obtener_conexion_usuarios
from models.user import User

# Diccionario en memoria para mantener las sesiones iniciadas rápidamente
# Estructura: { chat_id: User }
active_sessions = {}

def autenticar_usuario(username, password, telegram_id):
    """
    Verifica las credenciales y el hash en la base de datos de aplicativos_claro.
    Si son válidas, actualiza telegram_chat_id y fecha_login, registra la sesión y devuelve el objeto User.
    """
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        
        sql = "SELECT id, usuario, password, rol FROM usuarios WHERE usuario = %s LIMIT 1"
        cursor.execute(sql, (username,))
        resultado = cursor.fetchone()
        
        if resultado:
            # Obtener el hash de la base de datos
            hash_db = resultado['password'].encode('utf-8')
            
            # Validar la contraseña proporcionada contra el hash con bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), hash_db):
                # Contraseña correcta, actualizamos datos de sesión en BD
                sql_update = "UPDATE usuarios SET telegram_chat_id = %s, fecha_login = %s WHERE id = %s"
                fecha_actual = datetime.now()
                cursor.execute(sql_update, (telegram_id, fecha_actual, resultado['id']))
                conexion.commit()
                
                user = User(telegram_id=telegram_id, role=resultado['rol'], username=resultado['usuario'])
                active_sessions[telegram_id] = user
                return user
            else:
                print(f"Inicio de sesión fallido para el usuario '{username}': Contraseña incorrecta. (Telegram ID: {telegram_id})")
        else:
            print(f"Inicio de sesión fallido: El usuario '{username}' no existe. (Telegram ID: {telegram_id})")
                
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
    """Retorna la sesión activa para el telegram_id dado, verificando primero en memoria y luego en DB."""
    if telegram_id in active_sessions:
        return active_sessions[telegram_id]
        
    # Si no está en memoria, buscamos en base de datos para recuperar la sesión activa
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        
        sql = "SELECT usuario, rol FROM usuarios WHERE telegram_chat_id = %s LIMIT 1"
        cursor.execute(sql, (telegram_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            user = User(telegram_id=telegram_id, role=resultado['rol'], username=resultado['usuario'])
            active_sessions[telegram_id] = user
            return user
            
        return None
    except pymysql.MySQLError as e:
        print(f"Error de DB obteniendo sesión: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

def logout_usuario(telegram_id):
    """Cierra la sesión del usuario limpiando el telegram_chat_id en la BD y en memoria."""
    if telegram_id in active_sessions:
        del active_sessions[telegram_id]
        
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor()
        
        sql = "UPDATE usuarios SET telegram_chat_id = NULL WHERE telegram_chat_id = %s"
        cursor.execute(sql, (telegram_id,))
        conexion.commit()
    except pymysql.MySQLError as e:
        print(f"Error de DB en logout: {e}")
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

import os
import pymysql
import bcrypt
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def obtener_conexion_usuarios():
    return pymysql.connect(
        host=os.getenv("host_usuarios"),
        user=os.getenv("user_usuarios"),
        password=os.getenv("password_usuarios"),
        database=os.getenv("db_usuarios"),
        port=int(os.getenv("port_usuarios", 40164)),
        connect_timeout=10
    )

def agregar_usuario():
    print("=== Agregar Nuevo Usuario al Bot ===")
    cedula = input("Ingresa la cédula: ").strip()
    password = input("Ingresa la contraseña: ").strip()
    rol = input("Ingresa el rol principal a agregar (admin, enel, operaciones): ").strip().lower()
    
    if not cedula or not password or not rol:
        print("Error: Todos los campos son obligatorios.")
        return
        
    if rol not in ['admin', 'enel', 'operaciones']:
        print("Error: Rol no válido. Debe ser admin, enel u operaciones.")
        return
        
    # Encriptar la contraseña
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=10)).decode('utf-8')
    
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion_usuarios()
        cursor = conexion.cursor()
        
        # Insertar en tabla user
        sql_user = "INSERT INTO user (cedula, contrasena) VALUES (%s, %s)"
        cursor.execute(sql_user, (cedula, hashed_password))
        
        # Insertar en tabla de roles (inicializando en null y seteando solo el correspondiente)
        columna_rol = ""
        if rol == 'enel': columna_rol = "enelApConsultas"
        elif rol == 'operaciones': columna_rol = "wfmOperacionesNorte"
        elif rol == 'admin': columna_rol = "penalizaciones"
        
        sql_rol = f"INSERT INTO rol_chatbot_telegram (cedula, {columna_rol}) VALUES (%s, %s)"
        cursor.execute(sql_rol, (cedula, 'X'))
        
        conexion.commit()
        
        print(f"\n¡Usuario con cédula '{cedula}' (Rol: {rol}) agregado exitosamente!")
    except pymysql.MySQLError as e:
        print(f"\nError de base de datos: {e}")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

if __name__ == "__main__":
    agregar_usuario()

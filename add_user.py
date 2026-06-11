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
    usuario = input("Ingresa el nombre de usuario: ").strip()
    password = input("Ingresa la contraseña: ").strip()
    rol = input("Ingresa el rol (admin, enel, operaciones): ").strip().lower()
    
    if not usuario or not password or not rol:
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
        
        sql = "INSERT INTO usuarios (usuario, password, rol) VALUES (%s, %s, %s)"
        cursor.execute(sql, (usuario, hashed_password, rol))
        conexion.commit()
        
        print(f"\n¡Usuario '{usuario}' (Rol: {rol}) agregado exitosamente con contraseña encriptada!")
    except pymysql.MySQLError as e:
        print(f"\nError de base de datos: {e}")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()

if __name__ == "__main__":
    agregar_usuario()

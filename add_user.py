import os
import bcrypt
from dotenv import load_dotenv
from repositories.user_repository import UserRepository

# Cargar variables de entorno
load_dotenv()

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
    
    repo = UserRepository()
    
    try:
        repo.agregar_usuario_db(cedula, hashed_password, rol)
        print(f"\n¡Usuario con cédula '{cedula}' (Rol: {rol}) agregado exitosamente!")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    agregar_usuario()

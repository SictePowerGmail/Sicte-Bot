import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("Conectando a la DB...")
    conexion = pymysql.connect(
        host=os.getenv("host_usuarios"),
        user=os.getenv("user_usuarios"),
        password=os.getenv("password_usuarios"),
        database=os.getenv("db_usuarios"),
        port=int(os.getenv("port_usuarios", 40164)),
        connect_timeout=10
    )
    cursor = conexion.cursor()
    print("¡Conexión exitosa a", os.getenv("db_usuarios"), "!")

    from services.auth_service import verificar_cedula_existe, obtener_roles_usuario
    print("Test verificar cedula '80504117':", verificar_cedula_existe('80504117'))
    print("Test obtener roles '80504117':", obtener_roles_usuario('80504117'))
    print("Test obtener roles 'Invitado':", obtener_roles_usuario('Invitado'))


    print("\nProbando tabla `rol_chatbot_telegram`...")
    cursor.execute("SELECT * FROM `rol_chatbot_telegram` LIMIT 5")
    roles = cursor.fetchall()
    print("Roles encontrados:", len(roles))
    for r in roles:
        print(r)

except Exception as e:
    print("ERROR:", e)
finally:
    if 'cursor' in locals() and cursor: cursor.close()
    if 'conexion' in locals() and conexion: conexion.close()

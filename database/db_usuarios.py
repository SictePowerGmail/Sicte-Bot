import os
import pymysql

def obtener_conexion_usuarios():
    """Retorna una conexión a la base de datos de usuarios (aplicativos_claro en Railway)."""
    return pymysql.connect(
        host=os.getenv("host_usuarios"),
        user=os.getenv("user_usuarios"),
        password=os.getenv("password_usuarios"),
        database=os.getenv("db_usuarios"),
        port=int(os.getenv("port_usuarios", 40164)),
        connect_timeout=10
    )

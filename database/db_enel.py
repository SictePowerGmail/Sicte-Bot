import os
import pymysql

def obtener_conexion_enel():
    """Retorna una conexión a la base de datos de Enel."""
    return pymysql.connect(
        host=os.getenv("host_enel"),
        user=os.getenv("user_enel"),
        password=os.getenv("password_enel"),
        database=os.getenv("db_enel"),
        port=int(os.getenv("port_enel", 3306)),
        connect_timeout=10
    )

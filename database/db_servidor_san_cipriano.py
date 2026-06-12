import os
from database.db_connection import DatabaseConnection

class ServidorSanCiprianoDBManager(DatabaseConnection):
    """Gestor de conexiones Singleton para la base de datos de San Cipriano (Railway)."""
    def __init__(self):
        super().__init__(
            host=os.getenv("host_servidor_san_cipriano"),
            user=os.getenv("user_servidor_san_cipriano"),
            password=os.getenv("password_servidor_san_cipriano"),
            database=os.getenv("db_servidor_san_cipriano"),
            port=int(os.getenv("port_servidor_san_cipriano", 3309))
        )
import os
from database.db_connection import DatabaseConnection

class UsuariosDBManager(DatabaseConnection):
    """Gestor de conexiones Singleton para la base de datos de usuarios (Railway)."""
    def __init__(self):
        super().__init__(
            host=os.getenv("host_usuarios"),
            user=os.getenv("user_usuarios"),
            password=os.getenv("password_usuarios"),
            database=os.getenv("db_usuarios"),
            port=int(os.getenv("port_usuarios", 40164))
        )

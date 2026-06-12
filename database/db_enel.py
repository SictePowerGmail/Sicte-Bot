import os
from database.db_connection import DatabaseConnection

class EnelDBManager(DatabaseConnection):
    """Gestor de conexiones Singleton para la base de datos de Enel."""
    def __init__(self):
        super().__init__(
            host=os.getenv("host_enel"),
            user=os.getenv("user_enel"),
            password=os.getenv("password_enel"),
            database=os.getenv("db_enel"),
            port=int(os.getenv("port_enel", 3306))
        )

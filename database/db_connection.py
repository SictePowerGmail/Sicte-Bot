import pymysql
from contextlib import contextmanager

class DatabaseConnection:
    """Clase base para manejar conexiones usando el patrón Singleton."""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._pool = None
            cls._instance.config = {}
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, 'initialized'):
            self.config = kwargs
            self.initialized = True

    @contextmanager
    def get_connection(self):
        """Context manager para obtener y liberar conexiones de forma segura."""
        conexion = None
        try:
            conexion = pymysql.connect(
                host=self.config.get('host'),
                user=self.config.get('user'),
                password=self.config.get('password'),
                database=self.config.get('database'),
                port=int(self.config.get('port', 3306))
            )
            yield conexion
        except pymysql.MySQLError as e:
            print(f"Error de base de datos en {self.__class__.__name__}: {e}")
            raise
        finally:
            if conexion:
                conexion.close()

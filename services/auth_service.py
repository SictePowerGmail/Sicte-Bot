import bcrypt
from models.user import User
from repositories.user_repository import UserRepository

class AuthService:
    """Servicio para manejar la lógica de negocio de la autenticación."""
    
    # Singleton o estado compartido de sesiones en memoria
    active_sessions = {}
    
    def __init__(self):
        self.user_repo = UserRepository()

    def verificar_cedula_existe(self, cedula):
        return self.user_repo.verificar_cedula_existe(cedula)

    def obtener_roles_usuario(self, cedula):
        return self.user_repo.obtener_roles_usuario(cedula)

    def autenticar_usuario(self, cedula, password, telegram_id):
        resultado = self.user_repo.obtener_usuario_por_cedula(cedula)
        
        if resultado:
            hash_db = resultado['contrasena'].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hash_db):
                roles = self.obtener_roles_usuario(cedula)
                user = User(
                    telegram_id=telegram_id,
                    roles=roles,
                    cedula=cedula,
                    nombre=resultado["nombre"]
                    )
                self.active_sessions[telegram_id] = user
                return user
            else:
                print(f"Inicio de sesión fallido para la cédula '{cedula}': Contraseña incorrecta. (Telegram ID: {telegram_id})")
        else:
            print(f"Inicio de sesión fallido: La cédula '{cedula}' no existe. (Telegram ID: {telegram_id})")
                
        return None

    def logear_invitado(self, telegram_id):
        roles = self.obtener_roles_usuario("Invitado")
        user = User(telegram_id=telegram_id, roles=roles, cedula="Invitado")
        self.active_sessions[telegram_id] = user
        return user

    def get_session(self, telegram_id):
        return self.active_sessions.get(telegram_id)

    def logout_usuario(self, telegram_id):
        if telegram_id in self.active_sessions:
            del self.active_sessions[telegram_id]

# Instancia global del servicio (Dependency Injection simplificada para los handlers funcionales)
auth_service_instance = AuthService()

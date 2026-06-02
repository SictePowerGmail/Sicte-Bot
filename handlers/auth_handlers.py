from telebot import TeleBot
from states.bot_states import AuthState
from services.auth_service import get_session, autenticar_usuario, logout_usuario

login_temp_data = {}

def register_auth_handlers(bot: TeleBot):
    
    @bot.message_handler(commands=['start', 'login'])
    def handle_start(message):
        user = get_session(message.from_user.id)
        if user:
            bot.send_message(message.chat.id, f"Hola {user.username}, ya tienes una sesión iniciada con rol: {user.role}.")
            from handlers.menu_handlers import mostrar_menu_por_rol
            mostrar_menu_por_rol(bot, message.chat.id, user)
        else:
            bot.send_message(message.chat.id, "¡Bienvenido! Por favor, ingresa tu usuario:")
            bot.set_state(message.from_user.id, AuthState.waiting_for_username, message.chat.id)

    @bot.message_handler(state=AuthState.waiting_for_username)
    def process_username(message):
        login_temp_data[message.from_user.id] = message.text
        bot.send_message(message.chat.id, "Por favor, ingresa tu contraseña:")
        bot.set_state(message.from_user.id, AuthState.waiting_for_password, message.chat.id)

    @bot.message_handler(state=AuthState.waiting_for_password)
    def process_password(message):
        username = login_temp_data.get(message.from_user.id)
        password = message.text
        
        # Eliminar el mensaje de la contraseña por seguridad (opcional, pero útil)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass # Si el bot no tiene permisos de admin, no podrá borrar mensajes
            
        user = autenticar_usuario(username, password, message.from_user.id)
        if user:
            bot.send_message(message.chat.id, f"¡Sesión iniciada exitosamente!\nBienvenido {user.username} ({user.role})")
            bot.delete_state(message.from_user.id, message.chat.id)
            if message.from_user.id in login_temp_data:
                del login_temp_data[message.from_user.id]
            
            from handlers.menu_handlers import mostrar_menu_por_rol
            mostrar_menu_por_rol(bot, message.chat.id, user)
        else:
            bot.send_message(message.chat.id, "Credenciales incorrectas. Intenta nuevamente ingresando tu usuario:")
            bot.set_state(message.from_user.id, AuthState.waiting_for_username, message.chat.id)

    @bot.message_handler(commands=['logout'])
    def handle_logout(message):
        logout_usuario(message.from_user.id)
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, "Sesión cerrada. Usa /start para volver a ingresar.")

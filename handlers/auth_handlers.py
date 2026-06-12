from telebot import TeleBot, types
from states.bot_states import AuthState
from services.auth_service import get_session, autenticar_usuario, logout_usuario, logear_invitado

login_temp_data = {}

def register_auth_handlers(bot: TeleBot):
    
    @bot.message_handler(commands=['start', 'login'])
    def handle_start(message):
        user = get_session(message.from_user.id)
        if user:
            roles_str = ", ".join(user.roles) if user.roles else "Sin roles"
            bot.send_message(message.chat.id, f"Hola {user.cedula}, ya tienes una sesión iniciada con rol: {roles_str}.")
            from handlers.menu_handlers import mostrar_menu_por_rol
            mostrar_menu_por_rol(bot, message.chat.id, user)
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn_login = types.InlineKeyboardButton("🔑 Iniciar Sesión", callback_data="login_normal")
            btn_guest = types.InlineKeyboardButton("👤 Entrar como Invitado", callback_data="login_guest")
            markup.add(btn_login, btn_guest)
            bot.send_message(message.chat.id, "¡Bienvenido! Por favor, selecciona una opción para ingresar:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data in ["login_normal", "login_guest"])
    def callback_login(call):
        bot.answer_callback_query(call.id)
        if call.data == "login_normal":
            bot.send_message(call.message.chat.id, "Por favor, ingresa tu cédula:")
            bot.set_state(call.from_user.id, AuthState.waiting_for_username, call.message.chat.id)
        elif call.data == "login_guest":
            user = logear_invitado(call.from_user.id)
            roles_str = ", ".join(user.roles) if user.roles else "Sin roles"
            bot.send_message(call.message.chat.id, f"¡Has ingresado como Invitado!\nRoles asignados: {roles_str}")
            from handlers.menu_handlers import mostrar_menu_por_rol
            mostrar_menu_por_rol(bot, call.message.chat.id, user)

    @bot.message_handler(state=AuthState.waiting_for_username)
    def process_cedula(message):
        login_temp_data[message.from_user.id] = message.text
        bot.send_message(message.chat.id, "Por favor, ingresa tu contraseña:")
        bot.set_state(message.from_user.id, AuthState.waiting_for_password, message.chat.id)

    @bot.message_handler(state=AuthState.waiting_for_password)
    def process_password(message):
        cedula = login_temp_data.get(message.from_user.id)
        password = message.text
        
        # Eliminar el mensaje de la contraseña por seguridad
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
            
        user = autenticar_usuario(cedula, password, message.from_user.id)
        if user:
            roles_str = ", ".join(user.roles) if user.roles else "Sin roles"
            bot.send_message(message.chat.id, f"¡Sesión iniciada exitosamente!\nBienvenido {user.cedula} ({roles_str})")
            bot.delete_state(message.from_user.id, message.chat.id)
            if message.from_user.id in login_temp_data:
                del login_temp_data[message.from_user.id]
            
            from handlers.menu_handlers import mostrar_menu_por_rol
            mostrar_menu_por_rol(bot, message.chat.id, user)
        else:
            bot.send_message(message.chat.id, "Credenciales incorrectas. Intenta nuevamente ingresando tu cédula:")
            bot.set_state(message.from_user.id, AuthState.waiting_for_username, message.chat.id)

    @bot.message_handler(commands=['logout'])
    def handle_logout(message):
        logout_usuario(message.from_user.id)
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, "Sesión cerrada. Usa /start para volver a ingresar.")

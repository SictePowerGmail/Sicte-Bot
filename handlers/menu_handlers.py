from telebot import TeleBot, types

def mostrar_submenu_directo(bot, chat_id, rol, con_volver=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    titulo = ""
    
    if rol == 'enel':
        markup.add(
            types.KeyboardButton("📌 Consultar Orden"),
            types.KeyboardButton("🏷️ Consultar Rótulo")
        )
        titulo = "📝 Menú Enel. Selecciona una opción:"
    elif rol == 'admin':
        markup.add(
            types.KeyboardButton("🛠️ Admin: Consultar Orden"),
            types.KeyboardButton("🛠️ Admin: Consultar Rótulo")
        )
        titulo = "⚙️ Menú Administrador. Selecciona una opción:"
    elif rol == 'operaciones':
        markup.add(
            types.KeyboardButton("📤 Subir Archivo")
        )
        titulo = "📝 Menú Operaciones. Selecciona una opción:"
    else:
        bot.send_message(chat_id, "Tu rol no tiene un menú asignado.", reply_markup=types.ReplyKeyboardRemove())
        return

    if con_volver:
        markup.add(types.KeyboardButton("⬅️ Volver al Menú Principal"))
        
    bot.send_message(chat_id, titulo, reply_markup=markup)

def mostrar_menu_por_rol(bot: TeleBot, chat_id, user):
    roles = user.roles
    
    # Si no tiene roles
    if not roles:
        bot.send_message(chat_id, "Tu rol no tiene un menú asignado.", reply_markup=types.ReplyKeyboardRemove())
        return
        
    # Si solo tiene 1 rol, mostrar el submenú directamente sin botón de volver
    if len(roles) == 1:
        mostrar_submenu_directo(bot, chat_id, roles[0], con_volver=False)
        return
        
    # Si tiene más de 1 rol, mostrar el menú principal
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    has_menu = False
    
    if 'enel' in roles:
        markup.add(types.KeyboardButton("🏢 Menú Enel"))
        has_menu = True
        
    if 'admin' in roles:
        markup.add(types.KeyboardButton("⚙️ Menú Admin"))
        has_menu = True
        
    if 'operaciones' in roles:
        markup.add(types.KeyboardButton("👷‍♂️ Menú Operaciones"))
        has_menu = True
        
    if has_menu:
        bot.send_message(chat_id, "Selecciona el módulo al que deseas ingresar:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Tu rol no tiene un menú asignado.", reply_markup=types.ReplyKeyboardRemove())

def register_menu_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text in ["🏢 Menú Enel", "⚙️ Menú Admin", "👷‍♂️ Menú Operaciones", "⬅️ Volver al Menú Principal"])
    def handle_submenus(message):
        from services.auth_service import get_session
        user = get_session(message.from_user.id)
        if not user:
            return

        text = message.text
        if text == "⬅️ Volver al Menú Principal":
            mostrar_menu_por_rol(bot, message.chat.id, user)
            return
            
        if text == "🏢 Menú Enel" and 'enel' in user.roles:
            mostrar_submenu_directo(bot, message.chat.id, 'enel', con_volver=True)
            
        elif text == "⚙️ Menú Admin" and 'admin' in user.roles:
            mostrar_submenu_directo(bot, message.chat.id, 'admin', con_volver=True)
            
        elif text == "👷‍♂️ Menú Operaciones" and 'operaciones' in user.roles:
            mostrar_submenu_directo(bot, message.chat.id, 'operaciones', con_volver=True)

from telebot import TeleBot, types

def mostrar_menu_por_rol(bot: TeleBot, chat_id, user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    roles = user.roles
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
            
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        if text == "🏢 Menú Enel" and 'enel' in user.roles:
            markup.add(
                types.KeyboardButton("📌 Consultar Orden"),
                types.KeyboardButton("🏷️ Consultar Rótulo")
            )
            markup.add(types.KeyboardButton("⬅️ Volver al Menú Principal"))
            bot.send_message(message.chat.id, "📝 Menú Enel. Selecciona una opción:", reply_markup=markup)
            
        elif text == "⚙️ Menú Admin" and 'admin' in user.roles:
            markup.add(
                types.KeyboardButton("🛠️ Admin: Consultar Orden"),
                types.KeyboardButton("🛠️ Admin: Consultar Rótulo")
            )
            markup.add(types.KeyboardButton("⬅️ Volver al Menú Principal"))
            bot.send_message(message.chat.id, "⚙️ Menú Administrador. Selecciona una opción:", reply_markup=markup)
            
        elif text == "👷‍♂️ Menú Operaciones" and 'operaciones' in user.roles:
            markup.add(
                types.KeyboardButton("📤 Subir Archivo")
            )
            markup.add(types.KeyboardButton("⬅️ Volver al Menú Principal"))
            bot.send_message(message.chat.id, "📝 Menú Operaciones. Selecciona una opción:", reply_markup=markup)

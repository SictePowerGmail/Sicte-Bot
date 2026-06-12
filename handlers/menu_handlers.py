from telebot import TeleBot, types

def mostrar_menu_por_rol(bot: TeleBot, chat_id, user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    roles = user.roles
    has_menu = False
    
    if 'enel' in roles:
        markup.add(
            types.KeyboardButton("📌 Consultar Orden"),
            types.KeyboardButton("🏷️ Consultar Rótulo")
        )
        has_menu = True
        
    if 'admin' in roles:
        markup.add(
            types.KeyboardButton("🛠️ Admin: Consultar Orden"),
            types.KeyboardButton("🛠️ Admin: Consultar Rótulo")
        )
        has_menu = True
        
    if 'operaciones' in roles:
        markup.add(
            types.KeyboardButton("📤 Subir Archivo")
        )
        has_menu = True
        
    if has_menu:
        bot.send_message(chat_id, "Selecciona una opción del menú:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Tu rol no tiene un menú asignado.", reply_markup=types.ReplyKeyboardRemove())

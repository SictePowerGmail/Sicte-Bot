from telebot import TeleBot, types

def mostrar_menu_por_rol(bot: TeleBot, chat_id, user):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    rol = user.role.lower()
    
    if rol == 'enel':
        markup.add(
            types.KeyboardButton("📌 Consultar Orden"),
            types.KeyboardButton("🏷️ Consultar Rótulo")
        )
        bot.send_message(chat_id, "📝 Menú Enel. Selecciona una opción:", reply_markup=markup)
        
    elif rol == 'admin':
        markup.add(
            types.KeyboardButton("🛠️ Admin: Consultar Orden"),
            types.KeyboardButton("🛠️ Admin: Consultar Rótulo")
        )
        bot.send_message(chat_id, "⚙️ Menú Administrador. Selecciona una opción:", reply_markup=markup)
        
    elif rol == 'operaciones':
        markup.add(
            types.KeyboardButton("📤 Subir Archivo")
        )
        bot.send_message(chat_id, "📝 Menú Operaciones. Selecciona una opción:", reply_markup=markup)
        
    else:
        bot.send_message(chat_id, "Tu rol no tiene un menú asignado.", reply_markup=types.ReplyKeyboardRemove())

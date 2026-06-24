from telebot import TeleBot, types

def mostrar_submenu_directo(bot, chat_id, rol, con_volver=False, message_id=None):
    markup = types.InlineKeyboardMarkup(row_width=1)
    titulo = ""
    
    if rol == 'enel':
        markup.add(
            types.InlineKeyboardButton("📌 Consultar Orden", callback_data="op_enel_orden"),
            types.InlineKeyboardButton("🏷️ Consultar Rótulo", callback_data="op_enel_rotulo")
        )
        titulo = "📝 Menú Enel. Selecciona una opción:"
    elif rol == 'admin':
        markup.add(
            types.InlineKeyboardButton("⬇️ Descargar penalizaciones consolidado", callback_data="op_admin_penalizaciones")
        )
        titulo = "⚙️ Menú Administrador. Selecciona una opción:"
    elif rol == 'operaciones_centro':
        markup.add(
            types.InlineKeyboardButton("⬇️ Descargar preoperacional", callback_data="op_preoperacional_operaciones_centro")
        )
        titulo = "📝 Menú Operaciones Centro. Selecciona una opción:"
    elif rol == 'operaciones':
        markup.add(
            types.InlineKeyboardButton("📤 Subir Archivo", callback_data="op_operaciones_subir")
        )
        titulo = "📝 Menú Operaciones Norte. Selecciona una opción:"
    else:
        if message_id:
            bot.edit_message_text("Tu rol no tiene un menú asignado.", chat_id=chat_id, message_id=message_id)
        else:
            bot.send_message(chat_id, "Tu rol no tiene un menú asignado.")
        return

    if con_volver:
        markup.add(types.InlineKeyboardButton("⬅️ Volver al Menú Principal", callback_data="volver_menu_principal"))
        
    if message_id:
        bot.edit_message_text(titulo, chat_id=chat_id, message_id=message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, titulo, reply_markup=markup)

def mostrar_menu_por_rol(bot: TeleBot, chat_id, user, message_id=None):
    roles = user.roles
    
    # Si no tiene roles
    if not roles:
        if message_id:
            bot.edit_message_text("Tu rol no tiene un menú asignado.", chat_id=chat_id, message_id=message_id)
        else:
            bot.send_message(chat_id, "Tu rol no tiene un menú asignado.")
        return
        
    # Si solo tiene 1 rol, mostrar el submenú directamente sin botón de volver
    if len(roles) == 1:
        mostrar_submenu_directo(bot, chat_id, roles[0], con_volver=False, message_id=message_id)
        return
        
    # Si tiene más de 1 rol, mostrar el menú principal
    markup = types.InlineKeyboardMarkup(row_width=1)
    has_menu = False
    
    if 'enel' in roles:
        markup.add(types.InlineKeyboardButton("🏢 Menú Enel", callback_data="menu_enel"))
        has_menu = True
        
    if 'admin' in roles:
        markup.add(types.InlineKeyboardButton("⚙️ Menú Admin", callback_data="menu_admin"))
        has_menu = True

    if 'operaciones_centro' in roles:
        markup.add(types.InlineKeyboardButton("👷‍♂️ Menú Operaciones Centro", callback_data="menu_operaciones_centro"))
        has_menu = True
        
    if 'operaciones' in roles:
        markup.add(types.InlineKeyboardButton("👷‍♂️ Menú Operaciones Norte", callback_data="menu_operaciones"))
        has_menu = True
        
    if has_menu:
        titulo = "Selecciona el módulo al que deseas ingresar:"
        if message_id:
            bot.edit_message_text(titulo, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, titulo, reply_markup=markup)
    else:
        if message_id:
            bot.edit_message_text("Tu rol no tiene un menú asignado.", chat_id=chat_id, message_id=message_id)
        else:
            bot.send_message(chat_id, "Tu rol no tiene un menú asignado.")

def register_menu_handlers(bot: TeleBot):
    @bot.callback_query_handler(func=lambda call: call.data in ["menu_enel", "menu_admin", "menu_operaciones", "menu_operaciones_centro", "volver_menu_principal"])
    def handle_submenus(call):
        bot.answer_callback_query(call.id)
        from services.auth_service import auth_service_instance
        user = auth_service_instance.get_session(call.from_user.id)
        if not user:
            bot.send_message(call.message.chat.id, "Sesión expirada. Por favor usa /start")
            return

        data = call.data
        if data == "volver_menu_principal":
            mostrar_menu_por_rol(bot, call.message.chat.id, user, message_id=call.message.message_id)
            return
            
        if data == "menu_enel" and 'enel' in user.roles:
            mostrar_submenu_directo(bot, call.message.chat.id, 'enel', con_volver=True, message_id=call.message.message_id)
            
        elif data == "menu_admin" and 'admin' in user.roles:
            mostrar_submenu_directo(bot, call.message.chat.id, 'admin', con_volver=True, message_id=call.message.message_id)
            
        elif data == "menu_operaciones" and 'operaciones' in user.roles:
            mostrar_submenu_directo(bot, call.message.chat.id, 'operaciones', con_volver=True, message_id=call.message.message_id)

        elif data == "menu_operaciones_centro" and 'operaciones_centro' in user.roles:
            mostrar_submenu_directo(bot, call.message.chat.id, 'operaciones_centro', con_volver=True, message_id=call.message.message_id)

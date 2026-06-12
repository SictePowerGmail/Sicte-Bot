import time
from telebot import TeleBot
from states.bot_states import EnelState
from services.enel_service import enel_service_instance
from services.auth_service import auth_service_instance
from handlers.menu_handlers import mostrar_menu_por_rol

ultimo_uso = {}
ROLES_PERMITIDOS = ['enel', 'admin', 'operaciones']

def register_consulta_handlers(bot: TeleBot):
    
    def check_access(user_id, chat_id):
        user = auth_service_instance.get_session(user_id)
        if not user or not any(rol in user.roles for rol in ROLES_PERMITIDOS):
            bot.send_message(chat_id, "Acceso denegado o sesión expirada. Usa /start para iniciar sesión.")
            return None
            
        ahora = time.time()
        if user_id in ultimo_uso and (ahora - ultimo_uso[user_id]) < 2:
            bot.send_message(chat_id, "Espera 2 segundos entre consultas.")
            return None
            
        ultimo_uso[user_id] = ahora
        return user

    # ================== MANEJADORES DE BOTONES ==================
    @bot.callback_query_handler(func=lambda call: call.data in ["op_enel_orden", "op_admin_orden"])
    def ask_orden(call):
        bot.answer_callback_query(call.id)
        if not check_access(call.from_user.id, call.message.chat.id): return
        bot.send_message(call.message.chat.id, "Escribe el número de orden:")
        bot.set_state(call.from_user.id, EnelState.waiting_for_orden, call.message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data in ["op_enel_rotulo", "op_admin_rotulo"])
    def ask_rotulo(call):
        bot.answer_callback_query(call.id)
        if not check_access(call.from_user.id, call.message.chat.id): return
        bot.send_message(call.message.chat.id, "Escribe el número de rótulo:")
        bot.set_state(call.from_user.id, EnelState.waiting_for_rotulo, call.message.chat.id)

    # ================== MANEJADORES DE ESTADO (INPUT) ==================
    @bot.message_handler(state=EnelState.waiting_for_orden)
    def process_orden(message):
        user = check_access(message.from_user.id, message.chat.id)
        if not user: return
        
        orden = message.text.strip()
        bot.delete_state(message.from_user.id, message.chat.id)
        
        try:
            res, baremos, material = enel_service_instance.consultar_orden(orden)
            if res:
                ORDEN, ROTULO, ESTADO, FECHA_ESTADO, LOCALIDAD, TIPO_MOVIL = res
                respuesta = (
                    f"📌 <b>Orden:</b> {ORDEN}\n"
                    f"🏷️ <b>Rotulo:</b> {ROTULO}\n"
                    f"📄 <b>Estado:</b> {ESTADO}\n"
                    f"📅 <b>Fecha estado:</b> {FECHA_ESTADO}\n"
                    f"📍 <b>Localidad:</b> {LOCALIDAD}\n"
                    f"🚛 <b>Tipo móvil:</b> {TIPO_MOVIL}\n\n"
                )

                if baremos:
                    respuesta += "📋 <b>Baremos:</b>\n"
                    for fila in baremos:
                        item, cantidad, amap, Item_desc = fila
                        respuesta += f"\n• <b>Item:</b> {item} - {Item_desc}\n• <b>Cantidad:</b> {cantidad}\n• <b>Amap:</b> {amap}\n"
                else:
                    respuesta += "\n<b>Baremos:</b> Sin baremos\n"

                if material:
                    respuesta += "\n💡 <b>Material:</b>\n"
                    for fila in material:
                        item, cantidad, Item_desc = fila
                        respuesta += f"\n• <b>Item:</b> {item} - {Item_desc}\n• <b>Cantidad:</b> {cantidad}\n"
                else:
                    respuesta += "\n<b>Material:</b> Sin material\n"
            else:
                respuesta = "Favor validar con centro de control"
                
            bot.reply_to(message, respuesta, parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, str(e))
            
        mostrar_menu_por_rol(bot, message.chat.id, user)

    @bot.message_handler(state=EnelState.waiting_for_rotulo)
    def process_rotulo(message):
        user = check_access(message.from_user.id, message.chat.id)
        if not user: return
        
        rotulo = message.text.strip()
        bot.delete_state(message.from_user.id, message.chat.id)
        
        try:
            cantidad, detalles = enel_service_instance.consultar_rotulo(rotulo)
            if cantidad == 0:
                bot.reply_to(message, "Favor validar con centro de control")
                mostrar_menu_por_rol(bot, message.chat.id, user)
                return
                
            respuesta = f"Aquí tienes información del rotulo:\n\n🔎 <b>Rótulo:</b> {rotulo}\n🚐 <b>Atenciones registradas:</b> {cantidad}\n"
            
            for res, baremos, material in detalles:
                ORDEN, ROTULO, ESTADO, FECHA_ESTADO, LOCALIDAD, TIPO_MOVIL = res
                respuesta += (
                    f"\n\n📌 <b>Orden:</b> {ORDEN}\n"
                    f"📄 <b>Estado:</b> {ESTADO}\n"
                    f"📅 <b>Fecha:</b> {FECHA_ESTADO}\n"
                    f"📍 <b>Localidad:</b> {LOCALIDAD}\n"
                    f"🚛 <b>Tipo móvil:</b> {TIPO_MOVIL}\n\n"
                )
                
                if baremos:
                    respuesta += "📋 <b>Baremos:</b>\n"
                    for fila in baremos:
                        item, cant, amap, Item_desc = fila
                        respuesta += f"\n• <b>Item:</b> {item} - {Item_desc}\n• <b>Amap:</b> {amap}\n• <b>Cantidad:</b> {cant}\n"
                else:
                    respuesta += "📋 <b>Baremos:</b> Sin baremos\n"

                if material:
                    respuesta += "\n💡 <b>Material:</b>\n"
                    for fila in material:
                        item, cant, Item_desc = fila
                        respuesta += f"\n• <b>Item:</b> {item} - {Item_desc}\n• <b>Cantidad:</b>  {cant}\n"
                else:
                    respuesta += "\n💡 <b>Material:</b> Sin material\n"

            # Si el texto es muy largo, Telegram falla. Se envía la respuesta completa, 
            # pero en producción se podría dividir el texto si excede 4096 caracteres.
            bot.reply_to(message, respuesta, parse_mode='HTML')
        except Exception as e:
            bot.reply_to(message, str(e))
            
        mostrar_menu_por_rol(bot, message.chat.id, user)

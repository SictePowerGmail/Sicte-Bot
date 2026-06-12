import os
from telebot import TeleBot
from services.auth_service import auth_service_instance
from services.admin_service import admin_service_instance
from handlers.menu_handlers import mostrar_menu_por_rol

def register_admin_handlers(bot: TeleBot):
    """Registra los handlers para el módulo de administrador (Penalizaciones)."""

    @bot.callback_query_handler(func=lambda call: call.data == "op_admin_penalizaciones")
    def handle_descargar_penalizaciones(call):
        """Maneja el botón '⬇️ Descargar penalizaciones consolidado' del menú admin."""
        bot.answer_callback_query(call.id)
        
        user = auth_service_instance.get_session(call.from_user.id)
        if not user or 'admin' not in user.roles:
            bot.send_message(call.message.chat.id, "⛔ Acceso denegado. Esta función es solo para el rol Administrador.")
            return

        # Notificar al usuario que se está generando el reporte
        msg_procesando = bot.send_message(call.message.chat.id, "⏳ Consultando base de datos y generando archivo Excel, por favor espera...")
        
        file_path = None
        try:
            # Generar el Excel
            file_path = admin_service_instance.generar_excel_penalizaciones()
            
            if not file_path:
                bot.edit_message_text("⚠️ No se encontraron penalizaciones en la base de datos.", 
                                      chat_id=call.message.chat.id, 
                                      message_id=msg_procesando.message_id)
                return
                
            # Enviar el documento
            with open(file_path, 'rb') as document:
                bot.send_document(
                    call.message.chat.id,
                    document,
                    caption="✅ Aquí tienes el consolidado de penalizaciones."
                )
            
            # Eliminar mensaje de "procesando"
            bot.delete_message(call.message.chat.id, msg_procesando.message_id)
            
        except Exception as e:
            print(f"Error generando penalizaciones: {e}")
            bot.edit_message_text(f"❌ Ocurrió un error al generar el reporte:\n{str(e)}", 
                                  chat_id=call.message.chat.id, 
                                  message_id=msg_procesando.message_id)
        finally:
            # Limpiar archivo temporal si existe
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            
            # Volver a mostrar el menú por rol después de la acción
            mostrar_menu_por_rol(bot, call.message.chat.id, user)

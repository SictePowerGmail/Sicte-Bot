import os
from telebot import TeleBot
from services.auth_service import auth_service_instance
from services.operaciones_centro_service import preoperacional_centro_service_instance
from handlers.menu_handlers import mostrar_menu_por_rol

def register_admin_handlers(bot: TeleBot):
    """Registra los handlers para el módulo de Operaciones Centro (Preoperacional)."""

    @bot.callback_query_handler(func=lambda call: call.data == "op_preoperacional_operaciones_centro_penalizaciones")
    def handle_descargar_penalizaciones(call):
        """Maneja el botón '⬇️ Descargar Preoperacional Centro' del menú admin."""
        bot.answer_callback_query(call.id)
        
        user = auth_service_instance.get_session(call.from_user.id)
        if not user or 'admin' not in user.roles:
            bot.send_message(call.message.chat.id, "⛔ Acceso denegado. Esta función es solo para el rol Operaciones Centro.")
            return

        # Notificar al usuario que se está generando el reporte
        msg_procesando = bot.send_message(call.message.chat.id, "⏳ Consultando base de datos y generando archivo Excel, por favor espera...")
        
        file_path = None
        try:
            # Generar el Excel
            file_path = preoperacional_centro_service_instance.generar_excel_preoperacional_centro()
            
            if not file_path:
                bot.edit_message_text("⚠️ No se encontro Preoperacional en la base de datos.", 
                                      chat_id=call.message.chat.id, 
                                      message_id=msg_procesando.message_id)
                return
                
            # Enviar el documento con un timeout extendido (120 segundos) para archivos pesados
            with open(file_path, 'rb') as document:
                bot.send_document(
                    call.message.chat.id,
                    document,
                    caption="✅ Aquí tienes el Preoperacioanal.",
                    timeout=120
                )
            
            # Eliminar mensaje de "procesando"
            bot.delete_message(call.message.chat.id, msg_procesando.message_id)
            
        except Exception as e:
            print(f"Error generando preoperacional: {e}")
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

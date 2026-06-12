import os
import tempfile
from telebot import TeleBot, types
from states.bot_states import OperacionesState
from services.auth_service import auth_service_instance
from services.operaciones_service import operaciones_service_instance
from handlers.menu_handlers import mostrar_menu_por_rol

# Almacenamiento temporal: { user_id: tipo_archivo }
operaciones_temp_data = {}

# Extensiones de archivo permitidas
EXTENSIONES_PERMITIDAS = ('.xlsx', '.xls', '.csv')


def register_operaciones_handlers(bot: TeleBot):
    """Registra los handlers para el módulo de operaciones (subir archivos Excel)."""

    # Asegurar que la tabla existe al registrar los handlers
    try:
        operaciones_service_instance.inicializar_bd()
    except Exception as e:
        print(f"Advertencia: No se pudo verificar la tabla de operaciones: {e}")

    # ================== BOTÓN "Subir Archivo" ==================
    @bot.callback_query_handler(func=lambda call: call.data == "op_operaciones_subir")
    def handle_subir_archivo(call):
        """Maneja el botón '📤 Subir Archivo' del menú de operaciones."""
        bot.answer_callback_query(call.id)
        user = auth_service_instance.get_session(call.from_user.id)
        if not user or 'operaciones' not in user.roles:
            bot.send_message(call.message.chat.id, "⛔ Acceso denegado. Esta función es solo para el rol Operaciones.")
            return

        # Mostrar teclado inline con opciones de tipo de archivo
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🏠 Residencial", callback_data="op_tipo_Residencial"),
            types.InlineKeyboardButton("🏢 Pymes", callback_data="op_tipo_Pymes"),
            types.InlineKeyboardButton("👷‍♂️ Recurso", callback_data="op_tipo_Recurso")
        )
        bot.send_message(
            call.message.chat.id,
            "📂 <b>Selecciona el tipo de archivo que deseas subir:</b>",
            reply_markup=markup,
            parse_mode='HTML'
        )

    # ================== CALLBACK: Selección de tipo ==================
    @bot.callback_query_handler(func=lambda call: call.data.startswith("op_tipo_"))
    def handle_tipo_seleccion(call):
        """Maneja la selección del tipo de archivo (Residencial/Pymes)."""
        user = auth_service_instance.get_session(call.from_user.id)
        if not user or 'operaciones' not in user.roles:
            bot.answer_callback_query(call.id, "⛔ Acceso denegado.")
            return

        tipo_archivo = call.data.replace("op_tipo_", "")  # "Residencial" o "Pymes"
        operaciones_temp_data[call.from_user.id] = tipo_archivo

        # Editar el mensaje para confirmar la selección
        bot.edit_message_text(
            f"✅ Tipo seleccionado: <b>{tipo_archivo}</b>\n\n"
            f"📎 Ahora envía el archivo Excel (.xlsx, .xls) o CSV (.csv):",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML'
        )

        # Establecer estado de espera de archivo
        bot.set_state(call.from_user.id, OperacionesState.waiting_for_archivo, call.message.chat.id)
        bot.answer_callback_query(call.id)

    # ================== HANDLER: Recibir documento ==================
    @bot.message_handler(state=OperacionesState.waiting_for_archivo, content_types=['document'])
    def handle_archivo_recibido(message):
        """Procesa el archivo Excel/CSV enviado por el usuario."""
        user = auth_service_instance.get_session(message.from_user.id)
        if not user or 'operaciones' not in user.roles:
            bot.reply_to(message, "⛔ Acceso denegado o sesión expirada.")
            bot.delete_state(message.from_user.id, message.chat.id)
            return

        tipo_archivo = operaciones_temp_data.get(message.from_user.id)
        if not tipo_archivo:
            bot.reply_to(message, "❌ Error: No se encontró el tipo de archivo. Intenta de nuevo con '📤 Subir Archivo'.")
            bot.delete_state(message.from_user.id, message.chat.id)
            mostrar_menu_por_rol(bot, message.chat.id, user)
            return

        # Validar extensión del archivo
        file_name = message.document.file_name
        extension = os.path.splitext(file_name)[1].lower()
        if extension not in EXTENSIONES_PERMITIDAS:
            bot.reply_to(
                message,
                f"❌ Formato no soportado: <b>{extension}</b>\n"
                f"Envía un archivo con extensión: .xlsx, .xls o .csv",
                parse_mode='HTML'
            )
            return  # Mantener el estado para que pueda reintentar

        # Mensaje de procesamiento
        msg_procesando = bot.reply_to(message, "⏳ Procesando archivo, por favor espera...")

        file_path = None
        try:
            # Descargar el archivo
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Guardar en archivo temporal
            suffix = extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(downloaded_file)
                file_path = tmp_file.name

            # Procesar según el tipo de archivo
            if tipo_archivo == "Recurso":
                df, insertados = operaciones_service_instance.procesar_archivo_recurso(file_path)

                if df.empty:
                    bot.edit_message_text(
                        "⚠️ El archivo de Recurso está vacío o no contiene datos válidos.",
                        chat_id=message.chat.id,
                        message_id=msg_procesando.message_id
                    )
                    bot.delete_state(message.from_user.id, message.chat.id)
                    _limpiar_temp(message.from_user.id)
                    mostrar_menu_por_rol(bot, message.chat.id, user)
                    return

                # Mensaje de éxito
                resumen = (
                    f"✅ <b>Archivo de Recurso procesado exitosamente</b>\n\n"
                    f" <b>Archivo:</b> {file_name}\n"
                    f" <b>Tipo:</b> {tipo_archivo}\n"
                    f" <b>Registros insertados (Tabla reemplazada):</b> {insertados}\n"
                )

                bot.edit_message_text(
                    resumen,
                    chat_id=message.chat.id,
                    message_id=msg_procesando.message_id,
                    parse_mode='HTML'
                )

            else:
                # Procesar el archivo con pandas
                df, nombre_archivo, eliminados, insertados = operaciones_service_instance.procesar_archivo_excel(file_path, tipo_archivo)

                if df.empty:
                    bot.edit_message_text(
                        "⚠️ El archivo está vacío o no contiene datos válidos.",
                        chat_id=message.chat.id,
                        message_id=msg_procesando.message_id
                    )
                    bot.delete_state(message.from_user.id, message.chat.id)
                    _limpiar_temp(message.from_user.id)
                    mostrar_menu_por_rol(bot, message.chat.id, user)
                    return

                # Mensaje de éxito
                resumen = (
                    f"✅ <b>Archivo procesado exitosamente</b>\n\n"
                    f" <b>Archivo:</b> {file_name}\n"
                    f" <b>Tipo:</b> {tipo_archivo}\n"
                    f" <b>Etiqueta:</b> {nombre_archivo}\n"
                )
                if eliminados > 0:
                    resumen += f" <b>Registros previos eliminados:</b> {eliminados}\n"
                resumen += f" <b>Registros insertados:</b> {insertados}\n"

                bot.edit_message_text(
                    resumen,
                    chat_id=message.chat.id,
                    message_id=msg_procesando.message_id,
                    parse_mode='HTML'
                )

        except ValueError as e:
            bot.edit_message_text(
                f"❌ <b>Error de validación:</b>\n{str(e)}",
                chat_id=message.chat.id,
                message_id=msg_procesando.message_id,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Error procesando archivo de operaciones: {e}")
            bot.edit_message_text(
                f"❌ Error al procesar el archivo:\n{str(e)}",
                chat_id=message.chat.id,
                message_id=msg_procesando.message_id
            )
        finally:
            # Limpiar archivo temporal
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass

            # Limpiar estado y datos temporales
            bot.delete_state(message.from_user.id, message.chat.id)
            _limpiar_temp(message.from_user.id)
            mostrar_menu_por_rol(bot, message.chat.id, user)

    # ================== HANDLER: Texto en estado de espera de archivo ==================
    @bot.message_handler(state=OperacionesState.waiting_for_archivo)
    def handle_texto_en_espera_archivo(message):
        """Si el usuario envía texto en vez de un archivo, recordarle que debe enviar un documento."""
        bot.reply_to(
            message,
            "📎 Por favor envía un <b>archivo</b> (documento), no texto.\n"
            "Formatos aceptados: .xlsx, .xls, .csv\n\n"
            "Si deseas cancelar, usa /start para volver al menú.",
            parse_mode='HTML'
        )


def _limpiar_temp(user_id):
    """Limpia los datos temporales del usuario."""
    if user_id in operaciones_temp_data:
        del operaciones_temp_data[user_id]

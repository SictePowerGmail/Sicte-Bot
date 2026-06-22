import os
import sys
import telebot
from telebot.custom_filters import StateFilter
from dotenv import load_dotenv

# Importar handlers
from handlers.auth_handlers import register_auth_handlers
from handlers.operaciones_handlers import register_operaciones_handlers
from handlers.consulta_handlers import register_consulta_handlers
from handlers.menu_handlers import register_menu_handlers
from handlers.admin_handlers import register_admin_handlers
from handlers.operaciones_centro_handlers import register_operaciones_centro_handlers

load_dotenv()

if os.getenv("BOT_PAUSADO") == "true":
    print("Bot pausado")
    sys.exit()

TOKEN = os.getenv("telegram_sicte_bot")
if not TOKEN:
    print("ERROR: Token de Telegram no configurado en .env")
    sys.exit()

# Configurar bot con almacenamiento de estados en memoria
bot = telebot.TeleBot(TOKEN, state_storage=telebot.storage.StateMemoryStorage())

# COMANDOS DEL BOT
bot.set_my_commands([
    telebot.types.BotCommand("start", "Iniciar bot / Iniciar sesión"),
    telebot.types.BotCommand("logout", "Cerrar sesión")
])

# Registrar filtros de estado (NECESARIO para usar AuthState y EnelState)
bot.add_custom_filter(StateFilter(bot))

# Registrar handlers
register_auth_handlers(bot)
register_operaciones_handlers(bot)
register_operaciones_centro_handlers(bot)
register_consulta_handlers(bot)
register_menu_handlers(bot)
register_admin_handlers(bot)

# Manejador genérico para texto no reconocido o botones no mapeados
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    from services.auth_service import get_session
    from handlers.menu_handlers import mostrar_menu_por_rol
    
    user = get_session(message.from_user.id)
    if user:
        mostrar_menu_por_rol(bot, message.chat.id, user)
    else:
        bot.reply_to(message, "Por favor, inicia sesión con /start")

if __name__ == "__main__":
    print("Bot iniciado con Arquitectura POO y Control de Roles...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Error polling: {e}")
            import time
            time.sleep(5)

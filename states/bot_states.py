from telebot.handler_backends import State, StatesGroup

class AuthState(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

class EnelState(StatesGroup):
    waiting_for_orden = State()
    waiting_for_rotulo = State()

class OperacionesState(StatesGroup):
    waiting_for_tipo_archivo = State()
    waiting_for_archivo = State()

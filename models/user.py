class User:
    def __init__(self, telegram_id, roles, cedula=None):
        self.telegram_id = telegram_id
        self.roles = roles
        self.cedula = cedula

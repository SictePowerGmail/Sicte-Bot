class User:
    def __init__(self, telegram_id, role, username=None):
        self.telegram_id = telegram_id
        self.role = role
        self.username = username

from models.user import User


class Manager(User):
    def __init__(self, name, username, password):
        super().__init__(name, username, password)

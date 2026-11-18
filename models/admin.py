from models.manager import Manager


class Admin(Manager):
    def __init__(self, name, username, password):
        super().__init__(name, username, password)

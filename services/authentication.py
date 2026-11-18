from models.customer import Customer
from models.admin import Admin


class AuthenticationService:
    def __init__(self):
        # Accounts are stored in memory for this educational project.
        self.accounts = {}
        self.admin_accounts = {
            "admin": Admin("System Administrator", "admin", "admin123")
        }

    def register(self, name, username, password):
        if username in self.accounts or username in self.admin_accounts:
            return False
        self.accounts[username] = Customer(name, username, password)
        return True

    def login(self, username, password):
        customer = self.accounts.get(username)
        if customer and customer.password == password:
            return customer
        return None

    def admin_login(self, username, password):
        admin = self.admin_accounts.get(username)
        if admin and admin.password == password:
            return admin
        return None

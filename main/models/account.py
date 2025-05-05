import uuid

class Account:
    def __init__(self, name, type_, balance=0.0):
        self.id = str(uuid.uuid4())
        self.name = name
        self.type = type_
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        self.balance -= amount


class AccountGroup:
    def __init__(self, group_name):
        self.id = str(uuid.uuid4())
        self.group_name = group_name  # e.g., "Chase Bank"
        self.accounts = []

    def add_account(self, account: Account):
        self.accounts.append(account)

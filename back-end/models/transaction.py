from datetime import datetime
import uuid

class Transaction:
    def __init__(self, amount, category, type_, note="", date=None):
        self.id = str(uuid.uuid4())
        self.amount = amount
        self.category = category
        self.type = type_  # 'income' or 'expense'
        self.date = date or datetime.now()
        self.note = note

    def __str__(self):
        return f"{self.date.date()} | {self.type.upper()} | {self.category} | ${self.amount:.2f} | {self.note}"

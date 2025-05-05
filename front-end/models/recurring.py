from datetime import datetime

class RecurringTransaction:
    def __init__(self, amount, category, type_, note, frequency, start_date):
        self.amount = amount
        self.category = category
        self.type = type_  # 'income' or 'expense'
        self.note = note
        self.frequency = frequency  # e.g. 'monthly'
        self.start_date = start_date
        self.last_created = start_date

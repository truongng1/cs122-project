from collections import defaultdict
from models.account import AccountGroup
from models.transaction import Transaction
from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID as string
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, password):
        import uuid
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = password
        self.transactions = []
        self.accounts = []
        self.account_groups = []
        self.recurring_transactions = []

    def add_group(self, group_name):
        group = AccountGroup(group_name)
        self.account_groups.append(group)
        return group

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def get_summary(self):
        summary = defaultdict(float)
        for t in self.transactions:
            summary[t.category] += t.amount if t.type == "income" else -t.amount
        return summary

    def process_recurring(self):
        today = datetime.now().date()
        for rt in self.recurring_transactions:
            if rt.frequency == "monthly":
                due_date = rt.last_created.replace(day=1).replace(month=rt.last_created.month + 1)
                if today >= due_date:
                    self.transactions.append(Transaction(rt.amount, rt.category, rt.type, rt.note, datetime.now()))
                    rt.last_created = today


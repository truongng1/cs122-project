from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    transactions = db.relationship('Transaction', backref='user', lazy=True)
    account_groups = db.relationship('AccountGroup', backref='user', lazy=True)
    recurring_transactions = db.relationship('RecurringTransaction', backref='user', lazy=True)

    def __init__(self, name, email, password):
        import uuid
        self.id = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = password

    def get_summary(self):
        from collections import defaultdict
        summary = defaultdict(float)
        for t in self.transactions:
            if t.type == "income":
                summary[t.category] += t.amount
            else:
                summary[t.category] -= t.amount
        return summary

    def process_recurring(self):
        for rt in self.recurring_transactions:
            if rt.frequency == "monthly":
                from models.transaction import Transaction
                if not rt.last_created or datetime.now().date() >= rt.last_created.replace(day=1).replace(month=rt.last_created.month + 1):
                    new_txn = Transaction(
                        amount=rt.amount,
                        category=rt.category,
                        type=rt.type,
                        note=rt.note,
                        date=datetime.now(),
                        user_id=self.id
                    )
                    db.session.add(new_txn)
                    rt.last_created = datetime.now().date()

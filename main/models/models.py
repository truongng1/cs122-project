from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from collections import defaultdict

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    transactions = db.relationship('Transaction', backref='user', lazy=True)
    account_groups = db.relationship('AccountGroup', backref='user', lazy=True)
    accounts = db.relationship('Account', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_summary(self):
        summary = defaultdict(float)
        for t in self.transactions:
            if t.type == "income":
                summary[t.category] += t.amount
            else:
                summary[t.category] -= t.amount
        return summary


class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    type = db.Column(db.String(10))  # 'income', 'expense', or 'transfer'
    note = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    from_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    to_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    account = db.relationship('Account', foreign_keys=[account_id], back_populates='transactions')
    from_account = db.relationship('Account', foreign_keys=[from_account_id], back_populates='transactions_from')
    to_account = db.relationship('Account', foreign_keys=[to_account_id], back_populates='transactions_to')


class AccountGroup(db.Model):
    __tablename__ = 'account_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    accounts = db.relationship('Account', backref='group', lazy=True)


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # 'checking', 'savings', etc.
    balance = db.Column(db.Float, default=0)
    description = db.Column(db.String(255))

    group_id = db.Column(db.Integer, db.ForeignKey('account_group.id'))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))

    transactions = db.relationship('Transaction', foreign_keys='Transaction.account_id', back_populates='account', lazy=True)
    transactions_from = db.relationship('Transaction', foreign_keys='Transaction.from_account_id', back_populates='from_account', lazy=True)
    transactions_to = db.relationship('Transaction', foreign_keys='Transaction.to_account_id', back_populates='to_account', lazy=True)

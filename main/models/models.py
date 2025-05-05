from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    transactions = db.relationship('Transaction', backref='user', lazy=True)
    account_groups = db.relationship('AccountGroup', backref='user', lazy=True)
    recurring_transactions = db.relationship('RecurringTransaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    type = db.Column(db.String(10))  # 'income' or 'expense'
    note = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

class AccountGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    accounts = db.relationship('Account', backref='group', lazy=True)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))  # 'checking', 'savings', etc.
    balance = db.Column(db.Float, default=0)
    group_id = db.Column(db.Integer, db.ForeignKey('account_group.id'))
    transactions = db.relationship('Transaction', backref='account', lazy=True)

class RecurringTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    type = db.Column(db.String(10))  # 'income' or 'expense'
    note = db.Column(db.String(200))
    frequency = db.Column(db.String(20))  # 'monthly'
    start_date = db.Column(db.Date)
    last_created = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

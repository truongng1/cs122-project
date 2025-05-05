from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# import everything from models.py
from .models import User, Transaction, AccountGroup, Account, RecurringTransaction

__all__ = ['db', 'User', 'Transaction', 'AccountGroup', 'Account', 'RecurringTransaction']

from flask import Blueprint, request, redirect, session, url_for
from models.transaction import Transaction
from utils.helpers import save_user_to_file
from models.user import User  # or load from DB/file

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/add_transaction', methods=['POST'])
def add_transaction():
    user_id = session.get('user_id')
    user = User.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    transaction = Transaction(
        float(request.form['amount']),
        request.form['category'],
        request.form['type'],
        request.form.get('note', '')
    )
    user.add_transaction(transaction)
    save_user_to_file(user)
    return redirect(url_for('dashboard.dashboard'))

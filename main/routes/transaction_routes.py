import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Blueprint, request, redirect, session, url_for
from models import db, User, Transaction

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/add_transaction_form')
def add_transaction_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('add_transaction.html')


@transaction_bp.route('/add_transaction', methods=['POST'])
def add_transaction():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))

    # Create transaction
    transaction = Transaction(
        amount=float(request.form['amount']),
        category=request.form['category'],
        type=request.form['type'],
        note=request.form.get('note', ''),
        user_id=user.id
    )

    db.session.add(transaction)
    db.session.commit()

    return redirect(url_for('dashboard.dashboard'))

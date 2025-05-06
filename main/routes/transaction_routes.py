import sys
import os
from flask import Blueprint, request, redirect, session, url_for, render_template
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from flask import Blueprint, request, redirect, session, url_for
from models.models import db, User, Transaction, Account, AccountGroup



transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/add_transaction_form')
def add_transaction_form():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user:
        return redirect(url_for('login'))

    accounts = user.account_groups[0].accounts if user.account_groups else []

    expense_categories = [
        "Food", "Social Life", "Self-development", "Transportation", "Culture",
        "Household", "Apparel", "Beauty", "Health", "Education", "Gift", "Other"
    ]

    income_categories = ["Salary", "Allowance", "Bonus", "Interest earned", "Other"]

    return render_template("add_transaction.html",
                           user=user,
                           today=datetime.now().strftime("%Y-%m-%d"),
                           accounts=accounts,
                           income_categories=income_categories,
                           expense_categories=expense_categories)


@transaction_bp.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != user_id:
        return "Unauthorized", 403

    db.session.delete(transaction)
    db.session.commit()

    return redirect(url_for('dashboard', user_id=user_id))

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

    return redirect(url_for('dashboard', user_id=user.id))

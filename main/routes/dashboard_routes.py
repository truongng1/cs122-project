from flask import Blueprint, render_template, session, redirect, url_for, request, make_response
from models.models import db, User, Transaction, Account, AccountGroup
from collections import defaultdict
from datetime import datetime
import csv
import json
from io import StringIO

dashboard_bp = Blueprint('dash', __name__)


@dashboard_bp.route('/transactions', endpoint='dashboard')
def transactions():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    daily_transactions = defaultdict(list)
    monthly_summary = defaultdict(lambda: {"income": 0, "expense": 0})

    for t in user.transactions:
        date_str = t.date.strftime('%Y-%m-%d')
        daily_transactions[date_str].append(t)

        # Monthly summary
        month_key = t.date.strftime('%Y-%m')
        if t.type == 'income':
            monthly_summary[month_key]["income"] += t.amount
        elif t.type == 'expense':
            monthly_summary[month_key]["expense"] += t.amount

    return render_template(
        "add_transaction.html",
        user=user,
        daily_transactions=dict(daily_transactions),
        monthly_summary=dict(monthly_summary)
    )


@dashboard_bp.route('/stats')
def stats():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    month_str = request.args.get("month")
    selected_month = datetime.strptime(month_str, "%Y-%m") if month_str else datetime.now()

    category_summary = defaultdict(float)
    monthly_summary = defaultdict(lambda: {"income": 0, "expense": 0})

    for t in user.transactions:
        if t.date.year == selected_month.year and t.date.month == selected_month.month and t.type == "expense":
            category_summary[t.category] += t.amount

        if t.date.year == selected_month.year:
            month = t.date.strftime("%b")
            if t.type == "income":
                monthly_summary[month]["income"] += t.amount
            else:
                monthly_summary[month]["expense"] += t.amount

    return render_template(
        "stats.html",
        selected_month=selected_month.strftime("%Y-%m"),
        category_summary=dict(category_summary),
        monthly_summary=dict(monthly_summary)
    )


@dashboard_bp.route('/accounts')
def accounts():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    print(f"User: {user.name}")
    for group in user.account_groups:
        print(f"Group: {group.name} (ID: {group.id})")
        for account in group.accounts:
            print(f" - Account: {account.name}, Balance: {account.balance}")

    return render_template("accounts.html", user=user)

@dashboard_bp.route('/delete_account/<int:account_id>', methods=['POST'])
def delete_account_view(account_id):
    account = Account.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('dash.accounts'))

@dashboard_bp.route('/edit_account/<int:account_id>', methods=['POST'])
def edit_account_view(account_id):
    account = Account.query.get_or_404(account_id)
    account.name = request.form['account_name']
    account.balance = float(request.form['balance'])
    account.group_id = int(request.form['group'])  # Ensure this column exists in your Account model
    db.session.commit()
    return redirect(url_for('dash.accounts'))

@dashboard_bp.route('/add_account', methods=['POST'])
def add_account():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    group_id = request.form.get('group_id')
    custom_group_name = request.form.get('custom_group')
    account_name = request.form.get('account_name')
    account_type = request.form.get('account_type', 'checking')
    balance = float(request.form.get('balance', 0))
    description = request.form.get('description', '')

    # Create or find account group
    if group_id == "custom" and custom_group_name:
        group = AccountGroup(name=custom_group_name, user_id=user.id)
        db.session.add(group)
        db.session.commit()
    else:
        group = AccountGroup.query.filter_by(id=group_id, user_id=user.id).first()

    # Add account
    account = Account(
        name=account_name,
        type=account_type,
        balance=balance,
        group_id=group.id,
        user_id=user.id,
        description=description
    )
    db.session.add(account)
    db.session.commit()

    return redirect(url_for('dash.accounts'))
@dashboard_bp.route('/add_account_form')
def add_account_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    return render_template('add_account.html', user=user)

@dashboard_bp.route('/edit_account/<int:account_id>', methods=['GET', 'POST'])
def edit_account(account_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    account = Account.query.get_or_404(account_id)
    if not account.group or account.group.user_id != user_id:
        return "Unauthorized", 403

    if request.method == 'POST':
        account.name = request.form['account_name']
        account.balance = float(request.form['balance'])
        account.description = request.form['description']
        db.session.commit()
        return redirect(url_for('dashboard.accounts'))

    user = User.query.get(user_id)
    return render_template("edit_account.html", account=account, user=user)



@dashboard_bp.route('/delete_account/<int:account_id>', methods=['POST'])
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    user_id = session.get('user_id')
    if account.group.user_id != user_id:
        return "Unauthorized", 403

    db.session.delete(account)
    db.session.commit()
    return redirect(url_for('dashboard.accounts'))

@dashboard_bp.route('/add_group', methods=['POST'])
def add_group():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    group_name = request.form['group_name']
    group = AccountGroup(name=group_name, user_id=user.id)
    db.session.add(group)
    db.session.commit()

    return redirect(url_for('dashboard.accounts'))


@dashboard_bp.route('/add_recurring', methods=['POST'])
def add_recurring():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))

    recurring = RecurringTransaction(
        amount=float(request.form['amount']),
        category=request.form['category'],
        type=request.form['type'],
        note=request.form['note'],
        frequency=request.form['frequency'],
        start_date=datetime.strptime(request.form['start_date'], "%Y-%m-%d"),
        last_created=datetime.now().date(),
        user_id=user.id
    )
    db.session.add(recurring)
    db.session.commit()

    return redirect(url_for('dashboard.accounts'))


@dashboard_bp.route('/export_summary')
def export_summary():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    summary = defaultdict(lambda: {"income": 0, "expense": 0})
    for t in user.transactions:
        key = t.date.strftime('%Y-%m')
        if t.type == "income":
            summary[key]["income"] += t.amount
        else:
            summary[key]["expense"] += t.amount

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Month', 'Income', 'Expense'])

    for month, values in summary.items():
        writer.writerow([month, values["income"], values["expense"]])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=budget_summary.csv"
    response.headers["Content-type"] = "text/csv"
    return response


@dashboard_bp.route('/backup_data')
def backup_data():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    data = {
        "name": user.name,
        "email": user.email,
        "transactions": [
            {
                "amount": t.amount,
                "type": t.type,
                "category": t.category,
                "note": t.note,
                "date": t.date.strftime("%Y-%m-%d")
            }
            for t in user.transactions
        ]
    }

    output = StringIO()
    json.dump(data, output)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=backup.json"
    response.headers["Content-type"] = "application/json"
    return response


@dashboard_bp.route('/trend_data')
def trend_data():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    trends = defaultdict(lambda: {"income": 0, "expense": 0})
    for t in user.transactions:
        year = t.date.year
        if t.type == "income":
            trends[year]["income"] += t.amount
        else:
            trends[year]["expense"] += t.amount

    return render_template("trend.html", trends=dict(trends))

from flask import Blueprint, render_template, session, redirect, url_for, request
from models.user import User
from collections import defaultdict
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/transactions')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

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
        "transactions.html",
        user=user,
        daily_transactions=dict(daily_transactions),
        monthly_summary=dict(monthly_summary)
    )

@dashboard_bp.route('/stats')
def stats():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    month_str = request.args.get("month")
    if month_str:
        selected_month = datetime.strptime(month_str, "%Y-%m")
    else:
        selected_month = datetime.now()

    # Pie chart summary
    category_summary = defaultdict(float)
    for t in user.transactions:
        if t.date.year == selected_month.year and t.date.month == selected_month.month:
            if t.type == "expense":
                category_summary[t.category] += t.amount

    # Bar chart summary for the year
    monthly_summary = defaultdict(lambda: {"income": 0, "expense": 0})
    for t in user.transactions:
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
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    return render_template("accounts.html", user=user)

@dashboard_bp.route('/add_group', methods=['POST'])
def add_group():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404
    group_name = request.form['group_name']
    user.add_group(group_name)
    return redirect(url_for('dashboard.accounts'))

@dashboard_bp.route('/add_account/<group_id>', methods=['POST'])
def add_account(group_id):
    from models.user_manager import users
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = users[session['user_id']]
    account_name = request.form['account_name']
    account_type = request.form['account_type']
    balance = float(request.form.get('balance', 0))

    for group in user.account_groups:
        if group.id == group_id:
            from models.account import Account
            group.add_account(Account(account_name, account_type, balance))
            break

    return redirect(url_for('dashboard.accounts'))

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    from models.user_manager import users
    user_id = session.get('user_id')
    if not user_id or user_id not in users:
        return redirect(url_for('auth.login'))

    user = users[user_id]

    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = request.form['password']  # (plaintext now; hash it later)

    return render_template("profile.html", user=user)

@dashboard_bp.route('/add_recurring', methods=['POST'])
def add_recurring():
    user = users[session['user_id']]
    user.recurring_transactions.append(
        RecurringTransaction(
            float(request.form['amount']),
            request.form['category'],
            request.form['type'],
            request.form['note'],
            request.form['frequency'],
            datetime.strptime(request.form['start_date'], "%Y-%m-%d")
        )
    )
    return redirect(url_for('dashboard.more'))

@dashboard_bp.route('/export_summary')
def export_summary():
    from models.user_manager import users
    import csv
    from io import StringIO

    user = users[session['user_id']]
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

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=budget_summary.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@dashboard_bp.route('/backup_data')
def backup_data():
    import json
    from io import StringIO

    user = users[session['user_id']]
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
    output.seek(0)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=backup.json"
    response.headers["Content-type"] = "application/json"
    return response

@dashboard_bp.route('/trend_data')
def trend_data():
    from models.user_manager import users
    from collections import defaultdict

    user = users[session['user_id']]
    trends = defaultdict(lambda: {"income": 0, "expense": 0})

    for t in user.transactions:
        year = t.date.year
        if t.type == "income":
            trends[year]["income"] += t.amount
        else:
            trends[year]["expense"] += t.amount

    return render_template("trend.html", trends=dict(trends))

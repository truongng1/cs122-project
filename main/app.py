from flask import Flask, request, redirect, url_for, render_template, session, flash, g, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import io
import os

from routes.transaction_routes import transaction_bp
from routes.dashboard_routes import dashboard_bp
from models.models import db, User, Transaction, Account, AccountGroup

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
app.permanent_session_lifetime = timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///walleto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="alice@example.com").first():
        user = User(name="Alice", email="alice@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    g.user = User.query.get(user_id) if user_id else None

@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard', user_id=session['user_id']))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.permanent = True
            session['user_id'] = user.id
            return redirect(url_for('dashboard', user_id=user.id))
        else:
            error = "Invalid email or password"

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if len(password) < 6:
            error = "Password must meet all complexity requirements."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif User.query.filter_by(email=email).first():
            error = "Email already exists."
        else:
            new_user = User(name=f"{first_name} {last_name}", email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/user/<string:user_id>', endpoint='dashboard')
def dashboard(user_id):
    if session.get('user_id') != user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    daily_transactions = defaultdict(list)
    monthly_summary = defaultdict(lambda: {'income': 0, 'expense': 0})
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%B")

    for t in user.transactions:
        if t.date.year == current_year:
            month = t.date.strftime("%B")
            if t.type == 'income':
                monthly_summary[month]['income'] += t.amount
            elif t.type == 'expense':
                monthly_summary[month]['expense'] += t.amount

            if month == current_month:
                day = t.date.strftime("%Y-%m-%d")
                daily_transactions[day].append(t)

    return render_template("dashboard.html", user=user,
                           current_month=current_month,
                           current_year=current_year,
                           daily_transactions=daily_transactions,
                           monthly_summary=monthly_summary)

@app.route('/stats')
def stats():
    user = User.query.get(session.get('user_id'))
    year = request.args.get('year', default=datetime.now().year, type=int)
    monthly_summary = defaultdict(lambda: {'income': 0, 'expense': 0})

    for t in user.transactions:
        if t.date.year == year:
            month = t.date.strftime("%B")
            if t.type == 'income':
                monthly_summary[month]['income'] += t.amount
            elif t.type == 'expense':
                monthly_summary[month]['expense'] += t.amount

    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    income_data = [monthly_summary[m]['income'] for m in months]
    expense_data = [monthly_summary[m]['expense'] for m in months]

    return render_template('stats.html', user=user, labels=months,
                           income_data=income_data,
                           expense_data=expense_data,
                           current_year=year)

@app.route('/more', endpoint='more')
def more_page():
    user = User.query.get(session.get('user_id'))
    if not user:
        return redirect(url_for('login'))
    return render_template('more.html', user=user, current_year=datetime.now().year)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not g.user:
        flash("You must be logged in to change your password.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not g.user.check_password(old_password):
            flash("Old password is incorrect")
        elif new_password != confirm_password:
            flash("New passwords do not match")
        elif len(new_password) < 6:
            flash("Password must be at least 6 characters")
        else:
            g.user.set_password(new_password)
            db.session.commit()
            flash("Password updated successfully")
            return redirect(url_for('dashboard', user_id=g.user.id))

    return render_template("change_password.html")

@app.route('/export_transactions', methods=['GET', 'POST'])
def export_transactions():
    user = User.query.get(session.get('user_id'))
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        export_format = request.form.get('format')

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        transactions = Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.date >= start,
            Transaction.date <= end
        ).all()

        data = []
        for t in transactions:
            row = {
                'Date': t.date.strftime('%Y-%m-%d'),
                'Type': t.type,
                'Amount': t.amount,
                'Category': t.category,
                'Note': t.note,
                'Account': t.account.name if t.account else '',
                'Account Group': t.account.group.name if t.account and t.account.group else '',
                'From Account': t.from_account.name if t.from_account else '',
                'From Account Group': t.from_account.group.name if t.from_account and t.from_account.group else '',
                'To Account': t.to_account.name if t.to_account else '',
                'To Account Group': t.to_account.group.name if t.to_account and t.to_account.group else ''
            }
            data.append(row)

        df = pd.DataFrame(data)

        if export_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(io.BytesIO(output.getvalue().encode()),
                             download_name="transactions.csv",
                             as_attachment=True,
                             mimetype="text/csv")
        else:
            output = io.BytesIO()
            df.to_excel(output, index=False, sheet_name='Transactions')
            output.seek(0)
            return send_file(output,
                             download_name="transactions.xlsx",
                             as_attachment=True,
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    return render_template('export_transactions.html')




@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/transactions/add', methods=['GET'])
def show_add_transaction():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)

    accounts = Account.query.filter_by(user_id=user.id).all()
    income_categories = ["Salary", "Allowance", "Bonus", "Interest earned", "Other"]
    expense_categories = ["Food", "Transportation", "Rent", "Shopping", "Utilities", "Other"]

    today = datetime.today().strftime('%Y-%m-%d')

    return render_template("add_transaction.html",
                           accounts=accounts,
                           income_categories=income_categories,
                           expense_categories=expense_categories,
                           today=today)
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    t_type = request.form['type']
    amount = float(request.form['amount'])
    date = datetime.strptime(request.form['date'], "%Y-%m-%d")
    note = request.form.get('note', '')
    user_id = session['user_id']

    if t_type == 'income':
        account_id = request.form['account_id']
        account = Account.query.get(account_id)
        account.balance += amount
        db.session.add(Transaction(
            type='income', amount=amount, date=date,
            note=note, user_id=user_id, account_id=account_id
        ))

    elif t_type == 'expense':
        account_id = request.form['account_id']
        account = Account.query.get(account_id)
        account.balance -= amount
        db.session.add(Transaction(
            type='expense', amount=amount, date=date,
            note=note, user_id=user_id, account_id=account_id
        ))

    elif t_type == 'transfer':
        from_id = request.form['from_account_id']
        to_id = request.form['to_account_id']
        from_account = Account.query.get(from_id)
        to_account = Account.query.get(to_id)

        from_account.balance -= amount
        to_account.balance += amount

        db.session.add(Transaction(
            type='transfer', amount=amount, date=date,
            note=note, user_id=user_id,
            from_account_id=from_id,
            to_account_id=to_id
        ))

    db.session.commit()
    return redirect(url_for('dashboard', user_id=user_id))
app.register_blueprint(transaction_bp)
app.register_blueprint(dashboard_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, request, redirect, url_for, render_template, session, flash
from datetime import timedelta
import os
from flask_sqlalchemy import SQLAlchemy
from models import db, User
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
app.permanent_session_lifetime = timedelta(days=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///walleto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    from models import User
    db.create_all()
    if not User.query.filter_by(email="alice@example.com").first():
        db.session.add(User(name="Alice", email="alice@example.com", password="password123"))
        db.session.commit()

@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        return redirect(url_for('dashboard', user_id=user_id))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session.permanent = True
            session['user_id'] = user.id
            return redirect(url_for('dashboard', user_id=user.id))
        else:
            error = 'Invalid email or password'

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

        # ✅ Validate password
        if len(password) < 6:
            error = "Password must meet all complexity requirements."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif User.query.filter_by(email=email).first():
            error = "Email already exists."
        else:
            new_user = User(
                name=f"{first_name} {last_name}",
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)
@app.route('/user/<int:user_id>')
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
        # Daily
        if t.date.year == current_year and t.date.strftime("%B") == current_month:
            key = t.date.strftime("%Y-%m-%d")
            daily_transactions[key].append(t)
        # Monthly
        if t.date.year == current_year:
            key = t.date.strftime("%B")
            if t.type == "income":
                monthly_summary[key]['income'] += t.amount
            elif t.type == "expense":
                monthly_summary[key]['expense'] += t.amount

    return render_template("dashboard.html",
                           user=user,
                           current_month=current_month,
                           current_year=current_year,
                           daily_transactions=daily_transactions,
                           monthly_summary=monthly_summary)
@app.route('/stats')
def stats():
    return "<h1>Stats Page</h1>"

@app.route('/accounts')
def accounts():
    return "<h1>Accounts Page</h1>"

@app.route('/more')
def more():
    return "<h1>More Page</h1>"

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)

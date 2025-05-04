from flask import Flask, request, redirect, url_for, render_template, session, flash
import uuid
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'password123'

# ========= OOP CLASSES =========

class Transaction:
    def __init__(self, amount, category, type_, note="", date=None):
        self.id = uuid.uuid4()
        self.amount = amount
        self.category = category
        self.type = type_  # 'income' or 'expense'
        self.date = date or datetime.now()
        self.note = note

    def __str__(self):
        return f"{self.date.date()} | {self.type.upper()} | {self.category} | ${self.amount:.2f} | {self.note}"

class User:
    def __init__(self, name, email, password):
        self.id = uuid.uuid4()
        self.name = name
        self.email = email
        self.password = password
        self.transactions = []
        self.budgets = defaultdict(float)

    def get_summary(self):
        summary = defaultdict(float)
        for t in self.transactions:
            if t.type == "income":
                summary[t.category] += t.amount
            elif t.type == "expense":
                summary[t.category] -= t.amount
        return summary

class UserManager:
    def __init__(self):
        self.users = {}

    def create_user(self, name, email, password):
        user = User(name, email, password)
        self.users[str(user.id)] = user
        return user

    def get_user(self, user_id):
        return self.users.get(user_id)

    def list_users(self):
        return list(self.users.values())


# ========= INITIAL DATA =========

user_manager = UserManager()
user_manager.create_user("Alice", "alice@example.com", "password123")
user_manager.create_user("Bob", "bob@example.com", "password321")


# ========= ROUTES =========

@app.route('/')
def index():
    users = user_manager.list_users()
    return render_template("index.html", users=users)
    

@app.route('/create_user', methods=['POST'])
def create_user():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user_manager.create_user(name, email, password)
    return redirect(url_for('index'))

#@app.route('/user/<user_id>')
def dashboard(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return "User not found", 404
    summary = user.get_summary()
    return render_template("dashboard.html", user=user, summary=summary)

@app.route('/user/<user_id>/add_transaction', methods=['POST'])
def add_transaction(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return "User not found", 404
    try:
        amount = float(request.form['amount'])
        category = request.form['category']
        type_ = request.form['type']
        note = request.form.get('note', '')
        transaction = Transaction(amount, category, type_, note)
        user.add_transaction(transaction)
    except Exception as e:
        return f"Error: {e}", 400
    return redirect(url_for('dashboard', user_id=user_id))

@app.route('/user/<user_id>/set_budget', methods=['POST'])
def set_budget(user_id):
    user = user_manager.get_user(user_id)
    if not user:
        return "User not found", 404
    try:
        category = request.form['category']
        amount = float(request.form['amount'])
        user.set_budget(category, amount)
    except Exception as e:
        return f"Error: {e}", 400
    return redirect(url_for('dashboard', user_id=user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        for user in user_manager.list_users():
            if user.email == email and user.password == password:
                session['user_id'] = str(user.id)
                return redirect(url_for('dashboard', user_id=user.id))
        error = 'Invalid email or password'
    return render_template('login.html', error=error)

@app.route('/user/<user_id>')
def dashboard(user_id):
    if session.get('user_id') != user_id:
        return redirect(url_for('login'))
    user = user_manager.get_user(user_id)
    if not user:
        return "User not found", 404
    summary = user.get_summary()
    return render_template("dashboard.html", user=user, summary=summary)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))
# ========= RUN =========

if __name__ == '__main__':
    app.run(debug=True)
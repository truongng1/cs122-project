from flask import Blueprint, render_template, request, redirect, session, url_for
from models.user import User

auth_bp = Blueprint('auth', __name__)

users = {}  # replace later with DB

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        for user in users.values():
            if user.email == email and user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('dashboard.dashboard'))
    return render_template('login.html')

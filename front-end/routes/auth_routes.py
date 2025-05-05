from flask import Blueprint, render_template, request, redirect, session, url_for
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session.permanent = True
            session['user_id'] = user.id
            return redirect(url_for('dashboard.dashboard'))
        error = 'Invalid email or password'
    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))

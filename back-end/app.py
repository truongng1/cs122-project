from flask import Flask
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.transaction_routes import transaction_bp
from models.user_manager import preload_users  # 👍 preloading users

preload_users()  # ✅ loads dummy users + transactions before app runs

app = Flask(__name__)
app.secret_key = 'secret123'  # ✅ needed for sessions

# ✅ Registering your blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(transaction_bp)

@app.route('/')
def home():
    return "Welcome to WalletO! Backend is working."  # ✅ root page test

if __name__ == "__main__":
    app.run(debug=True)  # ✅ run server in debug mode for dev

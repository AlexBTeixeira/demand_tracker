# app.py
import os
from flask import Flask, redirect, url_for, request
import MySQLdb.cursors
from flask_login import current_user
from werkzeug.utils import secure_filename

from config import Config
from extensions import mysql, login_manager, User

# Import Blueprints
from blueprints.auth import auth_bp
from blueprints.demands import demands_bp
from blueprints.tracker import tracker_bp
from blueprints.reports import reports_bp

# App Initialization
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.config.from_object(Config)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize Extensions
mysql.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, username, name, password_hash FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['name'], user_data['password_hash'])
    return None

# Global Routes
@app.route("/")
def home():
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'demands')):
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'demands'))
    return redirect(url_for("demands.dashboard"))

# Login requirement for all non-auth routes
@app.before_request
def require_login():
    if request.endpoint and 'static' not in request.endpoint and 'auth' not in request.endpoint and not login_manager._login_disabled:
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(demands_bp, url_prefix='/demands')
app.register_blueprint(tracker_bp, url_prefix='/tracker')
app.register_blueprint(reports_bp, url_prefix='/reports')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
# app.py
import os
from flask import Flask, redirect, url_for, request
import MySQLdb.cursors
from flask_login import current_user
import cloudinary 

from config import Config
from extensions import mysql, login_manager, User

# Import Blueprints
from blueprints.auth import auth_bp
from blueprints.demands import demands_bp
from blueprints.tracker import tracker_bp
from blueprints.reports import reports_bp

def create_app(config_class=Config):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )
    app.config.from_object(config_class)

    cloudinary.config(
      cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
      api_key = os.environ.get('CLOUDINARY_API_KEY'),
      api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
      secure = True # Sempre use HTTPS
    )

    # Garante que a pasta de upload exista
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Inicializa as extensões com o app
    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # User Loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Usamos o contexto da aplicação para garantir que a conexão esteja ativa
        with app.app_context():
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT id, username, name, password_hash FROM users WHERE id = %s", (user_id,))
            user_data = cur.fetchone()
            cur.close()
            if user_data:
                return User(user_data['id'], user_data['username'], user_data['name'], user_data['password_hash'])
            return None

    # Rotas Globais
    @app.route("/")
    def home():
        # A pasta de uploads principal é criada na inicialização.
        # A subpasta 'demands' pode ser criada aqui ou na rota de upload.
        demands_upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'demands')
        if not os.path.exists(demands_upload_path):
            os.makedirs(demands_upload_path)
        return redirect(url_for("demands.dashboard"))

    # Requer login para todas as rotas que não são de autenticação ou estáticas
    @app.before_request
    def require_login():
        if (
            request.endpoint and 
            'static' not in request.endpoint and 
            'auth' not in request.endpoint and 
            not login_manager._login_disabled
        ):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))

    # Registra os Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(demands_bp, url_prefix='/demands')
    app.register_blueprint(tracker_bp, url_prefix='/tracker')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    return app

# Bloco para execução local (desenvolvimento)
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5050, debug=True)
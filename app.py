# app.py
import os
import time
from flask import Flask, redirect, url_for, request
import MySQLdb.cursors
import cloudinary 

from config import Config
from extensions import mysql, User

#, login_manager, 

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

    # Configuração centralizada do Cloudinary
    cloudinary.config(
      cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
      api_key = os.environ.get('CLOUDINARY_API_KEY'),
      api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
      secure = True 
    )

    # Inicializa as extensões com o app
    mysql.init_app(app)

    # Rota Global simplificada
    @app.route("/")
    def home():
        # ## REMOVIDO ##
        # A lógica de criação de pastas locais foi removida.
        # A rota agora apenas redireciona para o dashboard.
        return redirect(url_for("demands.dashboard"))

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
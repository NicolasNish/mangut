import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'mangut_chave_secreta_local'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mangut.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 📸 Configuração da pasta de Upload de Imagens
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB por arquivo

    # Garante que a pasta app/static/uploads exista no computador
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'

    from app import models

    with app.app_context():
        db.create_all()

    from app.routes import main
    app.register_blueprint(main)

    return app
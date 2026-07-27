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

    db.init_app(app)

    # Configuração do Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Rota para redirecionar caso não esteja logado
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'

    from app import models

    with app.app_context():
        db.create_all()

    from app.routes import main
    app.register_blueprint(main)

    return app
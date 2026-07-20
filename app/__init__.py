from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Configuração da chave secreta e banco de dados SQLite
    app.config['SECRET_KEY'] = 'mangut_chave_secreta_local'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mangut.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Importar os modelos para registrar na base
    from app import models

    # Criar tabelas se não existirem
    with app.app_context():
        db.create_all()

    # Registrar rotas
    from app.routes import main
    app.register_blueprint(main)

    return app
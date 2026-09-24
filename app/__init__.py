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

    # Configuração de pasta para uploads locais
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor, inicie sessão para aceder a esta página.'

    # Importação dos modelos
    from app.models import Gastronomo

    # 🔑 USER_LOADER: diz ao Flask-Login como recarregar o utilizador a partir do ID da sessão
    @login_manager.user_loader
    def load_user(user_id):
        return Gastronomo.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    # Registo do Blueprint de rotas
    from app.routes import main
    app.register_blueprint(main)

    return app
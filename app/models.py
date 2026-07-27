from app import db, login_manager
from flask_login import UserMixin


# Função necessária para o Flask-Login carregar o usuário logado a partir da sessão
@login_manager.user_loader
def load_user(user_id):
    return Gastronomo.query.get(int(user_id))


class Gastronomo(db.Model, UserMixin):
    __tablename__ = 'gastronomos'
    idgastronomos = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(55), unique=True, nullable=False)
    telefone = db.Column(db.String(12))
    senha = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # 👑 Define se o usuário é Administrador

    # Sobrescreve o método get_id do UserMixin para usar idgastronomos como chave primária
    def get_id(self):
        return str(self.idgastronomos)

    # Relacionamentos
    receitas = db.relationship('Receita', backref='autor', lazy=True)
    avaliacoes = db.relationship('AvaliacaoReceita', backref='usuario', lazy=True)


class Categoria(db.Model):
    __tablename__ = 'categoria'
    idcategoria = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(45), nullable=False)

    receitas = db.relationship('Receita', backref='categoria_rel', lazy=True)


class Receita(db.Model):
    __tablename__ = 'receitas'
    idreceitas = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(90), nullable=False)
    descricao = db.Column(db.String(255))
    lista_ingredientes = db.Column(db.Text, nullable=False)
    modo_preparo = db.Column(db.Text, nullable=False)
    imagem_url = db.Column(db.String(500), nullable=True)

    # Chaves Estrangeiras
    gastronomos_idgastronomos = db.Column(db.Integer, db.ForeignKey('gastronomos.idgastronomos'), nullable=False)
    categoria_idcategoria = db.Column(db.Integer, db.ForeignKey('categoria.idcategoria'), nullable=False)

    avaliacoes = db.relationship('AvaliacaoReceita', backref='receita', lazy=True)


class AvaliacaoReceita(db.Model):
    __tablename__ = 'avaliacoes_receitas'
    id = db.Column(db.Integer, primary_key=True)
    avaliacoes = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.String(500))

    receitas_idreceitas = db.Column(db.Integer, db.ForeignKey('receitas.idreceitas'), nullable=False)
    gastronomos_idgastronomos = db.Column(db.Integer, db.ForeignKey('gastronomos.idgastronomos'), nullable=True)
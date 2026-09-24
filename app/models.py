from app import db
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

class Gastronomo(UserMixin, db.Model):
    __tablename__ = 'gastronomos'

    idgastronomos = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    # Relacionamentos usando back_populates (evita conflito de backref)
    receitas = db.relationship('Receita', back_populates='autor', lazy=True)
    avaliacoes = db.relationship('AvaliacaoReceita', back_populates='usuario', lazy=True, cascade='all, delete-orphan')

    def get_id(self):
        return str(self.idgastronomos)


class Categoria(db.Model):
    __tablename__ = 'categoria'

    idcategoria = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

    receitas = db.relationship('Receita', back_populates='categoria_rel', lazy=True)


class Receita(db.Model):
    __tablename__ = 'receitas'

    idreceitas = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    lista_ingredientes = db.Column(db.Text, nullable=False)
    modo_preparo = db.Column(db.Text, nullable=False)
    imagem_url = db.Column(db.String(255), nullable=True)

    categoria_idcategoria = db.Column(db.Integer, db.ForeignKey('categoria.idcategoria'), nullable=False)
    gastronomos_idgastronomos = db.Column(db.Integer, db.ForeignKey('gastronomos.idgastronomos'), nullable=False)

    categoria_rel = db.relationship('Categoria', back_populates='receitas')
    autor = db.relationship('Gastronomo', back_populates='receitas')
    avaliacoes = db.relationship('AvaliacaoReceita', back_populates='receita', lazy=True, cascade='all, delete-orphan')


class AvaliacaoReceita(db.Model):
    __tablename__ = 'avaliacoes_receitas'

    id = db.Column(db.Integer, primary_key=True)
    avaliacoes = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=True)

    receitas_idreceitas = db.Column(db.Integer, db.ForeignKey('receitas.idreceitas'), nullable=False)
    gastronomos_idgastronomos = db.Column(db.Integer, db.ForeignKey('gastronomos.idgastronomos'), nullable=False)

    receita = db.relationship('Receita', back_populates='avaliacoes')
    usuario = db.relationship('Gastronomo', back_populates='avaliacoes')

    # Garante no banco que cada usuário só avalia uma receita 1 vez
    __table_args__ = (
        UniqueConstraint('receitas_idreceitas', 'gastronomos_idgastronomos', name='uq_usuario_receita_avaliacao'),
    )
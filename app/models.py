from app import db
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from datetime import datetime

# Tabela Associativa N:N entre Pasta e Receita
pastas_receitas = db.Table('pastas_receitas',
                           db.Column('pasta_id', db.Integer, db.ForeignKey('pastas_receitas_usuario.id'),
                                     primary_key=True),
                           db.Column('receita_id', db.Integer, db.ForeignKey('receitas.idreceitas'), primary_key=True)
                           )


class Gastronomo(UserMixin, db.Model):
    __tablename__ = 'gastronomos'

    idgastronomos = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    foto_perfil = db.Column(db.String(255), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    receitas = db.relationship('Receita', back_populates='autor', lazy=True)
    avaliacoes = db.relationship('AvaliacaoReceita', back_populates='usuario', lazy=True, cascade='all, delete-orphan')

    # 📚 Pastas de receitas do usuário
    pastas = db.relationship('PastaReceitas', back_populates='usuario', lazy=True, cascade='all, delete-orphan')

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
    visualizacoes = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='ativo')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

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
    status = db.Column(db.String(20), default='ativo')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    receitas_idreceitas = db.Column(db.Integer, db.ForeignKey('receitas.idreceitas'), nullable=False)
    gastronomos_idgastronomos = db.Column(db.Integer, db.ForeignKey('gastronomos.idgastronomos'), nullable=False)

    receita = db.relationship('Receita', back_populates='avaliacoes')
    usuario = db.relationship('Gastronomo', back_populates='avaliacoes')

    __table_args__ = (
        UniqueConstraint('receitas_idreceitas', 'gastronomos_idgastronomos', name='uq_usuario_receita_avaliacao'),
    )


# Pastas / Coleções de Receitas
class PastaReceitas(db.Model):
    __tablename__ = 'pastas_receitas_usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    gastronomo_id = db.Column(db.Integer, db.ForeignKey('gastronomos.idgastronomos'), nullable=False)
    usuario = db.relationship('Gastronomo', back_populates='pastas')

    # Relação com as receitas guardadas nesta pasta
    receitas_salvas = db.relationship('Receita', secondary=pastas_receitas, backref='pastas_onde_esta_salva',
                                      lazy='subquery')
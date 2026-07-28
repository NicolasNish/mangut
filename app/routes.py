import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import Receita, AvaliacaoReceita, Categoria, Gastronomo

main = Blueprint('main', __name__)

# Extensões de imagem permitidas para upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def salvar_imagem(file):
    """Função auxiliar para validar e salvar a imagem enviada do computador."""
    if file and file.filename != '':
        extensao = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if extensao in ALLOWED_EXTENSIONS:
            # Gera um nome único usando UUID para evitar sobreposição de arquivos no disco
            nome_arquivo = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            caminho_completo = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)
            file.save(caminho_completo)
            # Retorna o caminho relativo acessível pela web
            return f"/static/uploads/{nome_arquivo}"
    return None


# 🟢 Página Inicial (Home)
@main.route('/')
def index():
    query = request.args.get('q', '').strip()

    if query:
        # Busca por nome OU por ingredientes
        receitas_db = Receita.query.filter(
            (Receita.nome.ilike(f'%{query}%')) |
            (Receita.lista_ingredientes.ilike(f'%{query}%'))
        ).all()
    else:
        receitas_db = Receita.query.all()

    receitas_formatadas = []
    for r in receitas_db:
        avaliacoes = AvaliacaoReceita.query.filter_by(receitas_idreceitas=r.idreceitas).all()
        qtd_avaliacoes = len(avaliacoes)
        media_estrelas = round(sum(a.avaliacoes for a in avaliacoes) / qtd_avaliacoes, 1) if qtd_avaliacoes > 0 else 0.0

        receitas_formatadas.append({
            "id": r.idreceitas,
            "nome": r.nome,
            "categoria": r.categoria_rel.nome,
            "descricao": r.descricao,
            "imagem_url": r.imagem_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
            "media_estrelas": media_estrelas,
            "qtd_avaliacoes": qtd_avaliacoes
        })

    return render_template('index.html', receitas=receitas_formatadas, busca=query)


# 🔐 Autenticação: Cadastro
@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    next_page = request.args.get('next') or request.form.get('next')

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if Gastronomo.query.filter_by(email=email).first():
            return redirect(url_for('main.cadastro', next=next_page))

        novo_usuario = Gastronomo(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
            is_admin=False
        )
        db.session.add(novo_usuario)
        db.session.commit()
        login_user(novo_usuario)

        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))

    return render_template('cadastro.html', next=next_page)


# 🔐 Autenticação: Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next') or request.form.get('next')

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = Gastronomo.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)

            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))

    return render_template('login.html', next=next_page)


# 🔐 Autenticação: Logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# 👤 Perfil do Usuário
@main.route('/perfil')
@login_required
def perfil():
    receitas_usuario = Receita.query.filter_by(gastronomos_idgastronomos=current_user.idgastronomos).all()
    receitas_formatadas = []

    for r in receitas_usuario:
        avaliacoes = AvaliacaoReceita.query.filter_by(receitas_idreceitas=r.idreceitas).all()
        qtd_avaliacoes = len(avaliacoes)
        media_estrelas = round(sum(a.avaliacoes for a in avaliacoes) / qtd_avaliacoes, 1) if qtd_avaliacoes > 0 else 0.0

        receitas_formatadas.append({
            "id": r.idreceitas,
            "nome": r.nome,
            "categoria": r.categoria_rel.nome,
            "descricao": r.descricao,
            "imagem_url": r.imagem_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
            "media_estrelas": media_estrelas,
            "qtd_avaliacoes": qtd_avaliacoes
        })

    avaliacoes_usuario = AvaliacaoReceita.query.filter_by(gastronomos_idgastronomos=current_user.idgastronomos).all()
    avaliacoes_formatadas = []
    for av in avaliacoes_usuario:
        avaliacoes_formatadas.append({
            "receita_id": av.receita.idreceitas,
            "receita_nome": av.receita.nome,
            "nota": av.avaliacoes,
            "comentario": av.comentario
        })

    return render_template(
        'perfil.html',
        usuario=current_user,
        receitas=receitas_formatadas,
        avaliacoes=avaliacoes_formatadas
    )


# ✏️ Rota POST: Editar dados do Perfil
@main.route('/perfil/editar', methods=['POST'])
@login_required
def editar_perfil():
    novo_nome = request.form.get('nome')
    novo_telefone = request.form.get('telefone')

    if novo_nome:
        current_user.nome = novo_nome
        current_user.telefone = novo_telefone
        db.session.commit()

    return redirect(url_for('main.perfil'))


# 🗑️ Rota POST: Excluir a própria conta do usuário
@main.route('/perfil/excluir-conta', methods=['POST'])
@login_required
def excluir_conta():
    usuario = Gastronomo.query.get(current_user.idgastronomos)

    AvaliacaoReceita.query.filter_by(gastronomos_idgastronomos=usuario.idgastronomos).delete()

    receitas_usuario = Receita.query.filter_by(gastronomos_idgastronomos=usuario.idgastronomos).all()
    for r in receitas_usuario:
        AvaliacaoReceita.query.filter_by(receitas_idreceitas=r.idreceitas).delete()
        db.session.delete(r)

    logout_user()
    db.session.delete(usuario)
    db.session.commit()

    return redirect(url_for('main.index'))


# ➕ Cadastrar Nova Receita (Apenas usuários logados)
@main.route('/receita/nova', methods=['GET', 'POST'])
@login_required
def formulario_nova_receita():
    if request.method == 'POST':
        nome = request.form.get('nome')
        categoria_id = request.form.get('categoria_id')
        descricao = request.form.get('descricao')
        lista_ingredientes = request.form.get('lista_ingredientes')
        modo_preparo = request.form.get('modo_preparo')

        # 1. Tenta salvar o arquivo enviado do computador
        file_imagem = request.files.get('imagem_arquivo')
        imagem_url = salvar_imagem(file_imagem)

        # 2. Se não enviou arquivo do PC, pega a URL informada no input de texto
        if not imagem_url:
            imagem_url = request.form.get('imagem_url')

        if nome and categoria_id and lista_ingredientes and modo_preparo:
            nova_receita = Receita(
                nome=nome,
                descricao=descricao,
                lista_ingredientes=lista_ingredientes,
                modo_preparo=modo_preparo,
                imagem_url=imagem_url,
                categoria_idcategoria=int(categoria_id),
                gastronomos_idgastronomos=current_user.idgastronomos
            )
            db.session.add(nova_receita)
            db.session.commit()
            return redirect(url_for('main.detalhe_receita', id=nova_receita.idreceitas))

    categorias = Categoria.query.all()
    return render_template('nova_receita.html', categorias=categorias)


# 📖 Detalhe da Receita
@main.route('/receita/<int:id>')
def detalhe_receita(id):
    receita = Receita.query.get_or_404(id)
    ingredientes = receita.lista_ingredientes.split(',') if receita.lista_ingredientes else []

    avaliacoes_db = AvaliacaoReceita.query.filter_by(receitas_idreceitas=id).all()
    qtd_avaliacoes = len(avaliacoes_db)

    if qtd_avaliacoes > 0:
        media_estrelas = round(sum(a.avaliacoes for a in avaliacoes_db) / qtd_avaliacoes, 1)
    else:
        media_estrelas = 0.0

    avaliacoes_formatadas = []
    for av in avaliacoes_db:
        nome_autor = av.usuario.nome if av.usuario else "Gastrônomo Anônimo"
        autor_id = av.gastronomos_idgastronomos if av.usuario else None

        avaliacoes_formatadas.append({
            "id": av.id,
            "avaliacoes": av.avaliacoes,
            "comentario": av.comentario,
            "autor_nome": nome_autor,
            "autor_id": autor_id
        })

    dados_receita = {
        "id": receita.idreceitas,
        "nome": receita.nome,
        "categoria": receita.categoria_rel.nome,
        "descricao": receita.descricao,
        "modo_preparo": receita.modo_preparo,
        "imagem_url": receita.imagem_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        "autor_id": receita.gastronomos_idgastronomos,
        "autor_nome": receita.autor.nome,
        "media_estrelas": media_estrelas,
        "qtd_avaliacoes": qtd_avaliacoes
    }

    return render_template(
        'receita.html',
        receita=dados_receita,
        ingredientes=ingredientes,
        avaliacoes=avaliacoes_formatadas
    )


# 🗑️ Rota POST: Excluir uma Avaliação
@main.route('/avaliacao/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_avaliacao(id):
    avaliacao = AvaliacaoReceita.query.get_or_404(id)
    receita_id = avaliacao.receitas_idreceitas

    if avaliacao.gastronomos_idgastronomos != current_user.idgastronomos and not current_user.is_admin:
        return redirect(url_for('main.detalhe_receita', id=receita_id))

    db.session.delete(avaliacao)
    db.session.commit()

    return redirect(url_for('main.detalhe_receita', id=receita_id))


# ✏️ Editar Receita (Apenas Autor ou ADM)
@main.route('/receita/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def formulario_editar_receita(id):
    receita = Receita.query.get_or_404(id)

    if receita.gastronomos_idgastronomos != current_user.idgastronomos and not current_user.is_admin:
        return redirect(url_for('main.detalhe_receita', id=id))

    if request.method == 'POST':
        receita.nome = request.form.get('nome')
        receita.categoria_idcategoria = int(request.form.get('categoria_id'))
        receita.descricao = request.form.get('descricao')
        receita.lista_ingredientes = request.form.get('lista_ingredientes')
        receita.modo_preparo = request.form.get('modo_preparo')

        # Tenta pegar uma nova foto enviada do computador
        file_imagem = request.files.get('imagem_arquivo')
        nova_imagem = salvar_imagem(file_imagem)

        if nova_imagem:
            receita.imagem_url = nova_imagem
        elif request.form.get('imagem_url'):
            receita.imagem_url = request.form.get('imagem_url')

        db.session.commit()
        return redirect(url_for('main.detalhe_receita', id=receita.idreceitas))

    categorias = Categoria.query.all()
    dados_receita = {
        "id": receita.idreceitas,
        "nome": receita.nome,
        "descricao": receita.descricao,
        "lista_ingredientes": receita.lista_ingredientes,
        "modo_preparo": receita.modo_preparo,
        "imagem_url": receita.imagem_url,
        "categoria_id": receita.categoria_idcategoria
    }
    return render_template('editar_receita.html', receita=dados_receita, categorias=categorias)


# 🗑️ Excluir Receita (Apenas Autor ou ADM)
@main.route('/receita/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_receita(id):
    receita = Receita.query.get_or_404(id)

    if receita.gastronomos_idgastronomos != current_user.idgastronomos and not current_user.is_admin:
        return redirect(url_for('main.detalhe_receita', id=id))

    AvaliacaoReceita.query.filter_by(receitas_idreceitas=id).delete()
    db.session.delete(receita)
    db.session.commit()
    return redirect(url_for('main.index'))


# ⭐ Avaliar Receita (Apenas Usuários Logados)
@main.route('/receita/<int:id>/avaliar', methods=['POST'])
@login_required
def avaliar_receita(id):
    nota = request.form.get('avaliacoes')
    comentario = request.form.get('comentario')

    if nota and comentario:
        nova_avaliacao = AvaliacaoReceita(
            avaliacoes=int(nota),
            comentario=comentario,
            receitas_idreceitas=id,
            gastronomos_idgastronomos=current_user.idgastronomos
        )
        db.session.add(nova_avaliacao)
        db.session.commit()

    return redirect(url_for('main.detalhe_receita', id=id))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import Receita, AvaliacaoReceita, Categoria, Gastronomo

main = Blueprint('main', __name__)

# Rota Inicial
@main.route('/')
def index():
    receitas_db = Receita.query.all()
    receitas_formatadas = []
    for r in receitas_db:
        receitas_formatadas.append({
            "id": r.idreceitas,
            "nome": r.nome,
            "categoria": r.categoria_rel.nome,
            "descricao": r.descricao,
            "imagem_url": r.imagem_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500"
        })
    return render_template('index.html', receitas=receitas_formatadas)


# 🔐 Autenticação: Cadastro
@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    # Captura a página de origem enviada via parâmetro GET/POST
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

        # Redireciona para a página da receita original ou para a home
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.index'))

    return render_template('cadastro.html', next=next_page)


# 🔐 Autenticação: Login
@main.route('/login', methods=['GET', 'POST'])
def login():
    # Captura a página de origem enviada pelo Flask-Login ou via URL
    next_page = request.args.get('next') or request.form.get('next')

    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = Gastronomo.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)

            # Redireciona para a página da receita original ou para a home
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
        imagem_url = request.form.get('imagem_url')

        if nome and categoria_id and lista_ingredientes and modo_preparo:
            nova_receita = Receita(
                nome=nome,
                descricao=descricao,
                lista_ingredientes=lista_ingredientes,
                modo_preparo=modo_preparo,
                imagem_url=imagem_url,
                categoria_idcategoria=int(categoria_id),
                gastronomos_idgastronomos=current_user.idgastronomos # Atribui ao usuário logado
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

    # Buscar avaliações cadastradas da receita
    avaliacoes_db = AvaliacaoReceita.query.filter_by(receitas_idreceitas=id).all()

    # Formata as avaliações trazendo o nome do usuário que comentou
    avaliacoes_formatadas = []
    for av in avaliacoes_db:
        nome_autor = av.usuario.nome if av.usuario else "Gastrônomo Anônimo"
        avaliacoes_formatadas.append({
            "avaliacoes": av.avaliacoes,
            "comentario": av.comentario,
            "autor_nome": nome_autor
        })

    dados_receita = {
        "id": receita.idreceitas,
        "nome": receita.nome,
        "categoria": receita.categoria_rel.nome,
        "descricao": receita.descricao,
        "modo_preparo": receita.modo_preparo,
        "imagem_url": receita.imagem_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
        "autor_id": receita.gastronomos_idgastronomos,
        "autor_nome": receita.autor.nome
    }

    return render_template(
        'receita.html',
        receita=dados_receita,
        ingredientes=ingredientes,
        avaliacoes=avaliacoes_formatadas
    )

# ✏️ Editar Receita (Apenas Autor ou ADM)
@main.route('/receita/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def formulario_editar_receita(id):
    receita = Receita.query.get_or_404(id)

    # TRAVA DE SEGURANÇA: Somente o dono ou Admin pode editar
    if receita.gastronomos_idgastronomos != current_user.idgastronomos and not current_user.is_admin:
        return redirect(url_for('main.detalhe_receita', id=id))

    if request.method == 'POST':
        receita.nome = request.form.get('nome')
        receita.categoria_idcategoria = int(request.form.get('categoria_id'))
        receita.descricao = request.form.get('descricao')
        receita.imagem_url = request.form.get('imagem_url')
        receita.lista_ingredientes = request.form.get('lista_ingredientes')
        receita.modo_preparo = request.form.get('modo_preparo')

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

    # TRAVA DE SEGURANÇA: Somente o dono ou Admin pode excluir
    if receita.gastronomos_idgastronomos != current_user.idgastronomos and not current_user.is_admin:
        return redirect(url_for('main.detalhe_receita', id=id))

    AvaliacaoReceita.query.filter_by(receitas_idreceitas=id).delete()
    db.session.delete(receita)
    db.session.commit()
    return redirect(url_for('main.index'))

# ⭐ Avaliar Receita (Apenas Usuários Logados)
@main.route('/receita/<int:id>/avaliar', methods=['POST'])
@login_required # Trava de Segurança: impede o envio por quem não está logado
def avaliar_receita(id):
    nota = request.form.get('avaliacoes')
    comentario = request.form.get('comentario')

    if nota and comentario:
        nova_avaliacao = AvaliacaoReceita(
            avaliacoes=int(nota),
            comentario=comentario,
            receitas_idreceitas=id,
            gastronomos_idgastronomos=current_user.idgastronomos # Salva o ID do usuário logado
        )
        db.session.add(nova_avaliacao)
        db.session.commit()

    return redirect(url_for('main.detalhe_receita', id=id))
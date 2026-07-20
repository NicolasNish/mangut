from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Receita, AvaliacaoReceita, Categoria

main = Blueprint('main', __name__)


# Rota da Página Inicial (Home)
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


# Formulário de Nova Receita (GET)
@main.route('/receita/nova', methods=['GET'])
def formulario_nova_receita():
    categorias = Categoria.query.all()
    return render_template('nova_receita.html', categorias=categorias)


# Salvar Nova Receita (POST)
@main.route('/receita/nova', methods=['POST'])
def salvar_nova_receita():
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
            gastronomos_idgastronomos=1
        )
        db.session.add(nova_receita)
        db.session.commit()

        return redirect(url_for('main.detalhe_receita', id=nova_receita.idreceitas))

    return redirect(url_for('main.formulario_nova_receita'))


# Visualizar Detalhes da Receita
@main.route('/receita/<int:id>')
def detalhe_receita(id):
    receita = Receita.query.get_or_404(id)
    ingredientes = receita.lista_ingredientes.split(',') if receita.lista_ingredientes else []
    avaliacoes = AvaliacaoReceita.query.filter_by(receitas_idreceitas=id).all()

    dados_receita = {
        "id": receita.idreceitas,
        "nome": receita.nome,
        "categoria": receita.categoria_rel.nome,
        "descricao": receita.descricao,
        "modo_preparo": receita.modo_preparo,
        "imagem_url": receita.imagem_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500"
    }

    return render_template('receita.html', receita=dados_receita, ingredientes=ingredientes, avaliacoes=avaliacoes)


# ✏️ Formulário de Editar Receita (GET)
@main.route('/receita/<int:id>/editar', methods=['GET'])
def formulario_editar_receita(id):
    receita = Receita.query.get_or_404(id)
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


# ✏️ Salvar Edição da Receita (POST)
@main.route('/receita/<int:id>/editar', methods=['POST'])
def salvar_edicao_receita(id):
    receita = Receita.query.get_or_404(id)

    receita.nome = request.form.get('nome')
    receita.categoria_idcategoria = int(request.form.get('categoria_id'))
    receita.descricao = request.form.get('descricao')
    receita.imagem_url = request.form.get('imagem_url')
    receita.lista_ingredientes = request.form.get('lista_ingredientes')
    receita.modo_preparo = request.form.get('modo_preparo')

    db.session.commit()

    return redirect(url_for('main.detalhe_receita', id=receita.idreceitas))


# Salvar Avaliação (POST)
@main.route('/receita/<int:id>/avaliar', methods=['POST'])
def avaliar_receita(id):
    nota = request.form.get('avaliacoes')
    comentario = request.form.get('comentario')

    if nota and comentario:
        nova_avaliacao = AvaliacaoReceita(
            avaliacoes=int(nota),
            comentario=comentario,
            receitas_idreceitas=id,
            gastronomos_idgastronomos=1
        )
        db.session.add(nova_avaliacao)
        db.session.commit()

    return redirect(url_for('main.detalhe_receita', id=id))


# 🗑️ Rota POST: Excluir uma receita e suas avaliações
@main.route('/receita/<int:id>/excluir', methods=['POST'])
def excluir_receita(id):
    receita = Receita.query.get_or_404(id)

    # 1. Primeiro exclui as avaliações associadas à receita (para evitar erro de chave estrangeira)
    AvaliacaoReceita.query.filter_by(receitas_idreceitas=id).delete()

    # 2. Exclui a receita em si
    db.session.delete(receita)
    db.session.commit()

    # Redireciona de volta para a página inicial
    return redirect(url_for('main.index'))
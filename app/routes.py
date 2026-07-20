from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import Receita, AvaliacaoReceita, Categoria

main = Blueprint('main', __name__)

@main.route('/')
def index():
    receitas_db = Receita.query.all()
    receitas_formatadas = []
    for r in receitas_db:
        receitas_formatadas.append({
            "id": r.idreceitas,
            "nome": r.nome,
            "categoria": r.categoria_rel.nome,
            "descricao": r.descricao
        })
    return render_template('index.html', receitas=receitas_formatadas)


# 🟢 Rota GET: Exibe o formulário de cadastro de receita
@main.route('/receita/nova', methods=['GET'])
def formulario_nova_receita():
    categorias = Categoria.query.all()
    return render_template('nova_receita.html', categorias=categorias)


# 🟢 Rota POST: Processa o formulário e salva a nova receita no banco
@main.route('/receita/nova', methods=['POST'])
def salvar_nova_receita():
    nome = request.form.get('nome')
    categoria_id = request.form.get('categoria_id')
    descricao = request.form.get('descricao')
    lista_ingredientes = request.form.get('lista_ingredientes')
    modo_preparo = request.form.get('modo_preparo')

    if nome and categoria_id and lista_ingredientes and modo_preparo:
        nova_receita = Receita(
            nome=nome,
            descricao=descricao,
            lista_ingredientes=lista_ingredientes,
            modo_preparo=modo_preparo,
            categoria_idcategoria=int(categoria_id),
            gastronomos_idgastronomos=1  # Usando o usuário padrão criado pelo seed
        )
        db.session.add(nova_receita)
        db.session.commit()

        # Redireciona diretamente para a página da receita recém-criada
        return redirect(url_for('main.detalhe_receita', id=nova_receita.idreceitas))

    return redirect(url_for('main.formulario_nova_receita'))


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
        "modo_preparo": receita.modo_preparo
    }

    return render_template('receita.html', receita=dados_receita, ingredientes=ingredientes, avaliacoes=avaliacoes)


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
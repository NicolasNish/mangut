import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import Receita, AvaliacaoReceita, Categoria, Gastronomo, PastaReceitas
import base64
from io import BytesIO
from PIL import Image

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def salvar_imagem(file):
    """Valida e salva arquivos normais enviados via upload tradicional."""
    if file and file.filename != '':
        extensao = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if extensao in ALLOWED_EXTENSIONS:
            nome_arquivo = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            caminho_completo = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)
            file.save(caminho_completo)
            return f"/static/uploads/{nome_arquivo}"
    return None

def salvar_imagem_cortada(dados_base64, prefixo="receita"):
    """Decodifica a imagem cortada pelo navegador e salva como arquivo JPG/PNG no disco."""
    if not dados_base64 or not dados_base64.startswith('data:image'):
        return None
    try:
        cabecalho, base64_str = dados_base64.split(',', 1)
        extensao = 'png' if 'png' in cabecalho else 'jpg'

        nome_arquivo = f"{prefixo}_{uuid.uuid4().hex}.{extensao}"
        caminho_completo = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo)

        imagem_bytes = base64.b64decode(base64_str)
        imagem = Image.open(BytesIO(imagem_bytes))

        # Converte para RGB se for salvar em JPEG
        if extensao == 'jpg' and imagem.mode in ("RGBA", "P"):
            imagem = imagem.convert("RGB")

        imagem.save(caminho_completo)
        return f"/static/uploads/{nome_arquivo}"
    except Exception as e:
        print(f"Erro ao salvar imagem cortada: {e}")
        return None


def formatar_receitas(query_obj):
    """Função utilitária para formatar receitas com as respetivas médias."""
    receitas_db = query_obj.all()
    formatadas = []
    for r in receitas_db:
        avaliacoes = AvaliacaoReceita.query.filter_by(receitas_idreceitas=r.idreceitas).all()
        qtd = len(avaliacoes)
        media = round(sum(a.avaliacoes for a in avaliacoes) / qtd, 1) if qtd > 0 else 0.0
        formatadas.append({
            "id": r.idreceitas,
            "nome": r.nome,
            "categoria": r.categoria_rel.nome,
            "categoria_id": r.categoria_idcategoria,
            "descricao": r.descricao,
            "imagem_url": r.imagem_url,  # 🟢 Fica None caso não exista foto
            "media_estrelas": media,
            "qtd_avaliacoes": qtd
        })
    return formatadas


# 🟢 Página Inicial (Home / Landing Page)
@main.route('/')
def index():
    # Na Home trazemos os pratos em destaque
    receitas_destaque = formatar_receitas(Receita.query.limit(6))
    return render_template('index.html', receitas=receitas_destaque)


# 🍲 Página Dedicada: Catálogo Completo de Receitas com Filtro Multicategoria
@main.route('/receitas')
def catalogo_receitas():
    query = request.args.get('q', '').strip()
    categorias_selecionadas = request.args.getlist('categoria', type=int)

    consulta = Receita.query

    if categorias_selecionadas:
        consulta = consulta.filter(Receita.categoria_idcategoria.in_(categorias_selecionadas))

    if query:
        consulta = consulta.filter(
            (Receita.nome.ilike(f'%{query}%')) |
            (Receita.lista_ingredientes.ilike(f'%{query}%'))
        )

    receitas_formatadas = formatar_receitas(consulta)
    todas_categorias = Categoria.query.all()

    return render_template(
        'receitas.html',
        receitas=receitas_formatadas,
        categorias=todas_categorias,
        categorias_selecionadas=categorias_selecionadas,
        busca=query
    )


# 📂 Página Dedicada: Categorias da Gastronomia
@main.route('/categorias')
def ver_categorias():
    categorias = Categoria.query.all()
    dados_categorias = []
    for cat in categorias:
        receitas_cat = formatar_receitas(Receita.query.filter_by(categoria_idcategoria=cat.idcategoria))
        dados_categorias.append({
            "id": cat.idcategoria,
            "nome": cat.nome,
            "qtd_receitas": len(receitas_cat),
            "receitas": receitas_cat
        })
    return render_template('categorias.html', categorias=dados_categorias)


# 🌿 Página Dedicada: Sobre o Projeto e Desenvolvedores
@main.route('/sobre')
def sobre():
    return render_template('sobre.html')


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
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')

        usuario = Gastronomo.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('E-mail ou senha incorretos. Verifique suas credenciais.', 'danger')

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
    receitas_usuario = formatar_receitas(Receita.query.filter_by(gastronomos_idgastronomos=current_user.idgastronomos))

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
        receitas=receitas_usuario,
        avaliacoes=avaliacoes_formatadas
    )


# Rota POST: Editar dados do Perfil (Nome, Telefone e Foto de Perfil)
@main.route('/perfil/editar', methods=['POST'])
@login_required
def editar_perfil():
    novo_nome = request.form.get('nome')
    novo_telefone = request.form.get('telefone')

    # 1. Pega a foto cortada vinda do Cropper.js (Base64)
    foto_base64 = request.form.get('foto_perfil_cortada')
    nova_foto = salvar_imagem_cortada(foto_base64, prefixo="perfil")

    # 2. Fallback: caso tenha enviado o arquivo direto sem corte
    if not nova_foto:
        file_foto = request.files.get('foto_perfil_arquivo')
        nova_foto = salvar_imagem(file_foto)

    if novo_nome:
        current_user.nome = novo_nome
        current_user.telefone = novo_telefone

        # Atualiza a foto se uma nova tiver sido enviada
        if nova_foto:
            current_user.foto_perfil = nova_foto

        db.session.commit()

    return redirect(url_for('main.perfil'))

# 🗑️ Rota POST: Excluir Conta
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


# ➕ Cadastrar Nova Receita
@main.route('/receita/nova', methods=['GET', 'POST'])
@login_required
def formulario_nova_receita():
    if request.method == 'POST':
        nome = request.form.get('nome')
        categoria_id = request.form.get('categoria_id')
        descricao = request.form.get('descricao')
        lista_ingredientes = request.form.get('lista_ingredientes')
        modo_preparo = request.form.get('modo_preparo')

        # 1. Pega a imagem já recortada pelo navegador (Base64)
        imagem_base64 = request.form.get('imagem_cortada')
        imagem_url = salvar_imagem_cortada(imagem_base64, prefixo="receita")

        # 2. Fallback: caso o usuário tenha enviado o arquivo normal sem cortar
        if not imagem_url:
            file_imagem = request.files.get('imagem_arquivo')
            imagem_url = salvar_imagem(file_imagem)

        if nome and categoria_id and lista_ingredientes and modo_preparo:
            nova_receita = Receita(
                nome=nome,
                descricao=descricao,
                lista_ingredientes=lista_ingredientes.strip(),
                modo_preparo=modo_preparo.strip(),
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

    if receita.lista_ingredientes:
        if '\n' in receita.lista_ingredientes:
            ingredientes = [linha.strip() for linha in receita.lista_ingredientes.splitlines() if linha.strip()]
        else:
            ingredientes = [item.strip() for item in receita.lista_ingredientes.split(',') if item.strip()]
    else:
        ingredientes = []

    avaliacoes_db = AvaliacaoReceita.query.filter_by(receitas_idreceitas=id).all()
    qtd_avaliacoes = len(avaliacoes_db)
    media_estrelas = round(sum(a.avaliacoes for a in avaliacoes_db) / qtd_avaliacoes, 1) if qtd_avaliacoes > 0 else 0.0

    # 🔍 Verificar se o usuário autenticado já avaliou esta receita
    minha_avaliacao = None
    if current_user.is_authenticated:
        minha_avaliacao_obj = AvaliacaoReceita.query.filter_by(
            receitas_idreceitas=id,
            gastronomos_idgastronomos=current_user.idgastronomos
        ).first()
        if minha_avaliacao_obj:
            minha_avaliacao = {
                "id": minha_avaliacao_obj.id,
                "nota": minha_avaliacao_obj.avaliacoes,
                "comentario": minha_avaliacao_obj.comentario
            }

    minhas_pastas = []
    ids_pastas_salvas = []
    if current_user.is_authenticated:
        minhas_pastas = PastaReceitas.query.filter_by(gastronomo_id=current_user.idgastronomos).all()
        ids_pastas_salvas = [p.id for p in minhas_pastas if receita in p.receitas_salvas]

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
        "imagem_url": receita.imagem_url,  # 🟢 Sem placeholder externo
        "autor_id": receita.gastronomos_idgastronomos,
        "autor_nome": receita.autor.nome,
        "media_estrelas": media_estrelas,
        "qtd_avaliacoes": qtd_avaliacoes
    }

    return render_template(
        'receita.html',
        receita=dados_receita,
        ingredientes=ingredientes,
        avaliacoes=avaliacoes_formatadas,
        minha_avaliacao=minha_avaliacao,
        minhas_pastas=minhas_pastas,
        ids_pastas_salvas=ids_pastas_salvas
    )

# 🗑️ Excluir Avaliação
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


# ✏️ Editar Receita
@main.route('/receita/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def formulario_editar_receita(id):
    receita = Receita.query.get_or_404(id)

    # Verificação de permissão: apenas o autor ou administrador pode editar
    if receita.gastronomos_idgastronomos != current_user.idgastronomos and not current_user.is_admin:
        return redirect(url_for('main.detalhe_receita', id=id))

    if request.method == 'POST':
        receita.nome = request.form.get('nome')
        receita.categoria_idcategoria = int(request.form.get('categoria_id'))
        receita.descricao = request.form.get('descricao')
        receita.lista_ingredientes = request.form.get('lista_ingredientes').strip()
        receita.modo_preparo = request.form.get('modo_preparo').strip()

        # 1. Tenta pegar a imagem recortada (Base64)
        imagem_base64 = request.form.get('imagem_cortada')
        nova_imagem = salvar_imagem_cortada(imagem_base64, prefixo="receita")

        # 2. Se não cortou, verifica se enviou arquivo comum
        if not nova_imagem:
            file_imagem = request.files.get('imagem_arquivo')
            nova_imagem = salvar_imagem(file_imagem)

        # Se houver nova imagem (cortada ou comum), atualiza
        if nova_imagem:
            receita.imagem_url = nova_imagem

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

# 🗑️ Excluir Receita
@main.route('/receita/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_receita(id):
    receita = Receita.query.get_or_404(id)

    if receita.gastronomos_idgastronomos != current_user.idgastronomos and not current_user.is_admin:
        return redirect(url_for('main.detalhe_receita', id=id))

    AvaliacaoReceita.query.filter_by(receitas_idreceitas=id).delete()
    db.session.delete(receita)
    db.session.commit()
    return redirect(url_for('main.catalogo_receitas'))


# ⭐ Avaliar Receita (Apenas 1 vez por usuário)
@main.route('/receita/<int:id>/avaliar', methods=['POST'])
@login_required
def avaliar_receita(id):
    nota = request.form.get('avaliacoes')
    comentario = request.form.get('comentario', '').strip() or None

    if nota:
        # Busca se o usuário já avaliou esta receita anteriormente
        avaliacao_existente = AvaliacaoReceita.query.filter_by(
            receitas_idreceitas=id,
            gastronomos_idgastronomos=current_user.idgastronomos
        ).first()

        if avaliacao_existente:
            # Atualiza a avaliação já feita (em vez de duplicar)
            avaliacao_existente.avaliacoes = int(nota)
            avaliacao_existente.comentario = comentario
        else:
            # Cria a primeira avaliação do usuário
            nova_avaliacao = AvaliacaoReceita(
                avaliacoes=int(nota),
                comentario=comentario,
                receitas_idreceitas=id,
                gastronomos_idgastronomos=current_user.idgastronomos
            )
            db.session.add(nova_avaliacao)

        db.session.commit()

    return redirect(url_for('main.detalhe_receita', id=id))

# 📸 Rota POST: Atualizar apenas a foto de perfil cortada
@main.route('/perfil/foto', methods=['POST'])
@login_required
def atualizar_foto_perfil():
    foto_base64 = request.form.get('foto_perfil_cortada')
    if foto_base64:
        nova_foto = salvar_imagem_cortada(foto_base64, prefixo="perfil")
        if nova_foto:
            current_user.foto_perfil = nova_foto
            db.session.commit()
            flash('Foto de perfil atualizada com sucesso!', 'success')
    return redirect(url_for('main.perfil'))

# 📂 Listar todas as Pastas do Usuário
@main.route('/pastas')
@login_required
def listar_pastas():
    minhas_pastas = PastaReceitas.query.filter_by(gastronomo_id=current_user.idgastronomos).order_by(PastaReceitas.data_criacao.desc()).all()
    return render_template('pastas.html', pastas=minhas_pastas)


# ➕ Criar Nova Pasta
@main.route('/pastas/nova', methods=['POST'])
@login_required
def criar_pasta():
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()

    if nome:
        nova_pasta = PastaReceitas(
            nome=nome,
            descricao=descricao,
            gastronomo_id=current_user.idgastronomos
        )
        db.session.add(nova_pasta)
        db.session.commit()
        flash(f'Pasta "{nome}" criada com sucesso!', 'success')
    return redirect(url_for('main.listar_pastas'))


# 📖 Ver Receitas dentro de uma Pasta Específica
@main.route('/pastas/<int:id>')
@login_required
def ver_pasta(id):
    pasta = PastaReceitas.query.filter_by(id=id, gastronomo_id=current_user.idgastronomos).first_or_404()
    receitas_formatadas = formatar_receitas(Receita.query.filter(Receita.idreceitas.in_([r.idreceitas for r in pasta.receitas_salvas]))) if pasta.receitas_salvas else []
    return render_template('detalhe_pasta.html', pasta=pasta, receitas=receitas_formatadas)


# 🗑️ Excluir Pasta
@main.route('/pastas/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_pasta(id):
    pasta = PastaReceitas.query.filter_by(id=id, gastronomo_id=current_user.idgastronomos).first_or_404()
    db.session.delete(pasta)
    db.session.commit()
    flash(f'Pasta "{pasta.nome}" excluída.', 'info')
    return redirect(url_for('main.listar_pastas'))


# 📌 Salvar ou Remover Receita de uma Pasta (chamado a partir da página da receita ou da pasta)
@main.route('/receita/<int:receita_id>/salvar-pasta', methods=['POST'])
@login_required
def alternar_salvar_pasta(receita_id):
    pasta_id = request.form.get('pasta_id', type=int)
    pasta = PastaReceitas.query.filter_by(id=pasta_id, gastronomo_id=current_user.idgastronomos).first_or_404()
    receita = Receita.query.get_or_404(receita_id)

    if receita in pasta.receitas_salvas:
        pasta.receitas_salvas.remove(receita)
        flash(f'Receita removida da pasta "{pasta.nome}".', 'info')
    else:
        pasta.receitas_salvas.append(receita)
        flash(f'Receita guardada na pasta "{pasta.nome}"!', 'success')

    db.session.commit()
    return redirect(request.referrer or url_for('main.detalhe_receita', id=receita_id))
from app import create_app, db
from app.models import Gastronomo, Categoria, Receita, AvaliacaoReceita
from werkzeug.security import generate_password_hash

app = create_app()

def popular_banco():
    with app.app_context():
        if Categoria.query.first():
            print("O banco de dados já possui registros!")
            return

        print("Populando o banco de dados com dados de login...")

        # 1. Criar Usuário Comum
        chef = Gastronomo(
            nome="Chef Amazônico",
            email="chef@mangut.com.br",
            telefone="91999999999",
            senha=generate_password_hash("123456"), # Senha segura
            is_admin=False
        )

        # 2. Criar Usuário Administrador (ADM)
        admin = Gastronomo(
            nome="Administrador Mangut",
            email="admin@mangut.com.br",
            telefone="91988888888",
            senha=generate_password_hash("amdin123"),
            is_admin=True
        )

        db.session.add_all([chef, admin])
        db.session.commit()

        # 3. Categorias
        cat_caldos = Categoria(nome="Caldos e Sopas")
        cat_pratos = Categoria(nome="Pratos Principais")
        cat_doces = Categoria(nome="Sobremesas")

        db.session.add_all([cat_caldos, cat_pratos, cat_doces])
        db.session.commit()

        # 4. Receitas
        r1 = Receita(
            nome="Tacacá",
            descricao="Caldo fervente de tucupi com goma de mandioca, folhas de jambu e camarão seco.",
            lista_ingredientes="Tucupi, goma de mandioca, jambu, camarão seco, alho, pimenta-de-cheiro",
            modo_preparo="Cozinhe o tucupi temperado com alho e pimenta. Caldeie as folhas de jambu. Em uma cuia, monte a goma, o tucupi, o jambu e finalize com os camarões.",
            imagem_url="https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=600&q=80",
            gastronomos_idgastronomos=chef.idgastronomos,
            categoria_idcategoria=cat_caldos.idcategoria
        )

        r2 = Receita(
            nome="Maniçoba",
            descricao="Feijoada paraense feita com a maniva (folha de mandioca-brava moída e cozida).",
            lista_ingredientes="Maniva cozida por 7 dias, carne de porco, charque, toucinho, chouriço",
            modo_preparo="Cozinhe a maniva por 7 dias seguidos. Adicione as carnes salgadas e defumadas dessalgadas. Deixe apurar até formar um caldo encorpado e saboroso.",
            imagem_url="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500",
            gastronomos_idgastronomos=chef.idgastronomos,
            categoria_idcategoria=cat_pratos.idcategoria
        )

        db.session.add_all([r1, r2])
        db.session.commit()

        print("Banco populado com sucesso! Usuários criados:")
        print("👤 Usuário Comum: chef@mangut.com.br | Senha: 123456")
        print("👑 Administrador: admin@mangut.com.br | Senha: admin123")

if __name__ == '__main__':
    popular_banco()
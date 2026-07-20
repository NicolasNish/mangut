from app import create_app, db
from app.models import Gastronomo, Categoria, Receita, AvaliacaoReceita

app = create_app()

def popular_banco():
    with app.app_context():
        # Evita duplicar dados caso já existam
        if Categoria.query.first():
            print("O banco de dados já possui registros!")
            return

        print("Populando o banco de dados com receitas nortistas...")

        # 1. Criar um Usuário Gastrônomo inicial
        chef = Gastronomo(
            nome="Chef Amazônico",
            email="chef@mangut.com.br",
            telefone="91999999999",
            senha="pbkdf2:sha256:hash_seguro_aqui"
        )
        db.session.add(chef)
        db.session.commit()

        # 2. Criar Categorias
        cat_caldos = Categoria(nome="Caldos e Sopas")
        cat_pratos = Categoria(nome="Pratos Principais")
        cat_doces = Categoria(nome="Sobremesas")

        db.session.add_all([cat_caldos, cat_pratos, cat_doces])
        db.session.commit()

        # 3. Criar Receitas
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
            gastronomos_idgastronomos=chef.idgastronomos,
            categoria_idcategoria=cat_pratos.idcategoria
        )

        r3 = Receita(
            nome="Pato no Tucupi",
            descricao="Pato assado e cozido em um molho aromático de tucupi e jambu.",
            lista_ingredientes="1 pato inteiro, tucupi, folhas de jambu, chicória da Amazônia, pimenta-de-cheiro",
            modo_preparo="Tempere o pato e asse no forno. Corte em pedaços e termine o cozimento na panela com tucupi e ervas amazônicas. Sirva com jambu e arroz branco.",
            gastronomos_idgastronomos=chef.idgastronomos,
            categoria_idcategoria=cat_pratos.idcategoria
        )

        r4 = Receita(
            nome="Creme de Cupuaçu com Brigadeiro",
            descricao="Sobremesa clássica que equilibra o azedinho do cupuaçu com o doce do chocolate.",
            lista_ingredientes="Polpa de cupuaçu, leite condensado, creme de leite, chocolate em pó",
            modo_preparo="Bata a polpa de cupuaçu com leite condensado e creme de leite até formar um creme homogêneo. Faça um brigadeiro mole e monte em camadas.",
            gastronomos_idgastronomos=chef.idgastronomos,
            categoria_idcategoria=cat_doces.idcategoria
        )

        db.session.add_all([r1, r2, r3, r4])
        db.session.commit()

        # 4. Adicionar Avaliações (Importante para o futuro Sistema de Recomendação)
        a1 = AvaliacaoReceita(avaliacoes=5, comentario="Incomparável! O jambu treme na medida certa.", receitas_idreceitas=r1.idreceitas, gastronomos_idgastronomos=chef.idgastronomos)
        a2 = AvaliacaoReceita(avaliacoes=5, comentario="Prato forte e tradicional, perfeito.", receitas_idreceitas=r2.idreceitas, gastronomos_idgastronomos=chef.idgastronomos)

        db.session.add_all([a1, a2])
        db.session.commit()

        print("Banco de dados populado com sucesso!")

if __name__ == '__main__':
    popular_banco()

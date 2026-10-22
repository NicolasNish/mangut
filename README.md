<div align="center">

  <img src="app/static/img/logo.png" alt="Logo Mangut" width="180">

  # 🌿 Mangut — Sabores e Tradições da Amazônia

  **Plataforma web colaborativa para documentação, compartilhamento e avaliação da culinária tradicional nortista.**

  [![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-2.x%2B-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
  [![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Sobre o Projeto

O **Mangut** nasceu da necessidade de catalogar, valorizar e preservar a rica herança culinária da Amazônia. Mais do que um simples livro de receitas, o sistema atua como uma comunidade colaborativa para **gastrônomos**, cozinheiros amadores e entusiastas da gastronomia nortista.

A aplicação permite aos usuários cadastrar preparos com instruções detalhadas e ingredientes estruturados, carregar e recortar fotos em proporções ideais, avaliar pratos da comunidade sem repetição de votos e organizar suas receitas preferidas em pastas temáticas personalizadas.

---

## ✨ Funcionalidades Principais

- 📖 **Catálogo de Receitas**:
  - Busca textual instantânea por nome da receita ou ingredientes nativos (ex.: jambu, tucupi, pirarucu).
  - Filtro multicategoria suspenso com seleção múltipla via *checkboxes*.
- ⭐ **Sistema de Avaliação**:
  - Cada gastrônomo logado pode avaliar um prato apenas uma vez (restrição por par `usuário-receita`).
  - Média ponderada de estrelas calculada dinamicamente.
  - Comentários opinativos opcionais, com possibilidade de edição ou remoção do próprio voto.
- 📁 **Pastas & Livros de Receitas**:
  - Criação de pastas temáticas (ex.: *"Almoço de Domingo"*, *"Iguarias Típicas"*).
  - Adição e remoção rápida de receitas salvas diretamente da página do prato.
- 👤 **Área do Gastrônomo (Perfil)**:
  - Painel com resumo das receitas publicadas e histórico de avaliações enviadas.
  - Edição de informações pessoais, avatar visualizável em tamanho real e exclusão de conta em cascata.
- 🛡️ **Segurança e Níveis de Acesso (RBAC)**:
  - Hash seguro de senhas com *Werkzeug Security*.
  - Sessões autenticadas via *Flask-Login*.
  - Perfil Administrador (ADM) com permissão para gerenciar, editar ou excluir qualquer conteúdo.
- 📱 **Interface Fluida e Responsiva**:
  - Suporte completo a dispositivos móveis, tablets e monitores desktop.
  - Alternância de tema (*Light Mode* e *Dark Mode* inspirado na floresta noturna).

---

## 🛠️ Tecnologias e Ferramentas

| Camada | Tecnologias Utilizadas |
| :--- | :--- |
| **Back-end** | Python 3, Flask, Flask-Login |
| **Persistência / ORM** | Flask-SQLAlchemy, SQLite |
| **Front-end** | HTML5 Semântico, CSS3 Moderno (Custom Properties, Flexbox, Grid), JavaScript |
| **Bibliotecas Client-Side** | Cropper.js (corte e enquadramento de imagens em Canvas/Base64) |
| **Design & UI** | Google Fonts (Inter), Variáveis CSS com Paleta Temática Amazônica |

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- **Python 3.10** ou superior instalado no computador.
- Gerenciador de pacotes **pip**.
- **Git** configurado.

### 1. Clonar o Repositório
```bash
git clone https://github.com/NicolasNish/mangut.git
cd mangut
```

### 2. Criar e Ativar o Ambiente Virtual
- **No Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- **No Windows (Prompt / PowerShell):**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```

### 3. Instalar as Dependências
```bash
pip install -r requirements.txt
```

> **Nota:** Caso não possua o arquivo `requirements.txt`, as bibliotecas centrais são:
> ```bash
> pip install Flask Flask-SQLAlchemy Flask-Login Pillow
> ```

### 4. Inicializar o Banco de Dados e Dados Iniciais
Execute o script de povoamento para carregar as categorias regionais e as contas administrativas de teste:
```bash
python seed.py
```

### 5. Iniciar o Servidor
```bash
python run.py
```
Acesse o navegador no endereço: **`http://127.0.0.1:5000`**

---

## 🔐 Credenciais de Acesso para Testes

Para testar os níveis de permissão da aplicação:

| Perfil | E-mail | Senha |
| :--- | :--- | :--- |
| **Administrador (ADM)** | `admin@mangut.com.br` | `admin123` |
| **Gastrônomo Padrão** | `joelzito@gmail.com` | `123456` |

---

## 📂 Estrutura de Diretórios

```plaintext
mangut/
├── app/
│   ├── static/
│   │   ├── css/          # Estilização modular e regras responsivas
│   │   ├── js/           # Scripts de interatividade e tema escuro
│   │   ├── img/          # Logomarcas, ícones e avatares da equipe
│   │   └── uploads/      # Armazenamento local das imagens recortadas
│   ├── templates/        # Telas renderizadas via Jinja2 (HTML5)
│   ├── __init__.py       # Inicialização da App Factory e Flask-Login
│   ├── models.py         # Modelagem relacional e tabelas associativas
│   └── routes.py         # Blueprints e controladores das regras de negócio
├── instance/             # Base de dados local SQLite (mangut.db)
├── run.py                # Ponto de entrada para execução da aplicação
├── seed.py               # Script para povoamento de categorias e usuários
├── requirements.txt      # Dependências do projeto
└── README.md             # Documentação do repositório
```

---

## 👥 Autores & Desenvolvedores

* **Nícolas Nishiyama Soares** — *Ciência/Análise de Dados* — [GitHub](https://github.com/NicolasNish)
* **Joel Lima da Silva** — *DBA e Back-end* — [GitHub](https://github.com/JLimadasilva)

---
description: database estrutura
---

## 1. Estrutura de Pastas Obrigatória

Todo projeto DEVE seguir esta estrutura exata:
meu_projeto/
├── src/
│ ├── config/ # Conexões (database.py, api_config.py)
│ ├── models/ # Modelos SQLAlchemy (UserModel.py, ProductModel.py)
│ ├── services/ # Regras de negócio e lógica principal
│ ├── utils/ # Funções auxiliares (formatadores, validadores)
│ ├── analysis/ # Análises de dados (scripts de análise)
│ └── dashboard/ # Dashboards (Streamlit, Dash, ou código do dashboard)
├── data/
│ ├── raw/ # Dados brutos (nunca modificar)
│ ├── processed/ # Dados processados (resultados de análises)
│ └── temp/ # Dados temporários (pode deletar)
├── notebooks/ # Jupyter notebooks para exploração
├── tests/ # Testes unitários
├── .env # Variáveis de ambiente (senhas, chaves)
├── .gitignore # Arquivos ignorados pelo Git
├── requirements.txt # Bibliotecas do projeto (pip freeze)
└── venv/ # Ambiente virtual (NÃO commitar no Git)

text

## 2. Ambiente Virtual (venv) - Regras Obrigatórias

### Regras para o Ambiente Virtual:
- **SEMPRE** use ambiente virtual para cada projeto
- O venv DEVE ficar na RAIZ do projeto, pasta `venv/`
- **NUNCA** commite a pasta `venv/` no Git (já está no .gitignore)
- Todas as dependências DEVEM estar no `requirements.txt`

### Comandos que a IA DEVE saber e ensinar:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Linux/Mac
source venv/bin/activate

# Ativar no Windows
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Congelar dependências (salvar novas)
pip freeze > requirements.txt

# Sair do ambiente virtual
deactivate
Quando a IA for criar ou modificar um projeto:
Primeiro passo: Verificar se o venv existe

Segundo passo: Se não existir, sugerir criar com python -m venv venv

Terceiro passo: Sempre lembrar de ativar o venv antes de instalar pacotes

Quarto passo: Toda nova biblioteca DEVE ser adicionada ao requirements.txt

## 3. SQLAlchemy - Regras Obrigatórias
Sempre que criar código com SQLAlchemy:

Conexão e Sessão
Toda interação com o banco DEVE usar with Session(engine) as session:

A criação do engine fica em src/config/database.py

Os modelos ficam em src/models/

As funções de serviço ficam em src/services/

Exemplo obrigatório
python
from sqlalchemy.orm import Session
from src.config.database import engine

def buscar_dados(user_id: int):
    with Session(engine) as session:
        resultado = session.query(Usuario).filter(Usuario.id == user_id).first()
        return resultado
    # Sessão fechada automaticamente

## 4. Projetos de Análise de Dados - Regras Específicas
Estrutura de Análise
Análises exploratórias ficam em notebooks/

Análises finais/produção ficam em src/analysis/

Dashboards ficam em src/dashboard/

## 5. .gitignore obrigatório
gitignore
venv/
__pycache__/
*.pyc
.env
data/temp/
data/raw/
*.log
.DS_Store
.agent/
.vscode/
.ipynb_checkpoints/
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
6. Regras de Importação (Python)
Sempre use imports absolutos:

python
# Correto
from src.config.database import engine
from src.models.usuario import Usuario
from src.utils.date_utils import formatar_data

# Evitar (imports relativos)
from ..config.database import engine

## 7. Como quero que a IA se comporte
Para banco de dados:
Sempre use with Session(engine) as session:

Explique o código gerado (estou aprendendo)

Comente sobre commit/flush/rollback

Para análise de dados:
Primeiro sugira explorar em notebooks/

Depois refatore para src/analysis/

Por fim crie visualização em src/dashboard/

Para ambiente virtual:
Sempre me lembre de ativar o venv antes de rodar comandos pip

Sempre me lembre de dar pip freeze > requirements.txt quando instalar algo novo

Nunca sugira instalar pacotes sem o venv ativado

## 8. Regra de Documentação de Código
OBRIGATÓRIO: Todo código gerado DEVE ter comentários linha por linha explicando o que acontece.

Exemplo obrigatório:
python
# Busca dados de um usuário no banco
def buscar_dados(user_id: int):
    # Cria uma sessão com o banco usando context manager (with)
    # O 'with' garante que a sessão será fechada automaticamente, mesmo se der erro
    with Session(engine) as session:
        # Faz a query: seleciona todos os campos do modelo Usuario
        # Filtra onde o id é igual ao user_id recebido
        # .first() pega apenas o primeiro resultado (ou None se não existir)
        resultado = session.query(Usuario).filter(Usuario.id == user_id).first()
        # Retorna o resultado encontrado
        return resultado
    # Quando sai do 'with', a sessão é automaticamente fechada
Lembrete para a IA:
Você está me ajudando a APRENDER. Por favor:

Explique os conceitos enquanto escreve código

Aponte boas práticas

Sugira melhorias na organização

SEMPRE me lembre de ativar o ambiente virtual

SEMPRE me lembre de atualizar o requirements.txt

## 9. Dashboard (Dash + Plotly) - Estrutura Obrigatória

Dashboards ficam em `src/dashboard/` com esta estrutura:

src/dashboard/
├── app.py          # Aplicação Dash principal (server, layout root, login)
├── layouts/        # Telas/páginas (ex: home.py, operador.py)
├── callbacks/      # Lógica interativa dos gráficos (ex: graficos_cb.py)
└── components/     # Componentes reutilizáveis (cards, tabelas, headers)

### Regras para Dashboard:
- Gráficos SEMPRE feitos com Plotly
- App SEMPRE feito com Dash
- Login de operador DEVE usar usuários do banco (SQLAlchemy)
- Callbacks ficam SEPARADOS do layout (nunca misturar)
- Instalar: pip install dash plotly dash-auth
- Lembrar: pip freeze > requirements.txt após instalar
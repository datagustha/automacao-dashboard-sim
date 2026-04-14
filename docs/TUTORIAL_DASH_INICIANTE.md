# 🚀 Masterclass: Aprenda Dash e Construa do Zero

Este é o **Guia Definitivo** projetado para que você possa entender o funcionamento interno de um sistema com Dash. Imagine que você está começando com uma planilha vazia de Excel e quer transformá-la no painel em tempo real que você opera hoje.

Aqui ensinaremos como o cérebro (Dash/Python) conversa com o corpo (Layouts Visuais), passo a passo.

---

## 1. As Ferramentas do Construtor (Bibliotecas)
Para criar qualquer dashboard do Zero, você precisa instalar um "Kit" básico de bibliotecas no seu Python:

- **`pandas`**: O matemático. Ele lê arquivos do Excel, banco de dados ou CSV, filtra, agrupa e faz os cálculos antes deles irem para a tela.
- **`dash`**: O maestro. Cria o servidor web, as rotas e toda a lógica de atualização das tabelas.
- **`dash-bootstrap-components (dbc)`**: O design. Ele traz toda a estrutura do formato "Bootstrap" da internet — as colunas virtuais (`dbc.Col`), as linhas estruturadas (`dbc.Row`), abas coloridas e os famosos Cards.
- **`plotly`**: O pintor. O Dash usa os objetos construídos no `plotly.express` para renderizar o design sofisticado dos Gráficos.

---

## 2. A Estrutura do Seu Projeto
Não coloque 10.000 linhas de código no seu `app.py` senão você não conseguirá manter o projeto amanhã. Ao começar um dashboard do zero, crie logo pastas separadas:

1. **`src/`** (A pasta central do projeto)
   - **`dashboard/`** (Tudo visual e da teia de menus)
     - **`layouts/`** (O esqueleto — os arquivos com o desenho de cada página)
     - **`callbacks/`** (Os neurônios — os arquivos com as regras do que altera quando a tela é clicada)
     - **`app.py`** (O roteador principal — apenas carrega os layouts e as URLs)
   - **`services/`** (Funções puras usando apenas Pandas ou queries SQL puxando os dados sujos do Excel/banco).

---

## 3. Lendo Dados e Fazendo Cálculos primeiro (Pandas)
Antes de construir seu robô mecânico, construa a base do pensamento. Use funções dedicadas para ler seu Excel e extrair números antes de invocar o visual do Dash.

```python
# Digamos que isso fique no seu arquivo: /src/services/planilha_service.py
import pandas as pd

def extrair_vendas_do_excel(caminho_arquivo):
    # Lê uma aba do Excel e extrai o Dataframe
    df = pd.read_excel(caminho_arquivo, sheet_name="Relatorio")
    
    # Exemplo: Agrupar por 'Operador' e somar os valores
    agrupado = df.groupby('Operador')['Valor'].sum().reset_index()
    
    # Converter o Pandas de volta para uma Lista Simples ou Dicionário
    return agrupado.to_dict('records') # Agora o Dash consegue usar!
```

---

## 4. O Esqueleto Visual (Layouts)
Os "Layouts" não pensam, não somam os valores do filtro, não chamam banco de dados. Layouts são pedaços rígidos de "esqueleto de tela" que você deixa pre-montado num canto esperando a vida.

A chave mestra para dominar a criação de telas no Dash é uma propriedade mágica: o parâmetro **`id`**. Tudo que for mudar, interagir ou disparar uma ação deve ter um super e exclusivo **nome de ID.**

Veja como montamos a casca visual crua de um projeto onde criamos um Dropdown e uma área em branco que depois será um Gráfico (`dcc.Graph`):

```python
# Arquivo: /src/dashboard/layouts/tela_simples.py
from dash import html, dcc
import dash_bootstrap_components as dbc

def layout_minimo():
    return html.Div([
        # Linha principal
        dbc.Row([
            dbc.Col([
                html.H3("Meu Primeiro Dash", className="text-center mt-3")
            ], width=12)
        ]),

        # Linha dos Filtros
        dbc.Row([
            dbc.Col([
                html.Label("Selecione a Região:"),
                # ID AQUI É O ATIVADOR DO GATILHO:
                dcc.Dropdown(
                    id='dropdown-minha-regiao', 
                    options=[
                        {'label': 'Sul', 'value': 'SUL'},
                        {'label': 'Norte', 'value': 'NORTE'}
                    ],
                    value='SUL' # Região clicada base
                )
            ], width=4)
        ]),

        # Linha Onde o Gráfico Nascerá
        dbc.Row([
            dbc.Col([
                # A tela vai nascer cinza/branca aqui embaixo!
                # E o ID "grafico-vendas-regiao" é nossa porta para jogar o dado nele dps.
                dcc.Graph(id='grafico-vendas-regiao')
            ], width=12)
        ])
    ])
```

---

## 5. Dando Vida (Como funcionam os Callbacks)
O "Callback" é a cola orgânica que conecta o cérebro das funções de cálculo ao corpo passivo das telas de Layouts que aprendemos agora. 

Existem 3 tipos de braços que os Callbacks usam para conversar com a tela:
1. **`Input`**: "Ouvinte". O Gatilho de Disparo! (Ele avisa: *Ei Python, bateram o dedo no seletor de região! Execute tudo de novo agora!*, e manda o valor clicado pra dentro do Python).
2. **`Output`**: O "Atirador". Pra onde as equações que você processou abaixo dessa linha deverão ser cuspidas de volta na tela cega?
3. **`State` (Step, ou Estado)**: O "Espião silencioso". Imagine que você tenha um input de texto onde o usuário digita a "Região". Você não quer que o painel rode os cálculos sempre que ele apertar CADA TECLA do teclado. Então você declara essa barra de texto como State e adiciona um botão como Input! O botão de "Pesquisar" dispara o callback, e apenas nessa fração de segundo crucial, o State "espiona" e puxa silenciosamente a mensagem que o cara já havia deixado preenchida para dentro do cálculo.

```python
# Arquivo: /src/dashboard/callbacks/simples_callbacks.py
from dash.dependencies import Input, Output, State
import plotly.express as px

# Exemplo importando seu arquivo de calculos laurista:
# from src.services.planilha_service import extrair_vendas_do_excel

def registrar_meus_callbacks(app):

    # A MAGIA ACONTECE AQUI -> O Cérebro entende o Esqueleto:
    @app.callback(
        # O Output injeta a equação de volta, dentro do esqueleto do id 'grafico-vendas-regiao', 
        # apontando para o seu atríbuto interno genérico chamado 'figure'
        Output('grafico-vendas-regiao', 'figure'),
        
        # O Input aguarda a porta 'dropdown-minha-regiao' disparar alguma coisa. 
        # Toda vez que a pessoa virar as opções do Dropdown, o parametro 'value' de lá será lido.
        Input('dropdown-minha-regiao', 'value') 
    )
    def re_calcular_grafico(regiao_selecionada):
        # 1. Este bloco inteiro de função roda SOZINHO assim que a opção é alterada na web.
        # A var "regiao_selecionada" agora vale "NORTE" (se a pessoa clicou).

        # 2. Chamamos os Dados (Aqui entrariam os arquivos Excel base)
        dados = [
            {"regiao": "SUL", "operador": "Gustavo", "vendas": 500},
            {"regiao": "NORTE", "operador": "Lucas", "vendas": 800},
            {"regiao": "SUL", "operador": "Amanda", "vendas": 320}
        ]
        import pandas as pd
        df = pd.DataFrame(dados)

        # 3. Matemática cega do Pandas
        df_filtrado = df[df['regiao'] == regiao_selecionada]

        # 4. Construindo o Retrato/Gráfico em Plotly (O Pintor)
        fig = px.bar(df_filtrado, x="operador", y="vendas", color="vendas")

        # 5. Cuspa para a tela! O Python injeta fig no Output('grafico-vendas-regiao', 'figure') instantâneo.
        return fig
```

---

## 6. Navegação e Múltiplas Telas (Roteamento)
Como nós evitamos criar 15 páginas HTML e usar 15 janelas? O Dash recarrega as telinhas "num pino invisível" dentro da mesma página oca inicial.

Para isso o arquivo `app.py` tem o próprio layout mãe com duas tags supremas:
1. Um **`dcc.Location(id='url')`** → Este é o observador mudo que lê a barrinha superior HTTP do navegador.
2. Um container vázio tipo **`html.Div(id='page-content')`** → Será a nossa cesta de refil de páginas inteiras.

Ele faria assim (Callback de Rotas Mestras):
```python
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def checar_onde_a_pessoa_pousou(rota_vazia):
    if rota_vazia == '/pagamentos':
        from src.dashboard.layouts.pagamentos import get_pagamentos_layout
        return get_pagamentos_layout() # Injeta Layout Gigantesco dentro do page-content e aparece do nada.
    
    if rota_vazia == '/operadores':
        from src.dashboard.layouts.operadores import get_operadores_layout
        return get_operadores_layout()
    
    # Se não existe pra onde ir... devolve pra página inicial!
    from src.dashboard.layouts.login import get_login_layout
    return get_login_layout()

```

---

## 7. Como o Sistema "Se Lembra" do Login?
No desenvolvimento Web, nós chamamos as memorias persistentes de de cache local. O Navegador consegue armazenar textos silenciosamente pra você.
No Dash, o nome desta ferramenta genial é **`dcc.Store`**.

No arquivo `app.py` nós adicionamos ao esqueleto master a Tag cega e invisível:
`dcc.Store(id='login-success-store', storage_type='session')`.

Quando o operador entra com a senha "12345", nós verificamos junto aos bancos de dados do SQL ou Excel. Deu certo? Nós não redirecionamos ele por mágica.
1. Nosso Input pega que ele clicou em "Entrar".
2. Consultamos o Banco se o acesso é real.
3. Se for legalizado o acesso, O Dash dá um `Output` que cospe uma maleta com as infos `{"nome": "Gustavo", "perfil": "ADM"}` silenciosamente pro abismo digital do **`dcc.Store`**. 
4. E só então damos um "Refresh" da rota pro painel.
5. Agora em todos, repetindo, em ABSOLUTAMENTE TODOS os painéis do sistema, os nossos callbacks usaram nosso valioso Estado de **`State`** e plugarão `State('login-success-store', 'data')`  no meio de todos seus gatilhos. Ao carregar as tabelas eles sempre roubam um vislumbre do que diabos estiver salvo lá pra descobrir quem é a pessoa que está batendo os dedos no painel agora na internet.

Esses 7 degraus definem qualquer projeto monstruoso de Dash! Nunca se esqueça: crie seus esqueletos com um "id", importe os Dataframes de dados por trás dos panos, e use um Callback pedindo pro `Input` ativar o gatilho, usar seu `State` memorizado de login oculto, e cuspir o gráfico como mágica visual pela janela do `Output`!

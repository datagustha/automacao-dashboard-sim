1. layouts/ - A CARA (o que o usuário VÊ)
python
# layouts/dashboard.py
# Aqui você desenha a tela: onde fica o filtro, onde fica o gráfico, etc.

def get_dashboard_layout():
    return html.Div([
        dcc.Dropdown(id='filtro-fase', ...),  # ← Um filtro aqui
        dcc.Graph(id='grafico-faturamento'),   # ← Um gráfico aqui
        html.H3(id='kpi-faturamento'),         # ← Um número aqui
    ])
O que importa aqui: Os id que você coloca (ex: filtro-fase, grafico-faturamento)

2. callbacks/ - O CÉREBRO (o que ACONTECE)
python
# callbacks/graficos_callbacks.py
# Aqui você diz: QUANDO o usuário fizer algo, FAÇA ISSO.

@app.callback(
    Output('grafico-faturamento', 'figure'),  # ← MUDA o gráfico
    Input('filtro-fase', 'value')             # ← QUANDO o filtro mudar
)
def atualizar_grafico(fase_selecionada):
    # Busca dados, calcula, retorna o gráfico novo
    return figura
O que importa aqui: Os id precisam ser os MESMOS que estão nos layouts!

3. components/ - AS PEÇAS (reutilizáveis)
python
# components/cards.py
# Você cria uma "fábrica" de cards para usar em vários lugares.

def card_indicador(titulo, id_valor):
    return html.Div([
        html.H6(titulo),
        html.H3(id=id_valor)  # ← O id vem de fora
    ])
Depois você usa no layout:

python
# layouts/dashboard.py
card_indicador("Faturamento", "kpi-faturamento")  # ← Passa o id

ONDE CADA COISA É MONTADA?
O app.py é o montador final:
python
# app.py

# 1. Cria o app
app = dash.Dash(__name__)

# 2. Define o layout RAIZ (a estrutura base)
app.layout = html.Div([
    dcc.Location(id='url'),           # ← Controle de URL
    html.Div(id='page-content')       # ← Aqui entra o conteúdo (login, dashboard)
])

# 3. Registra os callbacks (conecta o cérebro)
from src.dashboard.callbacks import auth_callbacks, graficos_callbacks
auth_callbacks.register_callbacks(app)    # ← Conecta os callbacks de login
graficos_callbacks.register_callbacks(app) # ← Conecta os callbacks do dashboard

# 4. Roda o servidor
app.run(debug=True)
O page-content é onde as telas aparecem:
python
# auth_callbacks.py (parte do roteador)

@app.callback(
    Output('page-content', 'children'),  # ← MUDA o conteúdo da página
    Input('url', 'pathname')              # ← QUANDO a URL mudar
)
def render_page(pathname):
    if pathname == '/dashboard':
        return get_dashboard_layout()     # ← MOSTRA o dashboard
    else:
        return get_login_layout()         # ← MOSTRA o login
FLUXO COMPLETO (DESDE O LOGIN ATÉ O GRÁFICO)
text
1. USUÁRIO ABRE O SITE
   ↓
2. URL = "/" → mostra get_login_layout() (tela de login)
   ↓
3. USUÁRIO DIGITA LOGIN E CLICA
   ↓
4. auth_callbacks.py detecta o clique
   ↓
5. Busca no banco, se OK → muda URL para "/dashboard"
   ↓
6. URL mudou → render_page() mostra get_dashboard_layout()
   ↓
7. Tela do dashboard aparece (com filtros, gráficos, cards)
   ↓
8. USUÁRIO SELECIONA UMA FASE no filtro
   ↓
9. graficos_callbacks.py detecta a mudança no 'filtro-fase'
   ↓
10. Busca dados, calcula, retorna novos valores
   ↓
11. Os cards e gráficos atualizam automaticamente
O QUE CADA CALLBACK FAZ (RESUMO)
Arquivo	O que faz	Quando é usado
auth_callbacks.py	Login, logout, roteamento de páginas	Quando o usuário faz login ou sai
graficos_callbacks.py	Atualiza cards, gráfico e tabela do dashboard	Quando o usuário muda filtros ou timer
pgto_callbacks.py	Atualiza a tabela completa da página "Pagamentos"	Quando o usuário está na página de pagamentos
ONDE VOCÊ DEVE MEXER PARA CADA COISA:
O que quer mudar	Onde mexer
Aparência da tela (cores, posições)	layouts/dashboard.py
Opções do filtro (o que aparece no dropdown)	layouts/dashboard.py
O que acontece quando clica em algo	callbacks/graficos_callbacks.py
Como os números são calculados	services/analytics_service.py
Aparência de um card (se usado em vários lugares)	components/cards.py
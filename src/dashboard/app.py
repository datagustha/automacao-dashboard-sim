"""
APLICAÇÃO PRINCIPAL DO DASHBOARD
=================================
Este é o ponto de entrada (entry point) do dashboard.
Inicializa o servidor Dash, configura o layout raiz e registra os callbacks.

COMO EXECUTAR:
    python -m src.dashboard.app
"""

import sys
import os

# ========================================================================
# AJUSTA O CAMINHO DO PYTHON PARA ENCONTRAR O MÓDULO 'src'
# ========================================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ========================================================================
# IMPORTAÇÕES
# ========================================================================
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

# ========================================================================
# INICIALIZA O APP DASH PRINCIPAL
# ========================================================================
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,  # Necessário para layouts dinâmicos
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME # 🌟 Adicionado suporte aos Ícones Profissionais
    ]
)

server = app.server

# ========================================================================
# LAYOUT RAIZ (ROOT LAYOUT)
# ========================================================================
# IMPORTANTE: O Store 'login-success-store' precisa estar AQUI no layout raiz
# para que os callbacks possam acessá-lo antes mesmo de qualquer tela carregar
app.layout = html.Div([
    # Controle de URL (roteamento)
    dcc.Location(id='url', refresh=False),
    
    # Container onde as páginas (login/dashboard) serão renderizadas
    html.Div(id='page-content'),
    
    # ==================================================
    # STORE GLOBAL - GUARDA DADOS DO USUÁRIO LOGADO
    # Este componente fica SEMPRE no layout, mesmo quando a tela muda
    # É invisível e serve para guardar dados entre as páginas
    # ==================================================
    dcc.Store(id='login-success-store', storage_type='memory'),  # ✅ Adicionado globalmente
])

# ========================================================================
# IMPORTA OS CALLBACKS
# ========================================================================
from src.dashboard.callbacks import auth_callbacks, graficos_callbacks, pgto_callbacks

# Registra os callbacks
auth_callbacks.register_callbacks(app)
graficos_callbacks.register_callbacks(app)
pgto_callbacks.register_callbacks(app)

# ========================================================================
# PONTO DE ENTRADA
# ========================================================================
if __name__ == '__main__':
    print("=" * 50)
    print(" INICIANDO DASHBOARD SEMEAR")
    print("=" * 50)
    print(f" Diretorio raiz: {ROOT_DIR}")
    print(f" Acesse: http://127.0.0.1:8050")
    print("=" * 50)
    
    app.run(debug=True, port=8050)
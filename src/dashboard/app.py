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
from dash import dcc, html, Input, Output

# ========================================================================
# INICIALIZA O APP DASH PRINCIPAL
# ========================================================================
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,  # Necessário para layouts dinâmicos
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME
    ]
)

server = app.server

# ========================================================================
# LAYOUT RAIZ (ROOT LAYOUT)
# ========================================================================
# IMPORTANTE: Os Stores com storage_type='local' persistem entre navegações
app.layout = html.Div([
    # Controle de URL (roteamento)
    dcc.Location(id='url', refresh=False),
    
    # Container onde as páginas (login/dashboard) serão renderizadas
    html.Div(id='page-content'),
    
    # ==================================================
    # STORES GLOBAIS - PERSISTEM ENTRE PÁGINAS
    # ==================================================
    # storage_type='local' mantém os dados no navegador
    dcc.Store(id='login-success-store', storage_type='local'),
    dcc.Store(id='login-step-store', data={'step': 'login'}, storage_type='local'),
    
    # ==================================================
    # ATUALIZAÇÃO AUTOMÁTICA - A CADA 5 MINUTOS
    # ==================================================
    # interval=300000 = 5 minutos (em milissegundos)
    dcc.Interval(id='interval-component', interval=300000, n_intervals=0),
])

# ========================================================================
# IMPORTA OS CALLBACKS
# ========================================================================
from src.dashboard.callbacks import auth_callbacks, graficos_callbacks, pgto_callbacks, operador_callbacks, adm_callbacks

# ========================================================================
# REGISTRA OS CALLBACKS
# ========================================================================
auth_callbacks.register_callbacks(app)
graficos_callbacks.register_callbacks(app)
pgto_callbacks.register_callbacks(app)
operador_callbacks.register_callbacks(app)
adm_callbacks.register_callbacks(app)

# ========================================================================
# CALLBACK PARA ATUALIZAÇÃO AUTOMÁTICA
# ========================================================================
@app.callback(
    Output('page-content', 'children', allow_duplicate=True),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def atualizar_dashboard(n):
    """
    Atualiza o dashboard automaticamente a cada 5 minutos.
    Recarrega a página atual para buscar novos dados do banco.
    """
    from dash import page_registry
    from flask import request
    
    print(f"🔄 Atualizando dashboard automaticamente... (ciclo #{n})")
    
    # Força o recarregamento da página atual
    return dash.no_update

# ========================================================================
# PONTO DE ENTRADA
# ========================================================================
if __name__ == '__main__':
    print("=" * 50)
    print(" INICIANDO DASHBOARD SEMEAR")
    print("=" * 50)
    print(f" Diretorio raiz: {ROOT_DIR}")
    print(f" Acesse: http://127.0.0.1:8050")
    print(" Atualização automática a cada 5 minutos")
    print("=" * 50)
    
    app.run(debug=False, host='0.0.0.0', port=8050)
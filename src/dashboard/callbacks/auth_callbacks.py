"""
ROTEADOR E CONTROLE DE AUTENTICAÇÃO
====================================
Lê o "Caminho da URL" e decide que aba do sistema você vai visualizar.
"""

import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import html

from src.dashboard.layouts.login import get_login_layout
from src.dashboard.layouts.dashboard import get_dashboard_layout
from src.dashboard.layouts.pagamentos import get_pagamentos_layout
from src.services.db_service import Buscar_login

def register_callbacks(app: dash.Dash):

    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        [State('login-success-store', 'data')]
    )
    def render_page(pathname, login_dados):
        """
        Multipage Router!
        Avalia se tem autorização para o dashboard ou para a tela de pagamentos.
        """
        
        checado = False
        if login_dados and 'nome' in login_dados:
            checado = True
            imagem_usuario = login_dados.get('imagem', None)
            nome_usuario = login_dados['nome']
        
        # Rotas Protegidas     
        if pathname == '/dashboard':
            if checado: return get_dashboard_layout(nome_usuario, imagem_usuario)
            return dbc.Alert("❌ Você precisa estar logado.", color="danger")
            
        elif pathname == '/pagamentos':
            if checado: return get_pagamentos_layout(nome_usuario, imagem_usuario)
            return dbc.Alert("❌ Você precisa estar logado.", color="danger")

        # Fallback de Segurança
        return get_login_layout()

    # === Login Logic ===
    @app.callback(
        [
            Output('login-success-store', 'data'),
            Output('login-mensagem-erro', 'children'),
            Output('url', 'pathname', allow_duplicate=True)
        ],
        [Input('login-button', 'n_clicks')],
        [State('login-user-input', 'value')],
        prevent_initial_call=True
    )
    def tentar_login(n_clicks, valor_login):
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate
        
        if not valor_login:
            return None, "⚠️ Por favor, digite um login", dash.no_update
        
        usuario = Buscar_login(valor_login)
        if usuario:
            dados_usuario = {
                'nome': usuario['nome'],
                'login': usuario['login'],
                'imagem': usuario.get('imagem', None)
            }
            return dados_usuario, "", "/dashboard"
        else:
            return None, "❌ Login inválido. Tente novamente.", dash.no_update

    # === LOGOUT ===
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [Input('logout-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def fazer_logout(n_clicks):
        if n_clicks:
            return "/"
        raise PreventUpdate
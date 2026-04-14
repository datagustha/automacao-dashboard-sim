"""
CALLBACKS DE AUTENTICAÇÃO - VERSÃO COMPLETA
============================================
"""

import dash
import os
import json
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import dcc, html

from src.dashboard.layouts.login import get_login_layout
from src.dashboard.layouts.dashboard import get_dashboard_layout
from src.dashboard.layouts.dashboard_adm import get_dashboard_adm_layout
from src.dashboard.layouts.pagamentos import get_pagamentos_layout
from src.dashboard.layouts.operador_detalhe import get_operador_detalhe_layout

from src.services.db_service import Buscar_login
from src.services.auth_service import (
    operador_tem_senha, obter_email_operador, gerar_token_numerico,
    salvar_token, validar_token, salvar_senha
)
from src.services.email_service import enviar_token_email

# ================================================================
# CAMINHO DO ARQUIVO PARA SALVAR ÚLTIMO LOGIN
# ================================================================
ULTIMO_LOGIN_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'ultimo_login.json')


def register_callbacks(app):
    """
    Registra todos os callbacks de autenticação no aplicativo Dash.
    """

    # ================================================================
    # CALLBACK 1: ROTEADOR DE PÁGINAS (render_page)
    # ================================================================
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        [State('login-success-store', 'data')]
    )
    def render_page(pathname, login_dados):
        """
        FUNÇÃO ROTEADOR - Decide qual tela mostrar baseado na URL.
        """
        
        # ============================================================
        # ROTA: DASHBOARD
        # ============================================================
        if pathname == '/dashboard':
            if login_dados and 'nome' in login_dados:
                perfil = login_dados.get('perfil', 'operador')
                banco  = login_dados.get('banco', 'SEMEAR')
                if perfil == 'adm':
                    # ADM → layout com dois bancos
                    return get_dashboard_adm_layout(login_dados['nome'], login_dados.get('imagem'))
                else:
                    # Operador → layout individual, passa banco para controle de fase
                    return get_dashboard_layout(login_dados['nome'], login_dados.get('imagem'), banco=banco)
            return dbc.Alert("❌ Você precisa estar logado.", color="danger")

        # ============================================================
        # ROTA: PAGAMENTOS
        # ============================================================
        elif pathname == '/pagamentos':
            if login_dados and 'nome' in login_dados:
                perfil = login_dados.get('perfil', 'operador')
                return get_pagamentos_layout(
                    login_dados['nome'],
                    login_dados.get('imagem'),
                    perfil=perfil
                )
            
            if os.path.exists(ULTIMO_LOGIN_FILE):
                try:
                    with open(ULTIMO_LOGIN_FILE, 'r') as f:
                        data = json.load(f)
                        ultimo_login = data.get('login')
                        if ultimo_login:
                            operador = Buscar_login(ultimo_login)
                            if operador:
                                perfil = 'adm' if operador.get('banco', '').upper() == 'ADM' else 'operador'
                                return get_pagamentos_layout(operador['nome'], operador.get('imagem'), perfil=perfil)
                except:
                    pass
            
            return dbc.Alert("❌ Você precisa estar logado.", color="danger")

        # ============================================================
        # ROTA: OPERADORES (ADM consolida ou seleciona)
        # ============================================================
        elif pathname.startswith('/operadores'):
            partes = pathname.strip('/').split('/')
            banco = "SEMEAR"
            login_alvo = "TODOS"
            
            if len(partes) >= 2:
                banco = partes[1].upper()
            if len(partes) >= 3:
                login_alvo = partes[2]
                
            if login_dados and 'nome' in login_dados:
                perfil = login_dados.get('perfil', 'operador')
                if perfil == 'adm':
                    if login_alvo == "TODOS":
                        op_data = {"login": "TODOS", "banco": banco}
                    else:
                        op_banco = Buscar_login(login_alvo)
                        op_data = op_banco if op_banco else {"login": "TODOS", "banco": banco}
                        
                    return get_operador_detalhe_layout(
                        nome_usuario=login_dados['nome'],
                        imagem_url=login_dados.get('imagem'),
                        operador_selecionado=op_data,
                        banco=banco,
                        is_adm=True
                    )
                else:
                    return dcc.Location(href=f"/operador/{login_dados['login']}", id="redirect")
            return dcc.Location(href="/", id="redirect")

        # ============================================================
        # ROTA: DETALHE DO OPERADOR
        # ============================================================
        elif pathname.startswith('/operador/'):
            operador_login = pathname.split('/')[-1]
            operador = Buscar_login(operador_login)
            if operador:
                nome_logado = login_dados['nome'] if login_dados else operador['nome']
                imagem_logado = login_dados.get('imagem') if login_dados else operador.get('imagem')
                
                return get_operador_detalhe_layout(
                    nome_logado,
                    imagem_logado,
                    operador,
                    operador.get('banco', 'SEMEAR')
                )
            return dbc.Alert("❌ Operador não encontrado.", color="danger")

        # ============================================================
        # ROTA PADRÃO: TELA DE LOGIN
        # ============================================================
        return get_login_layout()
    
    
    # ================================================================
    # CALLBACK 2: GERENCIAR FLUXO DE LOGIN
    # ================================================================
    @app.callback(
        [
            Output('login-success-store', 'data'),
            Output('login-mensagem-erro', 'children'),
            Output('login-info-mensagem', 'children'),
            Output('login-password-input', 'style'),
            Output('login-token-input', 'style'),
            Output('login-nova-senha-input', 'style'),
            Output('login-confirma-senha-input', 'style'),
            Output('login-button', 'children'),
            Output('login-step-store', 'data'),
            Output('url', 'pathname', allow_duplicate=True)
        ],
        [
            Input('login-button', 'n_clicks'),
            Input('btn-esqueci-senha', 'n_clicks')
        ],
        [
            State('login-user-input', 'value'),
            State('login-password-input', 'value'),
            State('login-token-input', 'value'),
            State('login-nova-senha-input', 'value'),
            State('login-confirma-senha-input', 'value'),
            State('login-step-store', 'data')
        ],
        prevent_initial_call=True
    )
    def gerenciar_autenticacao(n_clicks_login, n_clicks_esqueci, 
                                login, senha, token, nova_senha, confirma_senha,
                                step_store):
        """
        FUNÇÃO PRINCIPAL DE AUTENTICAÇÃO.
        """
        
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id not in ['login-button', 'btn-esqueci-senha']:
            raise PreventUpdate
        
        # ============================================================
        # BOTÃO "ESQUECI MINHA SENHA"
        # ============================================================
        if trigger_id == 'btn-esqueci-senha':
            if not login:
                return (None, "Digite seu login primeiro", "", 
                        {"display": "none"}, {"display": "none"}, 
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", step_store, dash.no_update)
            
            email = obter_email_operador(login)
            if not email:
                return (None, "Login não encontrado ou e-mail não cadastrado", "", 
                        {"display": "none"}, {"display": "none"}, 
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", step_store, dash.no_update)
            
            token_num = gerar_token_numerico()
            salvar_token(login, token_num, "reset_senha")
            enviar_token_email(email, login, token_num, "reset_senha")
            
            return (None, "", f"📧 Código enviado para {email}",
                    {"display": "none"}, {"display": "block"}, 
                    {"display": "none"}, {"display": "none"},
                    "Validar Token", {'step': 'validar_token_reset', 'login': login}, 
                    dash.no_update)
        
        # ============================================================
        # VALIDAÇÕES INICIAIS
        # ============================================================
        if not login:
            return (None, "Digite seu login", "", 
                    {"display": "none"}, {"display": "none"}, 
                    {"display": "none"}, {"display": "none"}, 
                    "Entrar", step_store, dash.no_update)
        
        operador = Buscar_login(login)
        if not operador:
            return (None, "Login não encontrado", "", 
                    {"display": "none"}, {"display": "none"}, 
                    {"display": "none"}, {"display": "none"}, 
                    "Entrar", step_store, dash.no_update)
        
        # Salva o último login em arquivo para recuperação
        try:
            with open(ULTIMO_LOGIN_FILE, 'w') as f:
                json.dump({'login': login, 'nome': operador['nome']}, f)
        except:
            pass
        
        # ============================================================
        # RESETAR STEP SE FOR UM NOVO LOGIN (evita step pendente)
        # ============================================================
        if step_store and step_store.get('login') != login:
            step_store = {'step': 'login'}
        
        # Garante que step_store tem valor padrão
        if step_store is None:
            step_store = {'step': 'login'}
        
        step = step_store.get('step', 'login')
        
        # ============================================================
        # LOGIN (verificar se tem senha)
        # ============================================================
        if step == 'login':
            if operador_tem_senha(login):
                return (None, "", "Digite sua senha", 
                        {"display": "block"}, {"display": "none"}, 
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", {'step': 'validar_senha', 'login': login}, 
                        dash.no_update)
            else:
                email = obter_email_operador(login)
                if not email:
                    return (None, "E-mail não cadastrado", "", 
                            {"display": "none"}, {"display": "none"}, 
                            {"display": "none"}, {"display": "none"}, 
                            "Entrar", step_store, dash.no_update)
                
                token_num = gerar_token_numerico()
                salvar_token(login, token_num, "primeiro_acesso")
                enviar_token_email(email, login, token_num, "primeiro_acesso")
                
                return (None, "", f"📧 Código enviado para {email}",
                        {"display": "none"}, {"display": "block"}, 
                        {"display": "none"}, {"display": "none"},
                        "Validar Token", {'step': 'validar_token_primeiro', 'login': login}, 
                        dash.no_update)
        
        # ============================================================
        # VALIDAR SENHA
        # ============================================================
        elif step == 'validar_senha':
            # VERIFICA SE A SENHA FOI DIGITADA
            if not senha:
                return (None, "Digite sua senha", "", 
                        {"display": "block"}, {"display": "none"}, 
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", step_store, dash.no_update)
            
            from src.services.auth_service import verificar_senha
            from sqlalchemy.orm import Session
            from src.config.database import engine
            from src.models.LoginModel import analistas
            
            with Session(engine) as session:
                user = session.query(analistas).filter(
                    analistas.loguin == login
                ).first()
                
                if not user or not user.senha_hash:
                    return (None, "Erro: senha não encontrada", "", 
                            {"display": "block"}, {"display": "none"}, 
                            {"display": "none"}, {"display": "none"}, 
                            "Entrar", step_store, dash.no_update)
                
                if verificar_senha(user.senha_hash, senha):
                    banco_op = operador.get('banco', 'SEMEAR')
                    perfil_op = 'adm' if banco_op.upper() == 'ADM' else 'operador'
                    dados_usuario = {
                        'nome': operador['nome'],
                        'login': operador['login'],
                        'imagem': operador.get('imagem'),
                        'banco': banco_op,
                        'perfil': perfil_op
                    }
                    return (dados_usuario, "", "", 
                            {"display": "none"}, {"display": "none"}, 
                            {"display": "none"}, {"display": "none"}, 
                            "Entrar", step_store, "/dashboard")
                else:
                    return (None, "Senha incorreta", "", 
                            {"display": "block"}, {"display": "none"}, 
                            {"display": "none"}, {"display": "none"}, 
                            "Entrar", step_store, dash.no_update)
        
        # ============================================================
        # VALIDAR TOKEN
        # ============================================================
        elif step in ['validar_token_primeiro', 'validar_token_reset']:
            if not token:
                return (None, "Digite o código recebido", "", 
                        {"display": "none"}, {"display": "block"}, 
                        {"display": "none"}, {"display": "none"}, 
                        "Validar Token", step_store, dash.no_update)
            
            tipo = 'primeiro_acesso' if step == 'validar_token_primeiro' else 'reset_senha'
            
            if validar_token(login, token, tipo):
                return (None, "", "Token válido! Crie sua senha",
                        {"display": "none"}, {"display": "none"}, 
                        {"display": "block"}, {"display": "block"},
                        "Criar Senha", {'step': 'criar_senha', 'login': login}, 
                        dash.no_update)
            else:
                return (None, "Token inválido ou expirado", "", 
                        {"display": "none"}, {"display": "block"}, 
                        {"display": "none"}, {"display": "none"}, 
                        "Validar Token", step_store, dash.no_update)
        
        # ============================================================
        # CRIAR NOVA SENHA
        # ============================================================
        elif step == 'criar_senha':
            if not nova_senha or not confirma_senha:
                return (None, "Preencha ambos os campos", "", 
                        {"display": "none"}, {"display": "none"}, 
                        {"display": "block"}, {"display": "block"}, 
                        "Criar Senha", step_store, dash.no_update)
            
            if nova_senha != confirma_senha:
                return (None, "As senhas não coincidem", "", 
                        {"display": "none"}, {"display": "none"}, 
                        {"display": "block"}, {"display": "block"}, 
                        "Criar Senha", step_store, dash.no_update)
            
            if len(nova_senha) < 4:
                return (None, "Mínimo 4 caracteres", "", 
                        {"display": "none"}, {"display": "none"}, 
                        {"display": "block"}, {"display": "block"}, 
                        "Criar Senha", step_store, dash.no_update)
            
            if salvar_senha(login, nova_senha):
                operador = Buscar_login(login)
                banco_op = operador.get('banco', 'SEMEAR')
                perfil_op = 'adm' if banco_op.upper() == 'ADM' else 'operador'
                dados_usuario = {
                    'nome': operador['nome'],
                    'login': operador['login'],
                    'imagem': operador.get('imagem'),
                    'banco': banco_op,
                    'perfil': perfil_op
                }
                return (dados_usuario, "Senha criada com sucesso!", "", 
                        {"display": "none"}, {"display": "none"}, 
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", {'step': 'login'}, "/dashboard")
            else:
                return (None, "Erro ao salvar senha", "", 
                        {"display": "none"}, {"display": "none"}, 
                        {"display": "block"}, {"display": "block"}, 
                        "Criar Senha", step_store, dash.no_update)
        
        # ============================================================
        # FALLBACK
        # ============================================================
        return (None, "Erro no fluxo de autenticação", "", 
                {"display": "none"}, {"display": "none"}, 
                {"display": "none"}, {"display": "none"}, 
                "Entrar", step_store, dash.no_update)
    
    
    # ================================================================
    # CALLBACK 3: LOGOUT
    # ================================================================
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [Input('logout-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def fazer_logout(n_clicks):
        """FAZ LOGOUT - Redireciona para a tela de login."""
        if n_clicks:
            try:
                if os.path.exists(ULTIMO_LOGIN_FILE):
                    os.remove(ULTIMO_LOGIN_FILE)
            except:
                pass
            return "/"
        raise PreventUpdate
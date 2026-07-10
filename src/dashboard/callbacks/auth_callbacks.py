"""
CALLBACKS DE AUTENTICAÇÃO - VERSÃO COMPLETA COM 2FA
===================================================
Gerencia todo o fluxo de autenticação:
  - Callback 1: Roteador de páginas (decide qual layout renderizar)
  - Callback 2: Fluxo de login completo (login → senha → 2FA → dashboard)
  - Callback 3: Logout completo (limpa Stores + redireciona)

🔧 CORREÇÃO APLICADA:
  - Bug: step_store resetava para 'login' quando o login do store estava em
    caixa diferente do login digitado, derrubando o fluxo 2FA mesmo com
    código correto.
  - Fix: comparação agora é case-insensitive (.upper().strip()) na linha
    que verifica se o login mudou.
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
    salvar_token, validar_token, salvar_senha,
    # 🔥 NOVOS IMPORTS PARA 2FA
    salvar_token_2fa, validar_token_2fa
)
from src.services.email_service import enviar_token_email, enviar_token_2fa_email



def register_callbacks(app):
    """
    Registra todos os callbacks de autenticação no aplicativo Dash.
    """

    # ================================================================
    # CALLBACK 1: ROTEADOR DE PÁGINAS (render_page)
    # ================================================================
    @app.callback(
        Output('page-content', 'children'),
        [
            Input('url', 'pathname'),
            Input('login-success-store', 'data')
        ]
    )
    def render_page(pathname, login_dados):
        """ROTEADOR PRINCIPAL"""
        ctx = dash.callback_context

        # 1. DEFINIÇÃO DE ROTAS PROTEGIDAS
        rotas_protegidas = ['/dashboard', '/pagamentos', '/operadores']
        is_protegida = any(pathname.startswith(r) for r in rotas_protegidas if pathname)

        # 2. SE NÃO ESTIVER LOGADO...
        if not login_dados or 'nome' not in login_dados:
            # Se é a carga inicial e a URL é protegida, pode ser que o localStorage
            # ainda não terminou de carregar — mostramos uma tela de loading
            # para evitar o flash da tela de login antes do store ser lido.
            triggered_ids = [t['prop_id'] for t in ctx.triggered] if ctx.triggered else []
            only_store_fired = triggered_ids == ['login-success-store.data']
            if not triggered_ids or only_store_fired:
                if is_protegida:
                    # Tela de espera minimalista — dura apenas um ciclo de render
                    return html.Div(
                        html.Div(
                            [
                                html.Div(className="spinner-border text-primary", role="status",
                                         style={"width": "3rem", "height": "3rem"}),
                                html.P("Carregando...", className="mt-3 text-muted fw-semibold")
                            ],
                            className="d-flex flex-column align-items-center justify-content-center",
                            style={"minHeight": "100vh"}
                        )
                    )
            # Se tentar acessar algo protegido, força Login
            if is_protegida:
                return get_login_layout()
            # Se estiver na raiz ou qualquer outro lugar, mostra Login
            return get_login_layout()




        # 3. USUÁRIO LOGADO...
        # Obtém o perfil do usuário logado (ex: 'adm' ou 'operador')
        perfil = login_dados.get('perfil', 'operador')
        # Obtém o banco ativo do operador (ex: 'SEMEAR' ou 'AGORACRED')
        banco  = login_dados.get('banco', 'SEMEAR')
        # Obtém o nome completo do operador logado
        nome   = login_dados.get('nome')
        # Obtém a foto (imagem de perfil) do operador
        imagem = login_dados.get('imagem')
        # Obtém a data de admissão gravada na sessão
        admissao = login_dados.get('admissao')
        
        # Se a data de admissão não estiver nos dados da sessão (ex: login antigo)
        if not admissao:
            # Busca os dados do operador no banco de dados como fallback
            op_dados = Buscar_login(login_dados.get('login'))
            # Se o operador for localizado no banco
            if op_dados:
                # Recupera a data de admissão cadastrada no banco
                admissao = op_dados.get('admissao')

        # --- ROTA: RAIZ (se logado, vai pro dashboard) ---
        if pathname in ['/', None]:
            # Se o perfil for administrador
            if perfil == 'adm':
                # Retorna o layout do dashboard de administrador passando admissao
                return get_dashboard_adm_layout(nome, imagem, admissao=admissao)
            else:
                # Retorna o layout do operador comum passando admissao e o banco
                return get_dashboard_layout(nome, imagem, banco=banco, admissao=admissao)

        # --- ROTA: DASHBOARD ---
        elif pathname == '/dashboard':
            # Se o perfil for administrador
            if perfil == 'adm':
                # Retorna o layout do dashboard de administrador passando admissao
                return get_dashboard_adm_layout(nome, imagem, admissao=admissao)
            else:
                # Retorna o layout do operador comum passando admissao e o banco
                return get_dashboard_layout(nome, imagem, banco=banco, admissao=admissao)

        # --- ROTA: PAGAMENTOS ---
        elif pathname == '/pagamentos':
            # Retorna o layout de pagamentos passando admissao e o perfil correspondente
            return get_pagamentos_layout(nome, imagem, perfil=perfil, admissao=admissao)

        # --- ROTA: OPERADORES ---
        elif pathname.startswith('/operadores'):
            # Se o usuário logado NÃO for administrador
            if perfil != 'adm':
                # Operador vê APENAS seu próprio detalhe de produção (passando seus dados de sessão)
                op_data = {"login": login_dados.get('login'), "banco": banco, "nome": nome, "imagem": imagem, "admissao": admissao}
                # Retorna o layout de detalhe do operador passando admissao
                return get_operador_detalhe_layout(
                    nome_usuario=nome,
                    imagem_url=imagem,
                    operador_selecionado=op_data,
                    banco=banco,
                    is_adm=False
                )
            else:
                # ADM tem acesso à tela com filtros de banco, atividade e operador
                partes = pathname.strip('/').split('/')
                # Define o banco alvo a ser visualizado
                banco_alvo = partes[1].upper() if len(partes) >= 2 else "SEMEAR"
                # Define o login do operador alvo a ser visualizado
                login_alvo = partes[2]         if len(partes) >= 3 else "TODOS"
                
                # Se for selecionado "TODOS" os operadores
                if login_alvo == "TODOS":
                    # Cria dados gerais do operador contendo TODOS e o banco correspondente
                    op_data = {"login": "TODOS", "banco": banco_alvo}
                else:
                    # Busca os dados do operador no banco de dados pelo login
                    op_banco = Buscar_login(login_alvo)
                    # Se localizado, usa os dados do banco. Senha e demais campos nao sao afetados.
                    op_data  = op_banco if op_banco else {"login": "TODOS", "banco": banco_alvo}
                    
                # Retorna o detalhe do operador indicando is_adm=True
                return get_operador_detalhe_layout(
                    nome_usuario=nome,
                    imagem_url=imagem,
                    operador_selecionado=op_data,
                    banco=banco_alvo,
                    is_adm=True
                )

        # --- ROTA: DETALHE DO OPERADOR (Vista Individual) ---
        elif pathname.startswith('/operador/'):
            # Obtem o login do operador a partir da URL
            operador_login = pathname.split('/')[-1]
            # Busca os dados desse operador no banco de dados
            operador = Buscar_login(operador_login)
            # Se encontrar o operador
            if operador:
                # Retorna o layout de detalhe do operador com seus respectivos dados
                return get_operador_detalhe_layout(nome, imagem, operador, operador.get('banco', 'SEMEAR'))
            # Caso contrário, mostra alerta de não encontrado
            return dbc.Alert("Erro: Operador nao encontrado.", color="danger")

        # --- FALLBACK: Se a rota não existir mas está logado, volta pro Dashboard ---
        # Se for administrador
        if perfil == 'adm':
            # Retorna o dashboard administrativo correspondente
            return get_dashboard_adm_layout(nome, imagem, admissao=admissao)
        # Se for operador comum, retorna o dashboard do operador correspondente
        return get_dashboard_layout(nome, imagem, banco=banco, admissao=admissao)



    
    
    # ================================================================
    # CALLBACK 2: GERENCIAR FLUXO DE LOGIN (COM 2FA)
    # ================================================================
    @app.callback(
        [
            Output('login-success-store', 'data'),
            Output('login-mensagem-erro', 'children'),
            Output('login-info-mensagem', 'children'),
            Output('login-password-input', 'style'),
            Output('login-token-input', 'style'),
            Output('login-2fa-input', 'style'),  # 🔥 NOVO: campo 2FA
            Output('login-nova-senha-input', 'style'),
            Output('login-confirma-senha-input', 'style'),
            Output('login-button', 'children'),
            Output('login-step-store', 'data'),
            Output('url', 'pathname', allow_duplicate=True)
        ],
        [
            Input('login-button', 'n_clicks'),
            Input('login-user-input', 'n_submit'),
            Input('login-password-input', 'n_submit'),
            Input('login-token-input', 'n_submit'),
            Input('login-2fa-input', 'n_submit'),  # 🔥 NOVO: ENTER no 2FA
            Input('login-nova-senha-input', 'n_submit'),
            Input('login-confirma-senha-input', 'n_submit'),
            Input('btn-esqueci-senha', 'n_clicks')
        ],
        [
            State('login-user-input', 'value'),
            State('login-password-input', 'value'),
            State('login-token-input', 'value'),
            State('login-2fa-input', 'value'),  # 🔥 NOVO: valor do 2FA
            State('login-nova-senha-input', 'value'),
            State('login-confirma-senha-input', 'value'),
            State('login-step-store', 'data')
        ],
        prevent_initial_call=True
    )
    def gerenciar_autenticacao(n_clicks_login, n_submit_login, n_submit_senha, 
                                n_submit_token, n_submit_2fa, n_submit_nova, n_submit_confirma,
                                n_clicks_esqueci, 
                                login, senha, token, codigo_2fa, nova_senha, confirma_senha,
                                step_store):
        """
        FUNÇÃO PRINCIPAL DE AUTENTICAÇÃO COM 2FA.
        - Suporta ENTER em qualquer campo
        - 🔥 Converte login para MAIÚSCULO
        - 🔥 NOVO: 2FA após senha correta
        """
        
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # ============================================================
        # 🔥 CONVERTER LOGIN PARA MAIÚSCULO
        # ============================================================
        if login:
            login = login.upper().strip()

        # ============================================================
        # BOTÃO "ESQUECI MINHA SENHA"
        # ============================================================
        if trigger_id == 'btn-esqueci-senha':
            if not login:
                return (dash.no_update, "Digite seu login primeiro", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", step_store, dash.no_update)
            
            email = obter_email_operador(login)
            if not email:
                return (dash.no_update, "Login não encontrado ou e-mail não cadastrado", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", step_store, dash.no_update)
            
            token_num = gerar_token_numerico()
            salvar_token(login, token_num, "reset_senha")
            enviar_token_email(email, login, token_num, "reset_senha")
            
            return (dash.no_update, "", f"📧 Código enviado para {email}",
                    {"display": "none"}, {"display": "block"}, {"display": "none"},
                    {"display": "none"}, {"display": "none"},
                    "Validar Token", {'step': 'validar_token_reset', 'login': login}, 
                    dash.no_update)
        
        # ============================================================
        # VALIDAÇÕES INICIAIS
        # ============================================================
        if not login:
            return (dash.no_update, "Digite seu login", "", 
                    {"display": "none"}, {"display": "none"}, {"display": "none"},
                    {"display": "none"}, {"display": "none"}, 
                    "Entrar", step_store, dash.no_update)
        
        operador = Buscar_login(login)
        if not operador:
            return (dash.no_update, "Login não encontrado", "", 
                    {"display": "none"}, {"display": "none"}, {"display": "none"},
                    {"display": "none"}, {"display": "none"}, 
                    "Entrar", step_store, dash.no_update)
        
        # ============================================================
        # RESETAR STEP SE FOR UM NOVO LOGIN
        # 🔧 CORREÇÃO: comparação case-insensitive para não resetar o
        #    fluxo 2FA quando o login vier com capitalização diferente.
        # ============================================================
        if step_store and step_store.get('login', '').upper().strip() != login:
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
                return (dash.no_update, "", "Digite sua senha", 
                        {"display": "block"}, {"display": "none"}, {"display": "none"},
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", {'step': 'validar_senha', 'login': login}, 
                        dash.no_update)
            else:
                email = obter_email_operador(login)
                if not email:
                    return (dash.no_update, "E-mail não cadastrado", "", 
                            {"display": "none"}, {"display": "none"}, {"display": "none"},
                            {"display": "none"}, {"display": "none"}, 
                            "Entrar", step_store, dash.no_update)
                
                token_num = gerar_token_numerico()
                salvar_token(login, token_num, "primeiro_acesso")
                enviar_token_email(email, login, token_num, "primeiro_acesso")
                
                return (dash.no_update, "", f"📧 Código enviado para {email}",
                        {"display": "none"}, {"display": "block"}, {"display": "none"},
                        {"display": "none"}, {"display": "none"},
                        "Validar Token", {'step': 'validar_token_primeiro', 'login': login}, 
                        dash.no_update)
        
        # ============================================================
        # VALIDAR SENHA
        # ============================================================
        elif step == 'validar_senha':
            if not senha:
                return (dash.no_update, "Digite sua senha", "", 
                        {"display": "block"}, {"display": "none"}, {"display": "none"},
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
                    return (dash.no_update, "Erro: senha não encontrada", "", 
                            {"display": "block"}, {"display": "none"}, {"display": "none"},
                            {"display": "none"}, {"display": "none"}, 
                            "Entrar", step_store, dash.no_update)
                
                if verificar_senha(user.senha_hash, senha):
                    # 🔥 SENHA CORRETA! Agora verifica 2FA
                    # Gera token 2FA
                    token_2fa = gerar_token_numerico(6)
                    
                    # Salva no banco
                    salvar_token_2fa(login, token_2fa)
                    
                    # Envia por email
                    email = obter_email_operador(login)
                    if email:
                        enviar_token_2fa_email(email, login, token_2fa)
                    
                    return (dash.no_update, "", f"📱 Código 2FA enviado para seu e-mail!",
                            {"display": "none"}, {"display": "none"}, {"display": "block"},
                            {"display": "none"}, {"display": "none"},
                            "Validar 2FA", {'step': 'validar_2fa', 'login': login}, 
                            dash.no_update)
                else:
                    return (dash.no_update, "Senha incorreta", "", 
                            {"display": "block"}, {"display": "none"}, {"display": "none"},
                            {"display": "none"}, {"display": "none"}, 
                            "Entrar", step_store, dash.no_update)
        
        # ============================================================
        # 🔥 NOVO: VALIDAR 2FA (SEGUNDO FATOR)
        # ============================================================
        elif step == 'validar_2fa':
            if not codigo_2fa:
                return (dash.no_update, "Digite o código 2FA recebido", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "block"},
                        {"display": "none"}, {"display": "none"}, 
                        "Validar 2FA", step_store, dash.no_update)
            
            # Valida o token 2FA
            resultado = validar_token_2fa(login, codigo_2fa)
            
            if resultado['valido']:
                # 🔥 2FA OK! Login concluído com sucesso
                banco_op = operador.get('banco', 'SEMEAR')
                perfil_op = 'adm' if banco_op.upper() == 'ADM' else 'operador'
                # Cria o dicionario de dados do usuario que sera salvo na sessao do navegador
                dados_usuario = {
                    'nome': operador['nome'],
                    'login': operador['login'],
                    'imagem': operador.get('imagem'),
                    'banco': banco_op,
                    'perfil': perfil_op,
                    'admissao': operador.get('admissao')
                }
                
                return (dados_usuario, "", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", step_store, "/dashboard")
            else:
                return (dash.no_update, resultado['mensagem'], "", 
                        {"display": "none"}, {"display": "none"}, {"display": "block"},
                        {"display": "none"}, {"display": "none"}, 
                        "Validar 2FA", step_store, dash.no_update)
        
        # ============================================================
        # VALIDAR TOKEN (primeiro acesso / reset senha)
        # ============================================================
        elif step in ['validar_token_primeiro', 'validar_token_reset']:
            if not token:
                return (dash.no_update, "Digite o código recebido", "", 
                        {"display": "none"}, {"display": "block"}, {"display": "none"},
                        {"display": "none"}, {"display": "none"}, 
                        "Validar Token", step_store, dash.no_update)
            
            tipo = 'primeiro_acesso' if step == 'validar_token_primeiro' else 'reset_senha'
            
            if validar_token(login, token, tipo):
                return (dash.no_update, "", "Token válido! Crie sua senha",
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "block"}, {"display": "block"},
                        "Criar Senha", {'step': 'criar_senha', 'login': login}, 
                        dash.no_update)
            else:
                return (dash.no_update, "Token inválido ou expirado", "", 
                        {"display": "none"}, {"display": "block"}, {"display": "none"},
                        {"display": "none"}, {"display": "none"}, 
                        "Validar Token", step_store, dash.no_update)
        
        # ============================================================
        # CRIAR NOVA SENHA
        # ============================================================
        elif step == 'criar_senha':
            if not nova_senha or not confirma_senha:
                return (dash.no_update, "Preencha ambos os campos", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "block"}, {"display": "block"}, 
                        "Criar Senha", step_store, dash.no_update)
            
            if nova_senha != confirma_senha:
                return (dash.no_update, "As senhas não coincidem", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "block"}, {"display": "block"}, 
                        "Criar Senha", step_store, dash.no_update)
            
            if len(nova_senha) < 4:
                return (dash.no_update, "Mínimo 4 caracteres", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "block"}, {"display": "block"}, 
                        "Criar Senha", step_store, dash.no_update)
            
            if salvar_senha(login, nova_senha):
                operador = Buscar_login(login)
                banco_op = operador.get('banco', 'SEMEAR')
                perfil_op = 'adm' if banco_op.upper() == 'ADM' else 'operador'
                # Popula os dados do usuario que logou pela primeira vez apos criar senha
                dados_usuario = {
                    'nome': operador['nome'],
                    'login': operador['login'],
                    'imagem': operador.get('imagem'),
                    'banco': banco_op,
                    'perfil': perfil_op,
                    'admissao': operador.get('admissao')
                }
                return (dados_usuario, "Senha criada com sucesso!", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "none"}, {"display": "none"}, 
                        "Entrar", {'step': 'login'}, "/dashboard")
            else:
                return (dash.no_update, "Erro ao salvar senha", "", 
                        {"display": "none"}, {"display": "none"}, {"display": "none"},
                        {"display": "block"}, {"display": "block"}, 
                        "Criar Senha", step_store, dash.no_update)
        
        # ============================================================
        # FALLBACK
        # ============================================================
        return (dash.no_update, "Erro no fluxo de autenticação", "", 
                {"display": "none"}, {"display": "none"}, {"display": "none"},
                {"display": "none"}, {"display": "none"}, 
                "Entrar", step_store, dash.no_update)
    
    
    # ================================================================
    # CALLBACK 3: LOGOUT
    # ================================================================
    # Limpa os Stores de autenticação E redireciona para o login.
    # Sem essa limpeza, os dados persistem no localStorage e o
    # usuário continua "logado" mesmo após clicar em Sair.
    # ================================================================
    @app.callback(
        [
            Output('login-success-store', 'data', allow_duplicate=True),
            Output('login-step-store', 'data', allow_duplicate=True),
            Output('url', 'pathname', allow_duplicate=True),
        ],
        [Input('logout-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def fazer_logout(n_clicks):
        """
        FAZ LOGOUT COMPLETO:
        1. Limpa login-success-store (dados do usuário logado)
        2. Reseta login-step-store (passo do fluxo de login)
        3. Redireciona para a tela de login (/)
        """
        if n_clicks:
            # Retorna: store limpo, step resetado, redireciona para login
            return None, {'step': 'login'}, "/"
        raise PreventUpdate
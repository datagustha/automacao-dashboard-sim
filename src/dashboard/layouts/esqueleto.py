"""
LAYOUT DO DASHBOARD PRINCIPAL
==============================
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from datetime import date, datetime
from dash_iconify import DashIconify
from dash.dependencies import Input, Output, State

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.cards import card_indicador
from src.services.db_service import Buscar_login
from src.services.auth_service import gerar_token_numerico,validar_token, salvar_token
from src.services.email_service import enviar_token_email



def tela_login():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H4("Login do Operador", className="text-center"),
                                    style={"borderBottom": "1px solid #7e3d97"}
                                ),
                                dbc.CardBody(
                                    [
                                        # Campo de login (sempre visível)
                                        dbc.Input(
                                            id='login-user-input',
                                            placeholder="Digite seu login (ex: 2552NOME)",
                                            type="text",
                                            className="mb-3",
                                            style={"borderRadius": "8px"}
                                        ),
                                        
                                        # Campo de senha (escondido)
                                        dbc.Input(
                                            id='login-password-input',
                                            placeholder="Digite sua senha",
                                            type="password",
                                            className="mb-3",
                                            style={"display": "none", "borderRadius": "8px"}
                                        ),
                                        
                                        # Campo de TOKEN (escondido)
                                        dbc.Input(
                                            id='login-token-input',
                                            placeholder="Digite o código de 6 dígitos enviado por e-mail",
                                            type="text",
                                            className="mb-3",
                                            style={"display": "none", "borderRadius": "8px"}
                                        ),
                                        
                                        # Campo de NOVA SENHA (escondido)
                                        dbc.Input(
                                            id='login-nova-senha-input',
                                            placeholder="Digite sua nova senha",
                                            type="password",
                                            className="mb-3",
                                            style={"display": "none", "borderRadius": "8px"}
                                        ),
                                        
                                        # Campo de CONFIRMAR SENHA (escondido)
                                        dbc.Input(
                                            id='login-confirma-senha-input',
                                            placeholder="Confirme sua nova senha",
                                            type="password",
                                            className="mb-3",
                                            style={"display": "none", "borderRadius": "8px"}
                                        ),
                                        
                                        # Botão principal
                                        dbc.Button(
                                            "Entrar",
                                            id='login-button',
                                            style={
                                                "backgroundColor": "#7e3d97",
                                                "borderColor": "#7e3d97",
                                                "borderRadius": "8px"
                                            },
                                            className="w-100 fw-bold mb-2"
                                        ),

                                        # Botão "Esqueci minha senha"
                                        html.Button(
                                            "Esqueci minha senha?",
                                            id='btn-esqueci-senha',
                                            className="btn btn-link text-center w-100",
                                            style={"fontSize": "14px", "color": "#7e3d97"}
                                        ),

                                        # Área de mensagem de erro (vermelha)
                                        html.Div(
                                            id='login-mensagem-erro',
                                            className="text-danger mt-3 text-center",
                                            style={"fontSize": "14px"}
                                        ),

                                        # Área de mensagem informativa (roxa)
                                        html.Div(
                                            id='login-info-mensagem',
                                            className="text-info mt-2 text-center",
                                            style={"fontSize": "12px", "color": "#7e3d97"}
                                        )
                                    ]
                                )
                            ],
                            className="shadow-lg",
                            style={"borderRadius": "16px"}
                        )
                    ],
                    width=12, md=6, lg=4
                ),
                justify="center",
                align="center",
                className="vh-100"
            ),
            
            # STORES
            dcc.Store(id='login-success-store'),
            dcc.Store(id='login-step-store', data={'step': 'login'})
        ],
        fluid=True,
        className="bg-light"
    )


# ================================================================
# CALLBACK DE AUTENTICAÇÃO
# ================================================================

def register_callbacks(app):
    
    @app.callback(
        [
            Output('login-mensagem-erro', 'children'),
            Output('login-info-mensagem', 'children'),
            Output('login-password-input', 'style'),
            Output('login-token-input', 'style'),
            Output('login-nova-senha-input', 'style'),
            Output('login-confirma-senha-input', 'style'),
            Output('login-button', 'children'),
            Output('login-step-store', 'data')
        ],
        Input('login-button', 'n_clicks'),
        State('login-user-input', 'value'),
        State('login-password-input', 'value'),
        State('login-token-input', 'value'),
        State('login-nova-senha-input', 'value'),
        State('login-confirma-senha-input', 'value'),
        State('login-step-store', 'data')
    )
    def gerenciar_login(n_clicks, login, senha, token, nova_senha, confirma_senha, step_store):
        
        # Pega o passo atual
        step = step_store.get('step') if step_store else 'login'
        
        # Se o botão não foi clicado
        if not n_clicks:
            return "", "", {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", step_store
        
        # ============================================================
        # PASSO 1: LOGIN
        # ============================================================
        if step == 'login':
            if not login:
                return "❌ Digite seu login!", "", {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", step_store
            
            operador = Buscar_login(login)
            
            if not operador:
                return "❌ Login não encontrado!", "", {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", step_store
            
            if operador['primeiro_acesso'] == 1:
                # Primeiro acesso: envia token
                token_gerado = gerar_token_numerico()
                salvar_token(login, token_gerado, 'primeiro_acesso')
                email = operador['email']
                enviar_token_email(email, login, token_gerado, 'primeiro_acesso')
                
                return "", "✅ Primeiro acesso! Token enviado para seu e-mail.", {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "none"}, "Validar Token", {'step': 'token', 'login': login}
            else:
                # Já tem senha: pede senha
                return "", "✅ Digite sua senha.", {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", {'step': 'senha', 'login': login}
        
        # ============================================================
        # PASSO 2: VALIDAR SENHA
        # ============================================================
        elif step == 'senha':
            if not senha:
                return "❌ Digite sua senha!", "", {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", step_store
            
            # Buscar o hash da senha no banco
            from src.services.auth_service import verificar_senha
            from sqlalchemy.orm import Session
            from src.config.database import engine
            from src.models.LoginModel import analistas
            
            with Session(engine) as session:
                user = session.query(analistas).filter(analistas.loguin == login).first()
                
                if not user or not user.senha_hash:
                    return "❌ Erro: senha não encontrada!", "", {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", step_store
                
                if verificar_senha(user.senha_hash, senha):
                    # Senha correta! Entrar no dashboard
                    dados_usuario = {'nome': user.nome_completo, 'login': user.loguin}
                    return "", "", {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", {'step': 'dashboard', 'usuario': dados_usuario}
                else:
                    return "❌ Senha incorreta!", "", {"display": "block"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", step_store
        
        # ============================================================
        # PASSO 3: VALIDAR TOKEN
        # ============================================================
        elif step == 'token':
            if not token:
                return "❌ Digite o código recebido por e-mail!", "", {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "none"}, "Validar Token", step_store
            
            if validar_token(login, token, 'primeiro_acesso'):
                return "", "✅ Token válido! Crie sua senha.", {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "block"}, "Criar Senha", {'step': 'criar_senha', 'login': login}
            else:
                return "❌ Token inválido ou expirado!", "", {"display": "none"}, {"display": "block"}, {"display": "none"}, {"display": "none"}, "Validar Token", step_store
        
        # ============================================================
        # PASSO 4: CRIAR SENHA
        # ============================================================
        elif step == 'criar_senha':
            if not nova_senha or not confirma_senha:
                return "❌ Preencha ambos os campos de senha!", "", {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "block"}, "Criar Senha", step_store
            
            if nova_senha != confirma_senha:
                return "❌ As senhas não coincidem!", "", {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "block"}, "Criar Senha", step_store
            
            if len(nova_senha) < 4:
                return "❌ A senha deve ter pelo menos 4 caracteres!", "", {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "block"}, "Criar Senha", step_store
            
            from src.services.auth_service import salvar_senha
            if salvar_senha(login, nova_senha):
                # Senha criada com sucesso! Buscar dados do usuário
                operador = Buscar_login(login)
                dados_usuario = {'nome': operador['nome'], 'login': operador['login']}
                return "", "✅ Senha criada com sucesso!", {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", {'step': 'dashboard', 'usuario': dados_usuario}
            else:
                return "❌ Erro ao salvar senha!", "", {"display": "none"}, {"display": "none"}, {"display": "block"}, {"display": "block"}, "Criar Senha", step_store
        
        return "", "", {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"}, "Entrar", step_store
"""
LAYOUT DA TELA DE LOGIN
========================
Tela com suporte a:
- Login normal (com senha)
- Primeiro acesso (criação de senha via token)
- Recuperação de senha (token por e-mail)

CORES DA MARCA:
- Roxo principal: #7e3d97
- Roxo escuro: #612d75
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def get_login_layout():
    """
    Constrói a tela completa de login com suporte a múltiplos fluxos.
    
    O layout muda dinamicamente via callbacks:
    - Inicial: mostra apenas campo de login
    - Se usuário tem senha: mostra campo de senha
    - Se não tem senha: envia token e mostra campo de token + nova senha
    - Se esqueceu a senha: envia token e mostra campo de token + nova senha
    """
    
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            # ============================================
                            # CABEÇALHO DO CARD (com logo e título)
                            # ============================================
                            dbc.CardHeader(
                                html.Div([
                                    # Logo da empresa
                                    html.Div(
                                        html.Img(
                                            src="/assets/LOGO%20BRANCA%20SEM%20FUNDO.png", 
                                            style={"height": "60px"}
                                        ),
                                        style={
                                            "backgroundColor": "#7e3d97",  # Roxo principal
                                            "padding": "20px", 
                                            "borderRadius": "12px", 
                                            "marginBottom": "15px",
                                            "textAlign": "center"
                                        }
                                    ),
                                    html.H4(
                                        "Login do Operador", 
                                        className="text-center font-weight-bold m-0",
                                        style={"color": "#111827"}
                                    )
                                ], className="text-center"),
                                style={"backgroundColor": "white", "borderBottom": "none"}
                            ),
                            
                            # ============================================
                            # CORPO DO CARD (campos e botões)
                            # ============================================
                            dbc.CardBody(
                                [
                                    html.P(
                                        "Entre com suas credenciais ou crie sua senha.", 
                                        className="text-muted text-center mb-4"
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 1: LOGIN (sempre visível)
                                    # ========================================
                                    dbc.Input(
                                        id='login-user-input',
                                        placeholder="Digite seu login (ex: 2552USER)",
                                        type="text",
                                        className="mb-3",
                                        style={"borderRadius": "8px"}
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 2: SENHA (visível se já tem senha)
                                    # ========================================
                                    dbc.Input(
                                        id='login-password-input',
                                        placeholder="Digite sua senha",
                                        type="password",
                                        className="mb-3",
                                        style={"display": "none", "borderRadius": "8px"}
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 3: TOKEN (visível para primeiro acesso/reset)
                                    # ========================================
                                    dbc.Input(
                                        id='login-token-input',
                                        placeholder="Digite o código de 6 dígitos enviado por e-mail",
                                        type="text",
                                        className="mb-3",
                                        style={"display": "none", "borderRadius": "8px"}
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 4: NOVA SENHA (visível para criar/redefinir)
                                    # ========================================
                                    dbc.Input(
                                        id='login-nova-senha-input',
                                        placeholder="Digite sua nova senha",
                                        type="password",
                                        className="mb-3",
                                        style={"display": "none", "borderRadius": "8px"}
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 5: CONFIRMAR NOVA SENHA
                                    # ========================================
                                    dbc.Input(
                                        id='login-confirma-senha-input',
                                        placeholder="Confirme sua nova senha",
                                        type="password",
                                        className="mb-3",
                                        style={"display": "none", "borderRadius": "8px"}
                                    ),
                                    
                                    # ========================================
                                    # BOTÃO PRINCIPAL (com cor roxa)
                                    # ========================================
                                    dbc.Button(
                                        "Entrar",
                                        id='login-button',
                                        style={
                                            "backgroundColor": "#7e3d97",  # Roxo principal
                                            "borderColor": "#7e3d97",
                                            "borderRadius": "8px"
                                        },
                                        className="w-100 fw-bold mb-2"
                                    ),
                                    
                                    # ========================================
                                    # BOTÃO "ESQUECI MINHA SENHA"
                                    # ========================================
                                    html.Button(
                                        "Esqueci minha senha?",
                                        id='btn-esqueci-senha',
                                        className="btn btn-link text-center w-100",
                                        style={"fontSize": "14px", "color": "#7e3d97"}
                                    ),
                                    
                                    # ========================================
                                    # ÁREAS DE MENSAGENS
                                    # ========================================
                                    html.Div(
                                        id='login-mensagem-erro',
                                        className="text-danger mt-3 text-center",
                                        style={"fontSize": "14px"}
                                    ),
                                    html.Div(
                                        id='login-info-mensagem',
                                        className="text-info mt-2 text-center",
                                        style={"fontSize": "12px", "color": "#7e3d97"}
                                    )
                                ]
                            )
                        ],
                        className="shadow-lg",
                        style={"borderRadius": "16px", "border": "none"}
                    ),
                    width=12, md=6, lg=4
                ),
                justify="center",
                align="center",
                className="vh-100"
            ),
            
            # ========================================
            # STORES (armazenam dados temporários)
            # ========================================
            # dcc.Store(id='login-success-store'),           # Guarda dados do usuário logado
            # dcc.Store(id='login-step-store', data={'step': 'login'})  # Controla o fluxo atual
        ],
        fluid=True,
        className="bg-light"
    )
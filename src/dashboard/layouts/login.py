"""
LAYOUT DA TELA DE LOGIN
========================
Tela com suporte a:
- Login normal (com senha)
- Primeiro acesso (criação de senha via token)
- Recuperação de senha (token por e-mail)
- 🔐 Autenticação de Dois Fatores (2FA)

CORES DA MARCA:
- Roxo principal: #7e3d97
- Roxo escuro: #612d75
- Roxo claro: #f3e8f7 (para detalhes)
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
    - 🔐 Após senha correta: mostra campo de 2FA
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
                                            "backgroundColor": "#7e3d97",
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
                                    ),
                                    # 🔥 NOVO: Subtítulo com ícone de segurança
                                    html.P(
                                        html.Small(
                                            [html.I(className="fas fa-shield-alt me-1"), " Ambiente Seguro"],
                                            style={"color": "#7e3d97", "fontSize": "12px"}
                                        ),
                                        className="text-center mt-2 mb-0"
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
                                    html.Div(
                                        [
                                            html.Label(
                                                "Login", 
                                                className="fw-bold mb-1",
                                                style={"fontSize": "13px", "color": "#374151"}
                                            ),
                                            dbc.Input(
                                                id='login-user-input',
                                                placeholder="Ex: 2552GUSTHAVO",
                                                type="text",
                                                className="mb-3",
                                                style={"borderRadius": "8px"},
                                                n_submit=0 
                                            )
                                        ]
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 2: SENHA (visível se já tem senha)
                                    # ========================================
                                    html.Div(
                                        [
                                            html.Label(
                                                "Senha", 
                                                className="fw-bold mb-1",
                                                style={"fontSize": "13px", "color": "#374151"}
                                            ),
                                            dbc.Input(
                                                id='login-password-input',
                                                placeholder="Digite sua senha",
                                                type="password",
                                                className="mb-3",
                                                style={"display": "none", "borderRadius": "8px"}
                                            )
                                        ]
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 3: TOKEN (visível para primeiro acesso/reset)
                                    # ========================================
                                    html.Div(
                                        [
                                            html.Label(
                                                [html.I(className="fas fa-key me-1"), " Código de Verificação"],
                                                className="fw-bold mb-1",
                                                style={"fontSize": "13px", "color": "#374151"}
                                            ),
                                            dbc.Input(
                                                id='login-token-input',
                                                placeholder="Digite o código de 6 dígitos enviado por e-mail",
                                                type="text",
                                                className="mb-3",
                                                style={"display": "none", "borderRadius": "8px"}
                                            ),
                                            html.Small(
                                                "Expira em 15 minutos",
                                                style={"fontSize": "11px", "color": "#6c757d", "display": "none"},
                                                id="token-expiry-hint"
                                            )
                                        ]
                                    ),
                                    
                                    # ========================================
                                    # 🔥 NOVO CAMPO 4: 2FA (segundo fator)
                                    # ========================================
                                    html.Div(
                                        [
                                            html.Label(
                                                [html.I(className="fas fa-mobile-alt me-1"), " Código de Autenticação (2FA)"],
                                                className="fw-bold mb-1",
                                                style={"fontSize": "13px", "color": "#374151"}
                                            ),
                                            dbc.Input(
                                                id='login-2fa-input',
                                                placeholder="Digite o código de 6 dígitos",
                                                type="text",
                                                className="mb-3",
                                                style={"display": "none", "borderRadius": "8px", "letterSpacing": "5px", "fontWeight": "bold"}
                                            ),
                                            html.Small(
                                                [html.I(className="fas fa-clock me-1"), " Expira em 5 minutos"],
                                                style={"fontSize": "11px", "color": "#7e3d97", "display": "none"},
                                                id="fa-expiry-hint"
                                            )
                                        ]
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 5: NOVA SENHA (visível para criar/redefinir)
                                    # ========================================
                                    html.Div(
                                        [
                                            html.Label(
                                                "Nova Senha", 
                                                className="fw-bold mb-1",
                                                style={"fontSize": "13px", "color": "#374151"}
                                            ),
                                            dbc.Input(
                                                id='login-nova-senha-input',
                                                placeholder="Digite sua nova senha",
                                                type="password",
                                                className="mb-3",
                                                style={"display": "none", "borderRadius": "8px"}
                                            ),
                                            html.Small(
                                                "Mínimo de 4 caracteres",
                                                style={"fontSize": "11px", "color": "#6c757d"}
                                            )
                                        ]
                                    ),
                                    
                                    # ========================================
                                    # CAMPO 6: CONFIRMAR NOVA SENHA
                                    # ========================================
                                    html.Div(
                                        [
                                            html.Label(
                                                "Confirmar Senha", 
                                                className="fw-bold mb-1",
                                                style={"fontSize": "13px", "color": "#374151"}
                                            ),
                                            dbc.Input(
                                                id='login-confirma-senha-input',
                                                placeholder="Confirme sua nova senha",
                                                type="password",
                                                className="mb-3",
                                                style={"display": "none", "borderRadius": "8px"}
                                            )
                                        ]
                                    ),
                                    
                                    # ========================================
                                    # BOTÃO PRINCIPAL (com cor roxa e ícone)
                                    # ========================================
                                    dbc.Button(
                                        [
                                            html.I(className="fas fa-sign-in-alt me-2"),
                                            "Entrar"
                                        ],
                                        id='login-button',
                                        style={
                                            "backgroundColor": "#7e3d97",
                                            "borderColor": "#7e3d97",
                                            "borderRadius": "8px",
                                            "transition": "all 0.3s ease"
                                        },
                                        className="w-100 fw-bold mb-2"
                                    ),
                                    
                                    # ========================================
                                    # BOTÃO "ESQUECI MINHA SENHA"
                                    # ========================================
                                    html.Button(
                                        [html.I(className="fas fa-question-circle me-1"), " Esqueci minha senha?"],
                                        id='btn-esqueci-senha',
                                        className="btn btn-link text-center w-100",
                                        style={
                                            "fontSize": "14px", 
                                            "color": "#7e3d97",
                                            "textDecoration": "none",
                                            "transition": "all 0.3s ease"
                                        }
                                    ),
                                    
                                    # ========================================
                                    # ÁREAS DE MENSAGENS
                                    # ========================================
                                    html.Div(
                                        id='login-mensagem-erro',
                                        className="text-danger mt-3 text-center",
                                        style={"fontSize": "13px", "borderRadius": "8px", "padding": "8px"}
                                    ),
                                    html.Div(
                                        id='login-info-mensagem',
                                        className="mt-2 text-center",
                                        style={"fontSize": "12px", "color": "#7e3d97"}
                                    ),
                                    
                                    # ========================================
                                    # LINHA DIVISÓRIA COM ÍCONE
                                    # ========================================
                                    html.Hr(style={"backgroundColor": "#e5e7eb", "marginTop": "20px"}),
                                    
                                    html.P(
                                        [html.I(className="fas fa-lock me-1"), " Sua segurança é nossa prioridade"],
                                        className="text-center",
                                        style={"fontSize": "11px", "color": "#9ca3af", "marginBottom": "0"}
                                    )
                                ]
                            )
                        ],
                        className="shadow-lg",
                        style={"borderRadius": "20px", "border": "none"}
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
            dcc.Store(id='login-success-store'),
            dcc.Store(id='login-step-store', data={'step': 'login'})
        ],
        fluid=True,
        className="bg-gradient-light",
        style={
            "background": "linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%)",
            "minHeight": "100vh"
        }
    )
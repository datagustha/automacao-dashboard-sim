"""
LAYOUT DA TELA DE LOGIN
========================
"""

import dash_bootstrap_components as dbc
from dash import html

def get_login_layout():
    """
    Constrói a tela completa de login com cores do padrão.
    """
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                html.Div([
                                    # Logo da empresa centralizado usando o padrão transparente
                                    html.Div(
                                        html.Img(src="/assets/LOGO%20BRANCA%20SEM%20FUNDO.png", style={"height": "60px", "marginBottom": "5px"}),
                                        style={"backgroundColor": "var(--purple-main)", "padding": "20px", "borderRadius": "8px", "marginBottom": "15px"}
                                    ),
                                    html.H4(
                                        "Acesso ao Sistema", 
                                        className="text-center font-weight-bold m-0"
                                    )
                                ], className="text-center"),
                                style={"backgroundColor": "white", "borderBottom": "none"}
                            ),
                            dbc.CardBody(
                                [
                                    html.P(
                                        "Entre com suas credenciais do banco para acessar a plataforma.", 
                                        className="text-muted text-center mb-4"
                                    ),
                                    dbc.Input(
                                        id='login-user-input',
                                        placeholder="Digite seu login (ex: 2552NOME)...",
                                        type="text",
                                        className="mb-3",
                                        required=True,
                                        style={"borderRadius": "8px"}
                                    ),
                                    dbc.Button(
                                        "Acessar Dashboard",
                                        id='login-button',
                                        style={"backgroundColor": "var(--purple-main)", "borderColor": "var(--purple-main)", "borderRadius": "8px"},
                                        className="w-100 fw-bold shadow-sm"
                                    ),
                                    html.Div(
                                        id='login-mensagem-erro',
                                        className="text-danger mt-3 text-center fw-bold"
                                    )
                                ]
                            )
                        ],
                        className="shadow-lg", style={"borderRadius": "16px", "border": "none"}
                    ),
                    width=12, md=6, lg=4
                ),
                justify="center",
                align="center",
                className="vh-100"
            )
        ],
        fluid=True,
        className="bg-light"
    )
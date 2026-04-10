"""
COMPONENTES MENUS COMPARTILHADOS
================================
Cria a Sidebar e o Header (com foto do operador) e reutiliza 
esse padrão (Template) para qualquer página nova criada no sistema!
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_iconify import DashIconify


def get_sidebar(active_route: str, active_link: str = None):
    """
    Constrói o menu Lateral esquerdo do sistema.
    
    Args:
        active_route: Rota ativa para destaque ('dashboard', 'pagamentos', 'operadores')
        active_link: Link específico para destacar (usado quando o href é dinâmico)
    """
    def check_active(route):
        if active_link:
            return "nav-link active" if route == active_link else "nav-link"
        return "nav-link active" if route == active_route else "nav-link"

    return html.Div(
        [
            # Logo da empresa
            html.Div(
                html.Img(
                    src="/assets/LOGO%20BRANCA%20SEM%20FUNDO.png", 
                    style={"width": "80%"}
                ),
                className="text-center mt-3 mb-5"
            ),
            
            # Menu de navegação
            html.Div(
                [
                    dcc.Link(
                        [DashIconify(icon="lucide:layout-dashboard", width=20, className="me-3"), "Dashboard"], 
                        href="/dashboard", 
                        className=check_active("dashboard")
                    ),
                    dcc.Link(
                        [DashIconify(icon="lucide:dollar-sign", width=20, className="me-3"), "Pagamentos"], 
                        href="/pagamentos", 
                        className=check_active("pagamentos")
                    ),
                    dcc.Link(
                        [DashIconify(icon="lucide:users", width=20, className="me-3"), "Operadores"], 
                        href="/operador/2552ROSELI",  # Link temporário
                        className=check_active("operadores")
                    ),
                ],
                style={"flex": "1"}
            ),
            
            # Botão de logout
            html.Div(
                dbc.Button(
                    [DashIconify(icon="lucide:log-out", width=18, className="me-2"), "Sair do Sistema"],
                    id='logout-button', 
                    color="light", 
                    outline=True, 
                    className="w-100 fw-bold border-0 text-start px-4",
                    style={"color": "#cbd5e1"}
                ),
                style={"marginTop": "auto", "marginBottom": "20px"}
            )
        ],
        className="sidebar"
    )


def get_header(nome_usuario: str, imagem_url: str, titulo: str = "Dashboard"):
    """
    Constrói o cabeçalho Principal incluindo a moldura circular da 
    foto em formato Avatar no canto superior direito.
    """
    print(f"[DEBUG] get_header - imagem_url recebida: {imagem_url}")
    
    avatar = html.Img(
        src=imagem_url, 
        style={
            "width": "45px", 
            "height": "45px", 
            "borderRadius": "50%", 
            "objectFit": "cover"
        }
    ) if imagem_url else DashIconify(
        icon="lucide:user-circle", 
        width=45, 
        color="var(--purple-main)"
    )

    return dbc.Row(
        [
            dbc.Col(
                [
                    html.H3(
                        f"Olá, {nome_usuario.split(' ')[0].upper()}!", 
                        className="font-weight-bold mb-1", 
                        style={"color": "var(--text-main)"}
                    ),
                    html.P(titulo, className="text-muted m-0")
                ]
            ),
            dbc.Col(
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(nome_usuario, className="fw-bold me-2"),
                                html.Small("Operador", className="text-muted d-block text-end me-2")
                            ],
                            className="d-none d-md-block text-end"
                        ),
                        avatar
                    ],
                    className="d-flex align-items-center justify-content-end"
                ),
                className="text-end"
            )
        ],
        className="mb-4 align-items-center"
    )
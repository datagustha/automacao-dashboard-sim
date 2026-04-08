"""
COMPONENTES MENUS COMPARTILHADOS
================================
Cria a Sidebar e o Header (com foto do operador) e reutiliza 
esse padrão (Template) para qualquer página nova criada no sistema!
"""
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_iconify import DashIconify

def get_sidebar(active_route: str):
    """
    Constrói o menu Lateral esquerdo do sistema,
    definindo como ATIVO o botão que bater com a active_route.
    """
    def check_active(route):
        return "nav-link active" if route == active_route else "nav-link"

    return html.Div(
        [
            # Logo Empresa em Branco - Agora sozinha como exigido.
            html.Div(
                html.Img(src="/assets/LOGO%20BRANCA%20SEM%20FUNDO.png", style={"width": "80%"}),
                className="text-center mt-3 mb-5"
            ),
            
            # Navegação do Menu usando dcc.Link para não dar Full Page Reload no Dash (E não matar nossa memória do login)
            html.Div(
                [
                    dcc.Link([DashIconify(icon="lucide:layout-dashboard", width=20, className="me-3"), "Dashboard"], href="/dashboard", className=check_active("dashboard")),
                    dcc.Link([DashIconify(icon="lucide:dollar-sign", width=20, className="me-3"), "Pagamentos"], href="/pagamentos", className=check_active("pagamentos")),
                    dcc.Link([DashIconify(icon="lucide:users", width=20, className="me-3"), "Operadores"], href="#", className="nav-link"),
                ],
                style={"flex": "1"} # Puxa todo o background restante para o rodapé cair
            ),
            
            # Botão de Logout fixo no fim
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
    foto em formato Avatar no canto superior direito como num "SITE".
    """
    
    # Valida e processa a imagem para Avatar (Retirada a borda extra que já tem na foto nativa do banco)
    avatar = html.Img(
        src=imagem_url, 
        style={
            "width": "45px", "height": "45px", 
            "borderRadius": "50%", "objectFit": "cover"
        }
    ) if imagem_url else DashIconify(icon="lucide:user-circle", width=45, color="var(--purple-main)")

    return dbc.Row(
        [
            # === Seção à esquerda: Texto "Olá Roseli!" ===
            dbc.Col(
                [
                    html.H3(f"Olá, {nome_usuario.split(' ')[0].upper()}!", className="font-weight-bold mb-1", style={"color": "var(--text-main)"}),
                    html.P(titulo, className="text-muted m-0")
                ]
            ),
            
            # === Seção Direita: Menu de Perfil / Foto ===
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

"""
COMPONENTES MENUS COMPARTILHADOS
================================
Cria a Sidebar e o Header (com foto do operador) e reutiliza 
esse padrão (Template) para qualquer página nova criada no sistema!
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_iconify import DashIconify


def get_sidebar(active_route: str, active_link: str = None, perfil: str = 'operador'):
    """
    Constrói o menu Lateral esquerdo do sistema.
    
    Args:
        active_route: Rota ativa para destaque ('dashboard', 'pagamentos', 'operadores')
        active_link: Link específico para destacar (usado quando o href é dinâmico)
        perfil: 'adm' ou 'operador' — pode adaptar o menu conforme necessário
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
                        href="/operadores",
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


def get_header(nome_usuario: str, imagem_url: str, titulo: str = "Dashboard", admissao: str = None, perfil: str = 'operador'):
    """
    Constroi o cabecalho principal incluindo o nome, avatar e tempo de casa.
    """
    # Imprime no log o status do carregamento da imagem de perfil
    print(f"[DEBUG] get_header - imagem_url recebida: {imagem_url}")
    
    # Inicializa o bloco de tempo de casa como nulo
    tempo_casa_html = None
    # Se houver data de admissao cadastrada para o operador
    if admissao:
        # Importa a funcao de calculo do tempo de casa
        from src.services.analytics_service import calcular_tempo_de_casa
        # Calcula a string do tempo de casa
        tempo_str = calcular_tempo_de_casa(admissao)
        # Cria o componente html para exibir o tempo de casa estilizado
        tempo_casa_html = html.Small(
            f"Tempo de casa: {tempo_str}",
            className="text-muted d-block text-end me-2",
            style={"fontSize": "11px", "color": "#7c3aed", "fontWeight": "600"}
        )
    
    # Se a URL da imagem de perfil estiver preenchida
    if imagem_url:
        # Cria o elemento de imagem circular com a foto do operador
        avatar = html.Img(
            src=imagem_url, 
            style={
                "width": "45px", 
                "height": "45px", 
                "borderRadius": "50%", 
                "objectFit": "cover"
            }
        )
    else:
        # Caso nao tenha imagem, usa o icone de usuario padrão (circulo roxo)
        avatar = DashIconify(
            icon="lucide:user-circle", 
            width=45, 
            color="var(--purple-main)"
        )

    # Retorna uma linha do Bootstrap contendo as colunas do cabeçalho
    return dbc.Row(
        [
            # Coluna da esquerda contendo a saudacao e o titulo da pagina
            dbc.Col(
                [
                    # Saudacao contendo o primeiro nome do usuario em letras maiusculas
                    html.H3(
                        f"Olá, {nome_usuario.split(' ')[0].upper()}!", 
                        className="font-weight-bold mb-1", 
                        style={"color": "var(--text-main)"}
                    ),
                    # Subtitulo (titulo da pagina)
                    html.P(titulo, className="text-muted m-0")
                ]
            ),
            # Coluna da direita contendo o nome do usuario logado, perfil e tempo de casa
            dbc.Col(
                html.Div(
                    [
                        # Bloco de texto alinhado a direita (ocultado em telas mobile)
                        html.Div(
                            [
                                # Nome completo do analista
                                html.Span(nome_usuario, className="fw-bold me-2"),
                                # Perfil formatado (Administrador ou Operador)
                                html.Small("Administrador" if perfil == 'adm' else "Operador", className="text-muted d-block text-end me-2"),
                                # Bloco de tempo de casa adicionado dinamicamente
                                tempo_casa_html
                            ],
                            className="d-none d-md-block text-end"
                        ),
                        # Foto ou icone de perfil (avatar)
                        avatar
                    ],
                    className="d-flex align-items-center justify-content-end"
                ),
                className="text-end"
            )
        ],
        # Margem inferior e alinhamento vertical centralizado para a linha
        className="mb-4 align-items-center"
    )
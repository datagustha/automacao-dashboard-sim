"""
LAYOUT DO DASHBOARD PRINCIPAL (OPERADOR)
==========================================
Exibe os dados do operador logado:
- SEMEAR: exclui "Fora da fase", mostra gráfico por fase
- AGORACRED: considera todos os pagamentos, sem gráfico por fase
"""
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from datetime import date, datetime
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.cards import card_indicador, card_meta
from src.dashboard.components.tabelas import container_grafico, container_tabela, container_tabela_cheia
from src.dashboard.components.graficos import grafico_barras_fase, grafico_evolucao_diaria

from src.dashboard.components.filtros import criar_filtro_data_range, MESES, get_anos, OPCOES_FASES

# Usaremos get_anos() no layout para ter anos atualizados
meses = MESES
OPCOES_FASES_DASHBOARD = OPCOES_FASES

def get_dashboard_layout(nome_usuario: str, imagem_url: str = None, banco: str = "SEMEAR", admissao: str = None):
    """
    Constrói o layout do dashboard do operador.
    
    Args:
        nome_usuario: Nome do operador logado
        imagem_url: URL da foto do operador
        banco: 'SEMEAR' ou 'AGORACRED' — controla quais filtros e gráficos aparecem
        admissao: Data de admissão do operador logado
    """
    # Cria o menu lateral (sidebar) destacado na rota 'dashboard'
    sidebar = get_sidebar("dashboard")

    # Filtro de fase: visível só para SEMEAR
    fase_style = {"display": "block"} if banco == "SEMEAR" else {"display": "none"}

    # Largura do gráfico de evolução conforme o banco (AGORACRED não tem barras de fase, fica tela cheia)
    col_evolucao_width = 12 if banco == "AGORACRED" else 6

    # Bloco principal de conteúdo da página
    conteudo = html.Div(
        [
            # Renderiza o cabeçalho superior passando o nome, avatar, título, admissão e perfil do operador
            get_header(nome_usuario, imagem_url, "Painel Global Analítico", admissao=admissao, perfil="operador"),


            # === FILTROS — LINHA 1: busca + fase ===
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Busca", className="fw-bold mb-1", style={"color": "var(--text-muted)", "fontSize": "13px"}),
                            dbc.InputGroup([
                                dbc.InputGroupText(DashIconify(icon="lucide:search", width=18, color="var(--text-muted)"), style={"backgroundColor": "white", "borderRight": "none"}),
                                dbc.Input(
                                    id='filtro-texto-busca',
                                    type='text',
                                    placeholder="Procurar contrato / cliente...",
                                    style={"borderLeft": "none"},
                                    debounce=True
                                )
                            ], className="shadow-sm", style={"borderRadius": "8px"}),
                            # overlay indicando busca em andamento
                            html.Div(
                                id="busca-loading-hint",
                                children=[
                                    DashIconify(icon="lucide:loader", width=14, style={"marginRight": "4px"}),
                                    html.Span("Pesquisando...", style={"fontSize": "11px"})
                                ],
                                style={
                                    "display": "none",  # mostrado via callback
                                    "color": "#7e3d97", "fontWeight": "600",
                                    "marginTop": "4px", "fontSize": "11px"
                                }
                            ),
                        ],
                        width=12, md=5, className="mb-2"
                    ),
                    # FILTRO DE FASE — MULTIPLA SELEÇÃO (visível só para SEMEAR)
                    dbc.Col(
                        [
                            html.Label("Fase", className="fw-bold mb-1", style={"color": "var(--text-muted)", "fontSize": "13px"}),
                            dcc.Dropdown(
                                id="filtro-fase",
                                options=OPCOES_FASES_DASHBOARD,
                                value=["todas"],
                                multi=True,
                                clearable=True,
                                placeholder="Selecione fases...",
                                className="shadow-sm",
                                style={"borderRadius": "8px", **fase_style}
                            )
                        ],
                        width=12, md=4,
                        style=fase_style,
                        className="mb-2"
                    ),
                ],
                className="align-items-end g-3 mt-2"
            ),

            # === FILTROS — LINHA 2: mês/ano + data range ===
            dbc.Row(
                [
                    # FILTRO DE MÊS/ANO
                    dbc.Col(
                        [
                            html.Label("Mês/Ano", className="fw-bold mb-1", style={"color": "var(--text-muted)", "fontSize": "13px"}),
                            dbc.Row([
                                dbc.Col(dbc.Select(id="filtro-mes", options=meses, value=datetime.today().month, className="shadow-sm", style={"borderRadius": "8px"}), width=6, className="pe-1"),
                                dbc.Col(dbc.Select(id="filtro-ano", options=get_anos(), value=datetime.today().year, className="shadow-sm", style={"borderRadius": "8px"}), width=6, className="ps-1"),
                            ])
                        ],
                        width=12, md=3,
                        className="mb-3"
                    ),
                    # FILTRO DE DATA RANGE
                    dbc.Col(
                        criar_filtro_data_range(""),
                        width=12, md=5,
                        className="mb-3"
                    )
                ],
                className="align-items-end g-3 mb-4"
            ),

            # === KPIs ===
            dbc.Row(
                [
                    dbc.Col(
                        card_indicador(
                            titulo="FATURAMENTO TOTAL",
                            valor_default="R$ 0,00",
                            id_valor="kpi-faturamento",
                            cor_icone="var(--purple-main)",
                            icon_name="lucide:trending-up",
                            id_sub_texto="kpi-mes-anterior"
                        ),
                        width=12, md=3, className="mb-4"
                    ),
                    dbc.Col(
                        card_indicador(
                            titulo="TICKET MÉDIO",
                            valor_default="R$ 0,00",
                            id_valor="kpi-ticket",
                            cor_icone="var(--purple-main)",
                            icon_name="lucide:ticket"
                        ),
                        width=12, md=3, className="mb-4"
                    ),
                    dbc.Col(
                        card_indicador(
                            titulo="OPERAÇÕES PAGAS",
                            valor_default="0",
                            id_valor="kpi-total-pgtos",
                            cor_icone="var(--purple-main)",
                            icon_name="lucide:credit-card",
                            id_sub_texto="kpi-pgtos-anterior"
                        ),
                        width=12, md=3, className="mb-4"
                    ),
                    dbc.Col(
                        card_meta(
                            titulo="META DO MÊS",
                            id_meta_objetivo="kpi-meta-objetivo",
                            id_barra="kpi-meta-barra",
                            id_percentual="kpi-meta-percentual",
                            cor_icone="var(--purple-main)"
                        ),
                        width=12, md=3, className="mb-4"
                    ),
                ],
                className="g-3"
            ),

            # === KPIs DE LIGAÇÕES (TMA / ACIONAMENTO) ===
            html.Div([
                html.Hr(style={"borderColor": "#e5e7eb", "margin": "0 0 12px 0"}),
                html.Div([
                    DashIconify(icon="lucide:phone-call", width=16, color="var(--purple-main)", style={"marginRight": "6px"}),
                    html.Span("Métricas de Ligação (TMA)", style={"fontSize": "12px", "fontWeight": "700", "color": "var(--text-muted)", "letterSpacing": "0.5px", "textTransform": "uppercase"}),
                    html.Span(" — passe o mouse nos cards para entender cada indicador", style={"fontSize": "11px", "color": "#aaa", "marginLeft": "8px"})
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px"})
            ], style={"marginTop": "4px"}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            card_indicador(
                                titulo="TEMPO MÉDIO DE ATENDIMENTO (TMA)",
                                valor_default="—",
                                id_valor="kpi-tma-valor",
                                cor_icone="var(--purple-main)",
                                icon_name="lucide:phone-call",
                                id_sub_texto="kpi-tma-subtexto"
                            ),
                            dbc.Tooltip(
                                "TMA (Tempo Médio de Atendimento): tempo médio que o operador ficou em ligação por acionamento. Subtext mostra o total de tempo falado no mês.",
                                target="title-kpi-tma-valor",
                                placement="top",
                            ),
                        ],
                        width=12, md=4, className="mb-4"
                    ),
                    dbc.Col(
                        [
                            card_indicador(
                                titulo="QUANTIDADE DE ACIONAMENTOS",
                                valor_default="0",
                                id_valor="kpi-tma-acionamentos",
                                cor_icone="var(--purple-main)",
                                icon_name="lucide:list-todo",
                                id_sub_texto="kpi-tma-ult-acionamento"
                            ),
                            dbc.Tooltip(
                                "Total de ligações realizadas no período. O subtext mostra a data/hora do último acionamento registrado.",
                                target="title-kpi-tma-acionamentos",
                                placement="top",
                            ),
                        ],
                        width=12, md=4, className="mb-4"
                    ),
                    dbc.Col(
                        [
                            card_indicador(
                                titulo="TAXA DE REACIONAMENTO",
                                valor_default="0,0",
                                id_valor="kpi-tma-reacionamento",
                                cor_icone="var(--purple-main)",
                                icon_name="lucide:refresh-cw",
                                id_sub_texto="kpi-tma-clientes"
                            ),
                            dbc.Tooltip(
                                "Taxa de acionamentos por cliente único. Ex: 1,86x = em média cada cliente recebeu 1,86 ligações. Abaixo: total de clientes únicos acionados.",
                                target="title-kpi-tma-reacionamento",
                                placement="top",
                            ),
                        ],
                        width=12, md=4, className="mb-4"
                    ),
                ],
                className="g-3"
            ),


            # === GRÁFICOS ===
            dbc.Row([
                dbc.Col(
                    dcc.Loading(
                        type="circle",
                        children=grafico_evolucao_diaria("grafico-faturamento", "Evolução Diária - Faturamento no Período")
                    ), 
                    width=12, md=col_evolucao_width
                ),
                # Gráfico de fase: para AGORACRED fica oculto
                dbc.Col(
                    dcc.Loading(
                        type="circle",
                        children=grafico_barras_fase("grafico-fase", "Pagamentos por Fase", cor="roxo")
                    ),
                    width=12, md=6,
                    style={"display": "block"} if banco == "SEMEAR" else {"display": "none"}
                )
            ], className="mb-4"),

            # === TABELA DE PERFORMANCE ===
            html.Div(
                id='info-dias-performance',
                className="text-muted mb-2 px-1",
                style={"fontSize": "13px", "fontWeight": "500"}
            ),
            dbc.Row([
                dbc.Col(
                    dcc.Loading(
                        type="circle",
                        children=container_tabela_cheia("tabela-performance", titulo="📊 Performance do Operador")
                    ),
                    width=12
                )
            ], className="mb-4"),

            # === TABELA MÊS A MÊS ===
            dbc.Row([
                dbc.Col(
                    html.Div(
                        [
                            html.H5(
                                "📈 Resultado Mês a Mês",
                                className="m-0 font-weight-bold mb-3",
                                style={"color": "var(--text-main)"}
                            ),
                            dcc.Loading(
                                id="loading-tabela-mes-mes-dashboard",
                                type="circle",
                                children=[
                                    dash_table.DataTable(
                                        id="tabela-mes-mes-dashboard",
                                        page_size=12,
                                        sort_action="native",
                                        style_table={"overflowX": "auto", "borderRadius": "8px"},
                                        style_header={
                                            "backgroundColor": "var(--purple-main)",
                                            "color": "white",
                                            "fontWeight": "600",
                                            "textAlign": "center",
                                            "padding": "10px",
                                        },
                                        style_cell={
                                            "textAlign": "center",
                                            "padding": "10px",
                                            "borderBottom": "1px solid #E5E7EB",
                                            "color": "var(--text-main)",
                                            "fontSize": "13px",
                                        },
                                        style_data_conditional=[
                                            {
                                                "if": {"filter_query": '{nome_mes} = "TOTAL"'},
                                                "backgroundColor": "#e9d8fd",
                                                "color": "#4a1d8c",
                                                "fontWeight": "bold",
                                                "fontSize": "14px",
                                            },
                                            {"if": {"row_index": "odd"}, "backgroundColor": "#F9FAFB"},
                                        ],
                                    )
                                ],
                            ),
                        ],
                        className="dashboard-panel"
                    ),
                    width=12
                )
            ], className="mb-4"),

            # === TABELA DE PAGAMENTOS ===
            dbc.Row([
                dbc.Col(
                    dcc.Loading(
                        type="circle",
                        children=container_tabela("tabela-pagamentos")
                    ),
                    width=12
                )
            ]),

            # === TABELA DE VARIAÇÃO (Atual vs Mês Anterior) ===
            html.Div([
                html.Hr(style={"borderColor": "#f59e0b", "borderWidth": "2px", "marginTop": "24px"}),
                html.Div([
                    DashIconify(icon="lucide:trending-up", width=20, color="#d97706", style={"marginRight": "8px"}),
                    html.Span("Variação vs Mês Anterior", style={"fontSize": "14px", "fontWeight": "700", "color": "#d97706"}),
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
                html.P(
                    "Comparação do faturamento atual com o mês anterior — mostra variação em R$ e %, e quanto da meta foi atingido em cada período.",
                    style={"fontSize": "12px", "color": "var(--text-muted)", "marginBottom": "12px"}
                ),
                dcc.Loading(
                    type="circle",
                    children=[
                        html.Div(id="resumo-evolucao-operador", className="mb-2"),
                        dash_table.DataTable(
                            id="tabela-evolucao-operador",
                            columns=[],
                            data=[],
                            markdown_options={"html": True},
                            page_size=15,
                            sort_action="native",
                            style_table={"overflowX": "auto", "borderRadius": "8px"},
                            style_header={
                                "backgroundColor": "#d97706",
                                "color": "white",
                                "fontWeight": "600",
                                "textAlign": "center",
                                "padding": "10px",
                            },
                            style_cell={
                                "textAlign": "center",
                                "padding": "8px 12px",
                                "borderBottom": "1px solid #E5E7EB",
                                "fontSize": "13px",
                            },
                            style_data_conditional=[
                                {"if": {"row_index": "odd"}, "backgroundColor": "#F9FAFB"},
                            ],
                        )
                    ],
                ),
            ], className="dashboard-panel mb-4"),

            dcc.Interval(id='intervalo-atualizacao', interval=300*1000, n_intervals=0)
        ],
        className="main-content"
    )

    return html.Div([sidebar, conteudo])
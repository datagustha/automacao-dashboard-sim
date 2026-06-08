"""
LAYOUT DO DASHBOARD PRINCIPAL (OPERADOR)
==========================================
Exibe os dados do operador logado:
- SEMEAR: exclui "Fora da fase", mostra gráfico por fase
- AGORACRED: considera todos os pagamentos, sem gráfico por fase
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
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

    # Bloco principal de conteúdo da página
    conteudo = html.Div(
        [
            # Renderiza o cabeçalho superior passando o nome, avatar, título, admissão e perfil do operador
            get_header(nome_usuario, imagem_url, "Painel Global Analítico", admissao=admissao, perfil="operador"),


            # === FILTROS ===
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Busca", className="fw-bold mb-1", style={"color": "var(--text-muted)", "fontSize": "13px"}),
                            dbc.InputGroup([
                                dbc.InputGroupText(DashIconify(icon="lucide:search", width=18, color="var(--text-muted)"), style={"backgroundColor": "white", "borderRight": "none"}),
                                dbc.Input(id='filtro-texto-busca', type='text', placeholder="Procurar contrato / cliente...", style={"borderLeft": "none"})
                            ], className="shadow-sm", style={"borderRadius": "8px"})
                        ],
                        width=12, md=3, className="mb-4"
                    ),
                    # FILTRO DE FASE - MULTIPLA SELEÇÃO (visível só para SEMEAR)
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
                        width=12, md=2,
                        style=fase_style,
                        className="mb-4"
                    ),
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
                        className="mb-4"
                    ),
                    # FILTRO DE DATA RANGE
                    dbc.Col(
                        criar_filtro_data_range(""),
                        width=12, md=4,
                        className="mb-4"
                    )
                ],
                className="align-items-start"
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

            # === GRÁFICOS ===
            dbc.Row([
                dbc.Col(
                    grafico_evolucao_diaria("grafico-faturamento", "Evolução Diária - Faturamento no Período"), 
                    width=12, md=6
                ),
                # Gráfico de fase: para AGORACRED fica oculto
                dbc.Col(
                    grafico_barras_fase("grafico-fase", "Pagamentos por Fase", cor="roxo"),
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
                    container_tabela_cheia("tabela-performance", titulo="📊 Performance do Operador"),
                    width=12
                )
            ], className="mb-4"),

            # === TABELA DE PAGAMENTOS ===
            dbc.Row([dbc.Col(container_tabela("tabela-pagamentos"), width=12)]),

            dcc.Interval(id='intervalo-atualizacao', interval=300*1000, n_intervals=0)
        ],
        className="main-content"
    )

    return html.Div([sidebar, conteudo])
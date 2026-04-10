"""
LAYOUT DO DASHBOARD PRINCIPAL
==============================
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from datetime import date, datetime
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.cards import card_indicador, card_meta
from src.dashboard.components.tabelas import container_grafico, container_tabela, container_tabela_cheia
from src.dashboard.components.graficos import grafico_barras_fase, grafico_evolucao_diaria

anos = [{"label": str(ano), "value": ano} for ano in range(2020, date.today().year + 2)]
meses = [
    {"label": "Janeiro", "value": 1}, {"label": "Fevereiro", "value": 2}, {"label": "Março", "value": 3},
    {"label": "Abril", "value": 4}, {"label": "Maio", "value": 5}, {"label": "Junho", "value": 6},
    {"label": "Julho", "value": 7}, {"label": "Agosto", "value": 8}, {"label": "Setembro", "value": 9},
    {"label": "Outubro", "value": 10}, {"label": "Novembro", "value": 11}, {"label": "Dezembro", "value": 12}
]

def get_dashboard_layout(nome_usuario: str, imagem_url: str = None):
    # Sidebar Dinâmico apontando para a página atual
    sidebar = get_sidebar("dashboard")

    conteudo = html.Div(
        [
            # Header Dinâmico via menus.py puxando a imagem para o Avatar Superior Direito
            get_header(nome_usuario, imagem_url, "Painel Global Analítico"),

            # === FILTROS (Busca + Select de DATA + FASE) ===
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup([
                            dbc.InputGroupText(DashIconify(icon="lucide:search", width=18, color="var(--text-muted)"), style={"backgroundColor": "white", "borderRight": "none"}),
                            dbc.Input(id='filtro-texto-busca', type='text', placeholder="Procurar contrato / cliente...", style={"borderLeft": "none"})
                        ], className="shadow-sm mb-4", style={"borderRadius": "8px"}),
                        width=4
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="filtro-fase",
                            options=[
                                {"label": "Todas Fases", "value": "todas"},
                                {"label": "Fase 10 a 30", "value": "FASE 10 A 30"},
                                {"label": "Fase 31 a 60", "value": "FASE 31 A 60"},
                                {"label": "Fase 61 a 90", "value": "FASE 61 A 90"}
                            ],
                            value=["todas"], # Padrão
                            multi=True,
                            className="shadow-sm mb-4", style={"borderRadius": "8px"}
                        ), width=3
                    ),
                    dbc.Col(
                        dbc.Select(id="filtro-mes", options=meses, value=datetime.today().month, className="shadow-sm mb-4", style={"borderRadius": "8px"}),
                        width=2
                    ),
                    dbc.Col(
                        dbc.Select(id="filtro-ano", options=anos, value=datetime.today().year, className="shadow-sm mb-4", style={"borderRadius": "8px"}),
                        width=2
                    )
                ]
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
                            icon_name="lucide:credit-card"
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
                className="g-3"  # espaçamento entre os cards
            ),

            # === GRÁFICO E TABELA ===
            # No layout, dentro do dbc.Row:
            dbc.Row([
                # Gráfico de evolução (esquerda)
                dbc.Col(
                    grafico_evolucao_diaria("grafico-faturamento", "Evolução Diária - Faturamento no Período"), 
                    width=12, md=6
                ),
                # Gráfico de barras (direita)
                dbc.Col(
                    grafico_barras_fase("grafico-fase", "Pagamentos por Fase", cor="roxo"), 
                    width=12, md=6
                )
            ], className="mb-4"),

            # ================================================================
            # TABELA DE PERFORMANCE DO OPERADOR
            # ================================================================
            dbc.Row([
                dbc.Col(
                    container_tabela_cheia("tabela-performance", titulo="📊 Performance do Operador"),
                    width=12
                )
            ], className="mb-4"),

            # === TABELA ===

            dbc.Row([dbc.Col(container_tabela("tabela-pagamentos"), width=12)]),

            dcc.Interval(id='intervalo-atualizacao', interval=300*1000, n_intervals=0)
        ],
        className="main-content"
    )

    return html.Div([sidebar, conteudo])
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

anos = [{"label": str(ano), "value": ano} for ano in range(2020, date.today().year + 2)]
meses = [
    {"label": "Janeiro", "value": 1}, {"label": "Fevereiro", "value": 2}, {"label": "Março", "value": 3},
    {"label": "Abril", "value": 4}, {"label": "Maio", "value": 5}, {"label": "Junho", "value": 6},
    {"label": "Julho", "value": 7}, {"label": "Agosto", "value": 8}, {"label": "Setembro", "value": 9},
    {"label": "Outubro", "value": 10}, {"label": "Novembro", "value": 11}, {"label": "Dezembro", "value": 12}
]

def get_dashboard_layout(nome_usuario: str, imagem_url: str = None, banco: str = "SEMEAR"):
    """
    Constrói o layout do dashboard do operador.
    
    Args:
        nome_usuario: Nome do operador logado
        imagem_url: URL da foto do operador
        banco: 'SEMEAR' ou 'AGORACRED' — controla quais filtros e gráficos aparecem
    """
    sidebar = get_sidebar("dashboard")

    # Filtro de fase: visível só para SEMEAR
    fase_style = {"display": "block"} if banco == "SEMEAR" else {"display": "none"}

    conteudo = html.Div(
        [
            get_header(nome_usuario, imagem_url, "Painel Global Analítico"),

            # === FILTROS ===
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup([
                            dbc.InputGroupText(DashIconify(icon="lucide:search", width=18, color="var(--text-muted)"), style={"backgroundColor": "white", "borderRight": "none"}),
                            dbc.Input(id='filtro-texto-busca', type='text', placeholder="Procurar contrato / cliente...", style={"borderLeft": "none"})
                        ], className="shadow-sm mb-4", style={"borderRadius": "8px"}),
                        width=4
                    ),
                    # Filtro de fase — oculto para AGORACRED
                    dbc.Col(
                        dcc.Dropdown(
                            id="filtro-fase",
                            options=[
                                {"label": "Todas Fases", "value": "todas"},
                                {"label": "Fase 10 a 30", "value": "FASE 10 A 30"},
                                {"label": "Fase 31 a 60", "value": "FASE 31 A 60"},
                                {"label": "Fase 61 a 90", "value": "FASE 61 A 90"}
                            ],
                            value=["todas"],
                            multi=True,
                            className="shadow-sm mb-4",
                            style={"borderRadius": "8px", **fase_style}
                        ),
                        width=3,
                        style=fase_style
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
                            icon_name="lucide:credit-card",
                            id_sub_texto="kpi-pgtos-anterior"  # ← subtexto com mês anterior
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
            # Subtítulo com dias trabalhados/restantes (atualizado pelo callback)
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
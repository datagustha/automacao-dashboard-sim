"""
LAYOUT DO DASHBOARD ADM
========================
Exibe visão consolidada do grupo com duas seções:
- Faturamento + Tabela de operadores SEMEAR
- Faturamento + Tabela de operadores AGORACRED

Só é exibido quando o login tem banco='ADM'.
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from datetime import date, datetime
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.cards import card_indicador
from src.dashboard.components.tabelas import container_tabela_cheia

anos  = [{"label": str(ano), "value": ano} for ano in range(2020, date.today().year + 2)]
meses = [
    {"label": "Janeiro",   "value": 1},  {"label": "Fevereiro", "value": 2},
    {"label": "Março",     "value": 3},  {"label": "Abril",     "value": 4},
    {"label": "Maio",      "value": 5},  {"label": "Junho",     "value": 6},
    {"label": "Julho",     "value": 7},  {"label": "Agosto",    "value": 8},
    {"label": "Setembro",  "value": 9},  {"label": "Outubro",   "value": 10},
    {"label": "Novembro",  "value": 11}, {"label": "Dezembro",  "value": 12},
]


def get_dashboard_adm_layout(nome_usuario: str, imagem_url: str = None):
    """Constrói o layout do dashboard do ADM com as duas seções de banco."""

    sidebar = get_sidebar("dashboard", perfil="adm")

    conteudo = html.Div(
        [
            get_header(nome_usuario, imagem_url, "Painel ADM — Visão Geral do Grupo"),

            # ── Filtros ──────────────────────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Select(
                            id="filtro-mes-adm",
                            options=meses,
                            value=datetime.today().month,
                            className="shadow-sm",
                            style={"borderRadius": "8px"}
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="filtro-ano-adm",
                            options=anos,
                            value=datetime.today().year,
                            className="shadow-sm",
                            style={"borderRadius": "8px"}
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="filtro-atividade-adm",
                            options=[
                                {"label": "Somente Ativos", "value": "ATIVO"},
                                {"label": "Todos", "value": "TODOS"}
                            ],
                            value="ATIVO",
                            className="shadow-sm",
                            style={"borderRadius": "8px"}
                        ),
                        width=3
                    ),
                ],
                className="mb-4"
            ),

            # ── Cards globais do grupo ──────────────────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        card_indicador(
                            titulo="FATURAMENTO SEMEAR",
                            valor_default="R$ 0,00",
                            id_valor="kpi-fat-semear",
                            cor_icone="#7e3d97",
                            icon_name="lucide:trending-up",
                            id_sub_texto="kpi-fat-semear-anterior"
                        ),
                        width=12, md=3, className="mb-4"
                    ),
                    dbc.Col(
                        card_indicador(
                            titulo="FATURAMENTO AGORACRED",
                            valor_default="R$ 0,00",
                            id_valor="kpi-fat-agoracred",
                            cor_icone="#A0CD4A",
                            icon_name="lucide:trending-up",
                            id_sub_texto="kpi-fat-agoracred-anterior"
                        ),
                        width=12, md=3, className="mb-4"
                    ),
                    dbc.Col(
                        card_indicador(
                            titulo="OPERAÇÕES PAGAS",
                            valor_default="0",
                            id_valor="kpi-total-ops-adm",
                            cor_icone="#7e3d97",
                            icon_name="lucide:credit-card",
                            id_sub_texto="kpi-ops-adm-anterior"
                        ),
                        width=12, md=3, className="mb-4"
                    ),
                    dbc.Col(
                        card_indicador(
                            titulo="TICKET MÉDIO (GRUPO)",
                            valor_default="R$ 0,00",
                            id_valor="kpi-ticket-adm",
                            cor_icone="#7e3d97",
                            icon_name="lucide:ticket",
                        ),
                        width=12, md=3, className="mb-4"
                    ),
                ],
                className="g-3"
            ),

            # ── Seção SEMEAR ────────────────────────────────────────────
            html.Div(
                [
                    html.Hr(style={"borderColor": "#7e3d97", "borderWidth": "2px"}),
                    html.H4(
                        [DashIconify(icon="lucide:building-2", width=22, className="me-2"), "SEMEAR"],
                        style={"color": "#7e3d97", "fontWeight": "700"}
                    ),
                ],
                className="mb-3 mt-2"
            ),
            dbc.Row([
                dbc.Col(
                    container_tabela_cheia("tabela-adm-semear", "📊 Ranking de Operadores — SEMEAR"),
                    width=12
                )
            ], className="mb-4"),

            # ── Seção AGORACRED ─────────────────────────────────────────
            html.Div(
                [
                    html.Hr(style={"borderColor": "#A0CD4A", "borderWidth": "2px"}),
                    html.H4(
                        [DashIconify(icon="lucide:building-2", width=22, className="me-2"), "AGORACRED"],
                        style={"color": "#A0CD4A", "fontWeight": "700"}
                    ),
                ],
                className="mb-3 mt-2"
            ),
            dbc.Row([
                dbc.Col(
                    container_tabela_cheia("tabela-adm-agoracred", "📊 Ranking de Operadores — AGORACRED"),
                    width=12
                )
            ], className="mb-4"),

            dcc.Interval(id='intervalo-atualizacao-adm', interval=300 * 1000, n_intervals=0),
        ],
        className="main-content"
    )

    return html.Div([sidebar, conteudo])

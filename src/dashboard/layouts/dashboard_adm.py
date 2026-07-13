"""
LAYOUT DO DASHBOARD ADM
========================
Exibe visão consolidada do grupo com duas seções:
- Faturamento + Meta + % + Barra de progresso (SEMEAR e AGORACRED separados)
- Tabela de operadores SEMEAR
- Tabela de operadores AGORACRED
- Gráficos + Tabela de evolução diária separados por banco

Só é exibido quando o login tem banco='ADM'.

🔧 CORREÇÕES APLICADAS:
  1. Usa container_tabela_ranking para tabelas ADM
  2. fixed_columns ativo para fixar Foto, Banco, Operador
  3. page_size=10 para mostrar 10 operadores por página
  4. Try/except no layout para evitar crash
"""

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from datetime import date, datetime
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.cards import card_indicador, card_com_meta
from src.dashboard.components.tabelas import container_tabela_cheia, container_tabela_ranking

from src.dashboard.components.filtros import (
    criar_filtro_data_range,
    MESES,
    get_anos,
    OPCOES_FASES,
)

meses = MESES


def get_dashboard_adm_layout(
    nome_usuario: str, imagem_url: str = None, admissao: str = None
):
    """
    Constrói o layout do dashboard do ADM com as duas seções de banco e filtro de operador.
    
    🔧 CORREÇÃO: Try/except para evitar crash se algo falhar
    """
    try:
        # ============================================================
        # VALIDAÇÕES INICIAIS
        # ============================================================
        if not nome_usuario:
            nome_usuario = "Administrador"

        # Cria o menu lateral destacado como dashboard e com perfil adm
        sidebar = get_sidebar("dashboard", perfil="adm")

        # Bloco principal de conteúdo do painel ADM
        conteudo = html.Div(
            [
                # Renderiza o cabeçalho superior
                get_header(
                    nome_usuario,
                    imagem_url,
                    "Painel ADM — Visão Geral do Grupo",
                    admissao=admissao,
                    perfil="adm",
                ),
                # ── Filtros ──────────────────────────────────────
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label(
                                    "Mês/Ano",
                                    className="fw-bold mb-1",
                                    style={
                                        "color": "var(--text-muted)",
                                        "fontSize": "13px",
                                    },
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Select(
                                                id="filtro-mes-adm",
                                                options=meses,
                                                value=datetime.today().month,
                                                className="shadow-sm",
                                                style={"borderRadius": "8px"},
                                            ),
                                            width=6,
                                            className="pe-1",
                                        ),
                                        dbc.Col(
                                            dbc.Select(
                                                id="filtro-ano-adm",
                                                options=get_anos(),
                                                value=datetime.today().year,
                                                className="shadow-sm",
                                                style={"borderRadius": "8px"},
                                            ),
                                            width=6,
                                            className="ps-1",
                                        ),
                                    ]
                                ),
                            ],
                            width=3,
                        ),
                        dbc.Col(criar_filtro_data_range("adm"), width=4),
                        dbc.Col(
                            [
                                html.Label(
                                    "Atividade",
                                    className="fw-bold mb-1",
                                    style={
                                        "color": "var(--text-muted)",
                                        "fontSize": "13px",
                                    },
                                ),
                                dbc.Select(
                                    id="filtro-atividade-adm",
                                    options=[
                                        {"label": "🟢 Somente Ativos", "value": "ATIVO"},
                                        {"label": "⚪ Todos", "value": "TODOS"},
                                    ],
                                    value="ATIVO",
                                    className="shadow-sm",
                                    style={"borderRadius": "8px"},
                                ),
                            ],
                            width=2,
                        ),
                        dbc.Col(
                            [
                                html.Label(
                                    "Operador",
                                    className="fw-bold mb-1",
                                    style={
                                        "color": "var(--text-muted)",
                                        "fontSize": "13px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="filtro-operador-adm",
                                    placeholder="📊 Todos os Operadores",
                                    options=[],  # Será preenchido pelo callback
                                    value="TODOS",
                                    clearable=True,
                                    style={"borderRadius": "8px"},
                                ),
                            ],
                            width=3,
                        ),
                    ],
                    className="mb-4 align-items-start",
                ),
                # ── Linha 2 de Filtros: Contrato/Cliente + Faixa de Atraso ────────
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label(
                                    "Contrato / Cliente",
                                    className="fw-bold mb-1",
                                    style={
                                        "color": "var(--text-muted)",
                                        "fontSize": "13px",
                                    },
                                ),
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText(
                                            DashIconify(
                                                icon="lucide:search",
                                                width=16,
                                                color="var(--text-muted)",
                                            ),
                                            style={
                                                "backgroundColor": "white",
                                                "borderRight": "none",
                                            },
                                        ),
                                        dbc.Input(
                                            id="filtro-contrato-adm",
                                            type="text",
                                            placeholder="Buscar por contrato ou cliente...",
                                            style={"borderLeft": "none"},
                                            debounce=True,
                                        ),
                                    ],
                                    className="shadow-sm",
                                    style={"borderRadius": "8px"},
                                ),
                            ],
                            width=12,
                            md=5,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                html.Label(
                                    "Faixa de Atraso (SEMEAR)",
                                    className="fw-bold mb-1",
                                    style={
                                        "color": "var(--text-muted)",
                                        "fontSize": "13px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="filtro-faixa-adm",
                                    options=[
                                        {"label": "📊 Todas as faixas", "value": "todas"},
                                    ]
                                    + [
                                        {"label": f["label"], "value": f["value"]}
                                        for f in OPCOES_FASES
                                        if f["value"] != "todas"
                                    ],
                                    value="todas",
                                    clearable=False,
                                    placeholder="Selecione a faixa...",
                                    className="shadow-sm",
                                    style={"borderRadius": "8px"},
                                ),
                            ],
                            width=12,
                            md=4,
                            className="mb-3",
                        ),
                        dbc.Col(
                            [
                                html.Label(
                                    "\u00a0",
                                    className="fw-bold mb-1",
                                    style={
                                        "color": "var(--text-muted)",
                                        "fontSize": "13px",
                                    },
                                ),
                                html.Div(
                                    id="badge-filtros-ativos-adm",
                                    style={"display": "none"},
                                    children=html.Span(
                                        [
                                            DashIconify(
                                                icon="lucide:filter",
                                                width=12,
                                                className="me-1",
                                            ),
                                            "Filtros ativos",
                                        ],
                                        className="badge bg-warning text-dark",
                                    ),
                                ),
                            ],
                            width=12,
                            md=3,
                            className="mb-3",
                        ),
                    ],
                    className="mb-4 align-items-start",
                ),
                # ── LINHA 1: Cards SEMEAR e AGORACRED ────────────────
                dbc.Row(
                    [
                        dbc.Col(
                            id="card-semear",
                            children=card_com_meta(
                                titulo="FATURAMENTO SEMEAR",
                                valor="R$ 0,00",
                                meta="R$ 0,00",
                                percentual=0,
                                cor="#7e3d97",
                                id_valor="kpi-fat-semear",
                                id_meta="kpi-meta-semear",
                                id_percentual="kpi-percentual-semear",
                                id_barra="barra-progresso-semear",
                                id_sub_texto="kpi-fat-semear-anterior",
                            ),
                            width=12,
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            id="card-agoracred",
                            children=card_com_meta(
                                titulo="FATURAMENTO AGORACRED",
                                valor="R$ 0,00",
                                meta="R$ 0,00",
                                percentual=0,
                                cor="#10B981",
                                id_valor="kpi-fat-agoracred",
                                id_meta="kpi-meta-agoracred",
                                id_percentual="kpi-percentual-agoracred",
                                id_barra="barra-progresso-agoracred",
                                id_sub_texto="kpi-fat-agoracred-anterior",
                            ),
                            width=12,
                            md=6,
                            className="mb-3",
                        ),
                    ],
                    className="g-3 mb-0",
                ),
                # ── LINHA 2: Cards complementares (mesmo tamanho md=6) ──
                dbc.Row(
                    [
                        dbc.Col(
                            card_indicador(
                                titulo="OPERAÇÕES PAGAS",
                                valor_default="0",
                                id_valor="kpi-total-ops-adm",
                                cor_icone="#7e3d97",
                                icon_name="lucide:credit-card",
                                id_sub_texto="kpi-ops-adm-anterior",
                            ),
                            width=12,
                            md=6,
                            className="mb-3",
                        ),
                        dbc.Col(
                            card_indicador(
                                titulo="TICKET MÉDIO (GRUPO)",
                                valor_default="R$ 0,00",
                                id_valor="kpi-ticket-adm",
                                cor_icone="#7e3d97",
                                icon_name="lucide:ticket",
                            ),
                            width=12,
                            md=6,
                            className="mb-3",
                        ),
                    ],
                    className="g-3",
                ),
                # ── LINHA 2b: Operações Pagas e Ticket Médio SEPARADOS por banco ──
                dbc.Row(
                    [
                        dbc.Col(
                            card_indicador(
                                titulo="OPERAÇÕES PAGAS — SEMEAR",
                                valor_default="0",
                                id_valor="kpi-ops-semear",
                                cor_icone="#7e3d97",
                                icon_name="lucide:credit-card",
                                id_sub_texto="kpi-ops-semear-anterior",
                            ),
                            width=12,
                            md=3,
                            className="mb-3",
                        ),
                        dbc.Col(
                            card_indicador(
                                titulo="OPERAÇÕES PAGAS — AGORACRED",
                                valor_default="0",
                                id_valor="kpi-ops-agoracred",
                                cor_icone="#10B981",
                                icon_name="lucide:credit-card",
                                id_sub_texto="kpi-ops-agoracred-anterior",
                            ),
                            width=12,
                            md=3,
                            className="mb-3",
                        ),
                        dbc.Col(
                            card_indicador(
                                titulo="TICKET MÉDIO — SEMEAR",
                                valor_default="R$ 0,00",
                                id_valor="kpi-ticket-semear",
                                cor_icone="#7e3d97",
                                icon_name="lucide:ticket",
                                id_sub_texto="kpi-ticket-semear-anterior",
                            ),
                            width=12,
                            md=3,
                            className="mb-3",
                        ),
                        dbc.Col(
                            card_indicador(
                                titulo="TICKET MÉDIO — AGORACRED",
                                valor_default="R$ 0,00",
                                id_valor="kpi-ticket-agoracred",
                                cor_icone="#10B981",
                                icon_name="lucide:ticket",
                                id_sub_texto="kpi-ticket-agoracred-anterior",
                            ),
                            width=12,
                            md=3,
                            className="mb-3",
                        ),
                    ],
                    className="g-3",
                ),
                # ── GRÁFICOS DE EVOLUÇÃO DIÁRIA SEPARADOS ────────────
                html.Div(
                    [
                        html.Hr(style={"borderColor": "#7e3d97", "borderWidth": "2px"}),
                        html.H4(
                            [
                                DashIconify(
                                    icon="lucide:trending-up", width=22, className="me-2"
                                ),
                                "Evolução Diária por Banco",
                            ],
                            style={"color": "#7e3d97", "fontWeight": "700"},
                        ),
                    ],
                    className="mb-3 mt-2",
                ),
                # GRÁFICO SEMEAR
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.H5(
                                        "🟣 SEMEAR",
                                        style={
                                            "color": "#7e3d97",
                                            "fontWeight": "600",
                                            "marginBottom": "10px",
                                        },
                                    ),
                                    dcc.Loading(
                                        type="circle",
                                        children=dcc.Graph(
                                            id="grafico-evolucao-semear-adm",
                                            config={"displayModeBar": True},
                                        ),
                                    ),
                                ]
                            ),
                            width=12,
                            md=6,
                        ),
                        # GRÁFICO AGORACRED
                        dbc.Col(
                            html.Div(
                                [
                                    html.H5(
                                        "🟢 AGORACRED",
                                        style={
                                            "color": "#10B981",
                                            "fontWeight": "600",
                                            "marginBottom": "10px",
                                        },
                                    ),
                                    dcc.Loading(
                                        type="circle",
                                        children=dcc.Graph(
                                            id="grafico-evolucao-agoracred-adm",
                                            config={"displayModeBar": True},
                                        ),
                                    ),
                                ]
                            ),
                            width=12,
                            md=6,
                        ),
                    ],
                    className="mb-3",
                ),
                # TABELA DE VALORES DIÁRIOS (COM LINHA TOTAL ROXA)
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.H5(
                                        "📊 Valores Diários por Banco",
                                        className="m-0 font-weight-bold mb-3",
                                        style={"color": "var(--text-main)"},
                                    ),
                                    dcc.Loading(
                                        id="loading-tabela-evolucao",
                                        type="circle",
                                        children=[
                                            dash_table.DataTable(
                                                id="tabela-evolucao-diaria-adm",
                                                columns=[],
                                                data=[],
                                                markdown_options={"html": True},
                                                page_size=32,
                                                sort_action="native",
                                                style_table={
                                                    "overflowX": "auto",
                                                    "borderRadius": "8px",
                                                },
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
                                                        "if": {
                                                            "filter_query": '{dia} = "📊 TOTAL DO PERÍODO"'
                                                        },
                                                        "backgroundColor": "#e9d8fd",
                                                        "color": "#4a1d8c",
                                                        "fontWeight": "bold",
                                                        "fontSize": "14px",
                                                    },
                                                    {
                                                        "if": {"row_index": "odd"},
                                                        "backgroundColor": "#F9FAFB",
                                                    },
                                                ],
                                            )
                                        ],
                                    ),
                                ],
                                className="dashboard-panel",
                            ),
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                # ── Seção SEMEAR ────────────────────────────────────────────
                html.Div(
                    [
                        html.Hr(style={"borderColor": "#7e3d97", "borderWidth": "2px"}),
                        html.H4(
                            [
                                DashIconify(
                                    icon="lucide:building-2", width=22, className="me-2"
                                ),
                                "SEMEAR",
                            ],
                            style={"color": "#7e3d97", "fontWeight": "700"},
                        ),
                    ],
                    className="mb-3 mt-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            container_tabela_ranking(
                                "📊 Ranking de Operadores — SEMEAR",
                                "tabela-adm-semear",
                                fixed_cols=3,
                                page_size=10,
                            ),
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                # ── Tabela de Recebimento por Operador × Faixa de Atraso (SEMEAR) ────────
                html.Div(
                    [
                        html.Hr(
                            style={
                                "borderColor": "#7e3d97",
                                "borderWidth": "1px",
                                "opacity": "0.4",
                            }
                        ),
                        html.H5(
                            [
                                DashIconify(
                                    icon="lucide:layers", width=20, className="me-2"
                                ),
                                "Recebimento por Operador × Faixa de Atraso — SEMEAR",
                            ],
                            style={
                                "color": "#7e3d97",
                                "fontWeight": "700",
                                "marginBottom": "4px",
                            },
                        ),
                        html.P(
                            "Faturamento de cada operador por faixa de atraso no período selecionado.",
                            style={"color": "var(--text-muted)", "fontSize": "13px"},
                        ),
                    ],
                    className="mb-3 mt-1",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    dcc.Loading(
                                        type="circle",
                                        children=dash_table.DataTable(
                                            id="tabela-faixas-semear",
                                            columns=[],
                                            data=[],
                                            markdown_options={"html": True},
                                            page_size=10,
                                            sort_action="native",
                                            # fixed_columns removido para esta tabela
                                            style_table={
                                                "overflowX": "auto",
                                                "borderRadius": "8px",
                                                "minWidth": "100%",
                                            },
                                            style_header={
                                                "backgroundColor": "#7e3d97",
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
                                                "minWidth": "110px",
                                                "width": "140px",
                                                "maxWidth": "200px",
                                            },
                                            style_cell_conditional=[
                                                {
                                                    "if": {"column_id": "foto"},
                                                    "width": "65px",
                                                    "minWidth": "65px",
                                                    "maxWidth": "65px",
                                                },
                                                {
                                                    "if": {"column_id": "banco"},
                                                    "width": "110px",
                                                    "minWidth": "100px",
                                                    "maxWidth": "120px",
                                                },
                                                {
                                                    "if": {"column_id": "operador"},
                                                    "width": "140px",
                                                    "minWidth": "120px",
                                                    "maxWidth": "180px",
                                                },
                                            ],
                                            style_data_conditional=[
                                                {
                                                    "if": {"row_index": "odd"},
                                                    "backgroundColor": "#F9FAFB",
                                                },
                                                {
                                                    "if": {
                                                        "filter_query": '{operador} = "📊 TOTAL"'
                                                    },
                                                    "backgroundColor": "#e9d8fd",
                                                    "color": "#4a1d8c",
                                                    "fontWeight": "bold",
                                                },
                                            ],
                                        ),
                                    ),
                                ],
                                className="dashboard-panel",
                            ),
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                # ── Seção AGORACRED ─────────────────────────────────────────
                html.Div(
                    [
                        html.Hr(style={"borderColor": "#10B981", "borderWidth": "2px"}),
                        html.H4(
                            [
                                DashIconify(
                                    icon="lucide:building-2", width=22, className="me-2"
                                ),
                                "AGORACRED",
                            ],
                            style={"color": "#10B981", "fontWeight": "700"},
                        ),
                    ],
                    className="mb-3 mt-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            container_tabela_ranking(
                                "📊 Ranking de Operadores — AGORACRED",
                                "tabela-adm-agoracred",
                                fixed_cols=3,
                                page_size=10,
                            ),
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                dcc.Interval(
                    id="intervalo-atualizacao-adm", interval=300 * 1000, n_intervals=0
                ),
                # ── Seção EVOLUÇÃO / VARIAÇÃO DOS OPERADORES ───────────────────────────
                html.Div(
                    [
                        html.Hr(style={"borderColor": "#f59e0b", "borderWidth": "2px"}),
                        html.H4(
                            [
                                DashIconify(
                                    icon="lucide:trending-up", width=22, className="me-2"
                                ),
                                "Evolução dos Operadores — Variação vs Mês Anterior",
                            ],
                            style={"color": "#d97706", "fontWeight": "700"},
                        ),
                        html.P(
                            "Comparação de faturamento e % da meta entre o período selecionado e o mesmo período do mês anterior. "
                            "Quando há filtro de data, o período anterior é ajustado proporcionalmente.",
                            style={
                                "color": "var(--text-muted)",
                                "fontSize": "13px",
                                "marginTop": "4px",
                            },
                        ),
                    ],
                    className="mb-3 mt-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(id="resumo-evolucao-adm", className="mb-3"),
                                    dcc.Loading(
                                        type="circle",
                                        children=dash_table.DataTable(
                                            id="tabela-evolucao-operadores-adm",
                                            columns=[],
                                            data=[],
                                            markdown_options={"html": True},
                                            page_size=10,
                                            sort_action="native",
                                            fixed_columns=None,
                                            style_table={
                                                "overflowX": "auto",
                                                "borderRadius": "8px",
                                                "minWidth": "100%",
                                            },
                                            style_header={
                                                "backgroundColor": "#d97706",
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
                                                "minWidth": "110px",
                                                "width": "140px",
                                                "maxWidth": "200px",
                                            },
                                            style_cell_conditional=[
                                                {
                                                    "if": {"column_id": "foto"},
                                                    "width": "65px",
                                                    "minWidth": "65px",
                                                    "maxWidth": "65px",
                                                },
                                                {
                                                    "if": {"column_id": "banco"},
                                                    "width": "110px",
                                                    "minWidth": "100px",
                                                    "maxWidth": "120px",
                                                },
                                                {
                                                    "if": {"column_id": "operador"},
                                                    "width": "140px",
                                                    "minWidth": "120px",
                                                    "maxWidth": "180px",
                                                },
                                            ],
                                            style_data_conditional=[
                                                {
                                                    "if": {"row_index": "odd"},
                                                    "backgroundColor": "#FFF8F0",
                                                },
                                            ],
                                        ),
                                    ),
                                ],
                                className="dashboard-panel",
                            ),
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                # ── Seção TMA ───────────────────────────────────────────────
                html.Div(
                    [
                        html.Hr(style={"borderColor": "#0ea5e9", "borderWidth": "2px"}),
                        html.H4(
                            [
                                DashIconify(
                                    icon="lucide:phone-call", width=22, className="me-2"
                                ),
                                "Ranking de Acionamentos (TMA) — Mês Selecionado",
                            ],
                            style={"color": "#0ea5e9", "fontWeight": "700"},
                        ),
                        html.P(
                            "Dados gerados automaticamente pelo relatório de Acionamento por Operadores.",
                            style={
                                "color": "var(--text-muted)",
                                "fontSize": "13px",
                                "marginTop": "4px",
                            },
                        ),
                    ],
                    className="mb-3 mt-2",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    dcc.Loading(
                                        type="circle",
                                        children=dash_table.DataTable(
                                            id="tabela-tma-adm",
                                            columns=[],
                                            data=[],
                                            markdown_options={"html": True},
                                            page_size=10,
                                            sort_action="native",
                                            fixed_columns=None,
                                            style_table={
                                                "overflowX": "auto",
                                                "borderRadius": "8px",
                                                "minWidth": "100%",
                                            },
                                            style_header={
                                                "backgroundColor": "#0ea5e9",
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
                                                "minWidth": "110px",
                                                "width": "140px",
                                                "maxWidth": "200px",
                                            },
                                            style_cell_conditional=[
                                                {
                                                    "if": {"column_id": "foto"},
                                                    "width": "65px",
                                                    "minWidth": "65px",
                                                    "maxWidth": "65px",
                                                },
                                                {
                                                    "if": {"column_id": "banco"},
                                                    "width": "110px",
                                                    "minWidth": "100px",
                                                    "maxWidth": "120px",
                                                },
                                                {
                                                    "if": {"column_id": "operador"},
                                                    "width": "140px",
                                                    "minWidth": "120px",
                                                    "maxWidth": "180px",
                                                },
                                            ],
                                            style_data_conditional=[
                                                {
                                                    "if": {"row_index": "odd"},
                                                    "backgroundColor": "#F0F9FF",
                                                },
                                            ],
                                        ),
                                    ),
                                ],
                                className="dashboard-panel",
                            ),
                            width=12,
                        )
                    ],
                    className="mb-4",
                ),
                # Stores para armazenar valores calculados
                dcc.Store(id="store-meta-semear", data=0),
                dcc.Store(id="store-meta-agoracred", data=0),
            ],
            className="main-content",
            style={
                "marginLeft": "260px",
                "minHeight": "100vh",
                "padding": "24px 32px",
                "boxSizing": "border-box",
            },
        )

        return html.Div([sidebar, conteudo])
    
    except Exception as e:
        # ⚠️ ERRO AO CONSTRUIR LAYOUT
        print(f"[DASHBOARD_ADM] ❌ Erro ao construir layout: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Retorna um layout de erro
        return html.Div(
            [
                html.H2("❌ Erro ao carregar Dashboard ADM", 
                        style={"color": "red", "padding": "20px", "textAlign": "center"}),
                html.P(f"Detalhes: {str(e)}", style={"padding": "0 20px", "textAlign": "center"}),
                html.Div(
                    [
                        dbc.Button(
                            "🔄 Tentar novamente",
                            href="/dashboard",
                            color="primary",
                            className="me-2"
                        ),
                        dbc.Button(
                            "🏠 Voltar ao Login",
                            href="/",
                            color="secondary",
                        ),
                    ],
                    style={"textAlign": "center", "padding": "20px"}
                )
            ],
            style={"padding": "50px", "textAlign": "center"}
        )
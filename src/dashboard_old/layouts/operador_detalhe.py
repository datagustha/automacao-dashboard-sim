"""
LAYOUT DA TELA DE DETALHE DO OPERADOR
======================================
"""

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from datetime import datetime

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.tabelas import (
    container_tabela_simples,
    container_tabela_cheia,
    container_grafico,
)


def get_operador_detalhe_layout(
    nome_usuario: str,
    imagem_url: str = None,
    operador_selecionado: dict = None,
    banco: str = "SEMEAR",
    is_adm: bool = False,
):
    """Constrói a tela de detalhe do operador."""

    sidebar = get_sidebar("operadores", perfil="adm" if is_adm else "operador")

    nome_operador = (
        operador_selecionado.get("nome", nome_usuario)
        if operador_selecionado
        else nome_usuario
    )
    imagem_operador = (
        operador_selecionado.get("imagem", imagem_url)
        if operador_selecionado
        else imagem_url
    )

    # ================================================================
    # GRÁFICO DE FATURAMENTO POR MÊS
    # ================================================================
    grafico_componente = container_grafico(
        "Faturamento por Mês", "grafico-fase-operador"
    )

    # ================================================================
    # FILTROS
    # ================================================================
    from src.dashboard.components.filtros import (
        criar_filtro_data_range,
        MESES,
        get_anos,
    )

    ano_atual = datetime.now().year
    mes_atual = datetime.now().month

    anos = get_anos()
    meses = MESES

    # ================================================================
    # TABELA UNIFICADA (SUBSTITUI AS 3 TABELAS ANTIGAS)
    # ================================================================
    def container_tabela_unificada():
        """Tabela única que junta: Dia a Dia + Dia Útil + Meta Diária"""
        return html.Div(
            [
                html.H5(
                    "📅 Recebimento Diário - Meta Diária",
                    className="m-0 font-weight-bold mb-2",
                    style={"color": "var(--text-main)"},
                ),
                # Resumo de dias (preenchido pelo callback)
                html.Div(
                    id="info-meta-diaria",
                    className="mb-3",
                    style={"fontSize": "13px", "fontWeight": "500"},
                ),
                dcc.Loading(
                    id="loading-tabela-unificada",
                    type="circle",
                    children=[
                        dash_table.DataTable(
                            id="tabela-unificada",
                            columns=[
                                {"name": "Dia", "id": "dia", "type": "numeric"},
                                {
                                    "name": "Dia Útil",
                                    "id": "dia_util",
                                    "type": "numeric",
                                },
                                {"name": "Data", "id": "data", "type": "text"},
                                {
                                    "name": "Quantidade",
                                    "id": "quantidade",
                                    "type": "numeric",
                                },
                                {
                                    "name": "Faturamento",
                                    "id": "faturamento",
                                    "type": "text",
                                },
                                {
                                    "name": "Meta Diária",
                                    "id": "meta_diaria",
                                    "type": "text",
                                },
                                {
                                    "name": "Bateu Meta?",
                                    "id": "bateu_meta",
                                    "type": "text",
                                },
                            ],
                            page_size=32,
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
                                # Zebra (menor prioridade - vem primeiro)
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "#F9FAFB",
                                },
                                # Linhas com meta batida: verde (sobrescreve zebra)
                                {
                                    "if": {"filter_query": '{bateu_meta} = "✅ Sim"'},
                                    "backgroundColor": "#d4edda",
                                    "color": "#155724",
                                    "fontWeight": "500",
                                },
                                # Linha TOTAL em ROXO (maior prioridade - vem por último)
                                {
                                    "if": {"filter_query": '{dia} = "TOTAL"'},
                                    "backgroundColor": "#e9d8fd",
                                    "color": "#4a1d8c",
                                    "fontWeight": "bold",
                                    "fontSize": "14px",
                                },
                            ],
                            css=[
                                {
                                    "selector": ".dash-spreadsheet td.dash-cell--focused",
                                    "rule": "outline: none !important;",
                                }
                            ],
                        )
                    ],
                ),
            ],
            className="dashboard-panel",
        )

    # ================================================================
    # TABELA SEMANAL (COM LINHA TOTAL ROXA)
    # ================================================================
    def container_tabela_semanas():
        return html.Div(
            [
                html.H5(
                    "📆 Faturamento por Semana",
                    className="m-0 font-weight-bold mb-3",
                    style={"color": "var(--text-main)"},
                ),
                dcc.Loading(
                    id="loading-tabela-semanas",
                    type="circle",
                    children=[
                        dash_table.DataTable(
                            id="tabela-semanas",
                            columns=[
                                {"name": "Semana", "id": "semana", "type": "text"},
                                {"name": "Período", "id": "periodo", "type": "text"},
                                {
                                    "name": "Faturamento Total",
                                    "id": "faturamento",
                                    "type": "text",
                                },
                            ],
                            page_size=6,
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
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "#F9FAFB",
                                },
                                # linha de total em roxo
                                {
                                    "if": {"filter_query": '{semana} = "TOTAL"'},
                                    "fontWeight": "700",
                                    "backgroundColor": "#e9d8fd",
                                    "color": "#4a1d8c",
                                },
                            ],
                        )
                    ],
                ),
            ],
            className="dashboard-panel",
        )

    # ================================================================
    # LAYOUT PRINCIPAL
    # ================================================================
    # Define o titulo do header: se for ADM, mostra ambos os bancos unidos por hifen, senao mostra o banco individual
    titulo_header = (
        "📊 Desempenho - SEMEAR - AGORACRED" if is_adm else f"📊 Desempenho - {banco}"
    )
    # Obtem a data de admissao do operador visualizado para exibir no header (se fornecido)
    admissao_header = (
        operador_selecionado.get("admissao") if operador_selecionado else None
    )

    conteudo = html.Div(
        [
            # Renderiza o header superior com o titulo adaptado, a admissao e o perfil correto do usuario logado/visualizado
            get_header(
                nome_operador,
                imagem_operador,
                titulo_header,
                admissao=admissao_header,
                perfil="adm" if is_adm else "operador",
            ),
            # ── Tempo de casa ────────────────────────────────────────
            html.Div(
                id="tempo-de-casa",
                className="mb-4 px-1",
                style={"fontSize": "14px", "color": "var(--text-muted)"},
            ),
            # --- Bloco exclusivo ADM (sempre presente para o Dash, mas visível apenas para ADM) ---
            html.Div(
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            [
                                html.H5(
                                    "Escolha o banco e o operador",
                                    className="mb-4",
                                    style={
                                        "color": "var(--text-main)",
                                        "fontWeight": "700",
                                    },
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Label(
                                                    "Banco",
                                                    className="fw-bold mb-1",
                                                    style={
                                                        "color": "var(--text-muted)",
                                                        "fontSize": "13px",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="adm-banco-select",
                                                    options=[
                                                        {
                                                            "label": "🟣 SEMEAR",
                                                            "value": "SEMEAR",
                                                        },
                                                        {
                                                            "label": "🔵 AGORACRED",
                                                            "value": "AGORACRED",
                                                        },
                                                    ],
                                                    value=banco,
                                                    clearable=False,
                                                    style={"borderRadius": "8px"},
                                                ),
                                            ],
                                            width=12,
                                            md=3,
                                        ),
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
                                                dcc.Dropdown(
                                                    id="adm-filtro-atividade",
                                                    options=[
                                                        {
                                                            "label": "🟢 Ativos",
                                                            "value": "ativo",
                                                        },
                                                        {
                                                            "label": "⚪ Todos",
                                                            "value": "todos",
                                                        },
                                                    ],
                                                    value="ativo",
                                                    clearable=False,
                                                    style={"borderRadius": "8px"},
                                                ),
                                            ],
                                            width=12,
                                            md=2,
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
                                                    id="adm-operador-select",
                                                    options=[],
                                                    value=(
                                                        operador_selecionado.get(
                                                            "login", "TODOS"
                                                        )
                                                        if operador_selecionado
                                                        else "TODOS"
                                                    ),
                                                    placeholder="Selecione um operador...",
                                                    clearable=True,
                                                    style={"borderRadius": "8px"},
                                                ),
                                            ],
                                            width=12,
                                            md=4,
                                        ),
                                    ]
                                ),
                            ],
                            className="dashboard-panel mb-4",
                        ),
                        width=12,
                    )
                ),
                style={"display": "block"} if is_adm else {"display": "none"},
            ),
            # --------------------------
            # Filtros de Mês/Ano e Range
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
                                            id="filtro-mes-operador",
                                            options=meses,
                                            value=mes_atual,
                                            className="shadow-sm",
                                            style={"borderRadius": "8px"},
                                        ),
                                        width=6,
                                        className="pe-1",
                                    ),
                                    dbc.Col(
                                        dbc.Select(
                                            id="filtro-ano-operador",
                                            options=anos,
                                            value=ano_atual,
                                            className="shadow-sm",
                                            style={"borderRadius": "8px"},
                                        ),
                                        width=6,
                                        className="ps-1",
                                    ),
                                ]
                            ),
                        ],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        criar_filtro_data_range("operador"),
                        width=12,
                        md=4,
                        className="mb-3",
                    ),
                ],
                className="mb-4 align-items-start",
            ),
            # ── TABELA UNIFICADA (SUBSTITUI AS 3 TABELAS ANTIGAS) ────
            dbc.Row(
                [dbc.Col(container_tabela_unificada(), width=12)], className="mb-4"
            ),
            # ── TABELA FATURAMENTO POR SEMANA ────────────────────────
            dbc.Row([dbc.Col(container_tabela_semanas(), width=12)], className="mb-4"),
            # ── TABELA MÊS A MÊS ──────────────────────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H5(
                                    "📈 Resultado Mês a Mês",
                                    className="m-0 font-weight-bold mb-3",
                                    style={"color": "var(--text-main)"},
                                ),
                                dcc.Loading(
                                    id="loading-tabela-mes-mes",
                                    type="circle",
                                    children=[
                                        dash_table.DataTable(
                                            id="tabela-mes-mes",
                                            page_size=14,
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
                                                # Linha TOTAL em roxo (APENAS TOTAL, sem verde/vermelho)
                                                {
                                                    "if": {
                                                        "filter_query": '{nome_mes} = "TOTAL"'
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
            # ── TABELA DE VARIAÇÃO (Atual vs Mês Anterior) ────────────
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Hr(
                                    style={
                                        "borderColor": "#d97706",
                                        "borderWidth": "2px",
                                        "marginBottom": "12px",
                                    }
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            "📊 Variação vs Mês Anterior",
                                            style={
                                                "fontSize": "14px",
                                                "fontWeight": "700",
                                                "color": "#d97706",
                                            },
                                        ),
                                        html.Span(
                                            " — comparação do período selecionado com o mês anterior",
                                            style={
                                                "fontSize": "12px",
                                                "color": "var(--text-muted)",
                                                "marginLeft": "8px",
                                            },
                                        ),
                                    ],
                                    style={"marginBottom": "8px"},
                                ),
                                html.Div(
                                    id="resumo-evolucao-detalhe", className="mb-3"
                                ),
                                dcc.Loading(
                                    type="circle",
                                    children=[
                                        dash_table.DataTable(
                                            id="tabela-evolucao-detalhe",
                                            columns=[{"name": " ", "id": "_placeholder"}],
                                            data=[],
                                            markdown_options={"html": True},
                                            page_size=20,
                                            sort_action="native",
                                            fixed_columns={"headers": True, "data": 1},
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
                                                "padding": "8px 12px",
                                                "borderBottom": "1px solid #E5E7EB",
                                                "fontSize": "13px",
                                                "minWidth": "110px",
                                                "width": "140px",
                                                "maxWidth": "200px",
                                            },
                                            style_cell_conditional=[
                                                {
                                                    "if": {"column_id": "periodo"},
                                                    "width": "110px",
                                                    "minWidth": "100px",
                                                    "maxWidth": "130px",
                                                },
                                            ],
                                            style_data_conditional=[
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
            # ── TABELA DE PERFORMANCE ─────────────────────────────────
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Div(
                                    id="info-dias-operador",
                                    className="text-muted mb-2 px-1",
                                    style={"fontSize": "13px", "fontWeight": "500"},
                                ),
                                container_tabela_cheia(
                                    "tabela-performance-operador",
                                    "🎯 Performance do Operador",
                                    fixed_cols=1,
                                ),
                            ]
                        ),
                        width=12,
                    )
                ],
                className="mb-4",
            ),
            # ── GRÁFICO MENSAL ────────────────────────────────────────
            dbc.Row([dbc.Col(grafico_componente, width=12)], className="mb-4"),
            dcc.Interval(id="intervalo-operador", interval=300 * 1000, n_intervals=0),
            dcc.Store(id="operador-selecionado-store", data=operador_selecionado),
            dcc.Store(id="banco-operador-store", data=banco),
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

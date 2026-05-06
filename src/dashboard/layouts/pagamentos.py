"""
LAYOUT EXCLUSIVAMENTE PARA VISUALIZAÇÃO DE PAGAMENTOS
======================================================
- Operador: vê só seus próprios pagamentos do mês selecionado
- ADM: vê todos os pagamentos do banco selecionado por mês
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.tabelas import container_tabela_cheia

# ================================================================
# LISTA COMPLETA DE FASES EM ORDEM
# ================================================================
OPCOES_FASES = [
    {"label": "📊 Todas as fases", "value": "TODAS"},
    {"label": "📈 Fase 10 a 30", "value": "Fase 10 a 30"},
    {"label": "📈 Fase 31 a 60", "value": "Fase 31 a 60"},
    {"label": "📈 Fase 61 a 90", "value": "Fase 61 a 90"},
    {"label": "📈 Fase 91 a 120", "value": "Fase 91 a 120"},
    {"label": "📈 Fase 121 a 180", "value": "Fase 121 a 180"},
    {"label": "📈 Fase 181 a 240", "value": "Fase 181 a 240"},
    {"label": "📈 Fase 241 a 360", "value": "Fase 241 a 360"},
    {"label": "📈 Fase 361 a 720", "value": "Fase 361 a 720"},
    {"label": "📈 Fase 721 a 1080", "value": "Fase 721 a 1080"},
    {"label": "📈 Fase 1081 a 1440", "value": "Fase 1081 a 1440"},
    {"label": "📈 Fase 1081 a 1800", "value": "Fase 1081 a 1800"},
    {"label": "📈 Fase 1441 a 1800", "value": "Fase 1441 a 1800"},
    {"label": "📈 Fase 1801 a 9999", "value": "Fase 1801 a 9999"},
    {"label": "🚫 Fora da fase", "value": "Fora da fase"},
]

def get_pagamentos_layout(nome_usuario: str, imagem_url: str = None, perfil: str = 'operador'):
    """
    Constrói o layout de pagamentos.
    
    Args:
        nome_usuario: Nome do usuário logado
        imagem_url: URL da foto
        perfil: 'adm' ou 'operador' — ADM tem seletor de banco
    """
    sidebar = get_sidebar("pagamentos", perfil=perfil)

    # FILTROS: MÊS e ANO (para ambos perfis)
    from datetime import datetime
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    
    filtros_data = dbc.Row(
        [
            dbc.Col(
                [
                    html.Label("Mês", className="fw-bold mb-1",
                               style={"color": "var(--text-muted)", "fontSize": "13px"}),
                    dcc.Dropdown(
                        id="filtro-mes-pgtos",
                        options=[
                            {"label": "Janeiro", "value": 1},
                            {"label": "Fevereiro", "value": 2},
                            {"label": "Março", "value": 3},
                            {"label": "Abril", "value": 4},
                            {"label": "Maio", "value": 5},
                            {"label": "Junho", "value": 6},
                            {"label": "Julho", "value": 7},
                            {"label": "Agosto", "value": 8},
                            {"label": "Setembro", "value": 9},
                            {"label": "Outubro", "value": 10},
                            {"label": "Novembro", "value": 11},
                            {"label": "Dezembro", "value": 12},
                        ],
                        value=mes_atual,
                        clearable=False,
                        style={"borderRadius": "8px", "minWidth": "150px"}
                    ),
                ],
                width=2
            ),
            dbc.Col(
                [
                    html.Label("Ano", className="fw-bold mb-1",
                               style={"color": "var(--text-muted)", "fontSize": "13px"}),
                    dcc.Dropdown(
                        id="filtro-ano-pgtos",
                        options=[
                            {"label": str(ano), "value": ano} for ano in range(2023, ano_atual + 2)
                        ],
                        value=ano_atual,
                        clearable=False,
                        style={"borderRadius": "8px", "minWidth": "100px"}
                    ),
                ],
                width=2
            ),
            # FILTRO DE FASE - MULTIPLA SELEÇÃO
            dbc.Col(
                [
                    html.Label("Fase (múltipla seleção)", className="fw-bold mb-1",
                               style={"color": "var(--text-muted)", "fontSize": "13px"}),
                    dcc.Dropdown(
                        id="filtro-fase-pgtos",
                        options=OPCOES_FASES,
                        value=["TODAS"],
                        multi=True,
                        clearable=True,
                        placeholder="Selecione uma ou mais fases...",
                        style={"borderRadius": "8px", "minWidth": "250px"}
                    ),
                ],
                width=4
            ),
        ],
        className="mb-3 align-items-end"
    )

    # Seletor de banco — só aparece para ADM
    seletor_banco = html.Div(
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Banco", className="fw-bold mb-1",
                                   style={"color": "var(--text-muted)", "fontSize": "13px"}),
                        dcc.Dropdown(
                            id="banco-selecionado-pgtos",
                            options=[
                                {"label": "🟣 SEMEAR",    "value": "SEMEAR"},
                                {"label": "🔵 AGORACRED", "value": "AGORACRED"},
                            ],
                            value="SEMEAR",
                            clearable=False,
                            style={"borderRadius": "8px", "minWidth": "200px"}
                        ),
                    ],
                    width="auto"
                ),
                dbc.Col(
                    [
                        html.Label("Atividade", className="fw-bold mb-1", 
                                   style={"color": "var(--text-muted)", "fontSize": "13px"}),
                        dcc.Dropdown(
                            id="adm-filtro-atividade-pgtos",
                            options=[
                                {"label": "🟢 Apenas Ativos", "value": "ativo"},
                                {"label": "⚪ Todos", "value": "todos"},
                            ],
                            value="ativo",
                            clearable=False,
                            style={"borderRadius": "8px", "minWidth": "150px"}
                        ),
                    ],
                    width="auto"
                ),
            ],
            className="mb-3 align-items-end"
        )
    ) if perfil == 'adm' else html.Div(
        [
            dcc.Dropdown(id="banco-selecionado-pgtos", value="SEMEAR", options=[], style={"display": "none"}),
            dcc.Dropdown(id="adm-filtro-atividade-pgtos", value="ativo", options=[], style={"display": "none"})
        ]
    )

    conteudo = html.Div(
        [
            get_header(nome_usuario, imagem_url, "📋 Controle Geral de Pagamentos"),

            # Filtros de data e fase
            filtros_data,

            # Seletor de banco (ADM)
            seletor_banco,

            # Filtro de texto
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup([
                            dbc.InputGroupText(DashIconify(icon="lucide:search", width=18, color="var(--text-muted)"), 
                                             style={"backgroundColor": "white", "borderRight": "none"}),
                            dbc.Input(id='filtro-texto-pgtos-completo', type='text', 
                                     placeholder="🔍 Filtrar por Contrato, Cliente ou Fase...", 
                                     style={"borderLeft": "none"})
                        ], className="shadow-sm", style={"borderRadius": "8px"}),
                        width=12
                    )
                ], className="mb-3"
            ),
            
            # Tabela de pagamentos
            dbc.Row([dbc.Col(container_tabela_cheia("tabela-pagamentos-completa"), width=12)]),

            dcc.Interval(id='intervalo-atualizacao-pgtos', interval=300*1000, n_intervals=0)
        ],
        className="main-content"
    )

    return html.Div([sidebar, conteudo])
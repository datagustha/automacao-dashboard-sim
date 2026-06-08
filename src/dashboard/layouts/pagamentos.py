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

from src.dashboard.components.filtros import criar_filtro_data_range, MESES, get_anos, OPCOES_FASES_PGTOS

# Usaremos o OPCOES_FASES_PGTOS
OPCOES_FASES = OPCOES_FASES_PGTOS

def get_pagamentos_layout(nome_usuario: str, imagem_url: str = None, perfil: str = 'operador', admissao: str = None):
    """
    Constrói o layout de pagamentos.
    
    Args:
        nome_usuario: Nome do usuário logado
        imagem_url: URL da foto
        perfil: 'adm' ou 'operador' — ADM tem seletor de banco
        admissao: Data de admissão do usuário logado
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
                    html.Label("Mês/Ano", className="fw-bold mb-1", style={"color": "var(--text-muted)", "fontSize": "13px"}),
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(
                                id="filtro-mes-pgtos",
                                options=MESES,
                                value=mes_atual,
                                clearable=False,
                                style={"borderRadius": "8px"}
                            ), width=6, className="pe-1"
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="filtro-ano-pgtos",
                                options=get_anos(),
                                value=ano_atual,
                                clearable=False,
                                style={"borderRadius": "8px"}
                            ), width=6, className="ps-1"
                        )
                    ])
                ],
                width=3
            ),
            dbc.Col(
                criar_filtro_data_range("pgtos"),
                width=4
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
                width=5
            ),
        ],
        className="mb-4 align-items-start"
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

    # Bloco de conteudo principal da pagina de listagem de pagamentos
    conteudo = html.Div(
        [
            # Renderiza o header superior com o tempo de casa e o perfil correto do usuario logado
            get_header(nome_usuario, imagem_url, "📋 Controle Geral de Pagamentos", admissao=admissao, perfil=perfil),

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
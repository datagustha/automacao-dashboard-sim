"""
LAYOUT EXCLUSIVAMENTE PARA VISUALIZAÇÃO DE PAGAMENTOS
======================================================
- Operador: vê só seus próprios pagamentos
- ADM: vê todos os pagamentos do banco selecionado (SEMEAR ou AGORACRED)
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.tabelas import container_tabela_cheia

def get_pagamentos_layout(nome_usuario: str, imagem_url: str = None, perfil: str = 'operador'):
    """
    Constrói o layout de pagamentos.
    
    Args:
        nome_usuario: Nome do usuário logado
        imagem_url: URL da foto
        perfil: 'adm' ou 'operador' — ADM tem seletor de banco
    """
    sidebar = get_sidebar("pagamentos", perfil=perfil)

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
            ],
            className="mb-3 align-items-end"
        )
    ) if perfil == 'adm' else html.Div(
        # Para operador: componente oculto mas presente (o callback precisa do ID)
        dcc.Dropdown(id="banco-selecionado-pgtos", value="SEMEAR",
                     options=[], style={"display": "none"})
    )

    conteudo = html.Div(
        [
            get_header(nome_usuario, imagem_url, "Controle Geral de Pagamentos"),

            # Seletor de banco (ADM) ou vazio (operador)
            seletor_banco,

            # Filtro de texto
            dbc.Row(
                [
                    dbc.Col(
                        dbc.InputGroup([
                            dbc.InputGroupText(DashIconify(icon="lucide:search", width=18, color="var(--text-muted)"), style={"backgroundColor": "white", "borderRight": "none"}),
                            dbc.Input(id='filtro-texto-pgtos-completo', type='text', placeholder="Filtrar por qualquer dado (Ex: Fase, Nome)...", style={"borderLeft": "none"})
                        ], className="shadow-sm", style={"borderRadius": "8px"}),
                        width=12
                    )
                ]
            ),
            
            # Tabela de pagamentos
            dbc.Row([dbc.Col(container_tabela_cheia("tabela-pagamentos-completa"), width=12)]),

            dcc.Interval(id='intervalo-atualizacao-pgtos', interval=300*1000, n_intervals=0)
        ],
        className="main-content"
    )

    return html.Div([sidebar, conteudo])

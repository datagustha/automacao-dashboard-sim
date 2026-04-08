"""
LAYOUT EXCLUSIVAMENTE PARA VISUALIZAÇÃO DE PAGAMENTOS
======================================================
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.tabelas import container_tabela_cheia

def get_pagamentos_layout(nome_usuario: str, imagem_url: str = None):
    # Sidebar Dinâmico com foco na guia Pagamentos
    sidebar = get_sidebar("pagamentos")

    conteudo = html.Div(
        [
            get_header(nome_usuario, imagem_url, "Controle Geral de Pagamentos"),

            # Filtro isolado para focar tudo
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
            
            # NOSSA TABELA GIGANTE
            dbc.Row([dbc.Col(container_tabela_cheia("tabela-pagamentos-completa"), width=12)]),

            dcc.Interval(id='intervalo-atualizacao-pgtos', interval=300*1000, n_intervals=0)
        ],
        className="main-content"
    )

    return html.Div([sidebar, conteudo])

"""
LAYOUT DA TELA DE DETALHE DO OPERADOR
======================================
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.tabelas import container_tabela_simples, container_tabela_cheia, container_grafico


def get_operador_detalhe_layout(nome_usuario: str, imagem_url: str = None, operador_selecionado: dict = None, banco: str = "SEMEAR"):
    """Constrói a tela de detalhe do operador."""
    
    sidebar = get_sidebar("operador", active_link="operadores")
    
    nome_operador = operador_selecionado.get('nome', nome_usuario) if operador_selecionado else nome_usuario
    imagem_operador = operador_selecionado.get('imagem', imagem_url) if operador_selecionado else imagem_url
    
    # ================================================================
    # GRÁFICO DE FATURAMENTO POR MÊS
    # ================================================================
    grafico_componente = container_grafico("Faturamento por Mês", "grafico-fase-operador")
    
    # ================================================================
    # FILTROS
    # ================================================================
    anos = [{"label": str(ano), "value": ano} for ano in range(2024, 2027)]
    meses = [
        {"label": "Janeiro", "value": 1}, {"label": "Fevereiro", "value": 2},
        {"label": "Março", "value": 3}, {"label": "Abril", "value": 4},
        {"label": "Maio", "value": 5}, {"label": "Junho", "value": 6},
        {"label": "Julho", "value": 7}, {"label": "Agosto", "value": 8},
        {"label": "Setembro", "value": 9}, {"label": "Outubro", "value": 10},
        {"label": "Novembro", "value": 11}, {"label": "Dezembro", "value": 12}
    ]
    
    conteudo = html.Div(
        [
            get_header(nome_operador, imagem_operador, f"📊 Desempenho - {banco}"),
            
            # Filtros
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Select(
                            id="filtro-mes-operador",
                            options=meses,
                            value=4,
                            className="shadow-sm",
                            style={"borderRadius": "8px"}
                        ),
                        width=3, className="mb-3"
                    ),
                    dbc.Col(
                        dbc.Select(
                            id="filtro-ano-operador",
                            options=anos,
                            value=2026,
                            className="shadow-sm",
                            style={"borderRadius": "8px"}
                        ),
                        width=2, className="mb-3"
                    ),
                ],
                className="mb-4"
            ),
            
            # Tabela Dia a Dia
            dbc.Row([
                dbc.Col(
                    container_tabela_simples("tabela-dia-dia", "📅 Recebimento Dia a Dia"),
                    width=12
                )
            ], className="mb-4"),
            
            # Tabela Dia Útil
            dbc.Row([
                dbc.Col(
                    container_tabela_simples("tabela-dia-util", "📊 Recebimento por Dia Útil"),
                    width=12
                )
            ], className="mb-4"),
            
            # Tabela Mês a Mês
            dbc.Row([
                dbc.Col(
                    container_tabela_simples("tabela-mes-mes", "📈 Resultado Mês a Mês"),
                    width=12
                )
            ], className="mb-4"),
            
            # Tabela de Performance
            dbc.Row([
                dbc.Col(
                    container_tabela_cheia("tabela-performance-operador", "🎯 Performance do Operador"),
                    width=12
                )
            ], className="mb-4"),
            
            # GRÁFICO
            dbc.Row([
                dbc.Col(grafico_componente, width=12)
            ], className="mb-4"),
            
            dcc.Interval(id='intervalo-operador', interval=300*1000, n_intervals=0),
            dcc.Store(id='operador-selecionado-store', data=operador_selecionado),
            dcc.Store(id='banco-operador-store', data=banco),
        ],
        className="main-content"
    )
    
    return html.Div([sidebar, conteudo])
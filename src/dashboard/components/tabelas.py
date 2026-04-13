"""
COMPONENTE DE TABELA E GRAFICO INTERATIVOS
==========================================
"""

from dash import dash_table, dcc, html

def container_grafico(titulo: str, id_grafico: str):
    """Container para gráficos com título e loading."""
    return html.Div(
        [
            html.H5(titulo, className="m-0 font-weight-bold mb-3", style={"color": "var(--text-main)"}),
            dcc.Loading(
                id=f"loading-{id_grafico}",
                type="circle",
                children=[dcc.Graph(id=id_grafico, style={'height': '350px'})]
            )
        ],
        className="dashboard-panel"
    )


def container_tabela(id_tabela: str):
    """Tabela Menor (Últimos 5 Pagtos) para a página Dashboard Principal."""
    return html.Div(
        [
            html.H5("📋 Relação de Pagamentos Recentes", className="m-0 font-weight-bold mb-3", style={"color": "var(--text-main)"}),
            dash_table.DataTable(
                id=id_tabela,
                page_size=5, 
                sort_action="native",
                style_table={'overflowX': 'auto', 'borderRadius': '8px'}, 
                style_header={
                    'backgroundColor': 'var(--purple-main)', 
                    'color': 'white', 
                    'fontWeight': '600',
                    'textAlign': 'left',
                    'border': 'none',
                    'padding': '12px'
                },
                style_cell={'textAlign': 'left', 'padding': '12px', 'borderBottom': '1px solid #E5E7EB', 'color': 'var(--text-main)'},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#F9FAFB'}]
            )
        ],
        className="dashboard-panel"
    )


def container_tabela_cheia(id_tabela: str, titulo: str = "💸 Detalhamento de Operações"):
    """
    Tabela Massiva Paginada com título personalizado.
    
    Args:
        id_tabela: ID único para o callback
        titulo: Título da tabela (padrão: "💸 Detalhamento de Operações")
    """
    return html.Div(
        [
            html.H5(titulo, className="m-0 font-weight-bold mb-3", style={"color": "var(--text-main)"}),
            dcc.Loading(
                id=f"loading-{id_tabela}",
                type="circle",
                children=[
                    dash_table.DataTable(
                        id=id_tabela,
                        page_size=30,
                        sort_action="native",
                        filter_action="native",
                        markdown_options={"html": True},
                        style_table={'overflowX': 'auto', 'borderRadius': '12px'}, 
                        style_header={
                            'backgroundColor': 'var(--purple-main)', 
                            'color': 'white', 
                            'fontWeight': '600',
                            'textAlign': 'center',
                            'padding': '15px'
                        },
                        style_cell={
                            'textAlign': 'center', 'padding': '12px', 
                            'borderBottom': '1px solid #E5E7EB', 'color': 'var(--text-main)', 'fontSize': '14px'
                        },
                        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#F9FAFB'}]
                    )
                ]
            )
        ],
        className="dashboard-panel mt-4"
    )


def container_tabela_simples(id_tabela: str, titulo: str):
    """
    Tabela simples sem filtro nativo (para dia a dia, mês a mês).
    
    Args:
        id_tabela: ID único para o callback
        titulo: Título da tabela
    """
    return html.Div(
        [
            html.H5(titulo, className="m-0 font-weight-bold mb-3", style={"color": "var(--text-main)"}),
            dcc.Loading(
                id=f"loading-{id_tabela}",
                type="circle",
                children=[
                    dash_table.DataTable(
                        id=id_tabela,
                        page_size=31,  # máximo de dias em um mês
                        sort_action="native",
                        style_table={'overflowX': 'auto', 'borderRadius': '8px'},
                        style_header={
                            'backgroundColor': 'var(--purple-main)',
                            'color': 'white',
                            'fontWeight': '600',
                            'textAlign': 'center',
                            'padding': '10px'
                        },
                        style_cell={
                            'textAlign': 'center',
                            'padding': '10px',
                            'borderBottom': '1px solid #E5E7EB',
                            'color': 'var(--text-main)',
                            'fontSize': '13px'
                        },
                        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#F9FAFB'}]
                    )
                ]
            )
        ],
        className="dashboard-panel"
    )
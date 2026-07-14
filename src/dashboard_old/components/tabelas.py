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
                columns=[],
                data=[],
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


def container_tabela_cheia(id_tabela: str, titulo: str = "💸 Detalhamento de Operações", fixed_cols: int = 0, page_size: int = 30):
    """
    Tabela Massiva Paginada com título personalizado.
    
    🔧 CORREÇÃO: fixed_columns funciona com columns pré-definidas
    - Para fixed_cols > 0, a tabela espera que as primeiras 'fixed_cols' colunas sejam fixadas
    - O callback deve retornar columns com essa ordem
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
                        columns=[],
                        data=[],
                        page_size=page_size,
                        sort_action="native",
                        filter_action="native",
                        markdown_options={"html": True},
                        fixed_columns={'headers': True, 'data': fixed_cols} if fixed_cols > 0 else None,
                        style_table={'overflowX': 'auto', 'borderRadius': '12px', 'minWidth': '100%'}, 
                        style_header={
                            'backgroundColor': 'var(--purple-main)', 
                            'color': 'white', 
                            'fontWeight': '600',
                            'textAlign': 'center',
                            'padding': '15px'
                        },
                        style_cell={
                            'textAlign': 'center', 'padding': '12px', 
                            'borderBottom': '1px solid #E5E7EB', 'color': 'var(--text-main)', 'fontSize': '14px',
                            'minWidth': '120px', 'width': '150px', 'maxWidth': '220px',
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'foto'},
                                'width': '65px', 'minWidth': '65px', 'maxWidth': '65px',
                            },
                            {
                                'if': {'column_id': 'banco'},
                                'width': '110px', 'minWidth': '100px', 'maxWidth': '130px',
                            },
                            {
                                'if': {'column_id': 'operador'},
                                'width': '140px', 'minWidth': '120px', 'maxWidth': '180px',
                            },
                            {
                                'if': {'column_id': 'login'},
                                'width': '140px', 'minWidth': '120px', 'maxWidth': '180px',
                            },
                            {
                                'if': {'column_id': 'faturamento'},
                                'width': '130px', 'minWidth': '110px', 'maxWidth': '160px',
                            },
                            {
                                'if': {'column_id': 'meta'},
                                'width': '130px', 'minWidth': '110px', 'maxWidth': '160px',
                            },
                            {
                                'if': {'column_id': 'falta_70'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'falta_80'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'falta_90'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'projecao'},
                                'width': '130px', 'minWidth': '110px', 'maxWidth': '160px',
                            },
                        ],
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
                        columns=[],
                        data=[],
                        page_size=31,
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


def container_tabela_ranking(titulo: str, id_tabela: str, fixed_cols: int = 3, page_size: int = 10):
    """
    Tabela específica para Ranking de Operadores com colunas fixas (Foto, Banco, Operador).
    
    Args:
        titulo: Título da tabela
        id_tabela: ID único para o callback
        fixed_cols: Quantidade de colunas a fixar (padrão: 3)
        page_size: Quantidade de linhas por página (padrão: 10)
    
    🔧 CORREÇÃO: fixed_columns funciona com columns pré-definidas
    - As primeiras 'fixed_cols' colunas serão fixadas à esquerda
    - Útil para tabelas com muitas colunas (ranking, performance, etc.)
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
                        columns=[],
                        data=[],
                        page_size=page_size,
                        sort_action="native",
                        filter_action="native",
                        markdown_options={"html": True},
                        fixed_columns={'headers': True, 'data': fixed_cols} if fixed_cols > 0 else None,
                        style_table={'overflowX': 'auto', 'borderRadius': '12px', 'minWidth': '100%', 'maxHeight': '600px'}, 
                        style_header={
                            'backgroundColor': 'var(--purple-main)', 
                            'color': 'white', 
                            'fontWeight': '600',
                            'textAlign': 'center',
                            'padding': '12px',
                            'position': 'sticky',
                            'top': 0,
                            'zIndex': 1,
                        },
                        style_cell={
                            'textAlign': 'center', 'padding': '10px', 
                            'borderBottom': '1px solid #E5E7EB', 'color': 'var(--text-main)', 'fontSize': '13px',
                            'minWidth': '100px', 'width': '130px', 'maxWidth': '200px',
                        },
                        style_cell_conditional=[
                            # Colunas fixas - largura reduzida para caber mais
                            {
                                'if': {'column_id': 'foto'},
                                'width': '60px', 'minWidth': '60px', 'maxWidth': '60px',
                            },
                            {
                                'if': {'column_id': 'banco'},
                                'width': '100px', 'minWidth': '80px', 'maxWidth': '120px',
                            },
                            {
                                'if': {'column_id': 'operador'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '160px',
                            },
                            {
                                'if': {'column_id': 'login'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '160px',
                            },
                            # Colunas de valores - largura compacta
                            {
                                'if': {'column_id': 'faturamento'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'feito_dia'},
                                'width': '110px', 'minWidth': '90px', 'maxWidth': '140px',
                            },
                            {
                                'if': {'column_id': 'meta'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'perc_meta'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'falta_70'},
                                'width': '110px', 'minWidth': '90px', 'maxWidth': '140px',
                            },
                            {
                                'if': {'column_id': 'falta_80'},
                                'width': '110px', 'minWidth': '90px', 'maxWidth': '140px',
                            },
                            {
                                'if': {'column_id': 'falta_90'},
                                'width': '110px', 'minWidth': '90px', 'maxWidth': '140px',
                            },
                            {
                                'if': {'column_id': 'falta_100'},
                                'width': '110px', 'minWidth': '90px', 'maxWidth': '140px',
                            },
                            {
                                'if': {'column_id': 'ranking'},
                                'width': '100px', 'minWidth': '80px', 'maxWidth': '130px',
                            },
                            {
                                'if': {'column_id': 'projecao'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'proj_perc'},
                                'width': '100px', 'minWidth': '80px', 'maxWidth': '130px',
                            },
                            {
                                'if': {'column_id': 'tempo_casa'},
                                'width': '120px', 'minWidth': '100px', 'maxWidth': '150px',
                            },
                            {
                                'if': {'column_id': 'turno'},
                                'width': '80px', 'minWidth': '60px', 'maxWidth': '100px',
                            },
                        ],
                        style_data_conditional=[
                            {'if': {'row_index': 'odd'}, 'backgroundColor': '#F9FAFB'},
                            # Destaque para linha TOTAL
                            {
                                'if': {'filter_query': '{operador} = "📊 TOTAL"'},
                                'backgroundColor': '#e9d8fd',
                                'color': '#4a1d8c',
                                'fontWeight': 'bold',
                                'fontSize': '14px',
                            },
                            # Destaque para meta batida
                            {
                                'if': {'filter_query': '{perc_meta} contains "100"'},
                                'backgroundColor': '#d4edda',
                                'color': '#155724',
                            },
                        ]
                    )
                ]
            )
        ],
        className="dashboard-panel mt-4"
    )
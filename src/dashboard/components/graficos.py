"""
COMPONENTES DE GRÁFICOS REUTILIZÁVEIS
======================================
Todos os gráficos já saem com estilo padronizado.
"""

from dash import dcc
import plotly.graph_objects as go
import plotly.express as px


def aplicar_estilo_padrao(figura, titulo: str):
    """
    Aplica estilo padrão a qualquer gráfico.
    
    ARGS:
        figura: objeto Figure do Plotly
        titulo: título do gráfico
    
    RETORNA:
        figura com estilo aplicado
    """
    figura.update_layout(
        title=dict(
            text=titulo,
            font=dict(color='#111827', size=14, weight='bold'),
            x=0,
            xanchor='left'
        ),
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#111827')
    )
    return figura


def criar_grafico_linha(df, x, y, titulo: str, cor: str = '#7e3d97'):
    """
    Cria um gráfico de linha já estilizado.
    
    ARGS:
        df: DataFrame com os dados
        x: nome da coluna para eixo X
        y: nome da coluna para eixo Y
        titulo: título do gráfico
        cor: cor da linha (padrão roxo)
    
    RETORNA:
        figura do gráfico pronta
    """
    if df.empty:
        return go.Figure()
    
    figura = go.Figure()
    figura.add_trace(go.Scatter(
        mode='lines+markers',
        line=dict(color=cor, width=3),
        marker=dict(size=8, color=cor),
        fill='tozeroy',
        fillcolor=f'rgba({int(cor[1:3], 16)}, {int(cor[3:5], 16)}, {int(cor[5:7], 16)}, 0.2)',
        x=df[x],
        y=df[y]
    ))
    
    figura.update_layout(
        xaxis=dict(showgrid=True, gridcolor='#E5E7EB', title='', tickformat='%d'),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB', title='', visible=False)
    )
    
    return aplicar_estilo_padrao(figura, titulo)


def criar_grafico_barras(df, x, y, titulo: str, cor: str = '#7e3d97'):
    """
    Cria um gráfico de barras já estilizado.
    
    ARGS:
        df: DataFrame com os dados
        x: nome da coluna para eixo X
        y: nome da coluna para eixo Y
        titulo: título do gráfico
        cor: cor das barras (padrão roxo)
    
    RETORNA:
        figura do gráfico pronta
    """
    if df.empty:
        return go.Figure()
    
    figura = px.bar(df, x=x, y=y, text=y)
    
    figura.update_traces(
        marker_color=cor,
        marker_line_color='#612d75',
        marker_line_width=1,
        texttemplate='R$ %{y:,.0f}',
        textposition='outside'
    )
    
    figura.update_layout(
        xaxis_title=x.capitalize(),
        yaxis_title="Valor (R$)",
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )
    
    return aplicar_estilo_padrao(figura, titulo)


# Componentes para o layout (a "caixa vazia")
def grafico_barras_fase(id_grafico: str, titulo: str = "Pagamentos por Fase", cor: str = "roxo"):
    """Componente de gráfico de barras para o layout."""
    return dcc.Graph(id=id_grafico, className=f"graph-{cor}", config={'displayModeBar': True})

def grafico_evolucao_diaria(id_grafico: str, titulo: str = "Evolução Diária - Faturamento no Período"):
    """Componente de gráfico de linha para o layout."""
    return dcc.Graph(id=id_grafico, config={'displayModeBar': True})
import dash_bootstrap_components as dbc
from dash import html
from dash_iconify import DashIconify

def card_indicador(titulo: str, valor_default: str, id_valor: str, cor_icone: str, icon_name: str, id_sub_texto: str = None):
    children = [
        html.Div(DashIconify(icon=icon_name, width=28, color=cor_icone), style={"textAlign": "center"}),
        html.H6(titulo, className="kpi-title"),
        html.Div(
            html.H3(valor_default, id=id_valor, className="kpi-value"),
            className="kpi-value-wrapper"
        )
    ]
    
    if id_sub_texto:
        # Card com subtexto (ex: Faturamento)
        children.append(html.Div(id=id_sub_texto, className="kpi-subtext"))
    else:
        # Card SEM subtexto (ex: Ticket, Operações) - adiciona espaço vazio
        children.append(html.Div(className="kpi-subtext", style={"height": "24px", "visibility": "hidden"}))
    
    return html.Div(children, className="card-kpi")

def card_meta(titulo: str, id_meta_objetivo: str, id_barra: str, id_percentual: str, cor_icone: str = "#f59e0b"):
    """
    Cria um card de meta com barra de progresso.
    
    ARGS:
        titulo: Título do card
        id_meta_objetivo: ID para o valor da meta
        id_barra: ID para a barra de progresso
        id_percentual: ID para o texto do percentual
        cor_icone: Cor do ícone (padrão laranja)
    """
    children = [
        html.Div(DashIconify(icon="lucide:target", width=32, color=cor_icone), style={"textAlign": "center"}),
        html.H6(titulo, className="kpi-title"),
        html.H3(id=id_meta_objetivo, className="kpi-value"),
        # Barra de progresso
        html.Div(
            style={
                "width": "100%",
                "backgroundColor": "#e5e7eb",
                "borderRadius": "4px",
                "marginTop": "12px",
                "height": "6px"
            },
            children=[
                html.Div(
                    id=id_barra,
                    style={
                        "backgroundColor": "#f59e0b",
                        "height": "6px",
                        "borderRadius": "4px",
                        "width": "0%",
                        "transition": "width 0.5s"
                    }
                )
            ]
        ),
        html.Small(id=id_percentual, className="kpi-subtext text-muted")
    ]

    return html.Div(children, className="card-kpi")
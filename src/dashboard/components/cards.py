import dash_bootstrap_components as dbc
from dash import html
from dash_iconify import DashIconify

def card_indicador(titulo: str, valor_default: str, id_valor: str, cor_icone: str, icon_name: str, id_sub_texto: str = None):
    """
    Constrói pequenos cartões coloridos, os KPIs, com o novo design Premium.
    :param titulo: O texto descritivo do cabeçalho.
    :param valor_default: O valor que aparece antes de ser atualizado do banco.
    :param id_valor: O ID com o qual daremos callback e injetaremos a string calculada.
    :param cor_icone: A cor HEX do ícone.
    :param icon_name: O nome do ícone do Lucide (DashIconify).
    :param id_sub_texto: Se existir, adiciona o campo dinâmico de subtexto abaixo do valor.
    """
    
    # Criamos os filhos do card
    children = [
        html.Div(DashIconify(icon=icon_name, width=32, color=cor_icone)),
        html.H6(titulo, className="kpi-title"),
        html.H3(valor_default, id=id_valor, className="kpi-value")
    ]
    
    # Adicionamos o campo subtexto caso tenha sido solicitado (para o faturamento mes anterior)
    if id_sub_texto:
        children.append(
            html.Div(id=id_sub_texto, className="kpi-subtext text-muted")
        )

    return html.Div(children, className="card-kpi")

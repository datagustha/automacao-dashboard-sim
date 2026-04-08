"""
LAYOUT DO DASHBOARD PRINCIPAL
==============================
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from datetime import date, datetime
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.cards import card_indicador

#funcao para monstar dash

def esqueleto():
    sidebar = get_sidebar("Dashboard")
    
    conteudo = html.Div([
        html.H1("Olá, usuário!")  ,
        
        # aqui vão os cards

        card_indicador(
            titulo="META DO MÊS",
            valor_default="R$ 0,00",
            id_valor="kpi-meta",
            cor_icone="#f59e0b",
            icon_name="lucide:target"
        ),

         card_indicador(
            titulo="Teste",
            valor_default="R$ 10,00",
            id_valor="kpi-meta",
            cor_icone="#f59e0b",
            icon_name="lucide:target"
        )

    ], className = "main-content" # ← A classe main-content EMPURRA o conteúdo 260px para a direita
    )
    
    return html.Div([sidebar, conteudo])

    


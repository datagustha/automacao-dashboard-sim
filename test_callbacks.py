# -*- coding: utf-8 -*-
"""
Testa se os callbacks do ADM registram sem erros.
"""
import sys
sys.path.insert(0, '.')

import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id='url'),
    dcc.Store(id='login-success-store'),
    dcc.Store(id='operador-selecionado-store'),
    dcc.Store(id='banco-operador-store'),
    dcc.Interval(id='intervalo-atualizacao-adm', interval=300000, n_intervals=0),
    dcc.Interval(id='intervalo-operador', interval=300000, n_intervals=0),
    html.Div(id='kpi-fat-semear'),
    html.Div(id='kpi-fat-semear-anterior'),
    html.Div(id='kpi-fat-agoracred'),
    html.Div(id='kpi-fat-agoracred-anterior'),
    html.Div(id='kpi-total-ops-adm'),
    html.Div(id='kpi-ops-adm-anterior'),
    html.Div(id='kpi-ticket-adm'),
    html.Div(id='kpi-meta-semear'),
    html.Div(id='kpi-percentual-semear'),
    html.Div(id='barra-progresso-semear'),
    html.Div(id='kpi-meta-agoracred'),
    html.Div(id='kpi-percentual-agoracred'),
    html.Div(id='barra-progresso-agoracred'),
    html.Div(id='badge-data-range-adm'),
    dcc.Dropdown(id='filtro-mes-adm'),
    dcc.Dropdown(id='filtro-ano-adm'),
    dcc.Dropdown(id='filtro-atividade-adm'),
    dcc.Dropdown(id='filtro-operador-adm'),
    dcc.DatePickerRange(id='filtro-data-range-adm'),
    dcc.Graph(id='grafico-evolucao-semear-adm'),
    dcc.Graph(id='grafico-evolucao-agoracred-adm'),
    dash_table.DataTable(id='tabela-adm-semear'),
    dash_table.DataTable(id='tabela-adm-agoracred'),
    dash_table.DataTable(id='tabela-evolucao-diaria-adm'),
    dcc.Dropdown(id='adm-banco-select'),
    dcc.Dropdown(id='adm-filtro-atividade'),
    dcc.Dropdown(id='adm-operador-select'),
    # Operador callbacks IDs
    html.Div(id='tempo-de-casa'),
    html.Div(id='info-meta-diaria'),
    html.Div(id='info-dias-operador'),
    dcc.Dropdown(id='filtro-mes-operador'),
    dcc.Dropdown(id='filtro-ano-operador'),
    dcc.DatePickerRange(id='filtro-data-range-operador'),
    dash_table.DataTable(id='tabela-unificada'),
    dash_table.DataTable(id='tabela-mes-mes'),
    dash_table.DataTable(id='tabela-performance-operador'),
    dash_table.DataTable(id='tabela-semanas'),
    dcc.Graph(id='grafico-fase-operador'),
])

from src.dashboard.callbacks.adm_callbacks import register_callbacks as reg_adm
reg_adm(app)
print('[OK] adm_callbacks registrado!')

from src.dashboard.callbacks.operador_callbacks import register_callbacks as reg_op
reg_op(app)
print('[OK] operador_callbacks registrado!')

print(f'Total de callbacks: {len(app.callback_map)}')
print('[SUCESSO] App inicializa sem erros!')

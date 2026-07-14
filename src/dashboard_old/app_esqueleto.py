# app_esqueleto.py
import dash
import dash_bootstrap_components as dbc
from src.dashboard.layouts.esqueleto import tela_login, register_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.layout = tela_login()

# REGISTRA O CALLBACK
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=8051)
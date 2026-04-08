# app_esqueleto.py
import dash
import dash_bootstrap_components as dbc
from src.dashboard.layouts.esqueleto import esqueleto

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.layout = esqueleto()

if __name__ == '__main__':
    app.run(debug=True, port=8051)
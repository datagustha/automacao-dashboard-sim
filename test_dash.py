import dash
app = dash.Dash(__name__)
from src.dashboard.callbacks.adm_callbacks import register_callbacks
register_callbacks(app)
print('Registered')

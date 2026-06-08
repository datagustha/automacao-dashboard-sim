import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.db_service import Buscar_login
from src.dashboard.callbacks.adm_callbacks import register_callbacks

# Vamos criar um mock simples da app do Dash para registrar os callbacks
class MockApp:
    def __init__(self):
        self.callbacks = {}
        
    def callback(self, outputs, inputs, state=None, prevent_initial_call=False):
        def decorator(func):
            self.callbacks[func.__name__] = func
            return func
        return decorator

app = MockApp()
register_callbacks(app)

callback_func = app.callbacks['atualizar_dashboard_adm']

# Dados do operador de teste (ADM)
dados_operador = {
    'login': '2552GUSTHAVO',
    'nome': 'LUIZ GUSTHAVO',
    'banco': 'ADM',
    'perfil': 'adm',
    'admissao': '2023-01-01'
}

print("Executando callback atualizar_dashboard_adm para Junho de 2026...")
try:
    resultado = callback_func(
        n=0,
        pathname="/dashboard",
        mes=6,
        ano=2026,
        filtro_atividade="ATIVO",
        operador_filtro="TODOS",
        data_inicio=None,
        data_fim=None,
        dados_operador=dados_operador
    )
    
    print("\nSUCESSO!")
    print("KPI Fat Semear:", resultado[0])
    print("KPI Fat Semear Anterior:", resultado[1])
    print("KPI Fat Agoracred:", resultado[2])
    print("KPI Fat Agoracred Anterior:", resultado[3])
    print("KPI Total Ops:", resultado[4])
    print("KPI Ticket Médio:", resultado[6])
    print("Qtd dados Semear:", len(resultado[7]))
    print("Qtd dados Agoracred:", len(resultado[9]))
    print("Meta Semear:", resultado[12])
    print("Meta Agoracred:", resultado[15])
except Exception as e:
    import traceback
    print("\nERRO DE EXECUÇÃO:")
    traceback.print_exc()

import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT_DIR)

from src.dashboard.callbacks.graficos_callbacks import _atualizar_dashboard_interno

res = _atualizar_dashboard_interno(
    pathname='/dashboard',
    n_interval=0,
    mes=7,
    ano=2026,
    texto_busca=None,
    fase=['todas'],
    data_inicio=None,
    data_fim=None,
    dados_operador={'login': '2552ROSELI'}
)

# res[4] is dados_tabela
# res[5] is colunas_tabela
print("Tabela pagamentos (data):")
for row in res[4][:10]:
    print(row)

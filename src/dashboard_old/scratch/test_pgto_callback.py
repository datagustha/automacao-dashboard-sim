import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT_DIR)

from src.dashboard.callbacks.pgto_callbacks import atualizar_tabela_mestra

# Simulate for operator
res_op = atualizar_tabela_mestra(
    n_intervals=0,
    pathname='/pagamentos',
    mes=7,
    ano=2026,
    fases_selecionadas=['TODAS'],
    texto_busca=None,
    banco_escolhido='SEMEAR',
    atividade_escolhida='ativo',
    data_inicio=None,
    data_fim=None,
    dados_operador={'login': '2552ROSELI', 'perfil': 'operador', 'banco': 'SEMEAR'}
)

print("Tabela pagamentos completa - Operador (Julho 2026):")
for row in res_op[0][:5]:
    print(row)

# Simulate for admin
res_adm = atualizar_tabela_mestra(
    n_intervals=0,
    pathname='/pagamentos',
    mes=7,
    ano=2026,
    fases_selecionadas=['TODAS'],
    texto_busca=None,
    banco_escolhido='SEMEAR',
    atividade_escolhida='ativo',
    data_inicio=None,
    data_fim=None,
    dados_operador={'login': 'ADMIN', 'perfil': 'adm', 'banco': 'SEMEAR'}
)

print("\nTabela pagamentos completa - Admin (Julho 2026):")
for row in res_adm[0][:5]:
    print(row)

import sys
import os
import pandas as pd
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT_DIR)

from src.services.db_service import (
    Buscar_login,
    Buscar_pagamento_por_operador,
    buscar_pagamentos_todos_operadores_por_banco
)
from src.dashboard.components.filtros import aplicar_filtro_data

# Copied logic from pgto_callbacks.py for admin
login = 'ADMIN'
perfil = 'adm'
banco_escolhido = 'SEMEAR'
atividade_escolhida = 'ativo'
mes = 7
ano = 2026
data_inicio = None
data_fim = None

todos = buscar_pagamentos_todos_operadores_por_banco(banco_escolhido)
pagamentos_brutos = []

for operador_dict, pagamentos, _ in todos:
    if atividade_escolhida == 'ativo' and operador_dict.get('atividade') != 'ativo':
        continue
    if pagamentos:
        login_operador = operador_dict.get('login', '')
        for p in pagamentos:
            p['operador'] = login_operador
        pagamentos_brutos.extend(pagamentos)

df = pd.DataFrame(pagamentos_brutos)
print(f"Total pagamentos brutos: {len(df)}")

if 'dtPgto' in df.columns:
    df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
    df = df.dropna(subset=['dtPgto'])
    
    df_filtrado, usando_range, label_periodo = aplicar_filtro_data(df, mes, ano, data_inicio, data_fim)
    print(f"Total pagamentos filtrados: {len(df_filtrado)}")
    
    if not df_filtrado.empty:
        print("Meses e anos unicos nos pagamentos filtrados:")
        df_filtrado['ano_mes'] = df_filtrado['dtPgto'].dt.strftime('%Y-%m')
        print(df_filtrado['ano_mes'].value_counts())

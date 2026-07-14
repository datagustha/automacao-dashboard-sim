import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT_DIR)

from sqlalchemy.orm import Session
from src.config.database import engine
from src.services.db_service import Buscar_login, Buscar_pagamento_por_operador

operador = Buscar_login('2552ROSELI')
pagamentos = Buscar_pagamento_por_operador(operador)

df = pd.DataFrame(pagamentos)
df['dtPgto'] = pd.to_datetime(df['dtPgto'])

print(f"Total pagamentos: {len(df)}")
print("Meses e anos únicos nos pagamentos:")
df['ano_mes'] = df['dtPgto'].dt.strftime('%Y-%m')
print(df['ano_mes'].value_counts().sort_index())

print("\nAlgumas datas de Julho/2026:")
print(df[df['ano_mes'] == '2026-07']['dtPgto'].head(10))

print("\nAlgumas datas de Junho/2026:")
print(df[df['ano_mes'] == '2026-06']['dtPgto'].head(10))

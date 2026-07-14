import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT_DIR)

from sqlalchemy.orm import Session
from src.config.database import engine
from src.models.PgtoSemearModel import PgtoSemearBoleto
from src.services.db_service import Buscar_login, Buscar_pagamento_por_operador
from src.dashboard.components.filtros import aplicar_filtro_data

operador = Buscar_login('2552ROSELI')
pagamentos = Buscar_pagamento_por_operador(operador)

df = pd.DataFrame(pagamentos)
df['dtPgto'] = pd.to_datetime(df['dtPgto'])

# Filter by range: 2026-07-01 to 2026-07-10
df_range, usando_range, label = aplicar_filtro_data(df, 6, 2026, '2026-07-01', '2026-07-10')
print(f"Range filtered count: {len(df_range)}")
if not df_range.empty:
    print("Dates in range:")
    print(df_range['dtPgto'].dt.strftime('%Y-%m-%d').value_counts())

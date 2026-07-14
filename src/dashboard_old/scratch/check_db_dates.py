import sys
import os
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(ROOT_DIR)

from sqlalchemy.orm import Session
from src.config.database import engine
from src.models.PgtoSemearModel import PgtoSemearBoleto

with Session(engine) as session:
    # Query database for 2552ROSELI
    res = session.query(PgtoSemearBoleto).filter(
        PgtoSemearBoleto.operador == '2552ROSELI'
    ).all()
    
    df = pd.DataFrame([{
        "dtPgto_raw": p.dtPgto,
        "contrato": p.contrato,
        "cliente": p.cliente,
        "valorTotal": p.valorTotal
    } for p in res])
    
    df['dtPgto_parsed'] = pd.to_datetime(df['dtPgto_raw'])
    
    # Check July 2026
    df_julho = df[df['dtPgto_parsed'].dt.year == 2026]
    df_julho = df_julho[df_julho['dtPgto_parsed'].dt.month == 7]
    print(f"July 2026 payments count: {len(df_julho)}")
    if not df_julho.empty:
        print(df_julho[['dtPgto_raw', 'dtPgto_parsed', 'contrato', 'valorTotal']].head(5))
        
    # Check June 2026
    df_junho = df[df['dtPgto_parsed'].dt.year == 2026]
    df_junho = df_junho[df_junho['dtPgto_parsed'].dt.month == 6]
    print(f"\nJune 2026 payments count: {len(df_junho)}")
    if not df_junho.empty:
        print(df_junho[['dtPgto_raw', 'dtPgto_parsed', 'contrato', 'valorTotal']].head(5))

import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.db_service import buscar_pagamentos_todos_operadores_por_banco

print("Buscando pagamentos de todos os operadores do SEMEAR...")
dados = buscar_pagamentos_todos_operadores_por_banco("SEMEAR")
print(f"Número de tuplas retornadas: {len(dados)}")

total_geral_semear = 0.0
total_junho_semear = 0.0

for operador, pagamentos, metas in dados:
    if pagamentos:
        df = pd.DataFrame(pagamentos)
        df["dtPgto"] = pd.to_datetime(df["dtPgto"])
        total_geral_semear += df["valorTotal"].sum()
        
        # Filtrar Junho de 2026
        df_jun = df[(df["dtPgto"].dt.month == 6) & (df["dtPgto"].dt.year == 2026)]
        total_junho_semear += df_jun["valorTotal"].sum()
        
        # Filtro de "Fora da fase"
        if "faseAtraso" in df_jun.columns:
            df_jun_fase = df_jun[df_jun["faseAtraso"] != "Fora da fase"]
            faturamento_jun_com_fase = df_jun_fase["valorTotal"].sum()
        else:
            faturamento_jun_com_fase = df_jun["valorTotal"].sum()

        if faturamento_jun_com_fase > 0 or df_jun["valorTotal"].sum() > 0:
            print(f"Operador: {operador['login']} (Atividade: {operador['atividade']})")
            print(f"  Total Junho 2026 bruto: {df_jun['valorTotal'].sum()}")
            print(f"  Total Junho 2026 sem 'Fora da fase': {faturamento_jun_com_fase}")

print(f"\nFaturamento Geral SEMEAR: R$ {total_geral_semear:,.2f}")
print(f"Faturamento Junho 2026 SEMEAR: R$ {total_junho_semear:,.2f}")

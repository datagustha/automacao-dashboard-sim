# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

print("Testando importacoes...")

from src.services.db_service import (
    buscar_pagamentos_todos_operadores_por_banco,
    buscar_todos_operadores_por_banco,
    buscar_metas_por_operador,
)
print("[OK] db_service importado")

from src.services.analytics_service import (
    calcular_performance_operador,
    calcular_tempo_de_casa,
)
print("[OK] analytics_service importado")

from src.dashboard.components.filtros import aplicar_filtro_data, obter_mes_ano_do_range
print("[OK] filtros importado")

from src.dashboard.callbacks.adm_callbacks import criar_grafico_por_banco, _brl, _num, _is_ativo
print("[OK] adm_callbacks importado")

from src.dashboard.callbacks.operador_callbacks import register_callbacks as reg_op
print("[OK] operador_callbacks importado")

# ── Testes unitarios ────────────────────────────────────────────────
print("\n--- Testes unitarios ---")

op_ativo   = {"atividade": "ativo"}
op_inativo = {"atividade": "inativo"}

assert _is_ativo(op_ativo,   "ATIVO") == True,  "Deveria ser True p/ ativo"
assert _is_ativo(op_inativo, "ATIVO") == False, "Deveria ser False p/ inativo"
assert _is_ativo(op_inativo, "TODOS") == True,  "TODOS deve incluir todos"
print("[OK] _is_ativo OK")

assert _brl(1234.56) == "R$ 1.234,56", f"Esperado R$ 1.234,56, got {_brl(1234.56)}"
assert _brl(0) == "R$ 0,00"
print(f"[OK] _brl: {_brl(1234.56)}")

assert _num(1500) == "1.500"
print(f"[OK] _num: {_num(1500)}")

# ── Teste com dados reais do banco ─────────────────────────────────
print("\n--- Teste com banco de dados ---")

ops_semear = buscar_todos_operadores_por_banco('SEMEAR')
ativos_semear = [op for op in ops_semear if str(op.get('atividade','')).strip().lower() == 'ativo']
print(f"[INFO] Operadores SEMEAR total: {len(ops_semear)}, ativos: {len(ativos_semear)}")

ops_agoracred = buscar_todos_operadores_por_banco('AGORACRED')
ativos_agoracred = [op for op in ops_agoracred if str(op.get('atividade','')).strip().lower() == 'ativo']
print(f"[INFO] Operadores AGORACRED total: {len(ops_agoracred)}, ativos: {len(ativos_agoracred)}")

# Teste de calculo do faturamento para maio/2026
import pandas as pd

MES  = 5
ANO  = 2026

fat_semear = 0.0
fat_agoracred = 0.0

dados_semear = buscar_pagamentos_todos_operadores_por_banco('SEMEAR')
for operador, pagamentos, metas in dados_semear:
    if not _is_ativo(operador, 'ATIVO'):
        continue
    if not pagamentos:
        continue
    df = pd.DataFrame(pagamentos)
    df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
    df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0)
    df = df.dropna(subset=['dtPgto'])
    df = df[(df['dtPgto'].dt.month == MES) & (df['dtPgto'].dt.year == ANO)]
    if 'faseAtraso' in df.columns:
        df = df[df['faseAtraso'] != 'Fora da fase']
    fat_semear += float(df['valorTotal'].sum())

dados_agoracred = buscar_pagamentos_todos_operadores_por_banco('AGORACRED')
for operador, pagamentos, metas in dados_agoracred:
    if not _is_ativo(operador, 'ATIVO'):
        continue
    if not pagamentos:
        continue
    df = pd.DataFrame(pagamentos)
    df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
    df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0)
    df = df.dropna(subset=['dtPgto'])
    df = df[(df['dtPgto'].dt.month == MES) & (df['dtPgto'].dt.year == ANO)]
    fat_agoracred += float(df['valorTotal'].sum())

print(f"\n[RESULTADO] Maio/2026:")
print(f"  SEMEAR    : {_brl(fat_semear)}")
print(f"  AGORACRED : {_brl(fat_agoracred)}")
print(f"  TOTAL     : {_brl(fat_semear + fat_agoracred)}")

assert fat_semear > 0, "ERRO: Faturamento SEMEAR zerado! Verifique filtro de atividade."
print("\n[SUCESSO] Todos os testes passaram!")

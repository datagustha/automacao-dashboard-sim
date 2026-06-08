import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.db_service import buscar_pagamentos_todos_operadores_por_banco
from src.dashboard.components.filtros import aplicar_filtro_data, obter_mes_ano_do_range

mes = 6
ano = 2026
filtro_atividade = "ATIVO"
operador_filtro = "TODOS"
data_inicio = None
data_fim = None

mes_int, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
    int(mes) if mes else pd.Timestamp.now().month,
    int(ano) if ano else pd.Timestamp.now().year,
)

if mes_int == 1:
    mes_ant, ano_ant = 12, ano_int - 1
else:
    mes_ant, ano_ant = mes_int - 1, ano_int

def _is_ativo(operador, filtro_atividade):
    if filtro_atividade and filtro_atividade.upper() == "ATIVO":
        return str(operador.get("atividade", "")).strip().lower() == "ativo"
    return True

def processar_banco(banco: str, operador_especifico=None):
    dados = buscar_pagamentos_todos_operadores_por_banco(banco)
    if not dados:
        return 0.0, 0.0, 0, 0, 0.0, [], 0.0

    fat_atual     = 0.0
    fat_anterior  = 0.0
    ops_atual     = 0
    ops_anterior  = 0
    soma_tickets  = 0.0
    linhas_tabela = []
    meta_total_banco = 0.0

    for operador, pagamentos, metas in dados:
        if operador_especifico and operador_especifico != "TODOS":
            if operador.get("login") != operador_especifico:
                continue

        if not _is_ativo(operador, filtro_atividade):
            continue

        if not pagamentos:
            meta_op = 0.0
            if metas:
                for m in metas:
                    md = m.get("data")
                    if md:
                        if hasattr(md, "year"):
                            if md.year == ano_int and md.month == mes_int:
                                meta_op = float(m.get("meta100") or 0)
                                break
                        elif isinstance(md, str):
                            mdt = pd.to_datetime(md, errors="coerce")
                            if not pd.isna(mdt) and mdt.year == ano_int and mdt.month == mes_int:
                                meta_op = float(m.get("meta100") or 0)
                                break
            meta_total_banco += meta_op
            continue

        try:
            df = pd.DataFrame(pagamentos)
        except Exception as e:
            print(f"[ERRO] DataFrame {operador.get('login')}: {e}")
            continue

        if "dtPgto" not in df.columns or "valorTotal" not in df.columns:
            continue

        df["dtPgto"]     = pd.to_datetime(df["dtPgto"], errors="coerce")
        df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
        df = df.dropna(subset=["dtPgto"])

        if df.empty:
            continue

        if banco == "SEMEAR" and "faseAtraso" in df.columns:
            df = df[df["faseAtraso"] != "Fora da fase"]

        meta_operador = 0.0
        if metas:
            for meta in metas:
                md = meta.get("data")
                if md:
                    if hasattr(md, "year"):
                        if md.year == ano_int and md.month == mes_int:
                            meta_operador = float(meta.get("meta100") or 0)
                            break
                    elif isinstance(md, str):
                        mdt = pd.to_datetime(md, errors="coerce")
                        if not pd.isna(mdt) and mdt.year == ano_int and mdt.month == mes_int:
                            meta_operador = float(meta.get("meta100") or 0)
                            break
        meta_total_banco += meta_operador

        df_atual, _, _ = aplicar_filtro_data(df, mes, ano, data_inicio, data_fim)
        df_ant = df[
            (df["dtPgto"].dt.month == mes_ant) &
            (df["dtPgto"].dt.year  == ano_ant)
        ]

        fat   = float(df_atual["valorTotal"].sum()) if not df_atual.empty else 0.0
        fat_a = float(df_ant["valorTotal"].sum())   if not df_ant.empty  else 0.0
        ops   = len(df_atual)
        ops_a = len(df_ant)

        fat_atual    += fat
        fat_anterior += fat_a
        ops_atual    += ops
        ops_anterior += ops_a
        soma_tickets += fat

    return fat_atual, fat_anterior, ops_atual, ops_anterior, soma_tickets, len(linhas_tabela), meta_total_banco

print("Processando SEMEAR...")
res = processar_banco("SEMEAR", operador_filtro)
print("Resultado SEMEAR (fat_atual, fat_anterior, ops_atual, ops_anterior, soma_tickets, len_tabela, meta_total):")
print(res)

print("\nProcessando AGORACRED...")
res_a = processar_banco("AGORACRED", operador_filtro)
print("Resultado AGORACRED:")
print(res_a)

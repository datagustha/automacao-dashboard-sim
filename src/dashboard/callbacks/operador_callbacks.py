"""
CALLBACKS DA TELA DE DETALHE DO OPERADOR
=========================================
Gerencia as tabelas e gráficos do operador.

🔧 CORREÇÕES APLICADAS:
1. Todas as tabelas agora retornam columns=[] e data=[] quando vazias
2. Tratamento de erros com try/except em todos os callbacks
3. Nunca retorna None - sempre listas vazias
4. Validação de dados antes de processar
5. Tabela unificada com retorno seguro
6. Tabela mês a mês com retorno seguro
7. Tabela performance com retorno seguro
8. Tabela semanas com retorno seguro
9. Tabela evolução com retorno seguro
"""

from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime, date
import holidays

from src.services.db_service import Buscar_pagamento_por_operador, buscar_metas_por_operador, Buscar_login
from src.services.analytics_service import (
    calcular_performance_operador,
    calcular_tempo_de_casa,
    calcular_semanas_do_mes,
)
from src.dashboard.components.filtros import aplicar_filtro_data, obter_mes_ano_do_range


def register_callbacks(app):
    """Registra os callbacks da tela de detalhe do operador."""

    # ================================================================
    # FUNÇÃO AUXILIAR: DIAS ÚTEIS DO MÊS
    # ================================================================
    def get_dias_uteis(ano, mes):
        """Retorna lista de dias úteis (segunda a sexta, sem feriados) do mês.
        Inclui Corpus Christi (feriado facultativo, 60 dias após a Páscoa).
        """
        from dateutil.easter import easter
        from datetime import timedelta
        feriados_br = holidays.country_holidays("BR", years=ano)
        corpus_christi = easter(ano) + timedelta(days=60)
        feriados_br.update({corpus_christi: "Corpus Christi"})
        ultimo_dia  = calendar.monthrange(ano, mes)[1]
        return [
            dia for dia in range(1, ultimo_dia + 1)
            if date(ano, mes, dia).weekday() < 5 and date(ano, mes, dia) not in feriados_br
        ]

    # ================================================================
    # FUNÇÃO AUXILIAR: FILTRAR "FORA DA FASE" PARA SEMEAR
    # ================================================================
    def filtrar_fora_da_fase(df, banco):
        """Remove pagamentos 'Fora da fase' apenas para operadores SEMEAR."""
        if banco == "SEMEAR":
            if "faseAtraso" in df.columns:
                return df[df["faseAtraso"] != "Fora da fase"]
            elif "fase" in df.columns:
                return df[df["fase"] != "Fora da fase"]
        return df

    # ================================================================
    # FUNÇÃO AUXILIAR: EXTRAIR META DO MÊS
    # ================================================================
    def extrair_meta_mensal(metas, ano_int, mes_int):
        if not metas:
            return 0.0
        for meta in metas:
            md = meta.get("data")
            if md:
                if hasattr(md, "year"):
                    if md.year == ano_int and md.month == mes_int:
                        return float(meta.get("meta100") or 0)
                elif isinstance(md, str):
                    mdt = pd.to_datetime(md, errors="coerce")
                    if not pd.isna(mdt) and mdt.year == ano_int and mdt.month == mes_int:
                        return float(meta.get("meta100") or 0)
        return 0.0

    # ================================================================
    # TABELA UNIFICADA
    # ================================================================
    @app.callback(
        [
            Output("tabela-unificada", "data"),
            Output("tabela-unificada", "columns"),
            Output("info-meta-diaria", "children"),
        ],
        [
            Input("intervalo-operador", "n_intervals"),
            Input("filtro-mes-operador", "value"),
            Input("filtro-ano-operador", "value"),
            Input("filtro-data-range-operador", "start_date"),
            Input("filtro-data-range-operador", "end_date"),
            Input("adm-banco-select", "value"),
            Input("adm-filtro-atividade", "value"),
            Input("adm-operador-select", "value"),
        ],
        [
            State("operador-selecionado-store", "data"),
            State("banco-operador-store", "data"),
        ],
    )
    def atualizar_tabela_unificada(n, mes, ano, data_inicio, data_fim,
                                   adm_banco, adm_atividade, adm_operador,
                                   operador_selecionado, banco_store):
        """
        TABELA UNIFICADA:
        Dia | Dia Útil | Data | Quantidade | Faturamento | Meta Diária | Bateu Meta?
        
        🔧 CORREÇÃO: Retorno seguro com try/except
        """
        vazio = [], [], ""

        try:
            if not operador_selecionado:
                return vazio

            if operador_selecionado.get("login") == "TODOS":
                return vazio

            pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
            if not pagamentos:
                return vazio

            df = pd.DataFrame(pagamentos)
            df["dtPgto"] = pd.to_datetime(df["dtPgto"], errors="coerce")
            df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
            df = df.dropna(subset=["dtPgto"])

            if df.empty:
                return vazio

            mes_int, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
                int(mes) if mes else date.today().month,
                int(ano) if ano else date.today().year,
            )

            df_filtrado, _, _ = aplicar_filtro_data(df, mes_int, ano_int, data_inicio, data_fim)

            if df_filtrado.empty:
                return vazio

            banco_atual = adm_banco if adm_banco else banco_store
            df_filtrado = filtrar_fora_da_fase(df_filtrado, banco_atual)

            if df_filtrado.empty:
                return vazio

            metas = buscar_metas_por_operador(operador_selecionado)
            meta_mensal = extrair_meta_mensal(metas, ano_int, mes_int)

            dias_uteis_lista = get_dias_uteis(ano_int, mes_int)
            total_dias_uteis = len(dias_uteis_lista)

            meta_diaria = meta_mensal / total_dias_uteis if (total_dias_uteis > 0 and meta_mensal > 0) else 0.0

            dia_util_map = {dia: idx + 1 for idx, dia in enumerate(dias_uteis_lista)}

            df_filtrado["_dia"] = df_filtrado["dtPgto"].dt.day
            df_dia = df_filtrado.groupby("_dia").agg(
                quantidade=("valorTotal", "count"),
                faturamento=("valorTotal", "sum"),
            ).reset_index().rename(columns={"_dia": "dia"})
            df_dia = df_dia.sort_values("dia")

            def _brl(v):
                return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado = []
            for _, row in df_dia.iterrows():
                dia        = int(row["dia"])
                quantidade = int(row["quantidade"])
                faturamento = float(row["faturamento"])
                dia_util   = dia_util_map.get(dia, "-")
                data_str   = f"{dia:02d}/{mes_int:02d}/{ano_int}"
                bateu_meta = "✅ Sim" if (meta_diaria > 0 and faturamento >= meta_diaria) else "❌ Não"

                resultado.append({
                    "dia":        dia,
                    "dia_util":   dia_util,
                    "data":       data_str,
                    "quantidade": quantidade,
                    "faturamento": _brl(faturamento),
                    "meta_diaria": _brl(meta_diaria) if meta_diaria > 0 else "—",
                    "bateu_meta":  bateu_meta,
                })

            total_qtd = df_dia["quantidade"].sum()
            total_fat = df_dia["faturamento"].sum()
            resultado.append({
                "dia":        "TOTAL",
                "dia_util":   "-",
                "data":       "-",
                "quantidade": int(total_qtd),
                "faturamento": _brl(total_fat),
                "meta_diaria": "-",
                "bateu_meta":  "-",
            })

            dias_batidos   = sum(1 for r in resultado if r.get("bateu_meta") == "✅ Sim")
            dias_nao_bat   = sum(1 for r in resultado if r.get("bateu_meta") == "❌ Não")
            dias_trabalhados = dias_batidos + dias_nao_bat

            hoje = date.today()
            if ano_int == hoje.year and mes_int == hoje.month:
                dias_restantes = sum(1 for d in dias_uteis_lista if d > hoje.day)
            else:
                dias_restantes = 0

            resumo = html.Div([
                html.Span(f"📅 Dias trabalhados: {dias_trabalhados}",
                          style={"marginRight": "16px", "fontWeight": "600"}),
                html.Span(f"✅ Dias com meta: {dias_batidos}",
                          style={"marginRight": "16px", "color": "#16a34a", "fontWeight": "600"}),
                html.Span(f"❌ Dias sem meta: {dias_nao_bat}",
                          style={"marginRight": "16px", "color": "#dc2626", "fontWeight": "600"}),
                html.Span(f"⏳ Dias úteis restantes: {dias_restantes}",
                          style={"marginRight": "16px", "color": "#7c3aed", "fontWeight": "600"}),
                html.Span(f"📆 Total dias úteis: {total_dias_uteis}",
                          style={"fontWeight": "600"}),
            ], style={"fontSize": "13px", "padding": "4px 0"})

            colunas = [
                {"name": "Dia",         "id": "dia"},
                {"name": "Dia Útil",    "id": "dia_util"},
                {"name": "Data",        "id": "data"},
                {"name": "Quantidade",  "id": "quantidade"},
                {"name": "Faturamento", "id": "faturamento"},
                {"name": "Meta Diária", "id": "meta_diaria"},
                {"name": "Bateu Meta?", "id": "bateu_meta"},
            ]

            return resultado, colunas, resumo

        except Exception as e:
            print(f"[OPERADOR] ❌ Erro em tabela_unificada: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], [], ""

    # ================================================================
    # TABELA MÊS A MÊS
    # ================================================================
    @app.callback(
        [
            Output("tabela-mes-mes", "data"),
            Output("tabela-mes-mes", "columns"),
            Output("tabela-mes-mes", "style_data_conditional"),
        ],
        [
            Input("intervalo-operador", "n_intervals"),
            Input("filtro-ano-operador", "value"),
            Input("filtro-data-range-operador", "start_date"),
            Input("filtro-data-range-operador", "end_date"),
        ],
        [
            State("operador-selecionado-store", "data"),
            State("banco-operador-store", "data"),
        ],
    )
    def atualizar_tabela_mes_mes(n, ano, data_inicio, data_fim, operador_selecionado, banco_store):
        """Atualiza a tabela Mês a Mês — só mostra meses com meta > 0.
        
        🔧 CORREÇÃO: Retorno seguro com try/except
        """

        estilos_base = [
            {"if": {"row_index": "odd"}, "backgroundColor": "#F9FAFB"},
            {
                "if": {"filter_query": '{bateu} = "✅ Sim"'},
                "backgroundColor": "#d4edda",
                "color": "#155724",
                "fontWeight": "500",
            },
            {
                "if": {"filter_query": '{nome_mes} = "TOTAL"'},
                "backgroundColor": "#e9d8fd",
                "color": "#4a1d8c",
                "fontWeight": "bold",
                "fontSize": "14px",
            },
        ]

        try:
            if not operador_selecionado:
                return [], [], estilos_base

            if operador_selecionado.get("login") == "TODOS":
                return [], [], estilos_base

            pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
            if not pagamentos:
                return [], [], estilos_base

            metas = buscar_metas_por_operador(operador_selecionado)
            metas_dict = {}
            for meta in (metas or []):
                md = meta.get("data")
                if md:
                    if hasattr(md, "year"):
                        metas_dict[(md.year, md.month)] = float(meta.get("meta100") or 0)
                    elif isinstance(md, str):
                        mdt = pd.to_datetime(md, errors="coerce")
                        if not pd.isna(mdt):
                            metas_dict[(mdt.year, mdt.month)] = float(meta.get("meta100") or 0)

            df = pd.DataFrame(pagamentos)
            df["dtPgto"] = pd.to_datetime(df["dtPgto"], errors="coerce")
            df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
            df = df.dropna(subset=["dtPgto"])

            _, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
                None,
                int(ano) if ano else date.today().year,
            )

            df_ano = df[df["dtPgto"].dt.year == ano_int]

            meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                           "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            resultado = []

            for mes in range(1, 13):
                meta = metas_dict.get((ano_int, mes), 0.0)
                if meta <= 0:
                    continue

                df_mes = df_ano[df_ano["dtPgto"].dt.month == mes].copy()
                df_mes = filtrar_fora_da_fase(df_mes, banco_store)

                faturamento = float(df_mes["valorTotal"].sum()) if not df_mes.empty else 0.0
                quantidade  = len(df_mes)
                percentual  = (faturamento / meta) * 100 if meta > 0 else 0.0
                bateu       = faturamento >= meta

                def _brl(v):
                    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                resultado.append({
                    "mes":         mes,
                    "nome_mes":    meses_nomes[mes - 1],
                    "quantidade":  quantidade,
                    "faturamento": _brl(faturamento),
                    "meta":        _brl(meta),
                    "percentual":  f"{percentual:.1f}%",
                    "bateu":       "✅ Sim" if bateu else "❌ Não",
                })

            if not resultado:
                return [], [], estilos_base

            total_qtd = sum(r["quantidade"] for r in resultado)
            total_fat_raw = sum(
                float(r["faturamento"].replace("R$ ", "").replace(".", "").replace(",", "."))
                for r in resultado
            )

            def _brl(v):
                return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado.append({
                "mes":         9999,
                "nome_mes":    "TOTAL",
                "quantidade":  total_qtd,
                "faturamento": _brl(total_fat_raw),
                "meta":        "-",
                "percentual":  "-",
                "bateu":       "-",
            })

            colunas = [
                {"name": "Mês",        "id": "nome_mes"},
                {"name": "Quantidade", "id": "quantidade"},
                {"name": "Faturamento","id": "faturamento"},
                {"name": "Meta",       "id": "meta"},
                {"name": "% Meta",     "id": "percentual"},
                {"name": "Bateu?",     "id": "bateu"},
            ]

            return resultado, colunas, estilos_base

        except Exception as e:
            print(f"[OPERADOR] ❌ Erro em tabela_mes_mes: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], [], estilos_base

    # ================================================================
    # TABELA DE PERFORMANCE
    # ================================================================
    @app.callback(
        [
            Output("tabela-performance-operador", "data"),
            Output("tabela-performance-operador", "columns"),
            Output("info-dias-operador", "children"),
        ],
        [
            Input("intervalo-operador", "n_intervals"),
            Input("filtro-mes-operador", "value"),
            Input("filtro-ano-operador", "value"),
            Input("filtro-data-range-operador", "start_date"),
            Input("filtro-data-range-operador", "end_date"),
            Input("adm-banco-select", "value"),
            Input("adm-filtro-atividade", "value"),
            Input("adm-operador-select", "value"),
        ],
        [
            State("operador-selecionado-store", "data"),
            State("banco-operador-store", "data"),
        ],
    )
    def atualizar_tabela_performance(n, mes, ano, data_inicio, data_fim,
                                     adm_banco, adm_atividade, adm_operador,
                                     operador_selecionado, banco_store):
        """Atualiza a tabela de performance.
        
        🔧 CORREÇÃO: Retorno seguro com try/except
        """
        try:
            if not operador_selecionado:
                return [], [], ""

            banco_atual = adm_banco if adm_banco else banco_store
            mes_int, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
                int(mes) if mes else date.today().month,
                int(ano) if ano else date.today().year,
            )

            def _brl(v):
                return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            # Se for login TODOS, calcula a performance consolidada do grupo
            if operador_selecionado.get("login") == "TODOS":
                from src.services.db_service import buscar_pagamentos_todos_operadores_por_banco
                dados_banco = buscar_pagamentos_todos_operadores_por_banco(banco_atual)
                if not dados_banco:
                    return [], [], "Sem dados no banco"

                todos_pagamentos = []
                meta_total = 0.0
                
                atividade_filtro = adm_atividade if adm_atividade else "ativo"
                
                for operador, pagamentos_op, metas_op in dados_banco:
                    if atividade_filtro and atividade_filtro.lower() == "ativo":
                        if str(operador.get("atividade", "")).strip().lower() != "ativo":
                            continue
                    
                    if pagamentos_op:
                        todos_pagamentos.extend(pagamentos_op)
                    
                    if metas_op:
                        for m in metas_op:
                            md = m.get("data")
                            if md:
                                if hasattr(md, "year"):
                                    if md.year == ano_int and md.month == mes_int:
                                        meta_total += float(m.get("meta100") or 0)
                                        break
                                elif isinstance(md, str):
                                    mdt = pd.to_datetime(md, errors="coerce")
                                    if not pd.isna(mdt) and mdt.year == ano_int and mdt.month == mes_int:
                                        meta_total += float(m.get("meta100") or 0)
                                        break

                if todos_pagamentos:
                    df_mes = pd.DataFrame(todos_pagamentos)
                    df_mes['dtPgto'] = pd.to_datetime(df_mes['dtPgto'])
                    df_mes = df_mes[
                        (df_mes['dtPgto'].dt.month == mes_int) & 
                        (df_mes['dtPgto'].dt.year == ano_int)
                    ].copy()
                    
                    if banco_atual == "SEMEAR":
                        if 'faseAtraso' in df_mes.columns:
                            df_mes = df_mes[df_mes['faseAtraso'] != "Fora da fase"]
                        elif 'fase' in df_mes.columns:
                            df_mes = df_mes[df_mes['fase'] != "Fora da fase"]
                else:
                    df_mes = pd.DataFrame()

                faturamento = df_mes['valorTotal'].astype(float).sum() if not df_mes.empty else 0.0

                dias_uteis_lista = get_dias_uteis(ano_int, mes_int)
                total_dias_uteis = len(dias_uteis_lista)

                hoje = date.today()
                if ano_int == hoje.year and mes_int == hoje.month:
                    dias_trabalhados = sum(1 for d in dias_uteis_lista if d <= hoje.day)
                    dias_restantes = total_dias_uteis - dias_trabalhados
                else:
                    dias_trabalhados = total_dias_uteis
                    dias_restantes = 0

                feito_diario = faturamento / dias_trabalhados if dias_trabalhados > 0 else 0
                atingido_meta = (faturamento / meta_total) * 100 if meta_total > 0 else 0
                
                falta_70 = max(0, (meta_total * 0.7) - faturamento)
                falta_80 = max(0, (meta_total * 0.8) - faturamento)
                falta_90 = max(0, (meta_total * 0.9) - faturamento)
                falta_100 = max(0, meta_total - faturamento)
                
                if dias_restantes > 0 and feito_diario > 0:
                    projecao = faturamento + (feito_diario * dias_restantes)
                else:
                    projecao = faturamento
                
                projecao_percentual = (projecao / meta_total) * 100 if meta_total > 0 else 0

                bar_width  = min(atingido_meta, 100)
                bar_color  = "#10B981" if atingido_meta >= 100 else "#7e3d97"
                perc_html  = (
                    f'<div style="display:flex;align-items:center;gap:6px;min-width:110px;">'
                    f'<div style="flex:1;background:#e5e7eb;border-radius:4px;height:8px;">'
                    f'<div style="width:{bar_width:.0f}%;background:{bar_color};'
                    f'height:8px;border-radius:4px;"></div></div>'
                    f'<span style="white-space:nowrap;font-weight:700;color:{bar_color};'
                    f'font-size:12px;">{atingido_meta:.1f}%</span></div>'
                )

                txt_dias = (
                    f"📅 Dias trabalhados: {dias_trabalhados}  "
                    f"|  ⏳ Dias úteis restantes: {dias_restantes}  "
                    f"|  📆 Total dias úteis: {total_dias_uteis}"
                )

                dados_tabela = [{
                    "login":               f"GRUPO {banco_atual}",
                    "faturamento":         _brl(faturamento),
                    "feito_dia":           _brl(feito_diario),
                    "meta":                _brl(meta_total),
                    "atingido_meta":       perc_html,
                    "falta_70":            _brl(falta_70),
                    "falta_80":            _brl(falta_80),
                    "falta_90":            _brl(falta_90),
                    "falta_100":           _brl(falta_100),
                    "ranking":             "—",
                    "projecao":            _brl(projecao),
                    "projecao_percentual": f"{projecao_percentual:.1f}%",
                }]

                colunas = [
                    {"name": "Login",         "id": "login"},
                    {"name": "Faturamento",   "id": "faturamento"},
                    {"name": "Feito/Dia",     "id": "feito_dia"},
                    {"name": "Meta",          "id": "meta"},
                    {"name": "% Meta",        "id": "atingido_meta", "presentation": "markdown"},
                    {"name": "Falta 70%",     "id": "falta_70"},
                    {"name": "Falta 80%",     "id": "falta_80"},
                    {"name": "Falta 90%",     "id": "falta_90"},
                    {"name": "Falta 100%",    "id": "falta_100"},
                    {"name": "Ranking",       "id": "ranking"},
                    {"name": "Projeção (R$)", "id": "projecao"},
                    {"name": "Proj. %",       "id": "projecao_percentual"},
                ]

                return dados_tabela, colunas, txt_dias

            pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
            metas      = buscar_metas_por_operador(operador_selecionado)

            if not pagamentos:
                return [], [], ""

            perf = calcular_performance_operador(
                pagamentos=pagamentos,
                metas=metas or [],
                ano=ano_int,
                mes=mes_int,
                login=operador_selecionado.get("login"),
                banco=banco_atual,
            )

            val_perc   = float(perf.get("atingido_meta", 0))
            bar_width  = min(val_perc, 100)
            bar_color  = "#10B981" if val_perc >= 100 else "#7e3d97"
            perc_html  = (
                f'<div style="display:flex;align-items:center;gap:6px;min-width:110px;">'
                f'<div style="flex:1;background:#e5e7eb;border-radius:4px;height:8px;">'
                f'<div style="width:{bar_width:.0f}%;background:{bar_color};'
                f'height:8px;border-radius:4px;"></div></div>'
                f'<span style="white-space:nowrap;font-weight:700;color:{bar_color};'
                f'font-size:12px;">{val_perc:.1f}%</span></div>'
            )

            txt_dias = (
                f"📅 Dias trabalhados: {perf['dias_trabalhados']}  "
                f"|  ⏳ Dias úteis restantes: {perf['dias_restantes']}  "
                f"|  📆 Total dias úteis: {perf['total_dias_uteis']}"
            )

            dados_tabela = [{
                "login":               perf["login"],
                "faturamento":         _brl(perf["faturamento"]),
                "feito_dia":           _brl(perf["feito_diario"]),
                "meta":                _brl(perf["meta"]),
                "atingido_meta":       perc_html,
                "falta_70":            _brl(perf["falta_70"]),
                "falta_80":            _brl(perf["falta_80"]),
                "falta_90":            _brl(perf["falta_90"]),
                "falta_100":           _brl(perf["falta_100"]),
                "ranking":             _brl(perf["meta_ranking"]),
                "projecao":            _brl(perf["projecao"]),
                "projecao_percentual": f"{perf['projecao_percentual']:.1f}%",
            }]

            colunas = [
                {"name": "Login",         "id": "login"},
                {"name": "Faturamento",   "id": "faturamento"},
                {"name": "Feito/Dia",     "id": "feito_dia"},
                {"name": "Meta",          "id": "meta"},
                {"name": "% Meta",        "id": "atingido_meta", "presentation": "markdown"},
                {"name": "Falta 70%",     "id": "falta_70"},
                {"name": "Falta 80%",     "id": "falta_80"},
                {"name": "Falta 90%",     "id": "falta_90"},
                {"name": "Falta 100%",    "id": "falta_100"},
                {"name": "Ranking",       "id": "ranking"},
                {"name": "Projeção (R$)", "id": "projecao"},
                {"name": "Proj. %",       "id": "projecao_percentual"},
            ]

            return dados_tabela, colunas, txt_dias

        except Exception as e:
            print(f"[OPERADOR] ❌ Erro em tabela_performance: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], [], f"⚠️ Erro ao calcular performance"

    # ================================================================
    # GRÁFICO - Faturamento por Mês
    # ================================================================
    @app.callback(
        Output("grafico-fase-operador", "figure"),
        [
            Input("intervalo-operador", "n_intervals"),
            Input("filtro-ano-operador", "value"),
            Input("filtro-data-range-operador", "start_date"),
            Input("filtro-data-range-operador", "end_date"),
        ],
        [
            State("operador-selecionado-store", "data"),
            State("banco-operador-store", "data"),
        ],
    )
    def atualizar_grafico_mensal(n, ano, data_inicio, data_fim, operador_selecionado, banco):
        """Gráfico de barras: faturamento por mês do ano selecionado.
        
        🔧 CORREÇÃO: Retorno seguro com try/except
        """

        fig_blank = px.bar().update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            title="",
        )

        try:
            if not operador_selecionado:
                return fig_blank

            if operador_selecionado.get("login") == "TODOS":
                return fig_blank

            pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
            if not pagamentos:
                return fig_blank

            df = pd.DataFrame(pagamentos)
            df["dtPgto"] = pd.to_datetime(df["dtPgto"], errors="coerce")
            df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
            df = df.dropna(subset=["dtPgto"])

            _, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
                None,
                int(ano) if ano else date.today().year,
            )

            df_ano = df[df["dtPgto"].dt.year == ano_int]
            if df_ano.empty:
                return fig_blank

            meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                           "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            faturamento_mensal = []

            for mes in range(1, 13):
                df_mes = df_ano[df_ano["dtPgto"].dt.month == mes].copy()
                df_mes = filtrar_fora_da_fase(df_mes, banco)
                fat = float(df_mes["valorTotal"].sum()) if not df_mes.empty else 0.0
                faturamento_mensal.append({
                    "mes":      mes,
                    "mes_nome": meses_nomes[mes - 1],
                    "faturamento": fat,
                })

            df_mensal = pd.DataFrame(faturamento_mensal)
            df_plot = df_mensal[df_mensal["faturamento"] > 0]

            if df_plot.empty:
                return fig_blank

            fig = px.bar(
                df_plot,
                x="mes_nome",
                y="faturamento",
                text="faturamento",
                color_discrete_sequence=["#7e3d97"],
            )
            fig.update_traces(
                texttemplate="R$ %{y:,.0f}",
                textposition="outside",
            )
            fig.update_layout(
                title="",
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis_title="Mês",
                yaxis_title="Faturamento (R$)",
                font=dict(color="#111827"),
            )
            return fig

        except Exception as e:
            print(f"[OPERADOR] ❌ Erro em grafico_mensal: {str(e)}")
            return fig_blank

    # ================================================================
    # CALLBACK: TEMPO DE CASA DO OPERADOR
    # ================================================================
    @app.callback(
        Output("tempo-de-casa", "children"),
        [Input("intervalo-operador", "n_intervals")],
        [
            State("operador-selecionado-store", "data"),
            State("login-success-store", "data")
        ],
    )
    def atualizar_tempo_de_casa(n, operador_selecionado, login_dados):
        """Exibe o tempo de casa calculado com relativedelta.
        
        🔧 CORREÇÃO: Retorno seguro com try/except
        """
        try:
            if not operador_selecionado:
                return ""

            login_op = operador_selecionado.get("login")
            admissao = None
            if login_op == "TODOS" and login_dados:
                admissao = login_dados.get("admissao")
                if not admissao:
                    op_banco = Buscar_login(login_dados.get("login"))
                    if op_banco:
                        admissao = op_banco.get("admissao")
            else:
                admissao = operador_selecionado.get("admissao")
                if not admissao and login_op and login_op != "TODOS":
                    op_banco = Buscar_login(login_op)
                    if op_banco:
                        admissao = op_banco.get("admissao")

            tempo = calcular_tempo_de_casa(admissao)
            return html.Span([
                html.Span("🏠 Tempo de casa: ",
                          style={"fontWeight": "700", "color": "var(--text-muted)"}),
                html.Span(tempo,
                          style={"fontWeight": "600", "color": "#7c3aed"}),
            ])
        except Exception as e:
            print(f"[OPERADOR] ❌ Erro em tempo_de_casa: {str(e)}")
            return ""

    # ================================================================
    # CALLBACK: TABELA FATURAMENTO POR SEMANA
    # ================================================================
    @app.callback(
        [
            Output("tabela-semanas", "data"),
            Output("tabela-semanas", "columns"),
        ],
        [
            Input("intervalo-operador", "n_intervals"),
            Input("filtro-mes-operador", "value"),
            Input("filtro-ano-operador", "value"),
            Input("filtro-data-range-operador", "start_date"),
            Input("filtro-data-range-operador", "end_date"),
        ],
        [
            State("operador-selecionado-store", "data"),
            State("banco-operador-store", "data"),
        ],
    )
    def atualizar_tabela_semanas(n, mes, ano, data_inicio, data_fim, operador_selecionado, banco):
        """Tabela: Semana | Período | Faturamento Total.
        
        🔧 CORREÇÃO: Retorno seguro com try/except
        """

        vazio = [], []

        try:
            if not operador_selecionado:
                return vazio

            if operador_selecionado.get("login") == "TODOS":
                return vazio

            mes_int, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
                int(mes) if mes else date.today().month,
                int(ano) if ano else date.today().year,
            )

            pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
            if not pagamentos:
                return vazio

            linhas = calcular_semanas_do_mes(
                pagamentos=pagamentos,
                ano=ano_int,
                mes=mes_int,
                banco=banco or "SEMEAR",
            )

            if not linhas:
                return vazio

            total_raw = sum(r["faturamento_raw"] for r in linhas)
            total_str = (
                f"R$ {total_raw:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )
            linhas.append({
                "semana":          "TOTAL",
                "periodo":         "—",
                "faturamento_raw": total_raw,
                "faturamento":     total_str,
            })

            colunas = [
                {"name": "Semana",            "id": "semana"},
                {"name": "Período",           "id": "periodo"},
                {"name": "Faturamento Total", "id": "faturamento"},
            ]

            return linhas, colunas

        except Exception as e:
            print(f"[OPERADOR] ❌ Erro em tabela_semanas: {str(e)}")
            return [], []

    # ================================================================
    # TABELA DE VARIAÇÃO MÊS A MÊS — Página de Operadores
    # ================================================================
    @app.callback(
        [
            Output("tabela-evolucao-detalhe", "data"),
            Output("tabela-evolucao-detalhe", "columns"),
            Output("resumo-evolucao-detalhe", "children"),
        ],
        [
            Input("intervalo-operador", "n_intervals"),
            Input("filtro-mes-operador", "value"),
            Input("filtro-ano-operador", "value"),
            Input("filtro-data-range-operador", "start_date"),
            Input("filtro-data-range-operador", "end_date"),
            Input("adm-banco-select", "value"),
            Input("adm-filtro-atividade", "value"),
            Input("adm-operador-select", "value"),
        ],
        [State("login-success-store", "data")]
    )
    def atualizar_evolucao_detalhe(n, mes, ano, data_inicio, data_fim,
                                   banco_sel, filtro_atividade, operador_filtro,
                                   dados_sessao):
        """Variação mês a mês cronológica — do grupo (TODOS) ou de um operador.
        
        🔧 CORREÇÃO: Retorno seguro com try/except
        """
        from src.services.db_service import (
            buscar_pagamentos_todos_operadores_por_banco,
            Buscar_pagamento_por_operador, Buscar_login,
            buscar_metas_por_operador
        )
        import datetime

        try:
            if not dados_sessao:
                return [], [], ""

            perfil = dados_sessao.get("perfil", "operador")
            if perfil == "operador":
                operador_filtro = dados_sessao.get("login")

            banco = banco_sel
            if not banco:
                login = dados_sessao.get("login")
                operador_obj = Buscar_login(login) if login else None
                banco = operador_obj.get("banco") if operador_obj else "SEMEAR"

            _, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
                None,
                int(ano) if ano else datetime.datetime.now().year,
            )

            def _brl(v):
                return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            def _perc_html(v, cor):
                bar = min(v, 100)
                c = "#10B981" if v >= 100 else cor
                return (
                    f'<div style="display:flex;align-items:center;gap:5px;">'
                    f'<div style="flex:1;background:#e5e7eb;border-radius:3px;height:6px;">'
                    f'<div style="width:{bar:.0f}%;background:{c};height:6px;border-radius:3px;"></div></div>'
                    f'<span style="white-space:nowrap;font-weight:700;color:{c};font-size:11px;">{v:.1f}%</span></div>'
                )

            cor_banco_hex = "#7e3d97" if banco == "SEMEAR" else "#10B981"

            try:
                todos = buscar_pagamentos_todos_operadores_por_banco(banco)
            except Exception:
                return [], [], ""

            if not todos:
                return [], [], ""

            lista_pagamentos = []
            metas_por_periodo = {}

            for operador, pagamentos, metas in todos:
                if operador_filtro and operador_filtro != "TODOS":
                    if operador.get("login") != operador_filtro:
                        continue

                ativo = operador.get("ativo", True)
                if filtro_atividade == "ativo" and not ativo:
                    continue

                if pagamentos:
                    lista_pagamentos.extend(pagamentos)

                if metas:
                    for meta in metas:
                        md = meta.get("data")
                        if md:
                            m_val = float(meta.get("meta100") or 0)
                            if hasattr(md, "year"):
                                periodo_key = (md.year, md.month)
                                metas_por_periodo[periodo_key] = metas_por_periodo.get(periodo_key, 0.0) + m_val
                            elif isinstance(md, str):
                                mdt = pd.to_datetime(md, errors="coerce")
                                if not pd.isna(mdt):
                                    periodo_key = (mdt.year, mdt.month)
                                    metas_por_periodo[periodo_key] = metas_por_periodo.get(periodo_key, 0.0) + m_val

            if not lista_pagamentos:
                return [], [], ""

            df_all = pd.DataFrame(lista_pagamentos)
            df_all["dtPgto"] = pd.to_datetime(df_all["dtPgto"], errors="coerce")
            df_all["valorTotal"] = pd.to_numeric(df_all["valorTotal"], errors="coerce").fillna(0.0)
            df_all = df_all.dropna(subset=["dtPgto"])

            if banco == "SEMEAR" and "faseAtraso" in df_all.columns:
                df_all = df_all[df_all["faseAtraso"] != "Fora da fase"]

            linhas = []
            meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                           "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

            for mes_num in range(1, 13):
                meta_atual = metas_por_periodo.get((ano_int, mes_num), 0.0)
                df_mes = df_all[(df_all["dtPgto"].dt.month == mes_num) & (df_all["dtPgto"].dt.year == ano_int)]
                fat_atual = float(df_mes["valorTotal"].sum()) if not df_mes.empty else 0.0
                qtd_atual = len(df_mes)

                if meta_atual <= 0 and fat_atual <= 0:
                    continue

                if mes_num == 1:
                    mes_ant, ano_ant = 12, ano_int - 1
                else:
                    mes_ant, ano_ant = mes_num - 1, ano_int

                meta_ant = metas_por_periodo.get((ano_ant, mes_ant), 0.0)
                df_mes_ant = df_all[(df_all["dtPgto"].dt.month == mes_ant) & (df_all["dtPgto"].dt.year == ano_ant)]
                fat_ant = float(df_mes_ant["valorTotal"].sum()) if not df_mes_ant.empty else 0.0

                if fat_ant > 0:
                    var_pct = ((fat_atual - fat_ant) / fat_ant) * 100
                    seta = "↑" if var_pct >= 0 else "↓"
                    cor_v = "#16a34a" if var_pct >= 0 else "#dc2626"
                    var_pct_str = f'<span style="color:{cor_v};font-weight:700;">{seta} {abs(var_pct):.1f}%</span>'
                else:
                    var_pct = None
                    var_pct_str = "—"

                var_abs = fat_atual - fat_ant
                if var_abs > 0:
                    var_abs_str = f'<span style="color:#16a34a;font-weight:700;">+{_brl(abs(var_abs))}</span>'
                elif var_abs < 0:
                    var_abs_str = f'<span style="color:#dc2626;font-weight:700;">-{_brl(abs(var_abs))}</span>'
                else:
                    var_abs_str = _brl(0)

                perc_atual = (fat_atual / meta_atual * 100) if meta_atual > 0 else 0.0
                perc_ant = (fat_ant / meta_ant * 100) if meta_ant > 0 else 0.0

                if fat_ant > 0 and meta_ant > 0:
                    vm = perc_atual - perc_ant
                    cvm = "#16a34a" if vm >= 0 else "#dc2626"
                    svm = "↑" if vm >= 0 else "↓"
                    var_meta_str = f'<span style="color:{cvm};font-weight:700;">{svm} {abs(vm):.1f}pp</span>'
                else:
                    var_meta_str = "—"

                linhas.append({
                    "periodo":      f"{meses_nomes[mes_num - 1]}/{ano_int}",
                    "faturamento":  _brl(fat_atual),
                    "quantidade":   str(qtd_atual),
                    "meta":         _brl(meta_atual) if meta_atual > 0 else "—",
                    "perc_meta":    _perc_html(perc_atual, cor_banco_hex),
                    "variacao_brl": var_abs_str,
                    "variacao_pct": var_pct_str,
                    "var_meta_pct": var_meta_str,
                    "_var_pct_num": var_pct if var_pct is not None else -9999,
                    "_mes":         mes_num
                })

            if not linhas:
                return [], [], ""

            colunas = [
                {"name": "Período",        "id": "periodo"},
                {"name": "Faturamento",    "id": "faturamento"},
                {"name": "Contratos",      "id": "quantidade"},
                {"name": "Meta",           "id": "meta"},
                {"name": "% Meta",         "id": "perc_meta",    "presentation": "markdown"},
                {"name": "Var. R$",        "id": "variacao_brl", "presentation": "markdown"},
                {"name": "Var. %",         "id": "variacao_pct", "presentation": "markdown"},
                {"name": "Var. % Meta",    "id": "var_meta_pct", "presentation": "markdown"},
            ]

            ultimo_ativo = linhas[-1]
            var_pct_ultimo = ultimo_ativo["_var_pct_num"]
            if var_pct_ultimo != -9999:
                cor_r = "#16a34a" if var_pct_ultimo >= 0 else "#dc2626"
                emoji = "📈" if var_pct_ultimo >= 0 else "📉"
                resumo = html.Div(
                    f"{emoji} Variação de {abs(var_pct_ultimo):.1f}% no último mês ativo ({ultimo_ativo['periodo']}) em relação ao mês anterior.",
                    style={
                        "backgroundColor": "#fffbeb", "color": "#b45309",
                        "padding": "10px 14px", "borderRadius": "6px",
                        "fontWeight": "600", "fontSize": "13.5px",
                        "border": "1px solid #fde68a"
                    }
                )
            else:
                resumo = html.Span("Sem variação calculada para o último período.", 
                                   style={"fontSize": "12px", "color": "#aaa"})

            return linhas, colunas, resumo

        except Exception as e:
            print(f"[OPERADOR] ❌ Erro em evolucao_detalhe: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], [], ""
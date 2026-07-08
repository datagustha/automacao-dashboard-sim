"""
CALLBACKS DO DASHBOARD ADM
===========================
Gerencia os KPIs e as tabelas de ranking para o perfil ADM.
CORRIGIDO:
- Filtro de atividade: compara lowercase corretamente ('ativo' vs 'ATIVO')
- Ranking preenchido com dados reais de cada operador
- Cards de faturamento populados corretamente
- Tabela de evolução diária com linha TOTAL roxa
- Gráficos de evolução diária por banco funcionando
- 🔧 CORRIGIDO: Callback de navegação não entra mais em loop infinito
"""

import pandas as pd
import plotly.graph_objects as go
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from src.services.db_service import (
    buscar_pagamentos_todos_operadores_por_banco,
    buscar_todos_operadores_por_banco,
    buscar_metas_por_operador,
)
from src.services.analytics_service import calcular_performance_operador, calcular_tempo_de_casa
from src.dashboard.components.filtros import aplicar_filtro_data, obter_mes_ano_do_range


# ─── helpers de formatação ───────────────────────────────────────────────────
def _brl(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _num(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return "0"


def _is_ativo(operador, filtro_atividade):
    """Verifica se o operador deve ser incluído conforme o filtro de atividade.
    CORRIGIDO: compara em lowercase para evitar bugs de case.
    """
    if filtro_atividade and filtro_atividade.upper() == "ATIVO":
        return str(operador.get("atividade", "")).strip().lower() == "ativo"
    return True  # "TODOS" → inclui todos


# =========================================================================
# FUNÇÃO AUXILIAR PARA CRIAR GRÁFICO POR BANCO
# =========================================================================
def criar_grafico_por_banco(banco, mes, ano, data_inicio, data_fim, filtro_atividade, operador_filtro, cor, nome_banco):
    """Cria gráfico de evolução diária para um banco específico."""

    mes_int, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
        int(mes) if mes else pd.Timestamp.now().month,
        int(ano) if ano else pd.Timestamp.now().year,
    )

    dados = buscar_pagamentos_todos_operadores_por_banco(banco)

    def _fig_vazio(msg):
        fig = go.Figure()
        fig.update_layout(
            annotations=[dict(
                text=msg, x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=14, color="#9ca3af")
            )],
            height=350,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        return fig

    if not dados:
        return _fig_vazio(f"Sem dados para {nome_banco}")

    todos_pagamentos = []
    for operador, pagamentos, _ in dados:
        if operador_filtro and operador_filtro != "TODOS":
            if operador.get("login") != operador_filtro:
                continue
        if not _is_ativo(operador, filtro_atividade):
            continue
        if pagamentos:
            todos_pagamentos.extend(pagamentos)

    if not todos_pagamentos:
        return _fig_vazio(f"Sem dados para {nome_banco} no período")

    df = pd.DataFrame(todos_pagamentos)
    if "dtPgto" not in df.columns or "valorTotal" not in df.columns:
        return _fig_vazio("Colunas necessárias não encontradas")

    df["dtPgto"] = pd.to_datetime(df["dtPgto"], errors="coerce")
    df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
    df = df.dropna(subset=["dtPgto"])

    df, _, label_periodo = aplicar_filtro_data(df, mes, ano, data_inicio, data_fim)

    if banco == "SEMEAR" and "faseAtraso" in df.columns:
        df = df[df["faseAtraso"] != "Fora da fase"]

    if df.empty:
        return _fig_vazio(f"Sem dados para {nome_banco} no período")

    df["dia"] = df["dtPgto"].dt.day
    df_dia = df.groupby("dia")["valorTotal"].sum().reset_index()
    df_dia = df_dia.sort_values("dia")

    dias = df_dia["dia"].tolist()
    valores = df_dia["valorTotal"].tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dias,
        y=valores,
        mode="lines+markers",
        name=nome_banco,
        line=dict(color=cor, width=3),
        marker=dict(size=8, color=cor),
        hovertemplate="Dia %{x}<br>R$ %{y:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>Evolução Diária — {label_periodo}</b>",
            font=dict(color="#111827", size=14),
            x=0,
            xanchor="left",
        ),
        height=350,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title="Dia do Mês",
            tickmode="linear",
            tick0=1,
            dtick=1,
            showgrid=True,
            gridcolor="#E5E7EB",
        ),
        yaxis=dict(
            title="Recebimento (R$)",
            showgrid=True,
            gridcolor="#E5E7EB",
        ),
        margin=dict(l=60, r=40, t=60, b=40),
    )
    return fig


# =========================================================================
# REGISTRO DOS CALLBACKS
# =========================================================================
def register_callbacks(app):
    """Registra os callbacks do painel ADM."""

    # =========================================================================
    # CALLBACK 1 — KPIs globais + Tabelas de ranking por banco
    # =========================================================================
    @app.callback(
        [
            Output("kpi-fat-semear", "children"),
            Output("kpi-fat-semear-anterior", "children"),
            Output("kpi-fat-agoracred", "children"),
            Output("kpi-fat-agoracred-anterior", "children"),
            Output("kpi-total-ops-adm", "children"),
            Output("kpi-ops-adm-anterior", "children"),
            Output("kpi-ticket-adm", "children"),
            Output("tabela-adm-semear", "data"),
            Output("tabela-adm-semear", "columns"),
            Output("tabela-adm-agoracred", "data"),
            Output("tabela-adm-agoracred", "columns"),
            Output("badge-data-range-adm", "style"),
            # Cards com meta
            Output("kpi-meta-semear", "children"),
            Output("kpi-percentual-semear", "children"),
            Output("barra-progresso-semear", "style"),
            Output("kpi-meta-agoracred", "children"),
            Output("kpi-percentual-agoracred", "children"),
            Output("barra-progresso-agoracred", "style"),
        ],
        [
            Input("intervalo-atualizacao-adm", "n_intervals"),
            Input("url", "pathname"),
            Input("filtro-mes-adm", "value"),
            Input("filtro-ano-adm", "value"),
            Input("filtro-atividade-adm", "value"),
            Input("filtro-operador-adm", "value"),
            Input("filtro-data-range-adm", "start_date"),
            Input("filtro-data-range-adm", "end_date"),
        ],
        [State("login-success-store", "data")],
    )
    def atualizar_dashboard_adm(n, pathname, mes, ano, filtro_atividade, operador_filtro,
                                data_inicio, data_fim, dados_operador):
        """Consolida dados de todos os operadores de ambos os bancos."""

        if pathname != "/dashboard" or not dados_operador:
            return [dash.no_update] * 18

        perfil = dados_operador.get("perfil", "operador")
        if perfil != "adm":
            return [dash.no_update] * 18

        mes_int, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
            int(mes) if mes else pd.Timestamp.now().month,
            int(ano) if ano else pd.Timestamp.now().year,
        )

        if mes_int == 1:
            mes_ant, ano_ant = 12, ano_int - 1
        else:
            mes_ant, ano_ant = mes_int - 1, ano_int

        colunas = [
            {"name": "Foto",          "id": "foto",       "presentation": "markdown"},
            {"name": "Login",         "id": "operador"},
            {"name": "Turno",         "id": "turno"},
            {"name": "Tempo de Casa", "id": "tempo_casa"},
            {"name": "Faturamento",   "id": "faturamento"},
            {"name": "Feito/Dia",     "id": "feito_dia"},
            {"name": "Meta",          "id": "meta"},
            {"name": "% Meta",        "id": "perc_meta",  "presentation": "markdown"},
            {"name": "Falta 70%",     "id": "falta_70"},
            {"name": "Falta 80%",     "id": "falta_80"},
            {"name": "Falta 90%",     "id": "falta_90"},
            {"name": "Ranking",       "id": "ranking"},
            {"name": "Projeção (R$)", "id": "projecao"},
            {"name": "Proj. %",       "id": "proj_perc"},
        ]

        def _parse_brl(s):
            try:
                return float(str(s).replace("R$ ", "").replace(".", "").replace(",", "."))
            except Exception:
                return 0.0

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
                # Filtro por operador específico
                if operador_especifico and operador_especifico != "TODOS":
                    if operador.get("login") != operador_especifico:
                        continue

                # CORRIGIDO: filtro de atividade em lowercase
                if not _is_ativo(operador, filtro_atividade):
                    continue

                if not pagamentos:
                    # Operador sem pagamentos: inclui na tabela se tem meta
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
                    if meta_op > 0:
                        imagem_url0 = operador.get("imagem", "") or ""
                        foto_html0  = (f'<img src="{imagem_url0}" style="width:38px;height:38px;border-radius:50%;object-fit:cover;border:2px solid #e5e7eb;" />' if imagem_url0 else "👤")
                        admissao0   = operador.get("admissao")
                        tempo0      = calcular_tempo_de_casa(admissao0) if admissao0 else "—"
                        linhas_tabela.append({
                            "foto":        foto_html0,
                            "operador":   operador.get("login", ""),
                            "turno":      operador.get("turno", ""),
                            "tempo_casa": tempo0,
                            "faturamento": _brl(0),
                            "feito_dia":   _brl(0),
                            "meta":        _brl(meta_op),
                            "perc_meta":   '<span style="color:#6b7280;font-weight:600;">0,0%</span>',
                            "perc_meta_num": 0.0,
                            "falta_70":    _brl(meta_op * 0.7),
                            "falta_80":    _brl(meta_op * 0.8),
                            "falta_90":    _brl(meta_op * 0.9),
                            "ranking":     _brl(0),
                            "projecao":    _brl(0),
                            "proj_perc":   "0,0%",
                        })
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

                # Filtro "Fora da fase" apenas para SEMEAR
                if banco == "SEMEAR" and "faseAtraso" in df.columns:
                    df = df[df["faseAtraso"] != "Fora da fase"]

                # Calcula meta do operador para o mês atual
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

                try:
                    perf = calcular_performance_operador(
                        pagamentos=pagamentos,
                        metas=metas or [],
                        ano=ano_int,
                        mes=mes_int,
                        login=operador.get("login"),
                        banco=banco,
                    )
                except Exception as e:
                    print(f"[ERRO] Performance {operador.get('login')}: {e}")
                    perf = {
                        "faturamento": fat, "feito_diario": 0, "meta": meta_operador,
                        "atingido_meta": (fat / meta_operador * 100) if meta_operador > 0 else 0,
                        "falta_70": max(0, meta_operador * 0.7 - fat),
                        "falta_80": max(0, meta_operador * 0.8 - fat),
                        "falta_90": max(0, meta_operador * 0.9 - fat),
                        "meta_ranking": 0, "projecao": fat, "projecao_percentual": 0,
                    }

                # ── Foto do operador (HTML inline via markdown) ─────
                imagem_url = operador.get("imagem", "") or ""
                if imagem_url:
                    foto_html = (
                        f'<img src="{imagem_url}" '
                        f'style="width:38px;height:38px;border-radius:50%;'
                        f'object-fit:cover;border:2px solid #e5e7eb;" />'
                    )
                else:
                    foto_html = "👤"

                # ── Tempo de casa ───────────────────────────────────
                admissao_op = operador.get("admissao")
                tempo_casa  = calcular_tempo_de_casa(admissao_op) if admissao_op else "—"

                # ── Barra visual de % meta ──────────────────────────
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

                linhas_tabela.append({
                    "foto":        foto_html,
                    "operador":    operador.get("login", ""),
                    "turno":       operador.get("turno", ""),
                    "tempo_casa":  tempo_casa,
                    "faturamento": _brl(perf.get("faturamento", 0)),
                    "feito_dia":   _brl(perf.get("feito_diario", 0)),
                    "meta":        _brl(perf.get("meta", 0)),
                    "perc_meta":   perc_html,
                    "perc_meta_num": val_perc,
                    "falta_70":    _brl(perf.get("falta_70", 0)),
                    "falta_80":    _brl(perf.get("falta_80", 0)),
                    "falta_90":    _brl(perf.get("falta_90", 0)),
                    "ranking":     _brl(perf.get("meta_ranking", 0)),
                    "projecao":    _brl(perf.get("projecao", 0)),
                    "proj_perc":   f"{perf.get('projecao_percentual', 0):.1f}%",
                })

            # Ordena por % de meta decrescente
            linhas_tabela.sort(key=lambda x: x.get("perc_meta_num", 0), reverse=True)

            return fat_atual, fat_anterior, ops_atual, ops_anterior, soma_tickets, linhas_tabela, meta_total_banco

        fat_s, fat_s_ant, ops_s, ops_s_ant, tickets_s, dados_s, meta_s = processar_banco("SEMEAR", operador_filtro)
        fat_a, fat_a_ant, ops_a, ops_a_ant, tickets_a, dados_a, meta_a = processar_banco("AGORACRED", operador_filtro)

        ops_total    = ops_s + ops_a
        ops_ant_total = ops_s_ant + ops_a_ant
        tickets_total = tickets_s + tickets_a
        ticket_medio  = tickets_total / ops_total if ops_total > 0 else 0.0

        badge_style = {"display": "inline-flex"} if (data_inicio and data_fim) else {"display": "none"}

        percentual_semear    = (fat_s / meta_s * 100) if meta_s > 0 else 0.0
        percentual_agoracred = (fat_a / meta_a * 100) if meta_a > 0 else 0.0

        barra_semear = {
            "width": f"{min(percentual_semear, 100):.1f}%",
            "backgroundColor": "#7e3d97",
            "borderRadius": "5px",
            "height": "8px",
            "transition": "width 0.5s",
        }
        barra_agoracred = {
            "width": f"{min(percentual_agoracred, 100):.1f}%",
            "backgroundColor": "#10B981",
            "borderRadius": "5px",
            "height": "8px",
            "transition": "width 0.5s",
        }

        return (
            _brl(fat_s),
            f"Mês anterior: {_brl(fat_s_ant)}",
            _brl(fat_a),
            f"Mês anterior: {_brl(fat_a_ant)}",
            _num(ops_total),
            f"Mês anterior: {_num(ops_ant_total)}",
            _brl(ticket_medio),
            dados_s, colunas,
            dados_a, colunas,
            badge_style,
            _brl(meta_s),
            f"{percentual_semear:.1f}%",
            barra_semear,
            _brl(meta_a),
            f"{percentual_agoracred:.1f}%",
            barra_agoracred,
        )

    # =========================================================================
    # CALLBACK 2 — GRÁFICO DE EVOLUÇÃO DIÁRIA SEMEAR
    # =========================================================================
    @app.callback(
        Output("grafico-evolucao-semear-adm", "figure"),
        [
            Input("filtro-mes-adm", "value"),
            Input("filtro-ano-adm", "value"),
            Input("filtro-atividade-adm", "value"),
            Input("filtro-operador-adm", "value"),
            Input("filtro-data-range-adm", "start_date"),
            Input("filtro-data-range-adm", "end_date"),
            Input("intervalo-atualizacao-adm", "n_intervals"),
        ],
    )
    def atualizar_grafico_evolucao_semear(mes, ano, filtro_atividade, operador_filtro,
                                          data_inicio, data_fim, n):
        return criar_grafico_por_banco(
            "SEMEAR", mes, ano, data_inicio, data_fim,
            filtro_atividade, operador_filtro, "#7e3d97", "SEMEAR"
        )

    # =========================================================================
    # CALLBACK 3 — GRÁFICO DE EVOLUÇÃO DIÁRIA AGORACRED
    # =========================================================================
    @app.callback(
        Output("grafico-evolucao-agoracred-adm", "figure"),
        [
            Input("filtro-mes-adm", "value"),
            Input("filtro-ano-adm", "value"),
            Input("filtro-atividade-adm", "value"),
            Input("filtro-operador-adm", "value"),
            Input("filtro-data-range-adm", "start_date"),
            Input("filtro-data-range-adm", "end_date"),
            Input("intervalo-atualizacao-adm", "n_intervals"),
        ],
    )
    def atualizar_grafico_evolucao_agoracred(mes, ano, filtro_atividade, operador_filtro,
                                             data_inicio, data_fim, n):
        return criar_grafico_por_banco(
            "AGORACRED", mes, ano, data_inicio, data_fim,
            filtro_atividade, operador_filtro, "#10B981", "AGORACRED"
        )

    # =========================================================================
    # CALLBACK 4 — TABELA DE VALORES DIÁRIOS CONSOLIDADA
    # =========================================================================
    @app.callback(
        [
            Output("tabela-evolucao-diaria-adm", "data"),
            Output("tabela-evolucao-diaria-adm", "columns"),
        ],
        [
            Input("filtro-mes-adm", "value"),
            Input("filtro-ano-adm", "value"),
            Input("filtro-atividade-adm", "value"),
            Input("filtro-operador-adm", "value"),
            Input("filtro-data-range-adm", "start_date"),
            Input("filtro-data-range-adm", "end_date"),
            Input("intervalo-atualizacao-adm", "n_intervals"),
        ],
    )
    def atualizar_tabela_evolucao_adm(mes, ano, filtro_atividade, operador_filtro,
                                      data_inicio, data_fim, n):
        """Tabela de valores diários: Dia | SEMEAR | AGORACRED | TOTAL"""

        def buscar_dados_por_banco(banco):
            dados = buscar_pagamentos_todos_operadores_por_banco(banco)
            if not dados:
                return {}

            todos_pagamentos = []
            for operador, pagamentos, _ in dados:
                if operador_filtro and operador_filtro != "TODOS":
                    if operador.get("login") != operador_filtro:
                        continue
                if not _is_ativo(operador, filtro_atividade):
                    continue
                if pagamentos:
                    todos_pagamentos.extend(pagamentos)

            if not todos_pagamentos:
                return {}

            df = pd.DataFrame(todos_pagamentos)
            if "dtPgto" not in df.columns or "valorTotal" not in df.columns:
                return {}

            df["dtPgto"]     = pd.to_datetime(df["dtPgto"], errors="coerce")
            df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
            df = df.dropna(subset=["dtPgto"])

            df, _, _ = aplicar_filtro_data(df, mes, ano, data_inicio, data_fim)

            if banco == "SEMEAR" and "faseAtraso" in df.columns:
                df = df[df["faseAtraso"] != "Fora da fase"]

            if df.empty:
                return {}

            df["dia"] = df["dtPgto"].dt.day
            df_dia = df.groupby("dia")["valorTotal"].sum().reset_index()
            return dict(zip(df_dia["dia"], df_dia["valorTotal"]))

        semear_dict   = buscar_dados_por_banco("SEMEAR")
        agoracred_dict = buscar_dados_por_banco("AGORACRED")

        todos_dias = sorted(set(list(semear_dict.keys()) + list(agoracred_dict.keys())))

        if not todos_dias:
            return [], []

        def _fmt(v):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        dados_tabela = []
        for dia in todos_dias:
            sv = semear_dict.get(dia, 0)
            av = agoracred_dict.get(dia, 0)
            dados_tabela.append({
                "dia":      dia,
                "semear":   _fmt(sv),
                "agoracred": _fmt(av),
                "total":    _fmt(sv + av),
            })

        total_s = sum(semear_dict.values())
        total_a = sum(agoracred_dict.values())
        dados_tabela.append({
            "dia":       "📊 TOTAL DO PERÍODO",
            "semear":    _fmt(total_s),
            "agoracred": _fmt(total_a),
            "total":     _fmt(total_s + total_a),
        })

        colunas = [
            {"name": "📅 Dia",              "id": "dia"},
            {"name": "🟣 SEMEAR (R$)",      "id": "semear"},
            {"name": "🟢 AGORACRED (R$)",   "id": "agoracred"},
            {"name": "⚫ TOTAL (R$)",        "id": "total"},
        ]
        return dados_tabela, colunas

    # =========================================================================
    # CALLBACK 5 — Popula dropdown de operadores no Dashboard ADM
    # =========================================================================
    @app.callback(
        Output("filtro-operador-adm", "options"),
        [
            Input("filtro-mes-adm", "value"),
            Input("filtro-ano-adm", "value"),
            Input("filtro-atividade-adm", "value"),
        ],
    )
    def carregar_operadores_dashboard(mes, ano, atividade):
        todos_operadores = []
        for banco in ("SEMEAR", "AGORACRED"):
            try:
                ops = buscar_todos_operadores_por_banco(banco)
                if ops:
                    todos_operadores.extend(ops)
            except Exception:
                pass

        if not todos_operadores:
            return [{"label": "📊 Todos os Operadores", "value": "TODOS"}]

        # CORRIGIDO: lowercase
        if atividade and atividade.upper() == "ATIVO":
            todos_operadores = [op for op in todos_operadores
                                if str(op.get("atividade", "")).strip().lower() == "ativo"]

        logins_vistos = set()
        operadores_unicos = []
        for op in todos_operadores:
            login = op.get("login")
            if login and login not in logins_vistos:
                logins_vistos.add(login)
                operadores_unicos.append(op)

        operadores_unicos.sort(key=lambda x: x.get("login", ""))

        opcoes = [{"label": "📊 Todos os Operadores", "value": "TODOS"}]
        for op in operadores_unicos:
            login = op.get("login")
            if login:
                opcoes.append({"label": login, "value": login})
        return opcoes

    # =========================================================================
    # CALLBACK 6 — Popula dropdown de operadores no Detalhe ADM
    # =========================================================================
    @app.callback(
        Output("adm-operador-select", "options"),
        [
            Input("adm-banco-select", "value"),
            Input("adm-filtro-atividade", "value"),
        ],
    )
    def carregar_operadores_banco(banco, atividade):
        if not banco:
            return []

        operadores = buscar_todos_operadores_por_banco(banco)

        # CORRIGIDO: lowercase
        if atividade and atividade.lower() == "ativo":
            operadores = [op for op in operadores
                          if str(op.get("atividade", "")).strip().lower() == "ativo"]

        opcoes = [{"label": "🌟 Todos", "value": "TODOS"}]
        opcoes.extend(
            [{"label": op["login"], "value": op["login"]}
             for op in operadores if op.get("login")]
        )
        return opcoes

    # =========================================================================
    # CALLBACK 7 — Navega automaticamente ao alterar banco ou operador
    # 🔧 CORRIGIDO: Não entra mais em loop infinito
    # =========================================================================
    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        [
            Input("adm-banco-select", "value"),
            Input("adm-operador-select", "value"),
        ],
        [State("url", "pathname")],
        prevent_initial_call=True,
    )
    def navegar_para_operador(banco, login_operador, current_pathname):
        """
        Navega para a URL do operador selecionado.
        🔧 CORREÇÃO: Verifica se a URL já está correta antes de navegar.
        """
        # Se não tem banco, não faz nada
        if not banco:
            raise PreventUpdate
        
        # Se não tem operador selecionado, não faz nada
        if not login_operador:
            raise PreventUpdate
        
        # Constrói a URL de destino
        if login_operador == "TODOS":
            nova_url = f"/operadores/{banco}/TODOS"
        else:
            nova_url = f"/operadores/{banco}/{login_operador}"
        
        # 🔥 SÓ NAVEGA SE A URL FOR DIFERENTE
        if current_pathname == nova_url:
            raise PreventUpdate
        
        return nova_url

    # =========================================================================
    # CALLBACK 8 — Tabela de Ranking de TMA (Acionamento por Operadores)
    # =========================================================================
    @app.callback(
        [
            Output("tabela-tma-adm", "data"),
            Output("tabela-tma-adm", "columns"),
        ],
        [
            Input("filtro-mes-adm", "value"),
            Input("filtro-ano-adm", "value"),
            Input("filtro-atividade-adm", "value"),
            Input("filtro-operador-adm", "value"),
            Input("intervalo-atualizacao-adm", "n_intervals"),
        ],
        [State("login-success-store", "data")],
    )
    def atualizar_tabela_tma_adm(mes, ano, filtro_atividade, operador_filtro, n, dados_operador):
        """
        Lê os CSVs de TMA processados de ambos os bancos (SEMEAR e AGORACRED)
        e monta um ranking de acionamentos para o ADM.
        """
        import pathlib
        from datetime import datetime

        if not dados_operador:
            return [], []

        perfil = dados_operador.get("perfil", "operador")
        if perfil != "adm":
            return [], []

        mes_int  = int(mes) if mes else datetime.now().month
        ano_int  = int(ano) if ano else datetime.now().year
        mesabrev = datetime(ano_int, mes_int, 1).strftime("%b")

        BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent

        # Busca operadores ativos se o filtro estiver setado para ATIVO
        ativos_por_banco = {}
        if filtro_atividade and filtro_atividade.upper() == "ATIVO":
            for b in ("SEMEAR", "AGORACRED"):
                try:
                    ops = buscar_todos_operadores_por_banco(b)
                    if ops:
                        ativos_por_banco[b.lower()] = {
                            str(op.get("login")).strip().upper() for op in ops
                            if str(op.get("atividade", "")).strip().lower() == "ativo" and op.get("login")
                        }
                except Exception as e:
                    print(f"[TMA-ADM] Erro ao buscar ativos para {b}: {e}")

        linhas = []

        for banco in ("semear", "agoracred"):
            caminho_csv = (
                BASE_DIR / "data" / "processed" / banco / "tma" / str(ano_int)
                / f"tma_{banco}_{mes_int}_{mesabrev}_{ano_int}.csv"
            )

            if not caminho_csv.exists():
                continue

            try:
                df = pd.read_csv(caminho_csv)
            except Exception as e:
                print(f"[TMA-ADM] Erro ao ler CSV {banco}: {e}")
                continue

            if df.empty or "operador" not in df.columns:
                continue

            # Filtro por operador específico
            if operador_filtro and operador_filtro != "TODOS":
                df = df[df["operador"].astype(str).str.strip().str.upper()
                        == operador_filtro.strip().upper()]

            for _, row in df.iterrows():
                op_login = str(row.get("operador", "")).strip()

                # Filtro de atividade: se estiver marcado ATIVO, ignora os inativos
                if filtro_atividade and filtro_atividade.upper() == "ATIVO":
                    banco_key = banco.lower()
                    if banco_key in ativos_por_banco:
                        if op_login.upper() not in ativos_por_banco[banco_key]:
                            continue

                tts = int(row.get("tempoTotalSegundos", 0) or 0)
                h   = tts // 3600
                m   = (tts % 3600) // 60
                tempo_falado = f"{h}h {m:02d}min"

                ritmo = float(row.get("acionamentosPorHoraAtiva", 0) or 0)
                taxa  = float(row.get("taxaAcionamentoCliente", 0) or 0)

                # Formata data para o padrão BR: DD/MM/YYYY HH:MM:SS
                def _fmt_data(val):
                    if pd.isna(val) or not val or str(val).strip() in ("—", "nan", "None", ""):
                        return "—"
                    try:
                        dt = pd.to_datetime(val)
                        return dt.strftime("%d/%m/%Y %H:%M:%S")
                    except:
                        return str(val)

                linhas.append({
                    "operador":      op_login,
                    "tma":           str(row.get("tempoMedio", "—")),
                    "acionamentos":  int(row.get("qtdeAcionamentos", 0) or 0),
                    "clientes":      int(row.get("qtdeClientes", 0) or 0),
                    "ritmo":         f"{ritmo:.1f}",
                    "reacionamento": round(taxa, 2),
                    "tempo_falado":  tempo_falado,
                    "primeiro":      _fmt_data(row.get("primeiroAcionamento")),
                    "ultimo":        _fmt_data(row.get("ultimoAcionamento")),
                })

        if not linhas:
            return [], []

        # Ordena por quantidade de acionamentos (desc)
        linhas.sort(key=lambda x: x.get("acionamentos", 0), reverse=True)

        colunas = [
            {"name": "Operador",      "id": "operador"},
            {"name": "TMA",           "id": "tma"},
            {"name": "Acionamentos",  "id": "acionamentos"},
            {"name": "Clientes",      "id": "clientes"},
            {"name": "Ritmo/Hora",    "id": "ritmo"},
            {"name": "Reacionamento", "id": "reacionamento"},
            {"name": "Tempo Falado",  "id": "tempo_falado"},
            {"name": "1º Acion.",     "id": "primeiro"},
            {"name": "Últ. Acion.",   "id": "ultimo"},
        ]

        return linhas, colunas
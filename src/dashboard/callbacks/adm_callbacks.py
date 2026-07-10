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
            Output("badge-filtros-ativos-adm", "style"),
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
            Input("filtro-contrato-adm", "value"),
            Input("filtro-faixa-adm", "value"),
        ],
        [State("login-success-store", "data")],
    )
    def atualizar_dashboard_adm(n, pathname, mes, ano, filtro_atividade, operador_filtro,
                                data_inicio, data_fim, filtro_contrato, filtro_faixa, dados_operador):
        """Consolida dados de todos os operadores de ambos os bancos."""
        
        if pathname != "/dashboard" or not dados_operador:
            return [dash.no_update] * 19

        perfil = dados_operador.get("perfil", "operador")
        if perfil != "adm":
            return [dash.no_update] * 19

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

                # ─ Filtro de Contrato / Cliente ────────────────────────────
                if filtro_contrato and str(filtro_contrato).strip():
                    texto = str(filtro_contrato).strip().lower()
                    mask_contrato = df["contrato"].fillna("").astype(str).str.lower().str.contains(texto)
                    if "cliente" in df.columns:
                        mask_cliente = df["cliente"].fillna("").astype(str).str.lower().str.contains(texto)
                        df = df[mask_contrato | mask_cliente]
                    else:
                        df = df[mask_contrato]

                # ─ Filtro de Faixa de Atraso (apenas SEMEAR) ────────────────
                if banco == "SEMEAR" and filtro_faixa and filtro_faixa != "todas":
                    if "faseAtraso" in df.columns:
                        df = df[df["faseAtraso"].fillna("").astype(str).str.strip() == str(filtro_faixa).strip()]

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
                    # Usa df_atual (já filtrado por date range ou mês) em vez dos pagamentos brutos
                    # Isso garante que feito/dia, %meta, falta 70/80/90 e projeção respeitem o filtro
                    pags_para_perf = df_atual.to_dict('records') if not df_atual.empty else []
                    perf = calcular_performance_operador(
                        pagamentos=pags_para_perf,
                        metas=metas or [],
                        ano=ano_int,
                        mes=mes_int,
                        login=operador.get("login"),
                        banco=banco,
                    )
                    # Garante que o faturamento da perf bate com o fat calculado do df_atual
                    # (pode haver pequena divergência se calcular_performance_operador fizer filtro adicional)
                    if pags_para_perf:
                        perf["faturamento"] = fat
                        if perf.get("meta", 0) > 0:
                            perf["atingido_meta"] = (fat / perf["meta"]) * 100
                            perf["falta_70"] = max(0, perf["meta"] * 0.7 - fat)
                            perf["falta_80"] = max(0, perf["meta"] * 0.8 - fat)
                            perf["falta_90"] = max(0, perf["meta"] * 0.9 - fat)
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

        from dash import html

        # ── Cálculos de variação e falta de meta para Semear ─────────────────
        if fat_s_ant > 0:
            var_s_pct = ((fat_s - fat_s_ant) / fat_s_ant) * 100
            seta_s = "↑" if var_s_pct >= 0 else "↓"
            cor_var_s = "#16a34a" if var_s_pct >= 0 else "#dc2626"
            bg_var_s = "#dcfce7" if var_s_pct >= 0 else "#fee2e2"
            var_s_badge = html.Span(
                f"{seta_s} {abs(var_s_pct):.1f}%",
                style={
                    "color": cor_var_s, "backgroundColor": bg_var_s,
                    "padding": "2px 6px", "borderRadius": "4px", "fontWeight": "700", "fontSize": "11px",
                    "marginLeft": "6px", "display": "inline-block"
                }
            )
        else:
            var_s_badge = html.Span("—", style={"marginLeft": "6px"})

        falta_s = max(0.0, meta_s - fat_s)
        falta_s_pct = ((meta_s - fat_s) / meta_s * 100) if meta_s > 0 else 0.0
        if falta_s > 0:
            falta_s_comp = html.Div([
                html.Span(f"Falta: {_brl(falta_s)}", style={"fontWeight": "700", "color": "var(--text-main)", "fontSize": "12px"}),
                html.Span(
                    f"{falta_s_pct:.1f}% abaixo",
                    style={
                        "color": "#d97706", "backgroundColor": "#fef3c7",
                        "padding": "2px 6px", "borderRadius": "4px", "fontWeight": "700", "fontSize": "11px",
                        "marginLeft": "6px", "display": "inline-block"
                    }
                )
            ])
        else:
            falta_s_comp = html.Div(
                "Meta Atingida! 🎉",
                style={"fontWeight": "700", "color": "#16a34a", "fontSize": "12px"}
            )

        subtexto_semear = html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "width": "100%", "marginTop": "2px"},
            children=[
                html.Div([
                    html.Span("Mês Anterior", style={"fontSize": "11px", "color": "var(--text-muted)", "display": "block", "marginBottom": "2px"}),
                    html.Div([
                        html.Span(_brl(fat_s_ant), style={"fontWeight": "700", "color": "var(--text-main)", "fontSize": "12px"}),
                        var_s_badge
                    ], style={"display": "flex", "alignItems": "center"})
                ]),
                html.Div([
                    html.Span("Diferença da Meta", style={"fontSize": "11px", "color": "var(--text-muted)", "display": "block", "marginBottom": "2px", "textAlign": "right"}),
                    falta_s_comp
                ], style={"textAlign": "right"})
            ]
        )

        # ── Cálculos de variação e falta de meta para Agoracred ──────────────
        if fat_a_ant > 0:
            var_a_pct = ((fat_a - fat_a_ant) / fat_a_ant) * 100
            seta_a = "↑" if var_a_pct >= 0 else "↓"
            cor_var_a = "#16a34a" if var_a_pct >= 0 else "#dc2626"
            bg_var_a = "#dcfce7" if var_a_pct >= 0 else "#fee2e2"
            var_a_badge = html.Span(
                f"{seta_a} {abs(var_a_pct):.1f}%",
                style={
                    "color": cor_var_a, "backgroundColor": bg_var_a,
                    "padding": "2px 6px", "borderRadius": "4px", "fontWeight": "700", "fontSize": "11px",
                    "marginLeft": "6px", "display": "inline-block"
                }
            )
        else:
            var_a_badge = html.Span("—", style={"marginLeft": "6px"})

        falta_a = max(0.0, meta_a - fat_a)
        falta_a_pct = ((meta_a - fat_a) / meta_a * 100) if meta_a > 0 else 0.0
        if falta_a > 0:
            falta_a_comp = html.Div([
                html.Span(f"Falta: {_brl(falta_a)}", style={"fontWeight": "700", "color": "var(--text-main)", "fontSize": "12px"}),
                html.Span(
                    f"{falta_a_pct:.1f}% abaixo",
                    style={
                        "color": "#d97706", "backgroundColor": "#fef3c7",
                        "padding": "2px 6px", "borderRadius": "4px", "fontWeight": "700", "fontSize": "11px",
                        "marginLeft": "6px", "display": "inline-block"
                    }
                )
            ])
        else:
            falta_a_comp = html.Div(
                "Meta Atingida! 🎉",
                style={"fontWeight": "700", "color": "#16a34a", "fontSize": "12px"}
            )

        subtexto_agoracred = html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "width": "100%", "marginTop": "2px"},
            children=[
                html.Div([
                    html.Span("Mês Anterior", style={"fontSize": "11px", "color": "var(--text-muted)", "display": "block", "marginBottom": "2px"}),
                    html.Div([
                        html.Span(_brl(fat_a_ant), style={"fontWeight": "700", "color": "var(--text-main)", "fontSize": "12px"}),
                        var_a_badge
                    ], style={"display": "flex", "alignItems": "center"})
                ]),
                html.Div([
                    html.Span("Diferença da Meta", style={"fontSize": "11px", "color": "var(--text-muted)", "display": "block", "marginBottom": "2px", "textAlign": "right"}),
                    falta_a_comp
                ], style={"textAlign": "right"})
            ]
        )

        return (
            _brl(fat_s),
            subtexto_semear,
            _brl(fat_a),
            subtexto_agoracred,
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
            # badge filtros ativos
            {"display": "inline-block"} if (filtro_contrato and str(filtro_contrato).strip()) or (filtro_faixa and filtro_faixa != "todas") else {"display": "none"},
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
        🔧 CORREÇÃO REFORÇADA: Só navega se:
        1. A URL atual já é /operadores (State no momento do trigger)
        2. Banco e operador têm valores válidos
        3. A nova URL é diferente da atual
        4. O trigger foi explicitamente de adm-banco-select ou adm-operador-select
        """
        import dash

        # Guard 1: URL atual deve ser /operadores
        if not current_pathname or not current_pathname.startswith("/operadores"):
            raise PreventUpdate

        # Guard 2: contexto — o trigger deve ser um dos selects
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger_id not in ("adm-banco-select", "adm-operador-select"):
            raise PreventUpdate

        # Guard 3: valores válidos
        if not banco:
            raise PreventUpdate
        if not login_operador:
            raise PreventUpdate

        # Constrói a URL de destino
        if login_operador == "TODOS":
            nova_url = f"/operadores/{banco}/TODOS"
        else:
            nova_url = f"/operadores/{banco}/{login_operador}"

        # Guard 4: só navega se URL for diferente
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
        # Mapa de login → imagem para a tabela TMA
        imagem_por_login = {}
        if filtro_atividade and filtro_atividade.upper() == "ATIVO":
            for b in ("SEMEAR", "AGORACRED"):
                try:
                    ops = buscar_todos_operadores_por_banco(b)
                    if ops:
                        ativos_por_banco[b.lower()] = {
                            str(op.get("login")).strip().upper() for op in ops
                            if str(op.get("atividade", "")).strip().lower() == "ativo" and op.get("login")
                        }
                        for op in ops:
                            lg = str(op.get("login", "")).strip().upper()
                            if lg and op.get("imagem"):
                                imagem_por_login[lg] = op["imagem"]
                except Exception as e:
                    print(f"[TMA-ADM] Erro ao buscar ativos para {b}: {e}")
        else:
            for b in ("SEMEAR", "AGORACRED"):
                try:
                    ops = buscar_todos_operadores_por_banco(b)
                    if ops:
                        for op in ops:
                            lg = str(op.get("login", "")).strip().upper()
                            if lg and op.get("imagem"):
                                imagem_por_login[lg] = op["imagem"]
                except Exception:
                    pass

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

                taxa  = float(row.get("taxaAcionamentoCliente", 0) or 0)

                # Foto do operador (via mapa de imagens)
                imagem_tma = imagem_por_login.get(op_login.upper(), "")
                foto_html_tma = (
                    f'<img src="{imagem_tma}" style="width:34px;height:34px;border-radius:50%;'
                    f'object-fit:cover;border:2px solid #e5e7eb;" />'
                    if imagem_tma else "👤"
                )

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
                    "foto":          foto_html_tma,
                    "banco":         banco.upper(),
                    "operador":      op_login,
                    "tma":           str(row.get("tempoMedio", "—")),
                    "acionamentos":  int(row.get("qtdeAcionamentos", 0) or 0),
                    "clientes":      int(row.get("qtdeClientes", 0) or 0),
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
            {"name": "Foto",          "id": "foto",         "presentation": "markdown"},
            {"name": "Banco",         "id": "banco"},
            {"name": "Operador",      "id": "operador"},
            {"name": "TMA",           "id": "tma"},
            {"name": "Acionamentos",  "id": "acionamentos"},
            {"name": "Clientes",      "id": "clientes"},
            {"name": "Reacionamento", "id": "reacionamento"},
            {"name": "Tempo Falado",  "id": "tempo_falado"},
            {"name": "1º Acion.",     "id": "primeiro"},
            {"name": "Últ. Acion.",   "id": "ultimo"},
        ]

        return linhas, colunas

    # =========================================================================
    # CALLBACK 9 — Tabela de Recebimento por Operador × Faixa de Atraso (SEMEAR)
    # =========================================================================
    @app.callback(
        [
            Output("tabela-faixas-semear", "data"),
            Output("tabela-faixas-semear", "columns"),
        ],
        [
            Input("filtro-mes-adm", "value"),
            Input("filtro-ano-adm", "value"),
            Input("filtro-atividade-adm", "value"),
            Input("filtro-operador-adm", "value"),
            Input("filtro-data-range-adm", "start_date"),
            Input("filtro-data-range-adm", "end_date"),
            Input("filtro-contrato-adm", "value"),
            Input("intervalo-atualizacao-adm", "n_intervals"),
        ],
        [State("login-success-store", "data")],
    )
    def atualizar_tabela_faixas_semear(mes, ano, filtro_atividade, operador_filtro,
                                       data_inicio, data_fim, filtro_contrato, n, dados_operador):
        """Crosstab: Operador × Faixa de Atraso — soma valorTotal SEMEAR."""
        if not dados_operador or dados_operador.get("perfil") != "adm":
            return [], []

        mes_int, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
            int(mes) if mes else pd.Timestamp.now().month,
            int(ano) if ano else pd.Timestamp.now().year,
        )

        dados = buscar_pagamentos_todos_operadores_por_banco("SEMEAR")
        if not dados:
            return [], []

        todos_pagamentos = []
        for operador, pagamentos, _ in dados:
            if operador_filtro and operador_filtro != "TODOS":
                if operador.get("login") != operador_filtro:
                    continue
            if not _is_ativo(operador, filtro_atividade):
                continue
            if pagamentos:
                for p in pagamentos:
                    p["_operador"] = operador.get("login", "")
                todos_pagamentos.extend(pagamentos)

        if not todos_pagamentos:
            return [], []

        df = pd.DataFrame(todos_pagamentos)
        df["dtPgto"]     = pd.to_datetime(df["dtPgto"], errors="coerce")
        df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
        df = df.dropna(subset=["dtPgto"])

        df, _, _ = aplicar_filtro_data(df, mes, ano, data_inicio, data_fim)

        # Remove "Fora da fase"
        if "faseAtraso" in df.columns:
            df = df[df["faseAtraso"] != "Fora da fase"]

        # Filtro de contrato/cliente
        if filtro_contrato and str(filtro_contrato).strip():
            texto = str(filtro_contrato).strip().lower()
            mask = df["contrato"].fillna("").astype(str).str.lower().str.contains(texto)
            if "cliente" in df.columns:
                mask |= df["cliente"].fillna("").astype(str).str.lower().str.contains(texto)
            df = df[mask]

        if df.empty or "faseAtraso" not in df.columns:
            return [], []

        # Crosstab operador × faseAtraso
        df["operador_col"] = df["_operador"]
        pivot = df.groupby(["operador_col", "faseAtraso"])["valorTotal"].sum().unstack(fill_value=0)
        pivot = pivot.reset_index().rename(columns={"operador_col": "operador"})

        # Busca foto dos operadores para adicionar na tabela
        ativos_por_banco = {}
        imagem_por_login = {}
        try:
            ops = buscar_todos_operadores_por_banco("SEMEAR")
            if ops:
                for op in ops:
                    lg = str(op.get("login", "")).strip().upper()
                    if lg and op.get("imagem"):
                        imagem_por_login[lg] = op["imagem"]
        except Exception:
            pass

        # Ordena colunas (fases) por valor numérico inicial
        fases_cols = [c for c in pivot.columns if c != "operador"]
        def _fase_sort_key(f):
            import re
            nums = re.findall(r'\d+', str(f))
            return int(nums[0]) if nums else 99999
        fases_cols.sort(key=_fase_sort_key)

        # Linha TOTAL
        totais = {"operador": "📊 TOTAL"}
        for f in fases_cols:
            totais[f] = pivot[f].sum()
        pivot = pd.concat([pivot, pd.DataFrame([totais])], ignore_index=True)

        def _fmt(v):
            try:
                return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                return str(v)

        # Total por linha
        dados_tabela = []
        for _, row in pivot.iterrows():
            op_nome = row["operador"]
            
            # Formata foto se não for a linha TOTAL
            if op_nome != "📊 TOTAL":
                imagem_op = imagem_por_login.get(str(op_nome).upper(), "")
                foto_html = (
                    f'<img src="{imagem_op}" style="width:34px;height:34px;border-radius:50%;'
                    f'object-fit:cover;border:2px solid #e5e7eb;" />'
                    if imagem_op else "👤"
                )
            else:
                foto_html = ""

            linha = {
                "foto": foto_html,
                "operador": op_nome
            }
            
            total_linha = 0.0
            for f in fases_cols:
                v = float(row.get(f, 0))
                linha[f] = _fmt(v)
                total_linha += v
            linha["__total"] = _fmt(total_linha)
            dados_tabela.append(linha)

        colunas = [
            {"name": "Foto", "id": "foto", "presentation": "markdown"},
            {"name": "Operador", "id": "operador"}
        ]
        colunas += [{"name": f, "id": f} for f in fases_cols]
        colunas += [{"name": "⏫ Total", "id": "__total"}]

        return dados_tabela, colunas

    # =========================================================================
    # CALLBACK 10 — Tabela de Evolução dos Operadores (Variação vs Mês Anterior)
    # =========================================================================
    @app.callback(
        [
            Output("tabela-evolucao-operadores-adm", "data"),
            Output("tabela-evolucao-operadores-adm", "columns"),
            Output("resumo-evolucao-adm", "children"),
        ],
        [
            Input("filtro-mes-adm", "value"),
            Input("filtro-ano-adm", "value"),
            Input("filtro-atividade-adm", "value"),
            Input("filtro-operador-adm", "value"),
            Input("filtro-data-range-adm", "start_date"),
            Input("filtro-data-range-adm", "end_date"),
            Input("filtro-contrato-adm", "value"),
            Input("filtro-faixa-adm", "value"),
            Input("intervalo-atualizacao-adm", "n_intervals"),
        ],
        [State("login-success-store", "data")],
    )
    def atualizar_tabela_evolucao_operadores(mes, ano, filtro_atividade, operador_filtro,
                                             data_inicio, data_fim, filtro_contrato, filtro_faixa,
                                             n, dados_operador):
        """Compara fat. atual vs mês anterior para cada operador, com variação % e % da meta."""
        if not dados_operador or dados_operador.get("perfil") != "adm":
            return [], [], ""

        mes_int, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
            int(mes) if mes else pd.Timestamp.now().month,
            int(ano) if ano else pd.Timestamp.now().year,
        )

        # Período anterior
        if mes_int == 1:
            mes_ant, ano_ant = 12, ano_int - 1
        else:
            mes_ant, ano_ant = mes_int - 1, ano_int

        linhas = []

        for banco in ("SEMEAR", "AGORACRED"):
            cor_banco = "🟣" if banco == "SEMEAR" else "🟢"
            dados = buscar_pagamentos_todos_operadores_por_banco(banco)
            if not dados:
                continue

            for operador, pagamentos, metas in dados:
                if operador_filtro and operador_filtro != "TODOS":
                    if operador.get("login") != operador_filtro:
                        continue
                if not _is_ativo(operador, filtro_atividade):
                    continue
                if not pagamentos:
                    continue

                try:
                    df = pd.DataFrame(pagamentos)
                except Exception:
                    continue

                df["dtPgto"]     = pd.to_datetime(df["dtPgto"], errors="coerce")
                df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
                df = df.dropna(subset=["dtPgto"])
                if df.empty:
                    continue

                # Remove "Fora da fase" para SEMEAR
                if banco == "SEMEAR" and "faseAtraso" in df.columns:
                    df = df[df["faseAtraso"] != "Fora da fase"]

                # Filtro contrato/cliente
                if filtro_contrato and str(filtro_contrato).strip():
                    texto = str(filtro_contrato).strip().lower()
                    mask = df["contrato"].fillna("").astype(str).str.lower().str.contains(texto)
                    if "cliente" in df.columns:
                        mask |= df["cliente"].fillna("").astype(str).str.lower().str.contains(texto)
                    df = df[mask]

                # Filtro de faixa (SEMEAR)
                if banco == "SEMEAR" and filtro_faixa and filtro_faixa != "todas":
                    if "faseAtraso" in df.columns:
                        df = df[df["faseAtraso"].fillna("").astype(str).str.strip() == str(filtro_faixa).strip()]

                # Período atual
                df_atual, _, _ = aplicar_filtro_data(df, mes, ano, data_inicio, data_fim)

                # Período anterior (mesmo intervalo de dias do mês anterior)
                if data_inicio and data_fim:
                    try:
                        dt_inicio_ant = pd.to_datetime(data_inicio) - pd.DateOffset(months=1)
                        dt_fim_ant    = pd.to_datetime(data_fim) - pd.DateOffset(months=1)
                        df_ant = df[
                            (df["dtPgto"] >= dt_inicio_ant) &
                            (df["dtPgto"] <= dt_fim_ant + pd.Timedelta(hours=23, minutes=59, seconds=59))
                        ].copy()
                    except Exception:
                        df_ant = df[
                            (df["dtPgto"].dt.month == mes_ant) &
                            (df["dtPgto"].dt.year  == ano_ant)
                        ].copy()
                else:
                    df_ant = df[
                        (df["dtPgto"].dt.month == mes_ant) &
                        (df["dtPgto"].dt.year  == ano_ant)
                    ].copy()

                fat_atual = float(df_atual["valorTotal"].sum()) if not df_atual.empty else 0.0
                fat_ant   = float(df_ant["valorTotal"].sum())   if not df_ant.empty   else 0.0

                # Variação
                if fat_ant > 0:
                    var_pct = ((fat_atual - fat_ant) / fat_ant) * 100
                    seta = "↑" if var_pct >= 0 else "↓"
                    cor_v = "#16a34a" if var_pct >= 0 else "#dc2626"
                    var_pct_str = (
                        f'<span style="color:{cor_v};font-weight:700;">{seta} {abs(var_pct):.1f}%</span>'
                    )
                else:
                    var_pct     = None
                    var_pct_str = "—"

                var_abs = fat_atual - fat_ant
                var_abs_str = _brl(abs(var_abs))
                if var_abs > 0:
                    var_abs_str = f'<span style="color:#16a34a;font-weight:700;">+{var_abs_str}</span>'
                elif var_abs < 0:
                    var_abs_str = f'<span style="color:#dc2626;font-weight:700;">-{var_abs_str}</span>'

                # % Meta atual e anterior
                meta_op = 0.0
                meta_ant_op = 0.0
                if metas:
                    for meta in metas:
                        md = meta.get("data")
                        if md:
                            if hasattr(md, "year"):
                                if md.year == ano_int and md.month == mes_int:
                                    meta_op = float(meta.get("meta100") or 0)
                                elif md.year == ano_ant and md.month == mes_ant:
                                    meta_ant_op = float(meta.get("meta100") or 0)
                            elif isinstance(md, str):
                                mdt = pd.to_datetime(md, errors="coerce")
                                if not pd.isna(mdt):
                                    if mdt.year == ano_int and mdt.month == mes_int:
                                        meta_op = float(meta.get("meta100") or 0)
                                    elif mdt.year == ano_ant and mdt.month == mes_ant:
                                        meta_ant_op = float(meta.get("meta100") or 0)

                perc_atual = (fat_atual / meta_op * 100) if meta_op > 0 else 0.0
                perc_ant   = (fat_ant   / meta_ant_op * 100) if meta_ant_op > 0 else 0.0

                def _perc_html(v, cor):
                    bar = min(v, 100)
                    c   = "#10B981" if v >= 100 else cor
                    return (
                        f'<div style="display:flex;align-items:center;gap:5px;">'
                        f'<div style="flex:1;background:#e5e7eb;border-radius:3px;height:6px;">'
                        f'<div style="width:{bar:.0f}%;background:{c};height:6px;border-radius:3px;"></div></div>'
                        f'<span style="white-space:nowrap;font-weight:700;color:{c};font-size:11px;">{v:.1f}%</span></div>'
                    )

                cor_banco_hex = "#7e3d97" if banco == "SEMEAR" else "#10B981"

                # Foto do operador
                imagem_url = operador.get("imagem", "") or ""
                foto_html_ev = (
                    f'<img src="{imagem_url}" style="width:32px;height:32px;border-radius:50%;'
                    f'object-fit:cover;border:2px solid {cor_banco_hex};" />'
                    if imagem_url else "👤"
                )

                if fat_ant > 0 and meta_ant_op > 0:
                    var_meta_pct = perc_atual - perc_ant
                    cor_vm = "#16a34a" if var_meta_pct >= 0 else "#dc2626"
                    s_vm = "↑" if var_meta_pct >= 0 else "↓"
                    var_meta_str = f'<span style="color:{cor_vm};font-weight:700;">{s_vm} {abs(var_meta_pct):.1f}pp</span>'
                else:
                    var_meta_str = "—"

                linhas.append({
                    "foto":        foto_html_ev,
                    "banco":       f"{cor_banco} {banco}",
                    "operador":    operador.get("login", ""),
                    "fat_atual":   _brl(fat_atual),
                    "fat_ant":     _brl(fat_ant),
                    "var_abs":     var_abs_str,
                    "var_pct":     var_pct_str,
                    "perc_atual":  _perc_html(perc_atual, cor_banco_hex),
                    "perc_ant":    _perc_html(perc_ant,   cor_banco_hex),
                    "var_meta":    var_meta_str,
                    "_var_pct_num": var_pct if var_pct is not None else -9999,
                })

        if not linhas:
            return [], [], ""

        # Ordena por variação % decrescente
        linhas.sort(key=lambda x: x.get("_var_pct_num", -9999), reverse=True)

        colunas = [
            {"name": "Foto",            "id": "foto",       "presentation": "markdown"},
            {"name": "Banco",           "id": "banco"},
            {"name": "Operador",        "id": "operador"},
            {"name": "Fat. Atual",      "id": "fat_atual"},
            {"name": "Fat. Anterior",   "id": "fat_ant"},
            # Dif. Fat.(R$) = diferença absoluta em reais (atual - anterior)
            {"name": "Dif. Fat.(R$)",   "id": "var_abs",    "presentation": "markdown"},
            # Var. Fat.(%) = variação percentual do faturamento vs mês anterior
            {"name": "Var. Fat.(%)",    "id": "var_pct",    "presentation": "markdown"},
            # % Meta Atual = % da meta atingido no mês selecionado
            {"name": "% Meta Atual",    "id": "perc_atual", "presentation": "markdown"},
            # % Meta Ant. = % da meta atingido no mês anterior
            {"name": "% Meta Ant.",     "id": "perc_ant",   "presentation": "markdown"},
            # Dif. Meta(pp) = diferença em pontos percentuais entre % meta atual e anterior
            {"name": "Dif. Meta(pp)",   "id": "var_meta",   "presentation": "markdown"},
        ]


        # Resumo
        acima = sum(1 for x in linhas if x.get("_var_pct_num", -9999) != -9999 and x.get("_var_pct_num", 0) >= 0)
        abaixo = sum(1 for x in linhas if x.get("_var_pct_num", -9999) != -9999 and x.get("_var_pct_num", 0) < 0)
        
        resumo_html = (
            f"📈 {acima} operadores com faturamento acima do período anterior | "
            f"📉 {abaixo} operadores com faturamento abaixo do período anterior."
        )

        from dash import html
        resumo_componente = html.Div(
            resumo_html,
            style={
                "backgroundColor": "#fffbeb", "color": "#b45309", "padding": "10px 14px",
                "borderRadius": "6px", "fontWeight": "600", "fontSize": "13.5px",
                "border": "1px solid #fde68a"
            }
        )

        return linhas, colunas, resumo_componente
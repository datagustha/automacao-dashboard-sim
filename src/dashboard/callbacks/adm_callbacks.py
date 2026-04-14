"""
CALLBACKS DO DASHBOARD ADM
===========================
Gerencia os KPIs e as tabelas de ranking para o perfil ADM.
"""

import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from src.services.db_service import buscar_pagamentos_todos_operadores_por_banco
from src.services.analytics_service import calcular_performance_operador


# ─── helpers de formatação ───────────────────────────────────────────────────
def _brl(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def _num(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except:
        return "0"


def register_callbacks(app):
    """Registra os callbacks do painel ADM."""

    # =========================================================================
    # CALLBACK 1 — KPIs globais + Tabelas de ranking por banco
    # =========================================================================
    @app.callback(
        [
            Output('kpi-fat-semear',           'children'),
            Output('kpi-fat-semear-anterior',  'children'),
            Output('kpi-fat-agoracred',        'children'),
            Output('kpi-fat-agoracred-anterior','children'),
            Output('kpi-total-ops-adm',        'children'),
            Output('kpi-ops-adm-anterior',     'children'),
            Output('kpi-ticket-adm',           'children'),
            Output('tabela-adm-semear',        'data'),
            Output('tabela-adm-semear',        'columns'),
            Output('tabela-adm-agoracred',     'data'),
            Output('tabela-adm-agoracred',     'columns'),
        ],
        [
            Input('intervalo-atualizacao-adm', 'n_intervals'),
            Input('filtro-mes-adm', 'value'),
            Input('filtro-ano-adm', 'value'),
            Input('filtro-atividade-adm', 'value'),
        ]
    )
    def atualizar_dashboard_adm(n, mes, ano, filtro_atividade):
        """Consolida dados de todos os operadores de ambos os bancos."""

        mes_int = int(mes)
        ano_int = int(ano)

        if mes_int == 1:
            mes_ant, ano_ant = 12, ano_int - 1
        else:
            mes_ant, ano_ant = mes_int - 1, ano_int

        # Colunas da tabela é sempre a mesma estrutura
        colunas = [
            {"name": "Foto",          "id": "foto", "presentation": "markdown"},
            {"name": "Login",         "id": "operador"},
            {"name": "Turno",         "id": "turno"},
            {"name": "Faturamento",   "id": "faturamento"},
            {"name": "Feito/Dia",     "id": "feito_dia"},
            {"name": "Meta",          "id": "meta"},
            {"name": "% Meta",        "id": "perc_meta"},
            {"name": "Falta 70%",     "id": "falta_70"},
            {"name": "Falta 80%",     "id": "falta_80"},
            {"name": "Falta 90%",     "id": "falta_90"},
            {"name": "Ranking",       "id": "ranking"},
            {"name": "Projeção (R$)", "id": "projecao"},
            {"name": "Proj. %",       "id": "proj_perc"},
        ]

        # ── Processa um banco ──────────────────────────────────────────────
        def processar_banco(banco: str):
            dados = buscar_pagamentos_todos_operadores_por_banco(banco)
            if not dados:
                return 0.0, 0.0, 0, 0, 0.0, []

            fat_atual    = 0.0
            fat_anterior = 0.0
            ops_atual    = 0
            ops_anterior = 0
            soma_tickets = 0.0
            linhas_tabela = []

            for operador, pagamentos, metas in dados:
                # Filtra por atividade se selecionado
                if filtro_atividade == "ATIVO":
                    if str(operador.get('atividade', '')).strip().upper() != "ATIVO":
                        continue

                # Pula operadores sem nenhum pagamento
                if not pagamentos:
                    continue

                try:
                    df = pd.DataFrame(pagamentos)
                except Exception as e:
                    print(f"[ERRO] DataFrame {operador.get('login')}: {e}")
                    continue

                # Garante colunas mínimas necessárias
                if 'dtPgto' not in df.columns:
                    print(f"[AVISO] Sem coluna dtPgto para {operador.get('login')}")
                    continue
                if 'valorTotal' not in df.columns:
                    print(f"[AVISO] Sem coluna valorTotal para {operador.get('login')}")
                    continue

                df['dtPgto']     = pd.to_datetime(df['dtPgto'],    errors='coerce')
                df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0.0)
                df = df.dropna(subset=['dtPgto'])

                if df.empty:
                    continue

                # Semear exclui "Fora da fase"
                if banco == 'SEMEAR' and 'faseAtraso' in df.columns:
                    df = df[df['faseAtraso'] != 'Fora da fase']

                df_atual = df[
                    (df['dtPgto'].dt.month == mes_int) &
                    (df['dtPgto'].dt.year  == ano_int)
                ]
                df_ant = df[
                    (df['dtPgto'].dt.month == mes_ant) &
                    (df['dtPgto'].dt.year  == ano_ant)
                ]

                fat   = float(df_atual['valorTotal'].sum()) if not df_atual.empty else 0.0
                fat_a = float(df_ant['valorTotal'].sum())   if not df_ant.empty  else 0.0
                ops   = len(df_atual)
                ops_a = len(df_ant)

                fat_atual    += fat
                fat_anterior += fat_a
                ops_atual    += ops
                ops_anterior += ops_a
                soma_tickets += fat

                # Calcula performance (passa lista completa; a função filtra por mês)
                try:
                    perf = calcular_performance_operador(
                        pagamentos=pagamentos,
                        metas=metas or [],
                        ano=ano_int,
                        mes=mes_int,
                        login=operador.get('login'),
                        banco=banco
                    )
                except Exception as e:
                    print(f"[ERRO] Performance {operador.get('login')}: {e}")
                    continue

                foto_url = operador.get('imagem', '')
                foto_md = f"<img src='{foto_url}' style='width: 30px; height: 30px; border-radius: 50%; object-fit: cover;'/>" if foto_url else "👤"

                linhas_tabela.append({
                    "foto":      foto_md,
                    "operador":  operador.get('login', ''),
                    "turno":     operador.get('turno', ''),
                    "faturamento": _brl(perf.get('faturamento', 0)),
                    "feito_dia":   _brl(perf.get('feito_diario', 0)),
                    "meta":        _brl(perf.get('meta', 0)),
                    "perc_meta":   f"{perf.get('atingido_meta', 0):.1f}%",
                    "falta_70":    _brl(perf.get('falta_70', 0)),
                    "falta_80":    _brl(perf.get('falta_80', 0)),
                    "falta_90":    _brl(perf.get('falta_90', 0)),
                    "ranking":     _brl(perf.get('meta_ranking', 0)),
                    "projecao":    _brl(perf.get('projecao', 0)),
                    "proj_perc":   f"{perf.get('projecao_percentual', 0):.1f}%",
                })

            # Ordena por faturamento (maior primeiro)
            def _parse_brl(s):
                try:
                    return float(s.replace("R$ ", "").replace(".", "").replace(",", "."))
                except:
                    return 0.0

            linhas_tabela.sort(key=lambda x: _parse_brl(x.get('faturamento', '0')), reverse=True)

            return fat_atual, fat_anterior, ops_atual, ops_anterior, soma_tickets, linhas_tabela

        # ── Executa para os dois bancos ────────────────────────────────────
        fat_s, fat_s_ant, ops_s, ops_s_ant, tickets_s, dados_s = processar_banco('SEMEAR')
        fat_a, fat_a_ant, ops_a, ops_a_ant, tickets_a, dados_a = processar_banco('AGORACRED')

        # ── KPIs globais ───────────────────────────────────────────────────
        ops_total     = ops_s + ops_a
        ops_ant_total = ops_s_ant + ops_a_ant
        tickets_total = tickets_s + tickets_a
        ticket_medio  = tickets_total / ops_total if ops_total > 0 else 0.0

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
        )

    # =========================================================================
    # CALLBACK 2 — Popula dropdown de operadores no Detalhe ADM
    # =========================================================================
    @app.callback(
        Output('adm-operador-select', 'options'),
        [
            Input('adm-banco-select', 'value'),
            Input('adm-filtro-atividade', 'value')
        ]
    )
    def carregar_operadores_banco(banco, atividade):
        """Carrega os operadores do banco selecionado no dropdown, filtrando por atividade."""
        from src.services.db_service import buscar_todos_operadores_por_banco
        if not banco:
            return []
        
        operadores = buscar_todos_operadores_por_banco(banco)
        
        if atividade == "ativo":
            operadores = [op for op in operadores if op.get('atividade') == 'ativo']
            
        opcoes = [{"label": "🌟 Todos os Operadores (Consolidado)", "value": "TODOS"}]
        opcoes.extend(
            [{"label": f"{op['nome']} ({op['login']})", "value": op['login']} for op in operadores]
        )
        return opcoes

    # =========================================================================
    # CALLBACK 3 — Navega automaticamente ao alterar banco ou operador
    # =========================================================================
    @app.callback(
        Output('adm-redirect-detalhe', 'pathname'),
        [
            Input('adm-banco-select', 'value'),
            Input('adm-operador-select', 'value')
        ],
        prevent_initial_call=True
    )
    def navegar_para_operador(banco, login_operador):
        """Ao alterar o seletor, atualiza a url para /operadores/BANCO/LOGIN."""
        if not banco or not login_operador:
            raise PreventUpdate
        return f"/operadores/{banco}/{login_operador}"

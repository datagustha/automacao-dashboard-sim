"""
CALLBACKS DO DASHBOARD ADM
===========================
Gerencia os KPIs e as tabelas de ranking para o perfil ADM.
CORRIGIDO: Agora permite filtrar por operador específico no dashboard
NOVO: Gráficos separados SEMEAR e AGORACRED + Tabela de evolução diária
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from src.services.db_service import buscar_pagamentos_todos_operadores_por_banco, buscar_todos_operadores_por_banco
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


# =========================================================================
# FUNÇÃO AUXILIAR PARA CRIAR GRÁFICO POR BANCO (DEFINIDA FORA DOS CALLBACKS)
# =========================================================================
def criar_grafico_por_banco(banco, mes, ano, filtro_atividade, operador_filtro, cor, nome_banco):
    """Cria gráfico de evolução diária para um banco específico"""
    
    mes_int = int(mes) if mes else pd.Timestamp.now().month
    ano_int = int(ano) if ano else pd.Timestamp.now().year
    
    dados = buscar_pagamentos_todos_operadores_por_banco(banco)
    if not dados:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=f"<b>Sem dados para {nome_banco}</b>", x=0.5),
            height=350,
            plot_bgcolor='white'
        )
        return fig
    
    todos_pagamentos = []
    
    for operador, pagamentos, _ in dados:
        if operador_filtro and operador_filtro != "TODOS":
            if operador.get('login') != operador_filtro:
                continue
        
        if filtro_atividade == "ATIVO":
            if str(operador.get('atividade', '')).strip().upper() != "ATIVO":
                continue
        
        if pagamentos:
            todos_pagamentos.extend(pagamentos)
    
    if not todos_pagamentos:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=f"<b>Sem dados para {nome_banco}</b>", x=0.5),
            height=350,
            plot_bgcolor='white'
        )
        return fig
    
    df = pd.DataFrame(todos_pagamentos)
    if 'dtPgto' not in df.columns or 'valorTotal' not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=f"<b>Erro: colunas necessárias não encontradas</b>", x=0.5),
            height=350,
            plot_bgcolor='white'
        )
        return fig
    
    df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
    df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0.0)
    df = df.dropna(subset=['dtPgto'])
    
    df = df[
        (df['dtPgto'].dt.month == mes_int) &
        (df['dtPgto'].dt.year == ano_int)
    ]
    
    if banco == 'SEMEAR' and 'faseAtraso' in df.columns:
        df = df[df['faseAtraso'] != 'Fora da fase']
    
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=f"<b>Sem dados para {nome_banco} no período</b>", x=0.5),
            height=350,
            plot_bgcolor='white'
        )
        return fig
    
    df['dia'] = df['dtPgto'].dt.day
    df_dia = df.groupby('dia')['valorTotal'].sum().reset_index()
    
    dias = sorted(df_dia['dia'].tolist())
    valores = df_dia['valorTotal'].tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dias,
        y=valores,
        mode='lines+markers',
        name=nome_banco,
        line=dict(color=cor, width=3),
        marker=dict(size=8, color=cor),
        hovertemplate='Dia %{x}<br>R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>Evolução Diária - {mes_int}/{ano_int}</b>",
            font=dict(color='#111827', size=14),
            x=0,
            xanchor='left'
        ),
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title="Dia do Mês",
            tickmode='linear',
            tick0=1,
            dtick=1,
            showgrid=True,
            gridcolor='#E5E7EB'
        ),
        yaxis=dict(
            title="Recebimento (R$)",
            showgrid=True,
            gridcolor='#E5E7EB'
        ),
        margin=dict(l=60, r=40, t=60, b=40)
    )
    
    return fig


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
            Input('url', 'pathname'),
            Input('filtro-mes-adm', 'value'),
            Input('filtro-ano-adm', 'value'),
            Input('filtro-atividade-adm', 'value'),
            Input('filtro-operador-adm', 'value'),
        ],
        [State('login-success-store', 'data')]
    )
    def atualizar_dashboard_adm(n, pathname, mes, ano, filtro_atividade, operador_filtro, dados_operador):
        """Consolida dados de todos os operadores de ambos os bancos, com filtro opcional por operador."""
        
        if pathname != '/dashboard' or not dados_operador:
            return [dash.no_update] * 11
            
        perfil = dados_operador.get('perfil', 'operador')
        if perfil != 'adm':
            return [dash.no_update] * 11

        mes_int = int(mes) if mes else pd.Timestamp.now().month
        ano_int = int(ano) if ano else pd.Timestamp.now().year

        if mes_int == 1:
            mes_ant, ano_ant = 12, ano_int - 1
        else:
            mes_ant, ano_ant = mes_int - 1, ano_int

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

        def processar_banco(banco: str, operador_especifico=None):
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
                if operador_especifico and operador_especifico != "TODOS":
                    if operador.get('login') != operador_especifico:
                        continue
                
                if filtro_atividade == "ATIVO":
                    if str(operador.get('atividade', '')).strip().upper() != "ATIVO":
                        continue

                if not pagamentos:
                    continue

                try:
                    df = pd.DataFrame(pagamentos)
                except Exception as e:
                    print(f"[ERRO] DataFrame {operador.get('login')}: {e}")
                    continue

                if 'dtPgto' not in df.columns or 'valorTotal' not in df.columns:
                    continue

                df['dtPgto']     = pd.to_datetime(df['dtPgto'], errors='coerce')
                df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0.0)
                df = df.dropna(subset=['dtPgto'])

                if df.empty:
                    continue

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
                fat_a = float(df_ant['valorTotal'].sum())   if not df_ant.empty else 0.0
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

            def _parse_brl(s):
                try:
                    return float(s.replace("R$ ", "").replace(".", "").replace(",", "."))
                except:
                    return 0.0

            linhas_tabela.sort(key=lambda x: _parse_brl(x.get('faturamento', '0')), reverse=True)

            return fat_atual, fat_anterior, ops_atual, ops_anterior, soma_tickets, linhas_tabela

        fat_s, fat_s_ant, ops_s, ops_s_ant, tickets_s, dados_s = processar_banco('SEMEAR', operador_filtro)
        fat_a, fat_a_ant, ops_a, ops_a_ant, tickets_a, dados_a = processar_banco('AGORACRED', operador_filtro)

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
    # CALLBACK 2 — GRÁFICO DE EVOLUÇÃO DIÁRIA SEMEAR
    # =========================================================================
    @app.callback(
        Output('grafico-evolucao-semear-adm', 'figure'),
        [
            Input('filtro-mes-adm', 'value'),
            Input('filtro-ano-adm', 'value'),
            Input('filtro-atividade-adm', 'value'),
            Input('filtro-operador-adm', 'value'),
            Input('intervalo-atualizacao-adm', 'n_intervals'),
        ]
    )
    def atualizar_grafico_evolucao_semear(mes, ano, filtro_atividade, operador_filtro, n):
        """Gráfico de evolução diária - SEMEAR"""
        return criar_grafico_por_banco('SEMEAR', mes, ano, filtro_atividade, operador_filtro, '#7e3d97', 'SEMEAR')

    # =========================================================================
    # CALLBACK 3 — GRÁFICO DE EVOLUÇÃO DIÁRIA AGORACRED
    # =========================================================================
    @app.callback(
        Output('grafico-evolucao-agoracred-adm', 'figure'),
        [
            Input('filtro-mes-adm', 'value'),
            Input('filtro-ano-adm', 'value'),
            Input('filtro-atividade-adm', 'value'),
            Input('filtro-operador-adm', 'value'),
            Input('intervalo-atualizacao-adm', 'n_intervals'),
        ]
    )
    def atualizar_grafico_evolucao_agoracred(mes, ano, filtro_atividade, operador_filtro, n):
        """Gráfico de evolução diária - AGORACRED"""
        return criar_grafico_por_banco('AGORACRED', mes, ano, filtro_atividade, operador_filtro, '#10B981', 'AGORACRED')

    # =========================================================================
    # CALLBACK 4 — TABELA DE VALORES DIÁRIOS CONSOLIDADA
    # =========================================================================
    @app.callback(
        [
            Output('tabela-evolucao-diaria-adm', 'data'),
            Output('tabela-evolucao-diaria-adm', 'columns'),
        ],
        [
            Input('filtro-mes-adm', 'value'),
            Input('filtro-ano-adm', 'value'),
            Input('filtro-atividade-adm', 'value'),
            Input('filtro-operador-adm', 'value'),
            Input('intervalo-atualizacao-adm', 'n_intervals'),
        ]
    )
    def atualizar_tabela_evolucao_adm(mes, ano, filtro_atividade, operador_filtro, n):
        """Tabela de valores diários: Dia | SEMEAR | AGORACRED | TOTAL"""
        
        mes_int = int(mes) if mes else pd.Timestamp.now().month
        ano_int = int(ano) if ano else pd.Timestamp.now().year
        
        def buscar_dados_por_banco(banco):
            dados = buscar_pagamentos_todos_operadores_por_banco(banco)
            if not dados:
                return {}
            
            todos_pagamentos = []
            for operador, pagamentos, _ in dados:
                if operador_filtro and operador_filtro != "TODOS":
                    if operador.get('login') != operador_filtro:
                        continue
                
                if filtro_atividade == "ATIVO":
                    if str(operador.get('atividade', '')).strip().upper() != "ATIVO":
                        continue
                
                if pagamentos:
                    todos_pagamentos.extend(pagamentos)
            
            if not todos_pagamentos:
                return {}
            
            df = pd.DataFrame(todos_pagamentos)
            if 'dtPgto' not in df.columns or 'valorTotal' not in df.columns:
                return {}
            
            df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
            df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0.0)
            df = df.dropna(subset=['dtPgto'])
            
            df = df[
                (df['dtPgto'].dt.month == mes_int) &
                (df['dtPgto'].dt.year == ano_int)
            ]
            
            if banco == 'SEMEAR' and 'faseAtraso' in df.columns:
                df = df[df['faseAtraso'] != 'Fora da fase']
            
            if df.empty:
                return {}
            
            df['dia'] = df['dtPgto'].dt.day
            df_dia = df.groupby('dia')['valorTotal'].sum().reset_index()
            return dict(zip(df_dia['dia'], df_dia['valorTotal']))
        
        semear_dict = buscar_dados_por_banco('SEMEAR')
        agoracred_dict = buscar_dados_por_banco('AGORACRED')
        
        todos_dias = sorted(set(list(semear_dict.keys()) + list(agoracred_dict.keys())))
        
        if not todos_dias:
            return [], []
        
        dados_tabela = []
        for dia in todos_dias:
            semear_valor = semear_dict.get(dia, 0)
            agoracred_valor = agoracred_dict.get(dia, 0)
            total_valor = semear_valor + agoracred_valor
            
            dados_tabela.append({
                'dia': dia,
                'semear': f"R$ {semear_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'agoracred': f"R$ {agoracred_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'total': f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            })
        
        total_semear = sum(semear_dict.values())
        total_agoracred = sum(agoracred_dict.values())
        total_geral = total_semear + total_agoracred
        
        dados_tabela.append({
            'dia': '📊 TOTAL DO PERÍODO',
            'semear': f"R$ {total_semear:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            'agoracred': f"R$ {total_agoracred:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            'total': f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        })
        
        colunas = [
            {"name": "📅 Dia", "id": "dia"},
            {"name": "🟣 SEMEAR (R$)", "id": "semear"},
            {"name": "🟢 AGORACRED (R$)", "id": "agoracred"},
            {"name": "⚫ TOTAL (R$)", "id": "total"}
        ]
        
        return dados_tabela, colunas

    # =========================================================================
    # CALLBACK 5 — Popula dropdown de operadores no Dashboard ADM
    # =========================================================================
    @app.callback(
        Output('filtro-operador-adm', 'options'),
        [
            Input('filtro-mes-adm', 'value'),
            Input('filtro-ano-adm', 'value'),
        ]
    )
    def carregar_operadores_dashboard(mes, ano):
        """Carrega TODOS os operadores para o filtro do dashboard ADM"""
        
        # Busca operadores de ambos os bancos usando a mesma função que funciona na página de operadores
        todos_operadores = []
        
        # Busca operadores SEMEAR
        try:
            operadores_semear = buscar_todos_operadores_por_banco('SEMEAR')
            if operadores_semear:
                todos_operadores.extend(operadores_semear)
        except Exception as e:
            print(f"[ERRO] ao buscar operadores SEMEAR: {e}")
        
        # Busca operadores AGORACRED
        try:
            operadores_agoracred = buscar_todos_operadores_por_banco('AGORACRED')
            if operadores_agoracred:
                todos_operadores.extend(operadores_agoracred)
        except Exception as e:
            print(f"[ERRO] ao buscar operadores AGORACRED: {e}")
        
        if not todos_operadores:
            return [{"label": "📊 Todos os Operadores", "value": "TODOS"}]
        
        # Remove duplicatas por login
        logins_vistos = set()
        operadores_unicos = []
        for op in todos_operadores:
            login = op.get('login')
            if login and login not in logins_vistos:
                logins_vistos.add(login)
                operadores_unicos.append(op)
        
        # Ordena por nome
        operadores_unicos.sort(key=lambda x: x.get('nome', x.get('login', '')))
        
        opcoes = [{"label": "📊 Todos os Operadores", "value": "TODOS"}]
        for op in operadores_unicos:
            login = op.get('login')
            nome = op.get('nome', login)
            if login:
                opcoes.append({"label": f"{nome} ({login})", "value": login})
        
        print(f"[DEBUG] Total de operadores carregados: {len(opcoes)-1}")
        return opcoes

    # =========================================================================
    # CALLBACK 6 — Popula dropdown de operadores no Detalhe ADM
    # =========================================================================
    @app.callback(
        Output('adm-operador-select', 'options'),
        [
            Input('adm-banco-select', 'value'),
            Input('adm-filtro-atividade', 'value')
        ]
    )
    def carregar_operadores_banco(banco, atividade):
        if not banco:
            return []
        
        operadores = buscar_todos_operadores_por_banco(banco)
        
        if atividade == "ativo":
            operadores = [op for op in operadores if op.get('atividade') == 'ativo']
            
        opcoes = [{"label": "🌟 Todos os Operadores (Consolidado)", "value": "TODOS"}]
        opcoes.extend(
            [{"label": f"{op['nome']} ({op['login']})", "value": op['login']} for op in operadores if op.get('login')]
        )
        return opcoes

    # =========================================================================
    # CALLBACK 7 — Navega automaticamente ao alterar banco ou operador
    # =========================================================================
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        [
            Input('adm-banco-select', 'value'),
            Input('adm-operador-select', 'value')
        ],
        [State('url', 'pathname')],
        prevent_initial_call=True
    )
    def navegar_para_operador(banco, login_operador, current_pathname):
        if not banco or not login_operador or login_operador == "TODOS":
            raise PreventUpdate
        
        nova_url = f"/operadores/{banco}/{login_operador}"
        
        if current_pathname == nova_url:
            raise PreventUpdate
            
        return nova_url
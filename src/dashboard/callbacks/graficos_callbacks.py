"""
CALLBACKS DOS GRÁFICOS E TABELAS - DASHBOARD
=============================================

ARQUIVO: graficos_callbacks.py
LOCAL: src/dashboard/callbacks/
"""

import plotly.graph_objects as go
import pandas as pd
import datetime
import os
import re
from dash.dependencies import Input, Output, State

from src.services.db_service import (
    Buscar_login, 
    Buscar_pagamento_por_operador, 
    buscar_metas_por_operador
)
from src.services.analytics_service import (
    calcular_indicadores_operador, 
    calcular_faturamento_por_dia, 
    calcular_pagamentos_por_fase,
    calcular_performance_operador  # ← NOVO!
)


# ================================================================
# CONFIGURAÇÃO DE LOG PARA DEBUG
# ================================================================
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dashboard_debug.log")

def log_debug(mensagem):
    """Função auxiliar para escrever mensagens de debug em um arquivo."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")
    print(mensagem)


def register_callbacks(app):
    """Função principal que registra todos os callbacks do dashboard."""
    
    @app.callback(
        [
            Output('kpi-faturamento', 'children'),
            Output('kpi-ticket', 'children'),
            Output('kpi-total-pgtos', 'children'),
            Output('grafico-faturamento', 'figure'),
            Output('tabela-pagamentos', 'data'),
            Output('tabela-pagamentos', 'columns'),
            Output('kpi-mes-anterior', 'children'),
            Output('grafico-fase', 'figure'),
            Output('kpi-meta-objetivo', 'children'),
            Output('kpi-meta-barra', 'style'),
            Output('kpi-meta-percentual', 'children')
        ],
        [
            Input('intervalo-atualizacao', 'n_intervals'),
            Input('url', 'pathname'),
            Input('filtro-mes', 'value'),
            Input('filtro-ano', 'value'),
            Input('filtro-texto-busca', 'value'),
            Input('filtro-fase', 'value')
        ],
        [State('login-success-store', 'data')]
    )
    def atualizar_dashboard(n_intervals, pathname, mes, ano, texto_busca, fase, dados_operador):
        """Função principal que atualiza todo o dashboard."""
        
        log_debug("=" * 60)
        log_debug("CALLBACK EXECUTADO")
        log_debug(f"MES: {mes}, ANO: {ano}, FASE: {fase}, BUSCA: {texto_busca}")
        
        # ================================================================
        # FIGURA VAZIA (usada quando não há dados)
        # ================================================================
        fig_blank = go.Figure().update_layout(
            title="", 
            plot_bgcolor='white', 
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        texto_zero = "R$ 0,00"
        
        # ================================================================
        # VERIFICAÇÃO DE SEGURANÇA
        # ================================================================
        if pathname != '/dashboard' or not dados_operador:
            log_debug("FORA DO DASHBOARD OU SEM OPERADOR")
            return texto_zero, texto_zero, "0", fig_blank, [], [], "", fig_blank, texto_zero, {"width": "0%"}, "0%"
        
        login = dados_operador.get('login')
        if not login:
            log_debug("SEM LOGIN")
            return texto_zero, texto_zero, "0", fig_blank, [], [], "", fig_blank, texto_zero, {"width": "0%"}, "0%"
        
        # ================================================================
        # BUSCA OS DADOS DO BANCO
        # ================================================================
        operador = Buscar_login(login)
        if not operador:
            log_debug("OPERADOR NAO ENCONTRADO")
            return texto_zero, texto_zero, "0", fig_blank, [], [], "", fig_blank, texto_zero, {"width": "0%"}, "0%"
        
        # Usa a função genérica para buscar pagamentos
        pagamentos_brutos = Buscar_pagamento_por_operador(operador)
        
        if not pagamentos_brutos:
            log_debug("NENHUM PAGAMENTO ENCONTRADO")
            return texto_zero, texto_zero, "0", fig_blank, [], [], "", fig_blank, texto_zero, {"width": "0%"}, "0%"

        log_debug(f"Total de pagamentos: {len(pagamentos_brutos)}")
        
        # ================================================================
        # CONVERTE PARA DATAFRAME
        # ================================================================
        df = pd.DataFrame(pagamentos_brutos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        # ================================================================
        # FILTROS DE MÊS E ANO
        # ================================================================
        mes = int(mes)
        ano = int(ano)
        
        if mes == 1:
            mes_anterior = 12
            ano_anterior = ano - 1
        else:
            mes_anterior = mes - 1
            ano_anterior = ano
        
        df_mes_atual = df[
            (df['dtPgto'].dt.month == mes) & 
            (df['dtPgto'].dt.year == ano)
        ].copy()
        
        df_mes_anterior = df[
            (df['dtPgto'].dt.month == mes_anterior) & 
            (df['dtPgto'].dt.year == ano_anterior)
        ].copy()
        
        log_debug(f"Registros no mês atual: {len(df_mes_atual)}")
        
        # ================================================================
        # FILTRO DE FASE (apenas para SEMEAR)
        # ================================================================
        if fase and "todas" not in str(fase).lower() and operador.get('banco') == 'SEMEAR':
            log_debug(f"Aplicando filtro de fase: '{fase}'")
            
            if 'faseAtraso' in df_mes_atual.columns:
                def normalizar(texto):
                    if texto is None or pd.isna(texto):
                        return ""
                    return str(texto).strip().upper()
                
                df_mes_atual['_fase_norm'] = df_mes_atual['faseAtraso'].apply(normalizar)
                
                if isinstance(fase, list):
                    fase_norm = [normalizar(f) for f in fase]
                    df_mes_atual = df_mes_atual[df_mes_atual['_fase_norm'].isin(fase_norm)]
                else:
                    fase_norm = normalizar(fase)
                    df_mes_atual = df_mes_atual[df_mes_atual['_fase_norm'] == fase_norm]
                
                df_mes_atual = df_mes_atual.drop(columns=['_fase_norm'])
                log_debug(f"Registros após filtro de fase: {len(df_mes_atual)}")
        
        # ================================================================
        # FILTRO DE TEXTO (Busca por Contrato ou Cliente)
        # ================================================================
        if texto_busca:
            log_debug(f"Aplicando filtro de texto: '{texto_busca}'")
            texto = str(texto_busca).lower()
            contains_contrato = df_mes_atual['contrato'].fillna('').astype(str).str.lower().str.contains(texto)
            contains_cliente = df_mes_atual.get('cliente', pd.Series(dtype=str)).fillna('').astype(str).str.lower().str.contains(texto)
            df_mes_atual = df_mes_atual[contains_contrato | contains_cliente]
            log_debug(f"Registros após filtro de texto: {len(df_mes_atual)}")
        
        # ================================================================
        # CÁLCULO DO MÊS ANTERIOR
        # ================================================================
        fat_anterior = df_mes_anterior['valorTotal'].sum() if not df_mes_anterior.empty else 0.0
        txt_fat_anterior = f"Mês anterior: R$ {fat_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # ================================================================
        # VERIFICA SE TEM DADOS NO MÊS ATUAL
        # ================================================================
        if df_mes_atual.empty:
            log_debug("DataFrame vazio - retornando sem dados")
            return texto_zero, texto_zero, "0", fig_blank, [], [], txt_fat_anterior, fig_blank, texto_zero, {"width": "0%"}, "0%"
        
        # ================================================================
        # CONVERTE PARA LISTA DE DICIONÁRIOS
        # ================================================================
        pagamentos_filtrados = df_mes_atual.to_dict('records')
        
        # ================================================================
        # CALCULA INDICADORES (KPIs)
        # ================================================================
        indicadores = calcular_indicadores_operador(pagamentos_filtrados)
        
        faturamento = indicadores['faturamento_total']
        ticket = indicadores['ticket_medio']
        total = indicadores['total_pagamentos']
        
        txt_faturamento = f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        txt_ticket = f"R$ {ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        txt_total = f"{total:,}".replace(",", ".")

        # ================================================================
        # BUSCA A META DO MÊS
        # ================================================================
        metas = buscar_metas_por_operador(operador)
        meta_valor = 0.0

        if metas:
            for meta in metas:
                if meta['data'].year == ano and meta['data'].month == mes:
                    meta_valor = meta.get('meta100', 0)
                    break

        # Calcula o percentual da meta
        percentual_meta = (faturamento / meta_valor) * 100 if meta_valor > 0 else 0

        # Formata o valor da meta
        txt_meta_objetivo = f"R$ {meta_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # ================================================================
        # DEFINE A COR DA BARRA BASEADA NO PERCENTUAL
        # ================================================================
        if percentual_meta >= 100:
            cor_barra = "#10B981"  # verde (meta atingida)
        elif percentual_meta >= 70:
            cor_barra = "#f59e0b"  # laranja (quase lá)
        else:
            cor_barra = "#ef4444"  # vermelho (abaixo)

        # Estilo da barra
        estilo_barra = {
            "width": f"{min(percentual_meta, 100)}%",
            "backgroundColor": cor_barra,
            "height": "6px",
            "borderRadius": "4px",
            "transition": "width 0.5s"
        }
        
        # ================================================================
        # GRÁFICO 1: EVOLUÇÃO DIÁRIA (LINHA)
        # ================================================================
        from src.dashboard.components.graficos import criar_grafico_linha

        df_grafico = calcular_faturamento_por_dia(pagamentos_filtrados)
        figura = criar_grafico_linha(
            df=df_grafico,
            x='data',
            y='total',
            titulo="Evolução Diária - Faturamento no Período",
            cor='#7e3d97'
        )
        if df_grafico.empty:
            figura = fig_blank

        # ================================================================
        # GRÁFICO 2: PAGAMENTOS POR FASE (BARRAS) - APENAS PARA SEMEAR
        # ================================================================
        if operador.get('banco') == 'SEMEAR':
            df_fases = calcular_pagamentos_por_fase(pagamentos_filtrados)
            if not df_fases.empty:
                import plotly.express as px
                figura_fase = px.bar(
                    df_fases, 
                    x='fase', 
                    y='total',
                    text='total'
                )
                figura_fase.update_traces(
                    marker_color='#7e3d97',
                    marker_line_color='#612d75',
                    marker_line_width=1,
                    texttemplate='R$ %{y:,.0f}',
                    textposition='outside'
                )
                figura_fase.update_layout(
                    title=dict(
                        text="Pagamentos por Fase",
                        font=dict(color='#111827', size=14, weight='bold'),
                        x=0,
                        xanchor='left'
                    ),
                    height=350,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis_title="Fase",
                    yaxis_title="Valor (R$)",
                    font=dict(color='#111827'),
                    uniformtext_minsize=8,
                    uniformtext_mode='hide'
                )
            else:
                figura_fase = fig_blank
        else:
            # Para AGORACRED, mostra um gráfico de evolução mensal
            df_mensal = df_mes_atual.groupby(df_mes_atual['dtPgto'].dt.strftime('%Y-%m'))['valorTotal'].sum().reset_index()
            df_mensal.columns = ['mes', 'total']
            if not df_mensal.empty:
                import plotly.express as px
                figura_fase = px.line(
                    df_mensal, 
                    x='mes', 
                    y='total',
                    title="Evolução Mensal do Faturamento",
                    markers=True
                )
                figura_fase.update_layout(
                    title=dict(
                        text="Evolução Mensal do Faturamento",
                        font=dict(color='#111827', size=14, weight='bold'),
                        x=0,
                        xanchor='left'
                    ),
                    height=350,
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
            else:
                figura_fase = fig_blank

        # ================================================================
        # TABELA DE PAGAMENTOS RECENTES
        # ================================================================
        colunas_visiveis = ['dtPgto', 'contrato', 'cliente', 'valorTotal', 'faseAtraso']
        
        if 'faseAtraso' not in df_mes_atual.columns and 'fase' in df_mes_atual.columns:
            colunas_visiveis = ['dtPgto', 'contrato', 'cliente', 'valorTotal', 'fase']
        
        df_tabela = df_mes_atual[colunas_visiveis].copy()
        df_tabela = df_tabela.sort_values(by='dtPgto', ascending=False)
        df_tabela['dtPgto'] = df_tabela['dtPgto'].dt.strftime('%d/%m/%Y')
        df_tabela['valorTotal'] = df_tabela['valorTotal'].map(
            lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        rename_dict = {
            'dtPgto': 'Data',
            'contrato': 'Contrato',
            'cliente': 'Cliente',
            'valorTotal': 'Valor',
            'faseAtraso': 'Fase',
            'fase': 'Fase'
        }
        df_tabela = df_tabela.rename(columns=rename_dict)
        
        dados_tabela = df_tabela.to_dict('records')
        colunas_tabela = [{"name": i, "id": i} for i in df_tabela.columns]
        
        log_debug(f"FIM - Total final: {total} pagamentos")
        log_debug("=" * 60)
        
        # ================================================================
        # RETORNO
        # ================================================================
        return (
            txt_faturamento,
            txt_ticket,
            txt_total,
            figura,
            dados_tabela,
            colunas_tabela,
            txt_fat_anterior,
            figura_fase,
            txt_meta_objetivo,
            estilo_barra,
            f"{percentual_meta:.1f}% da meta"
        )


    # ================================================================
    # TABELA DE PERFORMANCE DO OPERADOR
    # ================================================================
    @app.callback(
        [
            Output('tabela-performance', 'data'),
            Output('tabela-performance', 'columns')
        ],
        [
            Input('intervalo-atualizacao', 'n_intervals'),
            Input('filtro-mes', 'value'),
            Input('filtro-ano', 'value')
        ],
        [State('login-success-store', 'data')]
    )
    def atualizar_tabela_performance(n, mes, ano, dados_operador):
        """
        ATUALIZA A TABELA DE PERFORMANCE DO OPERADOR LOGADO.
        
        Mostra:
        - Login, Turno
        - Faturamento, Feito Diário
        - Meta, Meta Diária, % Meta
        - Faltas para 70%, 80%, 90%, 100%
        - Meta Ranking, Projeção (R$ e %)
        - Dias trabalhados e restantes
        """
        
        # VERIFICA SE USUÁRIO ESTÁ LOGADO
        if not dados_operador:
            return [], []
        
        login = dados_operador.get('login')
        if not login:
            return [], []
        
        # BUSCA DADOS DO OPERADOR
        operador = Buscar_login(login)
        if not operador:
            return [], []
        
        # BUSCA PAGAMENTOS E METAS
        pagamentos = Buscar_pagamento_por_operador(operador)
        metas = buscar_metas_por_operador(operador)
        
        if not pagamentos:
            # Retorna tabela vazia com mensagem
            return [], [{"name": "Sem dados", "id": "sem_dados"}]
        
        # CALCULA PERFORMANCE
        perf = calcular_performance_operador(
            pagamentos=pagamentos,
            metas=metas,
            ano=ano,
            mes=mes,
            login=login
        )
        
        # PREPARA DADOS PARA A TABELA
        dados_tabela = [{
            "login": perf['login'],
            "turno": operador.get('turno', ''),
            "faturamento": f"R$ {perf['faturamento']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "feito_diario": f"R$ {perf['feito_diario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "meta": f"R$ {perf['meta']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "meta_diaria": f"R$ {perf['meta_diaria']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "atingido_meta": f"{perf['atingido_meta']:.1f}%",
            "falta_70": f"R$ {perf['falta_70']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "falta_80": f"R$ {perf['falta_80']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "falta_90": f"R$ {perf['falta_90']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "falta_100": f"R$ {perf['falta_100']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "meta_ranking": f"R$ {perf['meta_ranking']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "projecao": f"R$ {perf['projecao']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "projecao_percentual": f"{perf['projecao_percentual']:.1f}%",
            "dias_trabalhados": perf['dias_trabalhados'],
            "dias_restantes": perf['dias_restantes']
        }]
        
        # DEFINE AS COLUNAS DA TABELA
        colunas = [
            {"name": "Login", "id": "login"},
            {"name": "Turno", "id": "turno"},
            {"name": "Faturamento", "id": "faturamento"},
            {"name": "Feito Diário", "id": "feito_diario"},
            {"name": "Meta", "id": "meta"},
            {"name": "Meta Diária", "id": "meta_diaria"},
            {"name": "% Meta", "id": "atingido_meta"},
            {"name": "Falta 70%", "id": "falta_70"},
            {"name": "Falta 80%", "id": "falta_80"},
            {"name": "Falta 90%", "id": "falta_90"},
            {"name": "Falta 100%", "id": "falta_100"},
            {"name": "Meta Ranking", "id": "meta_ranking"},
            {"name": "Projeção (R$)", "id": "projecao"},
            {"name": "Projeção %", "id": "projecao_percentual"},
            {"name": "Dias Trab.", "id": "dias_trabalhados"},
            {"name": "Dias Rest.", "id": "dias_restantes"}
        ]
        
        return dados_tabela, colunas
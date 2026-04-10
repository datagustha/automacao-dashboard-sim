"""
CALLBACKS DA TELA DE DETALHE DO OPERADOR
=========================================
Gerencia as tabelas e gráficos do operador.
"""

from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime

from src.services.db_service import Buscar_login, Buscar_pagamento_por_operador, buscar_metas_por_operador
from src.services.analytics_service import calcular_performance_operador


def register_callbacks(app):
    """Registra os callbacks da tela de detalhe do operador."""
    
    # ================================================================
    # FUNÇÃO AUXILIAR: DIAS ÚTEIS DO MÊS
    # ================================================================
    def get_dias_uteis(ano, mes):
        """Retorna lista de dias úteis (segunda a sexta) do mês."""
        dias_uteis = []
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        for dia in range(1, ultimo_dia + 1):
            data = datetime(ano, mes, dia)
            if data.weekday() < 5:
                dias_uteis.append(dia)
        return dias_uteis
    
    # ================================================================
    # TABELA DIA A DIA
    # ================================================================
    @app.callback(
        [
            Output('tabela-dia-dia', 'data'),
            Output('tabela-dia-dia', 'columns')
        ],
        [
            Input('intervalo-operador', 'n_intervals'),
            Input('filtro-mes-operador', 'value'),
            Input('filtro-ano-operador', 'value')
        ],
        [State('operador-selecionado-store', 'data')]
    )
    def atualizar_tabela_dia_dia(n, mes, ano, operador_selecionado):
        """Atualiza a tabela Dia a Dia."""
        
        if not operador_selecionado:
            return [], []
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        if not pagamentos:
            return [], []
        
        df = pd.DataFrame(pagamentos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        df_mes = df[(df['dtPgto'].dt.month == mes) & (df['dtPgto'].dt.year == ano)]
        
        if df_mes.empty:
            return [], []
        
        ultima_data = df_mes['dtPgto'].max()
        df_mes = df_mes[df_mes['dtPgto'] <= ultima_data]
        
        df_mes['dia'] = df_mes['dtPgto'].dt.day
        df_dia = df_mes.groupby('dia').agg(
            quantidade=('valorTotal', 'count'),
            faturamento=('valorTotal', 'sum')
        ).reset_index()
        df_dia = df_dia.sort_values('dia')
        
        total_quantidade = df_dia['quantidade'].sum()
        total_faturamento = df_dia['faturamento'].sum()
        
        dados = []
        for _, row in df_dia.iterrows():
            dados.append({
                'dia': row['dia'],
                'quantidade': row['quantidade'],
                'faturamento': f"R$ {row['faturamento']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            })
        
        dados.append({
            'dia': 'TOTAL',
            'quantidade': total_quantidade,
            'faturamento': f"R$ {total_faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        })
        
        colunas = [
            {"name": "Dia", "id": "dia"},
            {"name": "Quantidade", "id": "quantidade"},
            {"name": "Faturamento", "id": "faturamento"}
        ]
        
        return dados, colunas
    
    # ================================================================
    # TABELA DIA ÚTIL
    # ================================================================
    @app.callback(
        [
            Output('tabela-dia-util', 'data'),
            Output('tabela-dia-util', 'columns')
        ],
        [
            Input('intervalo-operador', 'n_intervals'),
            Input('filtro-mes-operador', 'value'),
            Input('filtro-ano-operador', 'value')
        ],
        [State('operador-selecionado-store', 'data')]
    )
    def atualizar_tabela_dia_util(n, mes, ano, operador_selecionado):
        """Atualiza a tabela Dia Útil."""
        
        if not operador_selecionado:
            return [], []
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        if not pagamentos:
            return [], []
        
        df = pd.DataFrame(pagamentos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        df_mes = df[(df['dtPgto'].dt.month == mes) & (df['dtPgto'].dt.year == ano)]
        
        faturamento_por_dia = {}
        quantidade_por_dia = {}
        if not df_mes.empty:
            ultima_data = df_mes['dtPgto'].max()
            df_mes = df_mes[df_mes['dtPgto'] <= ultima_data]
            
            for _, row in df_mes.iterrows():
                dia = row['dtPgto'].day
                faturamento_por_dia[dia] = faturamento_por_dia.get(dia, 0) + row['valorTotal']
                quantidade_por_dia[dia] = quantidade_por_dia.get(dia, 0) + 1
        
        dias_uteis = get_dias_uteis(ano, mes)
        
        resultado = []
        for i, dia in enumerate(dias_uteis, start=1):
            resultado.append({
                'dia_util': i,
                'dia': dia,
                'quantidade': quantidade_por_dia.get(dia, 0),
                'faturamento': faturamento_por_dia.get(dia, 0)
            })
        
        df_resultado = pd.DataFrame(resultado)
        
        total_quantidade = df_resultado['quantidade'].sum()
        total_faturamento = df_resultado['faturamento'].sum()
        
        dados = []
        for _, row in df_resultado.iterrows():
            dados.append({
                'dia_util': row['dia_util'],
                'dia': row['dia'],
                'quantidade': row['quantidade'],
                'faturamento': f"R$ {row['faturamento']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            })
        
        dados.append({
            'dia_util': 'TOTAL',
            'dia': '-',
            'quantidade': total_quantidade,
            'faturamento': f"R$ {total_faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        })
        
        colunas = [
            {"name": "Dia Útil", "id": "dia_util"},
            {"name": "Data", "id": "dia"},
            {"name": "Quantidade", "id": "quantidade"},
            {"name": "Faturamento", "id": "faturamento"}
        ]
        
        return dados, colunas
    
    # ================================================================
    # TABELA MÊS A MÊS
    # ================================================================
    @app.callback(
        [
            Output('tabela-mes-mes', 'data'),
            Output('tabela-mes-mes', 'columns')
        ],
        [
            Input('intervalo-operador', 'n_intervals'),
            Input('filtro-ano-operador', 'value')
        ],
        [State('operador-selecionado-store', 'data')]
    )
    def atualizar_tabela_mes_mes(n, ano, operador_selecionado):
        """Atualiza a tabela Mês a Mês."""
        
        if not operador_selecionado:
            return [], []
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        metas = buscar_metas_por_operador(operador_selecionado)
        
        if not pagamentos:
            return [], []
        
        df = pd.DataFrame(pagamentos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        df_ano = df[df['dtPgto'].dt.year == ano]
        
        if not df_ano.empty:
            ultima_data = df_ano['dtPgto'].max()
            df_ano = df_ano[df_ano['dtPgto'] <= ultima_data]
        
        df_ano['mes'] = df_ano['dtPgto'].dt.month
        df_mes = df_ano.groupby('mes').agg(
            quantidade=('valorTotal', 'count'),
            faturamento=('valorTotal', 'sum')
        ).reset_index()
        
        metas_dict = {}
        if metas:
            for meta in metas:
                if meta['data'].year == ano:
                    metas_dict[meta['data'].month] = meta.get('meta100', 0)
        
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        resultado = []
        
        for mes in range(1, 13):
            pag_mes = df_mes[df_mes['mes'] == mes]
            faturamento = pag_mes['faturamento'].values[0] if not pag_mes.empty else 0
            quantidade = pag_mes['quantidade'].values[0] if not pag_mes.empty else 0
            meta = metas_dict.get(mes, 0)
            
            percentual = (faturamento / meta) * 100 if meta > 0 else 0
            bateu = faturamento >= meta
            
            resultado.append({
                'mes': mes,
                'nome_mes': meses_nomes[mes-1],
                'quantidade': quantidade,
                'faturamento': faturamento,
                'meta': meta,
                'percentual': percentual,
                'bateu': '✅ Sim' if bateu else '❌ Não'
            })
        
        df_resultado = pd.DataFrame(resultado)
        
        ultimo_mes_com_dado = df_mes['mes'].max() if not df_mes.empty else 0
        if ultimo_mes_com_dado > 0:
            df_resultado = df_resultado[df_resultado['mes'] <= ultimo_mes_com_dado]
        
        total_quantidade = df_resultado['quantidade'].sum()
        total_faturamento = df_resultado['faturamento'].sum()
        
        dados = []
        for _, row in df_resultado.iterrows():
            dados.append({
                'nome_mes': row['nome_mes'],
                'quantidade': row['quantidade'],
                'faturamento': f"R$ {row['faturamento']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'meta': f"R$ {row['meta']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                'percentual': f"{row['percentual']:.1f}%",
                'bateu': row['bateu']
            })
        
        dados.append({
            'nome_mes': 'TOTAL',
            'quantidade': total_quantidade,
            'faturamento': f"R$ {total_faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            'meta': '-',
            'percentual': '-',
            'bateu': '-'
        })
        
        colunas = [
            {"name": "Mês", "id": "nome_mes"},
            {"name": "Quantidade", "id": "quantidade"},
            {"name": "Faturamento", "id": "faturamento"},
            {"name": "Meta", "id": "meta"},
            {"name": "% Meta", "id": "percentual"},
            {"name": "Bateu?", "id": "bateu"}
        ]
        
        return dados, colunas
    
    # ================================================================
    # TABELA DE PERFORMANCE
    # ================================================================
    @app.callback(
        [
            Output('tabela-performance-operador', 'data'),
            Output('tabela-performance-operador', 'columns')
        ],
        [
            Input('intervalo-operador', 'n_intervals'),
            Input('filtro-mes-operador', 'value'),
            Input('filtro-ano-operador', 'value')
        ],
        [
            State('operador-selecionado-store', 'data'),
            State('banco-operador-store', 'data')
        ]
    )
    def atualizar_tabela_performance(n, mes, ano, operador_selecionado, banco):
        """Atualiza a tabela de performance."""
        
        if not operador_selecionado:
            return [], []
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        metas = buscar_metas_por_operador(operador_selecionado)
        
        if not pagamentos:
            return [], []
        
        perf = calcular_performance_operador(
            pagamentos=pagamentos,
            metas=metas,
            ano=ano,
            mes=mes,
            login=operador_selecionado.get('login')
        )
        
        dados_tabela = [{
            "login": perf['login'],
            "faturamento": f"R$ {perf['faturamento']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "feito_diario": f"R$ {perf['feito_diario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "meta": f"R$ {perf['meta']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "atingido_meta": f"{perf['atingido_meta']:.1f}%",
            "projecao": f"R$ {perf['projecao']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "dias_trabalhados": perf['dias_trabalhados'],
            "dias_restantes": perf['dias_restantes']
        }]
        
        colunas = [
            {"name": "Login", "id": "login"},
            {"name": "Faturamento", "id": "faturamento"},
            {"name": "Feito Diário", "id": "feito_diario"},
            {"name": "Meta", "id": "meta"},
            {"name": "% Meta", "id": "atingido_meta"},
            {"name": "Projeção (R$)", "id": "projecao"},
            {"name": "Dias Trab.", "id": "dias_trabalhados"},
            {"name": "Dias Rest.", "id": "dias_restantes"}
        ]
        
        return dados_tabela, colunas
    
    # ================================================================
    # GRÁFICO - Faturamento por Mês (Barras)
    # ================================================================
    @app.callback(
        Output('grafico-fase-operador', 'figure'),
        [
            Input('intervalo-operador', 'n_intervals'),
            Input('filtro-ano-operador', 'value')
        ],
        [State('operador-selecionado-store', 'data')]
    )
    def atualizar_grafico_mensal(n, ano, operador_selecionado):
        """Gráfico de barras: faturamento por mês do ano selecionado."""
        
        fig_blank = px.bar(title="Sem dados").update_layout(plot_bgcolor='white')
        
        if not operador_selecionado:
            return fig_blank
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        
        if not pagamentos:
            return fig_blank
        
        df = pd.DataFrame(pagamentos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        # Filtra pelo ano
        df_ano = df[df['dtPgto'].dt.year == ano]
        
        if df_ano.empty:
            return fig_blank
        
        # Encontra a última data do ano
        ultima_data = df_ano['dtPgto'].max()
        df_ano = df_ano[df_ano['dtPgto'] <= ultima_data]
        
        # Agrupa por mês
        df_mensal = df_ano.groupby(df_ano['dtPgto'].dt.month)['valorTotal'].sum().reset_index()
        df_mensal.columns = ['mes', 'faturamento']
        
        # Nomes dos meses
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        df_mensal['mes_nome'] = df_mensal['mes'].apply(lambda x: meses_nomes[x-1])
        
        # Gráfico de barras
        fig = px.bar(
            df_mensal, 
            x='mes_nome', 
            y='faturamento',
            title=f"Faturamento Mensal - {ano}",
            text='faturamento',
            color_discrete_sequence=['#7e3d97']
        )
        
        # Formata os valores nas barras
        fig.update_traces(
            texttemplate='R$ %{y:,.0f}',
            textposition='outside'
        )
        
        # Layout
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="Mês",
            yaxis_title="Faturamento (R$)",
            font=dict(color='#111827')
        )
        
        return fig
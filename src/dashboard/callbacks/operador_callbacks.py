"""
CALLBACKS DA TELA DE DETALHE DO OPERADOR
=========================================
Gerencia as tabelas e gráficos do operador.
"""

from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import calendar
from datetime import datetime, date
import holidays

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
        feriados_br = holidays.country_holidays('BR', years=ano)
        ultimo_dia = calendar.monthrange(ano, mes)[1]
        for dia in range(1, ultimo_dia + 1):
            data = date(ano, mes, dia)
            if data.weekday() < 5 and data not in feriados_br:
                dias_uteis.append(dia)
        return dias_uteis
    
    # ================================================================
    # FUNÇÃO AUXILIAR: FILTRAR "FORA DA FASE" PARA SEMEAR
    # ================================================================
    def filtrar_fora_da_fase(df, banco):
        """Remove pagamentos 'Fora da fase' apenas para operadores SEMEAR."""
        if banco == "SEMEAR":
            if 'faseAtraso' in df.columns:
                return df[df['faseAtraso'] != "Fora da fase"]
            elif 'fase' in df.columns:
                return df[df['fase'] != "Fora da fase"]
        return df
    
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
        [
            State('operador-selecionado-store', 'data'),
            State('banco-operador-store', 'data')
        ]
    )
    def atualizar_tabela_dia_dia(n, mes, ano, operador_selecionado, banco):
        """Atualiza a tabela Dia a Dia."""
        
        print(f"[DEBUG] Dia a Dia - Banco: {banco}")
        
        if not operador_selecionado:
            return [], []
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        if not pagamentos:
            return [], []
        
        df = pd.DataFrame(pagamentos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        mes_int = int(mes)
        ano_int = int(ano)
        
        df_mes = df[(df['dtPgto'].dt.month == mes_int) & (df['dtPgto'].dt.year == ano_int)]
        
        print(f"[DEBUG] Dia a Dia - Pagamentos no mês: {len(df_mes)}")
        
        if df_mes.empty:
            return [], []
        
        df_mes = filtrar_fora_da_fase(df_mes, banco)
        
        print(f"[DEBUG] Dia a Dia - Após filtro: {len(df_mes)}")
        
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
        [
            State('operador-selecionado-store', 'data'),
            State('banco-operador-store', 'data')
        ]
    )
    def atualizar_tabela_dia_util(n, mes, ano, operador_selecionado, banco):
        """Atualiza a tabela Dia Útil."""
        
        print(f"[DEBUG] Dia Útil - Banco: {banco}")
        
        if not operador_selecionado:
            return [], []
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        if not pagamentos:
            return [], []
        
        df = pd.DataFrame(pagamentos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        mes_int = int(mes)
        ano_int = int(ano)
        
        df_mes = df[(df['dtPgto'].dt.month == mes_int) & (df['dtPgto'].dt.year == ano_int)]
        
        print(f"[DEBUG] Dia Útil - Pagamentos no mês: {len(df_mes)}")
        
        df_mes = filtrar_fora_da_fase(df_mes, banco)
        
        print(f"[DEBUG] Dia Útil - Após filtro: {len(df_mes)}")
        
        faturamento_por_dia = {}
        quantidade_por_dia = {}
        if not df_mes.empty:
            ultima_data = df_mes['dtPgto'].max()
            df_mes = df_mes[df_mes['dtPgto'] <= ultima_data]
            
            for _, row in df_mes.iterrows():
                dia = row['dtPgto'].day
                faturamento_por_dia[dia] = faturamento_por_dia.get(dia, 0) + row['valorTotal']
                quantidade_por_dia[dia] = quantidade_por_dia.get(dia, 0) + 1
        
        dias_uteis = get_dias_uteis(ano_int, mes_int)
        
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
        [
            State('operador-selecionado-store', 'data'),
            State('banco-operador-store', 'data')
        ]
    )
    def atualizar_tabela_mes_mes(n, ano, operador_selecionado, banco):
        """Atualiza a tabela Mês a Mês."""
        
        print(f"[DEBUG] Mês a Mês - Banco: {banco}")
        
        if not operador_selecionado:
            return [], []
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        metas = buscar_metas_por_operador(operador_selecionado)
        
        if not pagamentos:
            return [], []
        
        df = pd.DataFrame(pagamentos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        ano_int = int(ano)
        
        df_ano = df[df['dtPgto'].dt.year == ano_int]
        
        metas_dict = {}
        if metas:
            for meta in metas:
                if meta['data'].year == ano_int:
                    metas_dict[meta['data'].month] = meta.get('meta100', 0)
        
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        resultado = []
        
        for mes in range(1, 13):
            df_mes = df_ano[df_ano['dtPgto'].dt.month == mes].copy()
            
            df_mes = filtrar_fora_da_fase(df_mes, banco)
            
            if not df_mes.empty:
                ultima_data = df_mes['dtPgto'].max()
                df_mes = df_mes[df_mes['dtPgto'] <= ultima_data]
            
            faturamento = df_mes['valorTotal'].sum() if not df_mes.empty else 0
            quantidade = len(df_mes) if not df_mes.empty else 0
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
        
        # Encontra o último mês com dado
        ultimo_mes_com_dado = 0
        for mes in range(12, 0, -1):
            if df_resultado.iloc[mes-1]['faturamento'] > 0:
                ultimo_mes_com_dado = mes
                break
        
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
            Output('tabela-performance-operador', 'columns'),
            Output('info-dias-operador', 'children'),  # ← subtítulo com dias
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
        """Atualiza a tabela de performance. Dias trabalhados/restantes vão como subtítulo."""
        
        if not operador_selecionado:
            return [], [], ""
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        metas = buscar_metas_por_operador(operador_selecionado)
        
        if not pagamentos:
            return [], [], ""
        
        ano_int = int(ano)
        mes_int = int(mes)
        
        perf = calcular_performance_operador(
            pagamentos=pagamentos,
            metas=metas,
            ano=ano_int,
            mes=mes_int,
            login=operador_selecionado.get('login'),
            banco=banco
        )
        
        # Subtítulo com os dias (substitui as colunas da tabela)
        txt_dias = (
            f"📅 Dias trabalhados: {perf['dias_trabalhados']}  "
            f"|  ⏳ Dias úteis restantes: {perf['dias_restantes']}  "
            f"|  📆 Total dias úteis: {perf['total_dias_uteis']}"
        )
        
        dados_tabela = [{
            "login":            perf['login'],
            "faturamento":      f"R$ {perf['faturamento']:,.2f}".replace(",","X").replace(".",",").replace("X","."),
            "feito_diario":     f"R$ {perf['feito_diario']:,.2f}".replace(",","X").replace(".",",").replace("X","."),
            "meta":             f"R$ {perf['meta']:,.2f}".replace(",","X").replace(".",",").replace("X","."),
            "atingido_meta":    f"{perf['atingido_meta']:.1f}%",
            "projecao":         f"R$ {perf['projecao']:,.2f}".replace(",","X").replace(".",",").replace("X","."),
        }]
        
        colunas = [
            {"name": "Login",         "id": "login"},
            {"name": "Faturamento",   "id": "faturamento"},
            {"name": "Feito Diário",  "id": "feito_diario"},
            {"name": "Meta",          "id": "meta"},
            {"name": "% Meta",        "id": "atingido_meta"},
            {"name": "Projeção (R$)", "id": "projecao"},
        ]
        
        return dados_tabela, colunas, txt_dias
    
    # ================================================================
    # GRÁFICO - Faturamento por Mês (Barras)
    # ================================================================
    @app.callback(
        Output('grafico-fase-operador', 'figure'),
        [
            Input('intervalo-operador', 'n_intervals'),
            Input('filtro-ano-operador', 'value')
        ],
        [
            State('operador-selecionado-store', 'data'),
            State('banco-operador-store', 'data')
        ]
    )
    def atualizar_grafico_mensal(n, ano, operador_selecionado, banco):
        """Gráfico de barras: faturamento por mês do ano selecionado."""
        
        fig_blank = px.bar(title="Sem dados").update_layout(plot_bgcolor='white')
        
        if not operador_selecionado:
            return fig_blank
        
        pagamentos = Buscar_pagamento_por_operador(operador_selecionado)
        
        if not pagamentos:
            return fig_blank
        
        df = pd.DataFrame(pagamentos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        ano_int = int(ano)
        
        df_ano = df[df['dtPgto'].dt.year == ano_int]
        
        if df_ano.empty:
            return fig_blank
        
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        faturamento_mensal = []
        
        for mes in range(1, 13):
            df_mes = df_ano[df_ano['dtPgto'].dt.month == mes].copy()
            
            df_mes = filtrar_fora_da_fase(df_mes, banco)
            
            if not df_mes.empty:
                ultima_data = df_mes['dtPgto'].max()
                df_mes = df_mes[df_mes['dtPgto'] <= ultima_data]
                faturamento = df_mes['valorTotal'].sum()
            else:
                faturamento = 0
            
            faturamento_mensal.append({
                'mes': mes,
                'mes_nome': meses_nomes[mes-1],
                'faturamento': faturamento
            })
        
        df_mensal = pd.DataFrame(faturamento_mensal)
        
        fig = px.bar(
            df_mensal[df_mensal['faturamento'] > 0], 
            x='mes_nome', 
            y='faturamento',
            title=f"Faturamento Mensal - {ano_int}",
            text='faturamento',
            color_discrete_sequence=['#7e3d97']
        )
        
        if not df_mensal[df_mensal['faturamento'] > 0].empty:
            fig.update_traces(
                texttemplate='R$ %{y:,.0f}',
                textposition='outside'
            )
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title="Mês",
            yaxis_title="Faturamento (R$)",
            font=dict(color='#111827')
        )
        
        return fig
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

from src.services.db_service import Buscar_login, Buscar_pagamento
from src.services.analytics_service import calcular_indicadores_operador, calcular_faturamento_por_dia


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
            Output('kpi-mes-anterior', 'children')
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
        # FIGURA VAZIA
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
            return texto_zero, texto_zero, "0", fig_blank, [], [], ""
        
        login = dados_operador.get('login')
        if not login:
            log_debug("SEM LOGIN")
            return texto_zero, texto_zero, "0", fig_blank, [], [], ""
        
        # ================================================================
        # BUSCA OS DADOS
        # ================================================================
        operador = Buscar_login(login)
        pagamentos_brutos = Buscar_pagamento(operador) if operador else None
        
        if not pagamentos_brutos:
            log_debug("NENHUM PAGAMENTO ENCONTRADO")
            return texto_zero, texto_zero, "0", fig_blank, [], [], ""

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
        # FILTRO DE FASE - VERSÃO QUE FUNCIONA
        # ================================================================
        if fase and "todas" not in str(fase).lower():
            log_debug(f"Aplicando filtro de fase: '{fase}'")
            
            if 'faseAtraso' in df_mes_atual.columns:
                # Mostra os valores únicos no banco
                log_debug(f"Valores no banco: {df_mes_atual['faseAtraso'].unique()}")
                
                # Função para normalizar (remove espaços, converte para maiúsculo)
                def normalizar(texto):
                    if texto is None or pd.isna(texto):
                        return ""
                    return str(texto).strip().upper()
                
                # Normaliza a coluna do banco
                df_mes_atual['_fase_norm'] = df_mes_atual['faseAtraso'].apply(normalizar)
                
                # Normaliza o filtro e aplica
                if isinstance(fase, list):
                    fase_norm = [normalizar(f) for f in fase]
                    df_mes_atual = df_mes_atual[df_mes_atual['_fase_norm'].isin(fase_norm)]
                else:
                    fase_norm = normalizar(fase)
                    df_mes_atual = df_mes_atual[df_mes_atual['_fase_norm'] == fase_norm]
                
                df_mes_atual = df_mes_atual.drop(columns=['_fase_norm'])
                log_debug(f"Registros após filtro de fase: {len(df_mes_atual)}")
            else:
                log_debug("ERRO: Coluna 'faseAtraso' não encontrada!")
                # Fallback para coluna 'fase' se existir
                if 'fase' in df_mes_atual.columns:
                    log_debug("Usando coluna 'fase' como fallback")
                    def normalizar(texto):
                        if texto is None or pd.isna(texto):
                            return ""
                        return str(texto).strip().upper()
                    
                    df_mes_atual['_fase_norm'] = df_mes_atual['fase'].apply(normalizar)
                    if isinstance(fase, list):
                        fase_norm = [normalizar(f) for f in fase]
                        df_mes_atual = df_mes_atual[df_mes_atual['_fase_norm'].isin(fase_norm)]
                    else:
                        fase_norm = normalizar(fase)
                        df_mes_atual = df_mes_atual[df_mes_atual['_fase_norm'] == fase_norm]
                    df_mes_atual = df_mes_atual.drop(columns=['_fase_norm'])
                    log_debug(f"Registros após filtro (fallback): {len(df_mes_atual)}")
        
        # ================================================================
        # FILTRO DE TEXTO
        # ================================================================
        if texto_busca:
            log_debug(f"Aplicando filtro de texto: '{texto_busca}'")
            texto = str(texto_busca).lower()
            contains_contrato = df_mes_atual['contrato'].fillna('').astype(str).str.lower().str.contains(texto)
            contains_cliente = df_mes_atual.get('cliente', pd.Series(dtype=str)).fillna('').astype(str).str.lower().str.contains(texto)
            df_mes_atual = df_mes_atual[contains_contrato | contains_cliente]
            log_debug(f"Registros após filtro de texto: {len(df_mes_atual)}")
        
        # ================================================================
        # CÁLCULOS
        # ================================================================
        fat_anterior = df_mes_anterior['valorTotal'].sum() if not df_mes_anterior.empty else 0.0
        txt_fat_anterior = f"Mês anterior: R$ {fat_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        if df_mes_atual.empty:
            log_debug("DataFrame vazio - retornando sem dados")
            return texto_zero, texto_zero, "0", fig_blank, [], [], txt_fat_anterior
        
        pagamentos_filtrados = df_mes_atual.to_dict('records')
        indicadores = calcular_indicadores_operador(pagamentos_filtrados)
        
        faturamento = indicadores['faturamento_total']
        ticket = indicadores['ticket_medio']
        total = indicadores['total_pagamentos']
        
        txt_faturamento = f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        txt_ticket = f"R$ {ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        txt_total = f"{total:,}".replace(",", ".")
        
        # ================================================================
        # GRÁFICO
        # ================================================================
        df_grafico = calcular_faturamento_por_dia(pagamentos_filtrados)
        
        if not df_grafico.empty:
            figura = go.Figure()
            figura.add_trace(go.Scatter(
                mode='lines+markers',
                line=dict(color='#7e3d97', width=3),
                marker=dict(size=8, color='#7e3d97'),
                fill='tozeroy',
                fillcolor='rgba(126, 61, 151, 0.2)',
                x=df_grafico['data'],
                y=df_grafico['total']
            ))
            figura.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(showgrid=True, gridcolor='#E5E7EB', title=''),
                yaxis=dict(showgrid=True, gridcolor='#E5E7EB', title='')
            )
        else:
            figura = fig_blank

        # ================================================================
        # TABELA
        # ================================================================
        colunas_visiveis = ['dtPgto', 'contrato', 'cliente', 'valorTotal', 'faseAtraso']
        
        # Verifica se a coluna 'faseAtraso' existe, se não usa 'fase'
        if 'faseAtraso' not in df_mes_atual.columns and 'fase' in df_mes_atual.columns:
            colunas_visiveis = ['dtPgto', 'contrato', 'cliente', 'valorTotal', 'fase']
        
        df_tabela = df_mes_atual[colunas_visiveis].copy()
        df_tabela = df_tabela.sort_values(by='dtPgto', ascending=False)
        df_tabela['dtPgto'] = df_tabela['dtPgto'].dt.strftime('%d/%m/%Y')
        df_tabela['valorTotal'] = df_tabela['valorTotal'].map(
            lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        # Renomeia as colunas
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
            txt_fat_anterior
        )
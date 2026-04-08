"""
CALLBACKS RESTRITOS A TELA DE PAGAMENTOS
=========================================
"""

import pandas as pd
from dash.dependencies import Input, Output, State

from src.services.db_service import Buscar_login, Buscar_pagamento

def register_callbacks(app):
    
    @app.callback(
        [
            Output('tabela-pagamentos-completa', 'data'),
            Output('tabela-pagamentos-completa', 'columns'),
        ],
        [
            Input('intervalo-atualizacao-pgtos', 'n_intervals'),
            Input('url', 'pathname'),
            Input('filtro-texto-pgtos-completo', 'value')        
        ],
        [State('login-success-store', 'data')]
    )
    def atualizar_tabela_mestra(n_intervals, pathname, texto_busca, dados_operador):
        
        # Só opera de verdade se o usuário estiver de fato com essa tela ("Pagamentos") aberta
        if pathname != '/pagamentos' or not dados_operador:
            return [], []
            
        login = dados_operador.get('login')
        if not login:
            return [], []
        
        operador = Buscar_login(login)
        pagamentos_brutos = Buscar_pagamento(operador) if operador else None
        
        if not pagamentos_brutos:
            return [], []

        # 🧪 FILTRAGEM
        df = pd.DataFrame(pagamentos_brutos)
        
        # Filtro Texto Completo em Qualquer Coluna (Opcional, pois a Table já tem Native Filter)
        if texto_busca:
            texto = str(texto_busca).lower()
            df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(texto).any(), axis=1)]
            
        if df.empty:
            return [], []

        # 📋 PREPARAÇÃO DA TABELA MASTER - 7 COLUNAS EXIGIDAS
        # 'dtPgto', 'VENCIMENTO', 'contrato', 'cliente', 'valorTotal', 'MAIOR_ATRASO', 'fase'
        
        # Vamos usar um Try/Except ou ".get" porque às vezes as colunas de "maior atraso" e "Vencimento" 
        # podem não estar padronizadas exatamente pelo crawler se ele não coletou
        col_venc = 'dtVenc' if 'dtVenc' in df.columns else 'data_vencimento' if 'data_vencimento' in df.columns else None
        col_atraso = 'maiorAtraso' if 'maiorAtraso' in df.columns else 'dias_atraso' if 'dias_atraso' in df.columns else None
        
        # Força criação pra não dar KeyError caso nulo
        if not col_venc: df['dtVenc'] = "-"; col_venc = 'dtVenc'
        if not col_atraso: df['maiorAtraso'] = "0"; col_atraso = 'maiorAtraso'
            
        colunas_visiveis = ['dtPgto', col_venc, 'contrato', 'cliente', 'valorTotal', col_atraso, 'fase']
        df_tabela = df[colunas_visiveis].copy()
        
        # Tenta formatar data pgto
        df_tabela['dtPgto'] = pd.to_datetime(df_tabela['dtPgto'], errors='coerce')
        df_tabela = df_tabela.sort_values(by='dtPgto', ascending=False)
        df_tabela['dtPgto'] = df_tabela['dtPgto'].dt.strftime('%d/%m/%Y')
        
        # Tenta formatar Vencimento 
        try:
            df_tabela[col_venc] = pd.to_datetime(df_tabela[col_venc], errors='coerce').dt.strftime('%d/%m/%Y').fillna("-")
        except:
            pass
            
        # Formata valor
        df_tabela['valorTotal'] = pd.to_numeric(df_tabela['valorTotal'], errors='coerce').fillna(0.0)
        df_tabela['valorTotal'] = df_tabela['valorTotal'].map(lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        nomes_colunas = {
            'dtPgto': 'Data Pgto',
            col_venc: 'Data Vencimento',
            'contrato': 'Contrato',
            'cliente': 'Cliente',
            'valorTotal': 'Valor Pago',
            col_atraso: 'Maior Atraso (Dias)',
            'fase': 'Fase Atraso'
        }
        df_tabela = df_tabela.rename(columns=nomes_colunas)
        
        dados_tabela = df_tabela.to_dict('records')
        colunas_tabela = [{"name": i, "id": i} for i in df_tabela.columns]

        return dados_tabela, colunas_tabela

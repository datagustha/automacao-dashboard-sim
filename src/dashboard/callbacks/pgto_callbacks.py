"""
CALLBACKS RESTRITOS A TELA DE PAGAMENTOS
=========================================
"""

import pandas as pd
from dash.dependencies import Input, Output, State

from src.services.db_service import Buscar_login, Buscar_pagamento_por_operador


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
        if not operador:
            return [], []
        
        # Usa a função genérica para buscar pagamentos
        pagamentos_brutos = Buscar_pagamento_por_operador(operador)
        
        if not pagamentos_brutos:
            return [], []

        # 🧪 FILTRAGEM
        df = pd.DataFrame(pagamentos_brutos)
        
        # Filtro Texto Completo em Qualquer Coluna
        if texto_busca:
            texto = str(texto_busca).lower()
            # Aplica o filtro em todas as colunas string
            mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(texto).any(), axis=1)
            df = df[mask]
            
        if df.empty:
            return [], []

        # 📋 PREPARAÇÃO DA TABELA MASTER
        # Define as colunas que serão exibidas
        colunas_visiveis = ['dtPgto', 'contrato', 'cliente', 'valorTotal', 'faseAtraso']
        
        # Verifica se as colunas existem
        colunas_existentes = [col for col in colunas_visiveis if col in df.columns]
        df_tabela = df[colunas_existentes].copy()
        
        # Formata data
        if 'dtPgto' in df_tabela.columns:
            df_tabela['dtPgto'] = pd.to_datetime(df_tabela['dtPgto'], errors='coerce')
            df_tabela = df_tabela.sort_values(by='dtPgto', ascending=False)
            df_tabela['dtPgto'] = df_tabela['dtPgto'].dt.strftime('%d/%m/%Y')
        
        # Formata valor
        if 'valorTotal' in df_tabela.columns:
            df_tabela['valorTotal'] = pd.to_numeric(df_tabela['valorTotal'], errors='coerce').fillna(0.0)
            df_tabela['valorTotal'] = df_tabela['valorTotal'].map(
                lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        
        # Renomeia as colunas
        rename_dict = {
            'dtPgto': 'Data Pgto',
            'contrato': 'Contrato',
            'cliente': 'Cliente',
            'valorTotal': 'Valor Pago',
            'faseAtraso': 'Fase Atraso'
        }
        df_tabela = df_tabela.rename(columns={k: v for k, v in rename_dict.items() if k in df_tabela.columns})
        
        dados_tabela = df_tabela.to_dict('records')
        colunas_tabela = [{"name": i, "id": i} for i in df_tabela.columns]

        return dados_tabela, colunas_tabela
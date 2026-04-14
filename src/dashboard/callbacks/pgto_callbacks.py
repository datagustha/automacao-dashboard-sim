"""
CALLBACKS RESTRITOS A TELA DE PAGAMENTOS
=========================================
- Operador: vê só seus próprios pagamentos
- ADM: usa banco-selecionado-pgtos para ver pagamentos de todos do banco
"""

import pandas as pd
from dash.dependencies import Input, Output, State

from src.services.db_service import (
    Buscar_login,
    Buscar_pagamento_por_operador,
    buscar_pagamentos_todos_operadores_por_banco
)


def register_callbacks(app):
    
    @app.callback(
        [
            Output('tabela-pagamentos-completa', 'data'),
            Output('tabela-pagamentos-completa', 'columns'),
        ],
        [
            Input('intervalo-atualizacao-pgtos', 'n_intervals'),
            Input('url', 'pathname'),
            Input('filtro-texto-pgtos-completo', 'value'),
            Input('banco-selecionado-pgtos', 'value'),  # ← seletor ADM
            Input('adm-filtro-atividade-pgtos', 'value'), # ← atividade ADM
        ],
        [State('login-success-store', 'data')]
    )
    def atualizar_tabela_mestra(n_intervals, pathname, texto_busca, banco_escolhido, atividade_escolhida, dados_operador):
        """
        Atualiza a tabela mestra de pagamentos.
        
        - Operador: mostra só os próprios pagamentos
        - ADM: mostra TODOS os pagamentos do banco selecionado, de acordo com a atividade
        """
        if pathname != '/pagamentos' or not dados_operador:
            return [], []
        
        login = dados_operador.get('login')
        if not login:
            return [], []

        perfil = dados_operador.get('perfil', 'operador')
        banco  = dados_operador.get('banco', 'SEMEAR')

        # ── ADM: carrega todos os pagamentos do banco selecionado ──────────
        if perfil == 'adm':
            banco_para_buscar = banco_escolhido or 'SEMEAR'
            todos = buscar_pagamentos_todos_operadores_por_banco(banco_para_buscar)
            pagamentos_brutos = []
            
            for operador_dict, pagamentos, _ in todos:
                # Se selecionado "ativo", ignora os dados de operadores não ativos
                if atividade_escolhida == 'ativo' and operador_dict.get('atividade') != 'ativo':
                    continue
                pagamentos_brutos.extend(pagamentos or [])
        else:
            # ── Operador: só os próprios ───────────────────────────────────
            operador = Buscar_login(login)
            if not operador:
                return [], []
            pagamentos_brutos = Buscar_pagamento_por_operador(operador)

        if not pagamentos_brutos:
            return [], []

        df = pd.DataFrame(pagamentos_brutos)
        
        # Filtro de texto em qualquer coluna
        if texto_busca:
            texto = str(texto_busca).lower()
            mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(texto).any(), axis=1)
            df = df[mask]
            
        if df.empty:
            return [], []

        # Colunas visíveis
        colunas_visiveis = ['dtPgto', 'contrato', 'cliente', 'valorTotal', 'faseAtraso']
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
        
        # Para ADM: adiciona coluna de operador se disponível
        if perfil == 'adm' and 'operador' in df.columns:
            df_tabela['operador'] = df['operador']
            colunas_existentes = ['operador'] + colunas_existentes

        rename_dict = {
            'dtPgto':    'Data Pgto',
            'contrato':  'Contrato',
            'cliente':   'Cliente',
            'valorTotal':'Valor Pago',
            'faseAtraso':'Fase Atraso',
            'operador':  'Operador',
        }
        df_tabela = df_tabela.rename(columns={k: v for k, v in rename_dict.items() if k in df_tabela.columns})
        
        dados_tabela  = df_tabela.to_dict('records')
        colunas_tabela = [{"name": i, "id": i} for i in df_tabela.columns]

        return dados_tabela, colunas_tabela
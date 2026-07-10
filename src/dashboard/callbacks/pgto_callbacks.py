"""
CALLBACKS RESTRITOS A TELA DE PAGAMENTOS
=========================================
- Operador: vê só seus próprios pagamentos do mês selecionado
- ADM: usa banco-selecionado-pgtos para ver pagamentos de todos do banco no mês
- CORRIGIDO: Filtros de mês, ano e fase (multi-select) funcionando
"""

import pandas as pd
import datetime
import dash
from dash.dependencies import Input, Output, State
from dash import no_update

from src.services.db_service import (
    Buscar_login,
    Buscar_pagamento_por_operador,
    buscar_pagamentos_todos_operadores_por_banco
)
from src.dashboard.components.filtros import aplicar_filtro_data

def register_callbacks(app):
    
    @app.callback(
        [
            Output('tabela-pagamentos-completa', 'data'),
            Output('tabela-pagamentos-completa', 'columns'),
            Output('badge-data-range-pgtos', 'style')
        ],
        [
            Input('intervalo-atualizacao-pgtos', 'n_intervals'),
            Input('url', 'pathname'),
            Input('filtro-mes-pgtos', 'value'),
            Input('filtro-ano-pgtos', 'value'),
            Input('filtro-fase-pgtos', 'value'),
            Input('filtro-texto-pgtos-completo', 'value'),
            Input('banco-selecionado-pgtos', 'value'),
            Input('adm-filtro-atividade-pgtos', 'value'),
            Input('filtro-data-range-pgtos', 'start_date'),
            Input('filtro-data-range-pgtos', 'end_date'),
        ],
        [
            State('login-success-store', 'data')
        ]
    )
    def atualizar_tabela_mestra(n_intervals, pathname, mes, ano, fases_selecionadas, texto_busca, 
                                 banco_escolhido, atividade_escolhida, data_inicio, data_fim, dados_operador):
        """
        CORRIGIDO: 
        - Agora filtra por MÊS e ANO ou RANGE
        - Filtro de FASE com multi-select (lista)
        - Operador vê APENAS seus pagamentos do mês
        - Admin vê todos do banco no mês
        """
        
        if pathname != '/pagamentos' or not dados_operador:
            return no_update, no_update, no_update
        
        login = dados_operador.get('login')
        if not login:
            return [], [], {"display": "none"}

        perfil = dados_operador.get('perfil', 'operador')
        banco_usuario = dados_operador.get('banco', 'SEMEAR')
        
        # Pega mês e ano (default: mês atual)
        if not mes or not ano:
            agora = datetime.datetime.now()
            mes = mes or agora.month
            ano = ano or agora.year
        else:
            mes = int(mes)
            ano = int(ano)
        
        print(f"[PAGAMENTOS] Usuário: {login} | Perfil: {perfil} | Mês: {mes}/{ano} | Fases: {fases_selecionadas}")

        # ── BUSCA OS DADOS CONFORME PERFIL ──────────────────────────────────
        if perfil == 'adm':
            # ADMIN: Busca todos operadores do banco selecionado
            banco_para_buscar = banco_escolhido or 'SEMEAR'
            todos = buscar_pagamentos_todos_operadores_por_banco(banco_para_buscar)
            pagamentos_brutos = []
            
            for operador_dict, pagamentos, _ in todos:
                # Filtra por atividade se necessário
                if atividade_escolhida == 'ativo' and operador_dict.get('atividade') != 'ativo':
                    continue
                if pagamentos:
                    login_operador = operador_dict.get('login', '')
                    for p in pagamentos:
                        # Garante que cada pagamento carregue o login do operador,
                        # necessário para exibir/filtrar a coluna "Operador" na tabela do ADM
                        p['operador'] = login_operador
                    pagamentos_brutos.extend(pagamentos)
        else:
            # OPERADOR: Busca apenas seus pagamentos
            operador = Buscar_login(login)
            if not operador:
                return [], [], {"display": "none"}
            pagamentos_brutos = Buscar_pagamento_por_operador(operador)

        if not pagamentos_brutos:
            print(f"[PAGAMENTOS] Nenhum pagamento encontrado")
            return [], [], {"display": "none"}

        # ── CONVERTE PARA DATAFRAME ─────────────────────────────────────────
        df = pd.DataFrame(pagamentos_brutos)
        
        # Converte data
        usando_range = False
        label_periodo = ""
        if 'dtPgto' in df.columns:
            df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
            df = df.dropna(subset=['dtPgto'])
            
            # FILTRO POR MÊS/ANO OU RANGE
            df, usando_range, label_periodo = aplicar_filtro_data(df, mes, ano, data_inicio, data_fim)
            print(f"[PAGAMENTOS] Após filtro de datas: {len(df)} registros")
        
        if df.empty:
            print(f"[PAGAMENTOS] Sem dados para o período")
            return [], [], {"display": "none"}
        
        # ── FILTRO DE FASE (multi-select) ──────────────────────────────────
        banco_atual = banco_escolhido if perfil == 'adm' else banco_usuario
        
        if banco_atual == 'SEMEAR' and fases_selecionadas:
            # Verifica se NÃO é "TODAS" e se tem fases selecionadas
            if "TODAS" not in fases_selecionadas and len(fases_selecionadas) > 0:
                # Pega a coluna de fase correta
                coluna_fase = None
                if 'faseAtraso' in df.columns:
                    coluna_fase = 'faseAtraso'
                elif 'fase' in df.columns:
                    coluna_fase = 'fase'
                
                if coluna_fase:
                    # Filtra para incluir apenas as fases selecionadas
                    df = df[df[coluna_fase].isin(fases_selecionadas)]
                    print(f"[PAGAMENTOS] Após filtro de fases {fases_selecionadas}: {len(df)} registros")
        
        # ── FILTRO DE TEXTO (busca em qualquer coluna) ──────────────────────
        if texto_busca:
            texto = str(texto_busca).lower()
            df_str = df.astype(str)
            mask = df_str.apply(lambda row: row.str.lower().str.contains(texto).any(), axis=1)
            df = df[mask]
            print(f"[PAGAMENTOS] Após filtro de texto: {len(df)} registros")
            
        if df.empty:
            return [], [], {"display": "none"}

        # ── PREPARA TABELA PARA EXIBIÇÃO ───────────────────────────────────
        # Define colunas visíveis
        colunas_visiveis = ['dtPgto', 'contrato', 'cliente', 'valorTotal']
        
        # Adiciona fase se existir
        if 'faseAtraso' in df.columns:
            colunas_visiveis.append('faseAtraso')
        elif 'fase' in df.columns:
            colunas_visiveis.append('fase')
        
        # Para ADMIN, adiciona coluna do operador
        if perfil == 'adm' and 'operador' in df.columns:
            colunas_visiveis.insert(0, 'operador')
        
        colunas_existentes = [col for col in colunas_visiveis if col in df.columns]
        df_tabela = df[colunas_existentes].copy()
        
        # Ordena por data (mais recente primeiro)
        if 'dtPgto' in df_tabela.columns:
            df_tabela = df_tabela.sort_values(by='dtPgto', ascending=False)
            df_tabela['dtPgto'] = df_tabela['dtPgto'].dt.strftime('%d/%m/%Y')
        
        # Formata valor
        if 'valorTotal' in df_tabela.columns:
            df_tabela['valorTotal'] = pd.to_numeric(df_tabela['valorTotal'], errors='coerce').fillna(0.0)
            df_tabela['valorTotal'] = df_tabela['valorTotal'].map(
                lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
        
        # Renomeia colunas para exibição
        rename_dict = {
            'dtPgto': 'Data',
            'operador': 'Operador',
            'contrato': 'Contrato',
            'cliente': 'Cliente',
            'valorTotal': 'Valor',
            'faseAtraso': 'Fase',
            'fase': 'Fase',
        }
        df_tabela = df_tabela.rename(columns={k: v for k, v in rename_dict.items() if k in df_tabela.columns})
        
        dados_tabela = df_tabela.to_dict('records')
        colunas_tabela = [{"name": i, "id": i} for i in df_tabela.columns]
        badge_style = {"display": "inline-flex"} if usando_range else {"display": "none"}

        print(f"[PAGAMENTOS] OK Finalizado - {len(dados_tabela)} pagamentos exibidos")
        return dados_tabela, colunas_tabela, badge_style
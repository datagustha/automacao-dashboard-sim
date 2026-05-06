"""
CALLBACKS DOS GRÁFICOS E TABELAS - DASHBOARD
=============================================
CORRIGIDO: Filtros de mês funcionando, diferencia ADMIN/OPERADOR
PADRONIZADO: Gráficos com mesmo estilo, títulos, tamanhos
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime
import os
import re
import dash
from dash.dependencies import Input, Output, State
from dash import no_update

from src.services.db_service import (
    Buscar_login, 
    Buscar_pagamento_por_operador, 
    buscar_metas_por_operador
)
from src.services.analytics_service import (
    calcular_indicadores_operador, 
    calcular_faturamento_por_dia, 
    calcular_pagamentos_por_fase,
    calcular_performance_operador
)

# ================================================================
# DEFINIÇÃO DO retorno_vazio
# ================================================================
texto_zero = "R$ 0,00"
fig_blank = go.Figure().update_layout(
    title=dict(
        text="<b>Sem dados para o período selecionado</b>",
        font=dict(color='#111827', size=14),
        x=0,
        xanchor='left'
    ),
    height=400,
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(visible=False),
    yaxis=dict(visible=False)
)

retorno_vazio = (texto_zero, texto_zero, "0", fig_blank, [], [], texto_zero, fig_blank, texto_zero, {"width": "0%"}, "0%", texto_zero)

# ================================================================
# FUNÇÃO PARA APLICAR ESTILO PADRÃO A QUALQUER GRÁFICO
# ================================================================
def aplicar_estilo_padrao(figura, titulo: str, altura: int = 400):
    """
    Aplica estilo padrão a qualquer gráfico.
    
    ARGS:
        figura: objeto Figure do Plotly
        titulo: título do gráfico
        altura: altura do gráfico em pixels
    """
    figura.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(color='#111827', size=14),
            x=0,
            xanchor='left'
        ),
        height=altura,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#111827')
    )
    return figura

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
            Output('kpi-meta-percentual', 'children'),
            Output('kpi-pgtos-anterior', 'children'),
        ],
        [
            Input('url', 'pathname'),
            Input('filtro-mes', 'value'),
            Input('filtro-ano', 'value'),
            Input('filtro-texto-busca', 'value'),
            Input('filtro-fase', 'value')
        ],
        [
            State('login-success-store', 'data')
        ]
    )
    def atualizar_dashboard(pathname, mes, ano, texto_busca, fase, dados_operador):
        """
        CORRIGIDO: 
        - Removeu n_intervals (causava recarga desnecessária)
        - Filtro de mês aplicado CORRETAMENTE
        - Gráficos padronizados com mesmo estilo
        """
        
        # VERIFICA SE ESTÁ NO DASHBOARD
        if pathname != '/dashboard':
            return [no_update] * 12
            
        if not dados_operador:
            log_debug("Nenhum dado de operador no store")
            return retorno_vazio
        
        login = dados_operador.get('login')
        tipo_usuario = dados_operador.get('tipo', 'OPERADOR')
        
        if not login:
            log_debug("Login não encontrado")
            return retorno_vazio
        
        # BUSCA DADOS DO OPERADOR
        operador = Buscar_login(login)
        if not operador:
            log_debug(f"Operador não encontrado: {login}")
            return retorno_vazio
        
        banco = operador.get('banco', 'SEMEAR')
        log_debug(f"=== DASHBOARD - Operador: {login} | Banco: {banco} | Tipo: {tipo_usuario} | Mês: {mes}/{ano} ===")
        
        # BUSCA PAGAMENTOS
        pagamentos_brutos = Buscar_pagamento_por_operador(operador)
        
        if not pagamentos_brutos:
            log_debug("Nenhum pagamento encontrado")
            return retorno_vazio

        log_debug(f"Total de pagamentos brutos: {len(pagamentos_brutos)}")
        
        # CONVERTE PARA DATAFRAME
        df = pd.DataFrame(pagamentos_brutos)
        df['dtPgto'] = pd.to_datetime(df['dtPgto'])
        
        # ================================================================
        # FILTROS DE MÊS E ANO
        # ================================================================
        mes = int(mes) if mes else datetime.datetime.now().month
        ano = int(ano) if ano else datetime.datetime.now().year
        
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
        
        log_debug(f"Registros no mês atual ({mes}/{ano}): {len(df_mes_atual)}")
        log_debug(f"Registros no mês anterior ({mes_anterior}/{ano_anterior}): {len(df_mes_anterior)}")
        
        # ================================================================
        # FILTRO DE FASE (apenas para SEMEAR)
        # ================================================================
        if banco == 'SEMEAR' and fase and "todas" not in str(fase).lower():
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
        # CÁLCULO DO MÊS ANTERIOR
        # ================================================================
        df_mes_anterior_filtrado = df_mes_anterior.copy()
        if banco == 'SEMEAR' and 'faseAtraso' in df_mes_anterior_filtrado.columns:
            df_mes_anterior_filtrado = df_mes_anterior_filtrado[
                df_mes_anterior_filtrado['faseAtraso'] != 'Fora da fase'
            ]
        
        fat_anterior = df_mes_anterior_filtrado['valorTotal'].sum() if not df_mes_anterior_filtrado.empty else 0.0
        txt_fat_anterior = f"Mês anterior: R$ {fat_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        pgtos_anterior_qtd = len(df_mes_anterior_filtrado)
        txt_pgtos_anterior = f"Mês anterior: {pgtos_anterior_qtd:,}".replace(",", ".")
        
        # ================================================================
        # VERIFICA SE TEM DADOS
        # ================================================================
        if df_mes_atual.empty:
            log_debug("DataFrame vazio - retornando sem dados")
            return (texto_zero, texto_zero, "0", fig_blank, [], [], txt_fat_anterior, fig_blank, texto_zero, {"width": "0%"}, "0%", txt_pgtos_anterior)
        
        # ================================================================
        # CONVERTE PARA LISTA
        # ================================================================
        pagamentos_filtrados = df_mes_atual.to_dict('records')
        
        # ================================================================
        # CALCULA INDICADORES (KPIs)
        # ================================================================
        indicadores = calcular_indicadores_operador(pagamentos_filtrados, banco=banco)
        
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
                data_meta = meta.get('data')
                if data_meta and hasattr(data_meta, 'year'):
                    if data_meta.year == ano and data_meta.month == mes:
                        meta_valor = meta.get('meta100', 0)
                        break

        percentual_meta = (faturamento / meta_valor) * 100 if meta_valor > 0 else 0
        txt_meta_objetivo = f"R$ {meta_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # BARRA DE PROGRESSO
        if percentual_meta >= 100:
            cor_barra = "#10B981"
        elif percentual_meta >= 70:
            cor_barra = "#f59e0b"
        else:
            cor_barra = "#ef4444"

        estilo_barra = {
            "width": f"{min(percentual_meta, 100)}%",
            "backgroundColor": cor_barra,
            "height": "6px",
            "borderRadius": "4px",
            "transition": "width 0.5s"
        }
        
        # ================================================================
        # GRÁFICO 1: EVOLUÇÃO DIÁRIA (CORRIGIDO - sem scroll para dias negativos/33)
        # ================================================================
        df_grafico = calcular_faturamento_por_dia(pagamentos_filtrados, banco=banco)
        
        if not df_grafico.empty:
            # Extrai apenas o dia do mês para o eixo X
            df_grafico['dia'] = pd.to_datetime(df_grafico['data']).dt.day
            
            # Pega os dias que realmente existem no mês
            dias_existentes = sorted(df_grafico['dia'].unique())
            primeiro_dia = min(dias_existentes) if dias_existentes else 1
            ultimo_dia = max(dias_existentes) if dias_existentes else 31
            
            figura_evolucao = px.line(
                df_grafico, 
                x='dia', 
                y='total',
                markers=True
            )
            figura_evolucao.update_traces(
                line_color='#7e3d97', 
                marker_color='#7e3d97',
                marker_size=8,
                line_width=3
            )
            
            figura_evolucao.update_layout(
                xaxis=dict(
                    title="",
                    tickmode='linear',
                    tick0=primeiro_dia,
                    dtick=1,
                    range=[primeiro_dia - 0.5, ultimo_dia + 0.5],  # LIMITA O SCROLL
                    showgrid=True,
                    gridcolor='#E5E7EB',
                    tickangle=0
                ),
                yaxis=dict(
                    title="Recebimento (R$)",
                    showgrid=True,
                    gridcolor='#E5E7EB'
                ),
                margin=dict(b=40, t=50, l=60, r=40)  # Margens consistentes
            )
            
            figura_evolucao = aplicar_estilo_padrao(figura_evolucao, f"Evolução Diária - {mes}/{ano}", 400)
        else:
            figura_evolucao = fig_blank

        # ================================================================
        # GRÁFICO 2: PAGAMENTOS POR FASE (CORRIGIDO - sem corte dos rótulos)
        # ================================================================
        if banco == 'SEMEAR':
            df_fases = calcular_pagamentos_por_fase(pagamentos_filtrados, banco=banco)
            if not df_fases.empty:
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
                    textposition='outside',
                    textfont_size=10
                )
                figura_fase.update_layout(
                    xaxis=dict(
                        title="",
                        tickangle=-45,
                        tickfont_size=9
                    ),
                    yaxis=dict(
                        title="Recebimento (R$)",
                        showgrid=True,
                        gridcolor='#E5E7EB'
                    ),
                    uniformtext_minsize=8,
                    uniformtext_mode='hide',
                    margin=dict(b=120, t=50, l=60, r=40)  # AUMENTADO b=120 para não cortar
                )
                figura_fase = aplicar_estilo_padrao(figura_fase, "Pagamentos por Fase", 400)
            else:
                figura_fase = fig_blank
        else:
            # AGORACRED - gráfico informativo
            figura_fase = go.Figure().update_layout(
                title=dict(
                    text="<b>Pagamentos por Fase</b>",
                    font=dict(color='#111827', size=14),
                    x=0,
                    xanchor='left'
                ),
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                annotations=[dict(
                    text="📊 Gráfico por fase não disponível para AGORACRED",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=14, color='#9ca3af')
                )]
            )
        
        # ================================================================
        # TABELA DE PAGAMENTOS
        # ================================================================
        colunas_visiveis = ['dtPgto', 'contrato', 'cliente', 'valorTotal']
        
        if banco == 'SEMEAR':
            if 'faseAtraso' in df_mes_atual.columns:
                colunas_visiveis.append('faseAtraso')
            elif 'fase' in df_mes_atual.columns:
                colunas_visiveis.append('fase')
        
        colunas_existentes = [c for c in colunas_visiveis if c in df_mes_atual.columns]
        df_tabela = df_mes_atual[colunas_existentes].copy()
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
        
        log_debug(f"✅ FINALIZADO - {total} pagamentos | Banco: {banco} | Mês: {mes}/{ano}")
        
        return (
            txt_faturamento,
            txt_ticket,
            txt_total,
            figura_evolucao,
            dados_tabela,
            colunas_tabela,
            txt_fat_anterior,
            figura_fase,
            txt_meta_objetivo,
            estilo_barra,
            f"{percentual_meta:.1f}% da meta",
            txt_pgtos_anterior,
        )

    # ================================================================
    # TABELA DE PERFORMANCE DO OPERADOR
    # ================================================================
    @app.callback(
        [
            Output('tabela-performance', 'data'),
            Output('tabela-performance', 'columns'),
            Output('info-dias-performance', 'children'),
        ],
        [
            Input('filtro-mes', 'value'),
            Input('filtro-ano', 'value')
        ],
        [State('login-success-store', 'data')]
    )
    def atualizar_tabela_performance(mes, ano, dados_operador):
        """Atualiza tabela de performance com os filtros corretos"""
        
        if not dados_operador:
            return [], [], ""
        
        login = dados_operador.get('login')
        if not login:
            return [], [], ""
        
        operador = Buscar_login(login)
        if not operador:
            return [], [], ""
        
        banco = operador.get('banco', 'SEMEAR')
        pagamentos = Buscar_pagamento_por_operador(operador)
        metas = buscar_metas_por_operador(operador)
        
        if not pagamentos:
            return [], [{"name": "Sem dados", "id": "sem_dados"}], ""
        
        mes = int(mes) if mes else datetime.datetime.now().month
        ano = int(ano) if ano else datetime.datetime.now().year
        
        perf = calcular_performance_operador(
            pagamentos=pagamentos,
            metas=metas,
            ano=ano,
            mes=mes,
            login=login,
            banco=banco
        )
        
        txt_dias = f"📅 Dias trabalhados: {perf['dias_trabalhados']}  |  ⏳ Dias úteis restantes: {perf['dias_restantes']}  |  📆 Total dias úteis: {perf['total_dias_uteis']}"
        
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
        }]
        
        colunas = [
            {"name": "Login", "id": "login"},
            {"name": "Turno", "id": "turno"},
            {"name": "Faturamento", "id": "faturamento"},
            {"name": "Feito/Dia", "id": "feito_diario"},
            {"name": "Meta", "id": "meta"},
            {"name": "Meta/Dia", "id": "meta_diaria"},
            {"name": "% Meta", "id": "atingido_meta"},
            {"name": "Falta 70%", "id": "falta_70"},
            {"name": "Falta 80%", "id": "falta_80"},
            {"name": "Falta 90%", "id": "falta_90"},
            {"name": "Falta 100%", "id": "falta_100"},
            {"name": "Ranking", "id": "meta_ranking"},
            {"name": "Projeção (R$)", "id": "projecao"},
            {"name": "Proj. %", "id": "projecao_percentual"},
        ]
        
        return dados_tabela, colunas, txt_dias
"""
CALLBACKS DOS GRÁFICOS E TABELAS - DASHBOARD
=============================================
CORRIGIDO: Filtros de mês funcionando, diferencia ADMIN/OPERADOR
PADRONIZADO: Gráficos com mesmo estilo, títulos, tamanhos
CORRIGIDO: Atualização automática a cada 5 minutos (dcc.Interval)
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime
import os
import re
import dash
from dash.dependencies import Input, Output, State
from dash import no_update, html

from src.services.db_service import (
    Buscar_login,
    Buscar_pagamento_por_operador,
    buscar_metas_por_operador,
    buscar_tma_operador,
)
from src.services.analytics_service import (
    calcular_indicadores_operador, 
    calcular_faturamento_por_dia, 
    calcular_pagamentos_por_fase,
    calcular_performance_operador
)
from src.dashboard.components.filtros import aplicar_filtro_data, obter_mes_ano_do_range

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

retorno_vazio = (texto_zero, texto_zero, "0", fig_blank, [], [], texto_zero, fig_blank, texto_zero, {"width": "0%"}, "0%", texto_zero, {"display": "none"}, "—", "Sem dados de ligações", "0", "Ritmo: —", "0,0", "Clientes únicos: —")


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
            Output('badge-data-range', 'style'),
            Output('kpi-tma-valor', 'children'),
            Output('kpi-tma-subtexto', 'children'),
            Output('kpi-tma-acionamentos', 'children'),
            Output('kpi-tma-ult-acionamento', 'children'),
            Output('kpi-tma-reacionamento', 'children'),
            Output('kpi-tma-clientes', 'children'),
        ],
        [
            Input('url', 'pathname'),
            Input('interval-component', 'n_intervals'),  # ← ADICIONADO! Atualização automática a cada 5 minutos
            Input('filtro-mes', 'value'),
            Input('filtro-ano', 'value'),
            Input('filtro-texto-busca', 'value'),
            Input('filtro-fase', 'value'),
            Input('filtro-data-range', 'start_date'),
            Input('filtro-data-range', 'end_date')
        ],
        [
            State('login-success-store', 'data')
        ]
    )
    def atualizar_dashboard(pathname, n_interval, mes, ano, texto_busca, fase, data_inicio, data_fim, dados_operador):
        """
        CORRIGIDO: 
        - Adicionado Input('interval-component', 'n_intervals') para atualização automática
        - Filtro de mês aplicado CORRETAMENTE
        - Gráficos padronizados com mesmo estilo
        """
        try:
            return _atualizar_dashboard_interno(pathname, n_interval, mes, ano, texto_busca, fase, data_inicio, data_fim, dados_operador)
        except Exception as e:
            import traceback
            log_debug(f"[ERRO CRÍTICO] Callback atualizar_dashboard falhou: {e}\n{traceback.format_exc()}")
            return retorno_vazio

    def _atualizar_dashboard_interno(pathname, n_interval, mes, ano, texto_busca, fase, data_inicio, data_fim, dados_operador):
        """Lógica interna do dashboard, separada para facilitar captura de erros."""
        
        # VERIFICA SE ESTÁ NO DASHBOARD
        if pathname != '/dashboard':
            return [no_update] * 19
            
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
        
        # Log para debug da atualização automática
        if n_interval and n_interval > 0:
            log_debug(f"🔄 ATUALIZAÇÃO AUTOMÁTICA #{n_interval} - Operador: {login} | Banco: {banco} | {datetime.datetime.now().strftime('%H:%M:%S')}")
        else:
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
        # FILTROS DE MÊS, ANO E DATA-RANGE
        # ================================================================
        df_mes_atual, usando_range, label_periodo = aplicar_filtro_data(df, mes, ano, data_inicio, data_fim)
        
        # Lógica para mês anterior
        mes_base = int(mes) if mes else datetime.datetime.now().month
        ano_base = int(ano) if ano else datetime.datetime.now().year
        
        if mes_base == 1:
            mes_anterior = 12
            ano_anterior = ano_base - 1
        else:
            mes_anterior = mes_base - 1
            ano_anterior = ano_base
        
        df_mes_anterior = df[
            (df['dtPgto'].dt.month == mes_anterior) & 
            (df['dtPgto'].dt.year == ano_anterior)
        ].copy()
        
        log_debug(f"Registros no período selecionado ({label_periodo}): {len(df_mes_atual)}")
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

        # ── Variação de faturamento (atual vs anterior) ──────────────────
        # Se o filtro for um date-range com data_fim, compara até o mesmo dia do mês anterior
        if data_inicio and data_fim:
            try:
                dt_fim_range = pd.to_datetime(data_fim)
                # Compara até o mesmo dia do mês anterior
                dt_inicio_ant = pd.to_datetime(data_inicio) - pd.DateOffset(months=1)
                dt_fim_ant    = dt_fim_range - pd.DateOffset(months=1)
                df_ant_range = df[
                    (df['dtPgto'] >= dt_inicio_ant) &
                    (df['dtPgto'] <= dt_fim_ant + pd.Timedelta(hours=23, minutes=59, seconds=59))
                ].copy()
                if banco == 'SEMEAR' and 'faseAtraso' in df_ant_range.columns:
                    df_ant_range = df_ant_range[df_ant_range['faseAtraso'] != 'Fora da fase']
                fat_anterior = float(df_ant_range['valorTotal'].sum()) if not df_ant_range.empty else 0.0
            except Exception:
                pass

        fat_anterior_brl = f"R$ {fat_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if fat_anterior > 0:
            variacao_pct = ((0 - fat_anterior) / fat_anterior) * 100  # será substituído após calcular faturamento atual
        else:
            variacao_pct = None
        txt_fat_anterior = f"Mês anterior: {fat_anterior_brl}"  # provisório
        
        pgtos_anterior_qtd = len(df_mes_anterior_filtrado)
        txt_pgtos_anterior = f"Mês anterior: {pgtos_anterior_qtd:,}".replace(",", ".")
        
        # ================================================================
        # VERIFICA SE TEM DADOS
        # ================================================================
        if df_mes_atual.empty:
            log_debug("DataFrame vazio - retornando sem dados")
            badge_style = {"display": "inline-flex"} if usando_range else {"display": "none"}
            return (texto_zero, texto_zero, "0", fig_blank, [], [], txt_fat_anterior, fig_blank, texto_zero, {"width": "0%"}, "0%", txt_pgtos_anterior, badge_style,
                    "—", "Sem ligações no período", "0", "Últ. Acion.: —", "—", "Clientes únicos: —")
        
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
        # BUSCA A META DO MÊS (trazida para cima para usar na variação/storytelling)
        # ================================================================
        metas = buscar_metas_por_operador(operador)
        meta_valor = 0.0

        if metas:
            mes_meta, ano_meta = obter_mes_ano_do_range(data_inicio, data_fim) or (int(mes) if mes else datetime.datetime.now().month, int(ano) if ano else datetime.datetime.now().year)
            for meta in metas:
                data_meta = meta.get('data')
                if data_meta and hasattr(data_meta, 'year'):
                    if data_meta.year == ano_meta and data_meta.month == mes_meta:
                        meta_valor = meta.get('meta100', 0)
                        break

        # ── Recalcula variação com o faturamento real e constrói o storytelling do card ──
        fat_ant_brl_fmt = f"R$ {fat_anterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if fat_anterior > 0:
            variacao_pct = ((faturamento - fat_anterior) / fat_anterior) * 100
            seta = "↑" if variacao_pct >= 0 else "↓"
            cor_var = "#16a34a" if variacao_pct >= 0 else "#dc2626"
            bg_var = "#dcfce7" if variacao_pct >= 0 else "#fee2e2"
            var_badge = html.Span(
                f"{seta} {abs(variacao_pct):.1f}%",
                style={
                    "color": cor_var, "backgroundColor": bg_var,
                    "padding": "2px 6px", "borderRadius": "4px", "fontWeight": "700", "fontSize": "11px",
                    "marginLeft": "6px", "display": "inline-block"
                }
            )
        else:
            var_badge = html.Span("—", style={"marginLeft": "6px"})

        # Cálculo da diferença da meta
        falta_meta = max(0.0, meta_valor - faturamento)
        falta_meta_pct = ((meta_valor - faturamento) / meta_valor * 100) if meta_valor > 0 else 0.0
        
        if falta_meta > 0:
            falta_comp = html.Div([
                html.Span(f"Falta: R$ {falta_meta:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), style={"fontWeight": "700", "color": "var(--text-main)", "fontSize": "12px"}),
                html.Span(
                    f"{falta_meta_pct:.1f}% abaixo",
                    style={
                        "color": "#d97706", "backgroundColor": "#fef3c7",
                        "padding": "2px 6px", "borderRadius": "4px", "fontWeight": "700", "fontSize": "11px",
                        "marginLeft": "6px", "display": "inline-block"
                    }
                )
            ])
        else:
            falta_comp = html.Div(
                "Meta Atingida! 🎉",
                style={"fontWeight": "700", "color": "#16a34a", "fontSize": "12px"}
            )

        # Container do subtexto do faturamento (storytelling em 2 colunas)
        txt_fat_anterior = html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "width": "100%", "marginTop": "2px"},
            children=[
                html.Div([
                    html.Span("Mês Anterior", style={"fontSize": "11px", "color": "var(--text-muted)", "display": "block", "marginBottom": "2px"}),
                    html.Div([
                        html.Span(fat_ant_brl_fmt, style={"fontWeight": "700", "color": "var(--text-main)", "fontSize": "12px"}),
                        var_badge
                    ], style={"display": "flex", "alignItems": "center"})
                ]),
                html.Div([
                    html.Span("Diferença da Meta", style={"fontSize": "11px", "color": "var(--text-muted)", "display": "block", "marginBottom": "2px", "textAlign": "right"}),
                    falta_comp
                ], style={"textAlign": "right"})
            ]
        )

        percentual_meta = (faturamento / meta_valor) * 100 if meta_valor > 0 else 0
        txt_meta_objetivo = f"R$ {meta_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # BARRA DE PROGRESSO E TEXTO INFORMATIVO
        if percentual_meta >= 100:
            cor_barra = "#10B981"
            txt_percentual_meta = html.Span(f"{percentual_meta:.1f}% da meta", style={"color": cor_barra, "fontWeight": "600"})
        else:
            if percentual_meta >= 70:
                cor_barra = "#f59e0b"
            else:
                cor_barra = "#ef4444"
            
            falta_valor = meta_valor - faturamento
            if falta_valor > 0:
                falta_brl = f"R$ {falta_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                txt_percentual_meta = html.Span([
                    html.Span(f"{percentual_meta:.1f}% da meta", style={"color": cor_barra, "fontWeight": "600"}),
                    html.Span(f" (Falta {falta_brl})", style={"color": "var(--text-muted)", "fontSize": "11px", "marginLeft": "4px"})
                ])
            else:
                txt_percentual_meta = html.Span(f"{percentual_meta:.1f}% da meta", style={"color": cor_barra, "fontWeight": "600"})

        estilo_barra = {
            "width": f"{min(percentual_meta, 100)}%",
            "backgroundColor": cor_barra,
            "height": "6px",
            "borderRadius": "4px",
            "transition": "width 0.5s"
        }
        
        # ================================================================
        # GRÁFICO 1: EVOLUÇÃO DIÁRIA (sem título duplicado)
        # ================================================================
        df_grafico = calcular_faturamento_por_dia(pagamentos_filtrados, banco=banco)
        
        if not df_grafico.empty:
            df_grafico['dia'] = pd.to_datetime(df_grafico['data']).dt.day
            
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
                title="",  # Remove título duplicado
                xaxis=dict(
                    title="",
                    tickmode='linear',
                    tick0=primeiro_dia,
                    dtick=1,
                    range=[primeiro_dia - 0.5, ultimo_dia + 0.5],
                    showgrid=True,
                    gridcolor='#E5E7EB',
                    tickangle=0
                ),
                yaxis=dict(
                    title="Recebimento (R$)",
                    showgrid=True,
                    gridcolor='#E5E7EB'
                ),
                margin=dict(b=40, t=50, l=60, r=40),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
        else:
            figura_evolucao = fig_blank

        # ================================================================
        # GRÁFICO 2: PAGAMENTOS POR FASE (sem título duplicado)
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
                    title="",  # Remove título duplicado
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
                    margin=dict(b=120, t=50, l=60, r=40),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
            else:
                figura_fase = fig_blank
        else:
            # AGORACRED - gráfico informativo
            figura_fase = go.Figure().update_layout(
                title="",  # Remove título duplicado
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
        
        log_debug(f"✅ FINALIZADO - {total} pagamentos | Banco: {banco} | Período: {label_periodo}")

        badge_style = {"display": "inline-flex"} if usando_range else {"display": "none"}

        # ================================================================
        # BUSCA DADOS DE TMA DO OPERADOR (Acionamento por Operadores)
        # ================================================================
        mes_tma  = int(mes) if mes else datetime.datetime.now().month
        ano_tma  = int(ano) if ano else datetime.datetime.now().year
        tma_dados = buscar_tma_operador(login=login, banco=banco, anoatual=ano_tma, mesnum=mes_tma)

        if tma_dados:
            tma_valor         = str(tma_dados.get('tempoMedio', '—'))  # Ex: "00:01:46"
            tempo_total_seg   = int(tma_dados.get('tempoTotalSegundos', 0))
            tma_h             = tempo_total_seg // 3600
            tma_m             = (tempo_total_seg % 3600) // 60
            tma_subtexto      = f"Falado no mês: {tma_h}h {tma_m:02d}min"

            qtde_acion        = int(tma_dados.get('qtdeAcionamentos', 0))
            tma_acionamentos  = str(qtde_acion)

            # Último acionamento formatado
            ult_acion_raw = tma_dados.get('ultimoAcionamento')
            if ult_acion_raw and str(ult_acion_raw).strip() not in ('', '—', 'nan', 'None'):
                try:
                    import pandas as _pd
                    dt_ult = _pd.to_datetime(ult_acion_raw)
                    tma_ult_acionamento = f"Últ. Acion.: {dt_ult.strftime('%d/%m/%Y %H:%M')}"
                except Exception:
                    tma_ult_acionamento = f"Últ. Acion.: {ult_acion_raw}"
            else:
                tma_ult_acionamento = "Últ. Acion.: —"

            taxa              = float(tma_dados.get('taxaAcionamentoCliente', 0))
            qtde_clientes     = int(tma_dados.get('qtdeClientes', 0))
            tma_reacionamento = f"{taxa:.2f}x"
            tma_clientes      = f"Clientes únicos: {qtde_clientes}"
        else:
            tma_valor           = '—'
            tma_subtexto        = 'Sem dados de ligações'
            tma_acionamentos    = '0'
            tma_ult_acionamento = 'Últ. Acion.: —'
            tma_reacionamento   = '—'
            tma_clientes        = 'Clientes únicos: —'

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
            txt_percentual_meta,
            txt_pgtos_anterior,
            badge_style,
            tma_valor,
            tma_subtexto,
            tma_acionamentos,
            tma_ult_acionamento,
            tma_reacionamento,
            tma_clientes,
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
            Input('interval-component', 'n_intervals'),  # ← ADICIONADO! Também atualiza a tabela automaticamente
            Input('filtro-mes', 'value'),
            Input('filtro-ano', 'value'),
            Input('filtro-data-range', 'start_date'),
            Input('filtro-data-range', 'end_date')
        ],
        [State('login-success-store', 'data')]
    )
    def atualizar_tabela_performance(n_interval, mes, ano, data_inicio, data_fim, dados_operador):
        """Atualiza tabela de performance com os filtros corretos e atualização automática"""
        
        if not dados_operador:
            return [], [], ""
        
        login = dados_operador.get('login')
        if not login:
            return [], [], ""
        
        operador = Buscar_login(login)
        if not operador:
            return [], [], ""
        
        # Log para debug
        if n_interval and n_interval > 0:
            log_debug(f"🔄 ATUALIZAÇÃO AUTOMÁTICA DA TABELA #{n_interval}")
        
        banco = operador.get('banco', 'SEMEAR')
        pagamentos = Buscar_pagamento_por_operador(operador)
        metas = buscar_metas_por_operador(operador)
        
        if not pagamentos:
            return [], [{"name": "Sem dados", "id": "sem_dados"}], ""
        
        mes_calc, ano_calc = obter_mes_ano_do_range(data_inicio, data_fim) or (
            int(mes) if mes else datetime.datetime.now().month,
            int(ano) if ano else datetime.datetime.now().year
        )

        # ── Filtra pagamentos pelo date range antes de calcular performance ──
        # Sem isso, calcular_performance_operador ignora o range e usa o mês inteiro
        pagamentos_para_perf = pagamentos
        if data_inicio and data_fim:
            try:
                df_tmp = pd.DataFrame(pagamentos)
                df_tmp['dtPgto'] = pd.to_datetime(df_tmp['dtPgto'])
                dt_ini = pd.to_datetime(data_inicio)
                dt_fim_dt = pd.to_datetime(data_fim) + pd.Timedelta(hours=23, minutes=59, seconds=59)
                df_tmp = df_tmp[(df_tmp['dtPgto'] >= dt_ini) & (df_tmp['dtPgto'] <= dt_fim_dt)]
                pagamentos_para_perf = df_tmp.to_dict('records')
                log_debug(f"[PERF] Date range ativo: {len(pagamentos_para_perf)} pagamentos de {data_inicio} até {data_fim}")
            except Exception as e:
                log_debug(f"[PERF] Erro ao filtrar por date range: {e}")

        perf = calcular_performance_operador(
            pagamentos=pagamentos_para_perf,
            metas=metas,
            ano=ano_calc,
            mes=mes_calc,
            login=login,
            banco=banco
        )
        
        txt_dias = f"📅 Dias trabalhados: {perf['dias_trabalhados']}  |  ⏳ Dias úteis restantes: {perf['dias_restantes']}  |  📆 Total dias úteis: {perf['total_dias_uteis']}"
        
        # Barra visual de % meta
        val_perc = float(perf.get("atingido_meta", 0))
        bar_width = min(val_perc, 100)
        bar_color = "#10B981" if val_perc >= 100 else "#7e3d97"
        perc_html = (
            f'<div style="display:flex;align-items:center;gap:6px;min-width:110px;">'
            f'<div style="flex:1;background:#e5e7eb;border-radius:4px;height:8px;">'
            f'<div style="width:{bar_width:.0f}%;background:{bar_color};'
            f'height:8px;border-radius:4px;"></div></div>'
            f'<span style="white-space:nowrap;font-weight:700;color:{bar_color};'
            f'font-size:12px;">{val_perc:.1f}%</span></div>'
        )

        dados_tabela = [{
            "login": perf['login'],
            "turno": operador.get('turno', ''),
            "faturamento": f"R$ {perf['faturamento']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "feito_diario": f"R$ {perf['feito_diario']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "meta": f"R$ {perf['meta']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "meta_diaria": f"R$ {perf['meta_diaria']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "atingido_meta": perc_html,
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
            {"name": "% Meta", "id": "atingido_meta", "presentation": "markdown"},
            {"name": "Falta 70%", "id": "falta_70"},
            {"name": "Falta 80%", "id": "falta_80"},
            {"name": "Falta 90%", "id": "falta_90"},
            {"name": "Falta 100%", "id": "falta_100"},
            {"name": "Ranking", "id": "meta_ranking"},
            {"name": "Projeção (R$)", "id": "projecao"},
            {"name": "Proj. %", "id": "projecao_percentual"},
        ]
        
        return dados_tabela, colunas, txt_dias

    # ================================================================
    # TABELA MÊS A MÊS - DASHBOARD
    # ================================================================
    @app.callback(
        [
            Output("tabela-mes-mes-dashboard", "data"),
            Output("tabela-mes-mes-dashboard", "columns"),
        ],
        [
            Input('interval-component', 'n_intervals'),
            Input('filtro-ano', 'value'),
            Input('filtro-data-range', 'start_date'),
            Input('filtro-data-range', 'end_date')
        ],
        [State('login-success-store', 'data')]
    )
    def atualizar_tabela_mes_mes_dashboard(n, ano, data_inicio, data_fim, dados_operador):
        """Atualiza a tabela Mês a Mês do dashboard do operador."""
        if not dados_operador:
            return [], []

        login = dados_operador.get('login')
        if not login:
            return [], []

        operador = Buscar_login(login)
        if not operador:
            return [], []

        banco = operador.get('banco', 'SEMEAR')
        pagamentos = Buscar_pagamento_por_operador(operador)
        if not pagamentos:
            return [], []

        metas = buscar_metas_por_operador(operador)
        metas_dict = {}
        for meta in (metas or []):
            md = meta.get("data")
            if md:
                if hasattr(md, "year"):
                    metas_dict[(md.year, md.month)] = float(meta.get("meta100") or 0)
                elif isinstance(md, str):
                    mdt = pd.to_datetime(md, errors="coerce")
                    if not pd.isna(mdt):
                        metas_dict[(mdt.year, mdt.month)] = float(meta.get("meta100") or 0)

        df = pd.DataFrame(pagamentos)
        df["dtPgto"] = pd.to_datetime(df["dtPgto"], errors="coerce")
        df["valorTotal"] = pd.to_numeric(df["valorTotal"], errors="coerce").fillna(0.0)
        df = df.dropna(subset=["dtPgto"])

        _, ano_int = obter_mes_ano_do_range(data_inicio, data_fim) or (
            None,
            int(ano) if ano else datetime.datetime.today().year,
        )

        df_ano = df[df["dtPgto"].dt.year == ano_int]

        meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                       "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        resultado = []

        for mes in range(1, 13):
            meta = metas_dict.get((ano_int, mes), 0.0)
            if meta <= 0:
                continue

            df_mes = df_ano[df_ano["dtPgto"].dt.month == mes].copy()
            if banco == 'SEMEAR' and 'faseAtraso' in df_mes.columns:
                df_mes = df_mes[df_mes['faseAtraso'] != 'Fora da fase']

            faturamento = float(df_mes["valorTotal"].sum()) if not df_mes.empty else 0.0
            quantidade  = len(df_mes)
            percentual  = (faturamento / meta) * 100 if meta > 0 else 0.0
            bateu       = faturamento >= meta

            def _brl(v):
                return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            resultado.append({
                "mes":         mes,
                "nome_mes":    meses_nomes[mes - 1],
                "quantidade":  quantidade,
                "faturamento": _brl(faturamento),
                "meta":        _brl(meta),
                "percentual":  f"{percentual:.1f}%",
                "bateu":       "✅ Sim" if bateu else "❌ Não",
            })

        if not resultado:
            return [], []

        total_qtd = sum(r["quantidade"] for r in resultado)
        total_fat_raw = sum(
            float(r["faturamento"].replace("R$ ", "").replace(".", "").replace(",", "."))
            for r in resultado
        )

        def _brl(v):
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        resultado.append({
            "mes":         9999,
            "nome_mes":    "TOTAL",
            "quantidade":  total_qtd,
            "faturamento": _brl(total_fat_raw),
            "meta":        "-",
            "percentual":  "-",
            "bateu":       "-",
        })

        colunas = [
            {"name": "Mês",        "id": "nome_mes"},
            {"name": "Quantidade", "id": "quantidade"},
            {"name": "Faturamento","id": "faturamento"},
            {"name": "Meta",       "id": "meta"},
            {"name": "% Meta",     "id": "percentual"},
            {"name": "Bateu?",     "id": "bateu"},
        ]

        return resultado, colunas
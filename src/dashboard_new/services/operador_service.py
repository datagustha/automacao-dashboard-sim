"""
OPERADOR SERVICE - Lógica do Dashboard do Operador
===================================================
"""

# ================================================================
# IMPORTS CORRETOS (usando src.)
# ================================================================
from src.dashboard_new.services.admin_service import (
    _pagamento_no_mes,
    _pagamento_no_range,
    _pagamento_no_du_range,
    _mes_anterior
)
from src.services.db_service import (
    Buscar_pagamento_semear,
    Buscar_pagamento_agoracred,
    buscar_metas_semear,
    buscar_metas_agoracred,
    buscar_tma_operador,
    buscar_todos_operadores_por_banco
)
from src.services.analytics_service import (
    calcular_indicadores_operador,
    calcular_performance_operador,
    calcular_faturamento_por_dia,
    calcular_pagamentos_por_fase,
    calcular_tempo_de_casa,
    calcular_meta_diaria_por_dia,
    buscar_meta_do_mes,
    montar_comparativo_trimestre_du,
    montar_matriz_faixa_vs_mes
)
from datetime import datetime, date
from typing import Optional


def montar_dashboard_operador(
    operador: dict,
    ano: int = None,
    mes: int = None,
    faixa: str = 'todas',
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    du_inicio: Optional[int] = None,
    du_fim: Optional[int] = None
):
    """
    Monta o dashboard completo do operador com suporte a alertas, projeções e comparativos.
    """
    if not operador:
        return None
    
    if ano is None:
        ano = datetime.now().year
    if mes is None:
        mes = datetime.now().month
    
    banco = operador.get('banco', 'SEMEAR')
    login = operador.get('login')
    
    if banco == 'SEMEAR':
        pagamentos = Buscar_pagamento_semear(operador) or []
        metas = buscar_metas_semear(operador) or []
    elif banco == 'AGORACRED':
        pagamentos = Buscar_pagamento_agoracred(operador) or []
        metas = buscar_metas_agoracred(operador) or []
    else:
        pagamentos = Buscar_pagamento_semear(operador) or []
        if not pagamentos:
            pagamentos = Buscar_pagamento_agoracred(operador) or []
        metas = buscar_metas_semear(operador) or []
        if not metas:
            metas = buscar_metas_agoracred(operador) or []
    
    if pagamentos and not isinstance(pagamentos[0], dict):
        pagamentos = [p.__dict__ for p in pagamentos]
    
    # Filtra por faixa de atraso se fornecido (SEMEAR apenas)
    if banco == 'SEMEAR' and faixa and faixa != 'todas':
        if ',' in faixa:
            lista_faixas = [f.strip().lower() for f in faixa.split(',') if f.strip()]
            pagamentos = [p for p in pagamentos if (p.get('faseAtraso', '') or '').strip().lower() in lista_faixas]
        else:
            pagamentos = [p for p in pagamentos if (p.get('faseAtraso', '') or '').strip().lower() == faixa.strip().lower()]

    # Calcular ano/mês anterior
    ano_ant = ano
    mes_ant = mes - 1
    if mes == 1:
        ano_ant = ano - 1
        mes_ant = 12

    # Filtrar pagamentos
    pagamentos_mes = [p for p in pagamentos if _pagamento_no_mes(p, ano, mes)]
    # Aplica filtro de intervalo de datas
    if data_inicio or data_fim:
        pagamentos_mes = [p for p in pagamentos_mes if _pagamento_no_range(p, data_inicio, data_fim)]
    # Aplica filtro por dia útil (DU)
    if du_inicio is not None or du_fim is not None:
        pagamentos_mes = [p for p in pagamentos_mes if _pagamento_no_du_range(p, du_inicio, du_fim)]

    pagamentos_ant = [p for p in pagamentos if _pagamento_no_mes(p, ano_ant, mes_ant)]
    
    indicadores = calcular_indicadores_operador(pagamentos_mes, banco)
    indicadores_ant = calcular_indicadores_operador(pagamentos_ant, banco)
    
    tempo_casa = calcular_tempo_de_casa(operador.get('admissao'))
    


    pagamentos_fase = calcular_pagamentos_por_fase(pagamentos_mes, banco)
    pagamentos_fase_json = pagamentos_fase.to_dict('records') if not pagamentos_fase.empty else []
    
    # --- CÁLCULO DE RANKING DO OPERADOR NO BANCO ---
    todos_operadores = buscar_todos_operadores_por_banco(banco) or []
    faturamento_operadores = []

    for op in todos_operadores:
        op_login = op.get('login')
        if not op_login:
            continue

        if banco == 'SEMEAR':
            op_pagamentos = Buscar_pagamento_semear(op) or []
        else:
            op_pagamentos = Buscar_pagamento_agoracred(op) or []

        if op_pagamentos and not isinstance(op_pagamentos[0], dict):
            op_pagamentos = [p.__dict__ for p in op_pagamentos]

        # Filtra pagamentos do mês
        op_pagamentos_mes = [p for p in op_pagamentos if _pagamento_no_mes(p, ano, mes)]

        # Filtra por faixa de atraso se fornecido (SEMEAR apenas)
        if banco == 'SEMEAR':
            if faixa and faixa != 'todas':
                if ',' in faixa:
                    lista_faixas = [f.strip().lower() for f in faixa.split(',') if f.strip()]
                    op_pagamentos_mes = [p for p in op_pagamentos_mes if (p.get('faseAtraso', '') or '').strip().lower() in lista_faixas]
                else:
                    op_pagamentos_mes = [p for p in op_pagamentos_mes if (p.get('faseAtraso', '') or '').strip().lower() == faixa.strip().lower()]
            else:
                op_pagamentos_mes = [p for p in op_pagamentos_mes if p.get('faseAtraso') != "Fora da fase"]

        op_fat = sum(float(p.get('valorTotal', 0.0) or 0.0) for p in op_pagamentos_mes)
        faturamento_operadores.append({'login': op_login, 'faturamento': op_fat, 'pagamentos_mes': op_pagamentos_mes})

    # Ordena faturamentos em ordem decrescente
    faturamento_operadores.sort(key=lambda x: x['faturamento'], reverse=True)

    posicao_ranking = 1
    max_data_banco: Optional[datetime] = None

    for idx, item in enumerate(faturamento_operadores):
        if item['login'] == login:
            posicao_ranking = idx + 1
        for p in (item.get('pagamentos_mes') or []):
            dt_val = p.get('dtPgto')
            if not dt_val:
                continue
            try:
                dt_obj = datetime.strptime(str(dt_val)[:10], '%Y-%m-%d') if not isinstance(dt_val, datetime) else dt_val
                if max_data_banco is None or dt_obj > max_data_banco:
                    max_data_banco = dt_obj
            except Exception:
                pass

    # Formata a data máxima do banco para exibição no banner
    ultima_baixa_banco = max_data_banco.strftime('%d/%m/%Y') if max_data_banco else None

    # Faturamento diário truncado até a última baixa do banco e respeitando filtros
    performance_diaria = calcular_meta_diaria_por_dia(
        pagamentos=pagamentos,
        metas=metas,
        ano=ano,
        mes=mes,
        banco=banco,
        data_inicio=data_inicio,
        data_fim=data_fim,
        du_inicio=du_inicio,
        du_fim=du_fim,
        ultima_baixa_str=ultima_baixa_banco
    )

    # Performance individual
    performance = calcular_performance_operador(
        pagamentos=pagamentos,
        metas=metas,
        ano=ano,
        mes=mes,
        login=login,
        banco=banco,
        data_referencia_banco=max_data_banco
    )

    performance['ranking'] = f"{posicao_ranking}º"
    performance['turno'] = operador.get('turno', '-')
    performance['ultima_baixa_banco'] = ultima_baixa_banco

    # Se houver filtro ativo (DU, intervalo de datas ou faixa de atraso), atualiza os indicadores
    # da performance para que a tabela e os cards fiquem perfeitamente sincronizados
    if data_inicio or data_fim or du_inicio is not None or du_fim is not None or (banco == 'SEMEAR' and faixa and faixa != 'todas'):
        fat_filtrado = sum(float(p.get('valorTotal', 0.0) or 0.0) for p in pagamentos_mes)
        qtd_filtrada = len(pagamentos_mes)
        meta_val = performance.get('meta', 0.0)
        performance['faturamento'] = round(fat_filtrado, 2)
        performance['quantidade'] = qtd_filtrada
        performance['atingido_meta'] = round((fat_filtrado / meta_val * 100.0), 2) if meta_val > 0 else 0.0
        dias_trab = performance.get('dias_trabalhados', 1) or 1
        performance['feito_diario'] = round(fat_filtrado / dias_trab, 2)
        performance['falta_70'] = round(max(0.0, meta_val * 0.7 - fat_filtrado), 2)
        performance['falta_80'] = round(max(0.0, meta_val * 0.8 - fat_filtrado), 2)
        performance['falta_90'] = round(max(0.0, meta_val * 0.9 - fat_filtrado), 2)
        performance['falta_100'] = round(max(0.0, meta_val * 1.0 - fat_filtrado), 2)

    # --- CÁLCULO DE ALERTA DE DIAS SEM RECEBIMENTO (> 2 DIAS) ---
    # Usa a lista completa de pagamentos do mês (sem os filtros de DU/range de datas ativos)
    # para evitar alertas falsos de inatividade quando o usuário filtra um intervalo de DU específico.
    pagamentos_mes_full = [p for p in pagamentos if _pagamento_no_mes(p, ano, mes)]
    if banco == 'SEMEAR':
        pagamentos_mes_full = [p for p in pagamentos_mes_full if p.get('faseAtraso') != "Fora da fase"]

    max_dt_op: Optional[datetime] = None
    for p in pagamentos_mes_full:
        dt_v = p.get('dtPgto')
        if not dt_v:
            continue
        try:
            dt_o = datetime.strptime(str(dt_v)[:10], '%Y-%m-%d') if not isinstance(dt_v, datetime) else dt_v
            if max_dt_op is None or dt_o > max_dt_op:
                max_dt_op = dt_o
        except Exception:
            pass

    ref_date = max_data_banco or datetime.now()
    if max_dt_op:
        dias_sem_receber = (ref_date.date() - max_dt_op.date()).days
    else:
        dias_sem_receber = ref_date.day

    alerta_sem_pgto = dias_sem_receber >= 2
    performance['alerta_sem_pgto'] = alerta_sem_pgto
    performance['dias_sem_pgto'] = dias_sem_receber

    # --- CÁLCULO DE RESULTADO MÊS A MÊS (com Projeção) ---
    resultado_mes_a_mes = []
    nomes_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    hoje = datetime.now()

    for m in range(1, 13):
        pg_mes = [p for p in pagamentos if _pagamento_no_mes(p, ano, m)]
        if data_inicio or data_fim:
            pg_mes = [p for p in pg_mes if _pagamento_no_range(p, data_inicio, data_fim)]
        if du_inicio is not None or du_fim is not None:
            pg_mes = [p for p in pg_mes if _pagamento_no_du_range(p, du_inicio, du_fim)]
        if banco == 'SEMEAR':
            pg_mes = [p for p in pg_mes if p.get('faseAtraso') != "Fora da fase"]

        fat_m = sum(float(p.get('valorTotal', 0.0) or 0.0) for p in pg_mes)
        qtd_m = len(pg_mes)
        meta_m = buscar_meta_do_mes(metas, ano, m)
        perc_m = (fat_m / meta_m) * 100 if meta_m > 0 else 0.0
        bateu_m = "Sim" if (meta_m > 0 and fat_m >= meta_m) else "Não"

        # Projeção para o mês atual / aberto
        proj_m = fat_m
        proj_perc_m = perc_m
        if ano == hoje.year and m == hoje.month and performance.get('dias_trabalhados', 0) > 0:
            d_pass = performance['dias_trabalhados']
            d_tot = performance['total_dias_uteis']
            proj_m = (fat_m / d_pass) * d_tot if d_pass > 0 else fat_m
            proj_perc_m = (proj_m / meta_m) * 100 if meta_m > 0 else 0.0

        resultado_mes_a_mes.append({
            'mes': nomes_meses[m-1],
            'mes_num': m,
            'quantidade': qtd_m,
            'faturamento': round(fat_m, 2),
            'meta': round(meta_m, 2),
            'perc_meta': round(perc_m, 2),
            'projecao': round(proj_m, 2),
            'projecao_percentual': round(proj_perc_m, 2),
            'bateu': bateu_m
        })

    # Visão Trimestral por Dia Útil
    trimestre_du = montar_comparativo_trimestre_du(pagamentos, ano, mes, banco, data_inicio, data_fim, du_inicio, du_fim, ultima_baixa_banco)

    # Relatório Faixa de Atraso vs Mês (apenas SEMEAR)
    matriz_faixas_mes = montar_matriz_faixa_vs_mes(pagamentos, ano, banco, data_inicio, data_fim, du_inicio, du_fim) if banco == 'SEMEAR' else None


    # Formatar todos os pagamentos do mês selecionado para a paginação no frontend
    todos_pagamentos_mes = []
    for p in pagamentos_mes:
        p_copia = dict(p)
        dt = p_copia.get('dtPgto')
        if isinstance(dt, (datetime, date)):
            p_copia['dtPgto'] = dt.strftime('%Y-%m-%d')
        else:
            p_copia['dtPgto'] = str(dt)[:10]

        vct = p_copia.get('vctoParc')
        if isinstance(vct, (datetime, date)):
            p_copia['vctoParc'] = vct.strftime('%Y-%m-%d')
        else:
            p_copia['vctoParc'] = str(vct)[:10]

        todos_pagamentos_mes.append(p_copia)

    todos_pagamentos_mes.sort(key=lambda x: x.get('dtPgto', ''), reverse=True)

    tma = buscar_tma_operador(login, banco, ano, mes) or {}

    # Segmentação ≤360 dias / >360 dias (apenas SEMEAR)
    # Usa pagamentos do PERÍODO COMPLETO (data_inicio a data_fim), não só do mês atual
    faixas_operador = None
    if banco == 'SEMEAR':
        fases_ate_360   = {'Fase 10 a 30', 'Fase 31 a 60', 'Fase 61 a 90', 'Fase 91 a 120',
                           'Fase 121 a 180', 'Fase 181 a 240', 'Fase 241 a 360'}
        fases_acima_360 = {'Fase 361 a 720', 'Fase 721 a 1080', 'Fase 1081 a 1440',
                           'Fase 1441 a 1800', '> 1800'}

        # Para período com filtro de data, usa todos os pagamentos do range (multi-mês)
        if data_inicio or data_fim:
            pgtos_periodo = [p for p in pagamentos if _pagamento_no_range(p, data_inicio, data_fim)]
        else:
            pgtos_periodo = pagamentos_mes  # fallback: só mês atual

        pgtos_ate_360   = [p for p in pgtos_periodo if (p.get('faseAtraso') or '') in fases_ate_360]
        pgtos_acima_360 = [p for p in pgtos_periodo if (p.get('faseAtraso') or '') in fases_acima_360]

        total_ate   = sum(float(p.get('valorTotal', 0) or 0) for p in pgtos_ate_360)
        total_acima = sum(float(p.get('valorTotal', 0) or 0) for p in pgtos_acima_360)
        total_geral = total_ate + total_acima

        faixas_operador = {
            'ate_360': {
                'total':      round(total_ate, 2),
                'qtd':        len(pgtos_ate_360),
                'percentual': round(total_ate / total_geral * 100, 1) if total_geral > 0 else 0.0
            },
            'acima_360': {
                'total':      round(total_acima, 2),
                'qtd':        len(pgtos_acima_360),
                'percentual': round(total_acima / total_geral * 100, 1) if total_geral > 0 else 0.0
            }
        }

    return {
        'operador': operador,
        'indicadores': indicadores,
        'indicadores_anterior': indicadores_ant,
        'performance': performance,
        'tempo_casa': tempo_casa,
        'performance_diaria': performance_diaria,
        'faturamento_dia': performance_diaria,
        'pagamentos_fase': pagamentos_fase_json,
        'ultimos_pagamentos': todos_pagamentos_mes,
        'resultado_mes_a_mes': resultado_mes_a_mes,
        'trimestre_du': trimestre_du,
        'matriz_faixas_mes': matriz_faixas_mes,
        'faixas_operador': faixas_operador,
        'total_pagamentos': len(pagamentos_mes),
        'metas': metas,
        'tma': tma
    }


def montar_performance_operador(operador: dict, ano: int, mes: int):
    """
    Monta os dados de performance do operador.
    """
    if not operador:
        return None
    
    banco = operador.get('banco', 'SEMEAR')
    login = operador.get('login')
    
    if banco == 'SEMEAR':
        pagamentos = Buscar_pagamento_semear(operador) or []
        metas = buscar_metas_semear(operador) or []
    elif banco == 'AGORACRED':
        pagamentos = Buscar_pagamento_agoracred(operador) or []
        metas = buscar_metas_agoracred(operador) or []
    else:
        pagamentos = Buscar_pagamento_semear(operador) or []
        if not pagamentos:
            pagamentos = Buscar_pagamento_agoracred(operador) or []
        metas = buscar_metas_semear(operador) or []
        if not metas:
            metas = buscar_metas_agoracred(operador) or []
    
    if pagamentos and not isinstance(pagamentos[0], dict):
        pagamentos = [p.__dict__ for p in pagamentos]
        
    # --- CÁLCULO DE DATA MÁXIMA DO BANCO INTEIRO ---
    # Necessário para que a performance individual do operador reflita a
    # divisão do faturamento acumulado pela data máxima global de baixas do banco
    todos_operadores = buscar_todos_operadores_por_banco(banco) or []
    max_data_banco: Optional[datetime] = None

    for op in todos_operadores:
        if banco == 'SEMEAR':
            op_pagamentos = Buscar_pagamento_semear(op) or []
        else:
            op_pagamentos = Buscar_pagamento_agoracred(op) or []

        if op_pagamentos and not isinstance(op_pagamentos[0], dict):
            op_pagamentos = [p.__dict__ for p in op_pagamentos]

        # Filtra pagamentos do mês
        op_pagamentos_mes = [p for p in op_pagamentos if _pagamento_no_mes(p, ano, mes)]
        
        # Filtra fora da fase para o Semear
        if banco == 'SEMEAR':
            op_pagamentos_mes = [p for p in op_pagamentos_mes if p.get('faseAtraso') != "Fora da fase"]

        for p in op_pagamentos_mes:
            dt_val = p.get('dtPgto')
            if not dt_val:
                continue
            try:
                dt_obj = datetime.strptime(str(dt_val)[:10], '%Y-%m-%d') if not isinstance(dt_val, datetime) else dt_val
                if max_data_banco is None or dt_obj > max_data_banco:
                    max_data_banco = dt_obj
            except Exception:
                pass

    performance = calcular_performance_operador(
        pagamentos=pagamentos,
        metas=metas,
        ano=ano,
        mes=mes,
        login=login,
        banco=banco,
        data_referencia_banco=max_data_banco
    )
    
    performance_diaria = calcular_meta_diaria_por_dia(
        pagamentos=pagamentos,
        metas=metas,
        ano=ano,
        mes=mes,
        banco=banco
    )
    
    # Injeta a data máxima formatada na performance
    performance['ultima_baixa_banco'] = max_data_banco.strftime('%d/%m/%Y') if max_data_banco else None
    
    return {
        'performance': performance,
        'performance_diaria': performance_diaria
    }
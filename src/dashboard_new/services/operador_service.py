"""
OPERADOR SERVICE - Lógica do Dashboard do Operador
===================================================
"""

# ================================================================
# IMPORTS CORRETOS (usando src.)
# ================================================================
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
    buscar_meta_do_mes
)
from datetime import datetime, date
from typing import Optional

# ================================================================
# HELPERS DE DATA COMPARTILHADOS
# ================================================================

def _pagamento_no_mes(pagamento: dict, a: int, m: int) -> bool:
    """Verifica se um pagamento pertence ao mês/ano especificado."""
    data = pagamento.get('dtPgto')
    if not data:
        return False
    try:
        if isinstance(data, datetime):
            return data.year == a and data.month == m
        data_str = str(data)[:10]
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        return data_obj.year == a and data_obj.month == m
    except Exception:
        return False


def montar_dashboard_operador(operador: dict, ano: int = None, mes: int = None, faixa: str = 'todas'):
    """
    Monta o dashboard completo do operador.
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
    pagamentos_ant = [p for p in pagamentos if _pagamento_no_mes(p, ano_ant, mes_ant)]
    
    indicadores = calcular_indicadores_operador(pagamentos_mes, banco)
    indicadores_ant = calcular_indicadores_operador(pagamentos_ant, banco)
    
    tempo_casa = calcular_tempo_de_casa(operador.get('admissao'))
    
    performance_diaria = calcular_meta_diaria_por_dia(
        pagamentos=pagamentos,
        metas=metas,
        ano=ano,
        mes=mes,
        banco=banco
    )

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
                # Caso contrário, remove "Fora da fase" por padrão
                op_pagamentos_mes = [p for p in op_pagamentos_mes if p.get('faseAtraso') != "Fora da fase"]

        op_fat = sum(float(p.get('valorTotal', 0.0) or 0.0) for p in op_pagamentos_mes)
        # Guarda pagamentos_mes junto com o faturamento para calcular max_data_banco posteriormente
        faturamento_operadores.append({'login': op_login, 'faturamento': op_fat, 'pagamentos_mes': op_pagamentos_mes})

    # Ordena faturamentos em ordem decrescente
    faturamento_operadores.sort(key=lambda x: x['faturamento'], reverse=True)

    posicao_ranking = 1
    # Acumula a data máxima de pagamento do banco inteiro (não do operador individual)
    # Usada no banner "Baixas até dia X" na visão de performance do operador
    max_data_banco: Optional[datetime] = None

    for idx, item in enumerate(faturamento_operadores):
        if item['login'] == login:
            posicao_ranking = idx + 1
        # Coleta a data máxima de todos os operadores do banco
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

    # Agora sim calcula a performance baseada na data máxima de baixa do banco
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
    # Injeta a data máxima do banco na performance para uso no banner do frontend
    performance['ultima_baixa_banco'] = ultima_baixa_banco

    # --- CÁLCULO DE RESULTADO MÊS A MÊS ---
    resultado_mes_a_mes = []
    nomes_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    for m in range(1, 13):
        pg_mes = [p for p in pagamentos if _pagamento_no_mes(p, ano, m)]
        if banco == 'SEMEAR':
            pg_mes = [p for p in pg_mes if p.get('faseAtraso') != "Fora da fase"]

        fat_m = sum(float(p.get('valorTotal', 0.0) or 0.0) for p in pg_mes)
        qtd_m = len(pg_mes)
        meta_m = buscar_meta_do_mes(metas, ano, m)
        perc_m = (fat_m / meta_m) * 100 if meta_m > 0 else 0.0
        bateu_m = "Sim" if (meta_m > 0 and fat_m >= meta_m) else "Não"

        resultado_mes_a_mes.append({
            'mes': nomes_meses[m-1],
            'mes_num': m,
            'quantidade': qtd_m,
            'faturamento': round(fat_m, 2),
            'meta': round(meta_m, 2),
            'perc_meta': round(perc_m, 2),
            'bateu': bateu_m
        })

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

    # Ordenar pagamentos do mês do mais recente para o mais antigo
    todos_pagamentos_mes.sort(key=lambda x: x.get('dtPgto', ''), reverse=True)

    tma = buscar_tma_operador(login, banco, ano, mes) or {}

    return {
        'operador': operador,
        'indicadores': indicadores,
        'indicadores_anterior': indicadores_ant,
        'performance': performance,
        'tempo_casa': tempo_casa,
        'performance_diaria': performance_diaria,
        'faturamento_dia': performance_diaria,  # mantém compatibilidade legacy
        'pagamentos_fase': pagamentos_fase_json,
        'ultimos_pagamentos': todos_pagamentos_mes,
        'resultado_mes_a_mes': resultado_mes_a_mes,
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
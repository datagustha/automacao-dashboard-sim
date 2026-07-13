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
    buscar_tma_operador
)
from src.services.analytics_service import (
    calcular_indicadores_operador,
    calcular_performance_operador,
    calcular_faturamento_por_dia,
    calcular_pagamentos_por_fase,
    calcular_tempo_de_casa,
    calcular_meta_diaria_por_dia
)
from datetime import datetime


def montar_dashboard_operador(operador: dict, ano: int = None, mes: int = None):
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
    
    # Calcular ano/mês anterior
    ano_ant = ano
    mes_ant = mes - 1
    if mes == 1:
        ano_ant = ano - 1
        mes_ant = 12

    # Função interna para verificar data
    def _pagamento_no_mes(pagamento: dict, a: int, m: int) -> bool:
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

    # Filtrar pagamentos
    pagamentos_mes = [p for p in pagamentos if _pagamento_no_mes(p, ano, mes)]
    pagamentos_ant = [p for p in pagamentos if _pagamento_no_mes(p, ano_ant, mes_ant)]
    
    indicadores = calcular_indicadores_operador(pagamentos_mes, banco)
    indicadores_ant = calcular_indicadores_operador(pagamentos_ant, banco)
    
    performance = calcular_performance_operador(
        pagamentos=pagamentos,
        metas=metas,
        ano=ano,
        mes=mes,
        login=login,
        banco=banco
    )
    
    tempo_casa = calcular_tempo_de_casa(operador.get('admissao'))
    
    faturamento_dia = calcular_faturamento_por_dia(pagamentos_mes, banco)
    faturamento_dia_json = faturamento_dia.to_dict('records') if not faturamento_dia.empty else []
    
    pagamentos_fase = calcular_pagamentos_por_fase(pagamentos_mes, banco)
    pagamentos_fase_json = pagamentos_fase.to_dict('records') if not pagamentos_fase.empty else []
    
    ultimos_pagamentos = pagamentos_mes[:10] if pagamentos_mes else []
    
    for p in ultimos_pagamentos:
        if isinstance(p.get('dtPgto'), datetime):
            p['dtPgto'] = p['dtPgto'].strftime('%Y-%m-%d')
        if isinstance(p.get('vctoParc'), datetime):
            p['vctoParc'] = p['vctoParc'].strftime('%Y-%m-%d')
    
    tma = buscar_tma_operador(login, banco, ano, mes) or {}
    
    return {
        'operador': operador,
        'indicadores': indicadores,
        'indicadores_anterior': indicadores_ant,
        'performance': performance,
        'tempo_casa': tempo_casa,
        'faturamento_dia': faturamento_dia_json,
        'pagamentos_fase': pagamentos_fase_json,
        'ultimos_pagamentos': ultimos_pagamentos,
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
    
    performance = calcular_performance_operador(
        pagamentos=pagamentos,
        metas=metas,
        ano=ano,
        mes=mes,
        login=login,
        banco=banco
    )
    
    performance_diaria = calcular_meta_diaria_por_dia(
        pagamentos=pagamentos,
        metas=metas,
        ano=ano,
        mes=mes,
        banco=banco
    )
    
    return {
        'performance': performance,
        'performance_diaria': performance_diaria
    }
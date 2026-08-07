# -*- coding: utf-8 -*-
"""
ADMIN SERVICE - Lógica do Dashboard ADM
========================================
Este arquivo contém os serviços que processam as regras de negócio para o painel administrativo.
A lógica foi modularizada em funções menores de responsabilidade única para facilitar a manutenção
e testes, mantendo 100% de compatibilidade com o formato JSON esperado pelo frontend.
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, date
from calendar import monthrange

# Importações de funções de persistência e serviços
from src.services.db_service import (
    buscar_todos_operadores_por_banco,
    Buscar_pagamento_semear,
    Buscar_pagamento_agoracred,
    buscar_metas_semear,
    buscar_metas_agoracred,
    buscar_tma_operador,
    buscar_pagamentos_todos_operadores_por_banco
)
from src.services.analytics_service import (
    calcular_performance_operador,
    calcular_tempo_de_casa,
    montar_matriz_faixa_vs_mes
)

def buscar_dados_semear(atividade: str = 'ATIVO') -> List[Dict[str, Any]]:
    """
    Busca a lista de todos os operadores do banco SEMEAR.
    Filtra os operadores se atividade for 'ATIVO'.
    """
    operadores = buscar_todos_operadores_por_banco('SEMEAR') or []
    if atividade == 'ATIVO':
        operadores = [op for op in operadores if op.get('atividade', '').upper() == 'ATIVO']
    return operadores

def buscar_dados_agoracred(atividade: str = 'ATIVO') -> List[Dict[str, Any]]:
    """
    Busca a lista de todos os operadores do banco AGORACRED.
    Filtra os operadores se atividade for 'ATIVO'.
    """
    operadores = buscar_todos_operadores_por_banco('AGORACRED') or []
    if atividade == 'ATIVO':
        operadores = [op for op in operadores if op.get('atividade', '').upper() == 'ATIVO']
    return operadores

def _mes_anterior(ano: int, mes: int) -> Tuple[int, int]:
    """Retorna o ano e mês anterior ao fornecido."""
    if mes == 1:
        return ano - 1, 12
    return ano, mes - 1

def _parse_date_safe(data: Any) -> Optional[date]:
    if not data:
        return None
    if isinstance(data, datetime):
        return data.date()
    if isinstance(data, date):
        return data
    s = str(data)[:10].strip()
    try:
        if '-' in s:
            return datetime.strptime(s, '%Y-%m-%d').date()
        elif '/' in s:
            return datetime.strptime(s, '%d/%m/%Y').date()
    except Exception:
        pass
    return None


def _pagamento_no_mes(pagamento: dict, ano: int, mes: int) -> bool:
    """Verifica se um pagamento pertence ao ano e mês informados."""
    dt_obj = _parse_date_safe(pagamento.get('dtPgto'))
    if not dt_obj:
        return False
    return dt_obj.year == ano and dt_obj.month == mes


def _pagamento_no_range(pagamento: dict, data_inicio: Optional[str], data_fim: Optional[str]) -> bool:
    """Verifica se um pagamento está dentro do range de datas fornecido."""
    if not data_inicio and not data_fim:
        return True
    dt = _parse_date_safe(pagamento.get('dtPgto'))
    if not dt:
        return False
    try:
        if data_inicio:
            inicio = _parse_date_safe(data_inicio)
            if inicio and dt < inicio:
                return False
        if data_fim:
            fim = _parse_date_safe(data_fim)
            if fim and dt > fim:
                return False
        return True
    except Exception:
        return False


import holidays

def _pagamento_no_du_range(pagamento: dict, du_inicio: Optional[int], du_fim: Optional[int]) -> bool:
    """Verifica se um pagamento ocorreu dentro do intervalo de dias úteis (du_inicio a du_fim) do seu mês."""
    if du_inicio is None and du_fim is None:
        return True
    dt_obj = _parse_date_safe(pagamento.get('dtPgto'))
    if not dt_obj:
        return False
    try:
        if dt_obj.weekday() >= 5:
            return False

        a, m = dt_obj.year, dt_obj.month
        total_dias = monthrange(a, m)[1]
        feriados_br = holidays.country_holidays('BR', years=a)
        from dateutil.easter import easter
        from datetime import timedelta as _td
        feriados_br.update({easter(a) + _td(days=60): "Corpus Christi"})

        du_rank = 0
        for d in range(1, total_dias + 1):
            cur_dt = date(a, m, d)
            if cur_dt.weekday() < 5 and cur_dt not in feriados_br:
                du_rank += 1
                if cur_dt == dt_obj:
                    ini = du_inicio or 1
                    fim = du_fim or 99
                    return ini <= du_rank <= fim
        return False
    except Exception:
        return False


def montar_ranking(
    operadores: List[Dict[str, Any]],
    banco: str,
    ano: int,
    mes: int,
    operador_filtro: str = 'TODOS',
    contrato_filtro: str = '',
    faixa_filtro: str = 'todas',
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    du_inicio: Optional[int] = None,
    du_fim: Optional[int] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], int, float, int, float, float, float, Optional[str]]:
    """
    Calcula a performance de cada operador, aplica os filtros de busca e
    monta o ranking ordenado de faturamento/atingimento de metas.

    Retorna: (ranking_list, faixas_acumuladas, ops_atual, fat_atual, ops_anterior, fat_anterior, ticket_medio, ticket_medio_ant)

    FEITO/DIA: usa a data máxima de pagamento do banco inteiro (não do operador individual),
    pois as baixas bancárias têm delay e podem não ser uniformes entre operadores.
    """
    ranking_list = []
    total_faturamento = 0.0
    total_operacoes = 0
    total_faturamento_ant = 0.0
    total_operacoes_ant = 0
    faixas_acumuladas = {}

    # Acumula a data máxima de pagamento do banco inteiro no período
    # Será usada como divisor do feito/dia para todos os operadores
    max_data_banco: Optional[datetime] = None

    ano_ant, mes_ant = _mes_anterior(ano, mes)

    # Verifica se tem filtro de range de data ativo
    tem_range = bool(data_inicio or data_fim)

    # ---------------------------------------------------------------
    # PRÉ-PASSAGEM: calcula a data máxima de pagamento (última baixa) do
    # BANCO INTEIRO, sempre olhando TODOS os operadores do banco.
    #
    # IMPORTANTE: isso é feito ANTES e INDEPENDENTE do filtro de operador/
    # contrato/faixa. Se calculássemos essa data dentro do loop filtrado
    # abaixo, ao selecionar um operador específico a "última baixa" passaria
    # a refletir só aquele operador (ex: baixas até dia 22), quando o banco
    # inteiro já recebeu baixas até um dia mais recente (ex: dia 24). Isso
    # cortava a evolução diária, a visão por banco e o filtro por operador
    # no dia errado.
    # ---------------------------------------------------------------
    for op_global in operadores:
        if banco == 'SEMEAR':
            pagamentos_global = Buscar_pagamento_semear(op_global) or []
        else:
            pagamentos_global = Buscar_pagamento_agoracred(op_global) or []

        if pagamentos_global and not isinstance(pagamentos_global[0], dict):
            pagamentos_global = [p.__dict__ for p in pagamentos_global]

        if tem_range:
            pagamentos_periodo_global = [p for p in pagamentos_global if _pagamento_no_range(p, data_inicio, data_fim)]
        else:
            pagamentos_periodo_global = [p for p in pagamentos_global if _pagamento_no_mes(p, ano, mes)]

        if du_inicio is not None or du_fim is not None:
            pagamentos_periodo_global = [p for p in pagamentos_periodo_global if _pagamento_no_du_range(p, du_inicio, du_fim)]

        for p in pagamentos_periodo_global:
            dt_val = p.get('dtPgto')
            if not dt_val:
                continue
            try:
                dt_obj = dt_val if isinstance(dt_val, datetime) else datetime.strptime(str(dt_val)[:10], '%Y-%m-%d')
                if max_data_banco is None or dt_obj > max_data_banco:
                    max_data_banco = dt_obj
            except Exception:
                pass

    # ---------------------------------------------------------------
    # PRIMEIRA PASSAGEM: coleta pagamentos e performance de cada operador
    # (max_data_banco já está definido acima e NÃO é mais recalculado aqui)
    # ---------------------------------------------------------------
    # Lista temporária para recalcular feito_dia após saber o max_data_banco
    dados_temporarios = []

    for op in operadores:
        login = op.get('login')

        # Filtra pelo operador específico caso seja solicitado (suporta múltiplos separados por vírgula)
        if operador_filtro != 'TODOS' and operador_filtro:
            if ',' in operador_filtro:
                lista_operadores = [o.strip().upper() for o in operador_filtro.split(',') if o.strip()]
                if login.strip().upper() not in lista_operadores:
                    continue
            else:
                if login.strip().upper() != operador_filtro.strip().upper():
                    continue

        # Busca os pagamentos e metas do operador com base no banco correspondente
        if banco == 'SEMEAR':
            pagamentos = Buscar_pagamento_semear(op) or []
            metas = buscar_metas_semear(op) or []
        else:
            pagamentos = Buscar_pagamento_agoracred(op) or []
            metas = buscar_metas_agoracred(op) or []

        # Converte objetos de pagamento para dicionário se necessário
        if pagamentos and not isinstance(pagamentos[0], dict):
            pagamentos = [p.__dict__ for p in pagamentos]

        # Filtra os pagamentos por contrato ou cliente caso preenchido
        if contrato_filtro:
            pagamentos = [
                p for p in pagamentos
                if contrato_filtro.lower() in (p.get('contrato', '') or '').lower() or
                contrato_filtro.lower() in (p.get('cliente', '') or '').lower()
            ]

        # Filtra os pagamentos por faixa de atraso específica (apenas para SEMEAR)
        if banco == 'SEMEAR' and faixa_filtro != 'todas' and faixa_filtro:
            # Suporta múltiplas faixas separadas por vírgula
            if ',' in faixa_filtro:
                lista_faixas = [f.strip() for f in faixa_filtro.split(',') if f.strip()]
                pagamentos = [p for p in pagamentos if (p.get('faseAtraso', '') or '') in lista_faixas]
            else:
                pagamentos = [p for p in pagamentos if (p.get('faseAtraso', '') or '') == faixa_filtro]

        # Se tem filtro de range, filtra por data range; caso contrário, filtra por mês/ano
        if tem_range:
            pagamentos_periodo = [p for p in pagamentos if _pagamento_no_range(p, data_inicio, data_fim)]
            # Calcula o mesmo intervalo equivalente no mês anterior para comparar
            try:
                from dateutil.relativedelta import relativedelta
                dt_ini = datetime.strptime(data_inicio[:10], '%Y-%m-%d') if data_inicio else None
                dt_fim = datetime.strptime(data_fim[:10], '%Y-%m-%d') if data_fim else None
                dt_ini_ant = (dt_ini - relativedelta(months=1)).strftime('%Y-%m-%d') if dt_ini else None
                dt_fim_ant = (dt_fim - relativedelta(months=1)).strftime('%Y-%m-%d') if dt_fim else None
                pagamentos_ant = [p for p in pagamentos if _pagamento_no_range(p, dt_ini_ant, dt_fim_ant)]
            except Exception:
                pagamentos_ant = []
            mes_para_meta = mes
            ano_para_meta = ano
        else:
            pagamentos_periodo = [p for p in pagamentos if _pagamento_no_mes(p, ano, mes)]
            pagamentos_ant = [p for p in pagamentos if _pagamento_no_mes(p, ano_ant, mes_ant)]
            mes_para_meta = mes
            ano_para_meta = ano

        if du_inicio is not None or du_fim is not None:
            pagamentos_periodo = [p for p in pagamentos_periodo if _pagamento_no_du_range(p, du_inicio, du_fim)]
            pagamentos_ant = [p for p in pagamentos_ant if _pagamento_no_du_range(p, du_inicio, du_fim)]

        # (max_data_banco já foi calculado no pré-passo acima, de forma
        # independente do operador/contrato/faixa filtrados aqui)

        # Calcula a performance do operador (mês atual / período)
        performance = calcular_performance_operador(
            pagamentos=pagamentos,
            metas=metas,
            ano=ano_para_meta,
            mes=mes_para_meta,
            login=login,
            banco=banco
        )

        # Calcula a performance do operador para o mês anterior
        if tem_range:
            performance_ant = {'faturamento': 0.0, 'meta': 0.0}
        else:
            performance_ant = calcular_performance_operador(
                pagamentos=pagamentos,
                metas=metas,
                ano=ano_ant,
                mes=mes_ant,
                login=login,
                banco=banco
            )

        # Consolida os valores calculados
        faturamento = sum(p.get('valorTotal') or 0.0 for p in pagamentos_periodo)
        faturamento_ant = sum(p.get('valorTotal') or 0.0 for p in pagamentos_ant)
        meta_val = performance.get('meta', 0.0)
        meta_ant_val = performance_ant.get('meta', 0.0)

        ops_atual = len(pagamentos_periodo)
        ops_anterior = len(pagamentos_ant)

        total_faturamento += faturamento
        total_operacoes += ops_atual
        total_faturamento_ant += faturamento_ant
        total_operacoes_ant += ops_anterior

        # Calcula o tempo de casa do operador
        tempo_casa = calcular_tempo_de_casa(op.get('admissao'))

        perc_meta_atual = (faturamento / meta_val * 100) if meta_val > 0 else 0.0
        perc_meta_ant = (faturamento_ant / meta_ant_val * 100) if meta_ant_val > 0 else 0.0

        # Mapeamento do meta_ranking para o mês/ano selecionado
        meta_ranking_val = 0.0
        for m in metas:
            try:
                # Se for objeto SqlAlchemy
                if not isinstance(m, dict):
                    m_data = m.data
                    m_val = getattr(m, 'metaRanking', 0.0) or 0.0
                else:
                    m_data = m.get('data')
                    m_val = m.get('meta_ranking', 0.0) or 0.0

                if isinstance(m_data, str):
                    dt_obj = datetime.strptime(m_data[:10], '%Y-%m-%d').date()
                else:
                    dt_obj = m_data

                if dt_obj and dt_obj.year == ano and dt_obj.month == mes:
                    meta_ranking_val = float(m_val)
                    break
            except Exception:
                continue

        # Armazena os dados temporários — feito_dia e projecao serão calculados
        # apenas após a primeira passagem, quando tivermos max_data_banco definitivo
        dados_temporarios.append({
            'op': op,
            'login': login,
            'pagamentos': pagamentos,
            'faturamento': faturamento,
            'faturamento_ant': faturamento_ant,
            'meta_val': meta_val,
            'meta_ant_val': meta_ant_val,
            'ops_atual': ops_atual,
            'ops_anterior': ops_anterior,
            'tempo_casa': tempo_casa,
            'perc_meta_atual': perc_meta_atual,
            'perc_meta_ant': perc_meta_ant,
            'meta_ranking_val': meta_ranking_val,
        })

    # ---------------------------------------------------------------
    # Formata a data máxima do banco para exibição no banner
    # Exemplo: "14/07/2026"
    # ---------------------------------------------------------------
    if max_data_banco:
        ultima_baixa_str = max_data_banco.strftime('%d/%m/%Y')  # ex: "14/07/2026"
        dia_divisor = max_data_banco.day  # dia numérico para feito/dia
    else:
        ultima_baixa_str = None
        dia_divisor = datetime.now().day  # fallback para o dia atual

    # ---------------------------------------------------------------
    # SEGUNDA PASSAGEM: monta o ranking usando dia_divisor do banco
    # ---------------------------------------------------------------
    hoje = datetime.now()
    total_dias_mes = monthrange(ano, mes)[1]

    # Pré-calcula dias úteis totais do mês para usar na projeção
    import holidays as _hols_rank
    from dateutil.easter import easter as _easter_rank
    from datetime import timedelta as _td_rank
    _feriados_rank = _hols_rank.country_holidays('BR', years=ano)
    _feriados_rank.update({_easter_rank(ano) + _td_rank(days=60): 'Corpus Christi'})
    total_du_mes = sum(
        1 for d in range(1, total_dias_mes + 1)
        if date(ano, mes, d).weekday() < 5 and date(ano, mes, d) not in _feriados_rank
    )

    for item in dados_temporarios:
        faturamento = item['faturamento']

        # Feito/dia usa a data máxima do banco inteiro, não o dia atual
        # Isso garante que o cálculo reflita a realidade das baixas bancárias
        if tem_range:
            # Calcula quantos dias corridos existem no range filtrado
            # e usa total de dias úteis do mês para projeção mensal
            try:
                from datetime import timedelta as _td2
                _dt_ini = datetime.strptime(data_inicio[:10], '%Y-%m-%d').date() if data_inicio else date(ano, mes, 1)
                # Usa a data máxima do banco como referência de "até quando foi recebido"
                _dt_fim_range = max_data_banco.date() if max_data_banco else (
                    datetime.strptime(data_fim[:10], '%Y-%m-%d').date() if data_fim else date(ano, mes, total_dias_mes)
                )
                # Dias úteis passados no range (início até data máxima do banco)
                dias_passados_calc = max(1, sum(
                    1 for i in range((_dt_fim_range - _dt_ini).days + 1)
                    if (_dt_ini + _td2(days=i)).weekday() < 5
                    and (_dt_ini + _td2(days=i)) not in _feriados_rank
                ))
                total_dias_calc = max(1, total_du_mes)
            except Exception:
                dias_passados_calc = 1
                total_dias_calc = 1
            feito_dia = faturamento / dias_passados_calc if dias_passados_calc > 0 else 0.0
        else:
            total_dias_calc = total_du_mes if total_du_mes > 0 else total_dias_mes
            # Usa dia_divisor (data máxima do banco) para meses atuais
            # Para meses passados usa o total de dias úteis do mês
            if hoje.year == ano and hoje.month == mes:
                # Dias úteis passados até a data máxima do banco
                if max_data_banco:
                    dias_passados_calc = sum(
                        1 for d in range(1, max_data_banco.day + 1)
                        if date(ano, mes, d).weekday() < 5 and date(ano, mes, d) not in _feriados_rank
                    )
                else:
                    dias_passados_calc = dia_divisor
                dias_passados_calc = max(1, dias_passados_calc)
            else:
                dias_passados_calc = total_dias_calc
            feito_dia = faturamento / dias_passados_calc if dias_passados_calc > 0 else 0.0

        # Calcula projeção do mês com base no ritmo do feito/dia
        projecao = (faturamento / dias_passados_calc * total_dias_calc) if dias_passados_calc > 0 else 0.0
        meta_val = item['meta_val']
        projecao_percentual = (projecao / meta_val * 100) if meta_val > 0 else 0.0

        # Calcula dias sem recebimento do operador individual
        max_dt_op: Optional[datetime] = None
        for p in item['pagamentos']:
            dt_v = p.get('dtPgto')
            if not dt_v:
                continue
            try:
                dt_o = datetime.strptime(str(dt_v)[:10], '%Y-%m-%d') if not isinstance(dt_v, datetime) else dt_v
                if dt_o.year == ano and dt_o.month == mes:
                    if max_dt_op is None or dt_o > max_dt_op:
                        max_dt_op = dt_o
            except Exception:
                pass

        # Calcula dias úteis sem recebimento do operador em relação à última baixa do banco
        ref_dt = max_data_banco or datetime.now()
        ultimo_valor_pgto = 0.0
        ultima_data_op_str = '-'

        if max_dt_op:
            # Seleciona o pagamento mais recente do operador no mês para obter o valor
            for p in item['pagamentos']:
                dt_v = p.get('dtPgto')
                if not dt_v:
                    continue
                try:
                    dt_o = datetime.strptime(str(dt_v)[:10], '%Y-%m-%d') if not isinstance(dt_v, datetime) else dt_v
                    if dt_o == max_dt_op:
                        ultimo_valor_pgto = float(p.get('valorTotal', 0.0) or 0.0)
                        break
                except Exception:
                    pass

            ultima_data_op_str = max_dt_op.strftime('%d/%m/%Y')

            # Conta exclusivamente DIAS ÚTEIS (seg-sex excluindo feriados BR)
            # entre a data do último pagamento do operador e a última baixa do banco
            from datetime import timedelta
            feriados_br = holidays.country_holidays('BR', years=ref_dt.year)
            start_d = max_dt_op.date()
            end_d = ref_dt.date()

            dias_sem_rec = 0
            curr_d = start_d + timedelta(days=1)
            while curr_d <= end_d:
                if curr_d.weekday() < 5 and curr_d not in feriados_br:
                    dias_sem_rec += 1
                curr_d += timedelta(days=1)
        else:
            dias_sem_rec = dias_passados_calc

        alerta_op = dias_sem_rec >= 2

        # Monta a estrutura de dados do operador para o ranking
        ranking_list.append({
            'login': item['login'],
            'imagem': item['op'].get('imagem', '') or '',
            'atividade': item['op'].get('atividade', '') or '',
            'turno': item['op'].get('turno', ''),
            'tempo_casa': item['tempo_casa'],
            'faturamento': faturamento,
            'faturamento_anterior': item['faturamento_ant'],
            'quantidade': item['ops_atual'],
            'feito_dia': round(feito_dia, 2),
            'meta': meta_val,
            'meta_anterior': item['meta_ant_val'],
            'meta_ranking': item['meta_ranking_val'],
            'perc_meta': item['perc_meta_atual'],
            'perc_meta_anterior': item['perc_meta_ant'],
            'falta_70': max(0.0, (meta_val * 0.7) - faturamento),
            'falta_80': max(0.0, (meta_val * 0.8) - faturamento),
            'falta_90': max(0.0, (meta_val * 0.9) - faturamento),
            'falta_100': max(0.0, meta_val - faturamento),
            'projecao': round(projecao, 2),
            'projecao_percentual': round(projecao_percentual, 2),
            'dias_trabalhados': dias_passados_calc,
            'total_dias_uteis': total_dias_calc,
            'ultima_baixa': ultima_baixa_str,
            'alerta_sem_pgto': alerta_op,
            'dias_sem_pgto': dias_sem_rec,
            'ultima_data_op': ultima_data_op_str,
            'ultimo_valor_pgto': round(ultimo_valor_pgto, 2),
            'pagamentos_brutos': item['pagamentos']
        })


    # Calcula ticket médio atual e anterior
    ticket_medio = total_faturamento / total_operacoes if total_operacoes > 0 else 0.0
    ticket_medio_ant = total_faturamento_ant / total_operacoes_ant if total_operacoes_ant > 0 else 0.0

    # Expõe a data máxima do banco como string no primeiro elemento da lista (para uso do caller)
    # A data fica também no campo dedicado ultima_baixa de cada operador
    return ranking_list, faixas_acumuladas, total_operacoes, total_faturamento, total_operacoes_ant, total_faturamento_ant, ticket_medio, ticket_medio_ant, ultima_baixa_str


def montar_evolucao(
    ranking_list: List[Dict[str, Any]],
    ano: int,
    mes: int,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    du_inicio: Optional[int] = None,
    du_fim: Optional[int] = None,
    max_data_banco_str: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Consolida o faturamento diário para o período selecionado somando
    os valores de faturamento de todos os pagamentos processados.
    Preenche com R$ 0,00 todos os dias úteis (seg-sex) sem pagamento.
    Respeita os filtros de data e dia útil.
    Limita o intervalo exibido até max_data_banco_str (última baixa real do banco)
    para evitar dias futuros zerados.
    """
    from calendar import monthrange
    import holidays as _hols
    from dateutil.easter import easter as _easter
    from datetime import timedelta as _td

    evolucao_diaria = {}
    tem_range = bool(data_inicio or data_fim)

    # --- determina intervalo a ser preenchido ---
    if tem_range and data_inicio and data_fim:
        try:
            ref_ini = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            ref_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        except Exception:
            ref_ini = date(ano, mes, 1)
            ref_fim = date(ano, mes, monthrange(ano, mes)[1])
    else:
        ref_ini = date(ano, mes, 1)
        ref_fim = date(ano, mes, monthrange(ano, mes)[1])

    # Limita ref_fim à última data real de baixa do banco (evita dias zerados futuros)
    # Aplica apenas quando não há filtro de data explícito (sem tem_range)
    if not tem_range and max_data_banco_str:
        try:
            max_dt = datetime.strptime(max_data_banco_str, '%d/%m/%Y').date()
            if max_dt < ref_fim:
                ref_fim = max_dt
        except Exception:
            pass

    # --- feriados para evitar exibir feriado como DU ---
    feriados = _hols.country_holidays('BR', years=ano)
    feriados.update({_easter(ano) + _td(days=60): 'Corpus Christi'})

    # Dias abreviados: 0=seg ... 6=dom
    DIAS_ABREV = ['seg', 'ter', 'qua', 'qui', 'sex', 'sab', 'dom']

    # Pre-popula todos os dias uteis do intervalo com 0
    d = ref_ini
    du_cont = 0
    while d <= ref_fim:
        if d.weekday() < 5 and d not in feriados:
            du_cont += 1
            # Se houver filtro de DU, filtra apenas os DUs dentro do intervalo
            if du_inicio is not None and du_cont < du_inicio:
                d += _td(days=1)
                continue
            if du_fim is not None and du_cont > du_fim:
                d += _td(days=1)
                continue

            ds = d.strftime('%Y-%m-%d')
            nome_dia = DIAS_ABREV[d.weekday()]
            evolucao_diaria[ds] = {
                'total': 0.0,
                'quantidade': 0,
                'data_formatada': f"{d.day} - {nome_dia}"
            }
        d += _td(days=1)

    for op in ranking_list:
        for p in op.get('pagamentos_brutos', []):
            data = p.get('dtPgto')
            if not data:
                continue

            if tem_range:
                if not _pagamento_no_range(p, data_inicio, data_fim):
                    continue
            else:
                if not _pagamento_no_mes(p, ano, mes):
                    continue

            if du_inicio is not None or du_fim is not None:
                if not _pagamento_no_du_range(p, du_inicio, du_fim):
                    continue

            if isinstance(data, datetime):
                data_str = data.strftime('%Y-%m-%d')
                dia_dt = data.date()
            else:
                data_str = str(data)[:10]
                try:
                    dia_dt = datetime.strptime(data_str, '%Y-%m-%d').date()
                except Exception:
                    continue

            # Só inclui se estiver presente no dicionário de dias pré-populados (respeita o filtro)
            if data_str in evolucao_diaria:
                evolucao_diaria[data_str]['total'] += (p.get('valorTotal') or 0.0)
                evolucao_diaria[data_str]['quantidade'] += 1

    return [
        {
            'data': k,
            'total': v['total'],
            'quantidade': v['quantidade'],
            'data_formatada': v.get('data_formatada', k)
        }
        for k, v in sorted(evolucao_diaria.items())
    ]



def montar_faixas(ranking_list: List[Dict[str, Any]], ano: int, mes: int, data_inicio: Optional[str] = None, data_fim: Optional[str] = None, du_inicio: Optional[int] = None, du_fim: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Monta a distribuição de faturamento e quantidade de pagamentos por faixas de atraso para os operadores.
    Mapeia os valores totais cobrados e a quantidade de cada operador por faixa (faseAtraso).
    """
    faixas_operadores = {}
    fases_encontradas = set()
    tem_range = bool(data_inicio or data_fim)

    for op in ranking_list:
        login = op['login']
        imagem = op.get('imagem', '') or ''
        faixas_operadores[login] = {'imagem': imagem}

        for p in op.get('pagamentos_brutos', []):
            # Filtra por período
            if tem_range:
                if not _pagamento_no_range(p, data_inicio, data_fim):
                    continue
            else:
                if not _pagamento_no_mes(p, ano, mes):
                    continue

            if du_inicio is not None or du_fim is not None:
                if not _pagamento_no_du_range(p, du_inicio, du_fim):
                    continue


            fase = p.get('faseAtraso') or 'Outros'
            fases_encontradas.add(str(fase))

            # Inicializa a fase com estrutura de dicionário para guardar valor e quantidade
            if fase not in faixas_operadores[login]:
                faixas_operadores[login][fase] = {'valor': 0.0, 'qtd': 0}
            elif not isinstance(faixas_operadores[login][fase], dict):
                faixas_operadores[login][fase] = {'valor': float(faixas_operadores[login][fase]), 'qtd': 0}

            faixas_operadores[login][fase]['valor'] += (p.get('valorTotal') or 0.0)
            faixas_operadores[login][fase]['qtd'] += 1

    # Formata o retorno estruturado esperado pelo frontend
    faixas_list = []
    for op in ranking_list:
        login = op['login']
        op_faixas = {
            'operador': login,
            'imagem': op.get('imagem', '') or ''
        }

        fases_filtradas = sorted([f for f in fases_encontradas if f])
        for fase in fases_filtradas:
            fase_data = faixas_operadores[login].get(fase, {'valor': 0.0, 'qtd': 0})
            if not isinstance(fase_data, dict):
                fase_data = {'valor': float(fase_data), 'qtd': 0}
            
            # Mantém chave padrão (valor em reais) para compatibilidade
            op_faixas[str(fase)] = fase_data['valor']
            # Adiciona nova chave com sufixo _qtd para a quantidade de contratos
            op_faixas[str(fase) + '_qtd'] = fase_data['qtd']

        faixas_list.append(op_faixas)

    return faixas_list


def montar_evolucao_operadores(
    ranking_semear: List[Dict[str, Any]],
    ranking_agoracred: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Monta a evolução dos operadores (Variação vs Mês Anterior)
    comparando faturamento atual com o mês anterior para cada operador.
    """
    evolucao = []

    for banco, ranking in [('SEMEAR', ranking_semear), ('AGORACRED', ranking_agoracred)]:
        for op in ranking:
            fat_atual = op.get('faturamento', 0.0)
            fat_anterior = op.get('faturamento_anterior', 0.0)
            meta_atual = op.get('meta', 0.0)
            meta_ant = op.get('meta_anterior', 0.0)
            variacao = fat_atual - fat_anterior
            variacao_pct = (variacao / fat_anterior * 100) if fat_anterior > 0 else 0.0
            perc_meta_atual = (fat_atual / meta_atual * 100) if meta_atual > 0 else 0.0
            perc_meta_ant = (fat_anterior / meta_ant * 100) if meta_ant > 0 else 0.0
            variacao_meta_pp = perc_meta_atual - perc_meta_ant

            projecao = op.get('projecao', 0.0)
            projecao_pct = op.get('projecao_percentual') or ((projecao / meta_atual * 100) if meta_atual > 0 else 0.0)

            evolucao.append({
                'banco': banco,
                'operador': op.get('login', '-'),
                'imagem': op.get('imagem', '') or '',
                'fat_atual': fat_atual,
                'fat_anterior': fat_anterior,
                'variacao': variacao,
                'variacao_percentual': variacao_pct,
                'perc_meta_atual': perc_meta_atual,
                'perc_meta_anterior': perc_meta_ant,
                'variacao_meta_pp': variacao_meta_pp,
                'projecao': projecao,
                'projecao_percentual': round(projecao_pct, 1),
                'meta': meta_atual
            })

    # Ordena os operadores por quem mais possui % de projeção atingida (decrescente)
    evolucao.sort(key=lambda x: x.get('projecao_percentual', 0.0), reverse=True)

    return evolucao



def montar_historico_mensal_banco(
    operadores: List[Dict[str, Any]],
    banco: str,
    ano: int,
    ultima_baixa: str = None
) -> List[Dict[str, Any]]:
    """
    Consolida o faturamento e a meta de todos os operadores do banco
    para cada um dos 12 meses do ano selecionado, retornando uma lista
    de 12 entradas no mesmo formato que o histórico mensal do operador individual.
    
    Resultado: lista de dicts com chaves: mes, mes_nome, faturamento, meta, perc_meta,
    variacao, variacao_pct, perc_meta_ant, contratos
    """
    MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    # Inicializa acumuladores por mês
    fat_por_mes = {m: 0.0 for m in range(1, 13)}
    meta_por_mes = {m: 0.0 for m in range(1, 13)}
    contratos_por_mes = {m: 0 for m in range(1, 13)}

    for op in operadores:
        if banco == 'SEMEAR':
            pagamentos = Buscar_pagamento_semear(op) or []
            metas = buscar_metas_semear(op) or []
        else:
            pagamentos = Buscar_pagamento_agoracred(op) or []
            metas = buscar_metas_agoracred(op) or []

        if pagamentos and not isinstance(pagamentos[0], dict):
            pagamentos = [p.__dict__ for p in pagamentos]

        # Acumula faturamento por mês
        for p in pagamentos:
            data = p.get('dtPgto')
            if not data:
                continue
            try:
                if isinstance(data, datetime):
                    p_ano, p_mes = data.year, data.month
                else:
                    dt = datetime.strptime(str(data)[:10], '%Y-%m-%d')
                    p_ano, p_mes = dt.year, dt.month
            except Exception:
                continue

            if p_ano == ano:
                fat_por_mes[p_mes] += float(p.get('valorTotal') or 0.0)
                contratos_por_mes[p_mes] += 1

        # Acumula metas por mês (soma de todos os operadores)
        if metas and not isinstance(metas[0], dict):
            metas = [m.__dict__ for m in metas]
        for m in metas:
            try:
                m_data = m.get('data')
                if not m_data:
                    continue
                if isinstance(m_data, str):
                    dt_obj = datetime.strptime(m_data[:10], '%Y-%m-%d')
                else:
                    dt_obj = m_data
                
                if dt_obj.year == ano:
                    m_mes = dt_obj.month
                    if 1 <= m_mes <= 12:
                        meta_por_mes[m_mes] += float(m.get('meta100', 0.0) or 0.0)
            except Exception:
                continue

    from src.services.analytics_service import _contar_dias_uteis
    hoje = datetime.now()

    # Monta resultado
    resultado = []
    for m in range(1, 13):
        fat = fat_por_mes[m]
        meta = meta_por_mes[m]
        perc = (fat / meta * 100) if meta > 0 else 0.0
        bateu = "Sim" if (meta > 0 and fat >= meta) else "Não"

        # Projeção para o mês atual / aberto
        proj_m = fat
        proj_perc_m = perc
        if ano == hoje.year and m == hoje.month:
            data_ref = hoje
            if ultima_baixa:
                try:
                    data_ref = datetime.strptime(ultima_baixa, '%d/%m/%Y')
                except Exception:
                    pass
            d_tot, d_pass = _contar_dias_uteis(ano, m, data_ref)
            if d_pass > 0:
                proj_m = (fat / d_pass) * d_tot
                proj_perc_m = (proj_m / meta * 100) if meta > 0 else 0.0

        # Calcula variação em relação ao mês anterior
        fat_ant = fat_por_mes[m - 1] if m > 1 else 0.0
        meta_ant = meta_por_mes[m - 1] if m > 1 else 0.0
        variacao = fat - fat_ant
        variacao_pct = (variacao / fat_ant * 100) if fat_ant > 0 else 0.0
        perc_meta_ant = (fat_ant / meta_ant * 100) if meta_ant > 0 else 0.0

        resultado.append({
            'mes': m,
            'mes_nome': MESES[m - 1],
            'faturamento': round(fat, 2),
            'meta': round(meta, 2),
            'contratos': contratos_por_mes[m],
            'perc_meta': round(perc, 2),
            'variacao': round(variacao, 2),
            'variacao_pct': round(variacao_pct, 2),
            'perc_meta_ant': round(perc_meta_ant, 2),
            'bateu': bateu,
            'projecao': round(proj_m, 2),
            'projecao_percentual': round(proj_perc_m, 2)
        })

    return resultado


def montar_dashboard_adm(
    ano: int,
    mes: int,
    banco: str = 'TODOS',
    atividade: str = 'ATIVO',
    operador_filtro: str = 'TODOS',
    contrato_filtro: str = '',
    faixa_filtro: str = 'todas',
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    du_inicio: Optional[int] = None,
    du_fim: Optional[int] = None
) -> Dict[str, Any]:
    """
    Função principal que coordena a montagem completa do painel do Administrador.
    Obtém, calcula e formata todos os dados de forma estruturada para retorno JSON.
    """
    # 1. Busca os operadores cadastrados por banco
    operadores_semear = buscar_dados_semear(atividade)
    operadores_agoracred = buscar_dados_agoracred(atividade)

    # 2. Monta o ranking e dados de performance dos operadores (SEMEAR)
    ranking_semear, _, ops_semear, fat_semear, ops_semear_ant, fat_semear_ant, ticket_semear, ticket_semear_ant, ultima_baixa_semear = montar_ranking(
        operadores=operadores_semear,
        banco='SEMEAR',
        ano=ano,
        mes=mes,
        operador_filtro=operador_filtro,
        contrato_filtro=contrato_filtro,
        faixa_filtro=faixa_filtro,
        data_inicio=data_inicio,
        data_fim=data_fim,
        du_inicio=du_inicio,
        du_fim=du_fim
    )

    # 3. Monta o ranking e dados de performance dos operadores (AGORACRED)
    ranking_agoracred, _, ops_agoracred, fat_agoracred, ops_agoracred_ant, fat_agoracred_ant, ticket_agoracred, ticket_agoracred_ant, ultima_baixa_agoracred = montar_ranking(
        operadores=operadores_agoracred,
        banco='AGORACRED',
        ano=ano,
        mes=mes,
        operador_filtro=operador_filtro,
        contrato_filtro=contrato_filtro,
        faixa_filtro=faixa_filtro,
        data_inicio=data_inicio,
        data_fim=data_fim,
        du_inicio=du_inicio,
        du_fim=du_fim
    )

    # Adiciona a indicação do banco para cada operador do ranking
    for op in ranking_semear:
        op['banco'] = 'SEMEAR'
    for op in ranking_agoracred:
        op['banco'] = 'AGORACRED'

    # 4. Processa a evolução diária de faturamento para cada banco
    # Passa ultima_baixa para limitar os dias exibidos até a última baixa real (sem dias futuros zerados)
    evolucao_semear = montar_evolucao(ranking_semear, ano, mes, data_inicio, data_fim, du_inicio, du_fim, ultima_baixa_semear)
    evolucao_agoracred = montar_evolucao(ranking_agoracred, ano, mes, data_inicio, data_fim, du_inicio, du_fim, ultima_baixa_agoracred)


    # 5. Processa as faixas de atraso dos operadores (SEMEAR)
    faixas_semear = montar_faixas(ranking_semear, ano, mes, data_inicio, data_fim, du_inicio, du_fim)

    # 6. Calcula metas totais por banco (soma das metas individuais)
    meta_semear = sum(op.get('meta', 0.0) for op in ranking_semear)
    meta_agoracred = sum(op.get('meta', 0.0) for op in ranking_agoracred)

    # 7. Monta a evolução geral dos operadores com dados reais (respeitando o filtro de banco)
    banco_upper = (banco or 'TODOS').upper()
    if banco_upper == 'SEMEAR':
        evolucao_operadores = montar_evolucao_operadores(ranking_semear, [])
    elif banco_upper == 'AGORACRED':
        evolucao_operadores = montar_evolucao_operadores([], ranking_agoracred)
    else:
        evolucao_operadores = montar_evolucao_operadores(ranking_semear, ranking_agoracred)

    # 8. Calcula KPIs consolidados
    total_ops = ops_semear + ops_agoracred
    total_fat = fat_semear + fat_agoracred
    total_ops_ant = ops_semear_ant + ops_agoracred_ant
    ticket_medio_grupo = total_fat / total_ops if total_ops > 0 else 0.0
    ticket_medio_anterior_grupo = (fat_semear_ant + fat_agoracred_ant) / total_ops_ant if total_ops_ant > 0 else 0.0

    # 9. Histórico de 12 meses consolidado por banco (para Resultado Mês a Mês)
    historico_semear = montar_historico_mensal_banco(operadores_semear, 'SEMEAR', ano, ultima_baixa_semear)
    historico_agoracred = montar_historico_mensal_banco(operadores_agoracred, 'AGORACRED', ano, ultima_baixa_agoracred)

    # 10. Matriz Faixas de Atraso vs Mês para o SEMEAR
    todos_pag_semear = []
    for op in ranking_semear:
        todos_pag_semear.extend(op.get('pagamentos_brutos', []))
    matriz_faixas_semear = montar_matriz_faixa_vs_mes(todos_pag_semear, ano, 'SEMEAR', data_inicio, data_fim, du_inicio, du_fim)


    # 11a. Visão Trimestral por DU — SEMEAR e AGORACRED
    from src.services.analytics_service import montar_comparativo_trimestre_du

    todos_pag_agoracred = []
    for op in ranking_agoracred:
        todos_pag_agoracred.extend(op.get('pagamentos_brutos', []))

    trimestre_du_semear = montar_comparativo_trimestre_du(todos_pag_semear, ano, mes, 'SEMEAR', data_inicio, data_fim, du_inicio, du_fim, ultima_baixa_semear)
    trimestre_du_agoracred = montar_comparativo_trimestre_du(todos_pag_agoracred, ano, mes, 'AGORACRED', data_inicio, data_fim, du_inicio, du_fim, ultima_baixa_agoracred)




    # ── PIVOT: Mês × Operador (usa pagamentos_brutos antes de removê-los) ──
    def _pivot_mes_op(ranking: list, banco_nome: str, metas_por_op: dict) -> list:
        """
        Retorna lista de operadores com faturamento e % meta por mês.
        Estrutura: [{login, mes_1..mes_12: {fat, perc_meta}}, ...]
        """
        MESES_ABREV = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
        resultado = []
        for op in ranking:
            login = op.get('login') or op.get('operador', '')
            pbr   = op.get('pagamentos_brutos', [])
            fat_m = {m: 0.0 for m in range(1, 13)}
            for p in pbr:
                data = p.get('dtPgto')
                if not data:
                    continue
                try:
                    if isinstance(data, datetime):
                        pm = data.month
                        py = data.year
                    else:
                        dt = datetime.strptime(str(data)[:10], '%Y-%m-%d')
                        pm, py = dt.month, dt.year
                except Exception:
                    continue
                if py == ano:
                    fat_m[pm] += float(p.get('valorTotal') or 0.0)

            meses_data = {}
            for i, nome in enumerate(MESES_ABREV, start=1):
                fat  = round(fat_m[i], 2)
                meta = metas_por_op.get(login, {}).get(i, 0.0)
                perc = round(fat / meta * 100, 1) if meta > 0 else 0.0
                meses_data[nome] = {'fat': fat, 'meta': round(meta, 2), 'perc': perc}
            resultado.append({'login': login, 'meses': meses_data})
        return resultado

    # Coleta metas por operador para o pivot
    def _metas_por_login(operadores_lista: list, banco_nome: str) -> dict:
        metas = {}
        for op in operadores_lista:
            login = op.get('login') or op.get('operador', '')
            if banco_nome == 'SEMEAR':
                m_list = buscar_metas_semear(op) or []
            else:
                m_list = buscar_metas_agoracred(op) or []
            if m_list and not isinstance(m_list[0], dict):
                m_list = [x.__dict__ for x in m_list]
            meta_m = {m: 0.0 for m in range(1, 13)}
            for m in m_list:
                try:
                    md = m.get('data')
                    if not md:
                        continue
                    if isinstance(md, str):
                        dt_obj = datetime.strptime(md[:10], '%Y-%m-%d')
                    else:
                        dt_obj = md
                    if dt_obj.year == ano:
                        meta_m[dt_obj.month] += float(m.get('meta100', 0.0) or 0.0)
                except Exception:
                    continue
            metas[login] = meta_m
        return metas

    metas_semear_op    = _metas_por_login(operadores_semear, 'SEMEAR')
    metas_agoracred_op = _metas_por_login(operadores_agoracred, 'AGORACRED')
    pivot_semear    = _pivot_mes_op(ranking_semear,    'SEMEAR',    metas_semear_op)
    pivot_agoracred = _pivot_mes_op(ranking_agoracred, 'AGORACRED', metas_agoracred_op)

    # 12. Remove pagamentos brutos antes de serializar
    for op in ranking_semear:
        op.pop('pagamentos_brutos', None)
    for op in ranking_agoracred:
        op.pop('pagamentos_brutos', None)


    # 13. Retorna o dicionário final com o formato exato esperado pelo frontend
    return {
        'semear': {
            'faturamento': fat_semear,
            'meta': meta_semear,
            'anterior': fat_semear_ant,
            'operacoes': ops_semear,
            'operacoes_anterior': ops_semear_ant,
            'ticket_medio': ticket_semear,
            'ticket_medio_anterior': ticket_semear_ant,
            'evolucao': evolucao_semear,
            'operadores': ranking_semear,
            'faixas': faixas_semear,
            'resultado_mes_a_mes': historico_semear,
            'matriz_faixas_mes': matriz_faixas_semear,
            'trimestre_du': trimestre_du_semear,
            'ultima_baixa': ultima_baixa_semear,
            'pivot_mes_operador': pivot_semear,
        },
        'agoracred': {
            'faturamento': fat_agoracred,
            'meta': meta_agoracred,
            'anterior': fat_agoracred_ant,
            'operacoes': ops_agoracred,
            'operacoes_anterior': ops_agoracred_ant,
            'ticket_medio': ticket_agoracred,
            'ticket_medio_anterior': ticket_agoracred_ant,
            'evolucao': evolucao_agoracred,
            'operadores': ranking_agoracred,
            'resultado_mes_a_mes': historico_agoracred,
            'trimestre_du': trimestre_du_agoracred,
            'ultima_baixa': ultima_baixa_agoracred,
            'pivot_mes_operador': pivot_agoracred,
        },
        'total_operacoes': total_ops,
        'operacoes_anterior': total_ops_ant,
        'ticket_medio': ticket_medio_grupo,
        'ticket_medio_anterior': ticket_medio_anterior_grupo,
        'evolucao_operadores': evolucao_operadores,
    }



# ==============================================================
# TMA - TODOS OS OPERADORES (ADM)
# ==============================================================

def buscar_tma_todos_operadores(ano: int, mes: int, atividade: str = 'ATIVO') -> List[Dict[str, Any]]:
    """
    Busca os dados de TMA de todos os operadores (SEMEAR + AGORACRED)
    e retorna uma lista unificada pronta para o painel ADM.
    """
    resultado = []

    for banco in ['SEMEAR', 'AGORACRED']:
        operadores = buscar_todos_operadores_por_banco(banco) or []
        if atividade == 'ATIVO':
            operadores = [op for op in operadores if op.get('atividade', '').upper() == 'ATIVO']

        for op in operadores:
            login = op.get('login', '')
            if not login:
                continue

            tma_data = buscar_tma_operador(login, banco, ano, mes)
            if not tma_data:
                continue

            resultado.append({
                'login': login,
                'banco': banco,
                'imagem': op.get('imagem', ''),
                'tma': str(tma_data.get('tma', '-')),
                'acionamentos': int(tma_data.get('acionamentos', 0) or 0),
                'clientes': int(tma_data.get('clientes', 0) or 0),
                'reacionamento': str(tma_data.get('reacionamento', '-')),
                'tempo_falado': str(tma_data.get('tempo_falado', '-')),
                'primeiro_acionamento': str(tma_data.get('primeiro_acionamento', '-')),
                'ultimo_acionamento': str(tma_data.get('ultimo_acionamento', '-')),
            })

    # Ordena por acionamentos (decrescente)
    resultado.sort(key=lambda x: x.get('acionamentos', 0), reverse=True)
    return resultado


def buscar_pagamentos_individuais_adm(ano: int, mes: int, banco: str = 'TODOS', operador_filtro: str = 'TODOS', data_inicio: str = None, data_fim: str = None, atividade: str = 'ATIVO', du_inicio: Optional[int] = None, du_fim: Optional[int] = None) -> Dict[str, Any]:
    """
    Busca pagamentos individuais (contrato a contrato) de todos os operadores
    filtrados pelo banco, operador, período e dias úteis selecionados.
    """
    pagamentos_filtrados = []
    operadores_disponiveis = {}

    # Define quais bancos buscar
    bancos_a_buscar = ['SEMEAR', 'AGORACRED'] if banco == 'TODOS' else [banco]

    for b in bancos_a_buscar:
        dados_ops = buscar_pagamentos_todos_operadores_por_banco(b) or []
        for op_dict, pagamentos, metas in dados_ops:
            login = op_dict.get('login')
            if not login:
                continue

            # Filtra operadores inativos se atividade == 'ATIVO'
            if atividade == 'ATIVO' and op_dict.get('atividade', '').upper() != 'ATIVO':
                continue

            operadores_disponiveis[login] = op_dict.get('imagem', '') or ''

            # Filtra operador
            if operador_filtro != 'TODOS' and login != operador_filtro:
                continue

            # Filtra pagamentos do operador pelo período
            for p in pagamentos:
                # Filtragem de data
                if data_inicio or data_fim:
                    if not _pagamento_no_range(p, data_inicio, data_fim):
                        continue
                else:
                    if not _pagamento_no_mes(p, ano, mes):
                        continue

                # Filtragem por Dia Útil (DU)
                if du_inicio is not None or du_fim is not None:
                    if not _pagamento_no_du_range(p, du_inicio, du_fim):
                        continue

                # Formata data
                dt = p.get('dtPgto')
                dt_str = dt
                if isinstance(dt, (datetime, date)):
                     dt_str = dt.strftime('%Y-%m-%d')
                else:
                    dt_str = str(dt)[:10]

                pagamentos_filtrados.append({
                    'dtPgto': dt_str,
                    'contrato': p.get('contrato', '-'),
                    'cliente': p.get('cliente', '-'),
                    'banco': b,
                    'operador': login,
                    'faseAtraso': p.get('faseAtraso', '-'),
                    'atraso': p.get('atraso'),
                    'maiorAtraso': p.get('maiorAtraso'),
                    'valorTotal': float(p.get('valorTotal', 0.0) or 0.0)
                })

    # Ordena por data de pagamento (descendente)
    pagamentos_filtrados.sort(key=lambda x: x.get('dtPgto', ''), reverse=True)

    return {
        'pagamentos': pagamentos_filtrados,
        'operadores': [{'login': l, 'imagem': img} for l, img in sorted(operadores_disponiveis.items())]
    }
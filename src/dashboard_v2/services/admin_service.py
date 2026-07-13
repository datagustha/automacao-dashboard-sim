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
    buscar_metas_agoracred
)
from src.services.analytics_service import (
    calcular_performance_operador,
    calcular_tempo_de_casa
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


def _pagamento_no_mes(pagamento: dict, ano: int, mes: int) -> bool:
    """Verifica se um pagamento pertence ao mês/ano especificado."""
    data = pagamento.get('dtPgto')
    if not data:
        return False
    try:
        if isinstance(data, datetime):
            return data.year == ano and data.month == mes
        data_obj = datetime.strptime(str(data)[:10], '%Y-%m-%d')
        return data_obj.year == ano and data_obj.month == mes
    except Exception:
        return False


def _pagamento_no_range(pagamento: dict, data_inicio: Optional[str], data_fim: Optional[str]) -> bool:
    """Verifica se um pagamento está dentro do range de datas fornecido."""
    if not data_inicio and not data_fim:
        return True
    data = pagamento.get('dtPgto')
    if not data:
        return False
    try:
        if isinstance(data, datetime):
            dt = data.date()
        else:
            dt = datetime.strptime(str(data)[:10], '%Y-%m-%d').date()

        if data_inicio:
            inicio = datetime.strptime(data_inicio[:10], '%Y-%m-%d').date()
            if dt < inicio:
                return False
        if data_fim:
            fim = datetime.strptime(data_fim[:10], '%Y-%m-%d').date()
            if dt > fim:
                return False
        return True
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
    data_fim: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], int, float, int, float, float, float]:
    """
    Calcula a performance de cada operador, aplica os filtros de busca e
    monta o ranking ordenado de faturamento/atingimento de metas.

    Retorna: (ranking_list, faixas_acumuladas, ops_atual, fat_atual, ops_anterior, fat_anterior, ticket_medio, ticket_medio_ant)
    """
    ranking_list = []
    total_faturamento = 0.0
    total_operacoes = 0
    total_faturamento_ant = 0.0
    total_operacoes_ant = 0
    faixas_acumuladas = {}

    ano_ant, mes_ant = _mes_anterior(ano, mes)

    # Verifica se tem filtro de range de data ativo
    tem_range = bool(data_inicio or data_fim)

    for op in operadores:
        login = op.get('login')

        # Filtra pelo operador específico caso seja solicitado
        if operador_filtro != 'TODOS' and login != operador_filtro:
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
        if banco == 'SEMEAR' and faixa_filtro != 'todas':
            pagamentos = [p for p in pagamentos if (p.get('faseAtraso', '') or '') == faixa_filtro]

        # Se tem filtro de range, filtra por data range; caso contrário, filtra por mês/ano
        if tem_range:
            pagamentos_periodo = [p for p in pagamentos if _pagamento_no_range(p, data_inicio, data_fim)]
            pagamentos_ant = []  # Sem período anterior quando usa range
            mes_para_meta = mes
            ano_para_meta = ano
        else:
            pagamentos_periodo = [p for p in pagamentos if _pagamento_no_mes(p, ano, mes)]
            pagamentos_ant = [p for p in pagamentos if _pagamento_no_mes(p, ano_ant, mes_ant)]
            mes_para_meta = mes
            ano_para_meta = ano

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

        # Calcula feito_dia (faturamento do período / dias passados no mês)
        hoje = datetime.now()
        if tem_range:
            feito_dia = faturamento  # Sem lógica diária para range
        else:
            dias_passados = hoje.day if (hoje.year == ano and hoje.month == mes) else monthrange(ano, mes)[1]
            feito_dia = faturamento / dias_passados if dias_passados > 0 else 0.0

        # Monta a estrutura de dados do operador para o ranking
        ranking_list.append({
            'login': login,
            'imagem': op.get('imagem', '') or '',
            'turno': op.get('turno', ''),
            'tempo_casa': tempo_casa,
            'faturamento': faturamento,
            'faturamento_anterior': faturamento_ant,
            'feito_dia': feito_dia,
            'meta': meta_val,
            'meta_anterior': meta_ant_val,
            'perc_meta': perc_meta_atual,
            'perc_meta_anterior': perc_meta_ant,
            'falta_70': max(0.0, (meta_val * 0.7) - faturamento),
            'falta_80': max(0.0, (meta_val * 0.8) - faturamento),
            'falta_90': max(0.0, (meta_val * 0.9) - faturamento),
            'falta_100': max(0.0, meta_val - faturamento),
            'pagamentos_brutos': pagamentos  # Mantém referência para cálculo de faixas e evolução
        })

    # Calcula ticket médio atual e anterior
    ticket_medio = total_faturamento / total_operacoes if total_operacoes > 0 else 0.0
    ticket_medio_ant = total_faturamento_ant / total_operacoes_ant if total_operacoes_ant > 0 else 0.0

    return ranking_list, faixas_acumuladas, total_operacoes, total_faturamento, total_operacoes_ant, total_faturamento_ant, ticket_medio, ticket_medio_ant


def montar_evolucao(ranking_list: List[Dict[str, Any]], ano: int, mes: int, data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Consolida o faturamento diário para o período selecionado somando
    os valores de faturamento de todos os pagamentos processados.
    """
    evolucao_diaria = {}
    tem_range = bool(data_inicio or data_fim)

    for op in ranking_list:
        for p in op.get('pagamentos_brutos', []):
            data = p.get('dtPgto')
            if not data:
                continue

            # Verifica se o pagamento é do período correto
            if tem_range:
                if not _pagamento_no_range(p, data_inicio, data_fim):
                    continue
            else:
                if not _pagamento_no_mes(p, ano, mes):
                    continue

            # Formata a data como string YYYY-MM-DD
            if isinstance(data, datetime):
                data_str = data.strftime('%Y-%m-%d')
            else:
                data_str = str(data)[:10]

            evolucao_diaria[data_str] = evolucao_diaria.get(data_str, 0.0) + (p.get('valorTotal') or 0.0)

    return [{'data': k, 'total': v} for k, v in sorted(evolucao_diaria.items())]


def montar_faixas(ranking_list: List[Dict[str, Any]], ano: int, mes: int, data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Monta a distribuição de faturamento por faixas de atraso para os operadores.
    Mapeia os valores totais cobrados de cada operador por faixa (faseAtraso).
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

            fase = p.get('faseAtraso') or 'Outros'
            fases_encontradas.add(str(fase))

            faixas_operadores[login][fase] = faixas_operadores[login].get(fase, 0.0) + (p.get('valorTotal') or 0.0)

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
            op_faixas[str(fase)] = faixas_operadores[login].get(fase, 0.0)

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
                'variacao_meta_pp': variacao_meta_pp
            })

    return evolucao


def montar_dashboard_adm(
    ano: int,
    mes: int,
    atividade: str = 'ATIVO',
    operador_filtro: str = 'TODOS',
    contrato_filtro: str = '',
    faixa_filtro: str = 'todas',
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None
) -> Dict[str, Any]:
    """
    Função principal que coordena a montagem completa do painel do Administrador.
    Obtém, calcula e formata todos os dados de forma estruturada para retorno JSON.
    """
    # 1. Busca os operadores cadastrados por banco
    operadores_semear = buscar_dados_semear(atividade)
    operadores_agoracred = buscar_dados_agoracred(atividade)

    # 2. Monta o ranking e dados de performance dos operadores (SEMEAR)
    ranking_semear, _, ops_semear, fat_semear, ops_semear_ant, fat_semear_ant, ticket_semear, ticket_semear_ant = montar_ranking(
        operadores=operadores_semear,
        banco='SEMEAR',
        ano=ano,
        mes=mes,
        operador_filtro=operador_filtro,
        contrato_filtro=contrato_filtro,
        faixa_filtro=faixa_filtro,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

    # 3. Monta o ranking e dados de performance dos operadores (AGORACRED)
    ranking_agoracred, _, ops_agoracred, fat_agoracred, ops_agoracred_ant, fat_agoracred_ant, ticket_agoracred, ticket_agoracred_ant = montar_ranking(
        operadores=operadores_agoracred,
        banco='AGORACRED',
        ano=ano,
        mes=mes,
        operador_filtro=operador_filtro,
        contrato_filtro=contrato_filtro,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

    # 4. Processa a evolução diária de faturamento para cada banco
    evolucao_semear = montar_evolucao(ranking_semear, ano, mes, data_inicio, data_fim)
    evolucao_agoracred = montar_evolucao(ranking_agoracred, ano, mes, data_inicio, data_fim)

    # 5. Processa as faixas de atraso dos operadores (SEMEAR)
    faixas_semear = montar_faixas(ranking_semear, ano, mes, data_inicio, data_fim)

    # 6. Calcula metas totais por banco (soma das metas individuais)
    meta_semear = sum(op.get('meta', 0.0) for op in ranking_semear)
    meta_agoracred = sum(op.get('meta', 0.0) for op in ranking_agoracred)

    # 7. Monta a evolução geral dos operadores com dados reais
    evolucao_operadores = montar_evolucao_operadores(ranking_semear, ranking_agoracred)

    # 8. Calcula KPIs consolidados
    total_ops = ops_semear + ops_agoracred
    total_fat = fat_semear + fat_agoracred
    total_ops_ant = ops_semear_ant + ops_agoracred_ant
    ticket_medio_grupo = total_fat / total_ops if total_ops > 0 else 0.0

    # 9. Remove pagamentos brutos antes de serializar
    for op in ranking_semear:
        op.pop('pagamentos_brutos', None)
    for op in ranking_agoracred:
        op.pop('pagamentos_brutos', None)

    # 10. Retorna o dicionário final com o formato exato esperado pelo frontend
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
            'faixas': faixas_semear
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
            'operadores': ranking_agoracred
        },
        'total_operacoes': total_ops,
        'operacoes_anterior': total_ops_ant,
        'ticket_medio': ticket_medio_grupo,
        'evolucao_operadores': evolucao_operadores
    }
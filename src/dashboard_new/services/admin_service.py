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
    # PRIMEIRA PASSAGEM: coleta pagamentos e performance de cada operador
    # Também coleta a data máxima de pagamento do banco inteiro
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
            pagamentos_ant = []  # Sem período anterior quando usa range
            mes_para_meta = mes
            ano_para_meta = ano
        else:
            pagamentos_periodo = [p for p in pagamentos if _pagamento_no_mes(p, ano, mes)]
            pagamentos_ant = [p for p in pagamentos if _pagamento_no_mes(p, ano_ant, mes_ant)]
            mes_para_meta = mes
            ano_para_meta = ano

        # Coleta a data máxima de pagamento do período deste operador
        # para compor a data máxima GLOBAL do banco inteiro
        for p in pagamentos_periodo:
            dt_val = p.get('dtPgto')
            if not dt_val:
                continue
            try:
                if isinstance(dt_val, datetime):
                    dt_obj = dt_val
                else:
                    dt_obj = datetime.strptime(str(dt_val)[:10], '%Y-%m-%d')
                if max_data_banco is None or dt_obj > max_data_banco:
                    max_data_banco = dt_obj  # atualiza o máximo do banco
            except Exception:
                pass

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

    for item in dados_temporarios:
        faturamento = item['faturamento']

        # Feito/dia usa a data máxima do banco inteiro, não o dia atual
        # Isso garante que o cálculo reflita a realidade das baixas bancárias
        if tem_range:
            feito_dia = faturamento  # Sem lógica diária para range
            dias_passados_calc = 1
            total_dias_calc = 1
        else:
            total_dias_calc = total_dias_mes
            # Usa dia_divisor (data máxima do banco) para meses atuais
            # Para meses passados usa o total de dias do mês
            if hoje.year == ano and hoje.month == mes:
                dias_passados_calc = dia_divisor  # DATA MÁXIMA DO BANCO INTEIRO
            else:
                dias_passados_calc = total_dias_mes
            feito_dia = faturamento / dias_passados_calc if dias_passados_calc > 0 else 0.0

        # Calcula projeção do mês com base no ritmo do feito/dia
        projecao = (faturamento / dias_passados_calc * total_dias_calc) if dias_passados_calc > 0 else 0.0
        meta_val = item['meta_val']
        projecao_percentual = (projecao / meta_val * 100) if meta_val > 0 else 0.0

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
            'ultima_baixa': ultima_baixa_str,  # "Baixas até dia X" — mesma para todos do banco
            'pagamentos_brutos': item['pagamentos']  # Mantém referência para cálculo de faixas e evolução
        })

    # Calcula ticket médio atual e anterior
    ticket_medio = total_faturamento / total_operacoes if total_operacoes > 0 else 0.0
    ticket_medio_ant = total_faturamento_ant / total_operacoes_ant if total_operacoes_ant > 0 else 0.0

    # Expõe a data máxima do banco como string no primeiro elemento da lista (para uso do caller)
    # A data fica também no campo dedicado ultima_baixa de cada operador
    return ranking_list, faixas_acumuladas, total_operacoes, total_faturamento, total_operacoes_ant, total_faturamento_ant, ticket_medio, ticket_medio_ant, ultima_baixa_str


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

            evolucao_diaria.setdefault(data_str, {'total': 0.0, 'quantidade': 0})
            evolucao_diaria[data_str]['total'] += (p.get('valorTotal') or 0.0)
            evolucao_diaria[data_str]['quantidade'] += 1

    return [{'data': k, 'total': v['total'], 'quantidade': v['quantidade']} for k, v in sorted(evolucao_diaria.items())]


def montar_faixas(ranking_list: List[Dict[str, Any]], ano: int, mes: int, data_inicio: Optional[str] = None, data_fim: Optional[str] = None) -> List[Dict[str, Any]]:
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


def montar_historico_mensal_banco(
    operadores: List[Dict[str, Any]],
    banco: str,
    ano: int
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

    # Monta resultado
    resultado = []
    for m in range(1, 13):
        fat = fat_por_mes[m]
        meta = meta_por_mes[m]
        perc = (fat / meta * 100) if meta > 0 else 0.0

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
        })

    return resultado


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
    # O 9º valor retornado é a data máxima de pagamento do banco (ex: "14/07/2026")
    ranking_semear, _, ops_semear, fat_semear, ops_semear_ant, fat_semear_ant, ticket_semear, ticket_semear_ant, ultima_baixa_semear = montar_ranking(
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
    ranking_agoracred, _, ops_agoracred, fat_agoracred, ops_agoracred_ant, fat_agoracred_ant, ticket_agoracred, ticket_agoracred_ant, ultima_baixa_agoracred = montar_ranking(
        operadores=operadores_agoracred,
        banco='AGORACRED',
        ano=ano,
        mes=mes,
        operador_filtro=operador_filtro,
        contrato_filtro=contrato_filtro,
        faixa_filtro=faixa_filtro,
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

    # 9. Histórico de 12 meses consolidado por banco (para Resultado Mês a Mês)
    historico_semear = montar_historico_mensal_banco(operadores_semear, 'SEMEAR', ano)
    historico_agoracred = montar_historico_mensal_banco(operadores_agoracred, 'AGORACRED', ano)

    # 10. Remove pagamentos brutos antes de serializar
    for op in ranking_semear:
        op.pop('pagamentos_brutos', None)
    for op in ranking_agoracred:
        op.pop('pagamentos_brutos', None)

    # 11. Retorna o dicionário final com o formato exato esperado pelo frontend
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
            # Data máxima de pagamento do SEMEAR (usada no banner "Baixas até dia X")
            'ultima_baixa': ultima_baixa_semear,
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
            # Data máxima de pagamento do AGORACRED (usada no banner "Baixas até dia X")
            'ultima_baixa': ultima_baixa_agoracred,
        },
        'total_operacoes': total_ops,
        'operacoes_anterior': total_ops_ant,
        'ticket_medio': ticket_medio_grupo,
        'evolucao_operadores': evolucao_operadores
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


def buscar_pagamentos_individuais_adm(ano: int, mes: int, banco: str = 'TODOS', operador_filtro: str = 'TODOS', data_inicio: str = None, data_fim: str = None, atividade: str = 'ATIVO') -> Dict[str, Any]:
    """
    Busca pagamentos individuais (contrato a contrato) de todos os operadores
    filtrados pelo banco, operador e período selecionados.
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
                    'valorTotal': float(p.get('valorTotal', 0.0) or 0.0)
                })

    # Ordena por data de pagamento (descendente)
    pagamentos_filtrados.sort(key=lambda x: x.get('dtPgto', ''), reverse=True)

    return {
        'pagamentos': pagamentos_filtrados,
        'operadores': [{'login': l, 'imagem': img} for l, img in sorted(operadores_disponiveis.items())]
    }
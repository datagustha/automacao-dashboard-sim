"""
SERVIÇO DE CÁLCULOS E INDICADORES
==================================

ARQUIVO: analytics_service.py
LOCAL: src/services/

RESPONSABILIDADE:
- Calcular métricas e indicadores a partir dos dados de pagamento
- NENHUMA função aqui faz consulta direta ao banco
- Todas recebem os dados como parâmetro e calculam
- Usa PANDAS para cálculos eficientes
- Funciona com OBJETOS SQLAlchemy OU DICIONÁRIOS

ESTRUTURA DO ARQUIVO:
1. Funções auxiliares (_extrair_valor)
2. Indicadores básicos (faturamento, ticket, total)
3. Gráficos (faturamento por dia, pagamentos por fase)
4. Meta (buscar meta do mês, calcular percentual)
5. PERFORMANCE (nova) - para tabela de performance do operador
"""

import pandas as pd
from typing import List, Any, Dict
from datetime import datetime
import calendar


# ================================================================
# 1. FUNÇÕES AUXILIARES
# ================================================================

def _extrair_valor(pagamento, campo: str):
    """
    EXTRAI UM VALOR DE UM PAGAMENTO, SEJA OBJETO OU DICIONÁRIO.
    
    PASSO A PASSO:
    1. Verifica se é dicionário (acessa com colchetes)
    2. Se não for, assume que é objeto (acessa com ponto)
    3. Retorna o valor ou None se não existir
    
    ARGS:
        pagamento: Objeto SQLAlchemy ou dicionário
        campo: Nome do campo a extrair (ex: 'valorTotal')
    
    RETORNO:
        Valor do campo ou None
    """
    if isinstance(pagamento, dict):
        return pagamento.get(campo)
    else:
        return getattr(pagamento, campo, None)


def _contar_dias_uteis(ano: int, mes: int, data_referencia: datetime = None):
    """
    CALCULA QUANTOS DIAS ÚTEIS NO MÊS E QUANTOS JÁ PASSARAM.
    
    O QUE FAZ:
    - Dias úteis = segunda a sexta (não considera feriados)
    - Se data_referencia for fornecida, conta apenas dias ATÉ aquela data
    
    ARGS:
        ano: Ano (ex: 2026)
        mes: Mês (ex: 4 para Abril)
        data_referencia: Data para contar dias úteis até ela (opcional)
    
    RETORNO:
        tuple: (total_dias_uteis, dias_uteis_passados)
    """
    # Total de dias no mês
    total_dias = calendar.monthrange(ano, mes)[1]
    
    # Lista de dias úteis (segunda=0, sexta=4)
    dias_uteis = []
    for dia in range(1, total_dias + 1):
        if calendar.weekday(ano, mes, dia) < 5:  # 0-4 = segunda a sexta
            dias_uteis.append(dia)
    
    total_dias_uteis = len(dias_uteis)
    
    # Conta dias úteis até a data de referência
    if data_referencia:
        dias_uteis_passados = 0
        for dia in dias_uteis:
            if dia <= data_referencia.day:
                dias_uteis_passados += 1
        return total_dias_uteis, dias_uteis_passados
    
    return total_dias_uteis, total_dias_uteis


# ================================================================
# 2. INDICADORES BÁSICOS
# ================================================================

def calcular_indicadores_operador(pagamentos: List[Any]) -> Dict[str, Any]:
    """
    CALCULA OS PRINCIPAIS INDICADORES DE UM OPERADOR.
    
    IMPORTANTE: Exclui automaticamente pagamentos com fase "Fora da fase"
    
    ARGS:
        pagamentos: Lista de pagamentos (objetos ou dicionários)
    
    RETORNO:
        dict: {
            'total_pagamentos': int,
            'faturamento_total': float,
            'ticket_medio': float
        }
    """
    
    # VALIDAÇÃO: Se não tem pagamentos, retorna tudo zero
    if not pagamentos:
        print("[AVISO] Lista de pagamentos vazia")
        return {
            'total_pagamentos': 0,
            'faturamento_total': 0.0,
            'ticket_medio': 0.0
        }
    
    # ================================================================
    # FILTRO: Excluir pagamentos com fase "Fora da fase"
    # ================================================================
    pagamentos_filtrados = []
    for pag in pagamentos:
        fase = _extrair_valor(pag, 'faseAtraso')
        if fase != "Fora da fase":
            pagamentos_filtrados.append(pag)
    
    if not pagamentos_filtrados:
        print("[AVISO] Todos os pagamentos estão com fase 'Fora da fase'")
        return {
            'total_pagamentos': 0,
            'faturamento_total': 0.0,
            'ticket_medio': 0.0
        }
    
    print(f"[FILTRO] Removidos {len(pagamentos) - len(pagamentos_filtrados)} pagamentos 'Fora da fase'")
    
    # Converte para DataFrame
    dados = []
    for pag in pagamentos_filtrados:
        valor = _extrair_valor(pag, 'valorTotal')
        if valor is not None and isinstance(valor, (int, float)):
            dados.append({
                'valorTotal': float(valor),
                'dtPgto': _extrair_valor(pag, 'dtPgto')
            })
    
    if not dados:
        return {'total_pagamentos': 0, 'faturamento_total': 0.0, 'ticket_medio': 0.0}
    
    df = pd.DataFrame(dados)
    
    # Calcula indicadores
    faturamento_total = df['valorTotal'].sum()
    total_pagamentos = len(df)
    ticket_medio = df['valorTotal'].mean() if total_pagamentos > 0 else 0
    
    return {
        'total_pagamentos': total_pagamentos,
        'faturamento_total': round(faturamento_total, 2),
        'ticket_medio': round(ticket_medio, 2)
    }


# ================================================================
# 3. GRÁFICOS
# ================================================================

def calcular_faturamento_por_dia(pagamentos: List[Any]) -> pd.DataFrame:
    """Calcula o faturamento agrupado por dia (exclui 'Fora da fase')."""
    
    if not pagamentos:
        return pd.DataFrame(columns=['data', 'total'])
    
    # Filtra "Fora da fase"
    pagamentos_filtrados = []
    for pag in pagamentos:
        fase = _extrair_valor(pag, 'faseAtraso')
        if fase != "Fora da fase":
            pagamentos_filtrados.append(pag)
    
    if not pagamentos_filtrados:
        return pd.DataFrame(columns=['data', 'total'])
    
    dados = []
    for pag in pagamentos_filtrados:
        data = _extrair_valor(pag, 'dtPgto')
        valor = _extrair_valor(pag, 'valorTotal')
        if data and valor and isinstance(valor, (int, float)):
            dados.append({'data': data, 'valor': float(valor)})
    
    if not dados:
        return pd.DataFrame(columns=['data', 'total'])
    
    df = pd.DataFrame(dados)
    df['data'] = pd.to_datetime(df['data']).dt.date
    resultado = df.groupby('data')['valor'].sum().reset_index()
    resultado.columns = ['data', 'total']
    
    return resultado.sort_values('data')


def calcular_pagamentos_por_fase(pagamentos: List[Any]) -> pd.DataFrame:
    """Agrupa pagamentos por fase (exclui 'Fora da fase')."""
    
    if not pagamentos:
        return pd.DataFrame(columns=['fase', 'total'])
    
    dados = []
    for pag in pagamentos:
        fase = _extrair_valor(pag, 'faseAtraso')
        valor = _extrair_valor(pag, 'valorTotal')
        if fase and fase != "Fora da fase" and valor and isinstance(valor, (int, float)):
            fase_limpa = str(fase).replace("Fase ", "").strip()
            dados.append({'fase': fase_limpa, 'valor': float(valor)})
    
    if not dados:
        return pd.DataFrame(columns=['fase', 'total'])
    
    df = pd.DataFrame(dados)
    resultado = df.groupby('fase')['valor'].sum().reset_index()
    resultado.columns = ['fase', 'total']
    
    return resultado.sort_values('total', ascending=False)


# ================================================================
# 4. META
# ================================================================

def buscar_meta_do_mes(metas: list, ano: int, mes: int) -> float:
    """Retorna o valor da meta100 para o mês/ano especificado."""
    for meta in metas:
        data = meta['data']
        if isinstance(data, str):
            data = pd.to_datetime(data)
        if data.year == ano and data.month == mes:
            return meta.get('meta100', 0)
    return 0


def calcular_percentual_meta(faturamento: float, meta_valor: float) -> float:
    """Calcula o percentual da meta atingida."""
    if meta_valor <= 0:
        return 0.0
    return round((faturamento / meta_valor) * 100, 2)


# ================================================================
# 5. TABELA DE PERFORMANCE (NOVO)
# ================================================================

def calcular_performance_operador(
    pagamentos: List[Any], 
    metas: List[Any], 
    ano: int, 
    mes: int,
    login: str = None
) -> Dict[str, Any]:
    """
    CALCULA A PERFORMANCE COMPLETA DE UM OPERADOR PARA A TABELA.
    
    O QUE CALCULA:
    - faturamento: soma dos valores
    - feito_diario: faturamento / dias_uteis_trabalhados
    - meta: meta100 do mês
    - meta_diaria: meta / dias_uteis_totais
    - atingido_meta: percentual do faturamento em relação à meta
    - faltas: quanto falta para 70%, 80%, 90%, 100%
    - meta_ranking: meta de ranking
    - projecao: projeção de faturamento até fim do mês
    - projecao_percentual: percentual projetado
    
    ARGS:
        pagamentos: Lista de pagamentos do operador
        metas: Lista de metas do operador
        ano: Ano desejado
        mes: Mês desejado
        login: Login do operador (opcional)
    
    RETORNO:
        dict: Dicionário com todas as métricas
    """
    
    # ----------------------------------------------------------------
    # 1. FILTRA PAGAMENTOS DO MÊS (exclui "Fora da fase")
    # ----------------------------------------------------------------
    df = pd.DataFrame(pagamentos)
    df['dtPgto'] = pd.to_datetime(df['dtPgto'])
    
    df_mes = df[
        (df['dtPgto'].dt.month == mes) & 
        (df['dtPgto'].dt.year == ano)
    ].copy()
    
    # Exclui "Fora da fase"
    df_mes = df_mes[df_mes['faseAtraso'] != "Fora da fase"]
    
    # ----------------------------------------------------------------
    # 2. BUSCA META DO MÊS
    # ----------------------------------------------------------------
    meta_valor = buscar_meta_do_mes(metas, ano, mes)
    meta_ranking = 0
    for meta in metas:
        data = meta['data']
        if isinstance(data, str):
            data = pd.to_datetime(data)
        if data.year == ano and data.month == mes:
            meta_ranking = meta.get('meta_ranking', 0)
            break
    
    # ----------------------------------------------------------------
    # 3. CÁLCULO DE FATURAMENTO
    # ----------------------------------------------------------------
    faturamento = df_mes['valorTotal'].sum() if not df_mes.empty else 0.0
    
    # ----------------------------------------------------------------
    # 4. CÁLCULO DE DIAS ÚTEIS
    # ----------------------------------------------------------------
    # Última data de pagamento (para calcular dias trabalhados)
    ultima_data = df_mes['dtPgto'].max() if not df_mes.empty else datetime.now()
    
    # Dias úteis totais do mês
    total_dias_uteis, dias_trabalhados = _contar_dias_uteis(ano, mes, ultima_data)
    dias_restantes = total_dias_uteis - dias_trabalhados
    
    # ----------------------------------------------------------------
    # 5. CÁLCULO DAS MÉTRICAS
    # ----------------------------------------------------------------
    # Feito diário (média por dia trabalhado)
    feito_diario = faturamento / dias_trabalhados if dias_trabalhados > 0 else 0
    
    # Meta diária
    meta_diaria = meta_valor / total_dias_uteis if total_dias_uteis > 0 else 0
    
    # Percentual atingido da meta
    atingido_meta = (faturamento / meta_valor) * 100 if meta_valor > 0 else 0
    
    # Quanto falta para cada nível da meta (se positivo, mostra quanto falta)
    falta_70 = max(0, (meta_valor * 0.7) - faturamento)
    falta_80 = max(0, (meta_valor * 0.8) - faturamento)
    falta_90 = max(0, (meta_valor * 0.9) - faturamento)
    falta_100 = max(0, meta_valor - faturamento)
    
    # Projeção (se tiver dias restantes)
    if dias_restantes > 0 and feito_diario > 0:
        projecao = faturamento + (feito_diario * dias_restantes)
    else:
        projecao = faturamento
    
    projecao_percentual = (projecao / meta_valor) * 100 if meta_valor > 0 else 0
    
    # ----------------------------------------------------------------
    # 6. RETORNA DICIONÁRIO
    # ----------------------------------------------------------------
    return {
        'login': login,
        'faturamento': round(faturamento, 2),
        'feito_diario': round(feito_diario, 2),
        'meta': round(meta_valor, 2),
        'meta_diaria': round(meta_diaria, 2),
        'atingido_meta': round(atingido_meta, 2),
        'falta_70': round(falta_70, 2),
        'falta_80': round(falta_80, 2),
        'falta_90': round(falta_90, 2),
        'falta_100': round(falta_100, 2),
        'meta_ranking': round(meta_ranking, 2),
        'projecao': round(projecao, 2),
        'projecao_percentual': round(projecao_percentual, 2),
        'dias_trabalhados': dias_trabalhados,
        'dias_restantes': dias_restantes,
        'total_dias_uteis': total_dias_uteis
    }


def calcular_performance_todos_operadores(
    lista_pagamentos: List[tuple],  # lista de (operador, pagamentos, metas)
    ano: int,
    mes: int
) -> pd.DataFrame:
    """
    CALCULA A PERFORMANCE DE TODOS OS OPERADORES PARA A TABELA DO ADM.
    
    ARGS:
        lista_pagamentos: Lista de tuplas (operador_dict, pagamentos_list, metas_list)
        ano: Ano desejado
        mes: Mês desejado
    
    RETORNO:
        pd.DataFrame: DataFrame com performance de todos os operadores
    """
    resultados = []
    
    for operador, pagamentos, metas in lista_pagamentos:
        perf = calcular_performance_operador(
            pagamentos=pagamentos,
            metas=metas,
            ano=ano,
            mes=mes,
            login=operador.get('login')
        )
        # Adiciona turno e outros dados do operador
        perf['turno'] = operador.get('turno', '')
        resultados.append(perf)
    
    df = pd.DataFrame(resultados)
    
    # Ordena por faturamento decrescente
    if not df.empty:
        df = df.sort_values('faturamento', ascending=False)
    
    return df
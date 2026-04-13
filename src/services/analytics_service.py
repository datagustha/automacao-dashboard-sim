"""
SERVIÇO DE CÁLCULOS E INDICADORES
==================================

ARQUIVO: analytics_service.py
LOCAL: src/services/
"""

import pandas as pd
from typing import List, Any, Dict
from datetime import datetime, date
import calendar
import holidays


# ================================================================
# 1. FUNÇÕES AUXILIARES
# ================================================================

def _extrair_valor(pagamento, campo: str):
    """Extrai um valor de um pagamento, seja objeto ou dicionário."""
    if isinstance(pagamento, dict):
        return pagamento.get(campo)
    else:
        return getattr(pagamento, campo, None)


def _contar_dias_uteis(ano, mes, data_referencia: datetime = None):
    """Calcula quantos dias úteis no mês e quantos já passaram."""
    ano = int(ano)
    mes = int(mes)
    
    total_dias = calendar.monthrange(ano, mes)[1]
    
    feriados_br = holidays.country_holidays('BR', years=ano)
    
    dias_uteis = []
    for dia in range(1, total_dias + 1):
        data_atual = date(ano, mes, dia)
        if data_atual.weekday() < 5 and data_atual not in feriados_br:
            dias_uteis.append(dia)
    
    total_dias_uteis = len(dias_uteis)
    
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

def calcular_indicadores_operador(pagamentos: List[Any], banco: str = "SEMEAR") -> Dict[str, Any]:
    """
    CALCULA OS PRINCIPAIS INDICADORES DE UM OPERADOR.
    
    IMPORTANTE: 
    - Para SEMEAR: exclui pagamentos com fase "Fora da fase"
    - Para AGORACRED: considera todos os pagamentos
    """
    
    if not pagamentos:
        print("[AVISO] Lista de pagamentos vazia")
        return {
            'total_pagamentos': 0,
            'faturamento_total': 0.0,
            'ticket_medio': 0.0
        }
    
    # ================================================================
    # FILTRO: Excluir pagamentos com fase "Fora da fase" (apenas SEMEAR)
    # ================================================================
    if banco == "SEMEAR":
        pagamentos_filtrados = []
        for pag in pagamentos:
            fase = _extrair_valor(pag, 'faseAtraso')
            # Se a fase for "Fora da fase", exclui
            if fase == "Fora da fase":
                continue
            pagamentos_filtrados.append(pag)
        
        if not pagamentos_filtrados:
            print("[AVISO] Todos os pagamentos estão com fase 'Fora da fase'")
            return {
                'total_pagamentos': 0,
                'faturamento_total': 0.0,
                'ticket_medio': 0.0
            }
        
        print(f"[FILTRO] Removidos {len(pagamentos) - len(pagamentos_filtrados)} pagamentos 'Fora da fase'")
        pagamentos_para_calculo = pagamentos_filtrados
    else:
        # AGORACRED: considera todos os pagamentos (sem filtro)
        pagamentos_para_calculo = pagamentos
        print(f"[INFO] AGORACRED: considerando todos os {len(pagamentos)} pagamentos")
    
    # Converte para DataFrame
    dados = []
    for pag in pagamentos_para_calculo:
        valor = _extrair_valor(pag, 'valorTotal')
        if valor is not None and isinstance(valor, (int, float)):
            dados.append({
                'valorTotal': float(valor),
                'dtPgto': _extrair_valor(pag, 'dtPgto')
            })
    
    if not dados:
        return {'total_pagamentos': 0, 'faturamento_total': 0.0, 'ticket_medio': 0.0}
    
    df = pd.DataFrame(dados)
    
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

def calcular_faturamento_por_dia(pagamentos: List[Any], banco: str = "SEMEAR") -> pd.DataFrame:
    """Calcula o faturamento agrupado por dia."""
    
    if not pagamentos:
        return pd.DataFrame(columns=['data', 'total'])
    
    # Filtra "Fora da fase" apenas para SEMEAR
    if banco == "SEMEAR":
        pagamentos_filtrados = []
        for pag in pagamentos:
            fase = _extrair_valor(pag, 'faseAtraso')
            if fase != "Fora da fase":
                pagamentos_filtrados.append(pag)
        
        if not pagamentos_filtrados:
            return pd.DataFrame(columns=['data', 'total'])
        pagamentos_para_calculo = pagamentos_filtrados
    else:
        pagamentos_para_calculo = pagamentos
    
    dados = []
    for pag in pagamentos_para_calculo:
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


def calcular_pagamentos_por_fase(pagamentos: List[Any], banco: str = "SEMEAR") -> pd.DataFrame:
    """Agrupa pagamentos por fase."""
    
    if not pagamentos:
        return pd.DataFrame(columns=['fase', 'total'])
    
    dados = []
    for pag in pagamentos:
        fase = _extrair_valor(pag, 'faseAtraso')
        valor = _extrair_valor(pag, 'valorTotal')
        
        # Para SEMEAR, exclui "Fora da fase"
        if banco == "SEMEAR" and fase == "Fora da fase":
            continue
        
        if fase and valor and isinstance(valor, (int, float)):
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
# 5. TABELA DE PERFORMANCE
# ================================================================

def calcular_performance_operador(
    pagamentos: List[Any], 
    metas: List[Any], 
    ano: int, 
    mes: int,
    login: str = None,
    banco: str = "SEMEAR"
) -> Dict[str, Any]:
    """
    CALCULA A PERFORMANCE COMPLETA DE UM OPERADOR PARA A TABELA.
    """
    
    # ----------------------------------------------------------------
    # 1. FILTRA PAGAMENTOS DO MÊS
    # ----------------------------------------------------------------
    df = pd.DataFrame(pagamentos)
    df['dtPgto'] = pd.to_datetime(df['dtPgto'])
    
    df_mes = df[
        (df['dtPgto'].dt.month == mes) & 
        (df['dtPgto'].dt.year == ano)
    ].copy()
    
    # ================================================================
    # FILTRO: Excluir "Fora da fase" apenas para SEMEAR
    # ================================================================
    if banco == "SEMEAR":
        if 'faseAtraso' in df_mes.columns:
            df_mes = df_mes[df_mes['faseAtraso'] != "Fora da fase"]
        elif 'fase' in df_mes.columns:
            df_mes = df_mes[df_mes['fase'] != "Fora da fase"]
    
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
    ultima_data = df_mes['dtPgto'].max() if not df_mes.empty else datetime.now()
    
    total_dias_uteis, dias_trabalhados = _contar_dias_uteis(ano, mes, ultima_data)
    dias_restantes = total_dias_uteis - dias_trabalhados
    
    # ----------------------------------------------------------------
    # 5. CÁLCULO DAS MÉTRICAS
    # ----------------------------------------------------------------
    feito_diario = faturamento / dias_trabalhados if dias_trabalhados > 0 else 0
    meta_diaria = meta_valor / total_dias_uteis if total_dias_uteis > 0 else 0
    atingido_meta = (faturamento / meta_valor) * 100 if meta_valor > 0 else 0
    
    falta_70 = max(0, (meta_valor * 0.7) - faturamento)
    falta_80 = max(0, (meta_valor * 0.8) - faturamento)
    falta_90 = max(0, (meta_valor * 0.9) - faturamento)
    falta_100 = max(0, meta_valor - faturamento)
    
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
    lista_pagamentos: List[tuple],
    ano: int,
    mes: int
) -> pd.DataFrame:
    """Calcula a performance de todos os operadores para a tabela do ADM."""
    resultados = []
    
    for operador, pagamentos, metas in lista_pagamentos:
        perf = calcular_performance_operador(
            pagamentos=pagamentos,
            metas=metas,
            ano=ano,
            mes=mes,
            login=operador.get('login'),
            banco=operador.get('banco', 'SEMEAR')
        )
        perf['turno'] = operador.get('turno', '')
        resultados.append(perf)
    
    df = pd.DataFrame(resultados)
    
    if not df.empty:
        df = df.sort_values('faturamento', ascending=False)
    
    return df
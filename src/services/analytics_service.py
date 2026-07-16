"""
SERVIÇO DE CÁLCULOS E INDICADORES
==================================

ARQUIVO: analytics_service.py
LOCAL: src/services/
"""

import pandas as pd
from typing import List, Any, Dict, Optional
from datetime import datetime, date
import calendar
import holidays
from dateutil.relativedelta import relativedelta


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
    """Calcula quantos dias úteis no mês e quantos já passaram.
    Inclui Corpus Christi (feriado facultativo/estadual — 60 dias após a Páscoa).
    """
    from dateutil.easter import easter

    ano = int(ano)
    mes = int(mes)

    total_dias = calendar.monthrange(ano, mes)[1]

    feriados_br = holidays.country_holidays('BR', years=ano)
    # Corpus Christi: não incluso na lib como feriado nacional, mas amplamente observado
    from datetime import timedelta as _td
    corpus_christi = easter(ano) + _td(days=60)
    feriados_br.update({corpus_christi: "Corpus Christi"})

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
    resultado = resultado.sort_values('data')

    # IMPORTANTE: converte a coluna 'data' para string ISO (YYYY-MM-DD) ANTES de
    # retornar. Se deixarmos como objeto `date` do Python, o jsonify do Flask
    # pode serializar em formato RFC (ex: "Wed, 01 Jun 2026 00:00:00 GMT")
    # dependendo da versão/configuração — e o front-end (que espera "YYYY-MM-DD"
    # para fatiar em DD/MM) quebra e mostra a string inteira no gráfico.
    resultado['data'] = resultado['data'].apply(lambda d: d.strftime('%Y-%m-%d'))

    return resultado


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
    banco: str = "SEMEAR",
    data_referencia_banco: datetime = None
) -> Dict[str, Any]:
    """
    CALCULA A PERFORMANCE COMPLETA DE UM OPERADOR PARA A TABELA.
    """
    
    # ----------------------------------------------------------------
    # 1. FILTRA PAGAMENTOS DO MÊS
    # ----------------------------------------------------------------
    # Guard: se lista de pagamentos estiver vazia, retorna zeros imediatamente
    # Evita crash ao acessar df['dtPgto'] quando não há dados (ex: faixa filtrada sem registros)
    if not pagamentos:
        meta_valor = buscar_meta_do_mes(metas, ano, mes)
        return {
            'login': login,
            'faturamento': 0.0,
            'feito_diario': 0.0,
            'meta': round(meta_valor, 2),
            'meta_diaria': 0.0,
            'atingido_meta': 0.0,
            'falta_70': round(meta_valor * 0.7, 2),
            'falta_80': round(meta_valor * 0.8, 2),
            'falta_90': round(meta_valor * 0.9, 2),
            'falta_100': round(meta_valor, 2),
            'meta_ranking': 0.0,
            'projecao': 0.0,
            'projecao_percentual': 0.0,
            'dias_trabalhados': 0,
            'dias_restantes': 0,
            'total_dias_uteis': 0,
            'quantidade': 0,
            'ultima_baixa_banco': None,  # sem pagamentos, sem data máxima
        }

    # Cria DataFrame e converte a coluna de data de pagamento para datetime
    df = pd.DataFrame(pagamentos)

    # Guard: verifica se a coluna dtPgto exists antes de acessá-la
    # (pode faltar se o dicionário de pagamentos vier com estrutura incorreta)
    if 'dtPgto' not in df.columns:
        meta_valor = buscar_meta_do_mes(metas, ano, mes)
        return {
            'login': login,
            'faturamento': 0.0,
            'feito_diario': 0.0,
            'meta': round(meta_valor, 2),
            'meta_diaria': 0.0,
            'atingido_meta': 0.0,
            'falta_70': round(meta_valor * 0.7, 2),
            'falta_80': round(meta_valor * 0.8, 2),
            'falta_90': round(meta_valor * 0.9, 2),
            'falta_100': round(meta_valor, 2),
            'meta_ranking': 0.0,
            'projecao': 0.0,
            'projecao_percentual': 0.0,
            'dias_trabalhados': 0,
            'dias_restantes': 0,
            'total_dias_uteis': 0,
            'quantidade': 0,
            'ultima_baixa_banco': None,  # sem coluna de data, sem data máxima
        }

    # Converte a coluna dtPgto para datetime
    df['dtPgto'] = pd.to_datetime(df['dtPgto'])

    # Filtra apenas os pagamentos do mês e ano informados
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
    # Se uma data de referência global do banco foi fornecida, nós a priorizamos
    # para garantir consistência no feito_diario de todos os operadores daquele banco
    if data_referencia_banco is not None:
        ultima_data = data_referencia_banco
    else:
        ultima_data = df_mes['dtPgto'].max() if not df_mes.empty else datetime.now()

    # Formata a data máxima como string ISO para serialização
    if pd.notna(ultima_data):
        ultima_baixa_banco_str = ultima_data.strftime('%Y-%m-%d')
    else:
        ultima_baixa_banco_str = None

    total_dias_uteis, dias_trabalhados = _contar_dias_uteis(ano, mes, ultima_data)
    dias_restantes = total_dias_uteis - dias_trabalhados
    
    # Determina o dia corrido divisor baseado na última baixa do banco
    if pd.notna(ultima_data):
        dia_divisor = ultima_data.day
    else:
        import datetime as dt_lib
        dia_divisor = dt_lib.datetime.now().day

    # Calcula total de dias corridos no mês para projeção
    import calendar as cal_lib
    total_dias_corridos_mes = cal_lib.monthrange(ano, mes)[1]

    # ----------------------------------------------------------------
    # 5. CÁLCULO DAS MÉTRICAS (Unificado com Admin: por dia corrido da data máxima)
    # ----------------------------------------------------------------
    feito_diario = faturamento / dia_divisor if dia_divisor > 0 else 0.0
    meta_diaria = meta_valor / total_dias_uteis if total_dias_uteis > 0 else 0
    atingido_meta = (faturamento / meta_valor) * 100 if meta_valor > 0 else 0
    
    falta_70 = max(0, (meta_valor * 0.7) - faturamento)
    falta_80 = max(0, (meta_valor * 0.8) - faturamento)
    falta_90 = max(0, (meta_valor * 0.9) - faturamento)
    falta_100 = max(0, meta_valor - faturamento)
    
    # Projeção baseada no feito_diario corrido multiplicado pelo total de dias corridos do mês
    projecao = feito_diario * total_dias_corridos_mes
    projecao_percentual = (projecao / meta_valor) * 100 if meta_valor > 0 else 0
    
    # ----------------------------------------------------------------
    # 6. RETORNA DICIONÁRIO
    # ----------------------------------------------------------------
    quantidade = len(df_mes)
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
        'total_dias_uteis': total_dias_uteis,
        'quantidade': quantidade,
        # Data máxima de pagamento desse operador no mês — usada pelo serviço caller
        # para calcular o máximo do banco inteiro e usar como divisor do feito/dia
        'ultima_baixa_banco': ultima_baixa_banco_str,
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


# ================================================================
# 6. TEMPO DE CASA
# ================================================================

def calcular_tempo_de_casa(admissao) -> str:
    # Se a admissao for vazia ou nula, retorna formato padrao zerado
    if not admissao:
        # Retorna o texto indicando zero de tempo de casa
        return "0 anos, 0 meses, 0 dias"

    try:
        # Importa timedelta para manipulação de intervalo de dias
        from datetime import timedelta
        # Inicializa a variável que armazenará a data de admissão convertida
        admissao_dt = None
        
        # Se a admissão fornecida for do tipo string (texto)
        if isinstance(admissao, str):
            # Remove horas e espacos extras se houver (por exemplo, '2024-03-15 00:00:00' vira '2024-03-15')
            admissao_limpa = admissao.split(" ")[0].strip()
            # Loop pelos formatos de data suportados para conversao
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%Y-%m-%dT%H:%M:%S'):
                try:
                    # Tenta converter a string de admissão limpa no formato atual
                    admissao_dt = datetime.strptime(admissao_limpa, fmt).date()
                    # Se converter com sucesso, interrompe o loop
                    break
                except ValueError:
                    # Se der erro de formato, continua testando o próximo formato do loop
                    continue
            else:
                # Se nenhum formato der certo, tenta converter usando o método genérico do pandas
                admissao_dt = pd.to_datetime(admissao).date()
        # Se o objeto de admissão já tiver o método .date() (tipo datetime do python)
        elif hasattr(admissao, 'date'):
            # Converte e extrai apenas a parte da data
            admissao_dt = admissao.date()
        # Se o objeto já for do tipo date diretamente
        elif isinstance(admissao, date):
            # Atribui diretamente a data de admissão
            admissao_dt = admissao
        else:
            # Caso o tipo não seja suportado, retorna formato zerado padrão
            return "0 anos, 0 meses, 0 dias"

        # Obtém a data atual do sistema (hoje)
        hoje = date.today()
        # Calcula a data de hoje inclusiva (hoje + 1 dia) para incluir o dia de admissão e o dia atual
        hoje_inclusive = hoje + timedelta(days=1)
        # Calcula a diferença detalhada usando o relativedelta
        delta = relativedelta(hoje_inclusive, admissao_dt)

        # Formata a string de retorno estritamente no formato requisitado: X anos, Y meses, Z dias
        return f"{delta.years} anos, {delta.months} meses, {delta.days} dias"

    except Exception as e:
        # Imprime o erro no console de debug do sistema
        print(f"[ERRO] calcular_tempo_de_casa: {e}")
        # Retorna o formato zerado padrão em caso de exceção no cálculo
        return "0 anos, 0 meses, 0 dias"



# ================================================================
# 7. VISÃO POR SEMANA
# ================================================================

def calcular_semanas_do_mes(
    pagamentos: List[Any],
    ano: int,
    mes: int,
    banco: str = "SEMEAR"
) -> List[Dict]:
    """
    Agrupa o faturamento por semana do mês.

    REGRAS:
    - Semana 1: dias 01–07, Semana 2: 08–14, Semana 3: 15–21, Semana 4: 22–28,
      Semana 5: 29 até fim do mês (quando houver)
    - Exclui "Fora da fase" para SEMEAR
    - Retorna lista de dicts prontos para DataTable do Dash
    """
    if not pagamentos:
        return []

    df = pd.DataFrame(pagamentos)
    if df.empty or 'dtPgto' not in df.columns or 'valorTotal' not in df.columns:
        return []

    df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
    df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0.0)
    df = df.dropna(subset=['dtPgto'])

    # Filtra mês/ano
    df = df[(df['dtPgto'].dt.month == mes) & (df['dtPgto'].dt.year == ano)]

    # Remove "Fora da fase" para SEMEAR
    if banco == "SEMEAR" and 'faseAtraso' in df.columns:
        df = df[df['faseAtraso'] != 'Fora da fase']

    if df.empty:
        return []

    ultimo_dia_mes = calendar.monthrange(ano, mes)[1]

    # Define faixas de semanas (calendário fixo)
    faixas = [
        (1,  7),
        (8,  14),
        (15, 21),
        (22, 28),
        (29, ultimo_dia_mes),
    ]

    resultado = []
    for num, (inicio, fim) in enumerate(faixas, start=1):
        if inicio > ultimo_dia_mes:
            break

        fim_real = min(fim, ultimo_dia_mes)
        mascara = (df['dtPgto'].dt.day >= inicio) & (df['dtPgto'].dt.day <= fim_real)
        faturamento = float(df.loc[mascara, 'valorTotal'].sum())

        periodo = (
            f"{inicio:02d}/{mes:02d} a {fim_real:02d}/{mes:02d}"
        )

        resultado.append({
            'semana': f"Semana {num}",
            'periodo': periodo,
            'faturamento_raw': faturamento,
            'faturamento': (
                f"R$ {faturamento:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            ),
        })

    return resultado


# ================================================================
# 8. META DIÁRIA POR DIA (para a tabela Dia a Dia enriquecida)
# ================================================================

def calcular_meta_diaria_por_dia(
    pagamentos: List[Any],
    metas: List[Any],
    ano: int,
    mes: int,
    banco: str = "SEMEAR"
) -> List[Dict]:
    """
    Retorna lista com faturamento de cada dia do mês e indica se a meta
    diária foi atingida.

    REGRAS:
    - Meta diária = meta100 do mês / total de dias úteis do mês
    - Exclui "Fora da fase" para SEMEAR
    - Só inclui dias que tiveram pagamento
    - Retorna dicts prontos para DataTable
    """
    if not pagamentos:
        return []

    df = pd.DataFrame(pagamentos)
    if df.empty or 'dtPgto' not in df.columns or 'valorTotal' not in df.columns:
        return []

    df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
    df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0.0)
    df = df.dropna(subset=['dtPgto'])

    # Filtra mês/ano
    df = df[(df['dtPgto'].dt.month == mes) & (df['dtPgto'].dt.year == ano)]

    # Remove "Fora da fase" para SEMEAR
    if banco == "SEMEAR" and 'faseAtraso' in df.columns:
        df = df[df['faseAtraso'] != 'Fora da fase']

    if df.empty:
        return []

    # Busca meta do mês
    meta_total = buscar_meta_do_mes(metas, ano, mes) if metas else 0.0

    # Calcula total de dias úteis do mês
    from dateutil.easter import easter
    feriados_br = holidays.country_holidays('BR', years=ano)
    from datetime import timedelta as _td
    corpus_christi = easter(ano) + _td(days=60)
    feriados_br.update({corpus_christi: "Corpus Christi"})
    total_dias_mes = calendar.monthrange(ano, mes)[1]
    dias_uteis = [
        d for d in range(1, total_dias_mes + 1)
        if date(ano, mes, d).weekday() < 5 and date(ano, mes, d) not in feriados_br
    ]
    total_du = len(dias_uteis)
    meta_diaria = meta_total / total_du if total_du > 0 and meta_total > 0 else 0.0

    # Agrupa por dia
    df['dia'] = df['dtPgto'].dt.day
    por_dia = df.groupby('dia').agg(
        valorTotal=('valorTotal', 'sum'),
        quantidade=('valorTotal', 'count')
    ).reset_index()
    por_dia = por_dia.sort_values('dia')

    resultado = []
    for _, row in por_dia.iterrows():
        fat = float(row['valorTotal'])
        qtd = int(row['quantidade'])
        bateu = fat >= meta_diaria if meta_diaria > 0 else None

        resultado.append({
            'dia': int(row['dia']),
            'quantidade': qtd,
            'realizado': (
                f"R$ {fat:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            ),
            'meta_diaria': (
                f"R$ {meta_diaria:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
                if meta_diaria > 0 else "—"
            ),
            'meta_batida': (
                "✅ Sim" if bateu is True
                else ("❌ Não" if bateu is False else "—")
            ),
        })

    return resultado
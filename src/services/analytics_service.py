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
    # 5. CÁLCULO DAS MÉTRICAS (Unificado com Admin: por dia útil)
    # ----------------------------------------------------------------
    feito_diario = faturamento / dias_trabalhados if dias_trabalhados > 0 else 0.0
    meta_diaria = meta_valor / total_dias_uteis if total_dias_uteis > 0 else 0
    atingido_meta = (faturamento / meta_valor) * 100 if meta_valor > 0 else 0
    
    falta_70 = max(0, (meta_valor * 0.7) - faturamento)
    falta_80 = max(0, (meta_valor * 0.8) - faturamento)
    falta_90 = max(0, (meta_valor * 0.9) - faturamento)
    falta_100 = max(0, meta_valor - faturamento)
    
    # Projeção baseada no feito_diario (DU) multiplicado pelo total de dias úteis do mês
    projecao = feito_diario * total_dias_uteis
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
    banco: str = "SEMEAR",
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    du_inicio: Optional[int] = None,
    du_fim: Optional[int] = None,
    ultima_baixa_str: Optional[str] = None
) -> List[Dict]:
    """
    Retorna lista com faturamento de todos os dias úteis (segunda a sexta) do mês.
    Trunca no dia da última baixa do banco e respeita os filtros de data e DU.
    """
    # Mapeamento dos dias da semana em português abreviado
    DIAS_SEMANA_ABREV = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']

    # Busca meta do mês
    meta_total = buscar_meta_do_mes(metas, ano, mes) if metas else 0.0

    # Feriados BR + Corpus Christi
    from dateutil.easter import easter
    feriados_br = holidays.country_holidays('BR', years=ano)
    from datetime import timedelta as _td
    corpus_christi = easter(ano) + _td(days=60)
    feriados_br.update({corpus_christi: "Corpus Christi"})

    # Total de dias corridos no mês
    total_dias_mes = calendar.monthrange(ano, mes)[1]

    # Determina dia limite com base na última baixa
    max_dia_baixa = total_dias_mes
    if ultima_baixa_str:
        try:
            if '/' in ultima_baixa_str:
                parts = ultima_baixa_str.split('/')
                max_dia_baixa = int(parts[0])
            elif '-' in ultima_baixa_str:
                parts = ultima_baixa_str.split('-')
                max_dia_baixa = int(parts[2][:2])
        except Exception:
            pass

    # Prepara mapa de pagamentos por dia
    pagos_por_dia = {}
    qtd_por_dia = {}

    if pagamentos:
        df = pd.DataFrame(pagamentos)
        if not df.empty and 'dtPgto' in df.columns and 'valorTotal' in df.columns:
            # Converte data e valor
            df['dtPgto'] = pd.to_datetime(df['dtPgto'], errors='coerce')
            df['valorTotal'] = pd.to_numeric(df['valorTotal'], errors='coerce').fillna(0.0)
            df = df.dropna(subset=['dtPgto'])
            # Filtra mês e ano
            df = df[(df['dtPgto'].dt.month == mes) & (df['dtPgto'].dt.year == ano)]
            # Remove "Fora da fase" para SEMEAR
            if banco == "SEMEAR" and 'faseAtraso' in df.columns:
                df = df[df['faseAtraso'] != 'Fora da fase']

            if not df.empty:
                df['dia'] = df['dtPgto'].dt.day
                grouped = df.groupby('dia').agg(
                    valorTotal=('valorTotal', 'sum'),
                    quantidade=('valorTotal', 'count')
                ).reset_index()
                for _, row in grouped.iterrows():
                    pagos_por_dia[int(row['dia'])] = float(row['valorTotal'])
                    qtd_por_dia[int(row['dia'])] = int(row['quantidade'])

    # Mapeia dias úteis do mês (segunda a sexta)
    dias_uteis_list = []
    for d in range(1, total_dias_mes + 1):
        dt_obj = date(ano, mes, d)
        # Filtra apenas dias de segunda a sexta (weekday < 5)
        if dt_obj.weekday() < 5 and dt_obj not in feriados_br:
            dias_uteis_list.append(d)

    total_du = len(dias_uteis_list)
    meta_diaria = meta_total / total_du if total_du > 0 and meta_total > 0 else 0.0

    dt_ini_filter = datetime.strptime(data_inicio[:10], '%Y-%m-%d').date() if data_inicio else None
    dt_fim_filter = datetime.strptime(data_fim[:10], '%Y-%m-%d').date() if data_fim else None

    resultado = []
    du_contador = 0

    # Percorre os dias do mês até a última baixa do banco
    for d in range(1, max_dia_baixa + 1):
        dt_obj = date(ano, mes, d)
        # Considera apenas dias de segunda a sexta-feira
        if dt_obj.weekday() >= 5:
            continue

        # Filtro de data
        if dt_ini_filter and dt_obj < dt_ini_filter:
            continue
        if dt_fim_filter and dt_obj > dt_fim_filter:
            continue

        dia_semana_str = DIAS_SEMANA_ABREV[dt_obj.weekday()]
        data_formatada = f"{d:02d} - {dia_semana_str}"

        # Verifica se é dia útil sequencial
        if d in dias_uteis_list:
            du_contador += 1
            dia_util_str = f"{du_contador}º DU"
            # Filtro por DU
            if du_inicio is not None and du_contador < du_inicio:
                continue
            if du_fim is not None and du_contador > du_fim:
                continue
        else:
            dia_util_str = "Feriado"

        fat = pagos_por_dia.get(d, 0.0)
        qtd = qtd_por_dia.get(d, 0)

        # Status da meta batida
        if meta_diaria > 0:
            bateu = fat >= meta_diaria
            status_meta = "✅ Sim" if bateu else "❌ Não"
        else:
            status_meta = "—"

        resultado.append({
            'dia': d,
            'data_formatada': data_formatada,
            'dia_util': dia_util_str,
            'quantidade': qtd,
            'realizado_num': round(fat, 2),
            'realizado': (
                f"R$ {fat:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            ),
            'meta_diaria': (
                f"R$ {meta_diaria:,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
                if meta_diaria > 0 else "—"
            ),
            'meta_batida': status_meta,
        })

    return resultado


# ================================================================
# 9. COMPARATIVO TRIMESTRAL POR DIA ÚTIL (Segunda a Sexta)
# ================================================================

def montar_comparativo_trimestre_du(
    pagamentos: List[Any],
    ano: int,
    mes: int,
    banco: str = "SEMEAR",
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    du_inicio: Optional[int] = None,
    du_fim: Optional[int] = None,
    ultima_baixa_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Monta a matriz comparativa dos últimos 3 meses por dia útil (somente seg a sex).
    Exemplo: para Julho/2026, compara Julho (atual), Junho (M-1) e Maio (M-2).
    Suporta filtragem por data_inicio/data_fim e du_inicio/du_fim.
    Trunca no DU da última baixa real para não exibir dias futuros zerados.
    """
    DIAS_SEMANA_ABREV = ['seg', 'ter', 'qua', 'qui', 'sex', 'sáb', 'dom']

    # Define os 3 meses
    dt_atual = date(ano, mes, 1)
    dt_m1 = dt_atual - relativedelta(months=1)
    dt_m2 = dt_atual - relativedelta(months=2)

    meses_info = [
        {'ano': dt_atual.year, 'mes': dt_atual.month, 'nome': calendar.month_name[dt_atual.month]},
        {'ano': dt_m1.year, 'mes': dt_m1.month, 'nome': calendar.month_name[dt_m1.month]},
        {'ano': dt_m2.year, 'mes': dt_m2.month, 'nome': calendar.month_name[dt_m2.month]}
    ]

    MESES_PT = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    nome_m0 = MESES_PT[dt_atual.month - 1]
    nome_m1 = MESES_PT[dt_m1.month - 1]
    nome_m2 = MESES_PT[dt_m2.month - 1]

    # Prepara mapa de pagamentos por (ano, mes, dia_util)
    df_pg = pd.DataFrame(pagamentos or [])
    if not df_pg.empty and 'dtPgto' in df_pg.columns and 'valorTotal' in df_pg.columns:
        df_pg['dtPgto'] = pd.to_datetime(df_pg['dtPgto'], errors='coerce')
        df_pg['valorTotal'] = pd.to_numeric(df_pg['valorTotal'], errors='coerce').fillna(0.0)
        df_pg = df_pg.dropna(subset=['dtPgto'])
        if banco == "SEMEAR" and 'faseAtraso' in df_pg.columns:
            df_pg = df_pg[df_pg['faseAtraso'] != 'Fora da fase']
    else:
        df_pg = pd.DataFrame()

    # Mapeia faturamento por (mês_idx, du_num)
    fat_matriz = {0: {}, 1: {}, 2: {}}

    for idx_m, info in enumerate(meses_info):
        a_i, m_i = info['ano'], info['mes']
        total_dias = calendar.monthrange(a_i, m_i)[1]
        
        # Feriados
        feriados_br = holidays.country_holidays('BR', years=a_i)
        from dateutil.easter import easter
        from datetime import timedelta as _td
        feriados_br.update({easter(a_i) + _td(days=60): "Corpus Christi"})

        du_cont = 0
        for d in range(1, total_dias + 1):
            dt_o = date(a_i, m_i, d)
            if dt_o.weekday() < 5 and dt_o not in feriados_br:
                du_cont += 1
                if not df_pg.empty:
                    df_dia = df_pg[(df_pg['dtPgto'].dt.year == a_i) & (df_pg['dtPgto'].dt.month == m_i) & (df_pg['dtPgto'].dt.day == d)]
                    val_dia = float(df_dia['valorTotal'].sum()) if not df_dia.empty else 0.0
                else:
                    val_dia = 0.0
                fat_matriz[idx_m][du_cont] = {'val': val_dia, 'dia': d, 'wday': dt_o.weekday(), 'dt_obj': dt_o}

    # Encontra o DU da última baixa real do banco no mês atual (m0)
    limit_du_m0 = None
    if ultima_baixa_str:
        try:
            if '/' in ultima_baixa_str:
                p = ultima_baixa_str.split('/')
                dt_baixa_banco = date(int(p[2]), int(p[1]), int(p[0]))
            else:
                dt_baixa_banco = datetime.strptime(ultima_baixa_str[:10], '%Y-%m-%d').date()

            # Localiza o DU correspondente a essa data em m0
            # Se a última baixa for num fim de semana/feriado, pega o último DU válido antes dela
            for du_k in sorted(fat_matriz[0].keys()):
                if fat_matriz[0][du_k]['dt_obj'] <= dt_baixa_banco:
                    limit_du_m0 = du_k
        except Exception:
            pass

    linhas = []
    totais = {0: 0.0, 1: 0.0, 2: 0.0}

    # Se não houver filtro de data nem DU fornecido, trunca no DU da última baixa
    max_du = max(len(fat_matriz[0]), len(fat_matriz[1]), len(fat_matriz[2]), 22)
    if limit_du_m0 and not data_inicio and not data_fim and du_fim is None:
        max_du = limit_du_m0

    # Determina limites de DU para filtro por data ou por DU
    dt_ini_filter = datetime.strptime(data_inicio[:10], '%Y-%m-%d').date() if data_inicio else None
    dt_fim_filter = datetime.strptime(data_fim[:10], '%Y-%m-%d').date() if data_fim else None

    for du in range(1, max_du + 1):
        info_m0 = fat_matriz[0].get(du, {'val': 0.0, 'dia': 0, 'wday': 0, 'dt_obj': None})
        info_m1 = fat_matriz[1].get(du, {'val': 0.0, 'dia': 0, 'wday': 0, 'dt_obj': None})
        info_m2 = fat_matriz[2].get(du, {'val': 0.0, 'dia': 0, 'wday': 0, 'dt_obj': None})

        # Aplica filtro de DU se fornecido
        if du_inicio is not None and du < du_inicio:
            continue
        if du_fim is not None and du > du_fim:
            continue

        # Aplica filtro de data se fornecido (compara com a data do mês atual m0)
        if dt_ini_filter and info_m0['dt_obj'] and info_m0['dt_obj'] < dt_ini_filter:
            continue
        if dt_fim_filter and info_m0['dt_obj'] and info_m0['dt_obj'] > dt_fim_filter:
            continue

        v0, v1, v2 = info_m0['val'], info_m1['val'], info_m2['val']
        totais[0] += v0
        totais[1] += v1
        totais[2] += v2

        dia_str = f"{info_m0['dia']:02d} - {DIAS_SEMANA_ABREV[info_m0['wday']]}" if info_m0['dia'] > 0 else "—"

        linhas.append({
            'dia_util': f"{du}º DU",
            'data_atual': dia_str,
            'v_atual': round(v0, 2),
            'v_m1': round(v1, 2),
            'v_m2': round(v2, 2),
        })

    return {
        'colunas': [nome_m0, nome_m1, nome_m2],
        'linhas': linhas,
        'totais': {
            'total_atual': round(totais[0], 2),
            'total_m1': round(totais[1], 2),
            'total_m2': round(totais[2], 2),
        }
    }



# ================================================================
# 10. RELATÓRIO FAIXA DE ATRASO VS MÊS (Relatório SEMEAR)
# ================================================================

def montar_matriz_faixa_vs_mes(
    pagamentos: List[Any],
    ano: int,
    banco: str = "SEMEAR",
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    du_inicio: Optional[int] = None,
    du_fim: Optional[int] = None
) -> Dict[str, Any]:
    """
    Monta a matriz de Faixas de Atraso vs Mês (Jan a Dez + Total) para o SEMEAR.
    Exclusivo do banco SEMEAR. Suporta filtragem por período de data e dia útil.
    """
    MESES_ABREV = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    FAIXAS_PADRAO = [
        'Fase 10 a 30',
        'Fase 31 a 60',
        'Fase 61 a 90',
        'Fase 91 a 120',
        'Fase 121 a 180',
        'Fase 181 a 240',
        'Fase 241 a 360',
        'Fase 361 a 720',
        'Fase 721 a 1080',
        'Fase 1081 a 1440',
        'Fase 1441 a 1800',
        '> 1800'
    ]

    matriz = {faixa: {m: 0.0 for m in range(1, 13)} for faixa in FAIXAS_PADRAO}
    matriz['Outras Faixas'] = {m: 0.0 for m in range(1, 13)}

    if pagamentos:
        df_pg = pd.DataFrame(pagamentos)
        if not df_pg.empty and 'dtPgto' in df_pg.columns and 'valorTotal' in df_pg.columns:
            df_pg['dtPgto'] = pd.to_datetime(df_pg['dtPgto'], errors='coerce')
            df_pg['valorTotal'] = pd.to_numeric(df_pg['valorTotal'], errors='coerce').fillna(0.0)
            df_pg = df_pg.dropna(subset=['dtPgto'])

            # Filtra por data_inicio / data_fim se fornecido
            if data_inicio:
                dt_i = pd.to_datetime(data_inicio[:10])
                df_pg = df_pg[df_pg['dtPgto'] >= dt_i]
            if data_fim:
                dt_f = pd.to_datetime(data_fim[:10]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                df_pg = df_pg[df_pg['dtPgto'] <= dt_f]
            if not data_inicio and not data_fim:
                df_pg = df_pg[df_pg['dtPgto'].dt.year == ano]

            # Filtra por intervalo de Dia Útil (du_inicio / du_fim) se fornecido
            if du_inicio is not None or du_fim is not None:
                feriados_cache = {}
                def _du_valido(dt_ts):
                    try:
                        d_obj = dt_ts.date()
                        y_val = d_obj.year
                        if y_val not in feriados_cache:
                            feriados_cache[y_val] = holidays.country_holidays('BR', years=y_val)
                            from dateutil.easter import easter
                            from datetime import timedelta as _td
                            feriados_cache[y_val].update({easter(y_val) + _td(days=60): "Corpus Christi"})
                        
                        feriados = feriados_cache[y_val]
                        du_cnt = 0
                        for day in range(1, d_obj.day + 1):
                            temp_d = date(y_val, d_obj.month, day)
                            if temp_d.weekday() < 5 and temp_d not in feriados:
                                du_cnt += 1

                        if du_inicio is not None and du_cnt < du_inicio:
                            return False
                        if du_fim is not None and du_cnt > du_fim:
                            return False
                        return True
                    except Exception:
                        return False
                df_pg = df_pg[df_pg['dtPgto'].apply(_du_valido)]


            for _, row in df_pg.iterrows():
                fase_val = str(row.get('faseAtraso') or 'Outras Faixas').strip()
                if fase_val == 'Fora da fase':
                    continue
                
                # Normaliza nome da faixa
                faixa_chave = fase_val if fase_val in FAIXAS_PADRAO else 'Outras Faixas'
                m_num = int(row['dtPgto'].month)
                if 1 <= m_num <= 12:
                    matriz[faixa_chave][m_num] += float(row['valorTotal'])

    linhas = []
    totais_por_mes = {m: 0.0 for m in range(1, 13)}
    total_geral = 0.0

    for faixa, valores_mes in matriz.items():
        soma_faixa = sum(valores_mes.values())
        if soma_faixa == 0 and faixa == 'Outras Faixas':
            continue

        item_linha = {'faixa': faixa, 'total_ano': round(soma_faixa, 2)}
        for m in range(1, 13):
            val = valores_mes[m]
            item_linha[MESES_ABREV[m - 1]] = round(val, 2)
            totais_por_mes[m] += val
        
        total_geral += soma_faixa
        linhas.append(item_linha)

    linha_totais = {'faixa': 'TOTAL GERAL', 'total_ano': round(total_geral, 2)}
    for m in range(1, 13):
        linha_totais[MESES_ABREV[m - 1]] = round(totais_por_mes[m], 2)

    return {
        'ano': ano,
        'meses': MESES_ABREV,
        'linhas': linhas,
        'totais': linha_totais
    }
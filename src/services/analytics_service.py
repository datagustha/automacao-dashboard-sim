"""
SERVIÇO DE CÁLCULOS E INDICADORES
==================================
Este arquivo contém TODAS as funções que calculam métricas e indicadores.
As funções aqui RECEBEM os dados (vindos do db_service) e RETORNAM os cálculos.

REGRAS IMPORTANTES:
- NENHUMA função aqui faz consulta direta ao banco
- Todas recebem os dados como parâmetro e calculam
- Usamos PANDAS para facilitar os cálculos (você já conhece)
- Funciona com OBJETOS SQLAlchemy OU DICIONÁRIOS
"""

import pandas as pd
from typing import List, Any, Dict


def _extrair_valor(pagamento, campo: str):
    """
    Função auxiliar que extrai um valor de um pagamento,
    seja ele um objeto SQLAlchemy ou um dicionário.
    
    PASSO A PASSO:
    1. Verifica se é dicionário (acessa com colchetes)
    2. Se não for, assume que é objeto (acessa com ponto)
    3. Retorna o valor ou None se não existir
    """
    if isinstance(pagamento, dict):
        # É um dicionário: usa .get() para ser seguro
        return pagamento.get(campo)
    else:
        # É um objeto: usa hasattr para verificar se o atributo existe
        return getattr(pagamento, campo, None)


def calcular_indicadores_operador(pagamentos: List[Any]) -> Dict[str, Any]:
    """
    Calcula os principais indicadores de um operador a partir da lista de pagamentos.
    
    Funciona com:
    - Lista de objetos SQLAlchemy (pagamento.valorTotal)
    - Lista de dicionários (pagamento['valorTotal'])
    
    Args:
        pagamentos (list): Lista de pagamentos (objetos ou dicionários)
        
    Returns:
        dict: Dicionário com os indicadores calculados
    """
    
    # VALIDAÇÃO: Se não tem pagamentos, retorna tudo zero
    if not pagamentos:
        print("[AVISO] Lista de pagamentos vazia")
        return {
            'total_pagamentos': 0,
            'faturamento_total': 0.0,
            'ticket_medio': 0.0
        }
    
    # PASSO 1: Converte para DataFrame do Pandas de forma segura
    dados = []
    for pag in pagamentos:
        # Extrai o valorTotal (funciona com objeto ou dicionário)
        valor = _extrair_valor(pag, 'valorTotal')
        
        # Só adiciona se o valor for numérico
        if valor is not None and isinstance(valor, (int, float)):
            dados.append({
                'valorTotal': float(valor),
                'cliente': _extrair_valor(pag, 'cliente') or 'Desconhecido',
                'dtPgto': _extrair_valor(pag, 'dtPgto'),
                'fase': _extrair_valor(pag, 'fase') or 'Sem fase'
            })
    
    # Se não conseguiu extrair nenhum valor
    if not dados:
        print("[AVISO] Não foi possível extrair valores dos pagamentos")
        return {
            'total_pagamentos': 0,
            'faturamento_total': 0.0,
            'ticket_medio': 0.0
        }
    
    # Cria o DataFrame
    df = pd.DataFrame(dados)
    
    # PASSO 2: Calcula os indicadores
    faturamento_total = df['valorTotal'].sum()
    total_pagamentos = len(df)
    ticket_medio = df['valorTotal'].mean()
    
    # Arredonda para 2 casas decimais
    faturamento_total = round(faturamento_total, 2)
    ticket_medio = round(ticket_medio, 2)
    
    print(f"[OK] Calculado: {total_pagamentos} pagamentos, R$ {faturamento_total:,.2f}")
    
    return {
        'total_pagamentos': total_pagamentos,
        'faturamento_total': faturamento_total,
        'ticket_medio': ticket_medio
    }


def calcular_faturamento_por_dia(pagamentos: List[Any]) -> pd.DataFrame:
    """
    Calcula o faturamento agrupado por dia para fazer gráfico de evolução.
    
    Funciona com:
    - Lista de objetos SQLAlchemy (pagamento.dtPgto, pagamento.valorTotal)
    - Lista de dicionários (pagamento['dtPgto'], pagamento['valorTotal'])
    
    Args:
        pagamentos (list): Lista de objetos PgtoSemearBoleto ou dicionários
        
    Returns:
        pd.DataFrame: DataFrame com colunas 'data' e 'total'
    """
    
    if not pagamentos:
        print("[AVISO] Lista de pagamentos vazia")
        return pd.DataFrame(columns=['data', 'total'])
    
    # PASSO 1: Converte para DataFrame
    dados = []
    for pag in pagamentos:
        # Extrai a data (funciona com objeto ou dicionário)
        data = _extrair_valor(pag, 'dtPgto')
        valor = _extrair_valor(pag, 'valorTotal')
        
        # Só adiciona se tiver data e valor válido
        if data is not None and valor is not None and isinstance(valor, (int, float)):
            dados.append({
                'data': data,
                'valor': float(valor)
            })
    
    if not dados:
        print("[AVISO] Nenhum pagamento com data e valor válidos")
        return pd.DataFrame(columns=['data', 'total'])
    
    # PASSO 2: Cria DataFrame
    df = pd.DataFrame(dados)
    
    # PASSO 3: Converte data para datetime
    df['data'] = pd.to_datetime(df['data'])
    
    # PASSO 4: Extrai só a data (sem hora)
    df['data'] = df['data'].dt.date
    
    # PASSO 5: Agrupa por dia e soma
    resultado = df.groupby('data')['valor'].sum().reset_index()
    resultado.columns = ['data', 'total']
    resultado = resultado.sort_values('data')
    
    print(f"[OK] Gráfico: {len(resultado)} dias de faturamento")
    return resultado
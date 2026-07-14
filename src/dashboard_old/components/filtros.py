"""
FILTROS CENTRALIZADOS DO DASHBOARD
====================================
Módulo que centraliza:
- Constantes compartilhadas (MESES, ANOS, FASES)
- Componente visual DatePickerRange reutilizável
- Função de filtragem de datas usada por todos os callbacks

REGRA DE PRIORIDADE:
    Se o usuário preencher data_inicio E data_fim → usa o range de datas
    Se qualquer um estiver vazio → usa o filtro mês/ano tradicional

⚠️ IMPORTANTE:
    Todos os layouts e callbacks devem importar deste módulo para
    evitar duplicação de listas (meses, anos, fases).
"""

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_iconify import DashIconify
from datetime import date, datetime


# ================================================================
# CONSTANTES COMPARTILHADAS
# ================================================================

def get_anos():
    """Retorna lista de opções de anos para dropdowns."""
    return [{"label": str(ano), "value": ano} for ano in range(2020, date.today().year + 2)]

MESES = [
    {"label": "Janeiro",   "value": 1},  {"label": "Fevereiro", "value": 2},
    {"label": "Março",     "value": 3},  {"label": "Abril",     "value": 4},
    {"label": "Maio",      "value": 5},  {"label": "Junho",     "value": 6},
    {"label": "Julho",     "value": 7},  {"label": "Agosto",    "value": 8},
    {"label": "Setembro",  "value": 9},  {"label": "Outubro",   "value": 10},
    {"label": "Novembro",  "value": 11}, {"label": "Dezembro",  "value": 12},
]

OPCOES_FASES = [
    {"label": "📊 Todas as fases", "value": "todas"},
    {"label": "📈 Fase 10 a 30", "value": "Fase 10 a 30"},
    {"label": "📈 Fase 31 a 60", "value": "Fase 31 a 60"},
    {"label": "📈 Fase 61 a 90", "value": "Fase 61 a 90"},
    {"label": "📈 Fase 91 a 120", "value": "Fase 91 a 120"},
    {"label": "📈 Fase 121 a 180", "value": "Fase 121 a 180"},
    {"label": "📈 Fase 181 a 240", "value": "Fase 181 a 240"},
    {"label": "📈 Fase 241 a 360", "value": "Fase 241 a 360"},
    {"label": "📈 Fase 361 a 720", "value": "Fase 361 a 720"},
    {"label": "📈 Fase 721 a 1080", "value": "Fase 721 a 1080"},
    {"label": "📈 Fase 1081 a 1440", "value": "Fase 1081 a 1440"},
    {"label": "📈 Fase 1081 a 1800", "value": "Fase 1081 a 1800"},
    {"label": "📈 Fase 1441 a 1800", "value": "Fase 1441 a 1800"},
    {"label": "📈 Fase 1801 a 9999", "value": "Fase 1801 a 9999"},
    {"label": "🚫 Fora da fase", "value": "Fora da fase"},
]

# Versão com valores em MAIÚSCULO (usada na tela de pagamentos)
OPCOES_FASES_PGTOS = [
    {"label": "📊 Todas as fases", "value": "TODAS"},
    {"label": "📈 Fase 10 a 30", "value": "Fase 10 a 30"},
    {"label": "📈 Fase 31 a 60", "value": "Fase 31 a 60"},
    {"label": "📈 Fase 61 a 90", "value": "Fase 61 a 90"},
    {"label": "📈 Fase 91 a 120", "value": "Fase 91 a 120"},
    {"label": "📈 Fase 121 a 180", "value": "Fase 121 a 180"},
    {"label": "📈 Fase 181 a 240", "value": "Fase 181 a 240"},
    {"label": "📈 Fase 241 a 360", "value": "Fase 241 a 360"},
    {"label": "📈 Fase 361 a 720", "value": "Fase 361 a 720"},
    {"label": "📈 Fase 721 a 1080", "value": "Fase 721 a 1080"},
    {"label": "📈 Fase 1081 a 1440", "value": "Fase 1081 a 1440"},
    {"label": "📈 Fase 1081 a 1800", "value": "Fase 1081 a 1800"},
    {"label": "📈 Fase 1441 a 1800", "value": "Fase 1441 a 1800"},
    {"label": "📈 Fase 1801 a 9999", "value": "Fase 1801 a 9999"},
    {"label": "🚫 Fora da fase", "value": "Fora da fase"},
]


# ================================================================
# COMPONENTE VISUAL: DatePickerRange
# ================================================================

def criar_filtro_data_range(id_prefix: str):
    """
    Cria o componente DatePickerRange com estilo consistente.
    
    Args:
        id_prefix: Prefixo para os IDs (ex: '' → 'filtro-data-inicio',
                   'adm' → 'filtro-data-inicio-adm')
    
    Returns:
        html.Div contendo o DatePickerRange e um badge de status
    """
    sufixo = f"-{id_prefix}" if id_prefix else ""
    
    return html.Div(
        [
            html.Label(
                [
                    DashIconify(icon="lucide:calendar-range", width=14, className="me-1"),
                    "Intervalo de Datas"
                ],
                className="fw-bold mb-1",
                style={"color": "var(--text-muted)", "fontSize": "13px"}
            ),
            dcc.DatePickerRange(
                id=f"filtro-data-range{sufixo}",
                start_date_placeholder_text="Início",
                end_date_placeholder_text="Fim",
                display_format="DD/MM/YYYY",
                month_format="MM/YYYY",
                clearable=True,
                with_portal=False,
                first_day_of_week=1,  # Segunda-feira
                minimum_nights=0,     # Permite mesmo dia
                style={"width": "100%", "display": "flex", "alignItems": "center"},
                className="dash-date-range",
            ),
            # Badge indicando que o filtro de range está ativo
            html.Div(
                id=f"badge-data-range{sufixo}",
                children=html.Small(
                    [
                        DashIconify(icon="lucide:info", width=12, className="me-1"),
                        "Range Ativo"
                    ],
                    className="badge-data-range-ativo"
                ),
                style={"display": "none"}  # Oculto por padrão
            ),
        ],
        className="filtro-data-range-container w-100",
    )


# ================================================================
# FUNÇÃO DE FILTRAGEM CENTRALIZADA
# ================================================================

def aplicar_filtro_data(df, mes, ano, data_inicio, data_fim, coluna='dtPgto'):
    """
    Filtra o DataFrame por intervalo de datas OU por mês/ano.
    
    REGRA DE PRIORIDADE:
        - Se data_inicio E data_fim estão preenchidos → usa range
        - Caso contrário → usa mês/ano
    
    Args:
        df: DataFrame com coluna de data
        mes: Mês selecionado no dropdown (int ou str)
        ano: Ano selecionado no dropdown (int ou str)
        data_inicio: Data início do range (str 'YYYY-MM-DD' ou None)
        data_fim: Data fim do range (str 'YYYY-MM-DD' ou None)
        coluna: Nome da coluna de data no DataFrame
    
    Returns:
        tuple: (df_filtrado, usando_range: bool, label_periodo: str)
    """
    if coluna not in df.columns:
        return df, False, ""
    
    # Garante que a coluna é datetime
    df[coluna] = pd.to_datetime(df[coluna], errors='coerce')
    df = df.dropna(subset=[coluna])
    
    if df.empty:
        return df, False, ""
    
    # PRIORIDADE: Range de datas (se ambos preenchidos)
    if data_inicio and data_fim:
        try:
            dt_inicio = pd.to_datetime(data_inicio)
            dt_fim = pd.to_datetime(data_fim)
            
            # Garante que dt_fim inclui o dia inteiro
            dt_fim = dt_fim + pd.Timedelta(hours=23, minutes=59, seconds=59)
            
            df_filtrado = df[
                (df[coluna] >= dt_inicio) & 
                (df[coluna] <= dt_fim)
            ].copy()
            
            label = f"{dt_inicio.strftime('%d/%m/%Y')} a {(dt_fim - pd.Timedelta(hours=23, minutes=59, seconds=59)).strftime('%d/%m/%Y')}"
            return df_filtrado, True, label
        except Exception:
            # Se falhar o parse, cai no filtro por mês/ano
            pass
    
    # FALLBACK: Filtro por mês/ano
    mes_int = int(mes) if mes else datetime.now().month
    ano_int = int(ano) if ano else datetime.now().year
    
    df_filtrado = df[
        (df[coluna].dt.month == mes_int) & 
        (df[coluna].dt.year == ano_int)
    ].copy()
    
    label = f"{mes_int}/{ano_int}"
    return df_filtrado, False, label


def obter_mes_ano_do_range(data_inicio, data_fim):
    """
    Extrai mês e ano de um range de datas para uso em cálculos
    que precisam de mês/ano (como metas).
    
    Retorna o mês/ano da data_inicio quando o range está ativo.
    
    Args:
        data_inicio: Data início (str 'YYYY-MM-DD' ou None)
        data_fim: Data fim (str 'YYYY-MM-DD' ou None)
    
    Returns:
        tuple: (mes: int, ano: int) ou None se range não está ativo
    """
    if data_inicio and data_fim:
        try:
            dt = pd.to_datetime(data_inicio)
            return dt.month, dt.year
        except Exception:
            return None
    return None

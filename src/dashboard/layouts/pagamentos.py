"""
LAYOUT EXCLUSIVAMENTE PARA VISUALIZAÇÃO DE PAGAMENTOS
======================================================
- Operador: vê só seus próprios pagamentos do mês selecionado
- ADM: vê todos os pagamentos do banco selecionado por mês

🔧 CORREÇÕES APLICADAS:
  1. container_tabela_cheia com fixed_cols=0 para não travar
  2. Adicionado badge de data range
  3. Try/except no layout
  4. Debounce no input de busca
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_iconify import DashIconify

from src.dashboard.components.menus import get_sidebar, get_header
from src.dashboard.components.tabelas import container_tabela_cheia

from src.dashboard.components.filtros import (
    criar_filtro_data_range,
    MESES,
    get_anos,
    OPCOES_FASES_PGTOS,
)

# Usaremos o OPCOES_FASES_PGTOS
OPCOES_FASES = OPCOES_FASES_PGTOS


def get_pagamentos_layout(
    nome_usuario: str,
    imagem_url: str = None,
    perfil: str = "operador",
    admissao: str = None,
):
    """
    Constrói o layout de pagamentos.

    Args:
        nome_usuario: Nome do usuário logado
        imagem_url: URL da foto
        perfil: 'adm' ou 'operador' — ADM tem seletor de banco
        admissao: Data de admissão do usuário logado
    
    🔧 CORREÇÃO: Try/except para evitar crash se algo falhar
    """
    try:
        # ============================================================
        # VALIDAÇÕES INICIAIS
        # ============================================================
        # Garante que perfil é válido
        if perfil not in ['adm', 'operador']:
            perfil = 'operador'
        
        # Garante que nome_usuario existe
        if not nome_usuario:
            nome_usuario = "Usuário"
        
        # ============================================================
        # CONSTRÓI O LAYOUT
        # ============================================================
        
        # Cria o menu lateral (sidebar) destacado na rota 'pagamentos'
        sidebar = get_sidebar("pagamentos", perfil=perfil)

        # FILTROS: MÊS e ANO (para ambos perfis)
        from datetime import datetime

        mes_atual = datetime.now().month
        ano_atual = datetime.now().year

        # === LINHA DE FILTROS: MÊS/ANO + DATA RANGE + FASE ===
        filtros_data = dbc.Row(
            [
                # FILTRO MÊS/ANO
                dbc.Col(
                    [
                        html.Label(
                            "Mês/Ano",
                            className="fw-bold mb-1",
                            style={"color": "var(--text-muted)", "fontSize": "13px"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="filtro-mes-pgtos",
                                        options=MESES,
                                        value=mes_atual,
                                        clearable=False,
                                        style={"borderRadius": "8px"},
                                    ),
                                    width=6,
                                    className="pe-1",
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="filtro-ano-pgtos",
                                        options=get_anos(),
                                        value=ano_atual,
                                        clearable=False,
                                        style={"borderRadius": "8px"},
                                    ),
                                    width=6,
                                    className="ps-1",
                                ),
                            ]
                        ),
                    ],
                    width=3,
                ),
                # FILTRO DATA RANGE
                dbc.Col(
                    criar_filtro_data_range("pgtos"), 
                    width=4
                ),
                # FILTRO DE FASE - MULTIPLA SELEÇÃO
                dbc.Col(
                    [
                        html.Label(
                            "Fase (múltipla seleção)",
                            className="fw-bold mb-1",
                            style={"color": "var(--text-muted)", "fontSize": "13px"},
                        ),
                        dcc.Dropdown(
                            id="filtro-fase-pgtos",
                            options=OPCOES_FASES,
                            value=["TODAS"],
                            multi=True,
                            clearable=True,
                            placeholder="Selecione uma ou mais fases...",
                            style={"borderRadius": "8px", "minWidth": "250px"},
                        ),
                    ],
                    width=5,
                ),
            ],
            className="mb-4 align-items-start",
        )

        # === SELETOR DE BANCO (só aparece para ADM) ===
        seletor_banco = (
            html.Div(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label(
                                    "Banco",
                                    className="fw-bold mb-1",
                                    style={
                                        "color": "var(--text-muted)",
                                        "fontSize": "13px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="banco-selecionado-pgtos",
                                    options=[
                                        {"label": "🟣 SEMEAR", "value": "SEMEAR"},
                                        {"label": "🔵 AGORACRED", "value": "AGORACRED"},
                                    ],
                                    value="SEMEAR",
                                    clearable=False,
                                    style={"borderRadius": "8px", "minWidth": "200px"},
                                ),
                            ],
                            width="auto",
                        ),
                        dbc.Col(
                            [
                                html.Label(
                                    "Atividade",
                                    className="fw-bold mb-1",
                                    style={
                                        "color": "var(--text-muted)",
                                        "fontSize": "13px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="adm-filtro-atividade-pgtos",
                                    options=[
                                        {"label": "🟢 Apenas Ativos", "value": "ativo"},
                                        {"label": "⚪ Todos", "value": "todos"},
                                    ],
                                    value="ativo",
                                    clearable=False,
                                    style={"borderRadius": "8px", "minWidth": "150px"},
                                ),
                            ],
                            width="auto",
                        ),
                    ],
                    className="mb-3 align-items-end",
                )
            )
            if perfil == "adm"
            else html.Div(
                [
                    # Dropdowns ocultos para operador (mantém os IDs no DOM)
                    dcc.Dropdown(
                        id="banco-selecionado-pgtos",
                        value="SEMEAR",
                        options=[],
                        style={"display": "none"},
                    ),
                    dcc.Dropdown(
                        id="adm-filtro-atividade-pgtos",
                        value="ativo",
                        options=[],
                        style={"display": "none"},
                    ),
                ]
            )
        )

        # === BADGE DE DATA RANGE (inicialmente oculto) ===
        badge_data_range = html.Div(
            id="badge-data-range-pgtos",
            children=[
                DashIconify(icon="lucide:calendar", width=14, style={"marginRight": "6px"}),
                html.Span("Intervalo personalizado", style={"fontSize": "12px"})
            ],
            style={
                "display": "none",
                "backgroundColor": "#e9d8fd",
                "color": "#4a1d8c",
                "padding": "6px 12px",
                "borderRadius": "20px",
                "fontWeight": "600",
                "fontSize": "12px",
                "marginTop": "8px",
                "alignItems": "center",
                "width": "fit-content"
            }
        )

        # === CONTEÚDO PRINCIPAL ===
        conteudo = html.Div(
            [
                # Renderiza o header superior
                get_header(
                    nome_usuario,
                    imagem_url,
                    "📋 Controle Geral de Pagamentos",
                    admissao=admissao,
                    perfil=perfil,
                ),
                
                # Badge de data range
                badge_data_range,
                
                # Filtros de data e fase
                filtros_data,
                
                # Seletor de banco (ADM)
                seletor_banco,
                
                # Filtro de texto (busca)
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(
                                        DashIconify(
                                            icon="lucide:search",
                                            width=18,
                                            color="var(--text-muted)",
                                        ),
                                        style={
                                            "backgroundColor": "white",
                                            "borderRight": "none",
                                        },
                                    ),
                                    dbc.Input(
                                        id="filtro-texto-pgtos-completo",
                                        type="text",
                                        placeholder="🔍 Filtrar por Contrato, Cliente ou Fase...",
                                        style={"borderLeft": "none"},
                                        debounce=True,
                                    ),
                                ],
                                className="shadow-sm",
                                style={"borderRadius": "8px"},
                            ),
                            width=12,
                        )
                    ],
                    className="mb-3",
                ),
                
                # Tabela de pagamentos - fixed_cols=0 para evitar erro
                dbc.Row(
                    [
                        dbc.Col(
                            container_tabela_cheia(
                                "tabela-pagamentos-completa",
                                fixed_cols=0,
                                page_size=30
                            ),
                            width=12
                        )
                    ]
                ),
                
                # Intervalo de atualização automática (5 minutos)
                dcc.Interval(
                    id="intervalo-atualizacao-pgtos", 
                    interval=300 * 1000,  # 5 minutos
                    n_intervals=0
                ),
            ],
            className="main-content",
            style={
                "marginLeft": "260px",
                "minHeight": "100vh",
                "padding": "24px 32px",
                "boxSizing": "border-box",
            },
        )

        return html.Div([sidebar, conteudo])
    
    except Exception as e:
        # ⚠️ ERRO AO CONSTRUIR LAYOUT
        print(f"[PAGAMENTOS] ❌ Erro ao construir layout: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Retorna um layout de erro amigável
        return html.Div(
            [
                html.Div(
                    [
                        html.H2("❌ Erro ao carregar página de pagamentos", 
                                style={"color": "#dc3545", "textAlign": "center", "padding": "20px"}),
                        html.P(
                            f"Detalhes: {str(e)}", 
                            style={"textAlign": "center", "color": "#666", "padding": "0 20px"}
                        ),
                        html.Hr(style={"margin": "20px 0"}),
                        html.Div(
                            [
                                dbc.Button(
                                    "🔄 Tentar novamente",
                                    href="/pagamentos",
                                    color="primary",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "🏠 Voltar ao Dashboard",
                                    href="/dashboard",
                                    color="secondary",
                                ),
                            ],
                            style={"textAlign": "center", "padding": "20px"}
                        ),
                        html.P(
                            "Se o problema persistir, entre em contato com o suporte.",
                            style={"textAlign": "center", "color": "#999", "fontSize": "14px", "marginTop": "20px"}
                        )
                    ],
                    className="card shadow-sm",
                    style={
                        "maxWidth": "600px",
                        "margin": "100px auto",
                        "padding": "40px",
                        "borderRadius": "12px",
                        "backgroundColor": "white"
                    }
                )
            ],
            style={
                "minHeight": "100vh",
                "backgroundColor": "#f8f9fa",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center"
            }
        )
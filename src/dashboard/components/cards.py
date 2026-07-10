import dash_bootstrap_components as dbc
from dash import html
from dash_iconify import DashIconify


def card_indicador(titulo: str, valor_default: str, id_valor: str, cor_icone: str, icon_name: str, id_sub_texto: str = None):
    """
    Card simples para indicadores (Operações, Ticket Médio)
    """
    children = [
        # Cabeçalho: ícone + título numa linha
        html.Div(
            [
                html.Div(DashIconify(icon=icon_name, width=24, color=cor_icone), style={"flexShrink": "0"}),
                html.H6(titulo, id=f"title-{id_valor}" if id_valor else None, className="kpi-title", style={
                    "fontSize": "11px", "fontWeight": "700", "margin": "0",
                    "letterSpacing": "0.5px", "color": "var(--text-muted)"
                }),
            ],
            style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "14px"}
        ),
        # Valor principal
        html.Div(
            html.H3(valor_default, id=id_valor, className="kpi-value", style={"marginBottom": "0"}),
            style={"marginBottom": "10px"}
        ),
    ]

    if id_sub_texto:
        children.append(
            html.Div(
                id=id_sub_texto,
                className="kpi-subtext",
                style={
                    "fontSize": "12px", "color": "var(--text-muted)",
                    "borderTop": "1px solid #f0f0f0", "paddingTop": "10px", "marginTop": "4px"
                }
            )
        )
    else:
        children.append(html.Div(style={"height": "33px"}))

    return html.Div(children, className="card-kpi", style={"padding": "20px"})


def card_meta(titulo: str, id_meta_objetivo: str, id_barra: str, id_percentual: str, cor_icone: str = "#f59e0b"):
    """
    Cria um card de meta com barra de progresso (versão simplificada).
    """
    children = [
        html.Div(DashIconify(icon="lucide:target", width=32, color=cor_icone), style={"textAlign": "center"}),
        html.H6(titulo, className="kpi-title"),
        html.H3(id=id_meta_objetivo, className="kpi-value"),
        html.Div(
            style={
                "width": "100%",
                "backgroundColor": "#e5e7eb",
                "borderRadius": "4px",
                "marginTop": "12px",
                "height": "6px"
            },
            children=[
                html.Div(
                    id=id_barra,
                    style={
                        "backgroundColor": "#f59e0b",
                        "height": "6px",
                        "borderRadius": "4px",
                        "width": "0%",
                        "transition": "width 0.5s"
                    }
                )
            ]
        ),
        html.Small(id=id_percentual, className="kpi-subtext text-muted")
    ]

    return html.Div(children, className="card-kpi")


def card_com_meta(titulo: str, valor: str, meta: str, percentual: float, cor: str,
                  id_valor: str = None, id_meta: str = None, id_percentual: str = None,
                  id_barra: str = None, id_sub_texto: str = None, icon_name: str = "lucide:trending-up"):
    """
    Card completo com meta, valor atual, percentual e barra de progresso.
    Redesenhado com layout limpo e espaçamento generoso.
    """

    # ── Cabeçalho: ícone + título ─────────────────────────────────
    cabecalho = html.Div(
        [
            html.Div(DashIconify(icon=icon_name, width=24, color=cor), style={"flexShrink": "0"}),
            html.H6(
                titulo,
                style={
                    "fontSize": "11px", "fontWeight": "700", "margin": "0",
                    "letterSpacing": "0.5px", "color": "var(--text-muted)", "textTransform": "uppercase"
                }
            ),
        ],
        style={"display": "flex", "alignItems": "center", "gap": "8px", "marginBottom": "16px"}
    )

    # ── Valor principal ───────────────────────────────────────────
    valor_bloco = html.Div(
        html.H2(
            id=id_valor, children=valor,
            style={
                "fontSize": "28px", "fontWeight": "800", "margin": "0",
                "color": "var(--text-main)", "letterSpacing": "-0.5px"
            }
        ),
        style={"marginBottom": "16px"}
    )

    # ── Barra de progresso ────────────────────────────────────────
    barra_container = html.Div(
        style={
            "width": "100%", "backgroundColor": "#e5e7eb",
            "borderRadius": "6px", "height": "10px", "marginBottom": "10px"
        },
        children=[
            html.Div(
                id=id_barra,
                style={
                    "backgroundColor": cor,
                    "height": "10px", "borderRadius": "6px",
                    "width": f"{min(percentual, 100)}%",
                    "transition": "width 0.6s ease",
                    "boxShadow": f"0 2px 6px {cor}55"
                }
            )
        ]
    )

    # ── Linha info: Meta (esq.) + Percentual (dir.) ───────────────
    linha_info = html.Div(
        [
            html.Div(
                [
                    html.Span("Meta: ", style={"fontSize": "11px", "color": "var(--text-muted)", "fontWeight": "600"}),
                    html.Span(id=id_meta, children=f"R$ {meta}", style={"fontSize": "12px", "fontWeight": "700", "color": "var(--text-main)"}),
                ],
                style={"flex": "1"}
            ),
            html.Span(
                id=id_percentual,
                children=f"{percentual:.1f}%",
                style={
                    "fontSize": "16px", "fontWeight": "800", "color": cor,
                    "background": f"{cor}15", "padding": "2px 10px",
                    "borderRadius": "20px", "letterSpacing": "-0.3px"
                }
            ),
        ],
        style={"display": "flex", "alignItems": "center", "justifyContent": "space-between", "marginBottom": "12px"}
    )

    # ── Separador + mês anterior ──────────────────────────────────
    rodape = html.Div(
        id=id_sub_texto,
        style={
            "fontSize": "12px", "color": "var(--text-muted)",
            "borderTop": "1px solid #f0f0f0", "paddingTop": "10px",
            "fontWeight": "500"
        }
    ) if id_sub_texto else html.Div(style={"height": "22px"})

    children = [cabecalho, valor_bloco, barra_container, linha_info, rodape]

    return html.Div(children, className="card-kpi", style={"padding": "22px", "minHeight": "200px"})
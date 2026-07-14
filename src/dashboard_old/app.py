"""
APLICAÇÃO PRINCIPAL DO DASHBOARD
=================================
Este é o ponto de entrada (entry point) do dashboard.
Inicializa o servidor Dash, configura o layout raiz e registra os callbacks.

ARQUITETURA:
    - app.py → layout raiz + Stores GLOBAIS + registro de callbacks
    - layouts/ → telas/páginas (login, dashboard, pagamentos, operadores)
    - callbacks/ → lógica interativa (autenticação, gráficos, filtros)
    - components/ → componentes reutilizáveis (cards, tabelas, menus)

⚠️ REGRA CRÍTICA:
    Os Stores globais (login-success-store, login-step-store) são definidos
    APENAS aqui no layout raiz. NUNCA criar Stores com esses IDs em layouts
    de página, pois isso sobrescreve os dados de autenticação e quebra a
    navegação entre páginas.

COMO EXECUTAR:
    python -m src.dashboard.app

🔧 CORREÇÕES APLICADAS:
    1. use_reloader=False para evitar processos em background
    2. Detecção de ambiente (local vs Google Colab)
    3. Tratamento de erro de porta ocupada
    4. Try/except no ponto de entrada
"""

import sys
import os

# ========================================================================
# AJUSTA O CAMINHO DO PYTHON PARA ENCONTRAR O MÓDULO 'src'
# ========================================================================
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# ========================================================================
# IMPORTAÇÕES
# ========================================================================
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output

# ========================================================================
# INICIALIZA O APP DASH PRINCIPAL
# ========================================================================
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,  # Necessário para layouts dinâmicos
    external_stylesheets=[
        dbc.themes.FLATLY,
        dbc.icons.FONT_AWESOME
    ]
)

server = app.server

# ========================================================================
# LAYOUT RAIZ (ROOT LAYOUT)
# ========================================================================
# IMPORTANTE: Os Stores com storage_type='local' persistem entre navegações
app.layout = html.Div([
    # Controle de URL (roteamento)
    dcc.Location(id='url', refresh=False),
    
    # Container onde as páginas (login/dashboard) serão renderizadas
    html.Div(id='page-content', style={"minHeight": "100vh"}),
    
    # ==================================================
    # STORES GLOBAIS - PERSISTEM ENTRE PÁGINAS
    # ==================================================
    # storage_type='local' mantém os dados no navegador
    dcc.Store(id='login-success-store', storage_type='local'),
    dcc.Store(id='login-step-store', data={'step': 'login'}, storage_type='memory'),
    
    # ==================================================
    # ATUALIZAÇÃO AUTOMÁTICA - A CADA 5 MINUTOS
    # ==================================================
    # interval=300000 = 5 minutos (em milissegundos)
    dcc.Interval(id='interval-component', interval=300000, n_intervals=0),
])

# ========================================================================
# IMPORTA OS CALLBACKS
# ========================================================================
from src.dashboard.callbacks import auth_callbacks, graficos_callbacks, pgto_callbacks, operador_callbacks, adm_callbacks

# ========================================================================
# REGISTRA OS CALLBACKS
# ========================================================================
auth_callbacks.register_callbacks(app)
graficos_callbacks.register_callbacks(app)
pgto_callbacks.register_callbacks(app)
operador_callbacks.register_callbacks(app)
adm_callbacks.register_callbacks(app)

# ========================================================================
# NOTA: O callback de atualização automática foi removido.
# Ele usava allow_duplicate=True no Output('page-content', 'children')
# e retornava dash.no_update, conflitando com o roteador de páginas.
# O dcc.Interval permanece no layout para uso futuro se necessário.
# ========================================================================

# ========================================================================
# PONTO DE ENTRADA
# ========================================================================
if __name__ == '__main__':
    print("=" * 50)
    print(" INICIANDO DASHBOARD SEMEAR")
    print("=" * 50)
    print(f" Diretorio raiz: {ROOT_DIR}")
    print("=" * 50)
    
    # ================================================================
    # CONFIGURAÇÃO DE PORTA - DETECTA AMBIENTE
    # ================================================================
    # Verifica se está rodando no Google Colab
    try:
        import google.colab
        IS_COLAB = True
        print("📱 Ambiente: Google Colab detectado")
    except:
        IS_COLAB = False
        print("💻 Ambiente: Local")
    
    # ================================================================
    # DEFINE PORTA E HOST
    # ================================================================
    if IS_COLAB:
        # No Colab, usa a porta padrão 8050 (que o Colab expõe)
        PORT = 8050
        HOST = '0.0.0.0'
        print(f"🔗 Acesse via: http://localhost:{PORT}")
        print("📌 Dica: Use o ngrok ou tunnel do Colab para acesso externo")
    else:
        # Ambiente local
        PORT = 80  # Pode mudar para 8050 se preferir
        HOST = '0.0.0.0'
        print(f"🔗 Acesse: http://127.0.0.1:{PORT}")
    
    # ================================================================
    # TRY/EXCEPT PARA CAPTURAR ERRO DE PORTA OCUPADA
    # ================================================================
    try:
        print(f"🚀 Iniciando servidor em {HOST}:{PORT}")
        print("=" * 50)
        
        # ✅ CORREÇÃO CRÍTICA: use_reloader=False
        # Isso evita que o servidor crie processos em background
        # e faz o CTRL+C funcionar corretamente
        app.run(
            debug=False,
            host=HOST,
            port=PORT,
            use_reloader=False,  # <-- ESSENCIAL!
            dev_tools_ui=False,   # Desativa UI de debug (opcional)
            dev_tools_props_check=False  # Desativa verificação de props (opcional)
        )
        
    except OSError as e:
        if "Address already in use" in str(e) or "port" in str(e).lower():
            print(f"\n❌ ERRO: A porta {PORT} já está em uso!")
            print(f"\n🔧 SOLUÇÕES:")
            print(f"   1. Execute: python -c \"import os; os.system('pkill -f python')\" (Linux/Mac)")
            print(f"   2. Ou no Windows: taskkill /F /IM python.exe")
            print(f"   3. Ou mude a porta no código (PORT = 8050)")
            print(f"\n🔄 Tentando porta alternativa 8050...")
            
            # Tenta porta alternativa
            try:
                app.run(
                    debug=False,
                    host=HOST,
                    port=8050,
                    use_reloader=False,
                    dev_tools_ui=False,
                    dev_tools_props_check=False
                )
            except Exception as e2:
                print(f"❌ Falha ao iniciar na porta 8050: {e2}")
                sys.exit(1)
        else:
            print(f"❌ Erro ao iniciar servidor: {e}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
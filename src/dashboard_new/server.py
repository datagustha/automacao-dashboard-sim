"""
SERVIDOR FLASK - DASHBOARD V2
==============================

Apenas criação do app, configurações e registro dos blueprints.
Toda lógica está nos arquivos de routes e services.
"""

from flask import Flask, send_from_directory
from pathlib import Path
import sys
import os

# ================================================================
# CONFIGURAÇÃO DO SISTEMA - CORRIGIDA
# ================================================================

# Adiciona o caminho src ao sys.path
src_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(src_path))

# Adiciona o caminho dashboard_v2 ao sys.path (para importar routes e services)
dashboard_path = Path(__file__).resolve().parent
sys.path.insert(0, str(dashboard_path))

# Adiciona também o caminho raiz (pgto) por segurança
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_path))

print(f"[INFO] Caminho src: {src_path}")
print(f"[INFO] Caminho dashboard: {dashboard_path}")
print(f"[INFO] Caminho raiz: {root_path}")

# ================================================================
# CRIAÇÃO DO APP
# ================================================================

app = Flask(__name__,
    static_folder='static',
    template_folder='templates'
)

# Chave secreta para sessões
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = 28800  # 8 horas

print("[OK] Flask configurado")

# ================================================================
# REGISTRO DOS BLUEPRINTS
# ================================================================

from routes.pages_routes import pages_bp
from routes.auth_routes import auth_bp
from routes.operador_routes import operador_bp
from routes.admin_routes import admin_bp

app.register_blueprint(pages_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(operador_bp)
app.register_blueprint(admin_bp)

print("[OK] Blueprints registrados")

# ================================================================
# ROTA PARA ARQUIVOS ESTÁTICOS
# ================================================================

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve arquivos estáticos (CSS, JS, imagens)."""
    return send_from_directory('static', filename)

# ================================================================
# ROTA DE TESTE
# ================================================================

@app.route('/api/teste')
def api_teste():
    """Endpoint de teste."""
    from datetime import datetime
    return {
        'success': True,
        'message': 'API do Dashboard V2 está funcionando!',
        'status': 'online',
        'timestamp': datetime.now().isoformat()
    }

# ================================================================
# INICIALIZAÇÃO
# ================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  DASHBOARD V2 - SERVIDOR INICIADO")
    print("="*60)
    print(f"  Login: http://localhost:5001/login")
    print(f"  Teste: http://localhost:5001/api/teste")
    print("  Pressione CTRL+C para parar")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=80)
"""
ROUTES - Blueprints do Dashboard V2
====================================

Organização das rotas por responsabilidade:
- pages_routes: Páginas HTML
- auth_routes: Autenticação e sessão
- operador_routes: APIs do operador
- admin_routes: APIs do ADM
"""

from .pages_routes import pages_bp
from .auth_routes import auth_bp
from .operador_routes import operador_bp
from .admin_routes import admin_bp

__all__ = ['pages_bp', 'auth_bp', 'operador_bp', 'admin_bp']
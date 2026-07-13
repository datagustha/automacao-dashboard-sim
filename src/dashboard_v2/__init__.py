"""
DASHBOARD V2
============

Versão estável do dashboard substituindo o Dash.

Tecnologias:
- Flask (backend)
- HTML + CSS + JS puro (frontend)
- Conexão com MySQL via services existentes

Estrutura:
- server.py: API endpoints
- static/: CSS, JS, imagens
- templates/: HTML
"""

from .server import app

__all__ = ['app']
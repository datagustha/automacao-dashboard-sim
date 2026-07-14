"""
PAGES ROUTES - Páginas HTML
============================

Rotas que servem as páginas do sistema.
Todas protegidas por verificação de sessão.
"""

from flask import Blueprint, render_template, redirect, session
from datetime import datetime

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    """Redireciona para login ou dashboard."""
    if session.get('operador'):
        operador = session.get('operador')
        if operador.get('banco') == 'ADM':
            return redirect('/dashboard-adm')
        return redirect('/dashboard')
    return redirect('/login')


@pages_bp.route('/login')
def login_page():
    """Página de login."""
    return render_template('login.html')


@pages_bp.route('/dashboard')
def dashboard_page():
    """Dashboard do operador."""
    if not session.get('operador'):
        return redirect('/login')
    now = datetime.now()
    return render_template('dashboard.html', mes_atual=now.month, ano_atual=now.year)


@pages_bp.route('/dashboard-adm')
def dashboard_adm_page():
    """Dashboard do ADM."""
    if not session.get('operador'):
        return redirect('/login')
    operador = session.get('operador')
    if operador.get('banco') != 'ADM':
        return redirect('/dashboard')
    now = datetime.now()
    return render_template('dashboard_adm.html', mes_atual=now.month, ano_atual=now.year)
# -*- coding: utf-8 -*-
"""
OPERADOR ROUTES - APIs do Operador
===================================
Gerencia os endpoints das APIs de operador, retornando dados de faturamento, metas,
pagamentos, performance, TMA e listagem de operadores, todos protegidos por controle de sessão.
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime

# Importações de persistência e serviços
from src.services.db_service import Buscar_login
from src.services.db_service import (
    Buscar_pagamento_semear,
    Buscar_pagamento_agoracred,
    buscar_metas_semear,
    buscar_metas_agoracred,
    buscar_todos_operadores_por_banco,
    buscar_tma_operador
)
from src.dashboard_new.services.operador_service import montar_dashboard_operador, montar_performance_operador

operador_bp = Blueprint('operador', __name__, url_prefix='/api')


@operador_bp.route('/operador/<login>')
def api_operador(login):
    """Retorna dados do operador pelo login."""
    print(f"[API] GET /api/operador/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        operador = Buscar_login(login)
        if operador:
            return jsonify({'success': True, 'data': operador})
        else:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/resumo/<login>')
def api_resumo(login):
    """Retorna o resumo completo do dashboard para o operador."""
    print(f"[API] GET /api/resumo/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        # Filtros de data
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        
        resultado = montar_dashboard_operador(operador, ano, mes)
        
        if resultado:
            return jsonify({'success': True, 'data': resultado})
        else:
            return jsonify({'success': False, 'message': 'Erro ao montar dashboard'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/pagamentos/<login>')
def api_pagamentos(login):
    """Retorna os pagamentos do operador."""
    print(f"[API] GET /api/pagamentos/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        banco = operador.get('banco', 'SEMEAR')
        
        # Busca pagamentos de acordo com o banco atribuído
        if banco == 'SEMEAR':
            pagamentos = Buscar_pagamento_semear(operador)
        elif banco == 'AGORACRED':
            pagamentos = Buscar_pagamento_agoracred(operador)
        else:
            pagamentos = Buscar_pagamento_semear(operador)
            if not pagamentos:
                pagamentos = Buscar_pagamento_agoracred(operador)
        
        # Converte em dicionário caso retorne objetos
        if pagamentos and not isinstance(pagamentos[0], dict):
            pagamentos = [p.__dict__ for p in pagamentos]
        
        return jsonify({
            'success': True,
            'data': pagamentos or [],
            'total': len(pagamentos or [])
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/metas/<login>')
def api_metas(login):
    """Retorna as metas do operador."""
    print(f"[API] GET /api/metas/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        banco = operador.get('banco', 'SEMEAR')
        
        # Busca metas de acordo com o banco atribuído
        if banco == 'SEMEAR':
            metas = buscar_metas_semear(operador)
        elif banco == 'AGORACRED':
            metas = buscar_metas_agoracred(operador)
        else:
            metas = buscar_metas_semear(operador)
            if not metas:
                metas = buscar_metas_agoracred(operador)
        
        return jsonify({
            'success': True,
            'data': metas or []
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/performance/<login>')
def api_performance(login):
    """Retorna a performance do operador."""
    print(f"[API] GET /api/performance/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        resultado = montar_performance_operador(operador, ano, mes)
        
        if resultado:
            return jsonify({'success': True, 'data': resultado})
        else:
            return jsonify({'success': False, 'message': 'Erro ao montar performance'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/tma/<login>')
def api_tma(login):
    """Retorna os dados de TMA do operador."""
    print(f"[API] GET /api/tma/{login}")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Operador só pode ver seus próprios dados, exceto se for ADM
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin and session.get('login', '').lower() != login.lower():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        ano = request.args.get('ano', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        
        operador = Buscar_login(login)
        if not operador:
            return jsonify({
                'success': False,
                'message': f'Operador {login} não encontrado'
            }), 404
        
        banco = operador.get('banco', 'SEMEAR')
        tma = buscar_tma_operador(login, banco, ano, mes)
        
        return jsonify({
            'success': True,
            'data': tma or {}
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@operador_bp.route('/operadores')
def api_operadores():
    """Retorna lista de todos os operadores."""
    print(f"[API] GET /api/operadores")
    
    # Verifica se o usuário está autenticado
    operador_sessao = session.get('operador')
    if not operador_sessao:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
        
    # Apenas administradores podem listar todos os operadores do sistema
    is_admin = operador_sessao.get('perfil') == 'adm' or operador_sessao.get('banco') == 'ADM'
    if not is_admin:
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
    try:
        banco = request.args.get('banco', 'SEMEAR')
        operadores = buscar_todos_operadores_por_banco(banco)
        
        return jsonify({
            'success': True,
            'data': operadores,
            'total': len(operadores)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
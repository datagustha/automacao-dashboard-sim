"""
AUTH ROUTES - Autenticação
===========================

Rotas de autenticação, sessão e envio de código.
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime
import random

from src.services.db_service import Buscar_login
from src.services.email_service import enviar_token_2fa_email, enviar_token_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# Armazenamento de códigos (em produção, usar Redis ou banco)
codigos_verificacao = {}


def gerar_codigo():
    """Gera um código de 6 dígitos."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


@auth_bp.route('/enviar-codigo', methods=['POST'])
def api_enviar_codigo():
    """Envia código de verificação por email."""
    try:
        data = request.json
        login = data.get('login', '').strip()
        
        if not login:
            return jsonify({'success': False, 'message': 'Login é obrigatório'}), 400
        
        operador = Buscar_login(login)
        if not operador:
            return jsonify({'success': False, 'message': f'Operador {login} não encontrado'}), 404
        
        email = operador.get('email')
        if not email:
            return jsonify({'success': False, 'message': 'Operador não possui email cadastrado'}), 400
        
        codigo = gerar_codigo()
        codigos_verificacao[email] = {
            'codigo': codigo,
            'timestamp': datetime.now(),
            'login': login,
            'operador': operador
        }
        
        enviado = enviar_token_2fa_email(email, login, codigo)
        if not enviado:
            enviado = enviar_token_email(email, login, codigo, "primeiro_acesso")
        
        if enviado:
            email_mascarado = email[:3] + '***' + email[email.find('@'):]
            return jsonify({
                'success': True,
                'message': 'Código enviado com sucesso',
                'email': email_mascarado
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao enviar email. Verifique a configuração do serviço de email.'
            }), 500
            
    except Exception as e:
        print(f"[ERRO] api_enviar_codigo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/verificar-codigo', methods=['POST'])
def api_verificar_codigo():
    """Verifica o código enviado por email."""
    try:
        data = request.json
        login = data.get('login', '').strip()
        codigo = data.get('codigo', '').strip()
        
        if not login or not codigo:
            return jsonify({'success': False, 'message': 'Login e código são obrigatórios'}), 400
        
        operador = Buscar_login(login)
        if not operador:
            return jsonify({'success': False, 'message': f'Operador {login} não encontrado'}), 404
        
        email = operador.get('email')
        if not email:
            return jsonify({'success': False, 'message': 'Operador não possui email cadastrado'}), 400
        
        registro = codigos_verificacao.get(email)
        if not registro:
            return jsonify({'success': False, 'message': 'Nenhum código solicitado. Solicite um novo código.'}), 400
        
        tempo_passado = datetime.now() - registro['timestamp']
        if tempo_passado.total_seconds() > 300:
            del codigos_verificacao[email]
            return jsonify({'success': False, 'message': 'Código expirado. Solicite um novo código.'}), 400
        
        if registro['codigo'] != codigo:
            return jsonify({'success': False, 'message': 'Código incorreto. Tente novamente.'}), 400
        
        session['operador'] = operador
        session['login'] = login
        session['banco'] = operador.get('banco', 'SEMEAR')
        session.permanent = True
        
        del codigos_verificacao[email]
        
        if operador.get('banco') == 'ADM':
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'redirect': '/dashboard-adm'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso!',
                'redirect': '/dashboard'
            })
            
    except Exception as e:
        print(f"[ERRO] api_verificar_codigo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/session', methods=['GET'])
def get_session():
    """Retorna os dados da sessão atual."""
    if session.get('operador'):
        return jsonify({'success': True, 'data': session.get('operador')})
    return jsonify({'success': False, 'message': 'Nenhuma sessão ativa'}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Faz logout do usuário."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})
"""
AUTH ROUTES - Autenticação
===========================

Rotas de autenticação, sessão e envio de código.

FLUXO (2 ETAPAS):
1) POST /api/login             -> valida login + senha (hash). Se ok, gera e envia código 2FA por email.
2) POST /api/verificar-codigo  -> valida o código de 6 dígitos e cria a sessão.
   POST /api/reenviar-codigo   -> reenvia o código sem pedir a senha de novo (usuário já autenticou na etapa 1).
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime
from werkzeug.security import check_password_hash
import random

from src.services.db_service import Buscar_login
from src.services.email_service import enviar_token_2fa_email, enviar_token_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# Armazenamento de códigos (em produção, usar Redis ou banco)
codigos_verificacao = {}


def gerar_codigo():
    """Gera um código de 6 dígitos."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def _mascarar_email(email: str) -> str:
    return email[:3] + '***' + email[email.find('@'):]


def _gerar_e_enviar_codigo(login: str, operador: dict):
    """
    Gera um novo código de verificação, guarda em memória e envia por email.
    Reaproveitado tanto no login (etapa 1) quanto no reenvio.
    Retorna (sucesso: bool, email_mascarado: str | None, mensagem_erro: str | None)
    """
    email = operador.get('email')
    if not email:
        return False, None, 'Operador não possui email cadastrado'

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
        return True, _mascarar_email(email), None
    return False, None, 'Erro ao enviar email. Verifique a configuração do serviço de email.'


@auth_bp.route('/login', methods=['POST'])
def api_login():
    """
    ETAPA 1: valida login + senha.
    Se a senha estiver correta, gera e envia o código de verificação por email.
    """
    try:
        data = request.json or {}
        login = (data.get('login') or '').strip()
        senha = data.get('senha') or ''

        if not login or not senha:
            return jsonify({'success': False, 'message': 'Login e senha são obrigatórios'}), 400

        operador = Buscar_login(login)
        if not operador:
            # Mensagem genérica de propósito (não revelar se o login existe ou não)
            return jsonify({'success': False, 'message': 'Login ou senha inválidos'}), 401

        senha_hash = operador.get('senha_hash')
        if not senha_hash:
            return jsonify({
                'success': False,
                'message': 'Este usuário ainda não possui senha cadastrada. Procure o administrador.'
            }), 400

        if not check_password_hash(senha_hash, senha):
            return jsonify({'success': False, 'message': 'Login ou senha inválidos'}), 401

        sucesso, email_mascarado, erro = _gerar_e_enviar_codigo(login, operador)
        if sucesso:
            return jsonify({
                'success': True,
                'message': 'Senha válida. Código enviado com sucesso',
                'email': email_mascarado
            })
        else:
            return jsonify({'success': False, 'message': erro}), 500

    except Exception as e:
        print(f"[ERRO] api_login: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/reenviar-codigo', methods=['POST'])
def api_reenviar_codigo():
    """
    Reenvia o código de verificação sem pedir a senha novamente
    (o usuário já validou a senha na etapa 1 / /api/login).
    """
    try:
        data = request.json or {}
        login = (data.get('login') or '').strip()

        if not login:
            return jsonify({'success': False, 'message': 'Login é obrigatório'}), 400

        operador = Buscar_login(login)
        if not operador:
            return jsonify({'success': False, 'message': f'Operador {login} não encontrado'}), 404

        sucesso, email_mascarado, erro = _gerar_e_enviar_codigo(login, operador)
        if sucesso:
            return jsonify({
                'success': True,
                'message': 'Código reenviado com sucesso',
                'email': email_mascarado
            })
        else:
            return jsonify({'success': False, 'message': erro}), 500

    except Exception as e:
        print(f"[ERRO] api_reenviar_codigo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/verificar-codigo', methods=['POST'])
def api_verificar_codigo():
    """ETAPA 2: Verifica o código enviado por email e cria a sessão."""
    try:
        data = request.json or {}
        login = (data.get('login') or '').strip()
        codigo = (data.get('codigo') or '').strip()

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
        session['login'] = operador.get('login', login)
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
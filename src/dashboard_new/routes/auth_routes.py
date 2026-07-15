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
# datetime: Para manipular horas e timestamps de expiração de token
from datetime import datetime
# check_password_hash: Verifica a senha digitada contra o hash salvo no banco
from werkzeug.security import check_password_hash
# random: Para gerar números aleatórios caso necessário
import random

# Buscar_login: Função que busca dados do operador na d_analista
from src.services.db_service import Buscar_login
# enviar_token_2fa_email, enviar_token_email: Serviços de envio de e-mail por SMTP
from src.services.email_service import enviar_token_2fa_email, enviar_token_email
# Funções de autenticação e manipulação de senhas/tokens no banco de dados
from src.services.auth_service import salvar_token, validar_token, salvar_senha, gerar_token_numerico

# Cria o blueprint de autenticação com prefixo /api
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

        # Verifica se o operador já tem uma senha cadastrada no sistema
        senha_hash = operador.get('senha_hash')
        # Se não tiver senha cadastrada
        if not senha_hash:
            # Retorna erro sugerindo que ele cadastre a senha clicando em Esqueci minha senha
            return jsonify({
                'success': False,
                'message': 'Este usuário ainda não possui senha cadastrada. Clique em "Esqueci minha senha" para criar uma.'
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


@auth_bp.route('/solicitar-recuperacao', methods=['POST'])
def api_solicitar_recuperacao():
    # Rota para solicitar redefinição/criação de senha
    try:
        # Pega os dados enviados no corpo da requisição em formato JSON
        data = request.json or {}
        # Obtém o login e remove espaços em branco nas pontas
        login = (data.get('login') or '').strip()

        # Verifica se o login foi fornecido
        if not login:
            # Se não foi fornecido, retorna erro 400 (Bad Request)
            return jsonify({'success': False, 'message': 'O login é obrigatório'}), 400

        # Busca o operador no banco de dados pelo login
        operador = Buscar_login(login)
        # Se o operador não for encontrado no banco
        if not operador:
            # Retorna erro 404 informando que o usuário não foi localizado
            return jsonify({'success': False, 'message': 'Operador não encontrado no sistema'}), 404

        # Obtém o e-mail do operador cadastrado no banco de dados
        email = operador.get('email')
        # Verifica se o operador possui um e-mail cadastrado
        if not email:
            # Se não possuir, retorna erro informando que deve contatar o adm
            return jsonify({
                'success': False,
                'message': 'Este operador não possui e-mail cadastrado. Contate o administrador.'
            }), 400

        # Gera um código de verificação numérico de 6 dígitos
        codigo = gerar_token_numerico(6)
        
        # Define se é primeiro acesso (quando ainda não tem senha cadastrada) ou recuperação
        tem_senha = operador.get('senha_hash') is not None
        # Tipo do token a ser salvo ('primeiro_acesso' ou 'reset_senha')
        tipo_token = "reset_senha" if tem_senha else "primeiro_acesso"

        # Salva o token gerado no banco de dados
        salvo = salvar_token(login, codigo, tipo_token)
        # Se falhou ao salvar o token no banco de dados
        if not salvo:
            # Retorna erro interno do servidor 500
            return jsonify({'success': False, 'message': 'Erro ao registrar o código no sistema'}), 500

        # Envia o e-mail com o token gerado
        enviado = enviar_token_email(email, login, codigo, tipo_token)
        # Se o e-mail foi enviado com sucesso
        if enviado:
            # Mascara o e-mail do usuário para exibir na tela de forma segura (ex: ros***@gmail.com)
            email_mascarado = _mascarar_email(email)
            # Retorna sucesso com a mensagem e o e-mail mascarado
            return jsonify({
                'success': True,
                'message': 'Código enviado com sucesso para o seu e-mail cadastrado.',
                'email': email_mascarado
            })
        else:
            # Se falhou ao enviar o e-mail, retorna erro 500
            return jsonify({
                'success': False,
                'message': 'Erro ao enviar o e-mail com o código de verificação.'
            }), 500

    except Exception as e:
        # Exibe o erro ocorrido no console do servidor
        print(f"[ERRO] api_solicitar_recuperacao: {str(e)}")
        # Retorna o erro 500 com a mensagem de exceção
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/redefinir-senha', methods=['POST'])
def api_redefinir_senha():
    # Rota para validar o token e salvar a nova senha cadastrada pelo usuário
    try:
        # Pega os dados enviados no formato JSON
        data = request.json or {}
        # Obtém o login do operador e limpa espaços
        login = (data.get('login') or '').strip()
        # Obtém o código digitado e limpa espaços
        codigo = (data.get('codigo') or '').strip()
        # Obtém a nova senha inserida
        nova_senha = data.get('nova_senha') or ''

        # Verifica se os três campos obrigatórios foram passados
        if not login or not codigo or not nova_senha:
            # Retorna erro de requisição caso algum campo esteja em falta
            return jsonify({'success': False, 'message': 'Login, código e nova senha são obrigatórios'}), 400

        # Busca o operador no banco de dados para ver se ele existe
        operador = Buscar_login(login)
        # Se o operador não for encontrado no banco
        if not operador:
            # Retorna erro informando que o operador não existe
            return jsonify({'success': False, 'message': 'Operador não encontrado'}), 404

        # Determina o tipo de token esperado com base na existência prévia de senha
        tem_senha = operador.get('senha_hash') is not None
        # Tipo do token cadastrado no banco ('reset_senha' ou 'primeiro_acesso')
        tipo_token = "reset_senha" if tem_senha else "primeiro_acesso"

        # Valida o token contra o banco de dados
        valido = validar_token(login, codigo, tipo_token)
        # Se o token não for válido (expirado, incorreto, usado)
        if not valido:
            # Retorna erro informando que o código é inválido ou expirou
            return jsonify({'success': False, 'message': 'Código de verificação incorreto ou expirado'}), 400

        # Salva a nova senha do operador com hash no banco de dados
        salvou = salvar_senha(login, nova_senha)
        # Se salvou a nova senha com sucesso no banco de dados
        if salvou:
            # Retorna sucesso informando que a senha foi atualizada com êxito
            return jsonify({'success': True, 'message': 'Nova senha cadastrada com sucesso! Faça login normalmente.'})
        else:
            # Se deu algum erro ao atualizar a senha no banco, retorna erro 500
            return jsonify({'success': False, 'message': 'Erro interno ao salvar a nova senha no banco de dados'}), 500

    except Exception as e:
        # Exibe o erro no terminal do servidor
        print(f"[ERRO] api_redefinir_senha: {str(e)}")
        # Retorna o erro 500 com a mensagem correspondente
        return jsonify({'success': False, 'message': str(e)}), 500
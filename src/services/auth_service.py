"""
SERVIÇO DE AUTENTICAÇÃO
========================
Este arquivo gerencia tudo relacionado a:
- Hash de senhas (transformar senha em código seguro)
- Tokens numéricos (códigos de 6 dígitos)
- Validação de tokens
- Busca de e-mails no banco
"""

# ================================================================
# IMPORTAÇÕES E PARA QUE SERVEM
# ================================================================

# werkzeug.security: Biblioteca que vem com Flask/Dash para segurança
# - generate_password_hash: Transforma uma senha em um hash (código seguro)
# - check_password_hash: Verifica se a senha digitada bate com o hash
from werkzeug.security import generate_password_hash, check_password_hash

# sqlalchemy.orm.Session: Gerencia a conexão com o banco de dados
from sqlalchemy.orm import Session

# datetime: Trabalha com datas e horas (ex: token expira em 15 minutos)
from datetime import datetime, timedelta

# random e string: Geram números aleatórios para os tokens
import random
import string

# engine: Nossa conexão com o banco (configurada em config/database.py)
from src.config.database import engine

# analistas: Modelo da tabela d_analista (onde ficam login, email, senha)
from src.models.LoginModel import analistas

# TokenRecuperacao: Modelo da tabela de tokens (criamos hoje)
from src.models.TokenModel import TokenRecuperacao


# ================================================================
# FUNÇÃO 1: Gerar token numérico
# ================================================================

def gerar_token_numerico(tamanho: int = 6) -> str:
    """
    Gera um token numérico aleatório de 6 dígitos.
    
    Exemplo: "483729" ou "125690"
    
    Como funciona:
    1. string.digits = "0123456789"
    2. random.choices escolhe 6 números aleatórios dessa string
    3. ''.join junta tudo em uma string
    
    Args:
        tamanho: Número de dígitos (padrão: 6)
    
    Returns:
        str: Token numérico (ex: "483729")
    """
    # string.digits = "0123456789"
    # random.choices pega 6 números aleatórios
    # ''.join transforma a lista em string: [4,8,3,7,2,9] → "483729"
    return ''.join(random.choices(string.digits, k=tamanho))


# ================================================================
# FUNÇÃO 2: Criar hash da senha
# ================================================================

def criar_hash_senha(senha: str) -> str:
    """
    Transforma uma senha em um HASH (código seguro).
    
    O QUE É HASH?
    - É uma forma de "embaralhar" a senha de forma que não dá para voltar atrás
    - Ex: senha "123456" vira algo como "pbkdf2:sha256:600000$..."
    - Mesmo que alguém veja o banco de dados, NÃO consegue saber a senha original
    
    O QUE É WERKZEUG?
    - Biblioteca de segurança do Flask/Dash
    - generate_password_hash usa algoritmo bcrypt (muito seguro)
    - Adiciona um "sal" (dados aleatórios) para tornar cada hash único
    
    Args:
        senha: Senha em texto puro (ex: "minhasenha123")
    
    Returns:
        str: Hash da senha (ex: "pbkdf2:sha256:600000$...")
    """
    # generate_password_hash faz:
    # 1. Adiciona um "sal" (dados aleatórios)
    # 2. Aplica algoritmo bcrypt (várias rodadas)
    # 3. Retorna uma string segura
    return generate_password_hash(senha)


# ================================================================
# FUNÇÃO 3: Verificar senha
# ================================================================

def verificar_senha(senha_hash: str, senha: str) -> bool:
    """
    Verifica se a senha digitada corresponde ao hash salvo no banco.
    
    Como funciona?
    1. Pega o hash que está no banco
    2. Pega a senha que o usuário digitou
    3. Aplica o mesmo algoritmo de hash na senha digitada
    4. Compara se é igual
    
    IMPORTANTE: Não dá para "descriptografar" o hash. Só podemos comparar.
    
    Args:
        senha_hash: Hash que está no banco de dados
        senha: Senha que o usuário digitou no login
    
    Returns:
        bool: True se a senha está correta, False se não
    """
    # check_password_hash faz:
    # 1. Extrai o "sal" do hash original
    # 2. Aplica o mesmo sal na senha digitada
    # 3. Compara se os hashes são iguais
    return check_password_hash(senha_hash, senha)


# ================================================================
# FUNÇÃO 4: Salvar token no banco
# ================================================================

def salvar_token(login: str, token: str, tipo: str = "primeiro_acesso") -> bool:
    """
    Salva o token no banco de dados com expiração de 15 minutos.
    
    O QUE É UM TOKEN?
    - Código temporário enviado por e-mail
    - Expira após 15 minutos (segurança)
    - Só pode ser usado uma vez
    
    Args:
        login: Login do operador (ex: "2552ROSELI")
        token: Token numérico (ex: "483729")
        tipo: 'primeiro_acesso' ou 'reset_senha'
    
    Returns:
        bool: True se salvou com sucesso
    """
    try:
        # Abre conexão com o banco
        with Session(engine) as session:
            
            # Cria um novo registro na tabela tokens_recuperacao
            novo_token = TokenRecuperacao(
                login=login,                                    # Login do operador
                token=token,                                    # Código de 6 dígitos
                tipo=tipo,                                      # Tipo do token
                expira_em=datetime.now() + timedelta(minutes=15),  # Expira em 15 minutos
                usado=False                                     # Ainda não foi usado
            )
            
            # Adiciona e salva no banco
            session.add(novo_token)
            session.commit()  # Salva de fato no banco
            return True
            
    except Exception as e:
        print(f"[ERRO] Erro ao salvar token: {str(e)}")
        return False


# ================================================================
# FUNÇÃO 5: Validar token
# ================================================================

def validar_token(login: str, token: str, tipo: str = "primeiro_acesso") -> bool:
    """
    Verifica se o token digitado pelo usuário é válido.
    
    Verificações:
    1. O token existe no banco?
    2. O token é para o login correto?
    3. O token ainda NÃO foi usado?
    4. O token NÃO expirou?
    
    Args:
        login: Login do operador
        token: Token digitado pelo usuário
        tipo: Tipo do token ('primeiro_acesso' ou 'reset_senha')
    
    Returns:
        bool: True se o token é válido
    """
    try:
        with Session(engine) as session:
            
            # Busca o token no banco com todas as condições
            registro = session.query(TokenRecuperacao).filter(
                TokenRecuperacao.login == login,        # Login correto
                TokenRecuperacao.token == token,        # Token correto
                TokenRecuperacao.tipo == tipo,          # Tipo correto
                TokenRecuperacao.usado == False,        # Nunca foi usado
                TokenRecuperacao.expira_em > datetime.now()  # Não expirou
            ).first()  # Pega o primeiro (deve ser único)
            
            if registro:
                # Marca como usado para não ser reutilizado
                registro.usado = True
                session.commit()
                return True
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao validar token: {str(e)}")
        return False


# ================================================================
# FUNÇÃO 6: Buscar e-mail do operador
# ================================================================

def obter_email_operador(login: str):
    """
    Busca o e-mail do operador no banco de dados.
    
    Args:
        login: Login do operador (ex: "2552ROSELI")
    
    Returns:
        str ou None: E-mail do operador ou None se não encontrado
    """
    try:
        with Session(engine) as session:
            # Busca o operador na tabela d_analista
            operador = session.query(analistas).filter(
                analistas.loguin == login
            ).first()
            
            # Se encontrou e tem e-mail, retorna
            if operador and operador.email:
                return operador.email
            return None
            
    except Exception as e:
        print(f"[ERRO] Erro ao buscar e-mail: {str(e)}")
        return None


# ================================================================
# FUNÇÃO 7: Verificar se operador tem senha
# ================================================================

def operador_tem_senha(login: str) -> bool:
    """
    Verifica se o operador já tem senha cadastrada.
    
    Args:
        login: Login do operador
    
    Returns:
        bool: True se já tem senha cadastrada
    """
    try:
        with Session(engine) as session:
            operador = session.query(analistas).filter(
                analistas.loguin == login
            ).first()
            
            # Se encontrou e tem senha_hash (não está vazio)
            if operador and operador.senha_hash:
                return True
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao verificar senha: {str(e)}")
        return False


# ================================================================
# FUNÇÃO 8: Salvar nova senha
# ================================================================

def salvar_senha(login: str, nova_senha: str) -> bool:
    """
    Salva a nova senha do operador no banco.
    
    Args:
        login: Login do operador
        nova_senha: Nova senha em texto puro
    
    Returns:
        bool: True se salvou com sucesso
    """
    try:
        with Session(engine) as session:
            operador = session.query(analistas).filter(
                analistas.loguin == login
            ).first()
            
            if operador:
                # Cria o hash da nova senha e salva
                operador.senha_hash = criar_hash_senha(nova_senha)
                operador.primeiro_acesso = False  # Não é mais primeiro acesso
                session.commit()
                return True
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao salvar senha: {str(e)}")
        return False


# ================================================================
# FUNÇÃO 9: Marcar primeiro acesso como concluído
# ================================================================

def marcar_primeiro_acesso_concluido(login: str) -> bool:
    """
    Marca que o operador já concluiu o primeiro acesso.
    
    Args:
        login: Login do operador
    
    Returns:
        bool: True se atualizou com sucesso
    """
    try:
        with Session(engine) as session:
            operador = session.query(analistas).filter(
                analistas.loguin == login
            ).first()
            
            if operador:
                operador.primeiro_acesso = False
                session.commit()
                return True
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao atualizar primeiro acesso: {str(e)}")
        return False

# ================================================================
# FUNÇÕES PARA 2FA (SEGUNDO FATOR DE AUTENTICAÇÃO)
# ================================================================

from src.models.token_2fa import Token2FA  # Modelo que você criou


def salvar_token_2fa(login: str, token: str) -> bool:
    """
    Salva token de 2FA no banco com expiração de 5 minutos.
    
    Args:
        login: Login do operador
        token: Token numérico de 6 dígitos
    
    Returns:
        bool: True se salvou com sucesso
    """
    try:
        with Session(engine) as session:
            # Remove tokens antigos não usados do mesmo login (opcional)
            session.query(Token2FA).filter(
                Token2FA.login == login,
                Token2FA.usado == False,
                Token2FA.expira_em < datetime.now()
            ).delete()
            
            # Cria novo token 2FA
            novo_token = Token2FA(
                login=login,
                codigo=token,  # Atenção: sua tabela usa 'codigo', não 'token'
                expira_em=datetime.now() + timedelta(minutes=5),  # 5 minutos
                usado=False,
                tentativas=0
            )
            
            session.add(novo_token)
            session.commit()
            return True
            
    except Exception as e:
        print(f"[ERRO] Erro ao salvar token 2FA: {str(e)}")
        return False


def validar_token_2fa(login: str, token_digitado: str) -> dict:
    """
    Verifica se o token 2FA digitado pelo usuário é válido.
    
    Args:
        login: Login do operador
        token_digitado: Token de 6 dígitos que o usuário digitou
    
    Returns:
        dict: {
            'valido': bool,
            'mensagem': str,
            'tentativas_restantes': int (opcional)
        }
    """
    try:
        with Session(engine) as session:
            # Busca token válido (não usado, não expirado)
            token = session.query(Token2FA).filter(
                Token2FA.login == login,
                Token2FA.usado == False,
                Token2FA.expira_em > datetime.now()
            ).first()
            
            # Token não encontrado ou expirado
            if not token:
                return {
                    'valido': False,
                    'mensagem': 'Código expirado ou inválido. Solicite um novo código.'
                }
            
            # Verifica tentativas (máximo 3)
            if token.tentativas >= 3:
                # Marca como expirado por muitas tentativas
                token.usado = True
                session.commit()
                return {
                    'valido': False,
                    'mensagem': 'Muitas tentativas. Solicite um novo código.'
                }
            
            # Verifica se o código está correto
            if token.codigo == token_digitado:
                # Sucesso! Marca como usado
                token.usado = True
                session.commit()
                return {
                    'valido': True,
                    'mensagem': 'Código validado com sucesso!'
                }
            else:
                # Código errado: incrementa tentativas
                token.tentativas += 1
                session.commit()
                
                tentativas_restantes = 3 - token.tentativas
                return {
                    'valido': False,
                    'mensagem': f'Código incorreto. Você tem mais {tentativas_restantes} tentativa(s).'
                }
            
    except Exception as e:
        print(f"[ERRO] Erro ao validar token 2FA: {str(e)}")
        return {
            'valido': False,
            'mensagem': 'Erro interno. Tente novamente.'
        }


def limpar_tokens_2fa_expirados() -> int:
    """
    Remove tokens 2FA expirados do banco.
    Rode isso num CRON diário para manter o banco limpo.
    
    Returns:
        int: Número de tokens removidos
    """
    try:
        with Session(engine) as session:
            removidos = session.query(Token2FA).filter(
                Token2FA.expira_em < datetime.now()
            ).delete()
            session.commit()
            return removidos
            
    except Exception as e:
        print(f"[ERRO] Erro ao limpar tokens 2FA: {str(e)}")
        return 0
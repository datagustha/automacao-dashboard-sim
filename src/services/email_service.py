"""
SERVIÇO DE ENVIO DE E-MAILS
============================
Responsável por enviar os tokens numéricos por e-mail usando o Gmail.
"""

# ================================================================
# IMPORTAÇÕES E PARA QUE SERVEM
# ================================================================

# smtplib: Biblioteca padrão do Python para enviar e-mails
# - SMTP (Simple Mail Transfer Protocol) é o protocolo de envio de e-mails
# - Ela faz a conexão com o servidor do Gmail e envia a mensagem
import smtplib

# email.mime: Biblioteca para construir e-mails com formatação
# - MIMEText: Para texto simples
# - MIMEMultipart: Para e-mails que combinam texto + HTML (mais completo)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# os: Acessa variáveis de ambiente do sistema
# - Usamos para ler o arquivo .env (não expor senhas no código)
import os

# dotenv: Carrega as variáveis do arquivo .env
# - Permite guardar senhas e configurações fora do código
from dotenv import load_dotenv

# ================================================================
# CARREGAR CONFIGURAÇÕES DO .env
# ================================================================

# Carrega as variáveis do arquivo .env (que fica na raiz do projeto)
# Exemplo do .env:
#   EMAIL_REMETENTE=seuemail@gmail.com
#   EMAIL_SENHA=abcd efgh ijkl mnop
load_dotenv()

# ================================================================
# CONFIGURAÇÕES DO GMAIL (servidor SMTP)
# ================================================================

# EMAIL_REMETENTE: Quem está enviando o e-mail
# - Busca a variável do .env
# - Se não encontrar, usa 'seuemail@gmail.com' como fallback
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE", "seuemail@gmail.com")

# EMAIL_SENHA: Senha de aplicativo do Gmail
# - NÃO é sua senha normal do Gmail
# - É uma senha especial gerada em: Conta Google > Senhas de Aplicativo
EMAIL_SENHA = os.getenv("EMAIL_SENHA", "sua senha de app")

# SMTP_SERVER: Endereço do servidor de e-mail do Gmail
# - smtp.gmail.com é o servidor padrão do Gmail
SMTP_SERVER = "smtp.gmail.com"

# SMTP_PORT: Porta de conexão
# - 587 é a porta padrão para TLS (transmissão segura)
# - TLS (Transport Layer Security) criptografa a comunicação
SMTP_PORT = 587


# ================================================================
# FUNÇÃO PRINCIPAL: Enviar e-mail com token
# ================================================================

def enviar_token_email(destinatario: str, login: str, token: str, tipo: str = "primeiro_acesso"):
    """
    Envia um e-mail com o token numérico para o operador.
    
    COMO FUNCIONA O ENVIO DE E-MAIL:
    1. Conecta ao servidor SMTP do Gmail
    2. Faz login com sua conta
    3. Cria uma mensagem com assunto e corpo
    4. Envia a mensagem
    5. Fecha a conexão
    
    Args:
        destinatario: E-mail do operador (ex: roseli@gmail.com)
        login: Login do operador (ex: 2552ROSELI)
        token: Código numérico de 6 dígitos (ex: 483729)
        tipo: 'primeiro_acesso' ou 'reset_senha'
    
    Returns:
        bool: True se o e-mail foi enviado com sucesso, False se houve erro
    """
    
    # ================================================================
    # PASSO 1: Definir assunto e mensagem baseado no tipo
    # ================================================================
    
    if tipo == "primeiro_acesso":
        # Primeiro acesso: operador está criando a senha pela primeira vez
        assunto = "🔐 Crie sua senha - Dashboard Semear"
        
        # Corpo do e-mail (texto puro, sem formatação HTML)
        mensagem = f"""
        Olá operador {login}!
        
        Você está criando seu acesso ao Dashboard Semear.
        
        Seu código de verificação é: {token}
        
        Este código expira em 15 minutos.
        
        Digite este código no dashboard para criar sua senha.
        
        Se você não solicitou este acesso, ignore este e-mail.
        
        ---
        Dashboard Semear - Sistema de Gestão de Pagamentos
        """
    else:
        # Reset de senha: operador esqueceu a senha e solicitou redefinição
        assunto = "🔐 Recuperação de senha - Dashboard Semear"
        
        mensagem = f"""
        Olá operador {login}!
        
        Você solicitou a recuperação de sua senha do Dashboard Semear.
        
        Seu código de verificação é: {token}
        
        Este código expira em 15 minutos.
        
        Digite este código no dashboard para redefinir sua senha.
        
        Se você não solicitou, ignore este e-mail.
        
        ---
        Dashboard Semear - Sistema de Gestão de Pagamentos
        """
    
    # ================================================================
    # PASSO 2: Tentar enviar o e-mail (com tratamento de erros)
    # ================================================================
    
    try:
        # ------------------------------------------------------------
        # 2.1: Criar a mensagem (estrutura do e-mail)
        # ------------------------------------------------------------
        # MIMEMultipart permite enviar e-mail com múltiplas partes
        msg = MIMEMultipart()
        
        # Quem está enviando (seu e-mail)
        msg['From'] = EMAIL_REMETENTE
        
        # Para quem está enviando (e-mail do operador)
        msg['To'] = destinatario
        
        # Assunto do e-mail
        msg['Subject'] = assunto
        
        # Adiciona o corpo da mensagem (texto puro, charset utf-8 para acentos)
        msg.attach(MIMEText(mensagem, 'plain', 'utf-8'))
        
        # ------------------------------------------------------------
        # 2.2: Conectar ao servidor SMTP do Gmail
        # ------------------------------------------------------------
        # Cria uma conexão com o servidor
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        
        # Inicia comunicação TLS (criptografia)
        # TLS garante que a senha não seja enviada em texto puro
        server.starttls()
        
        # Faz login no Gmail com seu e-mail e senha de app
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        
        # ------------------------------------------------------------
        # 2.3: Enviar o e-mail
        # ------------------------------------------------------------
        # send_message envia o e-mail completo
        server.send_message(msg)
        
        # ------------------------------------------------------------
        # 2.4: Fechar a conexão
        # ------------------------------------------------------------
        server.quit()
        
        # Se chegou até aqui, o e-mail foi enviado com sucesso
        print(f"[OK] E-mail enviado para {destinatario} (login: {login})")
        return True
        
    except Exception as e:
        # Se aconteceu qualquer erro (conexão, login, envio)
        print(f"[ERRO] Falha ao enviar e-mail para {destinatario}: {str(e)}")
        return False


# ================================================================
# FUNÇÃO EXTRA: Enviar e-mail de teste
# ================================================================

def enviar_email_teste(destinatario: str):
    """
    Função para testar se a configuração de e-mail está funcionando.
    
    Args:
        destinatario: E-mail de teste (pode ser o seu próprio)
    
    Returns:
        bool: True se o e-mail foi enviado com sucesso
    """
    assunto = "🧪 Teste de Configuração - Dashboard Semear"
    mensagem = f"""
    Este é um e-mail de teste do Dashboard Semear.
    
    Sua configuração de e-mail está funcionando corretamente!
    
    Você pode agora enviar tokens para os operadores.
    
    ---
    Dashboard Semear - Sistema de Gestão de Pagamentos
    """
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_REMETENTE, EMAIL_SENHA)
        server.send_message(msg)
        server.quit()
        
        print(f"[OK] E-mail de teste enviado para {destinatario}")
        return True
        
    except Exception as e:
        print(f"[ERRO] Falha no e-mail de teste: {str(e)}")
        return False
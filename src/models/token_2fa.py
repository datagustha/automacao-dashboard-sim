# models/token_2fa.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from sqlalchemy.orm import declarative_base # A base declarativa cria um vínculo entre a classe Python e a tabela do banco de dados

# Criamos a Base. Todos os nossos modelos vão 'herdar' dessa Base
Base = declarative_base()

class Token2FA(Base):
    __tablename__ = "token_2fa"
    
    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False)
    codigo = Column(String(6), nullable=False)  # 6 dígitos
    criado_em = Column(DateTime, server_default=func.now())
    expira_em = Column(DateTime, nullable=False)  # 5-10 minutos
    usado = Column(Boolean, default=False)
    tentativas = Column(Integer, default=0)  # controle de tentativas
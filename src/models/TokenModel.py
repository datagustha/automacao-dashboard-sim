# src/models/TokenModel.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class TokenRecuperacao(Base):
    __tablename__ = "tokens_recuperacao"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(255))
    token = Column(String(10))
    tipo = Column(String(20), default='primeiro_acesso')
    expira_em = Column(DateTime, default=lambda: datetime.now())
    usado = Column(Boolean, default=False)
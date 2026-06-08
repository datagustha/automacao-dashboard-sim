import sys
import os

# Adiciona o diretório do projeto ao sys.path para importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.config.database import engine
from src.models.LoginModel import analistas
from src.services.db_service import buscar_todos_operadores_por_banco, buscar_pagamentos_todos_operadores_por_banco

with Session(engine) as session:
    ops = session.query(analistas).all()
    print(f"Total de operadores no banco: {len(ops)}")
    for op in ops:
        print(f"Login: {op.loguin}, Nome: {op.nome_completo}, Banco: {op.banco}, Atividade: '{op.atividade}', Turno: {op.turno}")

print("\nBuscando via função do db_service:")
ops_semear = buscar_todos_operadores_por_banco("SEMEAR")
print(f"Operadores SEMEAR: {len(ops_semear)}")
ops_agora = buscar_todos_operadores_por_banco("AGORACRED")
print(f"Operadores AGORACRED: {len(ops_agora)}")

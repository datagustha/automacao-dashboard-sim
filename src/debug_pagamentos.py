import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.config.database import engine
from src.models.PgtoSemearModel import PgtoSemearBoleto
from src.models.PgtoAgoracredModel import PgtoAgoracred

with Session(engine) as session:
    semear_count = session.query(PgtoSemearBoleto).count()
    agora_count = session.query(PgtoAgoracred).count()
    print(f"Total pagamentos SEMEAR: {semear_count}")
    print(f"Total pagamentos AGORACRED: {agora_count}")
    
    if semear_count > 0:
        p_semear = session.query(PgtoSemearBoleto).order_by(PgtoSemearBoleto.dtPgto.desc()).limit(5).all()
        print("\nÚltimos 5 pagamentos SEMEAR:")
        for p in p_semear:
            print(f"Operador: {p.operador}, Data: {p.dtPgto}, Valor: {p.valorTotal}, Fase: {p.faseAtraso}")
            
    if agora_count > 0:
        p_agora = session.query(PgtoAgoracred).order_by(PgtoAgoracred.dtPgto.desc()).limit(5).all()
        print("\nÚltimos 5 pagamentos AGORACRED:")
        for p in p_agora:
            print(f"Operador: {p.operador}, Data: {p.dtPgto}, Valor: {p.valorTotal}, Fase: {p.faseAtraso}")

    # Distribuição por ano/mês
    print("\nDistribuição de pagamentos SEMEAR por ano/mês:")
    res_semear = session.execute("SELECT YEAR(dtPgto) as ano, MONTH(dtPgto) as mes, COUNT(*) as qtd, SUM(valorTotal) as total FROM fpgtoSemear GROUP BY ano, mes ORDER BY ano DESC, mes DESC LIMIT 12").fetchall()
    for row in res_semear:
        print(f"Ano: {row[0]}, Mês: {row[1]}, Qtd: {row[2]}, Faturamento: R$ {row[3]:,.2f}")

    print("\nDistribuição de pagamentos AGORACRED por ano/mês:")
    res_agora = session.execute("SELECT YEAR(dtPgto) as ano, MONTH(dtPgto) as mes, COUNT(*) as qtd, SUM(valorTotal) as total FROM fpgtoAgoracred GROUP BY ano, mes ORDER BY ano DESC, mes DESC LIMIT 12").fetchall()
    for row in res_agora:
        print(f"Ano: {row[0]}, Mês: {row[1]}, Qtd: {row[2]}, Faturamento: R$ {row[3]:,.2f}")

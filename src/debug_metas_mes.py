import sys
import os
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.config.database import engine

with Session(engine) as session:
    print("Metas SEMEAR por mês/ano:")
    res_semear = session.execute(text("SELECT YEAR(data) as ano, MONTH(data) as mes, COUNT(*) as qtd, SUM(meta100) as total FROM fmetaSemearop GROUP BY ano, mes ORDER BY ano DESC, mes DESC LIMIT 12")).fetchall()
    for row in res_semear:
        print(f"Ano: {row[0]}, Mês: {row[1]}, Qtd: {row[2]}, Meta Total: R$ {row[3]:,.2f}")

    print("\nMetas AGORACRED por mês/ano:")
    res_agora = session.execute(text("SELECT YEAR(data) as ano, MONTH(data) as mes, COUNT(*) as qtd, SUM(meta100) as total FROM fmetaAgoracredop GROUP BY ano, mes ORDER BY ano DESC, mes DESC LIMIT 12")).fetchall()
    for row in res_agora:
        print(f"Ano: {row[0]}, Mês: {row[1]}, Qtd: {row[2]}, Meta Total: R$ {row[3]:,.2f}")

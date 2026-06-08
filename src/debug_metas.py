import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.config.database import engine
from src.models.MetassemearModel import Metas_semear
from src.models.MetasagoracredModel import Metas_agoracred

with Session(engine) as session:
    print("Contagem metas SEMEAR:", session.query(Metas_semear).count())
    print("Contagem metas AGORACRED:", session.query(Metas_agoracred).count())
    
    m_semear = session.query(Metas_semear).limit(3).all()
    print("\nExemplo meta SEMEAR:")
    for m in m_semear:
        print(f"Operador: {m.operador}, Data: {m.data} (tipo: {type(m.data)}), Meta100: {m.meta100}")
        
    m_agoracred = session.query(Metas_agoracred).limit(3).all()
    print("\nExemplo meta AGORACRED:")
    for m in m_agoracred:
        print(f"Operador: {m.operador}, Data: {m.data} (tipo: {type(m.data)}), Meta100: {m.meta100}")

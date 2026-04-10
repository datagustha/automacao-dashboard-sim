from sqlalchemy import Column, Integer, String, Float, Date, DateTime # Importamos os tipos de dados que usaremos nas colunas
from sqlalchemy.orm import declarative_base # A base declarativa cria um vínculo entre a classe Python e a tabela do banco de dados

# Criamos a Base. Todos os nossos modelos vão 'herdar' dessa Base
Base = declarative_base()

# Definimos o nosso Modelo (Model). Cada modelo representa uma Tabela no banco de dados.
class Metas_agoracred(Base):
    # O atributo __tablename__ informa ao SQLAlchemy qual é o nome exato da tabela lá no MySQL
    __tablename__ = "fmetaAgoracredop" # ← exatamente igual ao MySQLante

    # Definimos cada uma das colunas. A 'primary_key=True' indica que 'id' é o que diferencia uma linha da outra (tipo um CPF único)
    # Autoincrement=True significa que o próprio banco vai adicionar +1 a cada nova linha
    id = Column(Integer, primary_key=True, autoincrement=True)  # ← ADICIONE ESTA LINHA
    data = Column(Date)
    operador = Column(String(255))
    turno = Column(String(255))
    meta70 = Column(Float)
    meta80 = Column(Float)
    meta90 = Column(Float)
    meta100 = Column(Float)
    metaRanking = Column(Float)
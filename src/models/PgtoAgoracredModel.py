from sqlalchemy import Column, Integer, String, Float, Date, DateTime # Importamos os tipos de dados que usaremos nas colunas
from sqlalchemy.orm import declarative_base # A base declarativa cria um vínculo entre a classe Python e a tabela do banco de dados

# Criamos a Base. Todos os nossos modelos vão 'herdar' dessa Base
Base = declarative_base()

# Definimos o nosso Modelo (Model). Cada modelo representa uma Tabela no banco de dados.
class PgtoAgoracred(Base):
    # O atributo __tablename__ informa ao SQLAlchemy qual é o nome exato da tabela lá no MySQL
    __tablename__ = "fpgtoAgoracred"

    # Definimos cada uma das colunas. A 'primary_key=True' indica que 'id' é o que diferencia uma linha da outra (tipo um CPF único)
    # Autoincrement=True significa que o próprio banco vai adicionar +1 a cada nova linha
    id = Column(Integer, primary_key=True, autoincrement=True) 
    
    cliente = Column(String(255), nullable=True)     # nullable=True significa que a coluna aceita ficar vazia (NULL)
    fase = Column(String(50), nullable=True)         # Nome da fase
    contrato = Column(String(100), nullable=True)    # Código do contrato
    dtAcordo = Column(Date, nullable=True)           # Data em que o acordo foi feito
    dtPgto = Column(DateTime, nullable=True)         # Data (e hora) exata do pagamento
    parcela = Column(Integer, nullable=True)         # Número da Parcela
    plano = Column(Integer, nullable=True)           # Quantidade de vezes do plano
    vctoParc = Column(Date, nullable=True)           # Vencimento original da parcela
    
    principal = Column(Float, nullable=True)         # Valor principal
    multa = Column(Float, nullable=True)             # Valor de multa
    juros = Column(Float, nullable=True)             # Valor de juros
    despesa = Column(Float, nullable=True)           # Valor de despesas extras
    valorTotal = Column(Float, nullable=True)        # Total pago
    
    operador = Column(String(100), nullable=True)    # Quem intermediou (operador)
    filial = Column(String(100), nullable=True)      # A filial ligada (às vezes vazio)
    
    atraso = Column(Integer, nullable=True)          # Dias em atraso daquela parcela
    maiorAtraso = Column(Integer, nullable=True)     # O maior atraso de todas as parcelas do contrato
    faseAtraso = Column(String(255), nullable=True)  # Nome da faixa de atraso (ex: 'Fase 31 a 60')

# Importa a classe Session para gerenciar a transacao com o banco de dados
from sqlalchemy.orm import Session
# Importa o engine de conexao com o banco de dados
from src.config.database import engine
# Importa o modelo de metas do SEMEAR
from src.models.MetassemearModel import Metas_semear
# Importa o modelo de analistas (operadores)
from src.models.LoginModel import analistas
# Importa o modulo datetime para manipulacao de datas
import datetime

def main():
    print("Conectando ao banco de dados para verificar as metas apos a correcao...")
    
    with Session(engine) as session:
        try:
            # Verifica como ficou a soma total de metas do SEMEAR para maio/2026
            start_date = datetime.date(2026, 5, 1)
            end_date = datetime.date(2026, 5, 31)
            
            metas_restantes = session.query(Metas_semear).filter(
                Metas_semear.data >= start_date,
                Metas_semear.data <= end_date
            ).all()
            
            soma = 0
            print("\nMetas remanescentes para Maio/2026:")
            for m in metas_restantes:
                analista = session.query(analistas).filter(analistas.loguin == m.operador).first()
                status = analista.atividade if analista else "Nao cadastrado"
                print(f"ID Meta: {m.id} | Operador: {m.operador} | Atividade: {status} | Meta100: R$ {m.meta100:,.2f}")
                soma += m.meta100
                
            print(f"\nSOMA TOTAL DAS METAS SEMEAR: R$ {soma:,.2f}")
            
        except Exception as e:
            print(f"Erro ao consultar as metas: {str(e)}")

if __name__ == "__main__":
    main()

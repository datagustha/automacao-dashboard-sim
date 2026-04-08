import pandas as pd
from sqlalchemy.orm import Session
# Imports Absolutos, como mandam as regras do projeto
from src.config.database import engine
from src.models.PgtoSemearModel import PgtoSemearBoleto
from src.models.LoginModel import analistas
from src.models.MetasModel import Metas

def enviar_para_banco(df: pd.DataFrame):
    """
    Função dedicada a guardar informações no Banco de Dados usando o modelo ORM do SQLAlchemy.
    Ela recebe o nosso glorioso DataFrame pandas gerado na fase de Análise de Dados.
    """
    
    if df is None or df.empty:
        print("[AVISO] DataFrame vazio, nada a enviar para o banco de dados.")
        return

    print("Iniciando injeção de dados no MySQL...")

    # CUIDADO REDOBRADO AQUI: Nós SEMPRE usamos a 'Session' englobada num 'with' (context manager).
    # Qual o motivo e a MÁGICA? 
    # Quando saímos do bloco 'with', o Python é inteligente para soltar a conexão de banco, fechando o tunel
    # Isso evita "Resource Leak" (vazamentos) bloqueando seu MySQL no futuro e não exigindo um connection.close() manual.
    with Session(engine) as session:
        
        # Iteramos (passamos um por um) nas linhas do excel em memória construído com Pandas
        for index, row in df.iterrows():
            try:
                # 1. VERIFICAR DUPLICATAS USANDO METODOLOGIA DO SQLALCHEMY
                # Aqui traduzimos aquele seu clássico (SELECT COUNT(*) from ...) 
                # para uma query pythonizada muito mais robusta contra Injection.
                # Explicando o query:
                # - Ele pega a nossa "fôrma" 'PgtoSemearBoleto'
                # - Filtra (o Where) usando as colunas preenchidas
                # - 'first()' pega o primeiro que achar rapidinho. Se achar 1, paramos por ai.
                registro_existe = session.query(PgtoSemearBoleto).filter(
                    PgtoSemearBoleto.contrato == str(row['contrato']),
                    PgtoSemearBoleto.parcela == row['parcela'],
                    PgtoSemearBoleto.vctoParc == row['vctoParc'],
                    PgtoSemearBoleto.dtPgto == row['dtPgto']
                ).first()

                if registro_existe:
                    # Se tiver a variável preenchida, é porque ele achou no banco já lançado
                    print(f"[IGNORADO] Registro (Contrato {row['contrato']} - Cliente {row['cliente']} - Data {row['dtPgto']}) ignorado (já existe).")
                else:
                    # 2. INSERIR
                    # Pra inserir dados a gente "instancia" o nosso ORM passando nossas linhas Pandas -> Atributos SQLAlchemy
                    novo_pagamento = PgtoSemearBoleto(
                        cliente = str(row['cliente']) if pd.notna(row['cliente']) else None,
                        fase = str(row['fase']) if pd.notna(row['fase']) else None,
                        contrato = str(row['contrato']) if pd.notna(row['contrato']) else None,
                        # Para lidar com datas e valores, asseguramos que os nulos pandas 'pd.notna' se tornem Null 'None' no banco relacional
                        dtAcordo = row['dtAcordo'].to_pydatetime() if pd.notna(row['dtAcordo']) else None,
                        dtPgto = row['dtPgto'].to_pydatetime() if pd.notna(row['dtPgto']) else None,
                        parcela = row['parcela'] if pd.notna(row['parcela']) else None,
                        plano = row['plano'] if pd.notna(row['plano']) else None,
                        vctoParc = row['vctoParc'].to_pydatetime() if pd.notna(row['vctoParc']) else None,
                        
                        principal = float(row['principal']) if pd.notna(row['principal']) else None,
                        multa = float(row['multa']) if pd.notna(row['multa']) else None,
                        juros = float(row['juros']) if pd.notna(row['juros']) else None,
                        despesa = float(row['despesa']) if pd.notna(row['despesa']) else None,
                        valorTotal = float(row['valorTotal']) if pd.notna(row['valorTotal']) else None,
                        
                        operador = str(row['operador']) if pd.notna(row['operador']) else None,
                        filial = str(row['filial']) if pd.notna(row['filial']) else None,
                        
                        atraso = row['atraso'] if pd.notna(row['atraso']) else None,
                        maiorAtraso = row['maiorAtraso'] if pd.notna(row['maiorAtraso']) else None,
                        faseAtraso = str(row['faseAtraso']) if pd.notna(row['faseAtraso']) else None
                    )
                    
                    # session.add marca na sacola local de gravação que deve adicionar ela. Ele NÃO vai direto ao banco aqui (economiza rede)
                    session.add(novo_pagamento)
                    
            except Exception as loop_error:
                # O Erro fica no iterador, continua o bloco
                print(f"[ERRO] Falha ao tentar formar o pacote da linha de {row['contrato']}: {str(loop_error)}")
        
        try:
            # 3. O 'COMMIT' FINAL
            # Depois que ele adiciona TODOS na sacola de gravações pendentes em cima ele dá "commit" de uma só vez (Acelerando muito)
            # Commit fecha permanentemente a gravação daquela "transação" local rumo ao banco.
            session.commit()
            print("[SUCESSO] Dados enviados com muito SUCESSO para nosso banco via SQLAlchemy!")
            
        except Exception as e:
            # 4. ROLLBACK
            # Se a panela de pressão estourar por motivo de foreign key errada, ele dá rollback e retira os pacotes engasgados que iam machucar a tabela inteira, revertendo o status
            session.rollback()
            print(f"[ERRO_FATAL] Falhou a escrita no banco! Operações abortadas. Erro Técnico: {str(e)}")
            
    # Ao bater aqui a "session" fecha e estamos livres.

def Buscar_login(login: str):
    with Session(engine) as session:
        try:
            operador = session.query(analistas).filter(
                analistas.loguin == login
            ).first()

            if not operador:
                print(f"[ERRO] Nenhum operador encontrado para: {login}")
                return None

            dados = {
                "login": operador.loguin,
                "imagem": operador.imagem,
                "nome": operador.nome_completo,
                "banco": operador.banco
            }
            
            print(f"[OK] Operador localizado: {dados['nome']}")
            return dados

        except Exception as e:
            print(f"[ERRO] Erro: {str(e)}")
            return None


def Buscar_pagamento(dados_operador: dict):
    if not dados_operador:
        print("[ERRO] Dados do operador não fornecidos")
        return None
    
    with Session(engine) as session:
        try:
            pagamentos = session.query(PgtoSemearBoleto).filter(
                PgtoSemearBoleto.operador == dados_operador["login"]
            ).all()
            
            if not pagamentos:
                print(f"[ERRO] Nenhum pagamento para: {dados_operador['login']}")
                return None
            
            print(f"[OK] Encontrados {len(pagamentos)} pagamentos")
            
            # Converter para lista de dicionários
            lista_pagamentos = []
            for p in pagamentos:
                lista_pagamentos.append({
                    "cliente": p.cliente,
                    "fase": p.fase,
                    "contrato": p.contrato,
                    "dtAcordo": p.dtAcordo,
                    "dtPgto": p.dtPgto,
                    "parcela": p.parcela,
                    "plano": p.plano,
                    "vctoParc": p.vctoParc,
                    "principal": p.principal,
                    "multa": p.multa,
                    "juros": p.juros,
                    "despesa": p.despesa,
                    "valorTotal": p.valorTotal,
                    "operador": p.operador,
                    "filial": p.filial,
                    "atraso": p.atraso,
                    "maiorAtraso": p.maiorAtraso,
                    "faseAtraso": p.faseAtraso
                })
            
            return lista_pagamentos
            
        except Exception as e:
            print(f"[ERRO] Erro ao buscar pagamentos: {str(e)}")
            return None

def buscar_metas(dados_operador: dict):
    """
    Busca as metas de um operador no banco de dados.
    
    Args:
        dados_operador (dict): Dicionário com os dados do operador (vindo do Buscar_login)
        
    Returns:
        list: Lista de dicionários com as metas do operador
    """
    
    if not dados_operador:
        print("[ERRO] Dados do operador não fornecidos")
        return None

    # Abre a sessão com o banco
    with Session(engine) as session:
        try:
            # ================================================================
            # BUSCA AS METAS DO OPERADOR
            # IMPORTANTE: Use um nome DIFERENTE para a variável (ex: 'resultado')
            # Não use o mesmo nome da classe 'Metas'!
            # ================================================================
            
            # ✅ CORRETO: resultado = session.query(Metas).filter(...)
            resultado = session.query(Metas).filter(
                Metas.operador == dados_operador["login"]
            ).all()
            
            # Verifica se encontrou alguma meta
            if not resultado:
                print(f"[ERRO] Nenhuma meta encontrada para: {dados_operador['login']}")
                return None

            # Converte para lista de dicionários
            lista_metas = []
            for meta in resultado:  # ← agora usa 'resultado' ou 'meta'
                lista_metas.append({
                    "operador": meta.operador,
                    "data": meta.data,
                    "turno": meta.turno,
                    "meta70": meta.meta70,
                    "meta80": meta.meta80,
                    "meta90": meta.meta90,
                    "meta100": meta.meta100,
                    "meta_ranking": meta.metaRanking
                })
            
            print(f"[OK] Encontradas {len(lista_metas)} metas para: {dados_operador['login']}")
            return lista_metas

        except Exception as e:
            print(f"[ERRO] Erro ao buscar metas: {str(e)}")
            return None
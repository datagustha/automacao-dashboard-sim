"""
SERVIÇO DE ACESSO AO BANCO DE DADOS
====================================

ARQUIVO: db_service.py
LOCAL: src/services/

RESPONSABILIDADE:
- Única camada do sistema que se comunica diretamente com o MySQL
- Todas as consultas ao banco passam por este arquivo
- Suporta dois bancos: SEMEAR e AGORACRED

PRINCÍPIOS:
- Nenhuma outra parte do sistema faz consultas diretas ao banco
- Todas as funções usam `with Session(engine) as session` (fecha automaticamente)
- Retornam dados em formatos simples (dicionários, listas)
- Funções de busca recebem dicionário do operador (vindo de Buscar_login)

ESTRUTURA DO ARQUIVO:
1. FUNÇÕES DE INSERÇÃO (enviar dados para o banco)
2. FUNÇÕES DE BUSCA - LOGIN (Buscar_login)
3. FUNÇÕES DE BUSCA - PAGAMENTOS (SEMEAR e AGORACRED)
4. FUNÇÕES DE BUSCA - METAS (SEMEAR e AGORACRED)
5. FUNÇÕES GENÉRICAS (para o dashboard)
"""

import pandas as pd
from sqlalchemy.orm import Session
from src.config.database import engine
from src.models.PgtoSemearModel import PgtoSemearBoleto
from src.models.PgtoAgoracredModel import PgtoAgoracred
from src.models.LoginModel import analistas
from src.models.MetassemearModel import Metas_semear
from src.models.MetasagoracredModel import Metas_agoracred


# ================================================================
# 1. FUNÇÕES DE INSERÇÃO (ENVIO PARA BANCO)
# ================================================================

def enviar_para_banco_semear(df: pd.DataFrame):
    """
    INSERE DADOS DE PAGAMENTO SEMEAR NO BANCO DE DADOS.
    
    O QUE FAZ:
    - Recebe um DataFrame do Pandas com os dados tratados
    - Abre uma sessão com o banco
    - Para cada linha do DataFrame:
      a) Verifica se o registro já existe (evita duplicatas)
      b) Se não existe, cria um novo objeto PgtoSemearBoleto
      c) Adiciona na sessão
    - Dá commit (salva tudo de uma vez)
    - Se erro, faz rollback (desfaz tudo)
    
    COMO EVITA DUPLICATAS:
    - Verifica se já existe um registro com o mesmo:
      * contrato
      * parcela
      * data de vencimento (vctoParc)
      * data de pagamento (dtPgto)
    
    ARGS:
        df: DataFrame do Pandas com os dados processados
    
    RETORNO:
        None (apenas printa mensagens no terminal)
    """
    
    # VALIDAÇÃO: Se o DataFrame está vazio, não faz nada
    if df is None or df.empty:
        print("[AVISO] DataFrame vazio, nada a enviar.")
        return

    print("Iniciando injeção de dados SEMEAR no MySQL...")

    # Abre a sessão com o banco (o 'with' fecha automaticamente ao sair)
    with Session(engine) as session:
        
        # Itera sobre cada linha do DataFrame
        for index, row in df.iterrows():
            try:
                # --------------------------------------------------------
                # 1. VERIFICAR SE O REGISTRO JÁ EXISTE (EVITAR DUPLICATAS)
                # --------------------------------------------------------
                registro_existe = session.query(PgtoSemearBoleto).filter(
                    PgtoSemearBoleto.contrato == str(row['contrato']),
                    PgtoSemearBoleto.parcela == row['parcela'],
                    PgtoSemearBoleto.vctoParc == row['vctoParc'],
                    PgtoSemearBoleto.dtPgto == row['dtPgto']
                ).first()

                if registro_existe:
                    # Se já existe, ignora e continua para a próxima linha
                    print(f"[IGNORADO] Registro já existe: {row['contrato']}")
                else:
                    # ----------------------------------------------------
                    # 2. CRIAR NOVO REGISTRO
                    # ----------------------------------------------------
                    # Cria um objeto PgtoSemearBoleto com os dados da linha
                    # pd.notna() verifica se o valor não é nulo (NaN)
                    # Se for nulo, coloca None (NULL no banco)
                    novo_pagamento = PgtoSemearBoleto(
                        cliente=str(row['cliente']) if pd.notna(row['cliente']) else None,
                        fase=str(row['fase']) if pd.notna(row['fase']) else None,
                        contrato=str(row['contrato']) if pd.notna(row['contrato']) else None,
                        dtAcordo=row['dtAcordo'].to_pydatetime() if pd.notna(row['dtAcordo']) else None,
                        dtPgto=row['dtPgto'].to_pydatetime() if pd.notna(row['dtPgto']) else None,
                        parcela=row['parcela'] if pd.notna(row['parcela']) else None,
                        plano=row['plano'] if pd.notna(row['plano']) else None,
                        vctoParc=row['vctoParc'].to_pydatetime() if pd.notna(row['vctoParc']) else None,
                        principal=float(row['principal']) if pd.notna(row['principal']) else None,
                        multa=float(row['multa']) if pd.notna(row['multa']) else None,
                        juros=float(row['juros']) if pd.notna(row['juros']) else None,
                        despesa=float(row['despesa']) if pd.notna(row['despesa']) else None,
                        valorTotal=float(row['valorTotal']) if pd.notna(row['valorTotal']) else None,
                        operador=str(row['operador']) if pd.notna(row['operador']) else None,
                        filial=str(row['filial']) if pd.notna(row['filial']) else None,
                        atraso=row['atraso'] if pd.notna(row['atraso']) else None,
                        maiorAtraso=row['maiorAtraso'] if pd.notna(row['maiorAtraso']) else None,
                        faseAtraso=str(row['faseAtraso']) if pd.notna(row['faseAtraso']) else None
                    )
                    
                    # Adiciona o objeto à sessão (ainda não foi salvo no banco)
                    session.add(novo_pagamento)
                    
            except Exception as loop_error:
                # Se erro em uma linha, continua para as próximas
                print(f"[ERRO] Falha na linha {row['contrato']}: {str(loop_error)}")
        
        # --------------------------------------------------------
        # 3. COMMIT (SALVAR TUDO DE UMA VEZ)
        # --------------------------------------------------------
        try:
            session.commit()  # Salva todas as alterações no banco
            print("[SUCESSO] Dados SEMEAR enviados com sucesso!")
        except Exception as e:
            # ----------------------------------------------------
            # 4. ROLLBACK (DESFAZER TUDO EM CASO DE ERRO)
            # ----------------------------------------------------
            session.rollback()  # Desfaz todas as alterações pendentes
            print(f"[ERRO_FATAL] Falha na escrita SEMEAR: {str(e)}")


def enviar_para_banco_agoracred(df: pd.DataFrame):
    """
    INSERE DADOS DE PAGAMENTO AGORACRED NO BANCO DE DADOS.
    
    Funcionamento IDÊNTICO ao enviar_para_banco_semear,
    mas usando a tabela fpgtoAgoracred.
    
    ARGS:
        df: DataFrame do Pandas com os dados processados
    
    RETORNO:
        None (apenas printa mensagens no terminal)
    """
    
    if df is None or df.empty:
        print("[AVISO] DataFrame vazio, nada a enviar.")
        return

    print("Iniciando injeção de dados AGORACRED no MySQL...")

    with Session(engine) as session:
        for index, row in df.iterrows():
            try:
                registro_existe = session.query(PgtoAgoracred).filter(
                    PgtoAgoracred.contrato == str(row['contrato']),
                    PgtoAgoracred.parcela == row['parcela'],
                    PgtoAgoracred.vctoParc == row['vctoParc'],
                    PgtoAgoracred.dtPgto == row['dtPgto']
                ).first()

                if registro_existe:
                    print(f"[IGNORADO] Registro já existe: {row['contrato']}")
                else:
                    novo_pagamento = PgtoAgoracred(
                        cliente=str(row['cliente']) if pd.notna(row['cliente']) else None,
                        fase=str(row['fase']) if pd.notna(row['fase']) else None,
                        contrato=str(row['contrato']) if pd.notna(row['contrato']) else None,
                        dtAcordo=row['dtAcordo'].to_pydatetime() if pd.notna(row['dtAcordo']) else None,
                        dtPgto=row['dtPgto'].to_pydatetime() if pd.notna(row['dtPgto']) else None,
                        parcela=row['parcela'] if pd.notna(row['parcela']) else None,
                        plano=row['plano'] if pd.notna(row['plano']) else None,
                        vctoParc=row['vctoParc'].to_pydatetime() if pd.notna(row['vctoParc']) else None,
                        principal=float(row['principal']) if pd.notna(row['principal']) else None,
                        multa=float(row['multa']) if pd.notna(row['multa']) else None,
                        juros=float(row['juros']) if pd.notna(row['juros']) else None,
                        despesa=float(row['despesa']) if pd.notna(row['despesa']) else None,
                        valorTotal=float(row['valorTotal']) if pd.notna(row['valorTotal']) else None,
                        operador=str(row['operador']) if pd.notna(row['operador']) else None,
                        filial=str(row['filial']) if pd.notna(row['filial']) else None,
                        atraso=row['atraso'] if pd.notna(row['atraso']) else None,
                        maiorAtraso=row['maiorAtraso'] if pd.notna(row['maiorAtraso']) else None,
                        faseAtraso=str(row['faseAtraso']) if pd.notna(row['faseAtraso']) else None
                    )
                    session.add(novo_pagamento)
                    
            except Exception as loop_error:
                print(f"[ERRO] Falha na linha {row['contrato']}: {str(loop_error)}")
        
        try:
            session.commit()
            print("[SUCESSO] Dados AGORACRED enviados com sucesso!")
        except Exception as e:
            session.rollback()
            print(f"[ERRO_FATAL] Falha na escrita AGORACRED: {str(e)}")


# ================================================================
# 2. FUNÇÕES DE BUSCA - LOGIN
# ================================================================

def Buscar_login(login: str):
    """
    BUSCA UM OPERADOR PELO LOGIN NA TABELA d_analista.
    
    O QUE FAZ:
    - Abre uma sessão com o banco
    - Faz uma query na tabela analistas (d_analista)
    - Filtra pelo campo 'loguin'
    - Pega o primeiro resultado (.first())
    - Converte o objeto SQLAlchemy em dicionário
    
    ARGS:
        login: Login do operador (ex: "2552ROSELI")
    
    RETORNO:
        dict: Dicionário com dados do operador
        None: Se o operador não for encontrado
    
    EXEMPLO DE RETORNO:
        {
            "login": "2552ROSELI",
            "imagem": "https://i.ibb.co/...",
            "nome": "ROSELI BATISTA DOS SANTOS",
            "banco": "SEMEAR",
            "email": "roseli@gmail.com",
            "senha_hash": "pbkdf2:sha256:600000$...",
            "primeiro_acesso": False
        }
    """
    
    # Abre a sessão (o 'with' fecha automaticamente)
    with Session(engine) as session:
        try:
            # Query: SELECT * FROM d_analista WHERE loguin = 'valor'
            operador = session.query(analistas).filter(
                analistas.loguin == login
            ).first()

            # Se não encontrou
            if not operador:
                print(f"[ERRO] Nenhum operador encontrado para: {login}")
                return None

            # Converte para dicionário (mais fácil de usar)
            dados = {
                "login": operador.loguin,
                "imagem": operador.imagem,
                "nome": operador.nome_completo,
                "banco": operador.banco,
                "email": operador.email,
                "senha_hash": operador.senha_hash,
                "primeiro_acesso": operador.primeiro_acesso,
            }
            
            print(f"[OK] Operador localizado: {dados['nome']}")
            return dados

        except Exception as e:
            print(f"[ERRO] Erro: {str(e)}")
            return None


# ================================================================
# 3. FUNÇÕES DE BUSCA - PAGAMENTOS
# ================================================================

def Buscar_pagamento_semear(dados_operador: dict):
    """
    BUSCA TODOS OS PAGAMENTOS SEMEAR DE UM OPERADOR.
    
    O QUE FAZ:
    - Recebe o dicionário do operador (vindo de Buscar_login)
    - Extrai o login do dicionário
    - Faz query na tabela PgtoSemearBoleto
    - Filtra pelo campo 'operador'
    - Retorna lista de dicionários com os pagamentos
    
    ARGS:
        dados_operador: Dicionário com dados do operador
    
    RETORNO:
        list: Lista de dicionários com os pagamentos
        None: Se não houver pagamentos ou erro
    
    EXEMPLO DE RETORNO:
        [
            {
                "cliente": "MARLY ALVES",
                "contrato": "62681655/0",
                "valorTotal": 505.31,
                "dtPgto": "2026-04-01",
                "faseAtraso": "Fora da fase"
            },
            ...
        ]
    """
    
    # VALIDAÇÃO: Verifica se recebeu os dados
    if not dados_operador:
        print("[ERRO] Dados do operador não fornecidos")
        return None
    
    # Abre a sessão
    with Session(engine) as session:
        try:
            # Query: SELECT * FROM fpgtoSemear WHERE operador = 'login'
            pagamentos = session.query(PgtoSemearBoleto).filter(
                PgtoSemearBoleto.operador == dados_operador["login"]
            ).all()
            
            # Se não encontrou pagamentos
            if not pagamentos:
                print(f"[ERRO] Nenhum pagamento SEMEAR para: {dados_operador['login']}")
                return None
            
            print(f"[OK] Encontrados {len(pagamentos)} pagamentos SEMEAR")
            
            # Converte a lista de objetos para lista de dicionários
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
            print(f"[ERRO] Erro ao buscar pagamentos SEMEAR: {str(e)}")
            return None


def Buscar_pagamento_agoracred(dados_operador: dict):
    """
    BUSCA TODOS OS PAGAMENTOS AGORACRED DE UM OPERADOR.
    
    Funcionamento IDÊNTICO ao Buscar_pagamento_semear,
    mas usando a tabela PgtoAgoracred.
    
    ARGS:
        dados_operador: Dicionário com dados do operador
    
    RETORNO:
        list: Lista de dicionários com os pagamentos
        None: Se não houver pagamentos ou erro
    """
    
    if not dados_operador:
        print("[ERRO] Dados do operador não fornecidos")
        return None
    
    with Session(engine) as session:
        try:
            pagamentos = session.query(PgtoAgoracred).filter(
                PgtoAgoracred.operador == dados_operador["login"]
            ).all()
            
            if not pagamentos:
                print(f"[ERRO] Nenhum pagamento AGORACRED para: {dados_operador['login']}")
                return None
            
            print(f"[OK] Encontrados {len(pagamentos)} pagamentos AGORACRED")
            
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
            print(f"[ERRO] Erro ao buscar pagamentos AGORACRED: {str(e)}")
            return None


# ================================================================
# 4. FUNÇÕES DE BUSCA - METAS
# ================================================================

def buscar_metas_semear(dados_operador: dict):
    """
    BUSCA AS METAS SEMEAR DE UM OPERADOR (DADOS HISTÓRICOS MENSAIS).
    
    O QUE FAZ:
    - Recebe o dicionário do operador
    - Faz query na tabela Metas_semear (fmetaSemearop)
    - Filtra pelo campo 'operador'
    - Retorna lista de metas (uma por mês)
    
    ARGS:
        dados_operador: Dicionário com dados do operador
    
    RETORNO:
        list: Lista de dicionários com as metas
        None: Se não houver metas ou erro
    
    EXEMPLO DE RETORNO:
        [
            {
                "operador": "2552ROSELI",
                "data": "2026-01-01",
                "meta70": 71110.2,
                "meta80": 81268.8,
                "meta90": 92443.3,
                "meta100": 101586.0
            },
            ...
        ]
    """
    
    if not dados_operador:
        print("[ERRO] Dados do operador não fornecidos")
        return None

    with Session(engine) as session:
        try:
            resultado = session.query(Metas_semear).filter(
                Metas_semear.operador == dados_operador["login"]
            ).all()
            
            if not resultado:
                print(f"[ERRO] Nenhuma meta SEMEAR encontrada para: {dados_operador['login']}")
                return None

            lista_metas = []
            for meta in resultado:
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
            
            print(f"[OK] Encontradas {len(lista_metas)} metas SEMEAR")
            return lista_metas

        except Exception as e:
            print(f"[ERRO] Erro ao buscar metas SEMEAR: {str(e)}")
            return None


def buscar_metas_agoracred(dados_operador: dict):
    """
    BUSCA AS METAS AGORACRED DE UM OPERADOR.
    
    Funcionamento IDÊNTICO ao buscar_metas_semear,
    mas usando a tabela Metas_agoracred (fmetaAgoracredop).
    
    ARGS:
        dados_operador: Dicionário com dados do operador
    
    RETORNO:
        list: Lista de dicionários com as metas
        None: Se não houver metas ou erro
    """
    
    if not dados_operador:
        print("[ERRO] Dados do operador não fornecidos")
        return None

    with Session(engine) as session:
        try:
            resultado = session.query(Metas_agoracred).filter(
                Metas_agoracred.operador == dados_operador["login"]
            ).all()
            
            if not resultado:
                print(f"[ERRO] Nenhuma meta AGORACRED encontrada para: {dados_operador['login']}")
                return None

            lista_metas = []
            for meta in resultado:
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
            
            print(f"[OK] Encontradas {len(lista_metas)} metas AGORACRED")
            return lista_metas

        except Exception as e:
            print(f"[ERRO] Erro ao buscar metas AGORACRED: {str(e)}")
            return None


# ================================================================
# 5. FUNÇÕES GENÉRICAS (PARA O DASHBOARD)
# ================================================================

def Buscar_pagamento_por_operador(dados_operador: dict):
    """
    BUSCA PAGAMENTOS DO OPERADOR BASEADO NO BANCO DELE (FUNÇÃO GENÉRICA).
    
    O QUE FAZ:
    - Verifica o campo 'banco' do operador
    - Se for 'SEMEAR', chama Buscar_pagamento_semear
    - Se for 'AGORACRED', chama Buscar_pagamento_agoracred
    - Se for 'ADM' ou outro, tenta ambos
    
    POR QUE USAR:
    - Simplifica o código do dashboard
    - O callback não precisa saber qual banco chamar
    - Centraliza a lógica de decisão
    
    ARGS:
        dados_operador: Dicionário com dados do operador
    
    RETORNO:
        list: Lista de pagamentos
        None: Se não houver pagamentos
    """
    
    if not dados_operador:
        return None
    
    banco = dados_operador.get('banco')
    
    if banco == 'SEMEAR':
        return Buscar_pagamento_semear(dados_operador)
    elif banco == 'AGORACRED':
        return Buscar_pagamento_agoracred(dados_operador)
    else:
        # Para ADM ou banco não identificado, tenta SEMEAR primeiro
        pagamentos = Buscar_pagamento_semear(dados_operador)
        if pagamentos:
            return pagamentos
        return Buscar_pagamento_agoracred(dados_operador)


def buscar_metas_por_operador(dados_operador: dict):
    """
    BUSCA METAS DO OPERADOR BASEADO NO BANCO DELE (FUNÇÃO GENÉRICA).
    
    Funcionamento IDÊNTICO ao Buscar_pagamento_por_operador,
    mas para as metas.
    
    ARGS:
        dados_operador: Dicionário com dados do operador
    
    RETORNO:
        list: Lista de metas
        None: Se não houver metas
    """
    
    if not dados_operador:
        return None
    
    banco = dados_operador.get('banco')
    
    if banco == 'SEMEAR':
        return buscar_metas_semear(dados_operador)
    elif banco == 'AGORACRED':
        return buscar_metas_agoracred(dados_operador)
    else:
        metas = buscar_metas_semear(dados_operador)
        if metas:
            return metas
        return buscar_metas_agoracred(dados_operador)
import os
import sys
from  IPython.display import display # ambiente jupyter
from tabulate import tabulate

# 1. pegar o caminho atual
caminho_atual = os.path.abspath(__file__)

# 2. voltar pasta de origem
pasta_origigem = os.path.dirname(caminho_atual)

# 3. voltar pasta raiz
pasta_raiz = os.path.dirname(pasta_origigem)

# 4. adicionar pasta sys
sys.path.append(pasta_raiz)

# 5. ver os buscar dados
from src.services.db_service import Buscar_login, buscar_metas_agoracred, buscar_metas_semear

# def test_buscar_metas_semear():

#     operador = Buscar_login("2552ROSELI")

#     if operador:
#         print(operador)

#         pagamentos = buscar_metas(operador)
#         print(pagamentos)

#     assert operador is not None

def test_buscar_metas_Agc():

    operador = Buscar_login("2552URSZULLA")

    if operador:
        print(operador)

        pagamentos = buscar_metas_agoracred(operador)
        print(pagamentos)

    assert operador is not None
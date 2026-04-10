import os
import sys


# 1. pegar o caminho atual
caminho_atual = os.path.abspath(__file__)

# 2. voltar pasta de origem
pasta_origigem = os.path.dirname(caminho_atual)

# 3. voltar pasta raiz
pasta_raiz = os.path.dirname(pasta_origigem)

# 4. adicionar pasta sys
sys.path.append(pasta_raiz)

# 5. ver os buscar dados
from src.services.db_service import Buscar_login, Buscar_pagamento_agoracred, Buscar_pagamento_semear

def test_buscar_login():

    operador = Buscar_login("2552ROSELI")

    if operador:
        print(operador)

        Buscar_pagamento_semear(operador)


    assert operador is not None

# def test_buscar_login_agc():

#     operador = Buscar_login("2552URSZULLA")

#     if operador:
#         print(operador)

#         Buscar_pagamento_agoracred(operador)

       

#     assert operador is not None
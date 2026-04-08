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

# 5. ver os dados
from src.analysis.data_processor import processar_arquivos_brutos
from src.services.db_service import enviar_para_banco

# auxiliar
 
datas   = {
        
        "mesnum"   : 4,
        "anoatual" : 2026,
        "mesabrev" : "Abr"
}

print(datas["mesnum"])

def test_data():
    print('Dados para envio')

    # Unpacking direto do dicionário
    resultado = processar_arquivos_brutos(
        datas["anoatual"], 
        datas["mesnum"], 
        datas["mesabrev"]
    )

    if resultado is not None:
        display(resultado)

        enviar_resultado = enviar_para_banco(resultado)
    assert resultado is not None

# def test_send_data():
#     print('Enviando Dados para envio')

#     resultado = enviar_para_banco()


#     assert resultado is not None

# verifica se existe

# pasta_input = os.path.join(r"C:\Users\T9\Desktop\all\SEMEAR\Recebimento semear\pgto boleto", str(datas["anoatual"]), f"{datas['mesnum']}. {datas['mesabrev']}")

# if os.path.exists(pasta_input):
#     print("encontrei")


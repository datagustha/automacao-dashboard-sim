import os
import sys

# arquivo criado para testa a funcao mover arquivo

# 1. pegar o caminho atual do arquivo
arquivo_atual = os.path.abspath(__file__)

# print(f'arquivo atual: {arquivo_atual}')

# 2. voltar a ao nivel de pasta
nivel_pasta = os.path.dirname(arquivo_atual)
# print(f'arquivo nivel pasta: {nivel_pasta}')

# 3. voltar para nivel raiz
nivel_raiz = os.path.dirname(nivel_pasta)
# print(f'arquivo nivel raiz: {nivel_raiz}')

# 4. colocar pasta raiz no sys
pasta_final = sys.path.append(nivel_raiz)
# print(f'arquivos no pasta_final: {pasta_final}')
# print(type(sys.path))

# 4. visualizar pastas 
# pastas_sys = [ print(f"Achei: {arqivo}" if arquivo == nivel_raiz  else {f"Não confere: {arquivo}"})  for arquivo in enumerate( sys.path, 1 )]
# print(pastas_sys)


# 5. chamar a funcao a ser testada
from src.services.scraper_service import mover_arquivo_para_raw, baixar_relatorio_portal

# 6. criar funcões para test

# def test_downlaod_arquivo():
#     print("Funcao download_arquivo o scraper seguro via PyTest!")
#     resultado = baixar_relatorio_portal()
#     assert resultado is not None

# def test_mover_arquivo():
#     print("Testando o scraper seguro via PyTest!")
#     info_arquivo = baixar_relatorio_portal()
#     resultado = mover_arquivo_para_raw()
#     assert resultado is not None # Garante absoluta certeza que a rotina devolveu algo válido


def test_fluxo_completo():
    # Roda o download primeiro
    info_arquivo = baixar_relatorio_portal()
    assert info_arquivo is not None

#     # Passa o retorno para a próxima função
    caminho = mover_arquivo_para_raw(info_arquivo)
    assert caminho is not None
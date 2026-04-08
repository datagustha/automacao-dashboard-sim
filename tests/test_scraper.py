import sys
import os

# ==============================================================================
# DESMEMBRANDO A MÁGICA DO SYS.PATH (Passo a Passo Didático)
# ==============================================================================

# Passo 1: Pegar o caminho exato onde *este* arquivo atual (test_scraper.py) está no Windows.
# O '__file__' é uma variável secreta nativa que guarda o nome deste arquivo, 
# e o abspath() assegura que não tenha cortes se rodar em outro SO, e vira absoluto.
# RETORNO AQUI É: "C:\...\1. pagamentos-auto\semear\tests\test_scraper.py"
arquivo_atual = os.path.abspath(__file__)
# print(f'1. arquivo atual: {arquivo_atual}')

# Passo 2: Descobrir em qual pasta esse arquivo mora (subir um nível na árvore).
# O .dirname corta o final /test_scraper.py da string acima, deixando só a pasta.
# RETORNO AQUI É: "C:\...\1. pagamentos-auto\semear\tests"
pasta_tests = os.path.dirname(arquivo_atual)
# print(f'2. pasta tests: {pasta_tests}')

# Passo 3: Descobrir a pasta raiz do projeto (subir mais um nível).
# Chamamos o .dirname de novo em cima da variável anterior para rancar o \tests do final.
# Desse jeito chegamos na mãe de todas as pastas onde fica o nosso 'src/' e os dados soltos.
# RETORNO AQUI É: "C:\...\1. pagamentos-auto\semear"
pasta_raiz_projeto = os.path.dirname(pasta_tests)
# print(f'3. pasta raiz projeto: {pasta_raiz_projeto}')

# Passo 4: Finalmente, injetar essa pasta na sacola da memória do Python.
# O 'sys.path' funciona do inglês = (Caminho do Sistema). Isso é uma lista gigantesca! 
# Onde lá dentro estão guardados todos os diretórios do seu windows em que o Python
# entra em desespero procurando sempre que você diz a palavra 'import ...' no código.
# Ao inserir a nossa pasta principal ali dentro, agora o interpretador "vê" o src.
sys.path.append(pasta_raiz_projeto)
# print(f'4. sys.path: {sys.path}')

# A clássica linha única complexa que as pessoas costumam decorar:
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Era apenas tudo isso concentrado em um oneliner!
# ==============================================================================

# 2. Importa a função que quer testar
from src.services.scraper_service import baixar_relatorio_portal

# 3. Roda o bloco apenas aqui dentro:
def test_download_funciona():
    print("Testando o scraper seguro via PyTest!")
    resultado = baixar_relatorio_portal()
    
    # ==========================================================================
    # CÁPSULA DE APRENDIZADO: O QUE É O "ASSERT"?
    # ==========================================================================
    # O "assert" (afirmação) funciona como um Detetive Linha-Dura.
    # Ele obedece a uma regra simples: "Ou você me prova que a condição abaixo é Verdade (True), 
    # ou eu explodo o programa agora mesmo gerando um AssertionError na tela!"
    #
    # Por que ele é útil em testes?
    # Se o Scraper lá em cima falhar, ele deve retornar Vazio (None).
    # Nós usamos a linha abaixo para dizer ao Python:
    # "Garanta para mim que a variável resultado NÃO É VAZIA (is not None)".
    # Se vier cheia (Sucesso), a vida segue perfeita. Se vier vazia, ele quebra avisando que o banco mudou o site!
    # ==========================================================================
    assert resultado is not None  # Garante absoluta certeza que a rotina devolveu algo válido

    # para usar o codigo é só digitar no terminal: pytest tests/test_scraper.py
    # para exibir print usar: pytest -s tests/test_scraper.py

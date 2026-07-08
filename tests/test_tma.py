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
from src.services.scraper_tma_service import _criar_navegador_headless, _fazer_login, _navegar_ate_relatorio_tma, _selecionar_periodo, _configurar_filtros , _gerar_e_aguardar_download
from datetime import datetime, timedelta

def test_tma():

    # testar abrir navegador
    print("Testando o scraper seguro via PyTest!")
    result = _criar_navegador_headless()

    # fazer login
    login = _fazer_login(result)

    # navegar tma
    navegar_relatorio = _navegar_ate_relatorio_tma(
        result
    )

     # Metadados de data
    data = datetime.now()
    mesnum = data.month
    anoatual = data.year
    mesabrev = data.strftime("%b")
    diaatual = data.day


    meses_en = ["january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december"]
    meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    alvo_ingles = meses_en[mesnum - 1]
    alvo_pt = meses_pt[mesnum - 1]

    # periodo
    periodo = _selecionar_periodo(result, alvo_pt= alvo_pt, alvo_ingles= alvo_ingles, anoatual= anoatual)
    
    credor = "BANCO SEMEAR"
    # filtros
    filtros = _configurar_filtros(result, credor)

    import pathlib
    #local
    BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
    
    # pasta_downloads = str(BASE_DIR / "data" / "downloads")

    #baixar relatorio
    baixar =  _gerar_e_aguardar_download(result)

    assert result is not None
    
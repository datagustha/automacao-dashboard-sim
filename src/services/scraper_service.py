"""
scraper_service.py - Versão Corrigida
Cada banco roda em um navegador separado para evitar conflitos.
Aguarda o processamento do relatório e clica em Visualizar para baixar.
"""

import os
import shutil
import time
import pathlib
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

from src.utils.web_utils import clicar_com_seguranca, aguardar_toast_fechar

load_dotenv()

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


def _criar_navegador_headless(pasta_downloads: str = None):
    """
    Cria e retorna um Chrome configurado para rodar em ambiente headless.
    Se pasta_downloads não for informada, usa a padrão do projeto.
    """
    opcoes = Options()
    opcoes.add_argument("--headless=new")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--window-size=1920,1080")

    if pasta_downloads is None:
        pasta_downloads = str(BASE_DIR / "data" / "downloads")
    
    os.makedirs(pasta_downloads, exist_ok=True)
    prefs = {"download.default_directory": pasta_downloads}
    opcoes.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=opcoes), pasta_downloads


def _fazer_login(navegador):
    """Realiza o login no portal."""
    portal_user = os.getenv("PORTAL_USER")
    portal_pass = os.getenv("PORTAL_PASS")

    if not portal_user or not portal_pass:
        raise EnvironmentError("❌ Credenciais não encontradas! Defina PORTAL_USER e PORTAL_PASS no .env")

    navegador.get("https://login.cobmais.com.br/")
    navegador.maximize_window()

    login = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="Username"]'))
    )
    login.send_keys(portal_user)

    senha = navegador.find_element(By.XPATH, '//*[@id="Password"]')
    senha.send_keys(portal_pass)

    navegador.find_element(By.XPATH, '//*[@id="Login"]').click()
    print("  ✅ Login realizado")


def _fechar_popup(navegador):
    """Fecha o popup inicial do portal."""
    print("  Aguardando popup inicial...")
    try:
        popup1 = WebDriverWait(navegador, 40).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="pushActionRefuse" and contains(text(), "Não, obrigado")]')
            )
        )
        popup1.click()
        print("  ✅ Popup fechado com sucesso!")
        time.sleep(1)
    except Exception:
        print("  ⏳ Popup não encontrado, continuando...")
        time.sleep(2)


def _navegar_ate_relatorio_pagamentos(navegador):
    """Navega até a tela de Relatório de Pagamentos."""
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="menusuperior"]/a')
    time.sleep(1)
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="lkbRelatorios"]')
    time.sleep(1)
    clicar_com_seguranca(navegador, By.XPATH, "//span[@class='nav-item-text' and text()='Financeiro']")
    time.sleep(1)
    clicar_com_seguranca(navegador, By.XPATH, "//span[@class='nav-item-text' and text()='Pagamentos']")
    time.sleep(3)
    print("  ✅ Navegou até Relatório de Pagamentos")


def _configurar_filtros(navegador, label_banco: str):
    """Configura os filtros do relatório para o banco específico."""
    # Tipo Analítico
    clicar_com_seguranca(navegador, By.XPATH, "//label[@for='rbTipoAnalitico']")
    time.sleep(1)
    print("  ✅ Tipo Analítico selecionado")

    # Abrir dropdown de bancos
    botao_todos = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'TODOS')]"))
    )
    botao_todos.click()
    time.sleep(1)
    print("  ✅ Dropdown de bancos aberto")

    # Desmarcar todos
    try:
        selecionar_todos = navegador.find_element(By.XPATH, "//label[contains(text(), 'Selecionar Todos')]")
        checkbox = selecionar_todos.find_element(By.XPATH, ".//input")
        if checkbox.is_selected():
            selecionar_todos.click()
            print("  ✅ Todos os bancos desmarcados")
        time.sleep(1)
    except Exception as e:
        print(f"  ⚠️ Erro ao desmarcar todos: {e}")

    # Selecionar o banco desejado
    banco_elem = navegador.find_element(By.XPATH, f"//label[normalize-space()='{label_banco}']")
    banco_elem.click()
    print(f"  ✅ Banco selecionado: {label_banco}")
    time.sleep(1)

    # Fechar dropdown
    botao_todos.click()
    time.sleep(1)
    print("  ✅ Dropdown fechado")


def _selecionar_periodo(navegador, alvo_pt: str, alvo_ingles: str, anoatual: int):
    """Seleciona o período do mês atual (dia 1 até último dia)."""
    # Data Inicial - dia 1
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="dtInicial"]')
    time.sleep(1)
    
    # Navegar até o mês atual
    mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
    ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    while not (mes_x in [alvo_pt, alvo_ingles] and anoatual == int(ano_x)):
        clicar_com_seguranca(navegador, By.XPATH, '//*[@id="ui-datepicker-div"]/div/a[2]/span', timeout=5)
        mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
        ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text
        time.sleep(0.5)

    navegador.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]//a[text()="1"]').click()
    time.sleep(1)
    print("  ✅ Data inicial: dia 1")

    # Data Final - último dia do mês
    navegador.find_element(By.XPATH, '//*[@id="dtFinal"]').click()
    time.sleep(1)
    
    mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
    ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    while not (mes_x in [alvo_pt, alvo_ingles] and anoatual == int(ano_x)):
        clicar_com_seguranca(navegador, By.XPATH, '//*[@id="ui-datepicker-div"]/div/a[2]/span', timeout=5)
        mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
        ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text
        time.sleep(0.5)

    # Seleciona o último dia do mês
    dias_elementos = navegador.find_elements(
        By.XPATH, '//*[@id="ui-datepicker-div"]//a[contains(@class,"ui-state-default")]'
    )
    datas = [int(dia.text.strip()) for dia in dias_elementos if dia.text.strip().isdigit()]
    maiordata = max(datas)
    navegador.find_element(By.XPATH, f'//*[@id="ui-datepicker-div"]//a[text()="{maiordata}"]').click()
    time.sleep(1)
    print(f"  ✅ Data final: dia {maiordata}")


def _selecionar_tipo_pagamento(navegador, banco: str):
    """Para SEMEAR, seleciona 'Pagamento' no Tipo de Finalização."""
    if banco == "semear":
        try:
            tipo = WebDriverWait(navegador, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="selTipoFinalizacao"]'))
            )
            tipo.click()
            time.sleep(1)
            navegador.find_element(By.XPATH, "//option[text()='Pagamento']").click()
            print("  ✅ Tipo de pagamento: Pagamento")
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠️ Erro ao selecionar Pagamento: {e}")
    else:
        print("  ℹ️ Tipo de pagamento: TODOS")


def _gerar_e_aguardar_download(navegador, pasta_downloads: str):
    """
    Clica em Gerar Relatório, aguarda o processamento no portal,
    espera o status ficar 'Processado' e clica no botão Visualizar.
    Aguarda o download completar e retorna o caminho do arquivo.
    """
    # 1. Clicar em Gerar Relatório
    print("  📥 Clicando em Gerar Relatório...")
    navegador.find_element(By.XPATH, '//*[@id="btnGerarOpcoes"]/i').click()
    aguardar_toast_fechar(navegador)
    time.sleep(2)
    
    navegador.find_element(By.XPATH, '//*[@id="frmRelatorio"]/div[2]/div/ul/li[1]/a').click()
    print("  📄 Relatório solicitado, aguardando processamento...")
    time.sleep(3)

    # 2. Fechar popup de processamento se existir
    try:
        fechar = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.ID, "btnFecharEmbedInteracao"))
        )
        fechar.click()
        print("  ✅ Popup de processamento fechado")
        time.sleep(1)
    except:
        pass

    # 3. Aguardar o relatório ficar com status "Processado" e clicar em Visualizar
    tempo_maximo = 300  # 5 minutos
    tempo_inicial = time.time()
    
    while time.time() - tempo_inicial < tempo_maximo:
        # Recarrega a página para ver a tabela atualizada
        navegador.refresh()
        time.sleep(2)
        
        # Aguarda a tabela carregar
        try:
            WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.ID, "tbRelatoriosOperador"))
            )
        except:
            continue
        
        # Procura a primeira linha da tabela (relatório mais recente)
        try:
            primeira_linha = navegador.find_element(By.XPATH, "//*[@id='tbRelatoriosOperador']/tbody/tr[1]")
            status = primeira_linha.find_element(By.XPATH, "./td[2]").text.strip()
            
            print(f"  ⏳ Status do relatório: {status}")
            
            if status.lower() == "processado":
                # Clica no botão Visualizar
                btn_visualizar = primeira_linha.find_element(By.XPATH, "./td[3]//button")
                btn_visualizar.click()
                print("  ✅ Botão Visualizar clicado! Iniciando download...")
                time.sleep(3)
                break
        except Exception as e:
            print(f"  ⏳ Aguardando relatório aparecer na tabela...")
        
        time.sleep(5)
    else:
        raise Exception("❌ Timeout: relatório não ficou Processado após 5 minutos")

    # 4. Aguardar o download completar
    print("  ⏳ Aguardando download finalizar...")
    tempo_inicial = time.time()
    tempo_maximo_download = 180  # 3 minutos
    
    while time.time() - tempo_inicial < tempo_maximo_download:
        arquivos_baixando = [f for f in os.listdir(pasta_downloads) if f.endswith('.crdownload')]
        arquivos_completos = [f for f in os.listdir(pasta_downloads) if f.endswith('.xlsx')]
        
        if arquivos_completos and not arquivos_baixando:
            arquivo = max(arquivos_completos, key=lambda f: os.path.getmtime(os.path.join(pasta_downloads, f)))
            caminho = os.path.join(pasta_downloads, arquivo)
            print(f"  ✅ Download concluído: {arquivo}")
            return caminho
        
        time.sleep(2)
    
    raise Exception(f"❌ Timeout: download não concluído após {tempo_maximo_download} segundos")


def _mover_para_storage(caminho_origem: str, banco: str, anoatual: int, mesnum: int, mesabrev: str, diaatual: int) -> str:
    """Move o arquivo baixado para a pasta de storage com o nome padronizado."""
    destino = BASE_DIR / "data" / "storage" / banco / str(anoatual) / f"{mesnum}. {mesabrev}"
    os.makedirs(destino, exist_ok=True)

    novo_nome = f"{mesnum}. Recebimento boleto {mesabrev} {diaatual} {anoatual}.xlsx"
    caminho_destino = str(destino / novo_nome)

    if os.path.exists(caminho_destino):
        os.remove(caminho_destino)

    shutil.move(caminho_origem, caminho_destino)
    print(f"  ✅ Arquivo movido para: {caminho_destino}")
    return caminho_destino


def baixar_relatorio_portal():
    """
    Ponto de entrada principal.
    Cada banco roda em um navegador completamente novo e isolado.
    """
    print("=" * 60)
    print("Iniciando Web Scraping — Semear + Agoracred")
    print("=" * 60)

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

    resultados = {}
    
    bancos = [
        {"label": "BANCO SEMEAR", "chave": "semear"},
        {"label": "Agoracred Financeira", "chave": "agoracred"},
    ]

    for banco in bancos:
        print(f"\n{'─' * 40}")
        print(f"▶ Processando: {banco['label']}")
        print(f"{'─' * 40}")

        # Limpa a pasta de downloads antes de cada banco
        pasta_downloads = str(BASE_DIR / "data" / "downloads")
        for f in os.listdir(pasta_downloads):
            if f.endswith(".xlsx") or f.endswith(".crdownload"):
                os.remove(os.path.join(pasta_downloads, f))

        # Cria um NOVO navegador para este banco
        navegador, _ = _criar_navegador_headless(pasta_downloads)
        
        try:
            # Login e navegação
            _fazer_login(navegador)
            _fechar_popup(navegador)
            _navegar_ate_relatorio_pagamentos(navegador)
            
            # Configuração dos filtros
            _configurar_filtros(navegador, banco["label"])
            _selecionar_periodo(navegador, alvo_pt, alvo_ingles, anoatual)
            _selecionar_tipo_pagamento(navegador, banco["chave"])
            
            # Gerar relatório e aguardar download
            caminho_baixado = _gerar_e_aguardar_download(navegador, pasta_downloads)
            
            # Mover para storage
            caminho_final = _mover_para_storage(
                caminho_baixado, banco["chave"], anoatual, mesnum, mesabrev, diaatual
            )
            
            resultados[banco["chave"]] = caminho_final
            print(f"  ✅ {banco['label']} processado com sucesso!")
            
        except Exception as e:
            print(f"  ❌ Erro no banco {banco['label']}: {e}")
            resultados[banco["chave"]] = None
        finally:
            navegador.quit()
            print(f"  ✅ Navegador fechado para {banco['label']}")
            time.sleep(3)  # Pausa entre bancos

    print("\n" + "=" * 60)
    print("Scraping finalizado!")
    print(f"Arquivos baixados: {resultados}")
    print("=" * 60)

    info = {
        "arquivos": resultados,
        "mesnum": mesnum,
        "mesabrev": mesabrev,
        "anoatual": anoatual,
        "diaatual": diaatual,
    }
    return info
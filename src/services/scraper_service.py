"""
scraper_service.py
Responsável por acessar o portal, baixar os relatórios (Semear e Agoracred),
e mover os arquivos para a estrutura de pastas do projeto.

Compatível com VPS Ubuntu (headless) e Windows.
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

# Carrega variáveis do .env (credenciais, etc.)
load_dotenv()

# Raiz do projeto (2 níveis acima de src/services/)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


def _criar_navegador_headless():
    """
    Cria e retorna um Chrome configurado para rodar em ambiente
    sem interface gráfica (VPS Ubuntu). Também funciona no Windows.
    """
    opcoes = Options()
    opcoes.add_argument("--headless=new")         # Sem interface gráfica
    opcoes.add_argument("--no-sandbox")            # Obrigatório em VPS Linux
    opcoes.add_argument("--disable-dev-shm-usage") # Evita crash por memória compartilhada
    opcoes.add_argument("--disable-gpu")           # Recomendado em ambiente headless
    opcoes.add_argument("--window-size=1920,1080") # Define tamanho de tela virtual

    # Redireciona os downloads para a pasta /data/downloads/ do projeto
    pasta_downloads = str(BASE_DIR / "data" / "downloads")
    os.makedirs(pasta_downloads, exist_ok=True)
    prefs = {"download.default_directory": pasta_downloads}
    opcoes.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=opcoes), pasta_downloads


def _fazer_login(navegador):
    """Realiza o login no portal. Quebra explicitamente se credenciais não estiverem no .env"""
    portal_user = os.getenv("PORTAL_USER")
    portal_pass = os.getenv("PORTAL_PASS")

    if not portal_user or not portal_pass:
        raise EnvironmentError(
            "❌ Credenciais não encontradas! Defina PORTAL_USER e PORTAL_PASS no arquivo .env"
        )

    navegador.get("https://login.cobmais.com.br/")
    navegador.maximize_window()

    login = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="Username"]'))
    )
    login.send_keys(portal_user)

    senha = navegador.find_element(By.XPATH, '//*[@id="Password"]')
    senha.send_keys(portal_pass)

    navegador.find_element(By.XPATH, '//*[@id="Login"]').click()


def _fechar_popup(navegador):
    """Fecha o popup inicial do portal com retry automático."""
    print("Aguardando popup inicial...")
    while True:
        try:
            popup1 = WebDriverWait(navegador, 40).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="pushActionRefuse" and contains(text(), "Não, obrigado")]')
                )
            )
            popup1.click()
            print("✅ Popup fechado com sucesso!")
            time.sleep(1)
            break
        except Exception:
            print("⏳ Popup ainda não disponível, aguardando 10 segundos...")
            navegador.refresh()
            time.sleep(10)
            break


def _navegar_ate_relatorio_pagamentos(navegador):
    """Navega até a tela de Relatório de Pagamentos."""
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="menusuperior"]/a')
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="lkbRelatorios"]')
    clicar_com_seguranca(navegador, By.XPATH, "//span[@class='nav-item-text' and text()='Financeiro']")
    clicar_com_seguranca(navegador, By.XPATH, "//span[@class='nav-item-text' and text()='Pagamentos']")


def _configurar_filtros(navegador, label_banco: str):
    """
    Configura os filtros do relatório:
    - Tipo: Analítico
    - Status: Processado
    - Banco: conforme label_banco passado
    - Tipo Finalização: opção 4
    """
    # 1. Tipo Analítico
    clicar_com_seguranca(navegador, By.XPATH, "//label[@for='rbTipoAnalitico']")
    time.sleep(0.5)

    # 2. Status: Processado
    status_btn = navegador.find_element(By.CSS_SELECTOR, "#divStatus button.btn.dropdown-toggle")
    status_btn.click()
    time.sleep(0.5)
    
    processado_option = navegador.find_element(By.XPATH, "//li/a/label[contains(text(), 'Processado')]")
    processado_option.click()
    time.sleep(0.5)
    
    status_btn.click()  # Fecha dropdown de status
    time.sleep(0.5)

    # 3. Banco - PRIMEIRO ABRE O DROPDOWN
    # Procura o botão que abre o dropdown de bancos
    banco_btn = navegador.find_element(By.XPATH, "//div[contains(@class, 'multiselect')]//button")
    banco_btn.click()
    time.sleep(1)  # Espera o dropdown abrir

    # Agora seleciona o banco desejado (já está visível)
    banco_elem = navegador.find_element(By.XPATH, f"//label[contains(text(), '{label_banco}')]")
    banco_elem.click()
    time.sleep(0.5)

    # Fecha o dropdown de bancos
    banco_btn.click()
    time.sleep(0.5)

    # 4. Tipo Finalização: opção 4
    navegador.find_element(By.XPATH, '//*[@id="selTipoFinalizacao"]').click()
    time.sleep(0.5)
    navegador.find_element(By.XPATH, '//*[@id="selTipoFinalizacao"]/option[4]').click()
    time.sleep(1)

    aguardar_toast_fechar(navegador)

    aguardar_toast_fechar(navegador)

def _selecionar_periodo(navegador, alvo_pt: str, alvo_ingles: str, anoatual: int):
    """
    Seleciona o período de data inicial (dia 1) e data final (último dia do mês atual).
    Compatível com calendário em PT e EN.
    """
    # Data Inicial: dia 1
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="dtInicial"]')
    mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
    ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    while not (mes_x in [alvo_pt, alvo_ingles] and anoatual == int(ano_x)):
        clicar_com_seguranca(navegador, By.XPATH, '//*[@id="ui-datepicker-div"]/div/a[2]/span', timeout=5)
        mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
        ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    navegador.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]//a[text()="1"]').click()

    # Data Final: último dia do mês
    navegador.find_element(By.XPATH, '//*[@id="dtFinal"]').click()
    mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
    ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    while not (mes_x in [alvo_pt, alvo_ingles] and anoatual == int(ano_x)):
        clicar_com_seguranca(navegador, By.XPATH, '//*[@id="ui-datepicker-div"]/div/a[2]/span', timeout=5)
        mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
        ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    dias_elementos = navegador.find_elements(
        By.XPATH, '//*[@id="ui-datepicker-div"]//a[contains(@class,"ui-state-default")]'
    )
    datas = [int(dia.text.strip()) for dia in dias_elementos if dia.text.strip().isdigit()]
    maiordata = max(datas)
    for dia in dias_elementos:
        if dia.text.strip() == str(maiordata):
            dia.click()
            break


def _disparar_download_e_aguardar(navegador, pasta_downloads: str):
    """
    Clica em Gerar Relatório, aguarda processamento no portal,
    e clica no botão de download. Aguarda o arquivo ser baixado completamente.
    Retorna o nome do arquivo baixado.
    """
    navegador.find_element(By.XPATH, '//*[@id="btnGerarOpcoes"]/i').click()
    aguardar_toast_fechar(navegador)
    navegador.find_element(By.XPATH, '//*[@id="frmRelatorio"]/div[2]/div/ul/li[1]/a').click()

    try:
        WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.ID, "btnFecharEmbedInteracao"))
        ).click()
    except Exception:
        pass

    time.sleep(15)

    # Aguarda o portal processar e disponibilizar o botão de download
    while True:
        navegador.refresh()
        WebDriverWait(navegador, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='tbRelatoriosOperador']/tbody"))
        )

        tr = navegador.find_elements(By.XPATH, "//*[@id='tbRelatoriosOperador']/tbody/tr")
        encontrado = False

        for i in tr:
            try:
                status = i.find_element(By.XPATH, "./td[2]").text.strip()
                if status.lower() == "processado":
                    i.find_element(By.XPATH, "./td[3]//button").click()
                    encontrado = True
                    break
            except Exception:
                continue

        if encontrado:
            break
        time.sleep(10)

    # Aguarda o Chrome terminar o download (arquivo .crdownload some)
    documento = "Relatório de Pagamentos.xlsx"
    while True:
        arquivos = os.listdir(pasta_downloads)
        baixando = any(a.endswith(".crdownload") for a in arquivos)
        ja_existe = any(a.startswith(documento.split(".")[0]) and a.endswith(".xlsx") for a in arquivos)
        if ja_existe and not baixando:
            print(f"✅ Download concluído: {documento}")
            break
        time.sleep(2)

    return documento


def _mover_para_storage(pasta_downloads: str, nome_arquivo: str, banco: str,
                        anoatual: int, mesnum: int, mesabrev: str, diaatual: int) -> str:
    """
    Move o arquivo baixado da pasta de downloads para:
    data/storage/<banco>/<ano>/<mesnum>. <mesabrev>/
    Renomeia seguindo o padrão do projeto.
    Retorna o caminho final do arquivo.
    """
    destino = BASE_DIR / "data" / "storage" / banco / str(anoatual) / f"{mesnum}. {mesabrev}"
    os.makedirs(destino, exist_ok=True)

    novo_nome = f"{mesnum}. Recebimento boleto {mesabrev} {diaatual} {anoatual}.xlsx"
    caminho_origem = os.path.join(pasta_downloads, nome_arquivo)
    caminho_destino = str(destino / novo_nome)

    if os.path.exists(caminho_destino):
        os.remove(caminho_destino)

    shutil.move(caminho_origem, caminho_destino)
    print(f"✅ Arquivo movido para storage: {caminho_destino}")
    return caminho_destino


def baixar_relatorio_portal():
    """
    Ponto de entrada principal do scraper.
    Abre o navegador UMA vez, faz login, e baixa os relatórios
    do BANCO SEMEAR e da AGORACRED sequencialmente.

    Retorna um dicionário com os caminhos dos arquivos e metadados de data,
    prontos para serem consumidos pelo data_processor.
    """
    print("=" * 60)
    print("Iniciando Web Scraping — Semear + Agoracred")
    print("=" * 60)

    # Metadados de data
    data = datetime.now()
    mesnum = data.month
    anoatual = data.year
    mesabrev = data.strftime("%b")

    meses_en = ["january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december"]
    meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    alvo_ingles = meses_en[mesnum - 1]
    alvo_pt = meses_pt[mesnum - 1]

    # Calcula o dia de referência (regra: segunda/terça retrocedem 4 dias, demais 2)
    dias_retroceder = 4 if data.weekday() in [0, 1] else 2
    diaatual = (data - timedelta(days=dias_retroceder)).day

    # Abre o navegador uma única vez
    navegador, pasta_downloads = _criar_navegador_headless()

    resultados = {}

    try:
        _fazer_login(navegador)
        _fechar_popup(navegador)

        # ── Bancos a processar ─────────────────────────────────────────
        bancos = [
            {"label": "BANCO SEMEAR", "chave": "semear"},
            {"label": "Agoracred Financeira",    "chave": "agoracred"},
        ]

        for banco in bancos:
            print(f"\n{'─' * 40}")
            print(f"▶ Processando: {banco['label']}")
            print(f"{'─' * 40}")

            _navegar_ate_relatorio_pagamentos(navegador)
            _configurar_filtros(navegador, banco["label"])
            _selecionar_periodo(navegador, alvo_pt, alvo_ingles, anoatual)

            nome_arquivo = _disparar_download_e_aguardar(navegador, pasta_downloads)

            caminho_final = _mover_para_storage(
                pasta_downloads=pasta_downloads,
                nome_arquivo=nome_arquivo,
                banco=banco["chave"],
                anoatual=anoatual,
                mesnum=mesnum,
                mesabrev=mesabrev,
                diaatual=diaatual,
            )

            resultados[banco["chave"]] = caminho_final

    except Exception as e:
        print(f"❌ Erro crítico no scraper: {e}")
        raise

    finally:
        navegador.quit()
        print("\n✅ Navegador encerrado.")

    # Metadados compartilhados para o processor
    info = {
        "arquivos": resultados,   # {"semear": "/path/...", "agoracred": "/path/..."}
        "mesnum": mesnum,
        "mesabrev": mesabrev,
        "anoatual": anoatual,
        "diaatual": diaatual,
    }

    print(f"\nArquivos baixados: {resultados}")
    return info
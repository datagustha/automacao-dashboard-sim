
#%% 
import os
import shutil
import time
from datetime import datetime, timedelta
import pathlib  
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from src.utils.web_utils import clicar_com_seguranca, aguardar_toast_fechar

def baixar_relatorio_portal():
    """
    Módulo responsável apenas por abrir o navegador, navegar no portal e 
    efetuar o download do arquivo para a pasta padrão (Downloads) do Windows.
    Retorna o nome esperado do arquivo baixado e as datas calculadas.
    """
    print("Iniciando processo de automação de navegador (Web Scraping)...")
    
    data = datetime.now()             
    mesnum = data.month
    anoatual = data.year
    mesabrev = data.strftime("%b")    # Usado lá embaixo só pra dar nome ao arquivo Excel
    
    # Prática Profissional: O Selenium sempre abre um "Chrome Virgem" que frequentemente vem em Inglês, mesmo no Brasil.
    # Mapearemos o alvo a partir do NÚMERO (mesnum), assim caçamos o mês em ambos os idiomas sem falha!
    meses_en = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    
    alvo_ingles = meses_en[mesnum - 1]
    alvo_pt = meses_pt[mesnum - 1]

    # Inicialização do Navegador
    navegador = webdriver.Chrome()
    navegador.get("https://login.cobmais.com.br/") 
    navegador.maximize_window() 
    
    # Login
    login = WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="Username"]'))
    )
    login.send_keys(os.getenv("PORTAL_USER", "2552GUSTHAVO")) 
    
    senha = navegador.find_element(By.XPATH, '//*[@id="Password"]')
    senha.send_keys(os.getenv("PORTAL_PASS", "123456789"))
    
    navegador.find_element(By.XPATH, '//*[@id="Login"]').click()

    # Fechar Popup
    print("Aguardando popup inicial...")
    while True:
        try:
            popup1 = WebDriverWait(navegador, 40).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="pushActionRefuse" and contains(text(), "Não, obrigado")]'))
            )
            popup1.click()
            print("✅ Popup fechado com sucesso!")
            time.sleep(1)
            break
        except Exception:
            print("⏳ Popup ainda não disponível, aguardando 10 segundos para dar refresh...")
            navegador.refresh()
            time.sleep(10)
            break
            
    # Navegação
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="menusuperior"]/a') 
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="lkbRelatorios"]') 
    clicar_com_seguranca(navegador, By.XPATH, "//span[@class ='nav-item-text' and text() = 'Financeiro']")
    clicar_com_seguranca(navegador, By.XPATH, "//span[@class ='nav-item-text' and text() = 'Pagamentos']")
    
    clicar_com_seguranca(navegador, By.XPATH, "//label[@for='rbTipoAnalitico']") 

    navegador.find_element(By.CSS_SELECTOR, "button.btn.dropdown-toggle").click()
    navegador.find_element(By.XPATH, '//*[@id="divStatus"]/div/div[2]/ul/li[2]/a/label').click() 
    
    WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//label[contains(normalize-space(.), "BANCO SEMEAR")]'))
    ).click()
    
    navegador.find_element(By.XPATH, '//*[@id="divStatus"]/div/div[2]/button').click() 
    
    navegador.find_element(By.XPATH, '//*[@id="selTipoFinalizacao"]').click()
    navegador.find_element(By.XPATH, '//*[@id="selTipoFinalizacao"]/option[4]').click()
    
    time.sleep(1)
    aguardar_toast_fechar(navegador) 

    # Regras de Calendário
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="dtInicial"]')
    mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
    ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text
    print(f'Mês calendário do site: {mes_x}')
    print(f'Mês final que o código quer buscar: {alvo_pt} / {alvo_ingles}')

    while True:
        if mes_x in [alvo_pt, alvo_ingles] and anoatual == int(ano_x):
            print("📅 Atingimos o mês inicial desejado.")
            break
        
        # Em vez de tentar de cara (o que pode dar Null/None na renderização rápida do site)
        # Passaremos a usar nosso botão inteligente que aguarda até aparecer:
        clicar_com_seguranca(navegador, By.XPATH, '//*[@id="ui-datepicker-div"]/div/a[2]/span', timeout=5)
        
        mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
        ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text
    
    
    navegador.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]//a[text()="1"]').click()

    navegador.find_element(By.XPATH, '//*[@id="dtFinal"]').click()
    mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
    ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    while True:
        if mes_x in [alvo_pt, alvo_ingles] and anoatual == int(ano_x):
            break
            
        clicar_com_seguranca(navegador, By.XPATH, '//*[@id="ui-datepicker-div"]/div/a[2]/span', timeout=5)
        
        mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
        ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    dias_elementos = navegador.find_elements(By.XPATH, '//*[@id="ui-datepicker-div"]//a[contains(@class,"ui-state-default")]')
    datas = [int(dia.text.strip()) for dia in dias_elementos if dia.text.strip().isdigit()]
    maiordata = max(datas)
    for dia in dias_elementos:
        if dia.text.strip() == str(maiordata):
            dia.click()

    # Download
    navegador.find_element(By.XPATH, '//*[@id="btnGerarOpcoes"]/i').click()
    aguardar_toast_fechar(navegador)
    navegador.find_element(By.XPATH, '//*[@id="frmRelatorio"]/div[2]/div/ul/li[1]/a').click()

    try:
         WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.ID, "btnFecharEmbedInteracao"))).click()
    except Exception:
         pass

    time.sleep(15)
    encontrado = False

    while True:
        navegador.refresh()
        WebDriverWait(navegador, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//*[@id='tbRelatoriosOperador']/tbody")))
        
        tr = navegador.find_elements(By.XPATH, "//*[@id='tbRelatoriosOperador']/tbody/tr")
        encontrado = False

        for i in tr:
            try:
                status = i.find_element(By.XPATH, "./td[2]").text.strip()
                if status.lower() == "processado":
                    botao_baixar = i.find_element(By.XPATH, "./td[3]//button")
                    botao_baixar.click()
                    encontrado = True
                    break 
            except Exception:
                continue

        if encontrado:
            break
        time.sleep(10)

    # Espera até o arquivo do Chrome 'crdownload' sumir da pasta finalizando o DL local
    downloads = os.path.expanduser(r"~\Downloads")
    documento = "Relatório de Pagamentos.xlsx"

    while True:
        arquivos = os.listdir(downloads)
        if any(arquivo.startswith(documento) and not arquivo.endswith(".crdownload") for arquivo in arquivos):
            print(f"O arquivo {documento} foi baixado com sucesso.")
            break
        time.sleep(2)
        
    navegador.quit() 
    
    # Retornamos as variaveis necessarias para a proxima etapa de gestao de arquivos
    if data.weekday() in [0, 1]:  # Segunda ou Terça
        dias_retroceder = 4
    else:
        dias_retroceder = 2
        
    diaatual = (data - timedelta(days=dias_retroceder)).day
    
    info_arquivo = {
        "nome_baixado": documento,
        "diretorio_origem": downloads,
        "mesnum": mesnum,
        "mesabrev": mesabrev,
        "anoatual": anoatual,
        "diaatual": diaatual
    }
    return info_arquivo


def mover_arquivo_para_raw(info_arquivo):
    """
    Módulo gestor de sistema de arquivos responsável apenas por capturar o arquivo
    já baixado na etapa anterior, e enviar para a pasta `data/raw/` de forma organizada.
    """
    print("Iniciando organização e transferência de arquivo para raw...")
    
    # Desempacota dicionario retornado pelo scraper
    origem = info_arquivo["diretorio_origem"]
    nome_padrao = info_arquivo["nome_baixado"]
    mesnum = info_arquivo["mesnum"]
    mesabrev = info_arquivo["mesabrev"]
    diaatual = info_arquivo["diaatual"]
    anoatual = info_arquivo["anoatual"]
    
    # novolocal = os.path.join(os.getcwd(), "data", "raw")
    novolocal = os.path.join(r"C:\Users\T9\Desktop\all\SEMEAR\Recebimento semear\pgto boleto", str(anoatual), f"{mesnum}. {mesabrev}")
    os.makedirs(novolocal, exist_ok=True) 

    novonome = f"{mesnum}. Recebimento boleto {mesabrev} {diaatual} {anoatual}.xlsx"
    caminhoantigo = os.path.join(origem, nome_padrao)
    caminhonovo = os.path.join(novolocal, novonome)

    # Verifica se a pasta RAW já tem esse arquivo por algum DL do mesmo dia, e substitui.
    if os.path.exists(caminhoantigo):
        if os.path.exists(caminhonovo):
            os.remove(caminhonovo)
            
        shutil.move(caminhoantigo, caminhonovo)
        print(f"✅ Arquivo movido e isolado com sucesso para DADOS BRUTOS (data/raw/): {caminhonovo}")
        return caminhonovo
    else:
        print("❌ Arquivo não foi encontrado no diretorio root de downloads.")
        return None

if __name__ == "__main__": #metodo teste no terminal rode python -m src.services.scraper_service
    # Testando módulo individualmente
    print("Testando o scraper sozinho...")
    download_file = baixar_relatorio_portal()
    print("Retorno:", download_file)


    
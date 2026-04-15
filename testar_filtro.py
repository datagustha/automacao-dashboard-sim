from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import time
import os

load_dotenv()

# Limpar pasta de downloads antes de começar
pasta_downloads = r"C:\Users\T9\Desktop\projetos\python\1. pagamentos-auto\semear\data\downloads"
for arquivo in os.listdir(pasta_downloads):
    if arquivo.endswith(".xlsx"):
        os.remove(os.path.join(pasta_downloads, arquivo))
print("✅ Pasta de downloads limpa")

driver = webdriver.Chrome()
driver.maximize_window()

# 1. LOGIN
print("\n[1] Fazendo login...")
driver.get('https://login.cobmais.com.br/')
time.sleep(2)
driver.find_element(By.XPATH, '//*[@id="Username"]').send_keys(os.getenv('PORTAL_USER'))
driver.find_element(By.XPATH, '//*[@id="Password"]').send_keys(os.getenv('PORTAL_PASS'))
driver.find_element(By.XPATH, '//*[@id="Login"]').click()
print("  ✅ Login clicado")
time.sleep(5)

# 2. FECHAR POPUP
print("\n[2] Fechando popup...")
try:
    popup = driver.find_element(By.XPATH, '//*[@id="pushActionRefuse"]')
    popup.click()
    print("  ✅ Popup fechado")
    time.sleep(2)
except:
    print("  ⚠️ Sem popup")
    time.sleep(2)

# 3. NAVEGAR ATÉ RELATÓRIO DE PAGAMENTOS
print("\n[3] Navegando para Relatório de Pagamentos...")
driver.find_element(By.XPATH, '//*[@id="menusuperior"]/a').click()
print("  ✅ Menu superior")
time.sleep(2)

driver.find_element(By.XPATH, '//*[@id="lkbRelatorios"]').click()
print("  ✅ Relatórios")
time.sleep(2)

driver.find_element(By.XPATH, "//span[@class='nav-item-text' and text()='Financeiro']").click()
print("  ✅ Financeiro")
time.sleep(2)

driver.find_element(By.XPATH, "//span[@class='nav-item-text' and text()='Pagamentos']").click()
print("  ✅ Pagamentos")
time.sleep(3)

# 4. TIPO ANALÍTICO
print("\n[4] Selecionando Tipo Analítico...")
analitico = driver.find_element(By.XPATH, "//label[@for='rbTipoAnalitico']")
analitico.click()
print("  ✅ Tipo Analítico selecionado")
time.sleep(2)

# 5. SELECIONAR BANCO AGORACRED
print("\n[5] Selecionando banco Agoracred Financeira...")
botao_todos = driver.find_element(By.XPATH, "//button[contains(text(), 'TODOS')]")
botao_todos.click()
print("  ✅ Dropdown aberto")
time.sleep(2)

# Desmarcar todos
selecionar_todos = driver.find_element(By.XPATH, "//label[contains(text(), 'Selecionar Todos')]")
selecionar_todos.click()
print("  ✅ Todos desmarcados")
time.sleep(1)

# Selecionar Agoracred
agoracred = driver.find_element(By.XPATH, "//label[contains(text(), 'Agoracred Financeira')]")
agoracred.click()
print("  ✅ Agoracred selecionado")
time.sleep(1)

# Fechar dropdown
botao_todos.click()
print("  ✅ Dropdown fechado")
time.sleep(2)

# 6. SELECIONAR PERÍODO
print("\n[6] Selecionando período...")
# Data Inicial - dia 1
driver.find_element(By.XPATH, '//*[@id="dtInicial"]').click()
print("  ✅ Clicou na data inicial")
time.sleep(2)

dia1 = driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]//a[text()="1"]')
dia1.click()
print("  ✅ Dia 1 selecionado")
time.sleep(2)

# Data Final - último dia
driver.find_element(By.XPATH, '//*[@id="dtFinal"]').click()
print("  ✅ Clicou na data final")
time.sleep(2)

dias = driver.find_elements(By.XPATH, '//*[@id="ui-datepicker-div"]//a[contains(@class,"ui-state-default")]')
ultimo_dia = 30
for dia in dias:
    if dia.text.isdigit() and int(dia.text) > ultimo_dia:
        ultimo_dia = int(dia.text)

driver.find_element(By.XPATH, f'//*[@id="ui-datepicker-div"]//a[text()="{ultimo_dia}"]').click()
print(f"  ✅ Último dia {ultimo_dia} selecionado")
time.sleep(2)

# 7. GERAR RELATÓRIO
print("\n[7] Gerando relatório...")
driver.find_element(By.XPATH, '//*[@id="btnGerarOpcoes"]/i').click()
print("  ✅ Botão Gerar clicado")
time.sleep(3)

driver.find_element(By.XPATH, '//*[@id="frmRelatorio"]/div[2]/div/ul/li[1]/a').click()
print("  ✅ Opção Gerar Relatório clicada")
time.sleep(2)

# 8. FECHAR POPUP DE INTERAÇÃO (se existir)
try:
    fechar = driver.find_element(By.ID, "btnFecharEmbedInteracao")
    fechar.click()
    print("  ✅ Popup de interação fechado")
    time.sleep(1)
except:
    pass

# 9. AGUARDAR DOWNLOAD (COM VERIFICAÇÃO)
print("\n[8] Aguardando download...")
tempo_maximo = 60  # 60 segundos
tempo_inicial = time.time()

while True:
    arquivos = os.listdir(pasta_downloads)
    
    # Verifica se há arquivo .crdownload (ainda baixando)
    baixando = any(a.endswith(".crdownload") for a in arquivos)
    
    # Verifica se há arquivo .xlsx já completo
    completo = any(a.endswith(".xlsx") for a in arquivos)
    
    if completo and not baixando:
        print("  ✅ Download completo!")
        break
    
    if time.time() - tempo_inicial > tempo_maximo:
        print("  ⚠️ Tempo limite excedido!")
        break
    
    print("  ⏳ Aguardando...")
    time.sleep(5)

# Verificar arquivos baixados
print(f"\n📁 Arquivos na pasta de downloads:")
for arquivo in os.listdir(pasta_downloads):
    if arquivo.endswith(".xlsx"):
        print(f"   ✅ {arquivo}")
    elif arquivo.endswith(".crdownload"):
        print(f"   ⏳ {arquivo} (ainda baixando)")

input("\nPressione ENTER para fechar o navegador...")
driver.quit()
"""
scraper_tma_service.py
Baixa o relatório "Acionamento por Operadores" (TMA) do portal Cobmais.
Roda em ambiente headless (sem interface gráfica) — compatível com VPS Linux.

Estrutura de destino:
    data/storage/<banco>/tma/<ano>/<mesnum>. <mesabrev>/
    Ex: data/storage/semear/tma/2026/7. Jul/

Estrutura geral do storage:
    data/storage/<banco>/recebimento/<ano>/  ← relatórios de pagamento
    data/storage/<banco>/tma/<ano>/          ← relatórios de TMA
"""

import os
import shutil
import time
import pathlib
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager

from src.utils.web_utils import clicar_com_seguranca, aguardar_toast_fechar, passar_mouse_sobre_elemento

load_dotenv()

# Raiz do projeto (3 níveis acima de src/services/)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


# ─────────────────────────────────────────────────────────────────────────────
# 1. INICIALIZAÇÃO DO NAVEGADOR
# ─────────────────────────────────────────────────────────────────────────────

def _criar_navegador_headless(pasta_downloads: str = None):
    """
    Cria e retorna um Chrome configurado para rodar em modo headless (sem janela).
    Necessário para ambientes Linux/VPS que não possuem servidor gráfico (X11/Wayland).

    Opções explicadas:
      --headless=new          → Modo headless moderno do Chrome (sem abrir janela).
                                'new' é mais estável que o legado '--headless' para downloads.
      --no-sandbox            → Desativa a sandbox de segurança do Chrome.
                                Obrigatório em containers/VPS onde o usuário não tem
                                privilégios suficientes para a sandbox funcionar.
      --disable-dev-shm-usage → Em Linux, o Chrome usa /dev/shm (memória compartilhada)
                                para renderização. Em VPS com pouca RAM, isso causa crash.
                                Esta opção força o uso do disco em vez da shm.
      --disable-gpu           → Desativa aceleração de hardware. Sem placa de vídeo
                                (ou drivers), o Chrome trava sem este flag.
      --window-size=1920,1080 → Define resolução virtual. Necessário em headless para
                                que elementos do DOM sejam renderizados com layout correto.
                                Sem isso, menus e dropdowns podem não aparecer.
      --remote-debugging-port → Habilita protocolo de debug. Útil para diagnosticar
                                problemas sem precisar de interface gráfica.

    download.default_directory → Diz ao Chrome onde salvar arquivos baixados
                                  automaticamente, sem perguntar ao usuário.

    Retorna:
        Tupla (navegador, pasta_downloads) — mesmo padrão do scraper_service.py.
    """
    opcoes = Options()

    # Localização do Chrome instalado no sistema Linux
    opcoes.binary_location = "/usr/bin/google-chrome"

    # Flags essenciais para funcionar sem interface gráfica
    opcoes.add_argument("--headless=new")           # Sem janela
    opcoes.add_argument("--no-sandbox")             # Necessário em VPS/containers
    opcoes.add_argument("--disable-dev-shm-usage")  # Evita crash de memória em VPS
    opcoes.add_argument("--disable-gpu")            # Sem aceleração de hardware
    opcoes.add_argument("--window-size=1920,1080")  # Resolução virtual do layout
    opcoes.add_argument("--remote-debugging-port=9222")  # Porta de debug remoto

    # Pasta de downloads: cria se não existir
    if pasta_downloads is None:
        pasta_downloads = str(BASE_DIR / "data" / "downloads")

    os.makedirs(pasta_downloads, exist_ok=True)

    # Instrui o Chrome a salvar downloads nessa pasta sem abrir diálogo
    prefs = {"download.default_directory": pasta_downloads}
    opcoes.add_experimental_option("prefs", prefs)

    # webdriver-manager baixa e gerencia o chromedriver automaticamente,
    # garantindo que a versão do driver bata com a versão do Chrome instalado.
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opcoes), pasta_downloads


# ─────────────────────────────────────────────────────────────────────────────
# 2. AUTENTICAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def _fazer_login(navegador):
    """Realiza o login no portal Cobmais com as credenciais do .env."""
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

    # Aguarda o redirecionamento pós-login completar antes de continuar
    time.sleep(3)


# ─────────────────────────────────────────────────────────────────────────────
# 3. INTERAÇÃO COM O PORTAL
# ─────────────────────────────────────────────────────────────────────────────

def _fechar_popup(navegador):
    """Fecha o popup de notificações push que aparece ao entrar no portal."""
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


def _navegar_ate_relatorio_tma(navegador):
    """
    Navega pelo menu do portal até o relatório 'Acionamento por Operadores'.
    Caminho: Menu Superior → Relatórios → Operação → Acionamento por Operadores
    """
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="menusuperior"]/a')
    time.sleep(1)
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="lkbRelatorios"]')
    time.sleep(1)
    # Hover no menu 'Operação' para revelar o submenu
    passar_mouse_sobre_elemento(navegador, By.XPATH, "//span[@class='nav-item-text' and text()='Operação']")
    time.sleep(1)
    clicar_com_seguranca(navegador, By.XPATH, "//span[@class='nav-item-text' and text()='Acionamento por Operadores']")
    time.sleep(3)
    print("  ✅ Navegou até Acionamento por Operadores")


def _selecionar_periodo(navegador, alvo_pt: str, alvo_ingles: str, anoatual: int):
    """
    Seleciona o período do relatório: do dia 1 até o último dia do mês atual.
    O calendário do portal pode exibir nomes de mês em PT ou EN,
    por isso comparamos contra os dois idiomas.
    """
    # ── Data Inicial: dia 1 ────────────────────────────────────────────────
    clicar_com_seguranca(navegador, By.XPATH, '//*[@id="dtInicial"]')
    time.sleep(1)

    # Avança o calendário até chegar no mês/ano correto
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

    # ── Data Final: último dia do mês ──────────────────────────────────────
    navegador.find_element(By.XPATH, '//*[@id="dtFinal"]').click()
    time.sleep(1)

    mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
    ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text

    while not (mes_x in [alvo_pt, alvo_ingles] and anoatual == int(ano_x)):
        clicar_com_seguranca(navegador, By.XPATH, '//*[@id="ui-datepicker-div"]/div/a[2]/span', timeout=5)
        mes_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
        ano_x = navegador.find_element(By.CLASS_NAME, "ui-datepicker-year").text
        time.sleep(0.5)

    # Pega todos os dias visíveis e clica no maior (= último dia do mês)
    dias_elementos = navegador.find_elements(
        By.XPATH, '//*[@id="ui-datepicker-div"]//a[contains(@class,"ui-state-default")]'
    )
    datas = [int(dia.text.strip()) for dia in dias_elementos if dia.text.strip().isdigit()]
    maiordata = max(datas)
    navegador.find_element(By.XPATH, f'//*[@id="ui-datepicker-div"]//a[text()="{maiordata}"]').click()
    time.sleep(1)
    print(f"  ✅ Data final: dia {maiordata}")


def _configurar_filtros(navegador, label_banco: str):
    """
    Abre o dropdown de carteiras/bancos, desmarca todos e seleciona
    apenas o banco desejado (ex: 'BANCO SEMEAR').
    """
    # Abre o dropdown que lista todos os bancos disponíveis
    botao_todos = WebDriverWait(navegador, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'TODOS')]"))
    )
    botao_todos.click()
    time.sleep(1)
    print("  ✅ Dropdown de bancos aberto")

    # Desmarca a opção "Selecionar Todos" para limpar a seleção
    try:
        selecionar_todos = navegador.find_element(By.XPATH, "//label[contains(text(), 'Selecionar Todos')]")
        checkbox = selecionar_todos.find_element(By.XPATH, ".//input")
        if checkbox.is_selected():
            selecionar_todos.click()
            print("  ✅ Todos os bancos desmarcados")
        time.sleep(1)
    except Exception as e:
        print(f"  ⚠️ Erro ao desmarcar todos: {e}")

    # Clica no label do banco específico para selecioná-lo
    banco_elem = navegador.find_element(By.XPATH, f"//label[normalize-space()='{label_banco}']")
    banco_elem.click()
    print(f"  ✅ Banco selecionado: {label_banco}")
    time.sleep(1)

    # Fecha o dropdown clicando novamente no mesmo botão
    botao_todos.click()
    time.sleep(1)
    print("  ✅ Dropdown fechado")


# ─────────────────────────────────────────────────────────────────────────────
# 4. GERAÇÃO E DOWNLOAD DO RELATÓRIO
# ─────────────────────────────────────────────────────────────────────────────

def _gerar_e_aguardar_download(navegador, pasta_downloads: str):
    """
    Clica em Gerar Relatório, aguarda o servidor processar,
    detecta o status 'Processado' na tabela e clica em Visualizar para baixar.
    Retorna o caminho completo do arquivo .xlsx baixado.

    O portal gera o relatório de forma assíncrona:
      1. Clicamos em Gerar → o servidor enfileira o relatório
      2. Ficamos recarregando a página até o status mudar para 'Processado'
      3. Clicamos em Visualizar → o Chrome baixa o .xlsx automaticamente
      4. Aguardamos o download completar (sem .crdownload na pasta)
    """
    # 1. Solicitar geração do relatório
    print("  📥 Clicando em Gerar Relatório...")
    navegador.find_element(By.XPATH, '//*[@id="btnGerarOpcoes"]/i').click()
    aguardar_toast_fechar(navegador)
    time.sleep(2)

    navegador.find_element(By.XPATH, '//*[@id="frmRelatorio"]/div[2]/div/ul/li[1]/a').click()
    print("  📄 Relatório solicitado, aguardando processamento...")
    time.sleep(3)

    # 2. Fechar popup de confirmação de envio, se aparecer
    try:
        fechar = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.ID, "btnFecharEmbedInteracao"))
        )
        fechar.click()
        print("  ✅ Popup de processamento fechado")
        time.sleep(1)
    except Exception:
        pass  # Popup não apareceu, tudo bem

    # 3. Aguardar status 'Processado' na tabela de relatórios (máx. 5 min)
    tempo_maximo = 300
    tempo_inicial = time.time()

    while time.time() - tempo_inicial < tempo_maximo:
        # Recarrega para ver o estado mais recente da tabela
        navegador.refresh()
        time.sleep(2)

        # Aguarda a tabela de relatórios carregar
        try:
            WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.ID, "tbRelatoriosOperador"))
            )
        except Exception:
            continue

        # Lê o status da primeira linha (= relatório mais recente)
        try:
            primeira_linha = navegador.find_element(By.XPATH, "//*[@id='tbRelatoriosOperador']/tbody/tr[1]")
            status = primeira_linha.find_element(By.XPATH, "./td[2]").text.strip()

            print(f"  ⏳ Status do relatório: {status}")

            if status.lower() == "processado":
                btn_visualizar = primeira_linha.find_element(By.XPATH, "./td[3]//button")
                btn_visualizar.click()
                print("  ✅ Botão Visualizar clicado! Iniciando download...")
                time.sleep(3)
                break
        except Exception:
            print("  ⏳ Aguardando relatório aparecer na tabela...")

        time.sleep(5)
    else:
        raise Exception("❌ Timeout: relatório não ficou Processado após 5 minutos")

    # 4. Aguardar o arquivo .xlsx ser salvo na pasta (máx. 3 min)
    print("  ⏳ Aguardando download finalizar...")
    tempo_inicial = time.time()
    tempo_maximo_download = 180

    while time.time() - tempo_inicial < tempo_maximo_download:
        # .crdownload = arquivo ainda sendo baixado pelo Chrome
        arquivos_baixando = [f for f in os.listdir(pasta_downloads) if f.endswith(".crdownload")]
        arquivos_completos = [f for f in os.listdir(pasta_downloads) if f.endswith(".xlsx")]

        if arquivos_completos and not arquivos_baixando:
            # Pega o .xlsx mais recente (por data de modificação)
            arquivo = max(arquivos_completos, key=lambda f: os.path.getmtime(os.path.join(pasta_downloads, f)))
            caminho = os.path.join(pasta_downloads, arquivo)
            print(f"  ✅ Download concluído: {arquivo}")
            return caminho

        time.sleep(2)

    raise Exception(f"❌ Timeout: download não concluído após {tempo_maximo_download} segundos")


# ─────────────────────────────────────────────────────────────────────────────
# 5. ORGANIZAÇÃO DO ARQUIVO NO STORAGE
# ─────────────────────────────────────────────────────────────────────────────

def _mover_para_storage(caminho_origem: str, banco: str, anoatual: int, mesnum: int, mesabrev: str, diaatual: int) -> str:
    """
    Move o arquivo baixado para a estrutura de pastas do projeto:

        data/storage/<banco>/tma/<ano>/<mesnum>. <mesabrev>/

    Exemplo real:
        data/storage/semear/tma/2026/7. Jul/7. TMA Jul 8 2026.xlsx

    A subcategoria 'tma/' separa os arquivos de TMA dos de recebimento.
    A estrutura completa do storage fica organizada assim na VPS:
        recebimento → data/storage/semear/recebimento/2026/
        tma          → data/storage/semear/tma/2026/

    O arquivo existente do mesmo mês é SUBSTITUÍDO (não acumula),
    porque o relatório já vem acumulado do dia 1 até hoje.
    """
    destino = BASE_DIR / "data" / "storage" / banco / "tma" / str(anoatual) / f"{mesnum}. {mesabrev}"
    os.makedirs(destino, exist_ok=True)

    novo_nome = f"{mesnum}. TMA {mesabrev} {diaatual} {anoatual}.xlsx"
    caminho_destino = str(destino / novo_nome)

    # Remove versão anterior do mesmo mês antes de mover
    if os.path.exists(caminho_destino):
        os.remove(caminho_destino)

    shutil.move(caminho_origem, caminho_destino)
    print(f"  ✅ Arquivo movido para: {caminho_destino}")
    return caminho_destino


# ─────────────────────────────────────────────────────────────────────────────
# 6. ORQUESTRADOR PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def baixar_relatorio_tma():
    """
    Ponto de entrada: baixa o relatório de TMA para cada banco configurado.
    Cada banco roda em um navegador novo e isolado para evitar conflitos de sessão.

    Retorna um dict com os caminhos dos arquivos baixados e metadados de data,
    no mesmo formato que scraper_service.py retorna — compatível com main.py.
    """
    print("=" * 60)
    print("Iniciando Web Scraping — TMA (Acionamento por Operadores)")
    print("=" * 60)

    # Metadados de data reutilizados por todos os bancos
    data = datetime.now()
    mesnum   = data.month
    anoatual = data.year
    mesabrev = data.strftime("%b")   # Ex: "Jul"
    diaatual = data.day

    # O datepicker do portal pode exibir o mês em PT ou EN
    meses_en = ["january", "february", "march", "april", "may", "june",
                "july", "august", "september", "october", "november", "december"]
    meses_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    alvo_ingles = meses_en[mesnum - 1]
    alvo_pt     = meses_pt[mesnum - 1]

    resultados = {}

    # Adicione aqui os bancos que possuem o relatório de TMA
    bancos = [
        {"label": "BANCO SEMEAR", "chave": "semear"},
        {"label": "Agoracred Financeira", "chave": "agoracred"},  # habilitar se necessário
    ]

    for banco in bancos:
        print(f"\n{'─' * 40}")
        print(f"▶ Processando TMA: {banco['label']}")
        print(f"{'─' * 40}")

        # Pasta de downloads limpa antes de cada banco
        pasta_downloads = str(BASE_DIR / "data" / "downloads")
        for f in os.listdir(pasta_downloads):
            if f.endswith(".xlsx") or f.endswith(".crdownload"):
                os.remove(os.path.join(pasta_downloads, f))

        # Cria um navegador novo e isolado para este banco
        navegador, _ = _criar_navegador_headless(pasta_downloads)

        try:
            _fazer_login(navegador)
            _fechar_popup(navegador)
            _navegar_ate_relatorio_tma(navegador)
            _configurar_filtros(navegador, banco["label"])
            _selecionar_periodo(navegador, alvo_pt, alvo_ingles, anoatual)

            caminho_baixado = _gerar_e_aguardar_download(navegador, pasta_downloads)

            caminho_final = _mover_para_storage(
                caminho_baixado, banco["chave"], anoatual, mesnum, mesabrev, diaatual
            )

            resultados[banco["chave"]] = caminho_final
            print(f"  ✅ {banco['label']} — TMA processado com sucesso!")

        except Exception as e:
            print(f"  ❌ Erro no banco {banco['label']}: {e}")
            resultados[banco["chave"]] = None
        finally:
            navegador.quit()
            print(f"  ✅ Navegador fechado para {banco['label']}")
            time.sleep(3)  # Pausa entre bancos para liberar recursos

    print("\n" + "=" * 60)
    print("Scraping TMA finalizado!")
    print(f"Arquivos salvos: {resultados}")
    print("=" * 60)

    return {
        "arquivos": resultados,
        "mesnum":   mesnum,
        "mesabrev": mesabrev,
        "anoatual": anoatual,
        "diaatual": diaatual,
    }
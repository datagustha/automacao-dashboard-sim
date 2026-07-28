"""
Teste rapido de extracao da tabela do Secullum RH.
Verifica se textContent traz todos os dias corretamente.
"""
import sys, json, time, pathlib
sys.stdout.reconfigure(encoding="utf-8")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = "financeiro@simfacilita.com.br"
SENHA = "54321"

opts = Options()
opts.add_argument("--window-size=1920,1080")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=opts)

try:
    # --- LOGIN ---
    print("[1] Login...")
    driver.get("https://pontoweb.secullum.com.br/login")
    time.sleep(3)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "Email")))
    driver.find_element(By.ID, "Email").send_keys(EMAIL)
    driver.find_element(By.ID, "Senha").send_keys(SENHA)
    driver.find_element(By.ID, "login").click()
    print("    Aguardando autenticacao (15s)...")
    time.sleep(15)
    print(f"    URL: {driver.current_url}")

    # --- MENU RELATORIOS ---
    print("[2] Clicando em Relatorios...")
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "relatorios")))
    driver.find_element(By.ID, "relatorios").click()
    time.sleep(2)

    # --- SUBMENU CALCULOS ---
    print("[3] Clicando em Calculos...")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "calculos")))
    driver.find_element(By.ID, "calculos").click()
    time.sleep(5)

    # --- AGUARDA FUNCIONARIO CARREGAR ---
    print("[4] Aguardando nome do funcionario...")
    el_nome = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#react-select-3--value-item"))
    )
    WebDriverWait(driver, 10).until(lambda d: el_nome.text.strip() != "")
    nome = el_nome.text.strip()
    print(f"    Funcionario: {nome}")

    # --- EXTRAI TABELA COM textContent ---
    print("[5] Extraindo tabela com textContent...")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "tabela-calculos-wrapper"))
    )
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, ".tabela-calculos-wrapper tbody tr")) > 0
    )
    time.sleep(2)

    registros = driver.execute_script("""
        var linhas = document.querySelectorAll('.tabela-calculos-wrapper tbody tr');
        var resultado = [];
        for(var i=0; i<linhas.length; i++){
            var tds = linhas[i].querySelectorAll('td');
            if(tds.length < 10) continue;
            function txt(el){ return el ? el.textContent.trim() : ''; }
            var data = txt(tds[2]);
            if(!data) continue;
            resultado.push({
                data:     data,
                entrada1: txt(tds[3]),
                saida1:   txt(tds[4]),
                entrada2: txt(tds[5]),
                saida2:   txt(tds[6]),
                b_saldo:  txt(tds[17]),
                b_total:  txt(tds[18])
            });
        }
        return resultado;
    """)

    print(f"\n    RESULTADO: {len(registros)} registros encontrados!\n")
    for r in registros:
        print(f"    {r['data']:<30} | E1={r['entrada1']:<6} | S1={r['saida1']:<6} | B_saldo={r['b_saldo']}")

    # Salva JSON para conferencia
    DATA_DIR = pathlib.Path(__file__).parent / "data"
    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / "teste_extracao.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"funcionario": nome, "registros": registros}, f, ensure_ascii=False, indent=2)
    print(f"\n    JSON salvo em: {out}")

except Exception as e:
    import traceback
    print(f"\n[ERRO] {e}")
    traceback.print_exc()
finally:
    input("\n>>> ENTER para fechar o browser...")
    driver.quit()

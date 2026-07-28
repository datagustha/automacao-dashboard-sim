"""
Inspeciona a pagina AvisoExpirado do Secullum para saber como fechar.
"""
import sys, time
sys.stdout.reconfigure(encoding="utf-8")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pathlib

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
    print("    Aguardando redirecionamento (15s)...")
    time.sleep(15)

    url = driver.current_url
    titulo = driver.title
    print(f"    URL: {url}")
    print(f"    Titulo: {titulo}")

    # --- INSPECIONA A PAGINA ---
    print("\n[2] HTML dos botoes na pagina:")
    btns = driver.execute_script("""
        var btns = document.querySelectorAll('button, a, input[type=button], input[type=submit]');
        var r = [];
        for(var i=0; i<btns.length; i++){
            r.push({
                tag: btns[i].tagName,
                id: btns[i].id || '',
                cls: btns[i].className.substring(0,60),
                txt: (btns[i].innerText || btns[i].value || '').trim().substring(0,60),
                href: btns[i].getAttribute('href') || ''
            });
        }
        return r;
    """)
    for b in btns:
        print(f"    <{b['tag']}> id='{b['id']}' txt='{b['txt']}' href='{b['href']}' class='{b['cls']}'")

    print("\n[3] HTML da pagina (primeiros 3000 chars):")
    print(driver.page_source[:3000])

    # Salva HTML
    DATA_DIR = pathlib.Path(__file__).parent / "data"
    DATA_DIR.mkdir(exist_ok=True)
    with open(DATA_DIR / "aviso_expirado.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"\n    HTML completo salvo em: {DATA_DIR / 'aviso_expirado.html'}")

    driver.save_screenshot(str(DATA_DIR / "aviso_expirado.png"))
    print(f"    Screenshot salvo em: {DATA_DIR / 'aviso_expirado.png'}")

except Exception as e:
    import traceback
    print(f"\n[ERRO] {e}")
    traceback.print_exc()
finally:
    input("\n>>> ENTER para fechar o browser...")
    driver.quit()

"""
Script de diagnostico WINDOWS - roda o browser visivelmente
Salva screenshots e HTML para identificar os seletores corretos.
"""
import os, sys, json, time, pathlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Forca encoding UTF-8 no terminal Windows
sys.stdout.reconfigure(encoding="utf-8")

EMAIL  = "financeiro@simfacilita.com.br"
SENHA  = "54321"

DATA_DIR = pathlib.Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

opts = Options()
opts.add_argument("--window-size=1920,1080")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver  = webdriver.Chrome(service=service, options=opts)
driver.set_window_size(1920, 1080)

resultado = {}

try:
    # ============================================================
    # 1. LOGIN
    # ============================================================
    print("\n[1] Abrindo Secullum RH...")
    driver.get("https://www.secullum.com.br/pt/produtos/secullum-rh")
    time.sleep(4)
    print(f"    URL: {driver.current_url}")
    driver.save_screenshot(str(DATA_DIR / "step1_pagina_inicial.png"))

    print("[2] Procurando botao de acesso...")
    btn_encontrado = False
    textos_btn = ["Acessar Secullum RH", "Acessar", "Login", "Entrar", "Acesse agora"]
    for texto in textos_btn:
        try:
            btn = driver.find_element(By.XPATH, f"//a[contains(., '{texto}')]")
            href = btn.get_attribute("href")
            print(f"    [OK] Botao encontrado: '{texto}' -> {href}")
            btn.click()
            btn_encontrado = True
            time.sleep(3)
            break
        except Exception:
            pass

    if not btn_encontrado:
        print("    [AV] Botao nao encontrado, indo direto para pontoweb...")
        driver.get("https://pontoweb.secullum.com.br")
        time.sleep(3)

    driver.save_screenshot(str(DATA_DIR / "step2_apos_btn.png"))
    print(f"    URL atual: {driver.current_url}")

    # ============================================================
    # 2. PREENCHER LOGIN
    # ============================================================
    print("[3] Preenchendo credenciais...")
    time.sleep(2)

    for id_email in ["Email", "email", "usuario", "login", "user"]:
        try:
            campo = driver.find_element(By.ID, id_email)
            campo.clear()
            campo.send_keys(EMAIL)
            print(f"    [OK] Campo email: id='{id_email}'")
            break
        except Exception:
            pass

    for id_senha in ["Senha", "senha", "password", "Password"]:
        try:
            campo = driver.find_element(By.ID, id_senha)
            campo.clear()
            campo.send_keys(SENHA)
            print(f"    [OK] Campo senha: id='{id_senha}'")
            break
        except Exception:
            pass

    for id_btn in ["login", "Login", "btnLogin", "submit"]:
        try:
            btn_login = driver.find_element(By.ID, id_btn)
            btn_login.click()
            print(f"    [OK] Botao submit: id='{id_btn}'")
            break
        except Exception:
            pass

    print("    Aguardando autenticacao (15s)...")
    time.sleep(15)

    driver.save_screenshot(str(DATA_DIR / "step3_apos_login.png"))
    print(f"    URL apos login: {driver.current_url}")

    # ============================================================
    # 3. NAVEGAR PARA CALCULOS
    # ============================================================
    print("[4] Navegando para Calculos...")
    driver.get("https://pontoweb.secullum.com.br/#/calculos")
    time.sleep(8)

    driver.save_screenshot(str(DATA_DIR / "step4_calculos.png"))
    print(f"    URL: {driver.current_url}")
    print(f"    Titulo: {driver.title}")

    html_path = DATA_DIR / "step4_calculos.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"    HTML salvo em: {html_path}")

    # ============================================================
    # 4. SELETORES DO NOME DO FUNCIONARIO
    # ============================================================
    print("\n[5] Testando seletores NOME:")
    seletores_nome = [
        "#react-select-3--value-item",
        "#react-select-2--value-item",
        "#react-select-1--value-item",
        ".Select-value-label",
        ".Select-value",
        "[class*='value-item']",
        "[class*='value-label']",
        "[class*='SingleValue']",
        "[class*='single-value']",
        ".Select--single .Select-value-label",
    ]
    for sel in seletores_nome:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            txt = el.text.strip()
            resultado.setdefault("nome", []).append({"sel": sel, "txt": txt})
            print(f"    [OK] {sel:<45} -> '{txt}'")
        except Exception:
            print(f"    [--] {sel}")

    # HTML do Select
    try:
        sel_el = driver.find_element(By.CSS_SELECTOR, ".Select")
        html_sel = sel_el.get_attribute("outerHTML")
        print(f"\n    HTML .Select:\n{html_sel[:2000]}")
        resultado["html_select"] = html_sel
    except Exception:
        print("    .Select nao encontrado")

    # ============================================================
    # 5. TODOS OS BOTOES DA PAGINA
    # ============================================================
    print("\n[6] Todos os botoes da pagina:")
    try:
        btns = driver.execute_script("""
            var btns = document.querySelectorAll('button');
            var r = [];
            for(var i=0; i<btns.length; i++){
                r.push({
                    i: i,
                    text: btns[i].innerText.trim().substring(0,30),
                    title: btns[i].getAttribute('title') || '',
                    cls: btns[i].className.substring(0,60),
                    html: btns[i].outerHTML.substring(0,200)
                });
            }
            return r;
        """)
        resultado["botoes"] = btns
        for b in btns:
            print(f"    #{b['i']:02d} text='{b['text']}' title='{b['title']}' class='{b['cls']}'")
    except Exception as e:
        print(f"    Erro: {e}")

    # ============================================================
    # 6. SELETORES DO BOTAO AVANCAR
    # ============================================================
    print("\n[7] Testando seletores BOTAO AVANCAR:")
    seletores_avancar = [
        "i.fa-chevron-right", "i.fa-arrow-right", "i.fa-angle-right",
        "i.fa-caret-right", "i.fa-step-forward",
        "[class*='chevron-right']", "[class*='arrow-right']",
        "button[title*='ximo']", "button[title*='Next']", "button[title*='next']",
        "[aria-label*='next']",
    ]
    for sel in seletores_avancar:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            html = el.get_attribute("outerHTML")[:120]
            resultado.setdefault("avancar", []).append({"sel": sel, "html": html})
            print(f"    [OK] {sel:<45} -> {html}")
        except Exception:
            print(f"    [--] {sel}")

    # ============================================================
    # 7. TODOS OS INPUTS
    # ============================================================
    print("\n[8] Inputs na pagina:")
    try:
        inputs = driver.execute_script("""
            var els = document.querySelectorAll('input');
            var r = [];
            for(var i=0; i<els.length; i++){
                r.push(els[i].outerHTML.substring(0,200));
            }
            return r;
        """)
        for inp in inputs:
            print(f"    {inp}")
    except Exception as e:
        print(f"    Erro: {e}")

    # Salva JSON
    json_path = DATA_DIR / "diagnostico_secullum.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"\n[CONCLUIDO] JSON salvo em: {json_path}")
    print(f"[CONCLUIDO] Screenshots em: {DATA_DIR}")

except Exception as e:
    import traceback
    print(f"\n[ERRO] {e}")
    traceback.print_exc()
    try:
        driver.save_screenshot(str(DATA_DIR / "erro_diagnostico.png"))
    except Exception:
        pass
finally:
    input("\n>>> Pressione ENTER para fechar o browser...")
    driver.quit()

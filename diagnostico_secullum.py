#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE DIAGNOSTICO DO SECULLUM RH
Descobre os seletores corretos para: nome do funcionario e botao avancar.
Salva o resultado em data/diagnostico_secullum.json

COMO USAR NA VPS:
  xvfb-run -a python diagnostico_secullum.py
"""
import os
import json
import time
import pathlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

# ================================================================
# Configuracao do Chrome
# ================================================================
options = Options()
if os.path.exists("/usr/bin/google-chrome"):
    options.binary_location = "/usr/bin/google-chrome"
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

resultado = {
    "login_ok": False,
    "calculos_ok": False,
    "seletores_nome": {},
    "seletores_avancar": {},
    "seletores_periodo": {},
    "html_select_funcionario": "",
    "html_botoes_navegacao": "",
    "html_inputs_data": "",
    "url_apos_login": "",
    "url_apos_calculos": "",
    "titulo_pagina": "",
}

try:
    # ----------------------------------------------------------------
    # 1. LOGIN
    # ----------------------------------------------------------------
    print("\n[1/4] Fazendo login no Secullum RH...")
    driver.get("https://www.secullum.com.br/pt/produtos/secullum-rh#/cartao-ponto")
    time.sleep(3)

    btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Acessar Secullum RH')]"))
    )
    btn.click()
    time.sleep(2)

    email = os.getenv("EMAIL_SISTEMA")
    senha = os.getenv("SENHA_SISTEMA")
    print(f"    Email: {email}")

    driver.find_element(By.ID, "Email").send_keys(email)
    driver.find_element(By.ID, "Senha").send_keys(senha)
    driver.find_element(By.ID, "login").click()
    print("    Aguardando autenticacao...")

    # Aguarda redirecionar para pontoweb
    inicio = time.time()
    while time.time() - inicio < 20:
        url = driver.current_url
        if "pontoweb.secullum.com.br" in url or ("#/" in url and "secullum" in url):
            break
        time.sleep(1)

    time.sleep(3)
    resultado["url_apos_login"] = driver.current_url
    resultado["login_ok"] = True
    print(f"    ✅ Login OK! URL: {driver.current_url}")

    # Fecha modais
    try:
        driver.execute_script("""
            var el = document.getElementById('modal-portaria-671-ok');
            if(el) el.click();
        """)
        time.sleep(1)
    except Exception:
        pass

    # ----------------------------------------------------------------
    # 2. NAVEGAR PARA CALCULOS
    # ----------------------------------------------------------------
    print("\n[2/4] Navegando para Calculos...")
    driver.get("https://pontoweb.secullum.com.br/#/calculos")
    time.sleep(6)

    resultado["url_apos_calculos"] = driver.current_url
    resultado["titulo_pagina"] = driver.title

    # Verifica se carregou
    seletores_detecao = [
        "#react-select-3--value-item",
        "#react-select-2--value-item",
        ".Select-value-label",
        "#dataInicio",
        "#btnAtualizar",
        ".tabela-calculos-wrapper",
    ]
    for sel in seletores_detecao:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            resultado["calculos_ok"] = True
            print(f"    ✅ Tela de Calculos detectada via: {sel}")
            break
        except Exception:
            pass

    if not resultado["calculos_ok"]:
        print(f"    ❌ Tela de Calculos NAO carregou. URL: {driver.current_url}")

    # ----------------------------------------------------------------
    # 3. TESTAR SELETORES DE NOME DO FUNCIONARIO
    # ----------------------------------------------------------------
    print("\n[3/4] Testando seletores do nome do funcionario...")
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
        ".css-1uccc91-singleValue",
        ".Select--single .Select-value-label",
    ]
    for sel in seletores_nome:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            texto = el.text.strip()
            resultado["seletores_nome"][sel] = {"encontrado": True, "texto": texto}
            print(f"    ✅ {sel:<45} → '{texto}'")
        except Exception:
            resultado["seletores_nome"][sel] = {"encontrado": False, "texto": ""}
            print(f"    ❌ {sel:<45} → NÃO ENCONTRADO")

    # HTML do componente Select principal
    try:
        select_el = driver.find_element(By.CSS_SELECTOR, ".Select--single")
        resultado["html_select_funcionario"] = select_el.get_attribute("outerHTML")[:2000]
        print(f"\n    HTML do Select (primeiros 500 chars):\n    {resultado['html_select_funcionario'][:500]}")
    except Exception:
        try:
            select_el = driver.find_element(By.CSS_SELECTOR, ".Select")
            resultado["html_select_funcionario"] = select_el.get_attribute("outerHTML")[:2000]
            print(f"\n    HTML do Select (primeiros 500 chars):\n    {resultado['html_select_funcionario'][:500]}")
        except Exception:
            resultado["html_select_funcionario"] = "nao encontrado"

    # ----------------------------------------------------------------
    # 4. TESTAR SELETORES DO BOTAO AVANCAR
    # ----------------------------------------------------------------
    print("\n[4/4] Testando seletores do botao AVANCAR...")
    seletores_avancar = [
        "i.fa-chevron-right",
        "i.fa-arrow-right",
        "i.fa-angle-right",
        "i.fa-caret-right",
        "i.fa-step-forward",
        "[class*='chevron-right']",
        "[class*='arrow-right']",
        "[class*='angle-right']",
        "button[title*='ximo']",
        "button[title*='Next']",
        "button[title*='next']",
        "button[title*='Próximo']",
        "button[title*='Avancar']",
        ".btn-next",
        ".next-btn",
        "[aria-label*='next']",
        "[aria-label*='próximo']",
    ]

    for sel in seletores_avancar:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                for el in elems:
                    outerhtml = el.get_attribute("outerHTML")[:100]
                    resultado["seletores_avancar"][sel] = {"encontrado": True, "html": outerhtml}
                    print(f"    ✅ {sel:<45} → {outerhtml}")
            else:
                resultado["seletores_avancar"][sel] = {"encontrado": False, "html": ""}
                print(f"    ❌ {sel:<45} → NÃO ENCONTRADO")
        except Exception as e:
            resultado["seletores_avancar"][sel] = {"encontrado": False, "html": str(e)[:50]}
            print(f"    ❌ {sel:<45} → ERRO: {e}")

    # Tenta achar botões próximos ao Select via JS
    try:
        btns_info = driver.execute_script("""
            var btns = document.querySelectorAll('button');
            var info = [];
            for(var i=0; i<Math.min(btns.length, 20); i++){
                info.push({
                    index: i,
                    text: btns[i].innerText.trim(),
                    title: btns[i].getAttribute('title') || '',
                    class: btns[i].className,
                    html: btns[i].outerHTML.substring(0, 200)
                });
            }
            return info;
        """)
        print("\n    TODOS OS BOTOES NA PAGINA (primeiros 20):")
        for b in btns_info:
            resultado["html_botoes_navegacao"] += f"\n--- Botao #{b['index']} (title={b['title']}, txt={b['text']}) ---\n{b['html']}\n"
            print(f"    #{b['index']} title='{b['title']}' text='{b['text']}' class='{b['class'][:60]}'")
    except Exception as e:
        print(f"    Erro ao listar botoes: {e}")

    # Inputs de data
    try:
        inputs_data = driver.execute_script("""
            var inputs = document.querySelectorAll('input[type=text], input[type=date]');
            var info = [];
            for(var i=0; i<Math.min(inputs.length, 10); i++){
                info.push(inputs[i].outerHTML.substring(0, 200));
            }
            return info;
        """)
        resultado["html_inputs_data"] = "\n".join(inputs_data)
        print("\n    INPUTS DE DATA/TEXTO:")
        for inp in inputs_data:
            print(f"    {inp}")
    except Exception as e:
        print(f"    Erro ao listar inputs: {e}")

    # ----------------------------------------------------------------
    # SALVA RESULTADO
    # ----------------------------------------------------------------
    pasta_data = pathlib.Path(__file__).parent / "data"
    os.makedirs(pasta_data, exist_ok=True)
    caminho = pasta_data / "diagnostico_secullum.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"✅ Diagnostico salvo em: {caminho}")
    print(f"{'=' * 60}")

    # Imprime resumo dos que funcionaram
    print("\n📋 RESUMO - Seletores que FUNCIONARAM:")
    print("  NOME DO FUNCIONARIO:")
    for sel, info in resultado["seletores_nome"].items():
        if info["encontrado"]:
            print(f"    ✅ {sel} → '{info['texto']}'")
    print("  BOTAO AVANCAR:")
    for sel, info in resultado["seletores_avancar"].items():
        if info["encontrado"]:
            print(f"    ✅ {sel}")

except Exception as e:
    import traceback
    print(f"\n❌ ERRO GERAL: {e}")
    traceback.print_exc()
finally:
    driver.quit()

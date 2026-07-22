# -*- coding: utf-8 -*-
"""
SERVICO DE SCRAPING DE PONTO ELETRONICO (SECULLUM RH)
ABORDAGEM: Navegacao por setas (igual ao sistema original que funcionava).
"""
import os
import json
import time
import pathlib
import unicodedata
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from sqlalchemy.orm import Session
from src.config.database import engine
from src.models.LoginModel import analistas

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def _normalizar(texto):
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).upper().strip()


def calcular_data_alvo_d1(data_referencia=None):
    if data_referencia is None:
        data_referencia = datetime.now()
    d1 = data_referencia - timedelta(days=1)
    if d1.weekday() == 5:
        d1 -= timedelta(days=1)
    elif d1.weekday() == 6:
        d1 -= timedelta(days=2)
    return d1


def iniciar_navegador(headless=True):
    opts = Options()
    opts.binary_location = "/usr/bin/google-chrome"  # 👈 ADICIONA!
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    
    # 👇 USA WEBDRIVER-MANAGER!
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


def realizar_login_secullum(navegador):
    email = os.getenv("EMAIL_SISTEMA")
    senha = os.getenv("SENHA_SISTEMA")
    if not email or not senha:
        print("[ERRO] EMAIL_SISTEMA ou SENHA_SISTEMA nao encontrados no .env")
        return False
    try:
        print("[PONTO SCRAPER] Acessando Secullum RH...")
        navegador.get("https://www.secullum.com.br/pt/produtos/secullum-rh#/cartao-ponto")
        time.sleep(3)
        btn = WebDriverWait(navegador, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Acessar Secullum RH')]"))
        )
        btn.click()
        time.sleep(2)
        campo_email = WebDriverWait(navegador, 15).until(
            EC.presence_of_element_located((By.ID, "Email"))
        )
        campo_email.clear()
        campo_email.send_keys(email)
        campo_senha = navegador.find_element(By.ID, "Senha")
        campo_senha.clear()
        campo_senha.send_keys(senha)
        navegador.find_element(By.ID, "login").click()
        print("[PONTO SCRAPER] Login solicitado.")
        time.sleep(5)
        try:
            WebDriverWait(navegador, 5).until(
                EC.element_to_be_clickable((By.ID, "modal-portaria-671-ok"))
            ).click()
            print("[PONTO SCRAPER] Popup inicial fechado.")
        except TimeoutException:
            pass
        return True
    except Exception as e:
        print(f"[ERRO] Falha no login: {e}")
        return False


def navegar_para_calculos(navegador):
    """Navega diretamente para a tela de Cálculos via URL Hash do Secullum RH."""
    print("[PONTO SCRAPER] Navegando para Calculos (https://pontoweb.secullum.com.br/#/calculos)...")
    try:
        navegador.get("https://pontoweb.secullum.com.br/#/calculos")
        time.sleep(3)

        # Aguarda a presenca do campo dataInicio
        WebDriverWait(navegador, 15).until(
            EC.presence_of_element_located((By.ID, "dataInicio"))
        )
        print("[PONTO SCRAPER] Tela de Calculos carregada com sucesso!")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao acessar Calculos: {e}")
        # Tenta fallback via JavaScript
        try:
            navegador.execute_script("window.location.hash = '#/calculos';")
            time.sleep(4)
            WebDriverWait(navegador, 10).until(
                EC.presence_of_element_located((By.ID, "dataInicio"))
            )
            print("[PONTO SCRAPER] Tela de Calculos carregada via Hash JS!")
            return True
        except Exception as e2:
            print(f"[ERRO] Fallback hash falhou: {e2}")
            return False



def configurar_periodo_calculo(navegador, data_inicio_str, data_fim_str):
    try:
        time.sleep(3)

        # Fecha modais/popups via JS se existirem
        navegador.execute_script("""
            var btnNo = document.getElementById('btnNo');
            if (btnNo) btnNo.click();
            var modalBtns = document.querySelectorAll('.ReactModal__Overlay button');
            for(var i=0; i<modalBtns.length; i++){
                if(modalBtns[i].id === 'btnNo' || modalBtns[i].innerText.includes('Não') || modalBtns[i].innerText.includes('OK')){
                    modalBtns[i].click();
                }
            }
        """)
        time.sleep(1)

        # Define os valores de dataInicio e dataFim via JS + eventos
        navegador.execute_script("""
            var ids = ['dataInicio', 'dataFim'];
            var vals = [arguments[0], arguments[1]];
            for(var i=0; i<ids.length; i++){
                var el = document.getElementById(ids[i]);
                if(el){
                    el.value = vals[i];
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                }
            }
        """, data_inicio_str, data_fim_str)
        time.sleep(1)

        try:
            btn = WebDriverWait(navegador, 8).until(
                EC.element_to_be_clickable((By.ID, "btnAtualizar"))
            )
            navegador.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.5)
            btn.click()
        except Exception:
            navegador.execute_script("var b=document.getElementById('btnAtualizar'); if(b) b.click();")
        print(f"[PONTO SCRAPER] Periodo configurado: {data_inicio_str} a {data_fim_str}")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao configurar periodo: {e}")
        return False


def obter_nome_funcionario_atual(navegador):
    try:
        el = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.ID, "react-select-3--value-item"))
        )
        nome = el.text.strip()
        if nome:
            return nome
    except Exception:
        pass
    try:
        labels = navegador.find_elements(By.CSS_SELECTOR, ".Select-value-label")
        if labels:
            return labels[-1].text.strip()
    except Exception:
        pass
    return None


def avancar_funcionario(navegador):
    seletores = [
        "i.fa-arrow-right",
        "[class*='arrow-right']",
        "button[title*='ximo']",
        "button[title*='next']",
    ]
    for sel in seletores:
        try:
            elem = navegador.find_element(By.CSS_SELECTOR, sel)
            pai = elem.find_element(By.XPATH, "..") if elem.tag_name == "i" else elem
            pai.click()
            time.sleep(2)
            print("[PONTO SCRAPER] Avancando...")
            return True
        except Exception:
            continue
    try:
        clicou = navegador.execute_script("""
            var icons = document.querySelectorAll('i.fa-arrow-right');
            for(var i=0; i<icons.length; i++){
                var btn = icons[i].closest('button') || icons[i].parentElement;
                if(btn){ btn.click(); return true; }
            }
            return false;
        """)
        if clicou:
            time.sleep(2)
            print("[PONTO SCRAPER] Avancou via JavaScript.")
            return True
    except Exception:
        pass
    print("[PONTO SCRAPER] Nao encontrou botao de avancar.")
    return False


def extrair_tabela_funcionario(navegador):
    try:
        WebDriverWait(navegador, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tabela-calculos-wrapper"))
        )
        time.sleep(2)
        registros = navegador.execute_script("""
            var linhas = document.querySelectorAll('.tabela-calculos-wrapper tbody tr');
            var resultado = [];
            for(var i=0; i<linhas.length; i++){
                var tds = linhas[i].querySelectorAll('td');
                if(tds.length < 10) continue;
                var data = (tds[2] ? tds[2].innerText.trim() : '');
                if(!data) continue;
                resultado.push({
                    data:     data,
                    entrada1: (tds[3]  ? tds[3].innerText.trim()  : ''),
                    saida1:   (tds[4]  ? tds[4].innerText.trim()  : ''),
                    entrada2: (tds[5]  ? tds[5].innerText.trim()  : ''),
                    saida2:   (tds[6]  ? tds[6].innerText.trim()  : ''),
                    b_saldo:  (tds[17] ? tds[17].innerText.trim() : ''),
                    b_total:  (tds[18] ? tds[18].innerText.trim() : '')
                });
            }
            return resultado;
        """)
        for reg in registros:
            for k in reg:
                if k != "data":
                    v = reg[k]
                    if not v:
                        reg[k] = "-"
                    elif v.startswith("+"):
                        reg[k] = v[1:]
        return registros or []
    except Exception as e:
        print(f"[PONTO SCRAPER] Erro ao extrair tabela: {e}")
        return []


def obter_mapa_nome_login():
    mapa = {}
    try:
        with Session(engine) as session:
            usuarios = session.query(analistas).all()
            for u in usuarios:
                if u.nome_completo and u.loguin:
                    chave = _normalizar(u.nome_completo)
                    mapa[chave] = {
                        "login": u.loguin.strip(),
                        "nome_db": u.nome_completo.strip(),
                        "banco": (u.banco or "").strip()
                    }
        print(f"[PONTO SCRAPER] {len(mapa)} operadores carregados do banco d_analista.")
    except Exception as e:
        print(f"[ERRO] Falha ao carregar operadores do banco: {e}")
    return mapa


def encontrar_login_por_nome(nome_secullum, mapa_nome_login):
    nome_norm = _normalizar(nome_secullum)
    if nome_norm in mapa_nome_login:
        return mapa_nome_login[nome_norm]
    partes = nome_norm.split()
    if len(partes) >= 2:
        chave_curta = f"{partes[0]} {partes[-1]}"
        for chave_db, info in mapa_nome_login.items():
            partes_db = chave_db.split()
            if len(partes_db) >= 2:
                if f"{partes_db[0]} {partes_db[-1]}" == chave_curta:
                    return info
    for chave_db, info in mapa_nome_login.items():
        if nome_norm in chave_db or chave_db in nome_norm:
            return info
    return None


def executar_scraping_completo_ponto(headless=True, max_funcionarios=120):
    print("\n" + "=" * 60)
    print("[PONTO SCRAPER] INICIANDO SCRAPING (NAVEGACAO POR SETAS)")
    print("=" * 60)
    hoje = datetime.now()
    d1 = calcular_data_alvo_d1(hoje)
    data_inicio_mes = f"01/{hoje.month:02d}/{hoje.year}"
    data_fim_str = d1.strftime("%d/%m/%Y")
    data_d1_str = d1.strftime("%d/%m/%Y")
    print(f"[PONTO SCRAPER] Periodo: {data_inicio_mes} a {data_fim_str}")
    mapa_nome_login = obter_mapa_nome_login()
    pasta_data = pathlib.Path(__file__).parent.parent.parent / "data"
    os.makedirs(pasta_data, exist_ok=True)
    caminho_cache = pasta_data / "ponto_cache.json"
    cache = {
        "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_alvo_d1": data_d1_str,
        "funcionarios": {}
    }
    navegador = iniciar_navegador(headless=headless)
    try:
        if not realizar_login_secullum(navegador):
            print("[ERRO] Falha no login.")
            navegador.quit()
            return False
        if not navegar_para_calculos(navegador):
            print("[ERRO] Nao acessou Calculos.")
            navegador.quit()
            return False
        if not configurar_periodo_calculo(navegador, data_inicio_mes, data_fim_str):
            print("[ERRO] Falha ao configurar periodo.")
            navegador.quit()
            return False
        total_sucesso = 0
        total_sem_mapeamento = 0
        nomes_vistos = set()
        for tentativa in range(max_funcionarios):
            nome_secullum = obter_nome_funcionario_atual(navegador)
            if not nome_secullum:
                print(f"[PONTO SCRAPER] ({tentativa+1}) Nao leu o nome. Avancando...")
                avancar_funcionario(navegador)
                continue
            print(f"\n[PONTO SCRAPER] ({tentativa+1}) {nome_secullum}")
            if nome_secullum in nomes_vistos:
                print(f"[PONTO SCRAPER] Nome repetido. Fim da lista.")
                break
            nomes_vistos.add(nome_secullum)
            registros = extrair_tabela_funcionario(navegador)
            
            # Filtra para manter somente as datas pertencentes ao mês atual (01/MM/AAAA em diante)
            mes_atual_str = f"/{hoje.month:02d}/{hoje.year}"
            registros_mes_atual = [r for r in registros if mes_atual_str in r.get("data", "")]
            # Usa os registros filtrados do mês atual (se houver)
            registros_final = registros_mes_atual if registros_mes_atual else registros

            print(f"[PONTO SCRAPER] -> {len(registros_final)} registros do mes atual.")

            registro_d1 = None
            for reg in registros_final:
                if data_d1_str in reg.get("data", ""):
                    registro_d1 = reg
                    break
            if not registro_d1 and registros_final:
                registro_d1 = registros_final[-1]

            info_db = encontrar_login_por_nome(nome_secullum, mapa_nome_login)
            if info_db:
                login = info_db["login"]
                cache["funcionarios"][login.lower()] = {
                    "nome_secullum": nome_secullum,
                    "login": login,
                    "status": "ok",
                    "card_d1": registro_d1 or {
                        "data": data_d1_str,
                        "entrada1": "-", "saida1": "-",
                        "entrada2": "-", "saida2": "-",
                        "b_saldo": "00:00", "b_total": "00:00"
                    },
                    "historico_mes": registros_final
                }

                total_sucesso += 1
                print(f"[PONTO SCRAPER] [OK] -> {login} ({info_db['banco']})")
            else:
                chave = _normalizar(nome_secullum).replace(" ", "_")
                cache["funcionarios"][f"_sem_login_{chave}"] = {
                    "nome_secullum": nome_secullum,
                    "login": None,
                    "status": "sem_mapeamento",
                    "card_d1": registro_d1 or {
                        "data": data_d1_str,
                        "entrada1": "-", "saida1": "-",
                        "entrada2": "-", "saida2": "-",
                        "b_saldo": "-", "b_total": "-"
                    },
                    "historico_mes": registros
                }
                total_sem_mapeamento += 1
                print(f"[PONTO SCRAPER] [!] Sem mapeamento: '{nome_secullum}'")
            try:
                cache["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(caminho_cache, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            except Exception as e_save:
                print(f"[PONTO SCRAPER] Erro ao salvar cache: {e_save}")
            if not avancar_funcionario(navegador):
                print("[PONTO SCRAPER] Nao avancou. Encerrando.")
                break
        print(f"\n{'=' * 60}")
        print(f"[PONTO SCRAPER] CONCLUIDO! Mapeados: {total_sucesso} | Sem mapeamento: {total_sem_mapeamento}")
        print(f"[PONTO SCRAPER] Cache: {caminho_cache}")
        print(f"{'=' * 60}")
        navegador.quit()
        return True
    except Exception as e:
        print(f"[ERRO] Falha: {e}")
        import traceback
        traceback.print_exc()
        try:
            navegador.quit()
        except Exception:
            pass
        return False

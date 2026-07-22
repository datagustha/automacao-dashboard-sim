# -*- coding: utf-8 -*-
"""
SERVICO DE SCRAPING DE PONTO ELETRONICO (SECULLUM RH)
ABORDAGEM: Navegacao por setas e sincronizacao com a lista de funcionarios ATIVOS no banco.
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


def _formatar_data_registro(data_raw, ano_atual):
    if not data_raw:
        return ""
    txt = data_raw.strip()
    partes = txt.split()
    data_pt = partes[0]
    dia_sem = " - " + " ".join(partes[1:]) if len(partes) > 1 else ""
    
    if "/" in data_pt:
        bits = data_pt.split("/")
        if len(bits) == 2:
            data_pt = f"{bits[0].zfill(2)}/{bits[1].zfill(2)}/{ano_atual}"
        elif len(bits) == 3:
            data_pt = f"{bits[0].zfill(2)}/{bits[1].zfill(2)}/{bits[2]}"
            
    return f"{data_pt}{dia_sem}"


def calcular_data_alvo_d1(data_referencia=None):
    if data_referencia is None:
        data_referencia = datetime.now()
    d1 = data_referencia - timedelta(days=1)
    if d1.weekday() == 5:  # Sábado -> Sexta
        d1 -= timedelta(days=1)
    elif d1.weekday() == 6:  # Domingo -> Sexta
        d1 -= timedelta(days=2)
    return d1


def fechar_popups_secullum(navegador):
    try:
        navegador.execute_script("""
            var ids = ['modal-portaria-671-ok', 'btnNo', 'btnOk', 'btn-ok'];
            ids.forEach(function(id){
                var el = document.getElementById(id);
                if (el) el.click();
            });
            var btns = document.querySelectorAll('.ReactModal__Overlay button, .modal button');
            for(var i=0; i<btns.length; i++){
                var txt = (btns[i].innerText || '').toLowerCase();
                if(txt.includes('não') || txt.includes('ok') || txt.includes('fechar') || txt.includes('entendi')){
                    btns[i].click();
                }
            }
        """)
    except Exception:
        pass


def iniciar_navegador(headless=True):
    opts = Options()
    if os.path.exists("/usr/bin/google-chrome"):
        opts.binary_location = "/usr/bin/google-chrome"
        
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    
    try:
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)
    except Exception as e:
        print(f"[AVISO] ChromeDriverManager falhou: {e}. Inicializando Chrome padrao...")
        return webdriver.Chrome(options=opts)


def realizar_login_secullum(navegador):
    email = os.getenv("EMAIL_SISTEMA")
    senha = os.getenv("SENHA_SISTEMA")
    if not email or not senha:
        print("[ERRO] EMAIL_SISTEMA ou SENHA_SISTEMA nao encontrados no .env")
        return False
    try:
        # Vai direto para a pagina de login do pontoweb (evita a pagina de marketing
        # que pode nao carregar corretamente na VPS)
        print("[PONTO SCRAPER] Acessando pagina de login do Secullum RH...")
        navegador.get("https://pontoweb.secullum.com.br/login")
        time.sleep(3)

        # Pode redirecionar para autenticador.secullum.com.br
        campo_email = WebDriverWait(navegador, 15).until(
            EC.presence_of_element_located((By.ID, "Email"))
        )
        campo_email.clear()
        campo_email.send_keys(email)
        campo_senha = navegador.find_element(By.ID, "Senha")
        campo_senha.clear()
        campo_senha.send_keys(senha)
        navegador.find_element(By.ID, "login").click()
        print("[PONTO SCRAPER] Login solicitado. Aguardando autenticacao...")

        # Aguarda redirecionamento para pontoweb.secullum.com.br/#/home
        inicio_login = time.time()
        while time.time() - inicio_login < 25:
            url_curr = navegador.current_url
            if "pontoweb.secullum.com.br/#/" in url_curr:
                print(f"[PONTO SCRAPER] Login efetuado! URL: {url_curr}")
                break
            time.sleep(1)

        time.sleep(3)
        fechar_popups_secullum(navegador)
        return True
    except Exception as e:
        print(f"[ERRO] Falha no login: {e}")
        return False


def navegar_para_calculos(navegador):
    """Navega para Calculos clicando no menu Relatorios -> Calculos.
    IDs confirmados pelo DevTools:
      - Menu principal: id='relatorios'
      - Submenu: id='calculos'
    """
    print("[PONTO SCRAPER] Navegando para Calculos via menu Relatorios...")
    fechar_popups_secullum(navegador)
    time.sleep(2)

    # ----------------------------------------------------------------
    # 1. Clica no menu principal "Relatorios" (id='relatorios')
    # ----------------------------------------------------------------
    clicou_relatorios = False
    try:
        btn_rel = WebDriverWait(navegador, 15).until(
            EC.element_to_be_clickable((By.ID, "relatorios"))
        )
        btn_rel.click()
        print("[PONTO SCRAPER] Menu Relatorios clicado!")
        clicou_relatorios = True
        time.sleep(2)
    except Exception as e:
        print(f"[AVISO] Nao encontrou id='relatorios': {e}")
        # Fallback: tenta por href ou texto
        try:
            btn_rel = navegador.find_element(
                By.XPATH,
                "//a[contains(@href,'relatorio') or contains(.,'Relat')]"
            )
            btn_rel.click()
            clicou_relatorios = True
            time.sleep(2)
            print("[PONTO SCRAPER] Menu Relatorios clicado via XPath fallback!")
        except Exception:
            pass

    # ----------------------------------------------------------------
    # 2. Clica no submenu "Calculos" (id='calculos')
    # ----------------------------------------------------------------
    clicou_calculos = False
    try:
        btn_calc = WebDriverWait(navegador, 10).until(
            EC.element_to_be_clickable((By.ID, "calculos"))
        )
        btn_calc.click()
        print("[PONTO SCRAPER] Submenu Calculos clicado!")
        clicou_calculos = True
        time.sleep(3)
    except Exception as e:
        print(f"[AVISO] Nao encontrou id='calculos': {e}")
        # Fallback: tenta por href #/calculos ou texto
        try:
            btn_calc = navegador.find_element(
                By.XPATH,
                "//a[@href='#/calculos' or contains(.,'lculos')]"
            )
            btn_calc.click()
            clicou_calculos = True
            time.sleep(3)
            print("[PONTO SCRAPER] Submenu Calculos clicado via XPath fallback!")
        except Exception:
            pass

    # ----------------------------------------------------------------
    # 3. Se nao conseguiu via menu, tenta URL direta como ultimo recurso
    # ----------------------------------------------------------------
    if not clicou_calculos:
        print("[PONTO SCRAPER] Tentando URL direta como fallback...")
        try:
            navegador.get("https://pontoweb.secullum.com.br/#/calculos")
            time.sleep(4)
        except Exception:
            pass

    # ----------------------------------------------------------------
    # 4. Aguarda a tela de Calculos carregar (seletor do funcionario)
    # ----------------------------------------------------------------
    print("[PONTO SCRAPER] Aguardando tela de Calculos carregar...")
    fechar_popups_secullum(navegador)

    for seletor in [
        (By.CSS_SELECTOR, "#react-select-3--value-item"),
        (By.ID, "dataInicio"),
        (By.ID, "rightArrow"),
        (By.ID, "btnAtualizar"),
        (By.CSS_SELECTOR, ".tabela-calculos-wrapper"),
    ]:
        try:
            WebDriverWait(navegador, 15).until(
                EC.presence_of_element_located(seletor)
            )
            print(f"[PONTO SCRAPER] Tela de Calculos carregada! Elemento: {seletor}")
            return True
        except Exception:
            continue

    # Falha total — grava dump HTML para diagnostico
    print(f"[ERRO] Tela de Calculos nao carregou.")
    print(f"[DIAGNOSTICO] URL Atual: {navegador.current_url}")
    print(f"[DIAGNOSTICO] Titulo: {navegador.title}")
    try:
        pasta_data = pathlib.Path(__file__).parent.parent.parent / "data"
        os.makedirs(pasta_data, exist_ok=True)
        dump_path = pasta_data / "debug_secullum_error.html"
        with open(dump_path, "w", encoding="utf-8") as f:
            f.write(navegador.page_source)
        print(f"[DIAGNOSTICO] HTML salvo em: {dump_path}")
        print(f"[DIAGNOSTICO] HTML (primeiros 1000 chars):\n{navegador.page_source[:1000]}")
    except Exception as e_dump:
        print(f"[DIAGNOSTICO] Erro ao salvar dump: {e_dump}")

    return False


def configurar_periodo_calculo(navegador, data_inicio_str, data_fim_str):
    """Define o periodo de calculos. Inputs sao type=text com formato dd/MM/yyyy."""
    try:
        time.sleep(3)
        fechar_popups_secullum(navegador)
        time.sleep(1)

        # Inputs confirmados: id='dataInicio' e id='dataFim', type='text', formato dd/MM/yyyy
        navegador.execute_script("""
            var ids = ['dataInicio', 'dataFim'];
            var vals = [arguments[0], arguments[1]];
            for(var i=0; i<ids.length; i++){
                var el = document.getElementById(ids[i]);
                if(el){
                    el.value = vals[i];
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    el.dispatchEvent(new Event('blur',  {bubbles:true}));
                }
            }
        """, data_inicio_str, data_fim_str)
        time.sleep(1)

        # Botao confirmado: text='Atualizar', id='btnAtualizar' ou button.btn com texto Atualizar
        clicou = False
        try:
            btn = WebDriverWait(navegador, 8).until(
                EC.element_to_be_clickable((By.ID, "btnAtualizar"))
            )
            navegador.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.5)
            btn.click()
            clicou = True
        except Exception:
            pass

        if not clicou:
            # Fallback: botao com texto 'Atualizar'
            try:
                btn = navegador.find_element(By.XPATH,
                    "//button[normalize-space(text())='Atualizar' or contains(.,'Atualizar')]")
                btn.click()
                clicou = True
            except Exception:
                pass

        if not clicou:
            navegador.execute_script(
                "var b=document.getElementById('btnAtualizar'); if(b) b.click();")

        print(f"[PONTO SCRAPER] Periodo configurado: {data_inicio_str} a {data_fim_str}")
        time.sleep(5)
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao configurar periodo: {e}")
        return False


def obter_nome_funcionario_atual(navegador):
    """Le o nome do funcionario usando o seletor #react-select-3--value-item.
    Aguarda ate 20s pelo elemento e ate 10s pelo texto nao-vazio."""
    try:
        # 1. Aguarda o elemento existir na pagina
        el = WebDriverWait(navegador, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#react-select-3--value-item"))
        )
        # 2. Aguarda o texto estar preenchido (nao vazio)
        WebDriverWait(navegador, 10).until(
            lambda d: el.text.strip() != ""
        )
        time.sleep(0.5)  # pequena pausa para garantir estabilidade
        nome = el.text.strip()
        if nome:
            return nome
    except Exception as e:
        print(f"[PONTO SCRAPER] [DEBUG] Erro ao ler nome: {e}")
        # Salva HTML para diagnostico em caso de falha
        try:
            pasta_data = pathlib.Path(__file__).parent.parent.parent / "data"
            dump = pasta_data / "debug_nome.html"
            with open(dump, "w", encoding="utf-8") as f:
                f.write(navegador.page_source)
            print(f"[PONTO SCRAPER] [DEBUG] HTML salvo em: {dump}")
        except Exception:
            pass

    # Fallback: qualquer .Select-value-label com texto
    try:
        labels = navegador.find_elements(By.CSS_SELECTOR, ".Select-value-label")
        for label in labels:
            txt = label.text.strip()
            if txt and not txt.startswith("57734"):  # ignora o seletor de empresa
                return txt
    except Exception:
        pass

    return None


def avancar_funcionario(navegador):
    """Clica no botao avançar funcionario.
    ID exato confirmado pelo DevTools: id='rightArrow'
    """
    # 1. SELETOR EXATO por ID (confirmado pelo DevTools)
    try:
        btn = WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.ID, "rightArrow"))
        )
        btn.click()
        time.sleep(2)
        print("[PONTO SCRAPER] Avancou via #rightArrow!")
        return True
    except Exception:
        pass

    # 2. Por titulo exato (confirmado pelo DevTools)
    try:
        btn = navegador.find_element(By.CSS_SELECTOR,
            "button[title='Visualizar o funcionario posterior']")
        btn.click()
        time.sleep(2)
        print("[PONTO SCRAPER] Avancou via title='...posterior'!")
        return True
    except Exception:
        pass

    # 3. Ícone fa-arrow-right -> botao pai (confirmado no DevTools)
    try:
        icone = WebDriverWait(navegador, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "i.fa-arrow-right"))
        )
        botao = icone.find_element(By.XPATH, "./ancestor::button")
        botao.click()
        time.sleep(2)
        print("[PONTO SCRAPER] Avancou via i.fa-arrow-right ancestor!")
        return True
    except Exception:
        pass

    # 4. Fallback JS pelo ID ou title
    try:
        clicou = navegador.execute_script("""
            // Tenta pelo ID exato
            var btn = document.getElementById('rightArrow');
            if(btn){ btn.click(); return 'id:rightArrow'; }
            // Tenta pelo title
            var btns = document.querySelectorAll('button');
            for(var i=0; i<btns.length; i++){
                var t = btns[i].getAttribute('title') || '';
                if(t.indexOf('posterior') >= 0){ btns[i].click(); return 'title:posterior'; }
            }
            // Fallback: fa-arrow-right
            var icon = document.querySelector('i.fa-arrow-right');
            if(icon){
                var b = icon.closest('button') || icon.parentElement;
                if(b){ b.click(); return 'icon:fa-arrow-right'; }
            }
            return false;
        """)
        if clicou:
            time.sleep(2)
            print(f"[PONTO SCRAPER] Avancou via JS ({clicou}).")
            return True
    except Exception:
        pass

    # Diagnostico em caso de falha total
    try:
        btns_info = navegador.execute_script("""
            var btns = document.querySelectorAll('button');
            var r = [];
            for(var i=0; i<btns.length; i++){
                r.push(btns[i].id + ' | ' + (btns[i].getAttribute('title')||'') + ' | ' + btns[i].className);
            }
            return r;
        """)
        print("[PONTO SCRAPER] [DEBUG] Botoes na pagina:")
        for b in btns_info:
            print(f"  -> {b}")
    except Exception:
        pass

    print("[PONTO SCRAPER] Nao encontrou botao de avancar funcionario.")
    return False



def extrair_tabela_funcionario(navegador):
    """Extrai TODAS as linhas da tabela de calculos.
    Usa textContent (funciona em modo headless) e aguarda a tabela estar populada.
    """
    try:
        # Aguarda a tabela aparecer
        WebDriverWait(navegador, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tabela-calculos-wrapper"))
        )
        # Aguarda que o tbody tenha pelo menos 1 linha de dado real
        WebDriverWait(navegador, 10).until(
            lambda d: len(d.find_elements(
                By.CSS_SELECTOR, ".tabela-calculos-wrapper tbody tr"
            )) > 0
        )
        time.sleep(2)  # estabilizacao

        registros = navegador.execute_script("""
            var linhas = document.querySelectorAll('.tabela-calculos-wrapper tbody tr');
            var resultado = [];
            for(var i=0; i<linhas.length; i++){
                var tds = linhas[i].querySelectorAll('td');
                if(tds.length < 10) continue;
                // Usa textContent (funciona em headless, diferente de innerText)
                function txt(el){ return el ? el.textContent.trim() : ''; }
                var data = txt(tds[2]);
                if(!data) continue;
                resultado.push({
                    data:     data,
                    entrada1: txt(tds[3]),
                    saida1:   txt(tds[4]),
                    entrada2: txt(tds[5]),
                    saida2:   txt(tds[6]),
                    entrada3: txt(tds[7]),
                    saida3:   txt(tds[8]),
                    normais:  txt(tds[9]),
                    faltas:   txt(tds[10]),
                    b_saldo:  txt(tds[17]),
                    b_total:  txt(tds[18])
                });
            }
            return resultado;
        """)

        # Normaliza os campos
        for reg in registros:
            for k in reg:
                if k != "data":
                    v = reg[k]
                    if not v:
                        reg[k] = "-"
                    elif v.startswith("+"):
                        reg[k] = v[1:]

        print(f"[PONTO SCRAPER] Tabela extraida: {len(registros)} linhas.")
        return registros or []
    except Exception as e:
        print(f"[PONTO SCRAPER] Erro ao extrair tabela: {e}")
        return []


def obter_mapa_nome_login():
    mapa = {}
    logins_ativos = set()
    try:
        with Session(engine) as session:
            usuarios = session.query(analistas).all()
            for u in usuarios:
                ativid = _normalizar(u.atividade)
                # Filtra apenas funcionarios ATIVOS no banco d_analista
                if (ativid == "ATIVO" or "ATIVO" in ativid) and u.nome_completo and u.loguin:
                    chave = _normalizar(u.nome_completo)
                    login_clean = u.loguin.strip()
                    mapa[chave] = {
                        "login": login_clean,
                        "nome_db": u.nome_completo.strip(),
                        "banco": (u.banco or "").strip()
                    }
                    logins_ativos.add(login_clean.lower())
        print(f"[PONTO SCRAPER] {len(mapa)} funcionarios ATIVOS carregados do banco de dados.")
    except Exception as e:
        print(f"[ERRO] Falha ao carregar funcionarios ativos do banco: {e}")
    return mapa, logins_ativos


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


def executar_scraping_completo_ponto(headless=True, max_funcionarios=150):
    print("\n" + "=" * 60)
    print("[PONTO SCRAPER] INICIANDO SCRAPING DE PONTO (SECULLUM RH)")
    print("=" * 60)
    
    hoje = datetime.now()
    d1 = calcular_data_alvo_d1(hoje)
    data_inicio_mes = f"01/{hoje.month:02d}/{hoje.year}"
    data_fim_str = d1.strftime("%d/%m/%Y")
    data_d1_str = d1.strftime("%d/%m/%Y")
    
    print(f"[PONTO SCRAPER] Data Alvo (D-1): {data_d1_str}")
    print(f"[PONTO SCRAPER] Periodo do mes: {data_inicio_mes} ate {data_fim_str}")
    
    mapa_nome_login, logins_ativos = obter_mapa_nome_login()
    
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
            print("[ERRO] Falha no login Secullum.")
            navegador.quit()
            return False
            
        if not navegar_para_calculos(navegador):
            print("[ERRO] Nao acessou tela de Calculos.")
            navegador.quit()
            return False
            
        if not configurar_periodo_calculo(navegador, data_inicio_mes, data_fim_str):
            print("[ERRO] Falha ao configurar periodo no Secullum.")
            navegador.quit()
            return False
            
        total_sucesso = 0
        total_sem_mapeamento = 0
        nomes_vistos = set()
        tentativas_avancar_falhas = 0
        
        for tentativa in range(max_funcionarios):
            nome_secullum = obter_nome_funcionario_atual(navegador)
            
            if not nome_secullum:
                print(f"[PONTO SCRAPER] ({tentativa+1}) Nao leu o nome. Tentando avancar...")
                if not avancar_funcionario(navegador):
                    tentativas_avancar_falhas += 1
                else:
                    tentativas_avancar_falhas = 0
                    
                if tentativas_avancar_falhas >= 3:
                    print("[PONTO SCRAPER] Botao de avancar falhou 3 vezes consecutivas. Encerrando loop.")
                    break
                continue
                
            print(f"\n[PONTO SCRAPER] ({tentativa+1}) {nome_secullum}")
            
            if nome_secullum in nomes_vistos:
                print(f"[PONTO SCRAPER] Nome repetido ('{nome_secullum}'). Fim da lista de funcionarios no Secullum RH.")
                break
                
            nomes_vistos.add(nome_secullum)
            
            # Extrai os registros da tabela do Secullum
            registros = extrair_tabela_funcionario(navegador)

            # Formata datas e armazena TODOS os registros da folha
            # (o Secullum mostra a folha completa, nao apenas o mes atual)
            registros_final = []
            for reg in registros:
                reg["data"] = _formatar_data_registro(reg.get("data", ""), hoje.year)
                registros_final.append(reg)

            print(f"[PONTO SCRAPER] -> {len(registros_final)} registros na folha.")
            
            # Busca o card de D-1 (data_d1_str ex: 21/07/2026)
            registro_d1 = None
            for reg in registros_final:
                if data_d1_str in reg.get("data", ""):
                    registro_d1 = reg
                    break
                    
            if not registro_d1:
                registro_d1 = {
                    "data": f"{data_d1_str} - {d1.strftime('%a')}",
                    "entrada1": "-", "saida1": "-",
                    "entrada2": "-", "saida2": "-",
                    "b_saldo": "00:00", "b_total": "00:00"
                }
                
            # Mapeamento de login no banco de dados (funcionários ativos)
            info_db = encontrar_login_por_nome(nome_secullum, mapa_nome_login)
            if info_db:
                login = info_db["login"]
                cache["funcionarios"][login.lower()] = {
                    "nome_secullum": nome_secullum,
                    "login": login,
                    "status": "ok",
                    "card_d1": registro_d1,
                    "historico_mes": registros_final
                }
                total_sucesso += 1
                print(f"[PONTO SCRAPER] [OK] -> {login} ({info_db['banco']})")
            else:
                chave_sem = _normalizar(nome_secullum).replace(" ", "_")
                cache["funcionarios"][f"_sem_login_{chave_sem}"] = {
                    "nome_secullum": nome_secullum,
                    "login": None,
                    "status": "sem_mapeamento",
                    "card_d1": registro_d1,
                    "historico_mes": registros_final
                }
                total_sem_mapeamento += 1
                print(f"[PONTO SCRAPER] [!] Sem mapeamento no banco: '{nome_secullum}'")
                
            # Salva o cache incrementalmente a cada funcionário lido
            try:
                cache["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(caminho_cache, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            except Exception as e_save:
                print(f"[PONTO SCRAPER] Erro ao salvar cache: {e_save}")
                
            # Avança para o próximo funcionário
            nome_anterior = nome_secullum
            clicou_avancar = avancar_funcionario(navegador)
            
            if not clicou_avancar:
                tentativas_avancar_falhas += 1
                print(f"[PONTO SCRAPER] Nao encontrou botao de avancar (falha {tentativas_avancar_falhas}/3).")
            else:
                time.sleep(1.5)
                novo_nome = obter_nome_funcionario_atual(navegador)
                if novo_nome == nome_anterior:
                    tentativas_avancar_falhas += 1
                    print(f"[PONTO SCRAPER] Nome nao mudou apos avancar (falha {tentativas_avancar_falhas}/3).")
                else:
                    tentativas_avancar_falhas = 0
                    
            if tentativas_avancar_falhas >= 3:
                print("[PONTO SCRAPER] Botao de avancar nao funcionou por 3 tentativas consecutivas. Encerrando.")
                break
                
        print(f"\n{'=' * 60}")
        print(f"[PONTO SCRAPER] CONCLUIDO! Mapeados: {total_sucesso} | Sem mapeamento: {total_sem_mapeamento}")
        print(f"[PONTO SCRAPER] Cache salvo em: {caminho_cache}")
        print(f"{'=' * 60}")
        
        navegador.quit()
        return True
        
    except Exception as e:
        print(f"[ERRO] Falha geral no scraper: {e}")
        import traceback
        traceback.print_exc()
        try:
            navegador.quit()
        except Exception:
            pass
        return False


if __name__ == "__main__":
    executar_scraping_completo_ponto(headless=False)

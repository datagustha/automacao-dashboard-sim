from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Esta função de utilidade foi criada para isolar comportamentos repetitivos da web

def aguardar_toast_fechar(navegador, timeout=5):
    """
    Função para aguardar uma notificação saltitante (toast) desaparecer da tela.
    """
    try:
        # Espera até o elemento de ID 'toast-container' ficar invisível
        WebDriverWait(navegador, timeout).until(
            EC.invisibility_of_element_located((By.ID, "toast-container"))
        )
        print("✅ Toast fechado/invisível")
    except TimeoutException:
        # Se esgotar o tempo e o toast não foi achado, não há problema, seguimos em frente
        print("ℹ️ Toast não encontrado ou já estava invisível")
        
    try:
        # Tenta injetar um script no navegador via Javascript para forçar a UI a esconder o toast
        toast = navegador.find_element(By.ID, "toast-container")
        navegador.execute_script("arguments[0].style.display = 'none';", toast)
        print("✅ Toast removido via JavaScript")
    except Exception:
        # Passa reto se não achar para remover pelo script
        pass

def clicar_com_seguranca(navegador, by, value, timeout=10):
    """
    Função inteligente que tenta clicar num elemento e, se estiver bloqueado por outro (como um aviso),
    usa javascript pra forçar o clique na marra.
    """
    try:
        # Aguarda o elemento existir e estar apto a receber clique
        elemento = WebDriverWait(navegador, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        # Limpa toasts que possam atrapalhar
        aguardar_toast_fechar(navegador)
        
        # Faz o clique comum
        elemento.click()
        return True
    
    except ElementClickInterceptedException:
        # Cai aqui se o Selenium disser: "O elemento está sendo tampado por outro elemento visual"
        print(f"⚠️ Elemento interceptado, tentando forçar com JavaScript...")
        try:
            # Pega o elemento bruto de volta e esmaga o clique via script interno
            elemento = navegador.find_element(by, value)
            navegador.execute_script("arguments[0].click();", elemento)
            return True
        except Exception:
            print(f"❌ Falha ao clicar via JavaScript")
            return False
            
    except Exception as e:
        # Pega qualquer outro problema imprevisível
        print(f"❌ Erro ao clicar: {e}")
        return False

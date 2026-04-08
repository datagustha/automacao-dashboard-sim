"""
Script Principal (Orquestrador)
Este arquivo tem apenas UM propósito agora: puxar os pauzinhos e unir o Scraper, Processador e Banco de Dados.
É uma das práticas obrigatórias do seu Workflow manter o controle geral enxuto! 
"""

import locale
from locale import setlocale

# Configurações de hora inicial pra ter padrão Brasileiro e UTF-8
try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except Exception:
    locale.setlocale(locale.LC_TIME, "Pt_BR.UTF8") # Fallback comum de Windows


# Imports Absolutos dos nossos super-arquivos modulares (Arquitetura limpa)
# Aqui, não tem SQL ou lógica repetida de clicks do selenium, tudo isso ficou nas "caixinhas" adequadas.
from src.services.scraper_service import executar_coleta_portal
from src.analysis.data_processor import processar_arquivos_brutos
from src.services.db_service import enviar_para_banco

def main():
    print("=== INICIANDO FLUXO PAGAMENTOS AUTOMATIZADOS SEMEAR ===")
    
    # PASSO 1: Chamamos os Serviços Web
    # Executará todo o Selenium configurado na src/services/, e joga no /data/raw
    caminho_arquivo = executar_coleta_portal()
    if not caminho_arquivo:
        print("Scraper não baixou arquivo adequadamente.")
        return

    # PASSO 2: Chamamos os Serviços de Tratamento/Dados (Nossa "Análise de Dados")
    # Pega o arquivo de /data/raw, consome de ponta-a-ponta e o trata com Pandas, largando num DataFrame Limpo
    df_resultado = processar_arquivos_brutos()
    
    
    # PASSO 3: Enviamos para o Banco de Dados (ORM)
    # Pega a tabela 'df_resultado' estruturadinha e salva usando nosso Engine do SQLAlchemy!
    if df_resultado is not None and not df_resultado.empty:
        enviar_para_banco(df_resultado)
    else:
        print("Dataframe vazio na saída do processamento!")
        
    print("=== FINALIZADO O SCRIPT! ===")

if __name__ == "__main__":
    # Garante que ele só executa nossa máquina se chamarmos o semearProcesso explicitamente
    main()

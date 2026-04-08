"""
Ponto de Entrada Principal (Main)
Este arquivo tem apenas UM propósito agora: puxar os pauzinhos e unir os módulos.
Seguindo as regras de @/database, mantemos a visão arquitetural limpa: o 'main.py' orquestra 
enquanto os 'services' e 'analysis' fazem o trabalho duro.
"""

import locale
import sys
import os

diretorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(diretorio_raiz)

try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except Exception:
    locale.setlocale(locale.LC_TIME, "Pt_BR.UTF8")

from src.services.scraper_service import baixar_relatorio_portal, mover_arquivo_para_raw
from src.analysis.data_processor import processar_arquivos_brutos
from src.services.db_service import enviar_para_banco

def main():
    print("=== INICIANDO FLUXO PAGAMENTOS AUTOMATIZADOS SEMEAR ===")
    
    # PASSO 1: Acessar Site e Pegar Dados
    # Executará somente o navegador e fará o download local.
    info_arquivo = baixar_relatorio_portal()
    if not info_arquivo:
        print("❌ Falha na etapa de Web Scraping do Portal.")
        return

    # PASSO 2: Enviar Dado para a Pasta Certa (Raw)
    # Executa a separação das pastas isolando as regras do SO.
    caminho_arquivo_raw = mover_arquivo_para_raw(info_arquivo)
    if not caminho_arquivo_raw:
        print("❌ Scraper não processou o arquivo adequadamente para o modelo raw.")
        return

    # PASSO 3: Pegar DF - Tratamento e Limpeza (Análise com Pandas)
    # Consome de /data/raw e joga para /data/processed. Retorna o DF limpo!
    df_resultado = processar_arquivos_brutos(
        mesnum   = info_arquivo["mesnum"],
        anoatual = info_arquivo['anoatual'],
        mesabrev = info_arquivo["mesabrev"]
    )
    
    # PASSO 4: Enviar Dados (Banco de Dados Otimizado)
    # Injeta no seu MySQL usando ferramentas SQLAlchemy / Utils
    if df_resultado is not None and not df_resultado.empty:
        enviar_para_banco(df_resultado)
    else:
        print("⚠️ Dataframe vazio na saída do processamento! Nada salvar.")
        
    print("=== FLUXO PRINCIPAL FINALIZADO COM SUCESSO! ===")

if __name__ == "__main__":
    main()

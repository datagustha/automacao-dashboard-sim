"""
main.py — Orquestrador Principal
Segue o fluxo: Scraping → Storage → Processamento → Banco de Dados
para cada banco (Semear e Agoracred) de forma sequencial.
"""

import locale
import sys
import os
import pathlib

# Garante que o Python encontre os módulos src/
diretorio_raiz = pathlib.Path(__file__).resolve().parent
sys.path.append(str(diretorio_raiz))

# Carrega variáveis de ambiente do .env ANTES de qualquer import interno
from dotenv import load_dotenv
load_dotenv()

# Configuração de locale para nomes de mês em PT-BR
try:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
except Exception:
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
    except Exception:
        print("⚠️  Locale pt_BR não disponível. Nomes de mês podem vir em inglês.")

from src.services.scraper_service import baixar_relatorio_portal
from src.analysis.data_processor import processar_arquivo_banco
from src.services.db_service import enviar_para_banco_semear, enviar_para_banco_agoracred


def main():
    print("=" * 60)
    print("  FLUXO PAGAMENTOS AUTOMATIZADOS — SEMEAR + AGORACRED")
    print("=" * 60)

    # ── PASSO 1: Scraping ──────────────────────────────────────────────
    # Abre o navegador UMA vez, baixa ambos os relatórios, fecha o navegador.
    print("\n[PASSO 1] Iniciando Web Scraping do portal...")
    info = baixar_relatorio_portal()

    if not info or not info.get("arquivos"):
        print("❌ Falha na etapa de Web Scraping. Encerrando.")
        return

    # Metadados de data (compartilhados entre os bancos)
    mesnum   = info["mesnum"]
    mesabrev = info["mesabrev"]
    anoatual = info["anoatual"]
    arquivos = info["arquivos"]  # {"semear": "/path/...", "agoracred": "/path/..."}

    # ── PASSO 2: Processamento e Injeção por Banco ─────────────────────
    # Mapeamos cada banco para sua função de envio correspondente
    bancos_config = {
        "semear":    enviar_para_banco_semear,
        "agoracred": enviar_para_banco_agoracred,
    }

    for banco, enviar_func in bancos_config.items():
        print(f"\n{'=' * 60}")
        print(f"  BANCO: {banco.upper()}")
        print(f"{'=' * 60}")

        caminho_arquivo = arquivos.get(banco)
        if not caminho_arquivo:
            print(f"  ⚠️  Arquivo do {banco} não encontrado nos resultados do scraper. Pulando.")
            continue

        # PASSO 2a: Tratamento com Pandas
        print(f"\n[PASSO 2a] Processando dados — {banco.upper()}...")
        df = processar_arquivo_banco(
            caminho_arquivo=caminho_arquivo,
            banco=banco,
            anoatual=anoatual,
            mesnum=mesnum,
            mesabrev=mesabrev,
        )

        if df is None or df.empty:
            print(f"  ⚠️  DataFrame vazio após processamento de {banco}. Pulando injeção.")
            continue

        # PASSO 2b: Injeção no Banco de Dados
        print(f"\n[PASSO 2b] Enviando para o banco de dados — {banco.upper()}...")
        enviar_func(df)

    print("\n" + "=" * 60)
    print("  FLUXO FINALIZADO COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    main()

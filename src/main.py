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
from src.services.scraper_tma_service import baixar_relatorio_tma
from src.analysis.data_processor import processar_arquivo_banco, processar_arquivo_tma
from src.services.db_service import enviar_para_banco_semear, enviar_para_banco_agoracred


def main():
    print("=" * 60)
    print("  FLUXO PAGAMENTOS AUTOMATIZADOS — SEMEAR + AGORACRED")
    print("=" * 60)

    # ── PASSO 1: Scraping Recebimentos ─────────────────────────────────
    print("\n[PASSO 1] Iniciando Web Scraping de recebimentos...")
    try:
        info = baixar_relatorio_portal()
    except Exception as e:
        print(f"❌ Erro crítico no Web Scraping de recebimentos: {e}")
        info = None

    if info and info.get("arquivos"):
        mesnum   = info["mesnum"]
        mesabrev = info["mesabrev"]
        anoatual = info["anoatual"]
        arquivos = info["arquivos"]

        bancos_config = {
            "semear":    enviar_para_banco_semear,
            "agoracred": enviar_para_banco_agoracred,
        }

        for banco, enviar_func in bancos_config.items():
            print(f"\n{'=' * 60}")
            print(f"  BANCO: {banco.upper()} (RECEBIMENTOS)")
            print(f"{'=' * 60}")

            caminho_arquivo = arquivos.get(banco)
            if not caminho_arquivo:
                print(f"  ⚠️  Arquivo do {banco} não encontrado nos resultados do scraper. Pulando.")
                continue

            print(f"\n[PASSO 2a] Processando dados — {banco.upper()}...")
            try:
                df = processar_arquivo_banco(
                    caminho_arquivo=caminho_arquivo,
                    banco=banco,
                    anoatual=anoatual,
                    mesnum=mesnum,
                    mesabrev=mesabrev,
                )
                if df is not None and not df.empty:
                    print(f"\n[PASSO 2b] Enviando para o banco de dados — {banco.upper()}...")
                    enviar_func(df)
                else:
                    print(f"  ⚠️  DataFrame vazio após processamento de {banco}. Pulando injeção.")
            except Exception as e:
                print(f"❌ Erro ao processar/injetar recebimentos do banco {banco}: {e}")
    else:
        print("⚠️  Etapa de recebimentos pulada ou falhou.")

    # ── PASSO 3: Scraping TMA ──────────────────────────────────────────
    print("\n[PASSO 3] Iniciando Web Scraping de TMA...")
    try:
        info_tma = baixar_relatorio_tma()
    except Exception as e:
        print(f"❌ Erro crítico no Web Scraping de TMA: {e}")
        info_tma = None

    if info_tma and info_tma.get("arquivos"):
        mesnum_tma   = info_tma["mesnum"]
        mesabrev_tma = info_tma["mesabrev"]
        anoatual_tma = info_tma["anoatual"]
        arquivos_tma = info_tma["arquivos"]

        for banco, caminho_tma in arquivos_tma.items():
            if not caminho_tma:
                print(f"  ⚠️  Arquivo de TMA para {banco} não encontrado ou falhou. Pulando.")
                continue

            print(f"\n[PASSO 4] Processando TMA — {banco.upper()}...")
            try:
                processar_arquivo_tma(
                    caminho_arquivo=caminho_tma,
                    banco=banco,
                    anoatual=anoatual_tma,
                    mesnum=mesnum_tma,
                    mesabrev=mesabrev_tma,
                )
            except Exception as e:
                print(f"❌ Erro ao processar TMA do banco {banco}: {e}")
    else:
        print("⚠️  Etapa de TMA pulada ou falhou.")

    print("\n" + "=" * 60)
    print("  FLUXO FINALIZADO COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    main()

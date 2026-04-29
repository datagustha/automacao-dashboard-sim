"""
data_processor.py
Camada de análise: lê os arquivos brutos de cada banco (Semear e Agoracred),
aplica transformações com Pandas, e retorna os DataFrames prontos para o DB.

Paths relativos ao projeto — compatível com VPS Ubuntu e Windows.
"""

import os
import pathlib
import pandas as pd
import numpy as np

# Raiz do projeto (2 níveis acima de src/analysis/)
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


def _classificar_fase(atraso):
    """Encapsula a lógica de faixas de atraso em dias."""
    if pd.isna(atraso):       return "Fora da fase"
    if atraso >= 1800:        return "Fase 1801 a 9999"
    elif atraso >= 1440:      return "Fase 1441 a 1800"
    elif atraso >= 1080:      return "Fase 1081 a 1440"
    elif atraso >= 720:       return "Fase 721 a 1080"
    elif atraso >= 360:       return "Fase 361 a 720"
    elif atraso >= 240:       return "Fase 241 a 360"
    elif atraso >= 180:       return "Fase 181 a 240"
    elif atraso >= 120:       return "Fase 121 a 180"
    elif atraso >= 90:        return "Fase 91 a 120"
    elif atraso >= 60:        return "Fase 61 a 90"
    elif atraso >= 30:        return "Fase 31 a 60"
    elif atraso >= 10:        return "Fase 10 a 30"
    else:                     return "Fora da fase"


def _processar_arquivo(caminho_arquivo: str) -> pd.DataFrame | None:
    """
    Lê e transforma um único arquivo .xlsx do portal Cobmais.
    Retorna um DataFrame tratado, ou None em caso de falha.

    O layout do relatório é idêntico para Semear e Agoracred:
    - Cabeçalho inútil nas primeiras 29 linhas
    - Última linha é rodapé (descartada)
    """
    arquivo = os.path.basename(caminho_arquivo)
    print(f"  📄 Processando: {arquivo}")

    try:
        # 1. Leitura
        engine = "openpyxl" if caminho_arquivo.endswith(".xlsx") else "xlrd"
        df = pd.read_excel(caminho_arquivo, engine=engine)

        # 2. Remove cabeçalho inútil e rodapé
        df = df.iloc[29:-1].reset_index(drop=True)

        # 3. Promove primeira linha como header
        df.columns = df.iloc[0]
        df = df.drop(0).dropna(axis=1, how="all")

        # 4. Padroniza nomes de colunas
        df.columns = df.columns.astype(str).str.lower().str.replace(" ", "").str.replace(".", "")

        # Remove CPF/CNPJ (LGPD)
        if "cpf/cnpj" in df.columns:
            df = df.drop("cpf/cnpj", axis=1)

        # Renomeia para o padrão interno
        colunas_map = {
            "dtacordo":  "dtAcordo",
            "dtpgto":    "dtPgto",
            "vctoparc":  "vctoParc",
            "valorpgto": "valorTotal",
        }
        df = df.rename(columns=colunas_map)

        # 5. Garante que todas as colunas esperadas existam
        colunas_principais = [
            "cliente", "fase", "contrato", "dtAcordo", "dtPgto",
            "parcela", "plano", "vctoParc", "principal", "multa",
            "juros", "despesa", "operador", "valorTotal"
        ]

        faltantes = set(colunas_principais) - set(df.columns)
        if faltantes:
            print(f"  ⚠️  Colunas ausentes preenchidas com None: {faltantes}")
        for col in faltantes:
            df[col] = None

        df = df[colunas_principais].copy()

        # 6. Conversão de tipos
        for col in ["dtAcordo", "dtPgto", "vctoParc"]:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        df["filial"] = None  # Regra de negócio

        # 7. Cálculo de atrasos
        df["atraso"] = (df["dtPgto"] - df["vctoParc"]).dt.days

        maior_atraso = df.groupby("contrato")["atraso"].max().reset_index()
        maior_atraso = maior_atraso.rename(columns={"atraso": "maiorAtraso"})
        df = pd.merge(df, maior_atraso, on="contrato", how="left")

        df["faseAtraso"] = df["maiorAtraso"].apply(_classificar_fase)

        # 8. Limpeza final de tipos
        df["filial"] = df["filial"].replace(np.nan, None)
        df["parcela"] = df["parcela"].fillna(0).astype(int)
        df["plano"] = df["plano"].fillna(0).infer_objects(copy=False).astype(int)

        for col in ["principal", "multa", "juros", "despesa", "valorTotal"]:
            df[col] = df[col].astype(float)

        return df

    except Exception as e:
        print(f"  ❌ Erro ao processar {arquivo}: {e}")
        return None


def processar_arquivo_banco(caminho_arquivo: str, banco: str,
                            anoatual: int, mesnum: int, mesabrev: str) -> pd.DataFrame | None:
    """
    Processa o arquivo de um banco específico (semear ou agoracred).
    Salva um CSV de auditoria em data/processed/<banco>/<ano>/
    e retorna o DataFrame final.

    Args:
        caminho_arquivo: Caminho completo do .xlsx em data/storage/
        banco:           'semear' ou 'agoracred'
        anoatual:        Ano atual (int)
        mesnum:          Número do mês (int)
        mesabrev:        Abreviação do mês (str, ex: 'Apr')
    """
    print(f"\n{'─' * 50}")
    print(f"▶ Processando dados: {banco.upper()}")
    print(f"{'─' * 50}")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)

    df = _processar_arquivo(caminho_arquivo)

    if df is None or df.empty:
        print(f"  ❌ DataFrame vazio para {banco}. Nada a processar.")
        return None

    # Remove duplicatas
    df = df.drop_duplicates(
        subset=["contrato", "dtPgto", "parcela", "vctoParc", "operador"]
    )

    # Salva CSV de auditoria/debug em data/processed/
    pasta_output = BASE_DIR / "data" / "processed" / banco / str(anoatual)
    os.makedirs(pasta_output, exist_ok=True)
    caminho_csv = pasta_output / f"pagamentos_{banco}_{mesnum}_{mesabrev}_{anoatual}.csv"
    df.to_csv(caminho_csv, index=False)

    print(f"  ✅ Processamento concluído! Linhas: {len(df)}")
    print(f"  💾 CSV de auditoria salvo em: {caminho_csv}")

    return df

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
    print(f"\n{'-' * 50}")
    print(f">> Processando dados: {banco.upper()}")
    print(f"{'-' * 50}")

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


def _processar_arquivo_tma(caminho_arquivo: str) -> pd.DataFrame | None:
    """
    Lê e transforma um arquivo .xlsx de TMA (Acionamento por Operadores) do portal Cobmais.
    Localiza dinamicamente o cabeçalho 'Operador' e realiza a limpeza e padronização dos dados.
    """
    arquivo = os.path.basename(caminho_arquivo)
    print(f"  [TMA] Processando: {arquivo}")

    try:
        # 1. Leitura
        engine = "openpyxl" if caminho_arquivo.endswith(".xlsx") else "xlrd"
        df_raw = pd.read_excel(caminho_arquivo, engine=engine)

        # 2. Localiza a linha do cabeçalho que contém exatamente 'Operador'
        header_row_idx = None
        for idx, row in df_raw.iterrows():
            if row.astype(str).str.strip().eq('Operador').any():
                header_row_idx = idx
                break

        if header_row_idx is None:
            print(f"  [ERRO] Cabeçalho 'Operador' não localizado no arquivo {arquivo}")
            return None

        # 3. Corta o DataFrame a partir da linha de cabeçalho
        df = df_raw.iloc[header_row_idx:].copy()
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)

        # 4. Remove colunas vazias e limpa nomes de colunas
        df = df.loc[:, df.columns.notna()]
        df.columns = df.columns.astype(str).str.strip()

        # 5. Filtragem de linhas inválidas (linhas vazias ou totalizador geral)
        df = df.dropna(subset=['Operador'])
        df = df[~df['Operador'].astype(str).str.contains('Total|Geral', case=False, na=False)]

        # 6. Conversão de tipos e normalização de datas/números
        df['Primeiro Acionamento'] = pd.to_datetime(df['Primeiro Acionamento'], errors='coerce')
        df['Último Acionamento'] = pd.to_datetime(df['Último Acionamento'], errors='coerce')

        for col in ['Qtde Acionam.', 'Qtde Contratos', 'Qtde Clientes']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # Função auxiliar para converter "HH:MM:SS" em segundos
        def _hms_para_segundos(t_str):
            if pd.isna(t_str) or not isinstance(t_str, str):
                return 0
            try:
                partes = t_str.split(':')
                if len(partes) == 3:
                    return int(partes[0]) * 3600 + int(partes[1]) * 60 + int(partes[2])
                elif len(partes) == 2:
                    return int(partes[0]) * 60 + int(partes[1])
                return 0
            except:
                return 0

        df['Tempo Total Segundos'] = df['Tempo Total'].apply(_hms_para_segundos)
        df['Tempo Médio Segundos'] = df['Tempo Médio'].apply(_hms_para_segundos)

        # 7. Cálculo de métricas adicionais de performance para o Dashboard
        df['Taxa Acionamento/Cliente'] = (df['Qtde Acionam.'] / df['Qtde Clientes']).round(2)
        df['Taxa Acionamento/Cliente'] = df['Taxa Acionamento/Cliente'].replace([np.inf, -np.inf], 0).fillna(0)

        # Amplitude de atividade no dia (horas da janela de trabalho ativa)
        df['Amplitude Atividade (Horas)'] = ((df['Último Acionamento'] - df['Primeiro Acionamento']).dt.total_seconds() / 3600).round(2)
        df['Amplitude Atividade (Horas)'] = df['Amplitude Atividade (Horas)'].replace([np.inf, -np.inf], 0).fillna(0)

        # Ritmo de acionamentos por hora ativa
        df['Acionamentos por Hora Ativa'] = (df['Qtde Acionam.'] / df['Amplitude Atividade (Horas)']).round(2)
        df['Acionamentos por Hora Ativa'] = df['Acionamentos por Hora Ativa'].replace([np.inf, -np.inf], 0).fillna(0)

        # 8. Mapeia para colunas amigáveis (camelCase)
        colunas_map = {
            'Operador': 'operador',
            'Primeiro Acionamento': 'primeiroAcionamento',
            'Último Acionamento': 'ultimoAcionamento',
            'Qtde Acionam.': 'qtdeAcionamentos',
            'Qtde Contratos': 'qtdeContratos',
            'Qtde Clientes': 'qtdeClientes',
            'Tempo Total': 'tempoTotal',
            'Tempo Médio': 'tempoMedio',
            'Tempo Total Segundos': 'tempoTotalSegundos',
            'Tempo Médio Segundos': 'tempoMedioSegundos',
            'Taxa Acionamento/Cliente': 'taxaAcionamentoCliente',
            'Amplitude Atividade (Horas)': 'amplitudeAtividadeHoras',
            'Acionamentos por Hora Ativa': 'acionamentosPorHoraAtiva'
        }
        df = df.rename(columns=colunas_map)

        # Filtra apenas colunas mapeadas de interesse
        colunas_finais = list(colunas_map.values())
        df = df[colunas_finais].copy()

        return df

    except Exception as e:
        print(f"  [ERRO] Erro ao processar TMA {arquivo}: {e}")
        return None


def processar_arquivo_tma(caminho_arquivo: str, banco: str,
                          anoatual: int, mesnum: int, mesabrev: str) -> pd.DataFrame | None:
    """
    Processa o arquivo de TMA (Acionamento por Operadores) de um banco.
    Salva um CSV de auditoria em data/processed/<banco>/tma/<ano>/
    e retorna o DataFrame final.
    """
    print(f"\n{'-' * 50}")
    print(f">> Processando TMA: {banco.upper()}")
    print(f"{'-' * 50}")

    df = _processar_arquivo_tma(caminho_arquivo)

    if df is None or df.empty:
        print(f"  [ERRO] DataFrame de TMA vazio para {banco}. Nada a processar.")
        return None

    # Remove duplicatas baseadas no operador
    df = df.drop_duplicates(subset=["operador"])

    # Salva CSV de auditoria/debug
    pasta_output = BASE_DIR / "data" / "processed" / banco / "tma" / str(anoatual)
    os.makedirs(pasta_output, exist_ok=True)
    caminho_csv = pasta_output / f"tma_{banco}_{mesnum}_{mesabrev}_{anoatual}.csv"
    df.to_csv(caminho_csv, index=False)

    print(f"  [OK] Processamento de TMA concluído! Linhas: {len(df)}")
    print(f"  [SALVO] CSV de auditoria salvos em: {caminho_csv}")

    return df
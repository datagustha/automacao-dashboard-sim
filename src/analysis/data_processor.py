import os
import pandas as pd
import numpy as np


# A ideia dessa camada de Analysis é ler o arquivo Bruto, amassar com o Pandas (tratamento, conversões numéricas) 
# e jogar o final polido na pasta 'data/processed'.

def processar_arquivos_brutos(anoatual, mesnum, mesabrev):
    """
    Função que lê os arquivos da pasta 'data/raw/', executa transformações do pacote pandas, e
    cospe um Excel e um CSV finalizados para a pasta 'data/processed/'.
    Retorna o dataframe consolidado para enviarmos ao DB posteriormente.
    """

    
    print("Iniciando tratamento dos dados com Pandas...")
    
    # Configurações do Pandas para podermos dar "print(df)" no terminal sem cortar as colunas visualmente
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)

    # Definimos caminhos usando a nossa raiz base. Os ./data/raw garantem aderência à estrutura.
    pasta_input = os.path.join(r"C:\Users\T9\Desktop\all\SEMEAR\Recebimento semear\pgto boleto", str(anoatual), f"{mesnum}. {mesabrev}")
    pasta_output = os.path.join(r"C:\Users\T9\Desktop\all\SEMEAR\banco de dados\tabelas fato\pgto tratado", str(anoatual), "excel")
    os.makedirs(pasta_output, exist_ok=True) # Garantimos existência

    # Recupera todos os `.xls` e `.xlsx`
    arquivos = [f for f in os.listdir(pasta_input) if (f.endswith(".xlsx") or f.endswith(".xls")) and not f.startswith("~$")]
    
    if not arquivos:
        print("❌ Não existem dados nativos não-processados!")
        return None

    dataframes = []

    for arquivo in arquivos:
        caminho_completo = os.path.join(pasta_input, arquivo)
        try:
            print(f"Lendo e lapidando o {arquivo}...")

            # 1. Leitura
            # Usamos engine openpyxl para xlsx recentes
            df = pd.read_excel(caminho_completo, engine="openpyxl" if arquivo.endswith(".xlsx") else "xlrd")

            # 2. Exclusão de ruído inicial
            # O relatório Cobmais vem com cabeçalho inútil até a linha 29. Eliminamos da 29 pra baixo até -1 (última).
            df = df.iloc[29:-1].reset_index(drop=True)

            # 3. Transforma a primeria linha no real Header (Colunas)
            df.columns = df.iloc[0]
            df = df.drop(0) # Retira a linha que a gente acabou de usar de header
            df = df.dropna(axis=1, how="all") # Dropa colunas infinitamente vazias produzidas por formatação suja

            # 4. Formataçao e Padronização de Colunas
            df.columns = df.columns.astype(str).str.lower().str.replace(" ", "").str.replace(".", "")
            
            if "cpf/cnpj" in df.columns:
                df = df.drop("cpf/cnpj", axis=1) # Excluí as LGPD para inserir no DB

            # Mapeia colunas velhas pra colunas da Tabela
            colunas_map = {
                "dtacordo": "dtAcordo",
                "dtpgto": "dtPgto",
                "vctoparc": "vctoParc",
                "valorpgto": "valorTotal",
            }
            df = df.rename(columns=colunas_map)

            # Força o Dataset a ter somente essas colunas cruciais
            colunas_principais = [
                "cliente", "fase", "contrato", "dtAcordo", "dtPgto",
                "parcela", "plano", "vctoParc", "principal", "multa",
                "juros", "despesa", "operador", "valorTotal"
            ]
            
            # Checa quais faltam caso o layout do Excel mude bruscamente (boa prática)
            faltantes = set(colunas_principais) - set(df.columns)
            for f in faltantes:
                df[f] = None
                
            df = df[colunas_principais].copy() # Fazemos uma cópia separando do pai em mémoria

            # 5. Tratamento de Tipos
            for col in ["dtAcordo", "dtPgto", "vctoParc"]:
                df[col] = pd.to_datetime(df[col], errors="coerce") # Converte para datetime e ignora falhas pontuais (joga NaT)

            df["filial"] = None # Regra de Negócio

            # 6. Lógica de Faixas de Atrasos
            df["atraso"] = (df["dtPgto"] - df["vctoParc"]).dt.days
            
            # Calculamos qual foi o pior dia dentre as parcelas pagas no grupo de Contratos
            maior_atraso = df.groupby("contrato")["atraso"].max().reset_index()
            maior_atraso = maior_atraso.rename(columns={"atraso": "maiorAtraso"})
            df = pd.merge(df, maior_atraso, on="contrato", how="left")

            # Esta subfunção apenas encapsula as fases de atraso
            def classificar_fase(atraso):
                if pd.isna(atraso): return "Fora da fase"
                if atraso >= 1800: return "Fase 1801 a 9999"
                elif atraso >= 1440: return "Fase 1441 a 1800"
                elif atraso >= 1080: return "Fase 1081 a 1440"
                elif atraso >= 720: return "Fase 721 a 1080"
                elif atraso >= 360: return "Fase 361 a 720"
                elif atraso >= 240: return "Fase 241 a 360"
                elif atraso >= 180: return "Fase 181 a 240"
                elif atraso >= 120: return "Fase 121 a 180"
                elif atraso >= 90: return "Fase 91 a 120"
                elif atraso >= 60: return "Fase 61 a 90"
                elif atraso >= 30: return "Fase 31 a 60"
                elif atraso >= 10: return "Fase 10 a 30"
                else: return "Fora da fase"

            # Aplica via apply para todas as linhas de um único golpe de vetor (é muito peroformático)
            df["faseAtraso"] = df["maiorAtraso"].apply(classificar_fase)

            # 7. Limpeza e Conclusões Pós Join
            df["filial"] = df["filial"].replace(np.nan, None)
            
            # Preenche parcelas vazias pra nao quebrar convertendo para float primeiro
            df['parcela'] = df['parcela'].fillna(0).astype(int)
            df['plano'] = df['plano'].fillna(0).astype(int)

            for float_col in ["principal", "multa", "juros", "despesa", "valorTotal"]:
                df[float_col] = df[float_col].astype(float)
                
            dataframes.append(df)

        except Exception as e:
            print(f"❌ Erro destrutivo ao ler arquivo {arquivo}: {e}")

    if dataframes:
        # Pega todos os relatorios abertos acima e costura eles em único DF Super Master
        df_final = pd.concat(dataframes, ignore_index=True)
        # Extraí as linhas que deram pau pela repetição de arquivos
        df_final = df_final.drop_duplicates(subset=["contrato", "dtPgto", "parcela", "vctoParc", "operador"])

        # Por fim, salvamos nas pastas correntas internamente pro programador/analista usar nos 'notebooks' posteriormente
        caminho_csv = os.path.join(pasta_output, "pagamentos_semear_tratados.csv")
        df_final.to_csv(caminho_csv, index=False)
        print(f"✅ Processamento de dados Pandas concluído! Artefato em: {caminho_csv}")

        return df_final
    
    return None

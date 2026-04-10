import os
import sys


# 1. pegar o caminho atual
caminho_atual = os.path.abspath(__file__)

# 2. voltar pasta de origem
pasta_origigem = os.path.dirname(caminho_atual)

# 3. voltar pasta raiz
pasta_raiz = os.path.dirname(pasta_origigem)

# 4. adicionar pasta sys
sys.path.append(pasta_raiz)

# 5. ver os buscar dados
from src.services.auth_service import criar_hash_senha, verificar_senha, gerar_token_numerico, salvar_token

# testar criação de senha

def test_hash_e_verificacao():
    # 1. Cria a senha e o hash
    senha_original = "Gugu123"
    hash_gerado = criar_hash_senha(senha_original)
    
    # 2. Testa verificação com senha correta
    resultado_correto = verificar_senha(hash_gerado, "Gugu123")
    assert resultado_correto == True  # Deve ser True
    
    # 3. Testa verificação com senha errada
    resultado_errado = verificar_senha(hash_gerado, "senhaerrada")
    assert resultado_errado == False  # Deve ser False

    # 4. gerar token
    resultado_token = gerar_token_numerico()
    assert resultado_token is not None
    print(resultado_token)

    # 5. salvar token
    resultado_salvar_token = salvar_token(
        "2552GUSTHAVO",
        resultado_token,

    )
    print(resultado_salvar_token)

    


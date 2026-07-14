import sys
sys.path.insert(0, '.')

from src.dashboard.callbacks.adm_callbacks import atualizar_tabela_tma_adm

# Mock de dados do operador administrador
dados_operador = {'perfil': 'adm', 'login': 'ADM'}

print("Executando callback de TMA para o painel de ADM...")
data, columns = atualizar_tabela_tma_adm(
    mes=7,
    ano=2026,
    filtro_atividade="TODOS",
    operador_filtro="TODOS",
    n=0,
    dados_operador=dados_operador
)

print(f"Colunas retornadas ({len(columns)}):")
for col in columns:
    print(f"  - {col['name']} ({col['id']})")

print(f"\nLinhas de dados retornadas ({len(data)}):")
for row in data[:10]:
    print(f"  Operador: {row['operador']:15s} | TMA: {row['tma']} | Acionamentos: {row['acionamentos']:3d} | Clientes: {row['clientes']:3d} | Ritmo: {row['ritmo']} | Reacionamento: {row['reacionamento']}")

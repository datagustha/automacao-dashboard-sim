import sys
sys.path.insert(0, '.')
from src.services.db_service import buscar_todos_operadores_por_banco, Buscar_pagamento_semear
from src.dashboard_v2.services.operador_service import montar_dashboard_operador
from datetime import datetime, date

# Pega o primeiro operador ativo da SEMEAR
operadores = buscar_todos_operadores_por_banco('SEMEAR') or []
op = next((o for o in operadores if o.get('atividade','').upper() == 'ATIVO'), None)

if not op:
    print("Nenhum operador ativo encontrado!")
    exit()

print("Operador: {}".format(op.get('login')))
print("Chamando montar_dashboard_operador(op, ano=2026, mes=7)...")

resultado = montar_dashboard_operador(op, ano=2026, mes=7)

pags = resultado.get('ultimos_pagamentos', [])
print("Total ultimos_pagamentos retornados: {}".format(len(pags)))

# Verifica quais estao fora de julho/2026
fora = []
for p in pags:
    dt = p.get('dtPgto', '')
    if not str(dt).startswith('2026-07'):
        fora.append(dt)

print("Pagamentos fora de julho/2026 em ultimos_pagamentos: {}".format(len(fora)))
for f in sorted(fora, reverse=True)[:10]:
    print("  FORA: {}".format(f))

if not fora:
    print("Backend correto! Todos os pagamentos estao em julho/2026.")
    print("Primeiros 3 pagamentos:")
    for p in pags[:3]:
        print("  {}".format(p.get('dtPgto')))

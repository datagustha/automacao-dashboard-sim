import holidays
from datetime import date

feriados = holidays.country_holidays('BR', years=2026)
data_teste = date(2026, 6, 4)

print(f"Data: {data_teste}")
print(f"É feriado? {data_teste in feriados}")
print(f"Nome do feriado: {feriados.get(data_teste)}")

print("\nTodos os feriados de 2026:")
for dt, nome in sorted(feriados.items()):
    print(f"  {dt}: {nome}")

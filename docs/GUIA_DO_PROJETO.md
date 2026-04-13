# 🗺️ Guia do Projeto — Semear Dashboard

> Este guia explica **onde cada coisa está** no projeto e **como o sistema funciona**.
> Leia antes de qualquer alteração para saber exatamente onde mexer.

---

## 📁 Mapa de Arquivos

```
semear/
├── src/
│   ├── config/
│   │   └── database.py          ← Conexão com o MySQL (engine do SQLAlchemy)
│   │
│   ├── models/                  ← Definem as tabelas do banco de dados
│   │   ├── LoginModel.py        ← Tabela d_analista (operadores e ADM)
│   │   ├── PgtoSemearModel.py   ← Tabela fpgtoSemear (pagamentos SEMEAR)
│   │   ├── PgtoAgoracredModel.py← Tabela fpgtoAgoracred (pagamentos AGORACRED)
│   │   ├── MetassemearModel.py  ← Tabela fmetaSemearop (metas SEMEAR)
│   │   ├── MetasagoracredModel.py← Tabela fmetaAgoracredop (metas AGORACRED)
│   │   └── TokenModel.py        ← Tabela tokens_recuperacao (tokens de acesso)
│   │
│   ├── services/                ← Toda a lógica de negócio e acesso ao banco
│   │   ├── db_service.py        ← ÚNICO arquivo que faz queries SQL
│   │   ├── analytics_service.py ← Cálculos (KPIs, performance, metas)
│   │   ├── auth_service.py      ← Autenticação (hash de senha, tokens por e-mail)
│   │   └── email_service.py     ← Envio de e-mails (tokens de acesso)
│   │
│   └── dashboard/
│       ├── app.py               ← PONTO DE ENTRADA — inicializa o Dash
│       ├── assets/              ← CSS, imagens, logo
│       │
│       ├── components/          ← Blocos visuais reutilizáveis
│       │   ├── cards.py         ← Cards de KPI (faturamento, ticket, etc.)
│       │   ├── graficos.py      ← Gráficos (linha, barras)
│       │   ├── menus.py         ← Sidebar e Header (usados em todas as páginas)
│       │   └── tabelas.py       ← Tabelas Dash DataTable
│       │
│       ├── layouts/             ← Montagem das páginas
│       │   ├── login.py         ← Tela de login
│       │   ├── dashboard.py     ← Dashboard do OPERADOR (SEMEAR/AGORACRED)
│       │   ├── dashboard_adm.py ← Dashboard do ADM (visão consolidada)
│       │   ├── pagamentos.py    ← Tela de pagamentos
│       │   ├── operador_detalhe.py← Detalhe de desempenho de um operador
│       │   └── operadores_adm.py← Seleção de banco + operador (só ADM)
│       │
│       └── callbacks/           ← Funções reativas (Dash Callbacks)
│           ├── auth_callbacks.py    ← Login, logout, roteamento de páginas
│           ├── graficos_callbacks.py← KPIs e gráficos do dashboard operador
│           ├── pgto_callbacks.py    ← Tabela de pagamentos
│           ├── operador_callbacks.py← Tabelas dia-a-dia, mês-a-mês, performance
│           └── adm_callbacks.py     ← KPIs e tabelas do dashboard ADM
│
├── semearProcesso.py    ← Script de automação (scraper de pagamentos)
└── requirements.txt    ← Dependências Python
```

---

## 🔄 Como o Sistema Funciona

### Fluxo Principal

```
Usuário acessa → Login → auth_callbacks identifica perfil
                              ↓
                    banco = 'SEMEAR' → dashboard.py (operador SEMEAR)
                    banco = 'AGORACRED' → dashboard.py (operador AGORACRED)
                    banco = 'ADM' → dashboard_adm.py (visão do grupo)
```

### Regras de Negócio por Perfil

| Perfil | Banco | O que vê |
|--------|-------|----------|
| ADM | ADM | Todos os operadores dos 2 bancos, todos os pagamentos |
| Operador SEMEAR | SEMEAR | Só os próprios dados, exclui "Fora da fase" |
| Operador AGORACRED | AGORACRED | Só os próprios dados, considera todos os pagamentos |

### Por que "Fora da fase" é excluído no SEMEAR?
No SEMEAR, pagamentos classificados como `faseAtraso = "Fora da fase"` **não entram** no faturamento computado. Essa regra existe em:
- `analytics_service.py` → funções `calcular_indicadores_operador`, `calcular_faturamento_por_dia`, `calcular_pagamentos_por_fase`, `calcular_performance_operador`
- `operador_callbacks.py` → função `filtrar_fora_da_fase`

---

## 🏃 Como Executar

```bash
# Na pasta raiz do projeto
.\venv\Scripts\python.exe -m src.dashboard.app
# Abre em: http://127.0.0.1:8050
```

---

## 🔗 Dependências Entre Arquivos

```
app.py
  └── importa callbacks → auth_callbacks, graficos_callbacks,
                           pgto_callbacks, operador_callbacks, adm_callbacks

auth_callbacks.py
  └── importa layouts → login, dashboard, dashboard_adm,
                        pagamentos, operador_detalhe, operadores_adm
  └── importa services → db_service (Buscar_login)
                         auth_service (verificar senha, token)

graficos_callbacks.py / adm_callbacks.py / operador_callbacks.py
  └── importa services → db_service (queries)
                         analytics_service (cálculos)

db_service.py
  └── importa config → database.py (engine)
  └── importa models → LoginModel, PgtoSemearModel, PgtoAgoracredModel,
                        MetassemearModel, MetasagoracredModel
```

---

## 📚 Mais Documentação

- [ONDE_MEXER.md](./ONDE_MEXER.md) → "Quero alterar X, qual arquivo editar?"
- [BANCO_DE_DADOS.md](./BANCO_DE_DADOS.md) → Tabelas MySQL e modelos SQLAlchemy
- [FLUXO_DE_LOGIN.md](./FLUXO_DE_LOGIN.md) → Passo a passo da autenticação

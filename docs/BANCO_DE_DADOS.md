# 🗄️ Banco de Dados — Documentação

> Todos os dados estão em **um único banco MySQL**: `dbsimfacilita` no servidor `192.168.100.200`.
> As credenciais ficam no arquivo `.env` na raiz do projeto.

---

## 📡 Conexão

**Arquivo:** `src/config/database.py`

```python
DATABASE_URL = "mysql+pymysql://{USER}:{PASS}@{HOST}/dbsimfacilita?charset=utf8mb4"
engine = create_engine(DATABASE_URL, pool_recycle=3600, echo=False)
```

- `pool_recycle=3600` → Recria conexões a cada 1h para evitar timeout do MySQL
- `echo=False` → Mude para `True` para ver o SQL gerado no terminal (debug)
- Todas as queries usam `with Session(engine) as session:` — a sessão fecha automaticamente

---

## 📋 Tabelas e Modelos

### `d_analista` → Operadores e ADM
**Modelo:** `src/models/LoginModel.py` → classe `analistas`

| Coluna MySQL | Atributo Python | Tipo | Descrição |
|-------------|-----------------|------|-----------|
| `ID_analista` | `ID_analista` | Integer (PK) | Chave primária |
| `loguin` | `loguin` | String | Login do operador (ex: 2552ROSELI) |
| `nome_completo` | `nome_completo` | String | Nome completo |
| `turno` | `turno` | String | Turno (M=Manhã, T=Tarde, N=Noite) |
| `jornada` | `jornada` | String | Coluna legada |
| `banco` | `banco` | String | **'SEMEAR', 'AGORACRED' ou 'ADM'** |
| `imagem` | `imagem` | String | URL da foto do operador |
| `email` | `email` | String | E-mail para envio de token |
| `senha_hash` | `senha_hash` | String | Hash bcrypt da senha |
| `primeiro_acesso` | `primeiro_acesso` | Boolean | True = nunca configurou senha |

> [!IMPORTANT]
> O campo `banco` é o que determina o **perfil** do usuário:
> - `SEMEAR` → Operador SEMEAR (exclui "Fora da fase")
> - `AGORACRED` → Operador AGORACRED (todos os pagamentos)
> - `ADM` → Visão consolidada de ambos os bancos

---

### `fpgtoSemear` → Pagamentos SEMEAR
**Modelo:** `src/models/PgtoSemearModel.py` → classe `PgtoSemearBoleto`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `operador` | String | Login do operador responsável |
| `cliente` | String | Nome do cliente |
| `contrato` | String | Número do contrato |
| `dtPgto` | DateTime | Data do pagamento |
| `valorTotal` | Float | Valor pago |
| `faseAtraso` | String | Fase do atraso (ex: "FASE 10 A 30", "Fora da fase") |
| `fase` | String | Fase do acordo |
| `parcela` | Integer | Número da parcela |
| `principal` | Float | Valor principal |
| `multa` | Float | Multa |
| `juros` | Float | Juros |
| `despesa` | Float | Despesa |

> [!WARNING]
> Pagamentos com `faseAtraso = "Fora da fase"` são **excluídos** dos cálculos SEMEAR.

---

### `fpgtoAgoracred` → Pagamentos AGORACRED
**Modelo:** `src/models/PgtoAgoracredModel.py` → classe `PgtoAgoracred`

Estrutura idêntica à tabela SEMEAR. Para AGORACRED, todos os pagamentos são considerados (sem filtro de fase).

---

### `fmetaSemearop` → Metas SEMEAR
**Modelo:** `src/models/MetassemearModel.py` → classe `Metas_semear`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `operador` | String | Login do operador |
| `data` | Date | Mês/ano da meta (ex: 2026-04-01) |
| `turno` | String | Turno |
| `meta70` | Float | Meta para atingir 70% |
| `meta80` | Float | Meta para atingir 80% |
| `meta90` | Float | Meta para atingir 90% |
| `meta100` | Float | Meta para atingir 100% |
| `metaRanking` | Float | Meta para ranking |

---

### `fmetaAgoracredop` → Metas AGORACRED
**Modelo:** `src/models/MetasagoracredModel.py` → classe `Metas_agoracred`

Estrutura idêntica às metas SEMEAR.

---

### `tokens_recuperacao` → Tokens de acesso
**Modelo:** `src/models/TokenModel.py` → classe `TokenRecuperacao`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `login` | String | Login do operador |
| `token` | String | Código de 6 dígitos |
| `tipo` | String | 'primeiro_acesso' ou 'reset_senha' |
| `expira_em` | DateTime | Data/hora de expiração (15 min) |
| `usado` | Boolean | True = já foi usado |

---

## 🔧 Funções de Banco (db_service.py)

| Função | Para que serve |
|--------|---------------|
| `Buscar_login(login)` | Busca um operador pelo login (normaliza para maiúsculo) |
| `Buscar_pagamento_semear(operador)` | Todos os pagamentos SEMEAR de um operador |
| `Buscar_pagamento_agoracred(operador)` | Todos os pagamentos AGORACRED de um operador |
| `Buscar_pagamento_por_operador(operador)` | **Genérica** — chama a certa baseado no `banco`. Suporta login = "TODOS" p/ consolidado. |
| `buscar_metas_semear(operador)` | Metas SEMEAR de um operador |
| `buscar_metas_agoracred(operador)` | Metas AGORACRED de um operador |
| `buscar_metas_por_operador(operador)` | **Genérica** — chama a certa baseado no `banco`. Suporta login = "TODOS" p/ consolidado. |
| `buscar_todos_operadores_por_banco(banco)` | Todos os operadores de SEMEAR ou AGORACRED (ADM) |
| `buscar_pagamentos_todos_operadores_por_banco(banco)` | Todos os pagamentos de todos os operadores de um banco (ADM) |
| `enviar_para_banco_semear(df)` | Insere lote de pagamentos SEMEAR (automação scraper) |
| `enviar_para_banco_agoracred(df)` | Insere lote de pagamentos AGORACRED (automação scraper) |

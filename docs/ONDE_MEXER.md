# 🔧 Onde Mexer — Guia Rápido de Alterações

> "Quero alterar **X**... qual arquivo edito?"

---

## 📊 Dashboard

| O que alterar | Arquivo | O que fazer |
|--------------|---------|-------------|
| Colunas da tabela de performance | `callbacks/graficos_callbacks.py` | Editar lista `colunas` na função `atualizar_tabela_performance` |
| Colunas da tabela de pagamentos recentes | `callbacks/graficos_callbacks.py` | Editar `rename_dict` e `colunas_visiveis` |
| Gráfico de evolução diária | `services/analytics_service.py` | Função `calcular_faturamento_por_dia` |
| Gráfico por fase (SEMEAR) | `services/analytics_service.py` | Função `calcular_pagamentos_por_fase` |
| Cards de KPI (faturamento, ticket, etc.) | `components/cards.py` | Funções `card_indicador` e `card_meta` |
| Layout visual do dashboard (operador) | `layouts/dashboard.py` | Editar `get_dashboard_layout()` |
| Layout visual do dashboard (ADM) | `layouts/dashboard_adm.py` | Editar `get_dashboard_adm_layout()` |
| Calcular projeção / falta para meta | `services/analytics_service.py` | Função `calcular_performance_operador` |

---

## 🔐 Login e Autenticação

| O que alterar | Arquivo | O que fazer |
|--------------|---------|-------------|
| Rota de cada página | `callbacks/auth_callbacks.py` | Função `render_page` |
| O que é salvo no login-store | `callbacks/auth_callbacks.py` | Dicionário `dados_usuario` (linhas ~274 e ~337) |
| Lógica de verificação de senha | `services/auth_service.py` | Função `verificar_senha` |
| Fluxo de primeiro acesso (token por e-mail) | `services/auth_service.py` | Funções `salvar_token`, `validar_token` |
| Qual perfil vai para qual dashboard | `callbacks/auth_callbacks.py` | Condição `if perfil == 'adm'` em `render_page` |

---

## 💳 Pagamentos

| O que alterar | Arquivo | O que fazer |
|--------------|---------|-------------|
| Tabela de pagamentos (layout) | `layouts/pagamentos.py` | Editar `get_pagamentos_layout()` |
| Tabela de pagamentos (dados/filtros) | `callbacks/pgto_callbacks.py` | Função `atualizar_tabela_mestra` |
| Seletor de banco (ADM) | `callbacks/pgto_callbacks.py` | Input `banco-selecionado-pgtos` |
| Colunas visíveis na tabela de pagamentos | `callbacks/pgto_callbacks.py` | Lista `colunas_visiveis` |

---

## 👤 Operadores

| O que alterar | Arquivo | O que fazer |
|--------------|---------|-------------|
| Tela detalhe / consolidação (ADM) | `layouts/operador_detalhe.py` | Editar `get_operador_detalhe_layout()` (agora inclui dropdowns ADM) |
| Tela detalhe (Operador comum) | `layouts/operador_detalhe.py` | Idem acima |
| Tabela dia a dia | `callbacks/operador_callbacks.py` | Função `atualizar_tabela_dia_dia` |
| Tabela dia útil (com Feriados) | `callbacks/operador_callbacks.py` | Função `atualizar_tabela_dia_util` / `get_dias_uteis` |
| Tabela mês a mês | `callbacks/operador_callbacks.py` | Função `atualizar_tabela_mes_mes` |
| Tabela performance (detalhe) | `callbacks/operador_callbacks.py` | Função `atualizar_tabela_performance` |
| Subtítulo com dias trabalhados | `callbacks/operador_callbacks.py` | Variável `txt_dias` em `atualizar_tabela_performance` |
| Gráfico de faturamento mensal | `callbacks/operador_callbacks.py` | Função `atualizar_grafico_mensal` |
| População de opções p/ ADM | `callbacks/adm_callbacks.py` | Função `carregar_operadores_banco` (Gera opção TODOS) |

---

## 🏛️ Dashboard ADM

| O que alterar | Arquivo | O que fazer |
|--------------|---------|-------------|
| KPIs consolidados (faturamento total, ticket) | `callbacks/adm_callbacks.py` | Função `atualizar_dashboard_adm` |
| Tabela de ranking dos operadores SEMEAR | `callbacks/adm_callbacks.py` | Bloco `processar_banco('SEMEAR')` |
| Tabela de ranking dos operadores AGORACRED | `callbacks/adm_callbacks.py` | Bloco `processar_banco('AGORACRED')` |
| Colunas da tabela de ranking ADM | `callbacks/adm_callbacks.py` | Lista `colunas` dentro de `processar_banco` |
| Layout do dashboard ADM | `layouts/dashboard_adm.py` | Editar `get_dashboard_adm_layout()` |

---

## 🗄️ Banco de Dados

| O que alterar | Arquivo | O que fazer |
|--------------|---------|-------------|
| String de conexão MySQL | `config/database.py` | Variáveis `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME` |
| Adicionar coluna ao modelo | `models/*.py` | Adicionar `Column(...)` na classe correspondente |
| Buscar operadores de um banco | `services/db_service.py` | `buscar_todos_operadores_por_banco(banco)` |
| Buscar pagamentos de um operador | `services/db_service.py` | `Buscar_pagamento_por_operador(dados_operador)` |
| Buscar metas de um operador | `services/db_service.py` | `buscar_metas_por_operador(dados_operador)` |

---

## 🎨 Visual / Estilo

| O que alterar | Arquivo | O que fazer |
|--------------|---------|-------------|
| Cores, fontes, espaçamentos globais | `assets/style.css` (ou similar) | Variáveis CSS `--purple-main`, `--text-main`, etc. |
| Sidebar (menu lateral) | `components/menus.py` | Função `get_sidebar` |
| Header (topo da página) | `components/menus.py` | Função `get_header` |
| Estilo das tabelas | `components/tabelas.py` | `style_header`, `style_cell`, `style_data_conditional` |

---

## ⚠️ Regras Importantes

> [!WARNING]
> **Nunca modifique `database.py` com senhas reais** no código. Use o arquivo `.env`.

> [!IMPORTANT]
> **Ao adicionar um novo Output em um callback**, você DEVE adicionar o elemento correspondente no layout. Caso contrário o Dash vai lançar erro na inicialização.

> [!TIP]
> **Login é sempre normalizado para maiúsculo** em `db_service.py → Buscar_login()`. O usuário pode digitar minúsculo que funciona.

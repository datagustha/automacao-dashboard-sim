# 📖 Dashboard SIM Facilita — Documentação Técnica

## Estrutura do Dashboard

```
src/dashboard/
├── app.py                  # Ponto de entrada principal (Stores GLOBAIS + registro de callbacks)
├── layouts/                # Telas/páginas (o que o usuário VÊ)
│   ├── login.py            # Tela de login (2FA, criação de senha, reset)
│   ├── dashboard.py        # Dashboard do Operador (KPIs, gráficos, tabela)
│   ├── dashboard_adm.py    # Dashboard do ADM (visão consolidada SEMEAR + AGORACRED)
│   ├── pagamentos.py       # Tela de Pagamentos (tabela completa)
│   ├── operador_detalhe.py # Detalhes do Operador (dia a dia, mês a mês, performance)
│   └── esqueleto.py        # ⚠️ LEGADO — arquivo limpo, sem uso ativo
├── callbacks/              # Lógica interativa (o "cérebro")
│   ├── auth_callbacks.py   # Login, logout, roteamento de páginas
│   ├── graficos_callbacks.py # KPIs, gráficos e tabela do dashboard
│   ├── pgto_callbacks.py   # Tabela mestra da tela de Pagamentos
│   ├── operador_callbacks.py # Tabelas e gráficos do detalhe do operador
│   └── adm_callbacks.py    # KPIs e ranking do painel ADM
├── components/             # Peças reutilizáveis
│   ├── menus.py            # Sidebar (navegação) + Header (avatar do usuário)
│   ├── cards.py            # Cards de KPI e Meta
│   ├── tabelas.py          # DataTables (simples, cheia, com gráfico)
│   └── graficos.py         # Gráficos Plotly reutilizáveis
└── assets/
    ├── style.css           # CSS global (variáveis, sidebar, cards, responsividade)
    └── *.png               # Logos e imagens
```

---

## ⚠️ REGRAS CRÍTICAS

### 1. Stores Globais — NUNCA duplicar
Os `dcc.Store` de autenticação são definidos **APENAS** no `app.py`:

```python
# app.py (layout raiz)
dcc.Store(id='login-success-store', storage_type='local')
dcc.Store(id='login-step-store', data={'step': 'login'}, storage_type='local')
```

**NUNCA** crie esses Stores em layouts de página (login.py, dashboard.py, etc.)!
Duplicá-los sobrescreve os dados de autenticação e quebra a navegação.

### 2. Logout — Sempre limpar os Stores
O callback de logout DEVE limpar `login-success-store` e `login-step-store`:

```python
# auth_callbacks.py - Callback 3
return None, {'step': 'login'}, "/"
#      ↑ limpa dados   ↑ reseta step   ↑ redireciona
```

---

## Fluxo Completo: Login → Dashboard → Navegação → Logout

```
1. USUÁRIO ABRE O SITE
   ↓
2. URL = "/" → render_page() mostra get_login_layout()
   ↓
3. USUÁRIO DIGITA LOGIN → gerenciar_autenticacao() verifica senha
   ↓
4. SENHA OK → envia 2FA por e-mail
   ↓
5. 2FA OK → salva dados no login-success-store + redireciona para /dashboard
   ↓
6. render_page() detecta URL /dashboard + dados no store
   ↓
7. ADM → get_dashboard_adm_layout() | Operador → get_dashboard_layout()
   ↓
8. USUÁRIO NAVEGA → clica em "Pagamentos" na sidebar
   ↓
9. dcc.Link muda URL para /pagamentos → render_page() renderiza nova página
   ↓
10. USUÁRIO CLICA "SAIR" → fazer_logout() limpa stores + redireciona
```

---

## O que cada callback faz

| Arquivo | O que faz | Quando é ativado |
|---|---|---|
| `auth_callbacks.py` | Login (2FA), logout, roteamento de páginas | Login, troca de URL, clique em Sair |
| `graficos_callbacks.py` | Atualiza KPIs, gráficos e tabela do Dashboard | Filtros de mês/ano/fase/busca ou timer |
| `pgto_callbacks.py` | Atualiza tabela mestra de Pagamentos | Filtros de texto/banco na tela de Pagamentos |
| `operador_callbacks.py` | Tabelas dia a dia, dia útil, mês a mês, performance | Filtros de mês/ano na tela de Operador |
| `adm_callbacks.py` | KPIs globais + ranking por banco | Filtros de mês/ano/atividade no painel ADM |

---

## Onde mexer para cada coisa

| O que quer mudar | Onde mexer |
|---|---|
| Aparência da tela (cores, posições) | `layouts/*.py` |
| Opções do filtro (dropdowns) | `layouts/*.py` |
| O que acontece quando muda filtro | `callbacks/*_callbacks.py` |
| Como os números são calculados | `services/analytics_service.py` |
| Aparência de card ou tabela | `components/*.py` |
| Cores e estilos globais (CSS) | `assets/style.css` |
| Sidebar e Header | `components/menus.py` |
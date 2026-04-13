# 🔐 Fluxo de Login — Documentação

> Explica passo a passo como o login funciona no sistema.

---

## Visão Geral

```
Usuário digita login
        ↓
[1] Busca no banco (d_analista)
        ↓
tem senha?
  NÃO → Enviar token por e-mail → Usuário digita token → Criar nova senha → Login
  SIM → Usuário digita senha → Verificar hash → Login
        ↓
[2] Salva no store: { nome, login, imagem, banco, perfil }
        ↓
[3] Roteia para a página correta
  perfil = 'adm'      → /dashboard (dashboard_adm)
  perfil = 'operador' → /dashboard (dashboard operador)
```

---

## Passo a Passo Detalhado

### 1. Usuário digita o login

- O login é **normalizado para maiúsculo** automaticamente em `db_service.py → Buscar_login()`
- Então `2552roseli`, `2552Roseli` e `2552ROSELI` funcionam igualmente

### 2. Sistema verifica se tem senha

```python
# auth_service.py → operador_tem_senha()
if operador.senha_hash:  # tem senha cadastrada
    → step = 'validar_senha'
else:  # nunca configurou senha
    → step = 'validar_token_primeiro'
```

### 3a. Se TEM senha — valida diretamente

```
Usuário digita senha
         ↓
verificar_senha(hash_do_banco, senha_digitada)  # werkzeug bcrypt
         ↓
OK → salva store → redireciona
ERROU → mostra erro
```

### 3b. Se NÃO tem senha — primeiro acesso por token

```
Sistema gera token de 6 dígitos
         ↓
Salva token no banco (tabela tokens_recuperacao, expira em 15 min)
         ↓
Envia token por e-mail (email_service.py)
         ↓
Usuário digita o token
         ↓
validar_token() verifica: correto? não usado? não expirado?
         ↓
Usuário cria nova senha (mínimo 4 caracteres)
         ↓
salvar_senha() gera hash bcrypt e salva no banco
         ↓
Login automático
```

---

## O Store de Login (`login-success-store`)

O store é salvo no **localStorage do navegador** e contém:

```python
{
    'nome':   'ROSELI BATISTA DOS SANTOS',  # nome completo
    'login':  '2552ROSELI',                 # login normalizado
    'imagem': 'https://i.ibb.co/...',       # URL da foto
    'banco':  'SEMEAR',                     # 'SEMEAR', 'AGORACRED' ou 'ADM'
    'perfil': 'operador'                    # 'operador' ou 'adm'
}
```

> [!IMPORTANT]
> Todos os callbacks que precisam saber quem está logado leem este store via `State('login-success-store', 'data')`.

---

## Roteamento por Perfil

**Arquivo:** `callbacks/auth_callbacks.py → render_page()`

| URL | Perfil ADM | Perfil Operador |
|-----|------------|-----------------|
| `/dashboard` | Dashboard ADM (2 bancos) | Dashboard do operador |
| `/pagamentos` | Todos com seletor de banco | Só os próprios |
| `/operadores` | Seletor de banco + dropdown | Redireciona para `/operador/{login}` |
| `/operador/{login}` | Detalhe do operador escolhido | Detalhe do próprio login |

---

## Arquivos Envolvidos no Login

| Arquivo | Responsabilidade |
|---------|-----------------|
| `layouts/login.py` | Visual da tela de login |
| `callbacks/auth_callbacks.py` | Toda a lógica de fluxo (steps) e roteamento |
| `services/auth_service.py` | Hash de senha, geração/validação de token |
| `services/email_service.py` | Envio do e-mail com token |
| `services/db_service.py` | Buscar operador no banco (`Buscar_login`) |
| `models/LoginModel.py` | Mapeamento da tabela `d_analista` |
| `models/TokenModel.py` | Mapeamento da tabela `tokens_recuperacao` |

---

## Redefinir Senha (Esqueci minha senha)

Fluxo ativado pelo botão **"Esqueci minha senha"** na tela de login:

```
Usuário clica em "Esqueci minha senha" (após digitar o login)
         ↓
Sistema envia token de 6 dígitos por e-mail (tipo = 'reset_senha')
         ↓
Usuário digita token
         ↓
Usuário cria nova senha
         ↓
Nova senha salva com hash no banco
```

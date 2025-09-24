# LaylaWeberBot — Starter (Python • Webhook • Render)

Pronto para rodar no **Render** (webhook) ou localmente (polling). Mantém em sigilo o token e segue a ordem de botões pedida: **1) Pix (PushinPay)**, **2) Cartão/PayPal (Ko‑fi)**, **3) Grupo de Prévias**.

---

## 1) Estrutura

```
.
├── app.py
├── requirements.txt
├── render.yaml
├── .env.example
└── README.md
```

### Variáveis (.env)
Copie `.env.example` para `.env` e preencha:
- `BOT_TOKEN`: token do seu bot (@BotFather)
- `PUSHINPAY_URL`: link direto do checkout PushinPay (PIX)
- `KOFI_URL`: link do produto no Ko‑fi (cartão/PayPal)
- `CANAL_PREVIAS`: link do canal/grupo de prévias
- `CANAL_VIP`: link do canal/grupo VIP (dica: use link com limite de ingressos)
- `ADMIN_USER_IDS`: IDs separados por vírgula com quem pode usar comandos de admin (ex.: `12345,67890`)

> **Atenção:** não salve o `BOT_TOKEN` em memória. Use `.env` local ou variáveis do Render.

---

## 2) Rodando local (polling)

Requisitos: Python 3.10+

```bash
pip install -r requirements.txt
cp .env.example .env  # edite o arquivo
python app.py --mode polling
```

---

## 3) Deploy no Render (webhook)

1. Faça login em https://render.com e crie um **Web Service** conectando este repositório ou subindo os arquivos.
2. Use este `render.yaml` (padrão do repositório) ou crie o serviço manualmente:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Health check**: `/health`
3. Em **Environment**, crie as variáveis: `BOT_TOKEN`, `PUSHINPAY_URL`, `KOFI_URL`, `CANAL_PREVIAS`, `CANAL_VIP`, `ADMIN_USER_IDS`.
4. Após o primeiro deploy, o Render define `RENDER_EXTERNAL_URL` (ex.: `https://seuservico.onrender.com`). O app seta sozinho o webhook nesse URL (`/webhook`).
5. Teste no Telegram: envie `/start` ao bot.

---

## 4) Comandos disponíveis

- `/start` — Boas‑vindas + atalho para `/assinar`
- `/assinar` — Mostra os **3 botões** (PushinPay • Ko‑fi • Canal de Prévias) na ordem pedida
- `/ajuda` — Lista de comandos
- `/status` — Mostra status básico do serviço
- `/vip` — Envia o link do canal VIP (pode ser restrito por admin)
- `/aprovar <user_id>` — **Admin:** aprova manualmente um usuário (registra no log). Exemplo: `/aprovar 123456789`
- `/admin` — Mostra ações básicas do admin

> **Observação:** Fluxos de pagamento (PushinPay/Ko‑fi) aqui estão via **links externos**. Caso deseje confirmação automática via webhook de pagamento, precisamos integrar com as APIs/retornos específicos.

---

## 5) Dicas de segurança

- Use um **link VIP com limite de ingressos** e renovação periódica (no Telegram > Gerenciar Grupo > Links de convite).
- Mantenha `ADMIN_USER_IDS` preenchido. Apenas admins podem revelar o link VIP via `/vip` para todos.
- Nunca comite `.env` no Git.

---

## 6) Troubleshooting rápido

- **Bot não responde (webhook):** verifique se o serviço abriu porta e que o `RENDER_EXTERNAL_URL` foi criado. Rode `/status`.
- **Webhook já setado em outro URL:** use `/status` e reinicie o serviço (ele tenta setar/atualizar sozinho).
- **Erro 401:** cheque `BOT_TOKEN`.
- **Sem botões:** confirme `PUSHINPAY_URL`, `KOFI_URL`, `CANAL_PREVIAS` no ambiente.

---

Feito sob medida para o projeto **Bot Telegram** (LaylaWeberBot). Qualquer ajuste, me diga que eu atualizo o pacote.

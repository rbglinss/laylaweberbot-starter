# app.py
"""
Telegram bot for Render (Polling/Webhook auto).

Environment variables expected:
- BOT_TOKEN (required)
- USE_POLLING=true (recommended on Render Background Worker)
- RENDER_EXTERNAL_URL (only for webhook mode on Web Service)
- PUSHINPAY_URL, KOFI_URL, CANAL_PREVIAS, CANAL_VIP (optional links)
- ADMIN_USER_IDS (comma-separated Telegram user IDs for admin-only commands)
"""

import os
import logging
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    AIORateLimiter,
    CommandHandler,
    ContextTypes,
)

# ---------- Logging ----------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("laylaweberbot")

# ---------- ENV ----------
TOKEN = os.getenv("BOT_TOKEN")

PUSHINPAY_URL = os.getenv("PUSHINPAY_URL", "").strip()
KOFI_URL = os.getenv("KOFI_URL", "").strip()
CANAL_PREVIAS = os.getenv("CANAL_PREVIAS", "").strip()
CANAL_VIP = os.getenv("CANAL_VIP", "").strip()

def _parse_admins(val: str) -> List[int]:
    out: List[int] = []
    if not val:
        return out
    for p in val.replace(";", ",").split(","):
        p = p.strip()
        if not p:
            continue
        try:
            out.append(int(p))
        except ValueError:
            log.warning("ADMIN_USER_IDS contém valor inválido: %s", p)
    return out

ADMIN_IDS = _parse_admins(os.getenv("ADMIN_USER_IDS", ""))

# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []

    # 1º Pix (PushinPay)
    if PUSHINPAY_URL:
        keyboard.append([InlineKeyboardButton("💸 Pagar via Pix (PushinPay)", url=PUSHINPAY_URL)])

    # 2º Cartão/PayPal (Ko-fi)
    if KOFI_URL:
        keyboard.append([InlineKeyboardButton("💳 Cartão/PayPal (Ko‑fi)", url=KOFI_URL)])

    # 3º Link grupo de prévias
    if CANAL_PREVIAS:
        keyboard.append([InlineKeyboardButton("🎬 Grupo de Prévias", url=CANAL_PREVIAS)])

    # 4º Link VIP
    if CANAL_VIP:
        keyboard.append([InlineKeyboardButton("⭐ Canal VIP", url=CANAL_VIP)])

    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    text = (
        "Olá! Eu sou o LaylaWeberBot.\n\n"
        "Escolha uma opção abaixo ou envie /links para ver todos os atalhos."
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    parts = []
    if PUSHINPAY_URL: parts.append(f"• 💸 Pix: {PUSHINPAY_URL}")
    if KOFI_URL: parts.append(f"• 💳 Cartão/PayPal (Ko‑fi): {KOFI_URL}")
    if CANAL_PREVIAS: parts.append(f"• 🎬 Grupo de Prévias: {CANAL_PREVIAS}")
    if CANAL_VIP: parts.append(f"• ⭐ Canal VIP: {CANAL_VIP}")
    if not parts:
        if update.message:
            await update.message.reply_text("Nenhum link configurado no momento.")
        return
    if update.message:
        await update.message.reply_text("Links úteis:\n" + "\n".join(parts))

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("pong 🏓")

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin only: /broadcast <texto> envia para o próprio admin (exemplo simples)."""
    if update.effective_user and update.effective_user.id not in ADMIN_IDS:
        if update.message:
            await update.message.reply_text("Apenas administradores podem usar este comando.")
        return

    if not context.args:
        if update.message:
            await update.message.reply_text("Uso: /broadcast Seu texto aqui")
        return

    msg = " ".join(context.args)
    if update.message:
        await update.message.reply_text(f"📣 Broadcast enviado (exemplo): {msg}")

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Erro não tratado: %s", context.error)

# Ensures webhook is removed before polling to avoid conflicts
async def _post_init(app: Application):
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        log.info("Webhook removido (se existia).")
    except Exception as e:
        log.warning("Falha ao remover webhook: %s", e)

# ---------- App factory ----------
def build_app() -> Application:
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN não definido nas variáveis de ambiente.")

    application = (
        Application.builder()
        .token(TOKEN)
        .rate_limiter(AIORateLimiter())
        .post_init(_post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("links", links))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("broadcast", admin_broadcast))

    application.add_error_handler(on_error)
    return application

# ---------- Runner (Polling/Webhook auto) ----------
def _to_bool(v: str) -> bool:
    return bool(v) and v.strip().lower() in ("1", "true", "yes", "on", "y")

def main():
    application = build_app()

    use_polling = _to_bool(os.getenv("USE_POLLING", ""))

    if use_polling:
        log.info("Starting bot in POLLING mode...")
        application.run_polling(
            allowed_updates=None,
            drop_pending_updates=True,
            stop_signals=None,
        )
    else:
        base_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("PUBLIC_URL")
        if not base_url:
            log.warning("RENDER_EXTERNAL_URL não encontrado e USE_POLLING não é true; pulei setWebhook.")
            return
        port = int(os.getenv("PORT", "10000"))
        webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
        log.info("Starting bot in WEBHOOK mode at %s%s on port %s...", base_url, webhook_path, port)
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=webhook_path,
            webhook_url=f"{base_url}{webhook_path}",
            drop_pending_updates=True,
            stop_signals=None,
        )

if __name__ == "__main__":
    main()

import os
import asyncio
import logging
import json

from aiohttp import web
from dotenv import load_dotenv
from pathlib import Path
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, ContextTypes, AIORateLimiter,
)

# Carrega .env local e sobrescreve variáveis do sistema, se houver
load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=True)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("laylaweberbot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
PUSHINPAY_URL = os.getenv("PUSHINPAY_URL", "").strip()
KOFI_URL = os.getenv("KOFI_URL", "").strip()
CANAL_PREVIAS = os.getenv("CANAL_PREVIAS", "").strip()
CANAL_VIP = os.getenv("CANAL_VIP", "").strip()
ADMIN_USER_IDS = {int(x) for x in os.getenv("ADMIN_USER_IDS", "").replace(" ", "").split(",") if x}

PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_PATH = "/webhook"
HEALTH_PATH = "/health"

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS

def assinatura_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💳 PIX (PushinPay)", url=PUSHINPAY_URL or "https://example.com")],
        [InlineKeyboardButton(text="💳 Cartão/PayPal (Ko-fi)", url=KOFI_URL or "https://example.com")],
        [InlineKeyboardButton(text="👀 Canal de Prévias", url=CANAL_PREVIAS or "https://t.me/")],
    ]
    return InlineKeyboardMarkup(buttons)

def start_message_html(first: str) -> str:
    return (
        f"✨ <b>Bem-vindo(a), {first}!</b> 👋\n"
        "<b>Bot oficial da <u>Layla Weber</u></b>\n\n"
        "Para assinar o VIP, toque nos botões abaixo ou envie <code>/assinar</code>.\n"
        "• 1º <b>PIX (PushinPay)</b>\n"
        "• 2º <b>Cartão/PayPal (Ko‑fi)</b>\n"
        "• 3º <b>Canal de Prévias</b>\n"
        "——————————————\n"
        "✨ <b>Welcome!</b> 👋\n"
        "<b>Official <u>Layla Weber</u> bot</b>\n\n"
        "To subscribe, use the buttons below or send <code>/assinar</code>.\n"
        "• 1st <b>PIX (PushinPay)</b>\n"
        "• 2nd <b>Card/PayPal (Ko‑fi)</b>\n"
        "• 3rd <b>Previews Channel</b>"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first = user.first_name or "amigo"
    await update.message.reply_html(start_message_html(first))
    await update.message.reply_html("<b>Escolha uma opção:</b>", reply_markup=assinatura_keyboard())

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "<b>Comandos disponíveis</b>\n"
        "/start — boas-vindas\n"
        "/assinar — botões de pagamento e prévias\n"
        "/vip — link do canal VIP (pode ser restrito)\n"
        "/status — status do serviço\n"
        "/admin — comandos do administrador"
    )
    await update.message.reply_html(txt)

async def assinar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html("<b>Escolha uma opção:</b>", reply_markup=assinatura_keyboard())

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_admin(user_id):
        await update.message.reply_text(f"Link VIP: {CANAL_VIP or 'defina CANAL_VIP' }")
    else:
        await update.message.reply_text(
            "Para acesso ao VIP, faça a assinatura em /assinar.\n"
            "Após confirmação, um admin libera o seu acesso."
        )

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = {
        "webhook_url": context.bot_data.get("webhook_url"),
        "render_external_url": os.getenv("RENDER_EXTERNAL_URL"),
        "pushinpay": bool(PUSHINPAY_URL),
        "kofi": bool(KOFI_URL),
        "canal_previas": bool(CANAL_PREVIAS),
        "canal_vip": bool(CANAL_VIP),
        "admins": sorted(list(ADMIN_USER_IDS)),
    }
    await update.message.reply_text("Status:\n" + json.dumps(data, indent=2, ensure_ascii=False))

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Acesso restrito a administradores.")
        return
    await update.message.reply_text(
        "Admin:\n"
        "/aprovar <user_id> — marca aprovação manual\n"
        "/vip — envia link VIP"
    )

async def aprovar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("Acesso restrito a administradores.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Uso: /aprovar <user_id>")
        return
    try:
        approved_id = int(args[0])
    except ValueError:
        await update.message.reply_text("ID inválido.")
        return
    logger.info(f"ADMIN aprovou user_id={approved_id}")
    await update.message.reply_text(f"Usuário {approved_id} aprovado. Envie o link VIP com /vip.")

async def on_health(request: web.Request):
    return web.json_response({"ok": True})

async def on_webhook(request: web.Request, application: Application):
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="invalid json")
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response(text="ok")

async def setup_web_app(application: Application) -> web.Application:
    app = web.Application()
    app.router.add_get(HEALTH_PATH, on_health)
    app.router.add_post(WEBHOOK_PATH, lambda r: on_webhook(r, application))
    return app

async def run_webhook(application: Application):
    web_app = await setup_web_app(application)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"HTTP server running on port {PORT}")

    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        webhook_url = render_url.rstrip("/") + WEBHOOK_PATH
        await application.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
        application.bot_data["webhook_url"] = webhook_url
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.warning("RENDER_EXTERNAL_URL não encontrado; pulei setWebhook.")

    await asyncio.Event().wait()

def build_app() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN não definido. Configure a variável de ambiente.")
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("assinar", assinar))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("aprovar", aprovar))

    return app

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["webhook", "polling"], default="webhook")
    args = parser.parse_args()

    application = build_app()

    if args.mode == "polling":
        application.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None)
    else:
        asyncio.run(run_webhook(application))

if __name__ == "__main__":
    main()

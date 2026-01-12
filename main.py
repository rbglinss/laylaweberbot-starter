import logging
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# =========================
# ENV
# =========================
load_dotenv()

BOT_TOKEN     = os.getenv("BOT_TOKEN")
CANAL_PREVIAS = os.getenv("CANAL_PREVIAS")
PIX_URL       = os.getenv("PIX_URL") or os.getenv("PUSHINPAY_URL")
CARD_URL      = os.getenv("CARD_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN não definido.")
if not CANAL_PREVIAS:
    raise RuntimeError("CANAL_PREVIAS não definido.")

# =========================
# LOG
# =========================
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("laylabot")

# =========================
# MENSAGENS
# =========================
WELCOME_PT = (
    "😈 Oi… chegou no lugar certo.\n\n"
    "Aqui você encontra conteúdos exclusivos 🔥\n"
    "Entre pela prévia gratuita ou vá direto para o VIP 🔒\n\n"
    "Escolha abaixo:"
)

WELCOME_EN = (
    "😈 Hey… you’re in the right place.\n\n"
    "Exclusive content awaits 🔥\n"
    "Join the free preview or go straight to VIP 🔒\n\n"
    "Choose below:"
)

# =========================
# TECLADO
# =========================
def make_keyboard() -> InlineKeyboardMarkup:
    buttons = []

    if PIX_URL:
        buttons.append([
            InlineKeyboardButton(
                "💸 Pix (Brasil) | Instant Access",
                url=PIX_URL
            )
        ])

    if CARD_URL:
        buttons.append([
            InlineKeyboardButton(
                "💳 Card / PayPal (International)",
                url=CARD_URL
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "🎬 Ver prévias gratuitas",
            url=CANAL_PREVIAS
        )
    ])

    return InlineKeyboardMarkup(buttons)

# =========================
# HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"{WELCOME_PT}\n\n{WELCOME_EN}"
    await update.effective_chat.send_message(
        text=text,
        reply_markup=make_keyboard(),
        parse_mode="Markdown"
    )

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# =========================
# MAIN
# =========================
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    log.info("Bot Layla Weber iniciado (long polling)...")
    await app.run_polling(
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

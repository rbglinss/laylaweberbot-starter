# app.py
"""
Telegram Bot main file for Render deployment.

- Includes build_app() where you configure the Application and handlers.
- Uses USE_POLLING=true to run in polling mode (recommended for Background Worker).
- Falls back to webhook mode if USE_POLLING is not set and RENDER_EXTERNAL_URL is defined.
"""

import os
from telegram.ext import Application, AIORateLimiter

TOKEN = os.getenv("BOT_TOKEN")

def build_app() -> Application:
    """Configure and return the Application with your handlers."""
    application = (
        Application.builder()
        .token(TOKEN)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    # TODO: Add your handlers here, for example:
    # from telegram.ext import CommandHandler
    # async def start(update, context):
    #     await update.message.reply_text("Hello! I'm alive on Render 🚀")
    # application.add_handler(CommandHandler("start", start))

    return application


# --- Runner for Render: polling vs webhook ---

def _to_bool(v: str) -> bool:
    return bool(v) and v.strip().lower() in ("1", "true", "yes", "on", "y")

def main():
    application = build_app()

    use_polling = _to_bool(os.getenv("USE_POLLING", ""))

    if use_polling:
        print("Starting bot in POLLING mode...")
        application.run_polling(
            allowed_updates=None,
            drop_pending_updates=True,
            stop_signals=None,
        )
    else:
        base_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("PUBLIC_URL")
        if not base_url:
            print("RENDER_EXTERNAL_URL not found and USE_POLLING not true; skipped setWebhook.")
            return
        port = int(os.getenv("PORT", "10000"))
        webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
        print(f"Starting bot in WEBHOOK mode at {base_url}{webhook_path} on port {port}...")
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

# start.py
"""
Runner for Render: chooses POLLING or WEBHOOK automatically.

- Set USE_POLLING=true in Render to force long polling (recommended for Background Worker).
- If USE_POLLING is not true, it will try to run as WEBHOOK using:
    PORT (default 10000) and RENDER_EXTERNAL_URL (or PUBLIC_URL).
- Expects your existing `app.py` to expose a function `build_app()`
  that returns a `telegram.ext.Application` already configured
  (handlers, AIORateLimiter, etc.).
"""

import os
import sys

try:
    from app import build_app  # your existing function
except Exception as e:
    print("ERROR: Could not import build_app from app.py:", e, file=sys.stderr)
    sys.exit(1)


def to_bool(val: str) -> bool:
    if not val:
        return False
    return val.strip().lower() in ("1", "true", "yes", "on", "y")


def main() -> None:
    application = build_app()

    use_polling = to_bool(os.getenv("USE_POLLING", ""))

    if use_polling:
        print("Starting bot in POLLING mode...")
        # Drop pending updates to avoid replaying old messages on restarts.
        application.run_polling(
            allowed_updates=None,
            drop_pending_updates=True,
            stop_signals=None,
        )
        return

    base_url = (
        os.getenv("RENDER_EXTERNAL_URL")  # Render's public URL when using a Web Service
        or os.getenv("PUBLIC_URL")
    )
    if not base_url:
        print(
            "WARNING: RENDER_EXTERNAL_URL not found and USE_POLLING is not true; "
            "skipping setWebhook. Set USE_POLLING=true for Background Worker, or define RENDER_EXTERNAL_URL for Webhook.",
            file=sys.stderr,
        )
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

import os
import asyncio
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# ✅ Welcome message
WELCOME_MESSAGE = """👋 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
*Entry247 | Premium Signals 🇻🇳*

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

# ✅ Inline buttons
BUTTONS = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Entry247 | Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Entry247 | Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc quyền, Free 100%", "https://t.me/+ghRLRK6fHeYzYzE1"),
    ("6️⃣ Học và hiểu ( Video )", "https://t.me/+ghRLRK6fHeYzYzE1")
]

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text, url=link)] for text, link in BUTTONS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup, parse_mode="Markdown")

# ❌ No button callbacks needed for now
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

# ✅ Optional echo handler (if needed)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Gõ /start để truy cập các tài nguyên Entry247.")

# ✅ HTTP server for keep-alive (Render)
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"✅ Entry247 bot is alive!")

def run_keep_alive_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    print(f"🌐 Keep-alive HTTP server running on port {port}")
    server.serve_forever()

# ✅ Main entry point
async def main():
    TOKEN = os.environ.get("7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4")
    if not TOKEN:
        raise ValueError("⚠️ BOT_TOKEN not set in environment variables")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("🤖 Entry247 bot is running...")
    await app.updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_keep_alive_server, daemon=True).start()
    asyncio.run(main())

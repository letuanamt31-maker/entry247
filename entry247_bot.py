import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# === CONFIGURATION ===
TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"  # <- Thay bằng token hợp lệ
PORT = int(os.environ.get("PORT", 10000))

# === WELCOME MESSAGE + BUTTONS ===
WELCOME_MESSAGE = """Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

BUTTONS = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Entry247 | Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Entry247 | Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc quyền, Free 100%", "https://t.me/+ghRLRK6fHeYzYzE1"),
    ("6️⃣ Học và hiểu ( Video )", "https://t.me/+ghRLRK6fHeYzYzE1")
]

# === BOT HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text, url=link)] for text, link in BUTTONS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Không cần xử lý callback vì chỉ mở link
    pass

# === KEEP-ALIVE SERVER (cho Render.com) ===
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("✅ Entry247 bot is alive!".encode())

def run_keep_alive_server():
    server = HTTPServer(("0.0.0.0", PORT), KeepAliveHandler)
    print(f"✅ Keep-alive HTTP server running on port {PORT}")
    server.serve_forever()

# === MAIN BOT APP ===
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))

    # Start keep-alive server in background
    threading.Thread(target=run_keep_alive_server, daemon=True).start()

    print("🤖 Entry247 Bot đang chạy...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

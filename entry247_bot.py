import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ===== TOKEN BOT & WEBHOOK =====
TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"
WEBHOOK_URL = "https://entry247.onrender.com/webhook"

# ===== FLASK APP =====
app = Flask(__name__)
bot_app: Application = None  # Biến toàn cục

# ===== WELCOME MESSAGE & MENU =====
WELCOME_MESSAGE = """👋 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập  
Entry247 | Premium Signals 🇻🇳

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính dưới đây:
"""

BUTTONS = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "data"),
    ("2️⃣ BCoin_Push", "push"),
    ("3️⃣ Entry247 | Premium Signals 🇻🇳", "signals"),
    ("4️⃣ Entry247 | Premium Trader Talk 🇻🇳", "talk"),
    ("5️⃣ Tool Độc quyền, Free 100%", "tools"),
    ("6️⃣ Học và hiểu ( Video )", "videos"),
]

LINKS = {
    "data": "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880",
    "push": "https://t.me/Entry247_Push",
    "signals": "https://t.me/+6yN39gbr94c0Zjk1",
    "talk": "https://t.me/+eALbHBRF3xtlZWNl",
    "tools": "https://t.me/+ghRLRK6fHeYzYzE1",
    "videos": "https://t.me/+ghRLRK6fHeYzYzE1"
}

def main_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data)] for text, data in BUTTONS])

# ===== HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=main_menu())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data in LINKS:
        await query.edit_message_text(
            f"""🔗 *Tài nguyên bạn chọn:*

👉 {LINKS[query.data]}

📘 *Hướng dẫn sử dụng:*
- Truy cập link trên để xem nội dung cập nhật mỗi ngày.
- Nếu chưa truy cập được, kiểm tra quyền truy cập hoặc nhắn hỗ trợ.""",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Quay lại menu chính", callback_data="back")]]),
            parse_mode="Markdown"
        )
    elif query.data == "back":
        await query.edit_message_text(WELCOME_MESSAGE, reply_markup=main_menu())

# ===== FLASK ROUTES =====
@app.route("/", methods=["GET"])
def root():
    return "✅ Entry247 Bot is live!"

@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_data().decode("utf-8")
    await bot_app._update(data)
    return "ok"

# ===== CHẠY BOT =====
async def run_bot():
    global bot_app
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(handle_button))

    await bot_app.initialize()
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    await bot_app.start()
    print(f"🚀 Webhook set tại: {WEBHOOK_URL}")

# ===== CHẠY FLASK =====
if __name__ == "__main__":
    import threading

    threading.Thread(target=lambda: asyncio.run(run_bot())).start()
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask server chạy tại cổng {port}")
    app.run(host="0.0.0.0", port=port)

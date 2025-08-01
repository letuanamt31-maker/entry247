import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from flask import Flask, request
import asyncio

# === Bot Token ===
TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

# === Welcome Message ===
WELCOME_MESSAGE = """👋 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập  
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính dưới đây:
"""

# === Main Buttons ===
BUTTONS = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "data"),
    ("2️⃣ BCoin_Push", "push"),
    ("3️⃣ Entry247 | Premium Signals 🇻🇳", "signals"),
    ("4️⃣ Entry247 | Premium Trader Talk 🇻🇳", "talk"),
    ("5️⃣ Tool Độc quyền, Free 100%", "tools"),
    ("6️⃣ Học và hiểu ( Video )", "videos"),
]

# === Resource Links ===
LINKS = {
    "data": "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880",
    "push": "https://t.me/Entry247_Push",
    "signals": "https://t.me/+6yN39gbr94c0Zjk1",
    "talk": "https://t.me/+eALbHBRF3xtlZWNl",
    "tools": "https://t.me/+ghRLRK6fHeYzYzE1",
    "videos": "https://t.me/+ghRLRK6fHeYzYzE1"
}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=data)] for text, data in BUTTONS
    ])

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=main_menu())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data in LINKS:
        link = LINKS[query.data]
        text = f"""🔗 *Tài nguyên bạn chọn:*

👉 {link}

📘 *Hướng dẫn sử dụng:*
- Truy cập link trên để xem nội dung cập nhật mỗi ngày.
- Nếu chưa truy cập được, kiểm tra quyền truy cập hoặc nhắn hỗ trợ.
"""
        keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu chính", callback_data="back")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "back":
        await query.edit_message_text(WELCOME_MESSAGE, reply_markup=main_menu())

# === Flask App ===
app_flask = Flask(__name__)
application = None  # Telegram bot app, sẽ được gán sau

@app_flask.route("/webhook", methods=["POST"])
def webhook():
    request_data = request.get_data(as_text=True)
    asyncio.run(application.update_queue.put(request_data))
    return "ok"

# === Main Function ===
async def main():
    global application
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button))

    # Đặt webhook URL (tự lấy từ biến môi trường)
    external_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not external_url:
        raise ValueError("⚠️ Thiếu biến môi trường RENDER_EXTERNAL_URL")

    webhook_url = f"{external_url}webhook"
    await application.bot.set_webhook(webhook_url)
    print(f"✅ Webhook đã được đặt tại: {webhook_url}")

    # Không dùng polling nữa
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # Cần thiết để xử lý queue
    print("🤖 Entry247 Bot đang chạy qua Webhook!")

if __name__ == '__main__':
    import threading
    import os

    # Chạy Telegram bot trong luồng phụ
    thread = threading.Thread(target=lambda: asyncio.run(main()))
    thread.start()

    # Chạy Flask HTTP server trên cổng 10000
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

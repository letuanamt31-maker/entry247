from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import threading
import logging

# Telegram Bot Token
TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

# Logger
logging.basicConfig(level=logging.INFO)

# Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Entry247 Bot đang hoạt động!"

# Tin nhắn chào
WELCOME_MSG = """
😉😌😍🥰😉😌😇🙂 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
<b>Entry247 | Premium Signals 🇻🇳</b>

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

# Tạo bàn phím
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Dữ liệu Bot Update 24/24", url="https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880")],
        [InlineKeyboardButton("📡 BCoin_Push (Báo tín hiệu)", url="https://t.me/Entry247_Push")],
        [InlineKeyboardButton("📈 Premium Signals (Call lệnh)", url="https://t.me/+6yN39gbr94c0Zjk1")],
        [InlineKeyboardButton("💬 Premium Trader Talk", url="https://t.me/+eALbHBRF3xtlZWNl")],
        [InlineKeyboardButton("🛠 Tool độc quyền FREE", callback_data="tools")],
        [InlineKeyboardButton("🎥 Học và Hiểu (Video)", callback_data="learning")],
        [InlineKeyboardButton("📞 Liên hệ Admin", url="https://t.me/Entry247")]
    ])

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_MSG,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# Hàm chạy bot
import asyncio

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_telegram = ApplicationBuilder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    print("🤖 Bot Telegram đang chạy...")
    app_telegram.run_polling()

# Main
if __name__ == "__main__":
    # Bot chạy trong thread riêng
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Flask chạy trên PORT 10000
    app.run(host="0.0.0.0", port=10000)

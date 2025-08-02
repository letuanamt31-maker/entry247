from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
import logging
import threading

# TOKEN bot
TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

# Log
logging.basicConfig(level=logging.INFO)

# Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Entry247 Bot đang hoạt động!"

# Nội dung
WELCOME_MESSAGE = """
😉😌😍🥰😉😌😇🙂 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
<b>Entry247 | Premium Signals 🇻🇳</b>

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

# Bàn phím nút
def build_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Dữ liệu Bot Update 24/24", url="https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880#gid=247967880")],
        [InlineKeyboardButton("📡 BCoin_Push (Báo tín hiệu)", url="https://t.me/Entry247_Push")],
        [InlineKeyboardButton("📈 Premium Signals (Call lệnh)", url="https://t.me/+6yN39gbr94c0Zjk1")],
        [InlineKeyboardButton("💬 Premium Trader Talk", url="https://t.me/+eALbHBRF3xtlZWNl")],
        [InlineKeyboardButton("🛠 Tool độc quyền FREE", callback_data='tools')],
        [InlineKeyboardButton("🎥 Học và Hiểu (Video)", callback_data='learning')],
        [InlineKeyboardButton("📞 Liên hệ Admin", url="https://t.me/Entry247")]
    ])

# Xử lý /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=build_keyboard(),
        parse_mode="HTML"
    )

# Chạy bot trong luồng riêng
def run_bot():
    asyncio.run(_run_bot())

async def _run_bot():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    print("🤖 Bot đang chạy...")
    await application.run_polling()

# Khởi chạy Flask và bot
if __name__ == "__main__":
    # Bot chạy trong thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Flask chạy trên cổng 10000
    app.run(host="0.0.0.0", port=10000)

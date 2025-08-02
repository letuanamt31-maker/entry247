# entry247_bot.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from flask import Flask
import threading
import asyncio
import nest_asyncio

nest_asyncio.apply()

# ====== Config ======
TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

WELCOME_MESSAGE = """
😉😌😍🥰😉😌😇🙂 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng , dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢

(Ấn vào từng mục để xem chi tiết 👇)
"""

SECTIONS = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880#gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Trader Talk", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc Quyền", "https://t.me/Entry247_Push"),
    ("6️⃣ Học & Hiểu (Video)", "https://t.me/Entry247_Push")
]

# ====== Handlers ======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(text, callback_data=f"main_{i}")]
        for i, (text, _) in enumerate(SECTIONS)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("main_"):
        index = int(data.split("_")[1])
        title, link = SECTIONS[index]
        buttons = [
            [InlineKeyboardButton("🔗 Xem hướng dẫn", url=link)],
            [InlineKeyboardButton("🔙 Trở lại", callback_data="back")]
        ]
        await query.edit_message_text(
            f"📌 *{title}*", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown"
        )
    elif data == "back":
        keyboard = [
            [InlineKeyboardButton(text, callback_data=f"main_{i}")]
            for i, (text, _) in enumerate(SECTIONS)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(WELCOME_MESSAGE, reply_markup=reply_markup)

# ====== Bot + Flask Setup ======

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return '🌐 Flask giữ bot luôn sống...'

async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Bot Telegram đang chạy...")
    await app.run_polling()

def start_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# ====== Main Start ======

if __name__ == "__main__":
    threading.Thread(target=start_flask).start()
    asyncio.run(run_bot())

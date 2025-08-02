from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import threading

BOT_TOKEN = '7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4'

app_flask = Flask(__name__)
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

# ===================== FLASK =====================
@app_flask.route("/")
def index():
    return "✅ Bot is running on Render!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

# ===================== TELEGRAM =====================

WELCOME_TEXT = """🎯 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập Entry247 | Premium Signals 🇻🇳
"""

MENU = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/..."),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc quyền", "https://t.me/Entry247"),
    ("6️⃣ Học và Hiểu (Video)", "https://t.me/Entry247"),
]

def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"menu_{i}")]
        for i, (text, _) in enumerate(MENU)
    ])

def build_sub_keyboard(index):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Xem hướng dẫn", url=MENU[index][1])],
        [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=build_main_keyboard())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "main_menu":
        await query.edit_message_text(WELCOME_TEXT, reply_markup=build_main_keyboard())
    elif query.data.startswith("menu_"):
        index = int(query.data.split("_")[1])
        await query.edit_message_text(
            f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index)
        )

# ===================== MAIN =====================

if __name__ == "__main__":
    # Start Flask server in background
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start Telegram bot (this keeps main thread alive)
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))

    print("🚀 Starting Telegram bot polling...")
    app_telegram.run_polling()

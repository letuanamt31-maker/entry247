from flask import Flask
from threading import Thread
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

BOT_TOKEN = '7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4'

app_flask = Flask(__name__)
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

# ===================== BOT HANDLERS =========================

WELCOME_TEXT = """😉😌😍🥰😉😌😇🙂 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

MENU = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880#gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc quyền", "https://t.me/Entry247"),
    ("6️⃣ Học và Hiểu (Video)", "https://t.me/Entry247"),
]

def build_main_keyboard():
    keyboard = [[InlineKeyboardButton(text, callback_data=f"menu_{i}")] for i, (text, _) in enumerate(MENU)]
    return InlineKeyboardMarkup(keyboard)

def build_sub_keyboard(index):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Xem hướng dẫn", url=MENU[index][1])],
        [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=build_main_keyboard())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        await query.edit_message_text(WELCOME_TEXT, reply_markup=build_main_keyboard())
    elif query.data.startswith("menu_"):
        index = int(query.data.split("_")[1])
        await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))

# =============== ROUTES FLASK ================

@app_flask.route("/")
def home():
    return "🤖 Entry247 Bot is alive!"

# =============== RUN BOT ASYNC ===============

async def run_bot():
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_button))
    print("🤖 Bot đang khởi chạy...")
    await app_telegram.run_polling()

def start_bot_thread():
    asyncio.run

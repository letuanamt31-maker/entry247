from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
import os

BOT_TOKEN = '7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4'
WEBHOOK_DOMAIN = 'https://entry247.onrender.com'  # ⚠️ Thay đúng tên miền Render của bạn
WEBHOOK_PATH = f"/{BOT_TOKEN}"

app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

WELCOME_TEXT = """🎯 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập Entry247 | Premium Signals 🇻🇳
"""

MENU = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc quyền", "https://t.me/Entry247"),
    ("6️⃣ Học và Hiểu (Video)", "https://t.me/Entry247")
]

def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"menu_{i}")]
        for i, (text, _) in enumerate(MENU)
    ])

def build_sub_keyboard(index):
    if index == 0:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Xem dữ liệu", url=MENU[index][1])],
            [InlineKeyboardButton("📺 Hướng dẫn đọc số liệu", callback_data="coming_soon")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index in [1, 2, 3]:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 Xin vào nhóm", url=MENU[index][1])],
            [InlineKeyboardButton("📺 Tìm hiểu nhóm", callback_data="coming_soon")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index == 4:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚧 Entry247 đang hoàn thiện. Sẽ public Free 100% trong Premium", callback_data="no_action")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index == 5:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 Đi đúng từ đầu", callback_data="video_start")],
            [InlineKeyboardButton("🚫 Biết để tránh", callback_data="video_trap")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=build_main_keyboard())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "main_menu":
        await query.edit_message_text(WELCOME_TEXT, reply_markup=build_main_keyboard())

    elif data.startswith("menu_"):
        index = int(data.split("_")[1])
        await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))

    elif data == "video_start":
        await query.edit_message_text("🎯 Video 'Đi đúng từ đầu' sẽ được bổ sung sau.", reply_markup=build_sub_keyboard(5))

    elif data == "video_trap":
        await query.edit_message_text("🚫 Video 'Biết để tránh' sẽ được bổ sung sau.", reply_markup=build_sub_keyboard(5))

    elif data == "coming_soon":
        await query.edit_message_text("📺 Video sẽ được bổ sung sau.", reply_markup=build_sub_keyboard(0))

    elif data == "no_action":
        await query.answer("🚧 Tính năng đang phát triển", show_alert=True)

# =============== Webhook Flask Handler ===============
@app.route("/")
def home():
    return "✅ Entry247 Webhook Bot Running!"

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

if __name__ == '__main__':
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_buttons))

    print("🚀 Setting webhook...")
    asyncio.run(application.bot.set_webhook(url=WEBHOOK_DOMAIN + WEBHOOK_PATH))

    print("🌐 Starting Flask app...")
    app.run(host="0.0.0.0", port=10000)

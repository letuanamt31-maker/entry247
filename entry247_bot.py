import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
import threading

TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

main_message = """😉😌😍🥰😉😌😇🙂 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
*Entry247 | Premium Signals 🇻🇳*

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng , dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

buttons = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "1"),
    ("2️⃣ BCoin_Push", "2"),
    ("3️⃣ Premium Signals", "3"),
    ("4️⃣ Trader Talk", "4"),
    ("5️⃣ Tool độc quyền", "5"),
    ("6️⃣ Video học & hiểu", "6"),
]

resources = {
    "1": "👉📄 Tại đây: https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880",
    "2": "👉 https://t.me/Entry247_Push",
    "3": "👉 https://t.me/+6yN39gbr94c0Zjk1",
    "4": "👉 https://t.me/+eALbHBRF3xtlZWNl",
    "5": "✅ Tool độc quyền nhóm Entry247\n\nBạn có ý tưởng gì không? Gửi cho @Entry247",
    "6": "🎥 Đang hoàn thành các video:\n- Đi đúng từ đầu 🤨\n- Né bẫy thị trường 🤨\n- Sử lý lỗi khi vào sai trends 💡",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(text, callback_data=f"main_{data}")] for text, data in buttons
    ]
    await update.message.reply_text(
        main_message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("main_"):
        key = query.data.split("_")[1]
        content = f"{resources[key]}\n\nChọn thao tác bên dưới 👇"
        keyboard = [
            [
                InlineKeyboardButton("📘 Xem hướng dẫn", url=resources.get(key, "#")),
                InlineKeyboardButton("🔙 Trở lại", callback_data="back")
            ]
        ]
        await query.edit_message_text(
            text=content,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton(text, callback_data=f"main_{data}")] for text, data in buttons
        ]
        await query.edit_message_text(
            text=main_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    await app.initialize()
    await app.start()
    print("🤖 Bot Telegram đang chạy...")
    await app.updater.start_polling()
    await app.updater.idle()


# Flask để giữ server sống
flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return "🌐 Flask giữ bot luôn sống..."


if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_bot())).start()
    flask_app.run(host="0.0.0.0", port=10000)

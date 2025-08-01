from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Nội dung tin nhắn chính
WELCOME_MESSAGE = """🚀 Xin chào các thành viên Entry247!

Chúc mừng bạn đã gia nhập Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính:
"""

BUTTONS = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Entry247 | Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Entry247 | Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc quyền, Free 100%", "https://t.me/+ghRLRK6fHeYzYzE1"),
    ("6️⃣ Học và hiểu (Video)", "https://t.me/+ghRLRK6fHeYzYzE1")
]

GUIDE_TEXT = """📘 Hướng dẫn sử dụng bot:

1️⃣ Nhấn vào các nút để truy cập tài nguyên.

2️⃣ Sau khi xem xong, bạn có thể nhấn 🔙 "Quay lại" để trở lại menu chính.

💬 Mọi thắc mắc vui lòng liên hệ admin hỗ trợ.
"""

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text, url=link)] for text, link in BUTTONS]
    keyboard.append([InlineKeyboardButton("📘 Xem hướng dẫn", callback_data="show_guide")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

# Xử lý callback từ nút bấm
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "show_guide":
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Quay lại", callback_data="back_to_main")]
        ])
        await query.edit_message_text(text=GUIDE_TEXT, reply_markup=reply_markup)

    elif query.data == "back_to_main":
        keyboard = [[InlineKeyboardButton(text, url=link)] for text, link in BUTTONS]
        keyboard.append([InlineKeyboardButton("📘 Xem hướng dẫn", callback_data="show_guide")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=WELCOME_MESSAGE, reply_markup=reply_markup)

# Main
if __name__ == '__main__':
    import os

    # ⚠️ Lưu ý: KHÔNG để token bot công khai khi triển khai thật
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Entry247 Bot đang chạy...")
    app.run_polling()

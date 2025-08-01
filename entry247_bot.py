from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

WELCOME_MESSAGE = """🟢 Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập  
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

📌 Bạn có quyền truy cập vào 6 tài nguyên chính dưới đây:
"""

BUTTONS = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "data"),
    ("2️⃣ BCoin_Push", "push"),
    ("3️⃣ Entry247 | Premium Signals 🇻🇳", "signals"),
    ("4️⃣ Entry247 | Premium Trader Talk 🇻🇳", "talk"),
    ("5️⃣ Tool Độc quyền, Free 100%", "tool"),
    ("6️⃣ Học và hiểu ( Video )", "video"),
]

RESOURCES = {
    "data": "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880",
    "push": "https://t.me/Entry247_Push",
    "signals": "https://t.me/+6yN39gbr94c0Zjk1",
    "talk": "https://t.me/+eALbHBRF3xtlZWNl",
    "tool": "https://t.me/+ghRLRK6fHeYzYzE1",
    "video": "https://t.me/+ghRLRK6fHeYzYzE1"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in BUTTONS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data in RESOURCES:
        # Gửi link kèm hướng dẫn sử dụng và nút "Quay lại"
        text = f"""📎 Đây là tài nguyên bạn chọn:

👉 {RESOURCES[query.data]}

📘 *Hướng dẫn sử dụng:*
- Truy cập link ở trên.
- Theo dõi nội dung cập nhật mỗi ngày.
- Chúc bạn giao dịch hiệu quả ✅"""

        keyboard = [[InlineKeyboardButton("⬅️ Quay lại menu chính", callback_data="back")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    
    elif query.data == "back":
        # Quay lại menu chính
        keyboard = [[InlineKeyboardButton(text, callback_data=data)] for text, data in BUTTONS]
        await query.edit_message_text(text=WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("🤖 Entry247 Bot đang chạy...")
    app.run_polling()

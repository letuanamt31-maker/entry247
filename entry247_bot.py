from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

WELCOME_MESSAGE = """Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
Entry247 | Premium Signals 🇻🇳

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

RESOURCES = {
    "data": {
        "label": "1️⃣ Kênh dữ liệu Update 24/24",
        "url": "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880",
        "desc": "📊 Đây là bảng dữ liệu cập nhật 24/24 với tín hiệu thị trường, phân tích dòng tiền, v.v."
    },
    "bcoin": {
        "label": "2️⃣ BCoin_Push",
        "url": "https://t.me/Entry247_Push",
        "desc": "📢 Kênh đẩy tín hiệu và cảnh báo realtime thị trường crypto."
    },
    "signal": {
        "label": "3️⃣ Entry247 | Premium Signals 🇻🇳",
        "url": "https://t.me/+6yN39gbr94c0Zjk1",
        "desc": "📈 Nơi chia sẻ tín hiệu giao dịch chất lượng mỗi ngày."
    },
    "talk": {
        "label": "4️⃣ Entry247 | Premium Trader Talk 🇻🇳",
        "url": "https://t.me/+eALbHBRF3xtlZWNl",
        "desc": "💬 Cộng đồng thảo luận chiến lược và chia sẻ kinh nghiệm."
    },
    "tool": {
        "label": "5️⃣ Tool Độc quyền, Free 100%",
        "url": "https://t.me/+ghRLRK6fHeYzYzE1",
        "desc": "🛠️ Bộ công cụ miễn phí hỗ trợ giao dịch thông minh."
    },
    "video": {
        "label": "6️⃣ Học và hiểu ( Video )",
        "url": "https://t.me/+ghRLRK6fHeYzYzE1",
        "desc": "🎥 Hướng dẫn bằng video, dễ hiểu, dễ áp dụng."
    }
}

# Gửi menu chính
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(info["label"], callback_data=f"open_{key}")]
        for key, info in RESOURCES.items()
    ]
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

# Xử lý nút
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back":
        await start(update, context)
        return

    if data.startswith("open_"):
        key = data.split("_")[1]
        resource = RESOURCES.get(key)
        if resource:
            keyboard = [
                [
                    InlineKeyboardButton("📘 Xem hướng dẫn", callback_data=f"help_{key}"),
                    InlineKeyboardButton("🔙 Quay lại", callback_data="back")
                ]
            ]
            await query.message.reply_text(f"🔗 {resource['url']}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("help_"):
        key = data.split("_")[1]
        desc = RESOURCES.get(key, {}).get("desc", "Không tìm thấy hướng dẫn.")
        await query.message.reply_text(desc)

# Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🤖 Entry247 Bot đang chạy...")
    app.run_polling()

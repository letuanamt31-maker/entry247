from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

WELCOME_MESSAGE = """Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

# Danh sách tài nguyên (key, text, url, mô tả hướng dẫn)
RESOURCES = {
    "data": {
        "label": "1️⃣ Kênh dữ liệu Update 24/24",
        "url": "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880",
        "desc": "📊 Đây là bảng dữ liệu cập nhật 24/24 bao gồm phân tích kỹ thuật, dòng tiền và tín hiệu."
    },
    "bcoin": {
        "label": "2️⃣ BCoin_Push",
        "url": "https://t.me/Entry247_Push",
        "desc": "📢 Kênh BCoin_Push gửi các cảnh báo, tín hiệu sớm và nhịp thị trường."
    },
    "signal": {
        "label": "3️⃣ Entry247 | Premium Signals 🇻🇳",
        "url": "https://t.me/+6yN39gbr94c0Zjk1",
        "desc": "📈 Nơi chia sẻ tín hiệu giao dịch chất lượng từ đội ngũ phân tích Entry247."
    },
    "talk": {
        "label": "4️⃣ Entry247 | Premium Trader Talk 🇻🇳",
        "url": "https://t.me/+eALbHBRF3xtlZWNl",
        "desc": "💬 Nhóm thảo luận chiến lược, kinh nghiệm giao dịch cùng cộng đồng Entry247."
    },
    "tool": {
        "label": "5️⃣ Tool Độc quyền, Free 100%",
        "url": "https://t.me/+ghRLRK6fHeYzYzE1",
        "desc": "🛠️ Bộ tool miễn phí dành riêng cho thành viên Entry247, hỗ trợ trade hiệu quả."
    },
    "video": {
        "label": "6️⃣ Học và hiểu ( Video )",
        "url": "https://t.me/+ghRLRK6fHeYzYzE1",
        "desc": "🎥 Video hướng dẫn từ cơ bản đến nâng cao giúp bạn hiểu sâu hơn về hệ thống."
    }
}

# Gửi menu chính
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for key, item in RESOURCES.items():
        keyboard.append([InlineKeyboardButton(item["label"], url=item["url"])])
        keyboard.append([
            InlineKeyboardButton("📘 Xem hướng dẫn", callback_data=f"help_{key}"),
            InlineKeyboardButton("🔙 Quay lại", callback_data="back")
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

# Xử lý callback từ button phụ
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back":
        await start(update, context)
    elif data.startswith("help_"):
        key = data.split("_")[1]
        if key in RESOURCES:
            await query.message.reply_text(RESOURCES[key]["desc"])
        else:
            await query.message.reply_text("❌ Không tìm thấy nội dung hướng dẫn.")

if __name__ == '__main__':
    TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("🤖 Entry247 Bot đang chạy...")
    app.run_polling()

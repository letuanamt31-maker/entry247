from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ======= TOKEN ==========
TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

# ======= NỘI DUNG CHÍNH =======
WELCOME_MESSAGE = """Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập 
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

RESOURCES = {
    "0": {
        "label": "1️⃣ Kênh dữ liệu Update 24/24",
        "url": "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880",
        "desc": "📊 Dữ liệu cập nhật 24/24 với phân tích kỹ thuật, dòng tiền và tín hiệu thị trường."
    },
    "1": {
        "label": "2️⃣ BCoin_Push",
        "url": "https://t.me/Entry247_Push",
        "desc": "📢 Kênh đẩy tín hiệu và cảnh báo realtime từ hệ thống Entry247."
    },
    "2": {
        "label": "3️⃣ Entry247 | Premium Signals 🇻🇳",
        "url": "https://t.me/+6yN39gbr94c0Zjk1",
        "desc": "📈 Tín hiệu giao dịch chất lượng cao, cập nhật thường xuyên trong ngày."
    },
    "3": {
        "label": "4️⃣ Entry247 | Premium Trader Talk 🇻🇳",
        "url": "https://t.me/+eALbHBRF3xtlZWNl",
        "desc": "💬 Cộng đồng thảo luận, chia sẻ kinh nghiệm giao dịch cùng nhau."
    },
    "4": {
        "label": "5️⃣ Tool Độc quyền, Free 100%",
        "url": "https://t.me/+ghRLRK6fHeYzYzE1",
        "desc": "🛠️ Các công cụ hỗ trợ giao dịch độc quyền, hoàn toàn miễn phí."
    },
    "5": {
        "label": "6️⃣ Học và hiểu ( Video )",
        "url": "https://t.me/+ghRLRK6fHeYzYzE1",
        "desc": "🎥 Video hướng dẫn dễ hiểu, từ cơ bản đến nâng cao."
    }
}

# ======= HIỂN THỊ MENU CHÍNH =======
async def show_main_menu(message):
    keyboard = [
        [InlineKeyboardButton(info["label"], callback_data=f"open_{key}")]
        for key, info in RESOURCES.items()
    ]
    await message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

# ======= LỆNH /START =======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await show_main_menu(update.message)

# ======= XỬ LÝ CALLBACK =======
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back":
        await show_main_menu(query.message)
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
            await query.message.reply_text(
                f"🔗 {resource['url']}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif data.startswith("help_"):
        key = data.split("_")[1]
        desc = RESOURCES.get(key, {}).get("desc", "❌ Không tìm thấy hướng dẫn.")
        await query.message.reply_text(desc)

# ======= MAIN =======
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🤖 Entry247 Bot đang chạy...")
    app.run_polling()

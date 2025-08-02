from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Hàm khởi đầu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_message = f"""
😉😌😍🥰😉😌😇🙂 Xin chào {user.full_name} 🚀

Chúc mừng bạn đã gia nhập Entry247 | Premium Signals 🇻🇳

✅ Nơi tổng hợp tín hiệu, dữ liệu và chiến lược giao dịch CHẤT lượng dành riêng cho trader nghiêm túc.

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính, chọn bên dưới để xem chi tiết:
"""
    keyboard = [
        [InlineKeyboardButton("📊 Dữ liệu 24/24", callback_data='du_lieu')],
        [InlineKeyboardButton("📡 BCoin_Push", callback_data='bcoin_push')],
        [InlineKeyboardButton("📈 CALL lệnh Premium", callback_data='premium_signals')],
        [InlineKeyboardButton("🗣 Trader Talk", callback_data='trader_talk')],
        [InlineKeyboardButton("🛠 Tool độc quyền", callback_data='tools')],
        [InlineKeyboardButton("🎓 Video học & hiểu", callback_data='video_hoc')],
        [InlineKeyboardButton("📌 Kiểm tra mục ghim", callback_data='ghim')],
        [InlineKeyboardButton("🆘 Góp ý & hỗ trợ", url='https://t.me/Entry247')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

# Xử lý callback
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    responses = {
        'du_lieu': """📊 *Kênh dữ liệu Update 24/24* từ BOT – Entry247

🔗 [Xem dữ liệu tại đây](https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880#gid=247967880)""",

        'bcoin_push': """📡 *BCoin_Push* – Tín hiệu Altcoin season, hành vi MM và nhiều nội dung thú vị khác

🔗 [Tham gia tại đây](https://t.me/Entry247_Push)""",

        'premium_signals': """📈 *Entry247 Premium Signals* – Nơi CALL lệnh chính xác, hỗ trợ vào lệnh đúng thời điểm!

🔗 [Vào nhóm](https://t.me/+6yN39gbr94c0Zjk1)""",

        'trader_talk': """🗣 *Trader Talk* – Thảo luận chiến lược, phân tích sâu & hỗ trợ cộng đồng ❤️

🔗 [Tham gia](https://t.me/+eALbHBRF3xtlZWNl)""",

        'tools': """🛠 *Tool độc quyền* – Miễn phí 100%

💡 Giúp nhận diện thị trường nhanh chóng & hiệu quả.

Bạn có ý tưởng? Gửi cho admin nhé 🕯""",

        'video_hoc': """🎓 *Video Học & Hiểu* (Đang hoàn thiện)

▶️ Đi đúng từ đầu 🤨  
▶️ Né bẫy thị trường 🤨  
▶️ Sửa lỗi vào sai trends 💡

📌 Đừng quên kiểm tra mục ghim nhé!""",

        'ghim': """📌 Kiểm tra mục Ghim trong nhóm để không bỏ lỡ chiến lược và video quan trọng!"""
    }

    data = query.data
    response = responses.get(data, "❗ Đã có lỗi xảy ra. Vui lòng thử lại.")
    await query.edit_message_text(response, parse_mode='Markdown', disable_web_page_preview=False)

# Chạy bot
if __name__ == '__main__':
    import os

    TOKEN = os.getenv("BOT_TOKEN") or "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("🤖 Entry247 Bot đang chạy...")
    app.run_polling()

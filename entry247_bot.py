from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import threading

BOT_TOKEN = '7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4'

app_flask = Flask(__name__)
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

@app_flask.route("/")
def index():
    return "✅ Bot is running on Render!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

# ==================== MENU ============================
MENU = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880#gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Altcoin Season Signals 🇻🇳", "https://t.me/+_T-rtdJDveRjMWRl"),
    ("6️⃣ Học và Hiểu (Video)", ""),
]

# =================== Bàn phím =========================
def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"menu_{i}")]
        for i, (text, _) in enumerate(MENU)
    ])

def build_sub_keyboard(index):
    if index == 0:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Xem dữ liệu", url=MENU[index][1])],
            [InlineKeyboardButton("📺 Hướng dẫn đọc số liệu", callback_data="guide_data")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index == 1:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Xin vào nhóm", url=MENU[index][1])],
            [InlineKeyboardButton("📺 Hướng dẫn đọc số liệu", callback_data="guide_bcoin")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index == 2:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Xin vào nhóm", url=MENU[index][1])],
            [InlineKeyboardButton("📺 Tìm hiểu nhóm", callback_data="info_group_3")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index == 3:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Xin vào nhóm", url=MENU[index][1])],
            [InlineKeyboardButton("📺 Tìm hiểu nhóm", callback_data="info_group_4")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index == 4:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Xin vào nhóm", url=MENU[index][1])],
            [InlineKeyboardButton("📺 Tìm hiểu nhóm", callback_data="info_group_5")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index == 5:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ Đi đúng từ đầu", callback_data="video_start_right")],
            [InlineKeyboardButton("❗ Biết để tránh", callback_data="video_avoid")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])

# =================== Lệnh /start ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_firstname = update.effective_user.first_name or "bạn"
    welcome_text = f"""🌟 Xin chào {user_firstname} 🚀

Chào mừng bạn tìm hiểu Entry247 Premium
Nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto , dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
📌 Mọi thông tin liên hệ và góp ý: Admin @Entry247
"""
    await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())

# ================ Xử lý nút nhấn ======================
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        user_firstname = query.from_user.first_name or "bạn"
        welcome_text = f"""🌟 Xin chào {user_firstname} 🚀

Chào mừng bạn tìm hiểu Entry247 Premium
Nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto , dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
📌 Mọi thông tin liên hệ và góp ý: Admin @Entry247
"""
        await query.edit_message_text(welcome_text, reply_markup=build_main_keyboard())

    elif query.data.startswith("menu_"):
        index = int(query.data.split("_")[1])
        await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))

    elif query.data == "guide_data":
        await query.message.reply_text("📺 Hướng dẫn đọc số liệu sẽ được bổ sung sau.")

    elif query.data == "guide_bcoin":
        # Gửi video từ file_id (sau khi bạn đã từng upload video này lên bot)
        file_id = "BAACAgUAAxkBAAIB1WZkYTGc4m-BKTIzqQnUj0AfkFL-AAIuCgAC9LUQV65omKa7ep5sNAQ"  # Cập nhật nếu cần
        await context.bot.send_video(chat_id=query.message.chat_id, video=BAACAgUAAxkBAAIBTWiTE_-7a-BlcLtoiOaR1j5vjNHNAAKZFgACyjqYVIZs7rD0n2xMNgQ, caption="📺 Hướng dẫn sử dụng nhóm BCoin")

    elif query.data == "info_group_3":
        await query.message.reply_text("📺 Tìm hiểu nhóm Premium Signals sẽ được bổ sung sau.")

    elif query.data == "info_group_4":
        await query.message.reply_text("📺 Tìm hiểu nhóm Trader Talk sẽ được bổ sung sau.")

    elif query.data == "info_group_5":
        await query.message.reply_text("📺 Tìm hiểu nhóm Altcoin Season sẽ được bổ sung sau.")

    elif query.data == "video_start_right":
        await query.message.reply_text("▶️ Video 'Đi đúng từ đầu' sẽ được bổ sung sau.")

    elif query.data == "video_avoid":
        await query.message.reply_text("❗ Video 'Biết để tránh' sẽ được bổ sung sau.")

# ============= Lấy file_id khi bạn gửi video ==========
async def save_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"🎥 File ID của video là:\n\n`{file_id}`", parse_mode="Markdown")

# ================= Khởi động bot =======================
if __name__ == "__main__":
    # Chạy Flask song song
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Handlers
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))
    app_telegram.add_handler(MessageHandler(filters.VIDEO, save_file_id))  # Nhận video và hiển thị file_id

    print("🚀 Starting Telegram bot polling...")
    app_telegram.run_polling()

from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import threading

BOT_TOKEN = '7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4'

app_flask = Flask(__name__)
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

@app_flask.route("/")
def index():
    return "✅ Bot is running on Render!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

WELCOME_TEXT = """Xin chào các thành viên Entry247 🚀

Bạn đang tìm hiểu và cũng đang tìm hiểu 
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅
Chúng tôi không thu bất kỳ khoản phí dịch vụ nào 
Hãy đăng ký cùng về team Entry247 nào !
🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

MENU = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880#gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc quyền", ""),
    ("6️⃣ Học và Hiểu (Video)", ""),
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
            [InlineKeyboardButton("🛠️ Entry247 đang hoàn thiện, sẽ public Free 100% trong Premium", callback_data="tool_info")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])
    elif index == 5:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ Đi đúng từ đầu", callback_data="video_start_right")],
            [InlineKeyboardButton("❗ Biết để tránh", callback_data="video_avoid")],
            [InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]
        ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=build_main_keyboard())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        await query.edit_message_text(WELCOME_TEXT, reply_markup=build_main_keyboard())
    elif query.data.startswith("menu_"):
        index = int(query.data.split("_")[1])
        await query.edit_message_text(
            f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index)
        )
    elif query.data == "guide_data":
        await query.message.reply_text("📺 Hướng dẫn đọc số liệu sẽ được bổ sung sau.")
    elif query.data == "guide_bcoin":
        await query.message.reply_text("📺 Hướng dẫn sử dụng nhóm Bcoin sẽ được bổ sung sau.")
    elif query.data == "info_group_3":
        await query.message.reply_text("📺 Tìm hiểu nhóm Premium Signals sẽ được bổ sung sau.")
    elif query.data == "info_group_4":
        await query.message.reply_text("📺 Tìm hiểu nhóm Trader Talk sẽ được bổ sung sau.")
    elif query.data == "tool_info":
        await query.message.reply_text("🛠️ Entry247 đang hoàn thiện, sẽ public Free 100% trong Premium.")
    elif query.data == "video_start_right":
        await query.message.reply_text("▶️ Video 'Đi đúng từ đầu' sẽ được bổ sung sau.")
    elif query.data == "video_avoid":
        await query.message.reply_text("❗ Video 'Biết để tránh' sẽ được bổ sung sau.")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))

    print("🚀 Starting Telegram bot polling...")
    app_telegram.run_polling()

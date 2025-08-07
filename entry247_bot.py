from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import threading
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======================= CONFIG ===========================
BOT_TOKEN = '7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4'
VIDEO_FILE_ID = "BAACAgUAAxkBAAIBTWiTE_-7a-BlcLtoiOaR1j5vjNHNAAKZFgACyjqYVIZs7rD0n2xMNgQ"
GOOGLE_SHEET_ID = "1fpBfphrqJEZYgV-2BZ_a9vHTxlXWLBe1feZJd_M7dlQ"

# ===================== FLASK SETUP ========================
app_flask = Flask(__name__)
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

@app_flask.route("/")
def index():
    return "✅ Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# =================== GOOGLE SHEET =========================
creds_json = os.getenv("GOOGLE_CREDS_JSON")
if not creds_json:
    raise ValueError("❌ GOOGLE_CREDS_JSON chưa được thiết lập hoặc rỗng!")

try:
    creds_dict = json.loads(creds_json)
except json.JSONDecodeError as e:
    raise ValueError(f"JSON sai cú pháp: {e}")

try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    print("✅ Kết nối Google Sheet thành công!")
except Exception as e:
    raise ValueError(f"Không kết nối được Google Sheet: {e}")

# ======================== MENU ============================
MENU = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880#gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Altcoin Season Signals 🇻🇳", "https://t.me/+_T-rtdJDveRjMWRl"),
    ("6️⃣ Học và Hiểu (Video)", "")
]

# ======================= KEYBOARD =========================
def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"menu_{i}")]
        for i, (text, _) in enumerate(MENU)
    ])

def build_sub_keyboard(index):
    buttons = []
    if index in [0, 1, 2, 3]:
        buttons.append([InlineKeyboardButton("🔗 Xin vào nhóm", url=MENU[index][1])])
        buttons.append([InlineKeyboardButton("📺 Hướng dẫn đọc số liệu", callback_data=f"guide_{index}")])
    elif index == 4:
        buttons.append([InlineKeyboardButton("Entr247 đang hoàn thiện", callback_data="info_group_5")])
    elif index == 5:
        buttons.append([
            InlineKeyboardButton("▶️ Đi đúng từ đầu", callback_data="video_start_right"),
            InlineKeyboardButton("❗ Biết để tránh", callback_data="video_avoid")
        ])
    buttons.append([InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

# =================== GHI USER VÀO SHEET ===================
def save_user(user):
    try:
        user_id = str(user.id)
        existing = sheet.col_values(1)
        if user_id not in existing:
            sheet.append_row([user_id, user.first_name or "", user.username or ""])
            print(f"✅ Ghi user {user_id} vào Google Sheet")
    except Exception as e:
        print(f"❌ Lỗi khi ghi user vào sheet: {e}")

# ================= XOÁ TIN NHẮN CŨ ========================
async def delete_old_messages(chat_id, context):
    message_ids = context.user_data.get("messages_to_delete", [])
    for msg_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            print(f"❌ Không thể xoá message {msg_id}: {e}")
    context.user_data["messages_to_delete"] = []

# ======================== /START ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    welcome_text = f"""🌟 Xin chào {user.first_name or 'bạn'} 🚀\n\nChào mừng bạn tìm hiểu Entry247 Premium\nNơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto , dành riêng cho những trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢\n📌 Mọi thông tin liên hệ và góp ý: Admin @Entry247"""
    msg = await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())
    context.user_data.setdefault("messages_to_delete", []).append(msg.message_id)

# ==================== BUTTON HANDLER ======================
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if query.data == "main_menu":
        await delete_old_messages(chat_id, context)
        user = query.from_user
        welcome_text = f"""🌟 Xin chào {user.first_name or 'bạn'} 🚀\n\nChào mừng bạn tìm hiểu Entry247 Premium\nNơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto , dành riêng cho những trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢\n📌 Mọi thông tin liên hệ và góp ý: Admin @Entry247"""
        msg = await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=build_main_keyboard())
        context.user_data.setdefault("messages_to_delete", []).append(msg.message_id)

    elif query.data.startswith("menu_"):
        index = int(query.data.split("_")[1])
        msg = await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))
        context.user_data.setdefault("messages_to_delete", []).append(msg.message_id)

    elif query.data.startswith("guide_"):
        msg = await context.bot.send_video(chat_id=chat_id, video=VIDEO_FILE_ID, caption="📺 Hướng dẫn sử dụng")
        context.user_data.setdefault("messages_to_delete", []).append(msg.message_id)

    elif query.data == "info_group_5":
        msg = await query.message.reply_text("📺 Altcoin Signals sẽ public Free 100% trong Premium.")
        context.user_data.setdefault("messages_to_delete", []).append(msg.message_id)

    elif query.data == "video_start_right":
        msg = await query.message.reply_text("▶️ Video 'Đi đúng từ đầu' sẽ được bổ sung sau.")
        context.user_data.setdefault("messages_to_delete", []).append(msg.message_id)

    elif query.data == "video_avoid":
        msg = await query.message.reply_text("❗ Video 'Biết để tránh' sẽ được bổ sung sau.")
        context.user_data.setdefault("messages_to_delete", []).append(msg.message_id)

# ==================== SAVE VIDEO FILE ID ==================
async def save_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        msg = await update.message.reply_text(f"🎥 File ID: `{file_id}`", parse_mode="Markdown")
        context.user_data.setdefault("messages_to_delete", []).append(msg.message_id)

# ========================= RUN ============================
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))
    app_telegram.add_handler(MessageHandler(filters.VIDEO, save_file_id))

    print("🚀 Bot is running...")
    app_telegram.run_polling()

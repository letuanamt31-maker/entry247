import os
import json
import base64
import threading
import logging
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ======================= Load .env =============================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIDEO_FILE_ID = os.getenv("VIDEO_FILE_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")  # Giải pháp base64

# ==================== Google Sheets ============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    if not GOOGLE_CREDS_B64:
        raise ValueError("GOOGLE_CREDS_B64 không tồn tại hoặc rỗng.")

    creds_bytes = base64.b64decode(GOOGLE_CREDS_B64)
    creds_path = Path("service_account.json")
    creds_path.write_bytes(creds_bytes)
    logger.info("✅ Đã giải mã service_account.json")

    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_file("service_account.json", scopes=scope)
    gc = gspread.authorize(credentials)

    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    sheet_users = spreadsheet.worksheet("Users")
    sheet_logs = spreadsheet.worksheet("Logs")

except Exception as e:
    logger.error(f"❌ Lỗi kết nối Google Sheet: {e}")
    raise Exception(f"❌ Lỗi kết nối Google Sheet: {e}")

# ==================== Flask App ===============================
app_flask = Flask(__name__)

@app_flask.route("/")
def index():
    return "✅ Entry247 bot đang chạy!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

# ==================== Telegram Bot ============================
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

MENU = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880#gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Altcoin Season Signals 🇻🇳", "https://t.me/+_T-rtdJDveRjMWRl"),
    ("6️⃣ Học và Hiểu (Video)", ""),
]

def build_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(text, callback_data=f"menu_{i}")]
        for i, (text, _) in enumerate(MENU)
    ])

def build_sub_keyboard(index):
    items = []
    if index in [0, 1, 2, 3, 4]:
        items.append([InlineKeyboardButton("🔗 Xem nội dung", url=MENU[index][1])])
    if index == 0:
        items.append([InlineKeyboardButton("📺 Hướng dẫn đọc số liệu", callback_data="guide_data")])
    elif index == 1:
        items.append([InlineKeyboardButton("📺 Hướng dẫn nhóm BCoin", callback_data="guide_bcoin")])
    elif index == 2:
        items.append([InlineKeyboardButton("📺 Premium Signals là gì?", callback_data="info_group_3")])
    elif index == 3:
        items.append([InlineKeyboardButton("📺 Tìm hiểu nhóm Trader", callback_data="info_group_4")])
    elif index == 4:
        items.append([InlineKeyboardButton("📺 Thông tin nhóm Altcoin", callback_data="info_group_5")])
    elif index == 5:
        items.extend([
            [InlineKeyboardButton("▶️ Đi đúng từ đầu", callback_data="video_start_right")],
            [InlineKeyboardButton("❗ Biết để tránh", callback_data="video_avoid")]
        ])
    items.append([InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")])
    return InlineKeyboardMarkup(items)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "bạn"
    username = user.username or ""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ghi user nếu chưa có
    users = sheet_users.get_all_records()
    if not any(str(user_id) == str(u["ID"]) for u in users):
        sheet_users.append_row([user_id, first_name, username, now])

    # Ghi log
    sheet_logs.append_row([now, user_id, "/start"])

    welcome_text = f"""🌟 Xin chào {first_name} 🚀

Chào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
📌 Mọi thông tin góp ý: @Entry247"""
    
    await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    data = query.data
    user_id = query.from_user.id
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if data == "main_menu":
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass
        await context.bot.send_message(
            chat_id=chat_id,
            text="🌟 Xin chào! Đây là menu chính:",
            reply_markup=build_main_keyboard()
        )
        sheet_logs.append_row([now, user_id, "Trở lại menu"])
    elif data.startswith("menu_"):
        index = int(data.split("_")[1])
        await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))
        sheet_logs.append_row([now, user_id, f"Xem: {MENU[index][0]}"])
    elif data == "guide_data":
        await query.message.reply_text("📺 Hướng dẫn đọc số liệu sẽ được bổ sung.")
    elif data == "guide_bcoin":
        if VIDEO_FILE_ID:
            await context.bot.send_video(chat_id=chat_id, video=VIDEO_FILE_ID, caption="📺 Hướng dẫn nhóm BCoin")
        else:
            await query.message.reply_text("⚠️ VIDEO_FILE_ID chưa được cấu hình.")
    elif data == "info_group_3":
        await query.message.reply_text("📺 Premium Signals sẽ được bổ sung.")
    elif data == "info_group_4":
        await query.message.reply_text("📺 Trader Talk sẽ được bổ sung.")
    elif data == "info_group_5":
        await query.message.reply_text("📺 Nhóm Altcoin Signals sẽ mở miễn phí cho Premium.")
    elif data == "video_start_right":
        await query.message.reply_text("▶️ Video 'Đi đúng từ đầu' sẽ được bổ sung.")
    elif data == "video_avoid":
        await query.message.reply_text("❗ Video 'Biết để tránh' sẽ được bổ sung.")

async def save_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"🎥 File ID của video là:\n\n`{file_id}`", parse_mode="Markdown")

# ==================== Start =====================
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))
    app_telegram.add_handler(MessageHandler(filters.VIDEO, save_file_id))
    logger.info("🚀 Bot Telegram đang chạy polling...")
    app_telegram.run_polling()

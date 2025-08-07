import os
import json
import base64
import logging
import threading
from flask import Flask
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import gspread
from google.oauth2.service_account import Credentials

# ============ Load .env =============
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_BASE64 = os.getenv("GOOGLE_CREDS_BASE64")

# ============ Giải mã và lưu file service_account.json ============
creds_path = "/tmp/service_account.json"
if GOOGLE_CREDS_BASE64:
    with open(creds_path, "wb") as f:
        f.write(base64.b64decode(GOOGLE_CREDS_BASE64))
    print("✅ Đã giải mã service_account.json")
else:
    raise Exception("❌ Thiếu GOOGLE_CREDS_BASE64")

# ============ Kết nối Google Sheet ============
try:
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)

    def get_or_create_worksheet(title, headers):
        try:
            ws = spreadsheet.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            ws = spreadsheet.add_worksheet(title=title, rows="100", cols="20")
            ws.append_row(headers)
        return ws

    sheet_users = get_or_create_worksheet("Users", ["ID", "Tên", "Username"])
    sheet_logs = get_or_create_worksheet("Logs", ["Hành động", "ID", "Tên", "Thời gian"])

    print("✅ Đã kết nối Google Sheets")
except Exception as e:
    logging.error(f"❌ Lỗi kết nối Google Sheet: {e}")
    raise Exception(f"❌ Lỗi kết nối Google Sheet: {e}")

# ============ Flask =================
app_flask = Flask(__name__)

@app_flask.route("/")
def index():
    return "✅ Entry247 bot đang chạy!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

# ============ Telegram ==============
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

MENU = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/..."),
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
    if index in range(5):
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
    uid = user.id
    name = user.full_name
    username = user.username or ""

    # Log người dùng mới
    existing_ids = [row[0] for row in sheet_users.get_all_values()[1:]]
    if str(uid) not in existing_ids:
        sheet_users.append_row([str(uid), name, username])

    # Ghi log hành động
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet_logs.append_row(["/start", str(uid), name, now])

    welcome_text = f"""🌟 Xin chào {user.first_name or "bạn"} 🚀

Chào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
📌 Mọi thông tin góp ý: @Entry247
"""
    await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    if query.data == "main_menu":
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass
        user_firstname = query.from_user.first_name or "bạn"
        welcome_text = f"""🌟 Xin chào {user_firstname} 🚀

Chào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
📌 Mọi thông tin góp ý: @Entry247
"""
        await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=build_main_keyboard())
    elif query.data.startswith("menu_"):
        index = int(query.data.split("_")[1])
        await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))
    elif query.data == "guide_data":
        await query.message.reply_text("📺 Hướng dẫn đọc số liệu sẽ được bổ sung.")
    elif query.data == "guide_bcoin":
        await query.message.reply_text("📺 Hướng dẫn nhóm BCoin sẽ được bổ sung.")
    elif query.data == "info_group_3":
        await query.message.reply_text("📺 Premium Signals là gì? sẽ được bổ sung.")
    elif query.data == "info_group_4":
        await query.message.reply_text("📺 Trader Talk sẽ được bổ sung.")
    elif query.data == "info_group_5":
        await query.message.reply_text("📺 Nhóm Altcoin Signals sẽ mở miễn phí cho Premium.")
    elif query.data == "video_start_right":
        await query.message.reply_text("▶️ Video 'Đi đúng từ đầu' sẽ được bổ sung.")
    elif query.data == "video_avoid":
        await query.message.reply_text("❗ Video 'Biết để tránh' sẽ được bổ sung.")

async def save_video_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"🎥 File ID của video là:\n\n`{file_id}`", parse_mode="Markdown")

# ============ Khởi động ============
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))
    app_telegram.add_handler(MessageHandler(filters.VIDEO, save_video_id))
    print("🚀 Bot đang chạy polling Telegram...")
    app_telegram.run_polling()

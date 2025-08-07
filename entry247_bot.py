# entry247_bot.py (phiên bản hoàn chỉnh)

import os
import base64
import threading
import logging
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import traceback

# ======================= Load .env =============================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
VIDEO_FILE_ID = os.getenv("VIDEO_FILE_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")
ADMIN_IDS = ["5128195334"]  # ID admin được phép dùng /broadcast

# ==================== Logging ============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Google Sheets ============================
try:
    creds_bytes = base64.b64decode(GOOGLE_CREDS_B64)
    creds_path = Path("service_account.json")
    creds_path.write_bytes(creds_bytes)

    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_file("service_account.json", scopes=scope)
    gc = gspread.authorize(credentials)

    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    sheet_users = spreadsheet.worksheet("Users")
    sheet_logs = spreadsheet.worksheet("Logs")
except Exception as e:
    logger.error(f"❌ Lỗi kết nối Google Sheet: {e}")
    raise

# ==================== Flask ===============================
app_flask = Flask(__name__)

@app_flask.route("/")
def index():
    return "✅ Entry247 bot đang chạy!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

# ==================== Telegram ============================
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

MENU = [
    ("Kênh dữ liệu Update 24/24", "https://docs.google.com/...", "📺 Hướng dẫn đọc số liệu"),
    ("BCoin_Push", "https://t.me/Entry247_Push", "📺 Hướng dẫn nhóm BCoin"),
    ("Premium Signals 🇻🇳", "https://t.me/+...", "📺 Premium Signals là gì?"),
    ("Premium Trader Talk 🇻🇳", "https://t.me/+...", "📺 Tìm hiểu nhóm Trader"),
    ("Altcoin Season Signals 🇻🇳", "https://t.me/+...", "📺 Thông tin nhóm Altcoin"),
    ("Học và Hiểu (Video)", None, None),
]

user_sent_messages = {}

def track_user_message(user_id, message_id):
    user_sent_messages.setdefault(user_id, []).append(message_id)

def build_main_keyboard():
    keyboard = [[InlineKeyboardButton(text, callback_data=f"menu_{i}")] for i, (text, _, _) in enumerate(MENU)]
    keyboard.append([
        InlineKeyboardButton("🔔 Bật cảnh báo đảo chiều", callback_data="optin"),
        InlineKeyboardButton("🔕 Tắt cảnh báo đảo chiều", callback_data="optout")
    ])
    return InlineKeyboardMarkup(keyboard)

def build_sub_keyboard(index):
    text, url, video_caption = MENU[index]
    items = []
    if url:
        items.append([InlineKeyboardButton("🔗 Xem nội dung", url=url)])
    if video_caption:
        items.append([InlineKeyboardButton(video_caption, callback_data=f"video_{index}")])
    if index == 5:
        items.extend([
            [InlineKeyboardButton("▶️ Đi đúng từ đầu", callback_data="video_start_right")],
            [InlineKeyboardButton("❗ Biết để tránh", callback_data="video_avoid")]
        ])
    items.append([InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")])
    return InlineKeyboardMarkup(items)

def update_user_optin(user_id, enabled):
    users = sheet_users.get_all_records()
    for idx, row in enumerate(users, start=2):
        if str(row["ID"]) == str(user_id):
            sheet_users.update_cell(idx, 5, "✅" if enabled else "❌")
            break

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "bạn"
    username = user.username or ""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    users = sheet_users.get_all_records()
    if not any(str(user_id) == str(u["ID"]) for u in users):
        sheet_users.append_row([user_id, first_name, username, now, "❌"])

    sheet_logs.append_row([now, user_id, "/start"])

    welcome_text = f"""🌟 Xin chào {first_name} 🚀\n\nChào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính\n📌 Góp ý: @Entry247"""
    msg = await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())
    track_user_message(user_id, msg.message_id)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if data == "optin":
        update_user_optin(user_id, True)
        await query.edit_message_text("✅ Cảnh báo đảo chiều : ON.", reply_markup=build_main_keyboard())
    elif data == "optout":
        update_user_optin(user_id, False)
        await query.edit_message_text("❌ Cảnh báo đảo chiều : OFF.", reply_markup=build_main_keyboard())
    elif data.startswith("menu_"):
        index = int(data.split("_")[1])
        await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))
        sheet_logs.append_row([now, user_id, f"Xem: {MENU[index][0]}"])
    elif data.startswith("video_"):
        index = int(data.split("_")[1])
        caption = MENU[index][2]
        await context.bot.send_message(chat_id=query.message.chat_id, text=caption or "📺 Video đang được cập nhật.")
    elif data == "video_start_right":
        await context.bot.send_message(chat_id=query.message.chat_id, text="▶️ Video 'Đi đúng từ đầu' sẽ được bổ sung.")
    elif data == "video_avoid":
        await context.bot.send_message(chat_id=query.message.chat_id, text="❗ Video 'Biết để tránh' sẽ được bổ sung.")
    elif data == "main_menu":
        await query.edit_message_text("🔙 Trở lại menu chính", reply_markup=build_main_keyboard())

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Dùng: /broadcast <nội dung> hoặc reply tin nhắn")
        return

    content = " ".join(context.args) if context.args else update.message.reply_to_message.text or ""
    video = update.message.reply_to_message.video if update.message.reply_to_message and update.message.reply_to_message.video else None
    image = update.message.reply_to_message.photo[-1] if update.message.reply_to_message and update.message.reply_to_message.photo else None

    users = sheet_users.get_all_records()
    count = 0
    for user in users:
        if user.get("Đăng ký nhận tin") == "✅":
            try:
                if video:
                    await context.bot.send_video(chat_id=int(user["ID"]), video=video.file_id, caption=content)
                elif image:
                    await context.bot.send_photo(chat_id=int(user["ID"]), photo=image.file_id, caption=content)
                else:
                    await context.bot.send_message(chat_id=int(user["ID"]), text=content)
                count += 1
            except Exception as e:
                logger.warning(f"❌ Không gửi được đến {user['ID']}: {e}")

    await update.message.reply_text(f"✅ Đã gửi đến {count} người dùng đang opt-in.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        return

    users = sheet_users.get_all_records()
    total = len(users)
    opted_in = sum(1 for u in users if u.get("Đăng ký nhận tin") == "✅")
    await update.message.reply_text(f"👥 Tổng người dùng: {total}\n🔔 Đang bật nhận tin: {opted_in}")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("broadcast", broadcast))
    app_telegram.add_handler(CommandHandler("stats", stats))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))
    app_telegram.add_error_handler(error_handler)

    logger.info("🚀 Bot Telegram đang chạy polling...")
    app_telegram.run_polling()

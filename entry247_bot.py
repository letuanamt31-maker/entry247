# entry247_bot.py (phiên bản hoàn chỉnh và tối ưu UI/UX)

import os
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
import traceback

# ======================= Load .env =============================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
VIDEO_FILE_ID = os.getenv("VIDEO_FILE_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")
ADMIN_IDS = ["5128195334"]

VIDEO_IDS = {
    0: os.getenv("VIDEO_ID_0"),
    1: os.getenv("VIDEO_ID_1"),
    2: os.getenv("VIDEO_ID_2"),
    3: os.getenv("VIDEO_ID_3"),
    4: os.getenv("VIDEO_ID_4"),
    5: os.getenv("VIDEO_ID_5"),
    "start_right": os.getenv("VIDEO_ID_START_RIGHT"),
    "avoid": os.getenv("VIDEO_ID_AVOID"),
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    creds_bytes = base64.b64decode(GOOGLE_CREDS_B64)
    creds_path = Path("service_account.json")
    creds_path.write_bytes(creds_bytes)
    credentials = Credentials.from_service_account_file("service_account.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    sheet_users = spreadsheet.worksheet("Users")
    sheet_logs = spreadsheet.worksheet("Logs")
except Exception as e:
    logger.error(f"❌ Lỗi kết nối Google Sheet: {e}")
    raise

app_flask = Flask(__name__)

@app_flask.route("/")
def index():
    return "✅ Entry247 bot đang chạy!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

MENU = [
    ("Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/...", "📺 Hướng dẫn đọc số liệu"),
    ("BCoin_Push", "https://t.me/Entry247_Push", "📺 Hướng dẫn nhóm BCoin"),
    ("Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1", "📺 Premium Signals giúp gì ?"),
    ("Premium Trader Talk 🇻🇳", "https://t.me/+X6ibaOa_ETVhNTY1", "📺 Tìm hiểu nhóm Trader"),
    ("Altcoin Season Signals 🇻🇳", "https://t.me/+_T-rtdJDveRjMWRl", "📺 Thông tin nhóm Altcoin"),
    ("Học và Hiểu (Video)", None, None),
]

user_sent_messages = {}

def track_user_message(user_id, message_id):
    user_sent_messages.setdefault(user_id, []).append(message_id)

def clear_old_messages(context, chat_id, user_id):
    if user_id in user_sent_messages:
        for mid in user_sent_messages[user_id]:
            try:
                context.bot.delete_message(chat_id=chat_id, message_id=mid)
            except:
                pass
        user_sent_messages[user_id] = []

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
    items.append([InlineKeyboardButton("⬅️ Quay lại", callback_data="main_menu")])
    return InlineKeyboardMarkup(items)

def update_user_optin(user_id, enabled):
    users = sheet_users.get_all_records()
    for idx, row in enumerate(users, start=2):
        if str(row["ID"]) == str(user_id):
            sheet_users.update_cell(idx, 5, "✅" if enabled else "❌")
            break

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
    clear_old_messages(context, update.message.chat_id, user_id)
    msg = await update.message.reply_text(
        f"🌟 Xin chào {first_name} 🚀\n\nChào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính\n📌 Góp ý: @Entry247",
        reply_markup=build_main_keyboard()
    )
    track_user_message(user_id, msg.message_id)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "bạn"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    clear_old_messages(context, chat_id, user_id)

    if data == "main_menu":
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"🌟 Xin chào {first_name} 🚀\n\nChào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính\n📌 Góp ý: @Entry247",
            reply_markup=build_main_keyboard()
        )
        track_user_message(user_id, msg.message_id)
        return

    if data.startswith("menu_"):
        index = int(data.split("_")[1])
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"🔹 {MENU[index][0]}",
            reply_markup=build_sub_keyboard(index)
        )
        track_user_message(user_id, msg.message_id)
        sheet_logs.append_row([now, user_id, f"Xem: {MENU[index][0]}"])
        return

    if data.startswith("video_"):
        key = data.split("_")[1]
        video_id = VIDEO_IDS.get(int(key)) if key.isdigit() else VIDEO_IDS.get(key)
        if video_id:
            msg = await context.bot.send_video(chat_id=chat_id, video=video_id)
        else:
            msg = await context.bot.send_message(chat_id=chat_id, text="Danh mục đang được hoàn thiện, sẽ sớm update tới các bạn 🔥")
        track_user_message(user_id, msg.message_id)
        back = await context.bot.send_message(chat_id=chat_id, text="⬅️ Quay lại", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Quay lại", callback_data="main_menu")]]))
        track_user_message(user_id, back.message_id)
        return

    if data == "optin":
        update_user_optin(user_id, True)
        msg = await context.bot.send_message(chat_id=chat_id, text="✅ Đã bật cảnh báo đảo chiều.", reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)
        return

    if data == "optout":
        update_user_optin(user_id, False)
        msg = await context.bot.send_message(chat_id=chat_id, text="❌ Đã tắt cảnh báo đảo chiều.", reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)
        return

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 Tính năng broadcast đang được phát triển.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Tính năng thống kê đang được phát triển.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

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

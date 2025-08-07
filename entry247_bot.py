from pathlib import Path

entry247_bot_code = """
import os
import json
import threading
from flask import Flask, request, abort
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ======================= Load .env =============================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIDEO_FILE_ID = os.getenv("VIDEO_FILE_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

# ==================== Google Sheets ============================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

sheet = None
worksheet_users = None
worksheet_logs = None

try:
    if not GOOGLE_CREDS_JSON:
        raise ValueError("GOOGLE_CREDS_JSON không tồn tại hoặc rỗng.")

    creds_dict = json.loads(GOOGLE_CREDS_JSON)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc = gspread.authorize(creds)

    if not SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID không được thiết lập trong .env")

    sheet = gc.open_by_key(SPREADSHEET_ID)

    # Ensure worksheets
    try:
        worksheet_users = sheet.worksheet("Users")
    except:
        worksheet_users = sheet.add_worksheet(title="Users", rows="1000", cols="5")
        worksheet_users.append_row(["ID", "Name", "Username", "First seen", "Last active"])

    try:
        worksheet_logs = sheet.worksheet("Logs")
    except:
        worksheet_logs = sheet.add_worksheet(title="Logs", rows="1000", cols="6")
        worksheet_logs.append_row(["Timestamp", "User ID", "Username", "Name", "Action", "Message"])

    print("✅ Đã kết nối Google Sheet")
except Exception as e:
    raise Exception(f"❌ Lỗi kết nối Google Sheet: {e}")

# ==================== Flask App ===============================
app_flask = Flask(__name__)

@app_flask.route("/")
def index():
    return "✅ Entry247 bot đang chạy!"

@app_flask.route("/admin/status")
def admin_status():
    token = request.args.get("token")
    if token != SECRET_TOKEN:
        abort(403)

    sheet_status = "✅ Google Sheets OK" if sheet else "❌ Không kết nối Google Sheets"
    return f"""
    ✅ Bot hoạt động<br>
    {sheet_status}<br>
    🔐 Admin xác thực OK
    """

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

def log_user(update: Update, action: str, message: str = ""):
    if not worksheet_users or not worksheet_logs:
        return

    user = update.effective_user
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    all_ids = [str(row[0]) for row in worksheet_users.get_all_values()[1:]]
    if str(user.id) not in all_ids:
        worksheet_users.append_row([str(user.id), user.full_name, user.username or "", now, now])
    else:
        cell = worksheet_users.find(str(user.id))
        worksheet_users.update_cell(cell.row, 5, now)  # Last active

    worksheet_logs.append_row([now, str(user.id), user.username or "", user.full_name, action, message or ""])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_firstname = update.effective_user.first_name or "bạn"
    welcome_text = f"""🌟 Xin chào {user_firstname} 🚀

Chào mừng bạn tìm hiểu Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
📌 Mọi thông tin góp ý: @Entry247
"""
    await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())
    log_user(update, "start")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    log_user(update, f"button:{query.data}")

    if query.data == "main_menu":
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass
        await context.bot.send_message(chat_id=chat_id, text="🌟 Menu chính", reply_markup=build_main_keyboard())
    elif query.data.startswith("menu_"):
        index = int(query.data.split("_")[1])
        await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))
    elif query.data == "guide_data":
        await query.message.reply_text("📺 Hướng dẫn đọc số liệu sẽ được bổ sung.")
    elif query.data == "guide_bcoin":
        if VIDEO_FILE_ID:
            await context.bot.send_video(chat_id=chat_id, video=VIDEO_FILE_ID, caption="📺 Hướng dẫn nhóm BCoin")
        else:
            await query.message.reply_text("⚠️ VIDEO_FILE_ID chưa được cấu hình.")
    elif query.data == "info_group_3":
        await query.message.reply_text("📺 Premium Signals sẽ được bổ sung.")
    elif query.data == "info_group_4":
        await query.message.reply_text("📺 Trader Talk sẽ được bổ sung.")
    elif query.data == "info_group_5":
        await query.message.reply_text("📺 Nhóm Altcoin Signals sẽ mở miễn phí cho Premium.")
    elif query.data == "video_start_right":
        await query.message.reply_text("▶️ Video 'Đi đúng từ đầu' sẽ được bổ sung.")
    elif query.data == "video_avoid":
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
    print("🚀 Bot đang chạy polling Telegram...")
    app_telegram.run_polling()
"""

path = Path("/mnt/data/entry247_bot.py")
path.write_text(entry247_bot_code.strip(), encoding="utf-8")
path.name

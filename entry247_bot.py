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
    ContextTypes, filters
)
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ======================= Load .env =============================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")

VIDEO_IDS = {
    0: os.getenv("VIDEO_ID_0"),
    1: os.getenv("VIDEO_ID_1"),
    2: os.getenv("VIDEO_ID_2"),
    3: os.getenv("VIDEO_ID_3"),
    4: os.getenv("VIDEO_ID_4"),
    5: os.getenv("VIDEO_ID_5")
}

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
    ("Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=1941100397#gid=1941100397", "📺 Hướng dẫn đọc số liệu"),
    ("BCoin_Push", "https://t.me/Entry247_Push", "📺 Tìm hiểu Bcoin (video)"),
    ("Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1", "📺 Premium Signals giúp gì ?"),
    ("Premium Trader Talk 🇻🇳", "https://t.me/+X6ibaOa_ETVhNTY1", "📺 Tìm hiểu nhóm Trader"),
    ("Altcoin Season Signals 🇻🇳", "https://t.me/+_T-rtdJDveRjMWRl", "📺 Thông tin nhóm Altcoin"),
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
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    data = query.data
    user_id = query.from_user.id
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id in user_sent_messages:
        for mid in user_sent_messages[user_id]:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=mid)
            except:
                pass
        user_sent_messages[user_id] = []

    if data == "main_menu":
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        welcome_text = f"""🌟 Xin chào {query.from_user.first_name or "bạn"} 🚀

          Chào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅

          🟢 Bạn có quyền truy cập vào 6 tài nguyên chính
          📌 Góp ý: @Entry247"""
        msg = await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)
        sheet_logs.append_row([now, user_id, "Trở lại menu"])

    elif data.startswith("menu_"):
        index = int(data.split("_")[1])
        msg = await context.bot.send_message(chat_id=chat_id, text=f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))
        track_user_message(user_id, msg.message_id)
        sheet_logs.append_row([now, user_id, f"Xem: {MENU[index][0]}"])

    elif data == "optin":
        update_user_optin(user_id, True)
        msg = await context.bot.send_message(chat_id=chat_id, text="✅ Nhận thông báo đảo chiều: ON.", reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)

    elif data == "optout":
        update_user_optin(user_id, False)
        msg = await context.bot.send_message(chat_id=chat_id, text="❌ Nhận thông báo đảo chiều: OFF.", reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)

    elif data.startswith("menu_"):
        index = int(data.split("_")[1])

    # Xoá message callback cũ để tránh đè nhau
    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    # Gửi lại menu phụ tương ứng
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"🔹 {MENU[index][0]}",
        reply_markup=build_sub_keyboard(index)
    )
        track_user_message(user_id, msg.message_id)
        sheet_logs.append_row([now, user_id, f"Xem: {MENU[index][0]}"])
                ])
            )
        else:
            msg = await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ Video chưa được cấu hình.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Trở lại", callback_data=f"menu_{index}")]
                ])
            )
        track_user_message(user_id, msg.message_id)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 Bạn không có quyền sử dụng lệnh này.")
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

# ======================= MAIN ========================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("broadcast", broadcast))
    app_telegram.add_handler(CommandHandler("stats", stats))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))

    logger.info("🚀 Bot Telegram đang chạy polling...")
    app_telegram.run_polling()

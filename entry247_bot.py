# entry247_bot.py (hoàn chỉnh với opt-in, broadcast, thống kê)

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
ADMIN_ID = int(os.getenv("ADMIN_ID", "5128195334"))

# ==================== Logging ============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Google Sheets ============================
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
    logger.info("✅ Kết nối Google Sheets thành công.")

except Exception as e:
    traceback.print_exc()
    logger.error(f"❌ Lỗi kết nối Google Sheet: {e}")
    raise

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
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit#gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Altcoin Season Signals 🇻🇳", "https://t.me/+_T-rtdJDveRjMWRl"),
    ("6️⃣ Học và Hiểu (Video)", "")
]

user_sent_messages = {}

def track_user_message(user_id, message_id):
    if user_id not in user_sent_messages:
        user_sent_messages[user_id] = []
    user_sent_messages[user_id].append(message_id)

def update_user_optin(user_id, enabled: bool):
    users = sheet_users.get_all_records()
    for idx, row in enumerate(users, start=2):
        if str(row["ID"]) == str(user_id):
            sheet_users.update_cell(idx, 5, "✅" if enabled else "❌")
            break

def build_main_keyboard():
    keyboard = [[InlineKeyboardButton(text, callback_data=f"menu_{i}")] for i, (text, _) in enumerate(MENU)]
    keyboard.append([
        InlineKeyboardButton("🔔 Bật cảnh báo đảo chiều", callback_data="optin"),
        InlineKeyboardButton("🔕 Tắt cảnh báo đảo chiều", callback_data="optout")
    ])
    return InlineKeyboardMarkup(keyboard)

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

    users = sheet_users.get_all_records()
    if not any(str(user_id) == str(u["ID"]) for u in users):
        sheet_users.append_row([user_id, first_name, username, now])

    sheet_logs.append_row([now, user_id, "/start"])

    welcome_text = f"""🌟 Xin chào {first_name} 🚀\n\nChào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢\n📌 Mọi thông tin góp ý: @Entry247"""
    msg = await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())
    track_user_message(user_id, msg.message_id)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    data = query.data
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "bạn"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if data == "main_menu":
        if user_id in user_sent_messages:
            for mid in user_sent_messages[user_id]:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=mid)
                except:
                    pass
            user_sent_messages[user_id] = []

        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

        welcome_text = f"""🌟 Xin chào {first_name} 🚀\n\nChào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢\n📌 Mọi thông tin góp ý: @Entry247"""
        msg = await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)
        sheet_logs.append_row([now, user_id, "Trở lại menu"])

    elif data.startswith("menu_"):
        index = int(data.split("_")[1])
        await query.edit_message_text(f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))
        sheet_logs.append_row([now, user_id, f"Xem: {MENU[index][0]}"])

    elif data == "optin":
        update_user_optin(user_id, True)
        await query.edit_message_text("✅ Nhận thông báo đào chiều sớm : ON.", reply_markup=build_main_keyboard())

    elif data == "optout":
        update_user_optin(user_id, False)
        await query.edit_message_text("❌ Nhận thông báo đào chiều sớm : OFF.", reply_markup=build_main_keyboard())

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")

    message_text = update.message.text_html or ""
    reply = update.message.reply_to_message
    users = sheet_users.get_all_records()
    count = 0

    for user in users:
        if user.get("Đăng ký nhận tin") == "✅":
            try:
                chat_id = int(user["ID"])
                if reply and reply.video:
                    await context.bot.send_video(chat_id=chat_id, video=reply.video.file_id, caption=message_text)
                elif reply and reply.photo:
                    await context.bot.send_photo(chat_id=chat_id, photo=reply.photo[-1].file_id, caption=message_text)
                else:
                    await context.bot.send_message(chat_id=chat_id, text=message_text)
                count += 1
            except Exception as e:
                logger.warning(f"❌ Không gửi được đến {user['ID']}: {e}")
    await update.message.reply_text(f"✅ Đã gửi đến {count} người dùng.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = sheet_users.get_all_records()
    total = len(users)
    yes = sum(1 for u in users if u.get("Đăng ký nhận tin") == "✅")
    no = total - yes
    await update.message.reply_text(f"📊 Thống kê:\n- Tổng người dùng: {total}\n- Đang nhận thông báo: {yes}\n- Đã tắt: {no}")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("broadcast", broadcast))
    app_telegram.add_handler(CommandHandler("stats", stats))
    app_telegram.add_handler(CallbackQueryHandler(handle_buttons))

    logger.info("🚀 Bot Telegram đang chạy polling...")
    app_telegram.run_polling()

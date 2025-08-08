# entry247_bot.py (final updated - hierarchical menus, back logic, delete old messages after showing new menu)

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
    ContextTypes
)
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ======================= Load .env =============================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")
# ADMIN_IDS: list of allowed admin IDs as strings; you can set ADMIN_ID env or edit here
ADMIN_IDS = [os.getenv("ADMIN_ID") or "5128195334"]

# VIDEO_IDS: map video_key -> telegram file_id (set these in .env as VIDEO_ID_0, VIDEO_ID_1, ...)
VIDEO_IDS = {
    "0": os.getenv("VIDEO_ID_0"),
    "1": os.getenv("VIDEO_ID_1"),
    "2": os.getenv("VIDEO_ID_2"),
    "3": os.getenv("VIDEO_ID_3"),
    "4": os.getenv("VIDEO_ID_4"),
    "5": os.getenv("VIDEO_ID_5"),
}

# ==================== Logging ============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== Google Sheets ============================
try:
    creds_bytes = base64.b64decode(GOOGLE_CREDS_B64)
    Path("service_account.json").write_bytes(creds_bytes)
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
    gc = gspread.authorize(creds)
    ss = gc.open_by_key(SPREADSHEET_ID)
    sheet_users = ss.worksheet("Users")
    sheet_logs = ss.worksheet("Logs")
except Exception as e:
    logger.error("❌ Lỗi kết nối Google Sheet: %s", e)
    raise

# ==================== Flask ===============================
app_flask = Flask(__name__)

@app_flask.route("/")
def index():
    return "✅ Entry247 bot đang chạy!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

# ==================== MENU (phân cấp) ======================
# Node: { "title": str, "url": str|None, "video_key": str|None, "children": [nodes] }
MENU_ROOT = {
    "title": "Entry247",
    "children": [
        {"title": "Kênh dữ liệu Update 24/24", "url": "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=1941100397#gid=1941100397", "video_key": "0", "children": []},
        {"title": "BCoin_Push", "url": "https://t.me/Entry247_Push", "video_key": "1", "children": [
            {"title": "Tìm hiểu thêm BCoin", "url": None, "video_key": None, "children": []}
        ]},
        {"title": "Premium Signals 🇻🇳", "url": "https://t.me/+6yN39gbr94c0Zjk1", "video_key": "2", "children": []},
        {"title": "Premium Trader Talk 🇻🇳", "url": "https://t.me/+X6ibaOa_ETVhNTY1", "video_key": "3", "children": []},
        {"title": "Altcoin Season Signals 🇻🇳", "url": "https://t.me/+_T-rtdJDveRjMWRl", "video_key": "4", "children": []},
        {"title": "Học và Hiểu (Video)", "url": None, "video_key": "5", "children": [
            {"title": "Đi đúng từ đầu", "url": None, "video_key": None, "children": []},
            {"title": "Biết để tránh", "url": None, "video_key": None, "children": []},
        ]},
    ]
}

# ==================== Helpers =============================
def get_node_by_path(path):
    """ path: '' or '0' or '1:0' -> returns node dict or None """
    if not path:
        return MENU_ROOT
    try:
        node = MENU_ROOT
        for p in path.split(":"):
            idx = int(p)
            node = node["children"][idx]
        return node
    except Exception:
        return None

def parent_path(path):
    if not path:
        return ""
    parts = path.split(":")
    if len(parts) <= 1:
        return ""
    return ":".join(parts[:-1])

def build_keyboard_for_node(path):
    node = get_node_by_path(path)
    if node is None:
        return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Trở lại", callback_data="main_menu")]])
    buttons = []
    # children
    for i, child in enumerate(node.get("children", [])):
        cb_path = (f"{path}:{i}" if path else str(i))
        buttons.append([InlineKeyboardButton(child["title"], callback_data=f"menu:{cb_path}")])
    # content buttons
    if node.get("url"):
        buttons.append([InlineKeyboardButton("🔗 Xem nội dung", url=node["url"])])
    if node.get("video_key"):
        buttons.append([InlineKeyboardButton("📺 Xem video", callback_data=f"video:{path}" if path else "video:")])
    # back button (to parent; root -> main_menu)
    parent = parent_path(path)
    back_cb = f"menu:{parent}" if parent else "main_menu"
    buttons.append([InlineKeyboardButton("⬅️ Trở lại", callback_data=back_cb)])
    return InlineKeyboardMarkup(buttons)

# per-user tracked message ids (so we can delete them)
user_sent_messages = {}  # user_id -> [message_id, ...]

def track_message(user_id, message_id):
    user_sent_messages.setdefault(user_id, []).append(message_id)

def delete_old_messages(bot, chat_id, user_id, keep_ids):
    """Delete all tracked messages for user except those in keep_ids."""
    mids = list(user_sent_messages.get(user_id, []))
    for mid in mids:
        if mid in keep_ids:
            continue
        try:
            bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception:
            pass
        # remove from tracked list
        try:
            user_sent_messages[user_id].remove(mid)
        except ValueError:
            pass

def build_main_keyboard():
    return build_keyboard_for_node("")

# ==================== Bot handlers ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "bạn"
    username = user.username or ""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        users = sheet_users.get_all_records()
        if not any(str(user_id) == str(u.get("ID")) for u in users):
            sheet_users.append_row([user_id, first_name, username, now, "❌"])
        sheet_logs.append_row([now, user_id, "/start"])
    except Exception:
        logger.warning("Warning: sheet write failed on /start")

    welcome_text = f"""🌟 Xin chào {first_name} 🚀

Chào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính
📌 Góp ý: @Entry247"""
    msg = await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())
    track_message(user_id, msg.message_id)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "bạn"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # === Trở về menu gốc (hiện menu trước, sau đó xóa cũ) ===
    if data in ("main_menu", "menu:"):
        msg = await context.bot.send_message(chat_id=chat_id, text="🔸 Menu chính", reply_markup=build_main_keyboard())
        track_message(user_id, msg.message_id)
        # delete all older messages except this menu
        delete_old_messages(context.bot, chat_id, user_id, keep_ids=[msg.message_id])
        try:
            sheet_logs.append_row([now, user_id, "Trở lại menu"])
        except Exception:
            pass
        return

    # === Điều hướng menu phân cấp ===
    if data.startswith("menu:"):
        path = data.split("menu:")[1]  # '' or '0' or '1:0'
        if path is None:
            path = ""
        node = get_node_by_path(path)
        if node is None:
            await context.bot.send_message(chat_id=chat_id, text="❌ Lỗi menu.")
            return

        # nếu không có url, video, children => đang hoàn thiện
        if not node.get("url") and not node.get("video_key") and not node.get("children"):
            msg = await context.bot.send_message(chat_id=chat_id, text="📢 Danh mục đang được hoàn thiện, sẽ sớm update tới các bạn 🔥")
            track_message(user_id, msg.message_id)
            delete_old_messages(context.bot, chat_id, user_id, keep_ids=[msg.message_id])
            try:
                sheet_logs.append_row([now, user_id, f"Xem: {node.get('title')} (đang hoàn thiện)"])
            except Exception:
                pass
            return

        # gửi submenu / content choices trước
        title = node.get("title", "Danh mục")
        msg = await context.bot.send_message(chat_id=chat_id, text=f"🔹 {title}", reply_markup=build_keyboard_for_node(path))
        track_message(user_id, msg.message_id)
        # sau đó xóa tin cũ (video, ảnh, text) trừ message vừa gửi
        delete_old_messages(context.bot, chat_id, user_id, keep_ids=[msg.message_id])
        try:
            sheet_logs.append_row([now, user_id, f"Xem: {title}"])
        except Exception:
            pass
        return

    # === Xem video ở node ===
    if data.startswith("video:"):
        path = data.split("video:")[1]  # '' or '0' etc
        if path is None:
            path = ""
        node = get_node_by_path(path)
        video_key = node.get("video_key") if node else None
        video_id = VIDEO_IDS.get(video_key) if video_key else None
        caption = node.get("title") if node else ""
        if video_id:
            msg = await context.bot.send_video(chat_id=chat_id, video=video_id, caption=caption)
            track_message(user_id, msg.message_id)
            try:
                sheet_logs.append_row([now, user_id, f"Xem video: {caption}"])
            except Exception:
                pass
        else:
            msg = await context.bot.send_message(chat_id=chat_id, text="⚠️ Video chưa được cấu hình.")
            track_message(user_id, msg.message_id)
            delete_old_messages(context.bot, chat_id, user_id, keep_ids=[msg.message_id])
        return

    # === optin / optout ===
    if data == "optin":
        try:
            users = sheet_users.get_all_records()
            for idx, row in enumerate(users, start=2):
                if str(row.get("ID")) == str(user_id):
                    sheet_users.update_cell(idx, 5, "✅")
                    break
        except Exception:
            pass
        msg = await context.bot.send_message(chat_id=chat_id, text="✅ Nhận thông báo đảo chiều: ON", reply_markup=build_main_keyboard())
        track_message(user_id, msg.message_id)
        delete_old_messages(context.bot, chat_id, user_id, keep_ids=[msg.message_id])
        return

    if data == "optout":
        try:
            users = sheet_users.get_all_records()
            for idx, row in enumerate(users, start=2):
                if str(row.get("ID")) == str(user_id):
                    sheet_users.update_cell(idx, 5, "❌")
                    break
        except Exception:
            pass
        msg = await context.bot.send_message(chat_id=chat_id, text="❌ Nhận thông báo đảo chiều: OFF", reply_markup=build_main_keyboard())
        track_message(user_id, msg.message_id)
        delete_old_messages(context.bot, chat_id, user_id, keep_ids=[msg.message_id])
        return

# ==================== Admin / utility commands =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 Bạn không có quyền sử dụng lệnh này.")
        return
    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Dùng: /broadcast <nội dung> hoặc reply tin nhắn")
        return
    content = " ".join(context.args) if context.args else (update.message.reply_to_message.text or "")
    video = update.message.reply_to_message.video if update.message.reply_to_message and update.message.reply_to_message.video else None
    image = update.message.reply_to_message.photo[-1] if update.message.reply_to_message and update.message.reply_to_message.photo else None

    try:
        users = sheet_users.get_all_records()
    except Exception:
        users = []
    count = 0
    for user in users:
        try:
            if user.get("Đăng ký nhận tin") != "✅":
                continue
            chat = int(user.get("ID"))
            if video:
                await context.bot.send_video(chat_id=chat, video=video.file_id, caption=content)
            elif image:
                await context.bot.send_photo(chat_id=chat, photo=image.file_id, caption=content)
            else:
                await context.bot.send_message(chat_id=chat, text=content)
            count += 1
        except Exception as e:
            logger.warning("broadcast to %s failed: %s", user.get("ID"), e)
    await update.message.reply_text(f"✅ Đã gửi đến {count} người dùng đang opt-in.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_IDS:
        return
    try:
        users = sheet_users.get_all_records()
    except Exception:
        users = []
    total = len(users)
    opted_in = sum(1 for u in users if u.get("Đăng ký nhận tin") == "✅")
    await update.message.reply_text(f"👥 Tổng người dùng: {total}\n🔔 Đang bật nhận tin: {opted_in}")

# global error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    try:
        if hasattr(update, "message") and update.message:
            await update.message.reply_text("❌ Đã xảy ra lỗi, thử lại sau.")
    except Exception:
        pass

# ==================== Start bot ==============================
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_error_handler(error_handler)

    logger.info("🚀 Bot Telegram đang chạy polling...")
    app.run_polling()

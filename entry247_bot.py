import os
import sys
import json
import logging

from flask import Flask, request, abort
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --- Kiểm tra môi trường để tránh chạy bot nhiều nơi ---
IS_RENDER = os.environ.get("RENDER") == "true" or "onrender.com" in os.environ.get("RENDER_EXTERNAL_URL", "")
if not IS_RENDER:
    print("❌ Bot chỉ chạy trên Render để tránh conflict polling.")
    sys.exit(0)

# --- Env Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "entry247")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

# --- Kết nối Google Sheets ---
sheet = None
try:
    if GOOGLE_CREDS_JSON:
        creds_dict = json.loads(GOOGLE_CREDS_JSON)
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(SPREADSHEET_ID)
        logging.info("✅ Đã kết nối Google Sheet")
    else:
        logging.warning("⚠️ GOOGLE_CREDS_JSON không được cấu hình")
except Exception as e:
    logging.error(f"❌ Lỗi kết nối Google Sheets: {e}")

# --- Flask App ---
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

# --- Handlers Telegram Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Đây là bot Entry247.\nGõ /help để xem hướng dẫn.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 Hướng dẫn sử dụng bot:\n/start - Bắt đầu\n/help - Trợ giúp")

# --- Khởi tạo Telegram Bot ---
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# --- Chạy polling khi chạy bằng Python (Render) ---
if __name__ == "__main__":
    if IS_RENDER:
        logging.info("🚀 Khởi động bot Telegram (Render)...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    else:
        logging.info("⛔ Không khởi động polling ngoài môi trường Render.")

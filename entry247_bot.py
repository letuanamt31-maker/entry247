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
SPREADSHEET_NAME = "Entry247_Users"

# ===================== FLASK SETUP ========================
app_flask = Flask(__name__)
app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()

@app_flask.route("/")
def index():
    return "✅ Bot is running on Render!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=10000)

# =================== GOOGLE SHEET =========================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1

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
    except Exception as e:
        print(f"Error saving user: {e}")

# ======================== GLOBAL ==========================
last_video_message = {}

# ======================== /START ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)
    welcome_text = f"""🌟 Xin chào {user.first_name or 'bạn'} 🚀\n\nChào mừng bạn tìm hiểu Entry247 Premium\nNơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto , dành riêng cho những trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢\n📌 Mọi thông tin liên hệ và góp ý: Admin @Entry247"""
    await update.message.reply_text(welcome_text, reply_markup=build_main_keyboard())

# ==================== BUTTON HANDLER ======================
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if query.data == "main_menu":
        try:
            await context.bot.delete_m

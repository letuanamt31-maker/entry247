import asyncio
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

# Flask app để giữ bot sống trên Render
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ Entry247 Bot đang hoạt động."

# ===== Tin nhắn chào mừng =====
WELCOME_MESSAGE = """😉😌😍🥰😉😌😇🙂 Xin chào các thành viên *Entry247 🚀*

Chúc mừng bạn đã gia nhập  
*Entry247 | Premium Signals 🇻🇳*

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào *6 tài nguyên chính* 🟢
"""

# ===== Nội dung chi tiết của 6 phần =====
RESOURCES = {
    "data": {
        "title": "1️⃣ Kênh dữ liệu Update 24/24",
        "text": "👉📄 Tại đây:\nhttps://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880",
        "guide": "💡 *Hướng dẫn:* Vào link Google Sheet để xem dữ liệu cập nhật theo thời gian thực từ bot giao dịch."
    },
    "push": {
        "title": "2️⃣ BCoin_Push",
        "text": "👉 https://t.me/Entry247_Push",
        "guide": "💡 *Hướng dẫn:* Tham gia kênh để nhận tín hiệu đẩy giá, báo hiệu mùa Altcoin season, và nhiều insight khác."
    },
    "signals": {
        "title": "3️⃣ Entry247 | Premium Signals 🇻🇳",
        "text": "👉 https://t.me/+6yN39gbr94c0Zjk1",
        "guide": "💡 *Hướng dẫn:* Nhóm call lệnh chính — vào để nhận điểm vào/ra lệnh chất lượng mỗi ngày."
    },
    "talk": {
        "title": "4️⃣ Entry247 | Premium Trader Talk 🇻🇳",
        "text": "👉 https://t.me/+eALbHBRF3xtlZWNl",
        "guide": "💡 *Hướng dẫn:* Thảo luận chiến lược, phân tích sâu, hỗ trợ từ cộng đồng AE Entry247."
    },
    "tools": {
        "title": "5️⃣ Tool Độc quyền, Free 100%",
        "text": "🛠 Mình sẽ làm tốt các công cụ nhận diện thị trường để AE nhóm tối ưu vào lệnh.",
        "guide": "💡 *Hướng dẫn:* Nếu có ý tưởng, hãy đề xuất — công cụ sẽ được phát triển theo nhu cầu thực tế."
    },
    "videos": {
        "title": "6️⃣ Học và hiểu (Video)",
        "text": "🎥 Nội dung đang hoàn thành:\n- Đi đúng từ đầu 🤨\n- Hiểu bẫy để né 🤨\n- Xử lý lỗi khi vào sai trends 💡",
        "guide": "💡 *Hướng dẫn:* Video hướng dẫn giúp trader hiểu rõ cách giao dịch và tránh lỗi cơ bản."
    }
}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(info["title"], callback_data=key)] for key, info in RESOURCES.items()
    ])

def resource_menu(key):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 Xem hướng dẫn", callback_data=f"guide_{key}"),
            InlineKeyboardButton("⬅️ Trở lại", callback_data="back")
        ]
    ])

# ===== Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown", reply_markup=main_menu())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data in RESOURCES:
        info = RESOURCES[data]
        text = f"*{info['title']}*\n\n{info['text']}"
        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=resource_menu(data)
        )
    elif data.startswith("guide_"):
        key = data.replace("guide_", "")
        guide = RESOURCES.get(key, {}).get("guide", "Chưa có hướng dẫn.")
        await query.edit_message_text(
            text=f"{guide}",
            parse_mode="Markdown",
            reply_markup=resource_menu(key)
        )
    elif data == "back":
        await query.edit_message_text(
            text=WELCOME_MESSAGE,
            parse_mode="Markdown",
            reply_markup=main_menu()
        )

# ===== Khởi chạy bot =====
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("🤖 Bot đang chạy polling...")
    await app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_bot())).start()
    print("🌐 Flask giữ bot luôn sống...")
    flask_app.run(host="0.0.0.0", port=10000)

import os
import asyncio
import logging
import threading
import http.server
import socketserver

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WELCOME_MESSAGE = "👋 Chào mừng bạn đến với Entry247 Bot! Hãy chọn một mục bên dưới:"
MAIN_MENU = [
    [InlineKeyboardButton("📌 Giới thiệu", callback_data="intro")],
    [InlineKeyboardButton("📋 Hướng dẫn", callback_data="guide")],
    [InlineKeyboardButton("🔙 Quay lại menu chính", callback_data="main_menu")],
]

# Gửi menu chính
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        try:
            await query.message.delete()
        except:
            pass
        await query.message.reply_text(
            WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(MAIN_MENU)
        )
    elif update.message:
        await update.message.reply_text(
            WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(MAIN_MENU)
        )


# Xử lý khi nhấn nút
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        data = query.data

        try:
            await query.message.delete()
        except:
            pass

        if data == "intro":
            await query.message.reply_text(
                "📌 Đây là bot hỗ trợ từ Entry247.\nChúng tôi cung cấp thông tin về kỳ thi, tư vấn, v.v.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Quay lại menu chính", callback_data="main_menu")]]
                ),
            )

        elif data == "guide":
            await query.message.reply_text(
                "📋 Hướng dẫn sử dụng bot:\n- Bấm các nút để xem thông tin\n- Dùng nút Quay lại để về menu",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Quay lại menu chính", callback_data="main_menu")]]
                ),
            )

        elif data == "main_menu":
            await query.message.reply_text(
                WELCOME_MESSAGE,
                reply_markup=InlineKeyboardMarkup(MAIN_MENU),
            )


# Cổng giả giữ cho app "sống" trên Render Free Tier
def keep_alive():
    PORT = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"✅ Keep-alive HTTP server running on port {PORT}")
        httpd.serve_forever()


# Chạy bot
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Entry247 Bot đang chạy...")
    await app.run_polling()


if __name__ == "__main__":
    threading.Thread(target=keep_alive).start()
    asyncio.run(main())

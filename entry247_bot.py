import os
import asyncio
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from aiohttp import web

TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

WELCOME_MESSAGE = """Xin chào các thành viên Entry247 🚀

Chúc mừng bạn đã gia nhập
Entry247 | Premium Signals 🇻🇳

Nơi tổng hợp dữ liệu, tín hiệu và chiến lược giao dịch chất lượng, dành riêng cho những trader nghiêm túc ✅

🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢
"""

BUTTONS = [
    ("1️⃣ Kênh dữ liệu Update 24/24", "https://docs.google.com/spreadsheets/d/1KvnPpwVFe-FlDWFc1bsjydmgBcEHcBIupC6XaeT1x9I/edit?gid=247967880"),
    ("2️⃣ BCoin_Push", "https://t.me/Entry247_Push"),
    ("3️⃣ Entry247 | Premium Signals 🇻🇳", "https://t.me/+6yN39gbr94c0Zjk1"),
    ("4️⃣ Entry247 | Premium Trader Talk 🇻🇳", "https://t.me/+eALbHBRF3xtlZWNl"),
    ("5️⃣ Tool Độc quyền, Free 100%", "https://t.me/+ghRLRK6fHeYzYzE1"),
    ("6️⃣ Học và hiểu ( Video )", "https://t.me/+ghRLRK6fHeYzYzE1"),
    ("📘 Xem hướng dẫn sử dụng", "HDSD")
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(text, callback_data=data if data == "HDSD" else f"URL|{url}")]
        for text, url in BUTTONS
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("URL|"):
        url = data.split("|", 1)[1]
        await query.message.reply_text(f"👉 Mở liên kết: {url}")
    elif data == "HDSD":
        await query.message.reply_text(
            "📘 *Hướng dẫn sử dụng bot:*\n\n"
            "- Nhấn vào các nút để truy cập dữ liệu, tín hiệu và cộng đồng hỗ trợ.\n"
            "- Trở lại menu chính bất kỳ lúc nào bằng cách nhấn nút 🔙 Quay lại.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Quay lại menu chính", callback_data="BACK")]
            ]),
            parse_mode='Markdown'
        )
    elif data == "BACK":
        return await start(update, context)

async def keep_alive():
    async def handler(request):
        return web.Response(text="✅ Bot is alive.")
    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()
    print("✅ Keep-alive HTTP server running on port 10000")

async def main():
    await keep_alive()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🤖 Entry247 Bot đang chạy...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

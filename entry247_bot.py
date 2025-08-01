from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7876918917:AAE8J2TT4fc-iZB18dnA_tAoUyrHwg_v6q4"

# Giao diện nút chính
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📄 Tính năng chính", callback_data='main')],
        [InlineKeyboardButton("📘 Xem hướng dẫn", callback_data='guide')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Giao diện sau khi chọn "Tính năng chính"
def feature_menu():
    keyboard = [
        [InlineKeyboardButton("📘 Xem hướng dẫn", callback_data='guide')],
        [InlineKeyboardButton("🔙 Quay lại", callback_data='back')]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Chào mừng bạn đến với bot Entry247!",
        reply_markup=main_menu()
    )

# Xử lý các callback khi người dùng nhấn button
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'main':
        await query.edit_message_text(
            text="🧮 Đây là tính năng chính của bot.",
            reply_markup=feature_menu()
        )

    elif query.data == 'guide':
        await query.edit_message_text(
            text="📘 Hướng dẫn sử dụng bot:\n\n- Nhấn vào các nút để tương tác.\n- Dùng /start để bắt đầu lại.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Quay lại", callback_data='back')]
            ])
        )

    elif query.data == 'back':
        await query.edit_message_text(
            text="🔙 Quay lại menu chính:",
            reply_markup=main_menu()
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot Entry247 đang chạy...")
    app.run_polling()

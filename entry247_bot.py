async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    data = query.data
    user_id = query.from_user.id
    first_name = query.from_user.first_name or "bạn"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if data == "main_menu":
        # 1. Hiện menu gốc trước
        welcome_text = f"""🌟 Xin chào {first_name} 🚀\n\nChào mừng bạn đến với Entry247 Premium – nơi tổng hợp dữ liệu, tín hiệu và chiến lược trading Crypto cho trader nghiêm túc ✅\n\n🟢 Bạn có quyền truy cập vào 6 tài nguyên chính 🟢\n📌 Mọi thông tin góp ý: @Entry247"""
        msg = await context.bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)

        # 2. Xoá các tin cũ (trừ menu gốc vừa gửi)
        if user_id in user_sent_messages:
            for mid in list(user_sent_messages[user_id]):
                if mid != msg.message_id:
                    try:
                        await context.bot.delete_message(chat_id=chat_id, message_id=mid)
                    except:
                        pass
            # Giữ lại chỉ message_id của menu gốc
            user_sent_messages[user_id] = [msg.message_id]

        sheet_logs.append_row([now, user_id, "Trở lại menu"])

    elif data.startswith("menu_"):
        index = int(data.split("_")[1])

        # Nếu chưa có link và video => báo đang hoàn thiện
        if not MENU[index][1] and not MENU[index][2]:
            msg = await context.bot.send_message(
                chat_id=chat_id,
                text="📢 Danh mục đang được hoàn thiện, sẽ sớm update tới các bạn 🔥"
            )
            track_user_message(user_id, msg.message_id)
            sheet_logs.append_row([now, user_id, f"Xem: {MENU[index][0]} (đang hoàn thiện)"])
            return

        msg = await context.bot.send_message(chat_id=chat_id, text=f"🔹 {MENU[index][0]}", reply_markup=build_sub_keyboard(index))
        track_user_message(user_id, msg.message_id)
        sheet_logs.append_row([now, user_id, f"Xem: {MENU[index][0]}"])

    elif data == "optin":
        update_user_optin(user_id, True)
        msg = await context.bot.send_message(chat_id=chat_id, text="✅ Nhận thông báo đào chiều sớm : ON.", reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)

    elif data == "optout":
        update_user_optin(user_id, False)
        msg = await context.bot.send_message(chat_id=chat_id, text="❌ Nhận thông báo đào chiều sớm : OFF.", reply_markup=build_main_keyboard())
        track_user_message(user_id, msg.message_id)

    elif data.startswith("video_"):
        index = int(data.split("_")[1])
        caption = MENU[index][2]
        video_id = VIDEO_IDS.get(index)
        if video_id:
            msg = await context.bot.send_video(chat_id=chat_id, video=video_id, caption=caption)
            track_user_message(user_id, msg.message_id)
        else:
            msg = await context.bot.send_message(chat_id=chat_id, text="⚠️ Video chưa được cấu hình.")
            track_user_message(user_id, msg.message_id)

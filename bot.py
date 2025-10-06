# ... (previous imports and setup remain the same)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await query.edit_message_text("❌ Bu işlemi yapma yetkiniz yok.")
        return
    
    data = query.data
    if data == 'yes':
        user_info = user_data.get(user_id, {})
        file_id = user_info.get('file_id')
        title = user_info.get('title', 'Bilinmeyen Şarkı')
        
        if not file_id:
            await query.edit_message_text("❌ Dosya bulunamadı. Lütfen tekrar deneyin.")
            return
            
        # Başlığı düzenle
        formatted_title = ' '.join(word.capitalize() for word in title.split())
        
        try:
            # Kanal için klavye oluştur
            keyboard = [[
                InlineKeyboardButton("🎵 Kanalımıza Katıl", url=f"https://t.me/{CHANNEL_USERNAME}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Kanalda paylaş
            await context.bot.send_audio(
                chat_id=f"@{CHANNEL_USERNAME}",
                audio=file_id,
                title=formatted_title[:64],
                performer="𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♪",
                caption=f"🎵 {formatted_title}\n\nKanalımıza katıl: @{CHANNEL_USERNAME}",
                reply_markup=reply_markup
            )
            
            # Kullanıcıya geri dön
            await query.edit_message_text(
                "✅ Müzik kanalda paylaşıldı!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎵 Kanalı Görüntüle", url=f"https://t.me/{CHANNEL_USERNAME}")
                ]])
            )
            
        except Exception as e:
            logger.error(f"Kanal gönderim hatası: {e}")
            await query.edit_message_text("❌ Kanalda paylaşılırken bir hata oluştu.")
    else:
        await query.edit_message_text("❌ Paylaşım iptal edildi.")
    
    # Kullanıcı verilerini temizle
    if user_id in user_data:
        del user_data[user_id]

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Yetki kontrolü
    if user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Bu botu kullanma yetkiniz yok.")
        return
    
    try:
        # Müzik dosyasını al
        audio_file = await update.message.audio.get_file()
        title = Path(update.message.audio.file_name).stem  # Uzantıyı kaldır
        
        # Başlığı düzenle
        formatted_title = ' '.join(word.capitalize() for word in title.split())
        
        # Kullanıcı verilerini kaydet
        user_data[user.id] = {
            'file_id': audio_file.file_id,
            'title': title
        }
        
        # Kanal için buton oluştur
        keyboard = [[
            InlineKeyboardButton("🎵 Kanalımıza Katıl", url=f"https://t.me/{CHANNEL_USERNAME}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Müziği kullanıcıya geri gönder
        await context.bot.send_audio(
            chat_id=chat_id,
            audio=audio_file.file_id,
            title=formatted_title[:64],
            performer="𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♪",
            caption=f"🎵 {formatted_title}\n\nKanal: @{CHANNEL_USERNAME}",
            reply_markup=reply_markup
        )
        
        # Onay butonları oluştur
        keyboard = [
            [InlineKeyboardButton("✅ Kanalda Paylaş", callback_data='yes')],
            [InlineKeyboardButton("❌ Paylaşma", callback_data='no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Onay iste
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"kanalda paylaşmak?\n\n"
                 f"Başlık: {formatted_title}\n"
                 f"Kanal: @{CHANNEL_USERNAME}",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Genel hata: {e}")
        await update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

# ... (main fonksiyonu ve diğer kodlar aynı kalacak)

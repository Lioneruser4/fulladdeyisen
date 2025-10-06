import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from pathlib import Path

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token'ı ve ayarlar
TOKEN = '2138035413:AAGYaGtgvQ4thyJKW2TXLS5n3wyZ6vVx3I8'
CHANNEL_USERNAME = 'btmusiqi'  # @ işareti olmadan
AUTHORIZED_USERS = [976640409]  # Yetkili kullanıcı ID'leri

# Kullanıcı verilerini saklamak için geçici depo
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Bu botu kullanma yetkiniz yok.")
        return
    await update.message.reply_text('Azərbaycan musiqisi göndər')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await query.edit_message_text("❌ Bu işlemi yapma yetkiniz yok.")
        return
    
    data = query.data
    if data == 'yes':
        # Kullanıcı verilerinden bilgileri al
        user_info = user_data.get(user_id, {})
        file_id = user_info.get('file_id')
        title = user_info.get('title', 'Bilinmeyen Şarkı')
        
        if not file_id:
            await query.edit_message_text("❌ Dosya bulunamadı. Lütfen tekrar deneyin.")
            return
            
        # Kanal için caption oluştur
        caption = f"{title}\n\n𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♪ (https://t.me/{CHANNEL_USERNAME})"
        
        try:
            # Kanalda paylaş
            await context.bot.send_audio(
                chat_id=f"@{CHANNEL_USERNAME}",
                audio=file_id,
                title=title[:64],
                performer="𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♪",
                caption=caption,
                parse_mode='HTML'
            )
            
            await query.edit_message_text("✅ Müzik kanalda paylaşıldı!")
            
            # Kullanıcıya geri gönder
            await context.bot.send_audio(
                chat_id=user_id,
                audio=file_id,
                caption=caption,
                parse_mode='HTML'
            )
            
        except Exception as e:
            logger.error(f"Kanal gönderim hatası: {e}")
            await query.edit_message_text("❌ Kanalda paylaşılırken bir hata oluştu.")
    else:
        await query.edit_message_text("❌ İşlem iptal edildi.")
    
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
        # Kullanıcıya işlem başladı bilgisi ver
        processing_msg = await update.message.reply_text("🎵 Müzik işleniyor, lütfen bekleyin...")
        
        # Müzik dosyasını al
        audio_file = await update.message.audio.get_file()
        title = Path(update.message.audio.file_name).stem  # Uzantıyı kaldır
        
        # Kullanıcı verilerini kaydet
        user_data[user.id] = {
            'file_id': audio_file.file_id,
            'title': title
        }
        
        # Onay butonları oluştur
        keyboard = [
            [InlineKeyboardButton("✅ Evet, Paylaş", callback_data='yes')],
            [InlineKeyboardButton("❌ İptal", callback_data='no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Onay iste
        await processing_msg.edit_text(
            f"Bu müziği kanalda paylaşmak istiyor musunuz?\n\n"
            f"Başlık: {title}\n"
            f"Kanal: @{CHANNEL_USERNAME}",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Genel hata: {e}")
        await update.message.reply_text("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

def main():
    # Uygulamayı oluştur
    application = Application.builder().token(TOKEN).build()
    
    # Komut işleyicileri
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Botu başlat
    application.run_polling()

if __name__ == '__main__':
    main()

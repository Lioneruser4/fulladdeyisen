import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pathlib import Path

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token'ı
TOKEN = '2138035413:AAGYaGtgvQ4thyJKW2TXLS5n3wyZ6vVx3I8'
CHANNEL_USERNAME = 'btmusiqi'  # @ işareti olmadan yazın

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Azərbaycan musiqisi göndər')

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    try:
        # Kullanıcıya işlem başladı bilgisi ver
        processing_msg = await update.message.reply_text("🎵 Müzik işleniyor, lütfen bekleyin...")
        
        # Müzik dosyasını al
        audio_file = await update.message.audio.get_file()
        
        # Başlık ve sanatçı bilgisini çıkar
        if ' - ' in update.message.audio.file_name:
            artist, title = update.message.audio.file_name.rsplit(' - ', 1)
            title = Path(title).stem  # Uzantıyı kaldır
        else:
            title = Path(update.message.audio.file_name).stem
            artist = "Bilinmiyor"
        
        # Kanalda paylaş
        try:
            # Önce kanala gönder
            channel_message = await context.bot.send_audio(
                chat_id=f"@{CHANNEL_USERNAME}",
                audio=audio_file.file_id,
                title=title[:64],
                performer=artist[:64],
                caption=f"🎵 {title}\n👤 {artist}\n\n🔊 @{CHANNEL_USERNAME}"
            )
            
            # Kullanıcıya geri gönder
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=channel_message.audio.file_id,
                caption=f"🎵 {title}\n👤 {artist}\n\n🔊 @{CHANNEL_USERNAME}"
            )
            
            # İşlem tamamlandı mesajını güncelle
            await processing_msg.edit_text("✅ Müzik başarıyla paylaşıldı!")
            
        except Exception as e:
            logger.error(f"Kanal gönderim hatası: {e}")
            await update.message.reply_text("Müzik kanala gönderilirken bir hata oluştu. Lütfen tekrar deneyin.")
            
    except Exception as e:
        logger.error(f"Genel hata: {e}")
        await update.message.reply_text("Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.")

def main():
    # Uygulamayı oluştur
    application = Application.builder().token(TOKEN).build()
    
    # Komut işleyicileri
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    
    # Botu başlat
    application.run_polling()

if __name__ == '__main__':
    main()

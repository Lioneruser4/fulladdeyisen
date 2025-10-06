import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TALB, COMM
from dotenv import load_dotenv

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# .env dosyasından token'ı yükle
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_USERNAME = 'btmusiqi'  # Kanal kullanıcı adı

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Azərbaycan musiqisi göndər')

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Müzik dosyasını indir
        audio_file = await update.message.audio.get_file()
        file_path = f"{update.message.audio.file_id}.mp3"
        await audio_file.download_to_drive(file_path)
        
        # Müzik dosyasını işle
        audio = MP3(file_path, ID3=ID3)
        
        # Mevcut etiketleri al veya yeni oluştur
        try:
            audio.add_tags()
        except Exception:
            pass
        
        # Sanatçı ve başlık bilgilerini güncelle
        artist = "𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♫"
        title = audio.get('TIT2', [''])[0] or os.path.splitext(update.message.audio.file_name)[0]
        
        audio.tags.add(TPE1(encoding=3, text=artist))  # Sanatçı
        audio.tags.add(TIT2(encoding=3, text=title))    # Başlık
        audio.tags.add(TALB(encoding=3, text=artist))   # Albüm
        
        # Açıklama kısmına kanal linkini ekle
        comment = f"🎵 {title}\n\n🔊 @{CHANNEL_USERNAME}"
        audio.tags.add(COMM(encoding=3, lang='eng', desc='', text=comment))
        
        # Değişiklikleri kaydet
        audio.save()
        
        # Buton kullanılmayacak, sadece caption olacak
        
        # Düzenlenmiş dosyayı gönder (butonsuz)
        with open(file_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title=title,
                performer=artist,
                caption=f"🎵 {title}\n👤 {artist}\n\n🔊 @{CHANNEL_USERNAME}"
            )
        
        # Geçici dosyayı sil
        os.remove(file_path)
        
    except Exception as e:
        logger.error(f"Hata oluştu: {e}")
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
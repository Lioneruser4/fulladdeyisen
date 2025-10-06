import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TALB, COMM
from mutagen.mp4 import MP4, MP4Cover
from pathlib import Path

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token'ı
TOKEN = '2138035413:AAGYaGtgvQ4thyJKW2TXLS5n3wyZ6vVx3I8'
CHANNEL_USERNAME = 'btmusiqi'  # Kanal kullanıcı adı

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Azərbaycan musiqisi göndər')

def process_mp3(file_path, file_name):
    audio = MP3(file_path, ID3=ID3)
    
    # Mevcut etiketleri al veya yeni oluştur
    try:
        audio.add_tags()
    except Exception:
        pass
    
    # Sanatçı ve başlık bilgilerini güncelle
    artist = "𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♫"
    title = audio.get('TIT2', [''])[0] or Path(file_name).stem
    
    audio.tags.add(TPE1(encoding=3, text=artist))  # Sanatçı
    audio.tags.add(TIT2(encoding=3, text=title))    # Başlık
    audio.tags.add(TALB(encoding=3, text=artist))   # Albüm
    
    # Açıklama kısmına kanal linkini ekle
    comment = f"🎵 {title}\n\n🔊 @{CHANNEL_USERNAME}"
    audio.tags.add(COMM(encoding=3, lang='eng', desc='', text=comment))
    
    # Değişiklikleri kaydet
    audio.save()
    return title, artist

def process_m4a(file_path, file_name):
    audio = MP4(file_path)
    
    # Sanatçı ve başlık bilgilerini güncelle
    artist = "𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♫"
    title = audio.get('\xa9nam', [Path(file_name).stem])[0]
    
    audio['\xa9ART'] = artist
    audio['\xa9nam'] = title
    audio['\xa9alb'] = artist
    audio['\xa9cmt'] = f"🎵 {title}\n\n🔊 @{CHANNEL_USERNAME}"
    
    # Değişiklikleri kaydet
    audio.save()
    return title, artist

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Müzik dosyasını indir
        audio_file = await update.message.audio.get_file()
        file_extension = Path(audio_file.file_path).suffix.lower()
        file_path = f"{update.message.audio.file_id}{file_extension}"
        await audio_file.download_to_drive(file_path)
        
        try:
            # Dosya uzantısına göre işleme yap
            if file_extension == '.mp3':
                title, artist = process_mp3(file_path, audio_file.file_path)
            elif file_extension in ['.m4a', '.mp4']:
                title, artist = process_m4a(file_path, audio_file.file_path)
            else:
                await update.message.reply_text("Desteklenmeyen dosya formatı. Lütfen MP3 veya M4A formatında müzik gönderin.")
                os.remove(file_path)
                return
                
            # Düzenlenmiş dosyayı gönder
            with open(file_path, 'rb') as file_to_send:
                await update.message.reply_audio(
                    audio=file_to_send,
                    title=title,
                    performer=artist,
                    caption=f"🎵 {title}\n👤 {artist}\n\n🔊 @{CHANNEL_USERNAME}"
                )
                
        except Exception as e:
            logger.error(f"Ses işleme hatası: {e}")
            await update.message.reply_text("Müzik işlenirken bir hata oluştu. Lütfen başka bir dosya deneyin.")
            
        finally:
            # Geçici dosyayı sil
            if os.path.exists(file_path):
                os.remove(file_path)
                
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

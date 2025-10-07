import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from pathlib import Path

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token and settings
TOKEN = '2138035413:AAGYaGtgvQ4thyJKW2TXLS5n3wyZ6vVx3I8'
CHANNEL_USERNAME = 'btmusiqi'  # without @
AUTHORIZED_USERS = [976640409]  # Authorized user IDs

# Temporary storage for user data
user_data = {}

def escape_markdown(text):
    """Escape special MarkdownV2 characters"""
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You don't have permission to use this bot.")
        return
    await update.message.reply_text('Send me an Azerbaijani music file')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in AUTHORIZED_USERS:
        await query.edit_message_text("❌ You don't have permission to perform this action.")
        return
    
    data = query.data
    if data == 'yes':
        user_info = user_data.get(user_id, {})
        file_id = user_info.get('file_id')
        title = user_info.get('title', 'Unknown Track')
        
        if not file_id:
            await query.edit_message_text("❌ File not found. Please try again.")
            return
            
        # Format the title with proper capitalization
        formatted_title = ' '.join(word.capitalize() for word in title.split())
        # Escape special characters
        safe_title = escape_markdown(formatted_title)
        
        # Create caption with the exact format you want
        caption = f"{safe_title} 𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♪"
        
        try:
            # Share to channel
            await context.bot.send_audio(
                chat_id=f"@{CHANNEL_USERNAME}",
                audio=file_id,
                title=formatted_title[:64],
                performer="𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♪",
                caption=caption,
                parse_mode='MarkdownV2'
            )
            
            await query.edit_message_text("✅ Music shared to channel!")
            
        except Exception as e:
            logger.error(f"Channel sharing error: {e}")
            await query.edit_message_text("❌ Error sharing to channel.")
    else:
        await query.edit_message_text("❌ Sharing cancelled.")
    
    # Clean up user data
    if user_id in user_data:
        del user_data[user_id]

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Permission check
    if user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You don't have permission to use this bot.")
        return
    
    try:
        # Get audio file
        audio_file = await update.message.audio.get_file()
        title = Path(update.message.audio.file_name).stem  # Remove extension
        
        # Format the title with proper capitalization
        formatted_title = ' '.join(word.capitalize() for word in title.split())
        # Escape special characters
        safe_title = escape_markdown(formatted_title)
        
        # Store user data
        user_data[user.id] = {
            'file_id': audio_file.file_id,
            'title': title
        }
        
        # Send music back to user
        caption = f"{safe_title} 𝐁𝐓 𝐌𝐮𝐬𝐢𝐪𝐢 ♪"
        await context.bot.send_audio(
            chat_id=chat_id,
            audio=audio_file.file_id,
            caption=caption,
            parse_mode='MarkdownV2'
        )
        
        # Create confirmation buttons
        keyboard = [
            [InlineKeyboardButton("✅ Share to Channel", callback_data='yes')],
            [InlineKeyboardButton("❌ Cancel", callback_data='no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Ask for confirmation
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Do you want to share this music to the channel?\n\n"
                 f"Title: {formatted_title}\n"
                 f"Channel: @{CHANNEL_USERNAME}",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"General error: {e}")
        await update.message.reply_text("❌ An error occurred. Please try again.")

def main():
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()

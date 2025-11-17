"""
Ghanaian Sign Language (GSL) Telegram Bot
A dictionary bot for learning GSL signs + Competitive Multiplayer Games
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

from config import BOT_TOKEN, ADMIN_USER_ID, MAX_SUGGESTIONS
from database import db
from game_database import game_db

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ========================
# COMMAND HANDLERS
# ========================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    welcome_text = """
🤟 **Welcome to GSL Dictionary Bot!**

I can help you learn Ghanaian Sign Language (GSL) signs.

📚 **How to use:**
• Just type any word (e.g., "A", "HELLO", "THANK YOU")
• I'll send you a video demonstration
• If not found, you can help contribute to the dictionary by submitting samples via our data collection app!
• Data Collection App: [https://unchancy-deadpan-codi.ngrok-free.dev]

🔍 **Commands:**
/start - Show this message
/browse - Browse by category
/stats - View dictionary statistics
/help - Get help

**Example:** Type "HELLO" or "A" to see the sign!
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help information"""
    help_text = """
ℹ️ **How to Use GSL Dictionary Bot**

**Search for Signs:**
Simply type any word, letter, or number:
• `A` → Shows alphabet sign for A
• `5` → Shows number sign for 5
• `HELLO` → Shows sign for "hello"

**Browse Categories:**
Use /browse to explore:
• 🔤 Alphabets (A-Z)
• 🔢 Numbers (0-9)
• 💬 Words (common phrases)

**Tips:**
• Case doesn't matter (a, A, or a all work)
• If exact match not found, you'll get suggestions
• Videos show the proper hand movements

**Other Commands:**
/stats - See how many signs are available
/start - Back to welcome message

Need more help? Contact the developer!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show database statistics"""
    stats = db.get_statistics()
    
    stats_text = f"""
📊 **GSL Dictionary Statistics**

Total Signs: **{stats['total_signs']}**

By Category:
🔤 Alphabets: {stats['alphabets']}
🔢 Numbers: {stats['numbers']}
💬 Words: {stats['words']}

Keep learning! 🤟
    """
    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def browse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show category browser"""
    keyboard = [
        [
            InlineKeyboardButton("🔤 Alphabets", callback_data='browse_alphabets'),
            InlineKeyboardButton("🔢 Numbers", callback_data='browse_numbers')
        ],
        [InlineKeyboardButton("💬 Words", callback_data='browse_words')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        '📚 **Browse GSL Signs by Category:**',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def browse_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category browsing callbacks"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace('browse_', '')
    items = db.get_category(category)
    
    if not items:
        await query.edit_message_text(
            f"📭 No signs available in **{category}** yet.",
            parse_mode='Markdown'
        )
        return
    
    # Create list of available signs
    signs_list = ', '.join(sorted(items.keys())[:50])  # Show first 50
    total = len(items)
    
    message = f"""
📖 **{category.capitalize()}** ({total} signs)

Available: {signs_list}

Type any of these to see the sign video!
    """
    
    if total > 50:
        message += f"\n\n_...and {total - 50} more!_"
    
    await query.edit_message_text(message, parse_mode='Markdown')


# ========================
# MESSAGE HANDLERS
# ========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user queries for signs"""
    query = update.message.text.strip()
    
    # Search for exact match
    result = db.search(query)
    
    if result:
        # Found exact match
        await send_sign_video(update, result)
    else:
        # Try fuzzy search
        suggestions = db.fuzzy_search(query, max_results=MAX_SUGGESTIONS)
        
        if suggestions:
            await send_suggestions(update, query, suggestions)
        else:
            await update.message.reply_text(
                f"❌ Sorry, I couldn't find any sign for **'{query}'**.\n\n"
                f"📚 **Help us build an inclusive GSL dictionary!**\n"
                f"This is a community-driven project - for the inclusive, by the inclusive.\n\n"
                f"🎥 **Contribute your signs:**\n"
                f"Visit our data collection app to record and submit GSL signs:\n"
                f"https://unchancy-deadpan-codi.ngrok-free.dev\n\n"
                f"💡 Or try /browse to see available signs.",
                parse_mode='Markdown'
            )


async def send_sign_video(update: Update, video_info: Dict):
    """Send video file for a sign"""
    video_path = Path(video_info['path'])
    
    if not video_path.exists():
        await update.message.reply_text(
            "⚠️ Video file not found. Please contact admin.",
            parse_mode='Markdown'
        )
        return
    
    caption = f"""
✅ **{video_info.get('description', 'GSL Sign')}**
Category: {video_info.get('category', 'Unknown').capitalize()}
    """
    
    try:
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=caption,
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error sending video: {e}")
        await update.message.reply_text(
            "⚠️ Error sending video. Please try again later.",
            parse_mode='Markdown'
        )


async def send_suggestions(update: Update, query: str, suggestions: List[Dict]):
    """Send suggestions when exact match not found"""
    suggestions_text = f"🔍 Didn't find **'{query}'**, but here are similar signs:\n\n"
    
    for i, item in enumerate(suggestions, 1):
        suggestions_text += f"{i}. {item['word']} ({item['category']})\n"
    
    suggestions_text += "\n💡 Type any of these to see the sign!"
    
    await update.message.reply_text(suggestions_text, parse_mode='Markdown')


# ========================
# ERROR HANDLER
# ========================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")


# ========================
# MAIN FUNCTION
# ========================

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("browse", browse_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(browse_callback, pattern='^browse_'))
    
    # Message handler (for sign queries)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🤖 GSL Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

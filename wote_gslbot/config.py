"""
Configuration for GSL Telegram Bot
"""
import os
import logging
from pathlib import Path

# Load environment variables from .env file (optional, for local dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ============================================================
# REQUIRED: Bot Token (get from @BotFather on Telegram)
# ============================================================
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("ERROR: TELEGRAM_BOT_TOKEN not set. Set it in .env or as an environment variable.")

# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
VIDEOS_DIR = DATA_DIR / 'videos'
DICTIONARY_FILE = DATA_DIR / 'dictionary.json'

# Configurable DB file path
DB_FILE = os.getenv('DB_FILE', './data/game_data.json')

# Video categories
CATEGORIES = {
    'alphabets': VIDEOS_DIR / 'alphabets',
    'numbers': VIDEOS_DIR / 'numbers',
    'words': VIDEOS_DIR / 'words'
}

# Create directories if they don't exist
for category_dir in CATEGORIES.values():
    category_dir.mkdir(parents=True, exist_ok=True)

# ============================================================
# LOGGING
# ============================================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ============================================================
# BOT SETTINGS
# ============================================================
MAX_SUGGESTIONS = 5
MAX_SEARCH_RESULTS = 5
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi']
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.gif']

# Admin user ID (for admin features / alerts)
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
if ADMIN_USER_ID:
    try:
        ADMIN_USER_ID = int(ADMIN_USER_ID)
    except ValueError:
        ADMIN_USER_ID = None

# ============================================================
# WEBHOOK MODE (Optional - for production)
# ============================================================
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # e.g., https://<ngrok-id>.ngrok.io/webhook
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 5000))

# ============================================================
# STORAGE BACKEND
# ============================================================
STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'json')  # 'json' or 'sqlite'

# ============================================================
# OPTIONAL INTEGRATIONS
# ============================================================
SENTRY_DSN = os.getenv('SENTRY_DSN')
REDIS_URL = os.getenv('REDIS_URL')
NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')

# Supabase (optional)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Messages
WELCOME_MESSAGE = """
🇬🇭 **Welcome to GSL Dictionary Bot!**

I can help you learn Ghana Sign Language by showing you video demonstrations.

**Commands:**
/start - Show this message
/search <word> - Search for a sign (e.g., /search apple)
/alphabet - Show all alphabet signs
/numbers - Show all number signs
/categories - List all available categories
/help - Get help

**Quick searches:**
Just type any word directly (e.g., "hello", "thank you")

Let's learn GSL together! 🤟
"""

HELP_MESSAGE = """
📚 **How to use GSL Dictionary Bot:**

**1. Search for a sign:**
   • Type: `/search apple`
   • Or just: `apple`

**2. Browse by category:**
   • `/alphabet` - All letters A-Z
   • `/numbers` - Numbers 0-9
   • `/categories` - See all categories

**3. Tips:**
   • Videos show proper hand positions
   • Watch multiple times for better learning
   • Practice along with the video

Need more signs? Let us know what to add! 💬
"""

NOT_FOUND_MESSAGE = """
❌ Sorry, I don't have a video for "{query}" yet.

**Available signs:**
{suggestions}

Try one of these or request this sign to be added!
"""

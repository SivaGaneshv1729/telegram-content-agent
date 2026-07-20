import logging
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import start_handler, setstyle_handler, message_handler
from storage.memory import init_db

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_telegram_bot_token_here":
        logger.error("TELEGRAM_BOT_TOKEN is not set or is default.")
        return

    # Initialize SQLite DB
    init_db()

    application = ApplicationBuilder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('setstyle', setstyle_handler))
    # Filter out commands from the generic message handler
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) | filters.Document.MimeType("application/pdf"), message_handler))

    logger.info("Starting bot (long polling)...")
    application.run_polling()

if __name__ == '__main__':
    main()
